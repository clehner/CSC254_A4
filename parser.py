import os, fnmatch, subprocess, itertools, re,collections
from token import Token
from scanner import scan

methodIDs = frozenset(['public','private','static','abstract','native','final','synchronized','volatile','strictfp'])

types = frozenset(['int','Integer','double','Double','float','Float','String','char','Character','void'])
"""
Find java files and their associated class files in a directory.
Returns an iterator of tuple of java filename and class filenames.
"""
def findJavaFiles(path):
	for root, dirs, files in os.walk(path):
		for file in fnmatch.filter(files, '*.java'):
			javaFile = os.path.join(root, file)
			classesFn = file.replace('.java', '*.class')
			classFiles = fnmatch.filter(files, classesFn)
			classFiles = [os.path.join(root, file) for file in classFiles]
			yield (javaFile, classFiles)

"""
Run javap to disassemble a classfile.
Returns an iterator of lines.
"""
def javap(file):
	proc = subprocess.Popen(['javap','-verbose', '-private', file],
			stdout=subprocess.PIPE)
	return iter(proc.stdout.readline, '')

def readConstantPool(lines):
	constants = [] # indexed from 1 in javap
	for line in lines:#                   g1         g2       g3 
		m = re.match(r"\s*#[0-9]* = ([^\s]*)\s*(.*?)(?:\s*\/\/\s*(.*))?$", line)
		if m:
			(name, val, comment) = (m.group(1), m.group(2), m.group(3))
			constants.append((name, val, comment))
		else:
			break
	return constants

def readInstructions(lines):
	instructions = collections.defaultdict(list)
	lines.next()
	lines.next()
	lines.next()
	for line in lines:
		#matching an instruction
		m_inst = re.match(r"^\s*([0-9]*): ([^\s]*)\s*(#[0-9]*)?(?:\s*\/\/\s*(.*))?$",line) 
		if m_inst:
			instructions[int(m_inst.group(1))] = [m_inst.group(2),m_inst.group(3),m_inst.group(4)]
		#when we've hit the line number table, stop
		else:
			break
	return instructions


def readLineTable(lines,instructions,constants):
	line_table = collections.defaultdict(list)
	prev = [0, 0]
	for line in lines:
		#loop through and build the line number table	
		m = re.match(r"\s*line ([0-9]*): ([0-9]*)",line)
		if m:
			curr = (line_num, i_num) = (int(m.group(1)), int(m.group(2)))
			#print('groups- ',m.group(1),m.group(2))
			last_instruction = i_num
			if not prev == [None]:	
				first_instruction = prev[1]
				#go through instructions, get constants
				for i in range(first_instruction,last_instruction-1):
					inst_constants = []
					#check if instruction is presetn
					if i in instructions:
						line_table[line_num].append(instructions[i])
			prev = curr
		else:
			line_table[prev[1]].append(['return'])
			break
	return line_table

"""
Parser
"""
class Parser(object):
	'''main class for parsing class files'''
	def __init__(self, inputDir):
		self.path = inputDir

	"""
	Parse the java and class files in the path
	Return an iterator of class data objects
	"""
	def parse(self):
		for (javaFile, classFiles) in findJavaFiles(self.path):
			#initialization junk
			javapFiles = [javap(file) for file in classFiles]
			sourceData = {}
			sourceData['class_names'] = []
			sourceData['constants'] = []
			sourceData['method_refs'] = collections.defaultdict(list)
			sourceData['lines'] = []
			sourceData['line_table'] = collections.defaultdict(list)
			sourceData['instructions'] = collections.defaultdict(list)

			for javapFile in javapFiles:
				#get the main class name
				for line in javapFile:
					m = re.match(r"^.*class (.+)$", line)
					if m:
						sourceData['class_name'] = m.group(1)
						break

				for line in javapFile:
					#get constant pool
					if line == "Constant pool:\n":
						sourceData['constants'] = readConstantPool(javapFile)

					#get the instruction list for a given method
					mID_re =  "(("+"|".join(methodIDs)+") )*"
					type_re = "(("+"|".join(types)    +") )?"
					if re.match("^\s*"+mID_re+type_re+".*\((.*)\);$",line):
						sourceData['instructions'] = readInstructions(javapFile)

						sourceData['line_table'] = readLineTable(javapFile,sourceData['instructions'],sourceData['constants'])
					'''
					#get the line table (should happen right after instructions)
					if re.match("^\s*LineNumberTable:\s*$",line):
						sourceData['line_table'] = readLineTable(javapFile,sourceData['instructions'],sourceData['constants'])
					'''
			#I commented these to test the other stuff, feel free to uncomment
			'''
			#get the info for each line in the source files
			line_tokens = []
			for toks in scan(open(javaFile)):
				line = []
				for tok in toks:
					if tok.tok_type == Token.METHOD_INVOCATION:
						tok.class_name = 'SomeClass'
						tok.method_type = 'todo'
					line.append(tok)
				line_tokens.append(line)
			sourceData['lines'] = line_tokens
			'''
			yield sourceData


def add_comments(line_tokens):
	for line in line_tokens:
		start_comment = False
		for i in range(len(line)):
			j = line[i].text.find('//')
			if j == 0:
				start_comment = True
				line[i].tok_type = Token.COMMENT
			elif j > -1:
				#split the token to take the '//' part off
				split_token = line[i].text.split('//')
				line[i:i+1] = [
					Token(split_token[0], line[i].tok_type),
					Token('//'+split_token[1], Token.COMMENT)]
				start_comment = True
				# skip the regular token
				i += 1

			#flatten the rest of the list if there's a comment
			if(start_comment):
				line[i].text = ''.join([tok.text for tok in line[i:]])
				line[i+1:] = []
				break

def print_array_lines(lis):
	for l in lis: print(l)
def print_dic(dic):
	for key,value in dic.items():
		print(key," : ",value)

if __name__ == '__main__':
	parser = Parser('java')
	info = parser.parse()
	first = next(info)
	print('line_table')
	#print_array_lines(first['constants'])
	print_dic(first['line_table'])
	'''	
	for i in info:
		print('##############')
		print('instructions')
		print(i['instructions'])
		#print('classes')
		#print(str(i['class_names']))
		#print('methods')
		#print(str(i['method_refs']))
		#print('lines')
		#print(str(i['lines']))
		print()	
	'''

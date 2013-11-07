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
	constants = [None] # indexed from 1 in javap
	prev_idx = 0
	for line in lines:#       r1         g2       g3                g4
		m = re.match(r"\s*#([0-9]*) = ([^\s]*)\s*(.*?)(?:\s*\/\/\s*(.*))?$", line)
		if m:
			(idx, name, val, comment) =\
				(int(m.group(1)), m.group(2), m.group(3), m.group(4))
			skip = idx - prev_idx - 1
			if skip:
				# fill space for values that take >1 byte
				constants.extend(None for _ in range(0, skip))
			prev_idx = idx
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
		m_inst = re.match(r"^\s*([0-9]*): ([^\s]*)\s*(.*?)(?:\s*\/\/\s*(.*))?$",line)
		if m_inst:
			instructions[int(m_inst.group(1))] = [m_inst.group(2),m_inst.group(3),m_inst.group(4)]
		#when we've hit the line number table, stop
		else:
			break
	return instructions


def readLineTable(lines,instructions,line_table):
	prev = [0, 0]
	for line in lines:
		#loop through and build the line number table	
		m = re.match(r"\s*line ([0-9]*): ([0-9]*)",line)
		if m:
			curr = (line_num, i_num) = (int(m.group(1)), int(m.group(2)))
			last_instruction = i_num
			if not prev == [None]:	
				first_instruction = prev[1]
				#go through instructions, get constants
				for i in range(first_instruction,last_instruction-1):
					inst_constants = []
					#check if instruction is presetn
					if i in instructions:
						line_table[prev[0]].append(instructions[i])
			prev = curr
		else:
			line_table[prev[0]].append(['return'])
			break
	return line_table

def parse_constant(constants, num):
	num = int(num[1:])
	(constType, values, comment) = constants[num]
	if constType == 'Utf8':
		return values
	m = re.split(r'[.:]', values)
	if len(m) == 2:
		return (parse_constant(constants, m[0]),
			parse_constant(constants, m[1]))
	elif len(m) == 1:
		return parse_constant(constants, m[0])

def find_method_invocation(line_num, method_name, source_data):
	instructions = source_data['line_table'][line_num]
	constants = source_data['constants']
	for inst in instructions:
		if inst[0][:6] == 'invoke':
			const = parse_constant(constants, inst[1])
			(class_name, (name, method_type)) = const
			if method_name == name:
				return (class_name, method_type)
	return None

def annotate_token(tok, line_num, source_data):
	if tok.tok_type == Token.METHOD_UNKNOWN:
		m = find_method_invocation(line_num, tok.text, source_data)
		if m:
			tok.tok_type = Token.METHOD_INVOCATION
			(tok.class_name, tok.method_type) = m
		else:
			#it's a declaration, not invocation
			tok.tok_type = Token.METHOD_DECLARATION
			tok.class_name = 'Declaration'
			tok.method_type = 'todo'


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
						break

				for line in javapFile:
					#get the instruction list for a given method
					mID_re =  "(("+"|".join(methodIDs)+") )*"
					type_re = "(("+"|".join(types)    +") )?"
					if re.match("^\s*"+mID_re+type_re+".*\((.*)\);$",line):
						instructions = readInstructions(javapFile)
						sourceData['line_table'] = readLineTable(javapFile, instructions, sourceData['line_table'])
					'''
					#get the line table (should happen right after instructions)
					if re.match("^\s*LineNumberTable:\s*$",line):
						sourceData['line_table'] = readLineTable(javapFile,sourceData['instructions'],sourceData['constants'])
					'''
			#get the info for each line in the source files
			line_tokens = []
			for line_num, toks in enumerate(scan(open(javaFile))):
				line = []
				for tok in toks:
					annotate_token(tok, line_num+1, sourceData)
					line.append(tok)
				line_tokens.append(line)
			sourceData['lines'] = line_tokens
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

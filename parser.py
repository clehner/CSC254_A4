import os, fnmatch, subprocess, itertools, re,collections
from token import Token
from scanner import scan

method_declaration_re = "^  .*? ([^\s]*)(\(.*?\));$"

method_scanner = re.Scanner([
#todo: add more arg types to read with this regex
	("\(", None),
	("\).*", None),
	(r"D",lambda s,tok: 'double'),
	(r"L(.*?);",lambda s,tok: tok[1:-1].replace('/', '.')),
	(r"I",lambda s,tok: 'int'),
])

"""
Find java files and class files in each directory.
Returns an iterator of tuple of java filenames and class filenames.
"""
def findClassFiles(path):
	for root, dirs, files in os.walk(path):
		classFiles = fnmatch.filter(files,'*.class')
		classFiles = [os.path.join(root, file) for file in classFiles]
		yield (classFiles, root)

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

def readInstructions(lines, constants):
	instructions = collections.defaultdict(list)
	lines.next()
	lines.next()
	lines.next()
	for line in lines:
		#matching an instruction
		m_inst = re.match(r"^\s*([0-9]*): ([^\s]*)\s*(.*?)(?:\s*\/\/\s*(.*))?$",line)
		if m_inst:
			(idx, instType, params, comment) = (int(m_inst.group(1)),m_inst.group(2),m_inst.group(3),m_inst.group(4))

			if instType[:6] == 'invoke':
				if instType == 'invokeinterface':
					resolved_params = parse_constant(constants, params.split(',')[0])
				else:
					resolved_params = parse_constant(constants, params)
			else:
				resolved_params = params

			instructions[idx] = (instType, resolved_params, comment)
		#when we've hit the line number table, stop
		else:
			break
	return instructions


def readLineTable(lines,instructions,line_table):
	prev = [0, 0]
	first_line_read = -1
	last_line_read = -1
	for line in lines:
		#loop through and build the line number table
		m = re.match(r"\s*line ([0-9]*): ([0-9]*)",line)
		if m:
			curr = (line_num, i_num) = (int(m.group(1)), int(m.group(2)))
			last_line_read = line_num
			if first_line_read < 0:
				first_line_read = line_num
			last_instruction = i_num
			if not prev == [None]:
				first_instruction = prev[1]
				#go through instructions, get constants
				for i in range(first_instruction,last_instruction):
					inst_constants = []
					#check if instruction is present
					if i in instructions:
						line_table[prev[0]].append(instructions[i])
			prev = curr
		else:
			# add last instructions
			for i in range(last_instruction,max(instructions)):
				if i in instructions:
					line_table[prev[0]].append(instructions[i])
			break
	if first_line_read < 0:
		first_line_read = float("infinity")
		# todo: may need to distinguish between multiple interface methods
	return (line_table,first_line_read,last_line_read)

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
	for inst in instructions:
		if inst[0][:6] == 'invoke':
			const = inst[1]
			(class_name, (name, method_type)) = const
			if method_name == name:
				#print('matched name', method_name)
				return (class_name,parse_method_type( method_type))
			#else:
				#print('incorrect name', method_name, name)
	return None

def find_method_declaration(line_num, method_name, source_data):
	for (class_name, method_type, start_line, end_line) in\
		source_data['method_refs'][method_name]:
			if line_num >= start_line and line_num <= end_line:
				return (class_name, method_type)
			#else:
				#print("bad match", line_num, start_line, end_line, method_name)

def parse_method_type(method_type):
	types = method_scanner.scan(method_type)[0]
	return '(' + ', '.join(types) + ')'

def annotate_token(tok, line_num, source_data):
	if tok.tok_type == Token.METHOD_UNKNOWN:
		m = find_method_invocation(line_num, tok.text, source_data)
		if m:
			tok.tok_type = Token.METHOD_INVOCATION
			(tok.class_name, tok.method_type) = m
		else:
			# it's a declaration, not invocation
			m = find_method_declaration(line_num, tok.text, source_data)
			if m:
				(tok.class_name, tok.method_type) = m
				tok.tok_type = Token.METHOD_DECLARATION
			else:
				# unable to identify
				tok.tok_type = Token.PLAIN
"""
maps java source files to the classes they house
"""
def match_src_class(classFiles, rootDir):
	src_class = collections.defaultdict(list)
	for classFile in classFiles:
		javapFile = javap(classFile)
		for line in javapFile:
			m = re.match('^\s*Compiled from "(.*)"\s*$', line)
			if m:
				javaFile = os.path.join(rootDir, m.group(1))
				src_class[javaFile].append(javapFile)
				break
	return src_class

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
		for (classFiles, rootDir) in findClassFiles(self.path):
			src_class = match_src_class(classFiles, rootDir)
			for javaFile, javapFiles in src_class.iteritems():
				yield self.parseJava(javaFile, javapFiles)

	def parseJava(self, javaFile, javapFiles):
		#initialization junk
		sourceData = {}
		sourceData['class_names'] = []
		sourceData['constants'] = []
		sourceData['method_refs'] = collections.defaultdict(list)
		sourceData['lines'] = []
		sourceData['line_table'] = collections.defaultdict(list)
		sourceData['has_main'] = False

		for javapFile in javapFiles:
			#get the main class name
			for line in javapFile:
				m = re.match(r"^.*(?:class|interface) ([^\s<>]+).*?$", line)
				if m:
					class_name = m.group(1)
					sourceData['class_names'].append(class_name)
					break

			for line in javapFile:
				#get constant pool
				if line == "Constant pool:\n":
					constants = readConstantPool(javapFile)
					break

			prev_line_num = 0
			for line in javapFile:
				#get the instruction list for a given method
				m = re.match(method_declaration_re,line)
				if m:
					(method_name, m_types) = (m.group(1), m.group(2))
					#prev_line_num = len(sourceData['line_table'])
					instructions = readInstructions(javapFile, constants)
					(sourceData['line_table'], first_line_read,last_line_read) = readLineTable(javapFile, instructions, sourceData['line_table'])
					if prev_line_num > first_line_read:
						prev_line_num = 0
					sourceData['method_refs'][method_name].append((class_name, m_types, prev_line_num, first_line_read))
					prev_line_num = last_line_read
		if 'main' in sourceData['method_refs']:
			sourceData['has_main'] = True
		#get the info for each line in the source files
		line_tokens = []
		for line_num, toks in enumerate(scan(open(javaFile))):
			line = []
			for tok in toks:
				annotate_token(tok, line_num+1, sourceData)
				line.append(tok)
			line_tokens.append(line)
		sourceData['lines'] = line_tokens
		if len(sourceData['class_names']) is 0:
			sourceData['class_name'] = 'Unknown'
		else:
			sourceData['class_name'] = min(sourceData['class_names'], key=len)
		return sourceData


def print_array_lines(lis):
	for l in lis: print(l)
def print_dic(dic):
	for key,value in dic.items():
		print(key," : ",value)

if __name__ == '__main__':
	parser = Parser('java')
	info = parser.parse()
	first = next(info)
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

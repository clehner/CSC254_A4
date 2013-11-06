import os, fnmatch, subprocess, itertools, re,collections
from token import Token
from scanner import scan

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
	for line in lines:
		m = re.match(r"\s*#[0-9]* = ([^\s]*)\s*(.*?)(?:\s*\/\/\s*(.*))?$", line)
		if m:
			(name, val, comment) = (m.group(1), m.group(2), m.group(3))
			constants.append((name, val, comment))
		else:
			break
	return constants

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

			for javapFile in javapFiles:
				#get the main class name
				for line in javapFile:
					m = re.match(r"^.*class (.+)$", line)
					if m:
						sourceData['class_name'] = m.group(1)
						break

				#get constant pool
				for line in javapFile:
					if line == "Constant pool:\n":
						sourceData['constants'] = readConstantPool(javapFile)

				#loop through javap, collect class data
				#get class name, methods used from javap file
				current_class= ''
				for line in javapFile:
					#matches classes
					match = re.match(r"^.*class (.+)$", line)
					if match:
						sourceData['class_names'].append(match.group(1))
						current_class= match.group(1)
					if not match:
						sourceData['class_names'].append('UnknownClass')

					#get methods
					match2 = re.match(r"^.*invoke(.*)$",line)
					if match2:
						s = str(match2.group(1))
						s = s[s.index('Method')+7 :]
						s = s.split('.')
						#isourceData['method_refs'][s[0]].append(s[1]) if s[1] != None else sourceData['method_refs'][current_class].append(s[0])
						if len(s) > 1:
							sourceData['method_refs'][s[0]].append(s[1])
						else:
							sourceData['method_refs'][current_class].append(s[0])

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
			yield sourceData

if __name__ == '__main__':
	parser = Parser('java')
	info = parser.parse()
	first = next(info)
	#print(first['lines'])
	'''
	for i in info:
		print('##############')
		print('classes')
		print(str(i['class_names']))
		print('methods')
		print(str(i['method_refs']))
		print('lines')
		print(str(i['lines']))
		print()
	'''

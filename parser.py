import os, fnmatch, subprocess, itertools, re

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
			sourceData['method_refs'] = {}
			sourceData['lines'] = []
			
			for javapFile in javapFiles:
				#loop through javap, collect class data
				#get class name, methods used from javap file
				line = next(itertools.islice(javapFile, 4, None))
				if line:
					#matches classes
					match = re.match(r"^.*class (.+)$", line)
					if match:
						sourceData['class_names'].append(match.group(1))
					if not match:
						sourceData['class_names'].append('UnknownClass')

				for line in javapFile:	
					#get methods
					match2 = re.match(r"^.*invoke(.*)$",line)
					if match2:
						s = str(match2.group(1))
						s = s[s.index('Method')+7 :s.index(':')]
						s = s.split('.')
						sourceData['method_refs'][s[0]] = s[1]


			#get the info for each line
			line_tokens = []
			for line in open(javaFile):
				#TODO- make this not get rid of tabs
				line_tokens.append(line.split())	
			sourceData['lines'] = line_tokens

			yield sourceData


if __name__ == '__main__':
	parser = Parser('.')
	info = parser.parse()
	for i in info:
		print('##############')
		print('classes')
		print(str(i['class_names']))
		print('methods')
		print(str(i['method_refs']))
		print('lines')
		print(str(i['lines']))
		print()

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
			classData = {}
			javaPFile = javapFiles[0]
			line = next(itertools.islice(javaPFile, 4, None))

			#get class name
			if line:
				#matches invalid classes
				match = re.match(r"^.*class (.+)$", line)
				if match:
					classData['name'] = match.group(1)
				if not match:
					classData['name'] = 'UnknownClass'

			#get the info for each line
			line_tokens = []
			for line in open(javaFile):
				#TODO- make this not get rid of tabs
				line_tokens.append(line.split())	
			classData['lines'] = line_tokens

			#get the 
			yield classData


if __name__ == '__main__':
	parser = Parser('.')
	info = parser.parse()
	print(info.next())
	print('\n\n&&&&&&&&&&&&&&&&&&&&&&    loadinate      &&&&&&&&&&&&&&&\n\n')
	print(info.next())

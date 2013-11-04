import os, fnmatch, subprocess, itertools, re,collections
from token import Token

keywords = frozenset(['abstact','assert','boolean','break','byte','case','catch','const','continue','default','do','double','else','enum','extends','final','finally','float',\
'for','goto','if','implements','import','instanceof','int','interface','long','native','new','package','private','protected','public','return','short','static','strictfp',\
'super','switch','synchronized','this','throw','throws','transient','try','void','volatile','while'])

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
			sourceData['method_refs'] = collections.defaultdict(list)
			sourceData['lines'] = []

			for javapFile in javapFiles:
				#get the main class name
				for line in javapFile:
					m = re.match(r"^.*class (.+)$", line)
					if m:
						sourceData['class_name'] = m.group(1)
						break

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

			#get the info for each line
			line_tokens = []
			for line in open(javaFile):
				words = line.rstrip().split(" ")
				line = []
				for word in words:
					if word.strip() in keywords:
						tok_type = Token.KEYWORD
					else:
						tok_type = Token.PLAIN
					line.append(Token(word+" ", tok_type))
				line_tokens.append(line)
			#add comments
			lines_commented = add_comments(line_tokens)
			sourceData['lines'] = lines_commented

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

	return line_tokens


if __name__ == '__main__':
	parser = Parser('.')
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

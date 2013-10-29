'''
the file for decompiling and parsing java documents
by Dan Scarafoni
	
'''
import sys
import re
def main():
	f = open(sys.argv[1],'r')
	contents_raw = f.read()
	contents_lines = contents_raw.split('\n')

	#regex for class, method
	class_re  = re.compile('\s*(public|private) class \w+') #embellish
	method_re = re.compile('\s*(public|private|static) (void|int|String|double|char) \w+') #embellish

	#iterate through, look for classes and methods
	for line in contents_lines:
		if class_re.match(line):
			print(line)
		elif method_re.match(line):
			print(line)

if __name__ == '__main__':
	main()

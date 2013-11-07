import sys, os, fnmatch, shutil
from token import Token

"""
Template for index page
"""

indexHeader = """<!doctype html>
<html>
<head>
	<meta charset="utf-8">
	<title>Java Cross-Indexer</title>
	<link rel="stylesheet" href="static/style.css" type="text/css">
</head>
<body>
	<h1>Java Cross-Indexer</h1>
	<ul>
"""

indexFooter = """	</ul>
</body>
</html>
"""

indexLinkLine = '\t\t<li><a href="%s">%s</a></li>\n'

"""
Template for class page
"""

classHeader = """<!doctype html>
<html>
<head>
	<meta charset="utf-8">
	<title>%s</title>
	<link rel="stylesheet" href="%sstatic/style.css" type="text/css">
</head>
<body>
	<h1>%s</h1>
	<ol class="javaclass">"""

classFooter = """	</ol>
</body>
</html>
"""


"""
Ensure that directorys exists to contain a file.
"""
def ensureDir(f):
	d = os.path.dirname(f)
	if not os.path.exists(d):
		os.makedirs(d)

"""
Get a URL to a class page, relative to another page
"""
def getClassURL(className, page):
	classPage = className.replace('.', os.path.sep) + '.html'
	print('classPage ',classPage)
	if 'java' in className:
		return 'http://docs.oracle.com/javase/7/docs/api/' + classPage
	return os.path.relpath(classPage, page)

"""
Render a token on a page as text/html
"""
def tokenToHTML(tok, page):
	text = tok.text.replace('\t', '    ')\
		.replace('&', '&amp;')\
		.replace('<', '&lt;')\
		.replace('>', '&gt;')\
		.replace('"', '&quot;')\
		.replace('\'', '&apos;')
	tokType = tok.get_type()
	if tok.tok_type == Token.METHOD_INVOCATION:
		# make a link to the declaration of the method
		rel_file = getClassURL(tok.class_name, page)
		link = rel_file + '#' + tok.text + tok.method_type
		return '<a href="' + link + '" class="' + tokType + '">' + text + '</a>'
	elif tok.tok_type == Token.METHOD_DECLARATION:
		# make an anchor for the declaration, that can be linked to
		name = tok.method_type
		return '<a id="' + name + '" class="' + tokType + '">' + text + '</a>'
	elif tokType:
		# render a token of a given type
		return '<span class="' + tokType + '">' + text + '</span>'
	else:
		# render an unstyled token
		return text

"""
Renderer
Converts data about Java classes into HTML pages
"""
class Renderer(object):
	def __init__(self, outputDir):
		self.path = outputDir
		scriptDir = os.path.dirname(sys.argv[0])
		self.staticSource = os.path.join(scriptDir, 'static')
		self.staticDest = os.path.join(self.path, 'static')

	"""
	Copy static files into XREF directory
	"""
	def copyStatics(self):
		print "Copying static files"
		for srcDir, dirs, files in os.walk(self.staticSource):
			dstDir = srcDir.replace(self.staticSource, self.staticDest)
			if not os.path.exists(dstDir):
				os.mkdir(dstDir)
			for file in files:
				srcFile = os.path.join(srcDir, file)
				shutil.copy(srcFile, dstDir)

	"""
	Create and write an HTML page for a Java class
	"""
	def renderClass(self, classData):
		className = classData['class_name']
		print "Rendering " + className
		dirs = className.split('.')
		page = os.path.join(self.path, *dirs)+'.html'
		path = os.path.dirname(os.path.join(*dirs))
		ensureDir(page)
		rootDir = "../" * (len(dirs)-1)
		with open(page, 'w') as f:
			f.write(classHeader % (className, rootDir, className))
			for line in classData['lines']:
				f.write('<li>' +
						''.join([tokenToHTML(token, path) for token in line]) +
						'</li>\n')
			f.write(classFooter)

	"""
	Build and write an index page, with table of contents for classes.
	"""
	def renderIndex(self):
		print "Rendering index"
		page = os.path.join(self.path, 'index.html')
		ensureDir(page)
		with open(page, 'w') as f:
			f.write(indexHeader)
			# Add a link for every page in the directory
			for root, dirs, files in os.walk(self.path):
				for file in fnmatch.filter(files, '*.html'):
					if file == 'index.html':
						continue
					relDir = os.path.relpath(root, self.path)
					relFile = os.path.join(relDir, file).replace('./', '')
					className = relFile.replace(os.path.sep,
							'.').replace('.html', '')
					f.write(indexLinkLine % (relFile, className))
			f.write(indexFooter)

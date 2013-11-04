import sys, os, fnmatch, shutil

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

def tokenToHTML(tok):
	innerText = tok.text.replace('\t', '    ')\
		.replace('&', '&amp;')\
		.replace('<', '&lt;')\
		.replace('>', '&gt;')\
		.replace('"', '&quot;')\
		.replace('\'', '&apos;')
	tokType = tok.get_type()
	if tokType:
		return '<span class="' + tokType + '">' + innerText + '</span>'
	else:
		return innerText

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
		print "Rendering class " + className
		dirs = className.split('.')
		page = os.path.join(self.path, *dirs)+'.html'
		print "Writing " + page
		ensureDir(page)
		rootDir = "../" * (len(dirs)-1)
		with open(page, 'w') as f:
			f.write(classHeader % (className, rootDir, className))
			for line in classData['lines']:
				f.write('<li>' +
						' '.join([tokenToHTML(token) for token in line]) +
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

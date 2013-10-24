import os, fnmatch

indexHeader = """<!doctype html>
<html>
<head>
	<meta charset="utf-8">
	<title>Java Cross-Indexer</title>
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

header = """<!doctype html>
<html>
<head>
	<meta charset="utf-8">
	<title>%s</title>
</head>
<body>
	<h1>%s</h1>
"""

footer = """</body>
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
Renderer
Converts data about Java classes into HTML pages
"""
class Renderer(object):
	def __init__(self, outputDir):
		self.path = outputDir

	"""
	Create and write an HTML page for a Java class
	"""
	def renderClass(self, classData):
		className = classData['name']
		print "Rendering class " + className
		page = os.path.join(self.path, *className.split('.'))+'.html'
		print "Writing " + page
		ensureDir(page)
		with open(page, 'w') as f:
			f.write(header % (className, className))
			f.write(footer)
			#f.write('<td><font style="background-color:%s;">%s<font></td>' %
					#(colour[j % len(colour)], k))

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

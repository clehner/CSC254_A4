import os

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
			f.write("<!doctype html>\n")

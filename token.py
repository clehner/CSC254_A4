
"""
Renderer
Converts data about Java classes into HTML pages
"""
class Token(object):
	# token types
	UNKNOWN = 0
	PLAIN = 1
	COMMENT = 2
	KEYWORD = 3

	def __init__(self, text, tok_type=PLAIN):
		self.text = text
		self.tok_type = tok_type

	def __str__(self):
		return self.text

	def __repr__(self):
		return "Token(" + repr(self.text) + ", " + str(self.tok_type) + ")"

	def get_type(self):
		if self.tok_type == Token.PLAIN:
			return 'plain'
		elif self.tok_type == Token.COMMENT:
			return 'comment'
		elif self.tok_type == Token.KEYWORD:
			return 'keyword'
		else:
			return 'unknown'


"""
Renderer
Converts data about Java classes into HTML pages
"""
class Token(object):
	# token types
	PLAIN = 0
	COMMENT = 1
	KEYWORD = 2

	token_names = {
		PLAIN: None,
		COMMENT: "comment",
		KEYWORD: "keyword"
	}

	def __init__(self, text, tok_type=PLAIN):
		self.text = text
		self.tok_type = tok_type

	def __str__(self):
		return self.text

	def __repr__(self):
		return "Token(" + repr(self.text) + ", " + str(self.tok_type) + ")"

	def get_type(self):
		return self.token_names[self.tok_type]

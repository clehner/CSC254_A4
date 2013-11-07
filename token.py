
"""
Token
Represents a unit of Java source code
"""
class Token(object):
	# token types
	PLAIN = 0
	COMMENT = 1
	KEYWORD = 2
	METHOD_INVOCATION = 3
	METHOD_DECLARATION = 4

	# method invocation/declaration properties
	method_type = None
	class_name = None

	token_names = {
		PLAIN: None,
		COMMENT: "comment",
		KEYWORD: "keyword",
		METHOD_INVOCATION: "method-invocation",
		METHOD_DECLARATION: "method-declaration"
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

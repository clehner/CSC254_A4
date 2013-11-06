import re
from token import Token

keywords = ['abstact','assert','boolean','break','byte','case','catch','const','continue','default','do','double','else','enum','extends','final','finally','float',\
'for','goto','if','implements','import','instanceof','int','interface','long','native','new','package','private','protected','public','return','short','static','strictfp',\
'super','switch','synchronized','this','throw','throws','transient','try','void','volatile','while']

scanner = re.Scanner([
	(r'//.+', lambda s, tok: Token(tok, Token.COMMENT)),
	(r'\s+', lambda s, tok: Token(tok, Token.PLAIN)),
	(r'[a-zA-Z0-9_]+(?=\()', lambda s, tok: Token(tok, Token.METHOD_INVOCATION)),
	(r'[^a-z]', lambda s, tok: Token(tok, Token.PLAIN)),
	(r'".*?(?:\\\\)*"', lambda s, tok: Token(tok, Token.PLAIN)),
	('|'.join(keywords), lambda s, tok: Token(tok, Token.KEYWORD)),
	(r'[a-zA-Z0-9_]*', lambda s, tok: Token(tok, Token.PLAIN)),
	#(r'\s+', None), # None == skip token.
])

'''
Scan lines into tokens.
takes a generator of strings
returns a generator of lists of tokens,
return a generator of tuple (token type, string)
without information dependent on javap data
'''
def scan(lines):
	rest = ''
	for line in lines:
		(toks, rest) = scanner.scan(rest + line)
		yield toks

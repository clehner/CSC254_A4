import re
from token import Token

keywords = ['abstact','assert','boolean','break','byte','case','catch','const','continue','default','do','double','else','enum','extends','final','finally','float',\
'for','goto','if','implements','import','instanceof','int','interface','long','native','new','package','private','protected','public','return','short','static','strictfp',\
'super','switch','synchronized','this','throw','throws','transient','try','void','volatile','while']

scanner = re.Scanner([
	(r'".*?(?:\\\\)*"', lambda s, tok: Token(tok, Token.PLAIN)),
	(r'/[/*].*', lambda s, tok: Token(tok, Token.COMMENT)),
	(r'\s+', lambda s, tok: Token(tok, Token.PLAIN)),
	('(?:' + '|'.join(keywords) + ')(?=[^a-zA-Z0-9_])', lambda s, tok: Token(tok, Token.KEYWORD)),
	(r'[a-zA-Z0-9_]+(?=\()', lambda s, tok: Token(tok, Token.METHOD_UNKNOWN)),
	(r'[^a-z]', lambda s, tok: Token(tok, Token.PLAIN)),
	(r'[a-zA-Z0-9_]*', lambda s, tok: Token(tok, Token.PLAIN)),
])

'''
Scan lines into tokens.
takes a generator of strings
returns a generator of lists of tokens,
without information dependent on javap data
'''
def scan(lines):
	rest = ''
	in_multiline_comment = False
	for line in lines:
		line = line.rstrip('\n')
		if in_multiline_comment:
			i = line.find("*/") + 2
			if i == 1:
				toks = [Token(line, Token.COMMENT)]
			else:
				comment = line[:i]
				line = line[i:]
				tok = Token(comment, Token.COMMENT)
				(toks, rest) = scanner.scan(rest + line)
				toks.insert(0, tok)
				in_multiline_comment = False
		else:
			(toks, rest) = scanner.scan(rest + line)
			if len(toks) > 0:
				last_tok = toks[-1]
				if last_tok.tok_type == Token.COMMENT and last_tok.text[:2] == '/*':
					in_multiline_comment = True
		yield toks

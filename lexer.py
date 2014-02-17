import ply.lex as lex
import Queue

class Token:
	'''
	The Token Class. Holds a type, line number, and value if necessary
	'''

	def __init__(self, token_type, line_no, value=None):
		self.type = token_type
		self.line_no = line_no
		self.value = (token_type, value, line_no)

	def __repr__(self):
		return "Token{}".format(self.value)


class Lexer:
	# List of Token names
	token_types = (
	"integer", "class", "type", "case",
	"at", "equals", "larrow", "rarrow",
	"lbrace", "rbrace", "le", "lt", "semi",
	"colon", "tilde", "lparen", "rparen",
	"divide", "times", "plus", "minus", 
	"else", "comma", "dot", "false", "true",
	"fi", "if", "inherits", "in", "isvoid",
	"let", "loop", "new", "not", "of",
	"pool", "then", "while", "esac", "string",
	"identifier"
	)

	def __init__(self):
		self.tokens = Queue.Queue()

	def add_token(self, token_type, line_no, value=None):
		if token_type in self.token_types:
			# t = lex.LexToken()
			# t.type = token_type
			# t.value = value
			# t.lineno = int(line_no)
			# t.lexpos = 0
			t = Token(token_type, line_no, value)
		else:
			print 'Invalid Token Type'
			return
		self.tokens.put(t)

	def token(self):
		if self.tokens.empty():
			return None
		else:
			return self.tokens.get()
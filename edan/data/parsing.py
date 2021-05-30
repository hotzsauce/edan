"""
parsing & evaluating expressions of series
"""

import numpy as np



# basic lexeme object
class Token(object):

	def __init__(self, token_type, value):
		self.type = token_type
		self.value = value

	def __repr__(self):
		return f"Token({self.type}, {self.value})"


# constants and keywords
COMMA = 'COMMA'
ID = 'ID'
NUMBER = 'NUMBER'
EOF = 'EOF'
LPARE = '('
RPARE = ')'

PLUS = 'PLUS'
MINUS = 'MINUS'
MUL = 'MUL'
DIV = 'DIV'
POWER = 'POWER'

E = 'e'
PI = 'pi'

# recognized functions
FUNCTION = 'FUNCTION'
EXP = 'exp'
LOG = 'log'
LN = 'ln'
LOG10 = 'log10'
SQRT = 'sqrt'
ABS = 'abs'
SIGN = 'sign'
SIN = 'sin'
COS = 'cos'
TAN = 'tan'
ASIN = 'asin'
ACOS = 'acos'
ATAN = 'atan'

RESERVED_KEYWORDS = {
	E: Token(NUMBER, np.e),
	PI: Token(NUMBER, np.pi),
	EXP: Token(FUNCTION, EXP),
	LOG: Token(FUNCTION, LOG),
	LN: Token(FUNCTION, LN),
	LOG10: Token(FUNCTION, LOG10),
	SQRT: Token(FUNCTION, SQRT),
	ABS: Token(FUNCTION, ABS),
	SIGN: Token(FUNCTION, SIGN),
	SIN: Token(FUNCTION, SIN),
	COS: Token(FUNCTION, COS),
	TAN: Token(FUNCTION, TAN),
	ASIN: Token(FUNCTION, ASIN),
	ACOS: Token(FUNCTION, ACOS),
	ATAN: Token(FUNCTION, ATAN)
}



# validating functions used by the Lexer
def is_valid_varchar(c):
	try:
		# excl. point is for BEA codes; semis for edan codes
		return c.isalnum() or c == '!' or c == ':'
	except AttributeError:
		return False

def is_valid_varname_start(c):
	try:
		return c.isalpha()
	except AttributeError:
		return False

def is_valid_numchar(c):
	try:
		return c.isdigit()
	except AttributeError:
		return False




# lexer section
class Lexer(object):

	def __init__(self, text):
		self.text = text

		self.pos = self.token_pos = 0
		self.current_char = self.text[self.pos]

		self.tokenize()

	def error(self, char):
		raise Exception(f"Invalid character: {repr(char)}")

	def advance(self):
		"""advance the char position and set the new current char"""
		self.pos += 1
		try:
			self.current_char = self.text[self.pos]
		except IndexError:
			self.current_char = None

	def peek(self):
		peek_pos = self.pos + 1
		try:
			return self.text[peek_pos]
		except IndexError:
			return None

	def _skip_whitespace(self):
		while self.current_char is not None and self.current_char.isspace():
			self.advance()

	def _id(self):
		result = ''
		while is_valid_varchar(self.current_char):
			result += self.current_char
			self.advance()
		token = RESERVED_KEYWORDS.get(result, Token(ID, result))
		return token

	def _number(self):
		result = ''
		while self.current_char is not None and is_valid_numchar(self.current_char):
			result += self.current_char
			self.advance()

		try:
			token = Token(NUMBER, float(result))
		except ValueError:
			# too many decimals
			raise ValueError(result) from None

		return token

	def next_token(self):

		while self.current_char is not None:

			if self.current_char.isspace():
				self._skip_whitespace()

			if is_valid_varname_start(self.current_char):
				return self._id()

			if is_valid_numchar(self.current_char):
				return self._number()

			if self.current_char == '*' and self.peek() == '*':
				self.advance()
				self.advance()
				return Token(POWER, '**')

			if self.current_char == '*':
				self.advance()
				return Token(MUL, '*')

			if self.current_char == '/':
				self.advance()
				return Token(DIV, '/')

			if self.current_char == '+':
				self.advance()
				return Token(PLUS, '+')

			if self.current_char == '-':
				self.advance()
				return Token(MINUS, '-')

			if self.current_char == '(':
				self.advance()
				return Token(LPARE, '(')

			if self.current_char == ')':
				self.advance()
				return Token(RPARE, ')')

			if self.current_char == ',':
				self.advance()
				return Token(COMMA, ',')

			if self.current_char is not None:
				self.error(self.current_char)

	def tokenize(self):
		self.token_stream = []

		while self.current_char is not None:
			t = self.next_token()
			if isinstance(t, Token):
				self.token_stream.append(t)
		self.token_stream.append(Token(EOF, None))

	def get_next_token(self):
		token = self.token_stream[self.token_pos]
		self.token_pos += 1
		return token




# AST section
class AST(object):

	def __init__(self):
		pass

	def __repr__(self):
		return f"<{type(self).__name__} Object>"


class BinaryOp(AST):

	def __init__(self, left, op, right):
		self.left, self.op, self.right = left, op, right


class UnaryOp(AST):

	def __init__(self, op, expr):
		self.op, self.expr = op, expr


class Num(AST):

	def __init__(self, token):
		self.token, self.value = token, token.value


class Var(AST):

	def __init__(self, token):
		self.token, self.value = token, token.value


class Function(AST):

	def __init__(self, token, expr):
		self.token, self.value, self.expr = token, token.value, expr




# Parsing section
class Parser(object):

	def __init__(self, lexer):
		self.lexer = lexer
		self.current_token = self.lexer.get_next_token()

	def error(self):
		raise Exception(self.current_token)

	def eat(self, token_type):
		if self.current_token.type == token_type:
			self.current_token = self.lexer.get_next_token()
		else:
			self.error()

	def peek(self):
		return self.lexer.get_next_token()

	def atom(self):
		token = self.current_token

		if token.type == ID:
			node = Var(token)
			self.eat(ID)
			return node
		elif token.type == NUMBER:
			self.eat(NUMBER)
			return Num(token)
		elif token.type == LPARE:
			self.eat(LPARE)
			node = self.expr()
			self.eat(RPARE)
			return node
		elif token.type in (MINUS, PLUS):
			self.eat(token.type)
			node = UnaryOp(op=token, expr=self.term())
		else:
			self.error()

	def call(self):
		node = self.atom()

		while self.current_token.type == FUNCTION:
			token = self.current_token
			self.eat(FUNCTION)
			self.eat(LPARE)

			node = Function(token=token, expr=self.expr())
			self.eat(RPARE)

		return node

	def exponent(self):
		node = self.call()

		while self.current_token.type == POWER:
			token = self.current_token
			self.eat(POWER)

			node = BinaryOp(left=node, op=token, right=self.exponent())

		return node

	def term(self):
		node = self.exponent()

		while self.current_token.type in (MUL, DIV):
			token = self.current_token
			self.eat(token.type)

			node = BinaryOp(left=node, op=token, right=self.exponent())

		return node

	def expr(self):
		node = self.term()

		while self.current_token.type in (PLUS, MINUS):
			token = self.current_token
			self.eat(token.type)

			node = BinaryOp(left=node, op=token, right=self.term())

		return node

	def parse(self):
		return self.expr()




# Interpreting & Evaluating section
class ABCVisitor(object):

	def __init__(self, tree):
		self.tree = tree

	def visit(self, node):
		method = 'visit_' + type(node).__name__
		visitor = getattr(self, method, self._nonexistent_node)
		return visitor(node)

	def _nonexistent_node(self, node):
		raise Exception(f"No visit_{type(node).__name__} method")

	def walk(self):
		return self.visit(self.tree)


class CodeLocator(ABCVisitor):
	"""
	find the series identifiers
	"""

	def __init__(self, tree):
		super().__init__(tree)
		self.codes = set()

	def visit_Num(self, node):
		pass

	def visit_Var(self, node):
		self.codes.add(node.value)

	def visit_UnaryOp(self, node):
		self.visit(node.expr)

	def visit_BinaryOp(self, node):
		self.visit(node.left)
		self.visit(node.right)

	def visit_Function(self, node):
		self.visit(node.expr)


class Evaluator(ABCVisitor):
	"""
	evaluate an expression with series codes in it
	"""
	def __init__(self, tree, series):
		super().__init__(tree)
		self.series = series

	def visit_Num(self, node):
		return node.value

	def visit_Var(self, node):
		print(node.value)
		data = self.series[node.value]
		return data

	def visit_UnaryOp(self, node):
		if node.op.type == PLUS:
			return self.visit(node.expr)
		elif node.op.type == MINUS:
			return - self.visit(node.expr)

	def visit_BinaryOp(self, node):
		if node.op.type == PLUS:
			return self.visit(node.left) + self.visit(node.right)
		elif node.op.type == MINUS:
			return self.visit(node.left) - self.visit(node.right)
		elif node.op.type == MUL:
			return self.visit(node.left) * self.visit(node.right)
		elif node.op.type == DIV:
			return self.visit(node.left) / self.visit(node.right)
		elif node.op.type == POWERS:
			return self.visit(node.left) ** self.visit(node.right)

	def visit_Function(self, node):
		f = node.value

		if f == EXP:
			return np.exp(self.visit(node.expr))
		elif (f == LOG) or (f == LN):
			return np.log(self.visit(node.expr))
		elif f == LOG10:
			return np.log10(self.visit(node.expr))
		elif f == SQRT:
			return np.sqrt(self.visit(node.expr))
		elif f == ABS:
			return np.abs(self.visit(node.expr))
		elif f == SIGN:
			return np.sign(self.visit(node.expr))
		elif f == SIN:
			return np.sin(self.visit(node.expr))
		elif f == COS:
			return np.cos(self.visit(node.expr))
		elif f == TAN:
			return np.tan(self.visit(node.expr))
		elif f == ASIN:
			return np.arcsin(self.visit(node.expr))
		elif f == ACOS:
			return np.arccos(self.visit(node.expr))
		elif f == ATAN:
			return np.arctan(self.visit(node.expr))




# forward-facing functions
def is_expression(expr: str):
	"""
	returns False if `expr` is just a single series code; otherwise returns True

	Parameters
	----------
	expr : str
	"""
	ops = r'+-*/)('
	return any(char in expr for char in ops)


def parse_and_extract_series(expr: str):
	"""
	translate the expression into an Abstract Syntax Tree and return it, and a
	set of the series codes that are in it

	Parameters
	----------
	expr: str
	"""
	lexer = Lexer(expr)
	print(lexer.token_stream)
	parser = Parser(lexer)

	tree = parser.parse()

	locator = CodeLocator(tree)
	locator.walk()

	return tree, list(locator.codes)


def evaluate_expr(tree: AST, series: dict):
	"""
	given the AST & dictionary of {code: Series}, evaluate the expression

	Parameters
	----------
	tree : AST
		the abstract syntax tree of the expression
	series : dict
		dictionary of series
	"""
	ev = Evaluator(tree, series)
	return ev.walk()

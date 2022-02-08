import ply.lex as lex

tokens = (
	'VAR', 'BEGIN', 'END', "COMMA", 'COLON', 'SEMICOLON', 'ASSIGN', 'ID',
	'READ', 'WRITE',
	'NUMBER', 'PLUS', 'MINUS', 'MULT', 'DIV', 'MOD',
	'EQUALS', 'NEQUALS', 'LESS', 'GREATER', 'LESSEQ', 'GREATEREQ',
	'PAREN_OPEN', 'PAREN_CLOSE',  'IF', 'THEN', 'ELSE', 'ENDIF',
	'FOR', 'FROM', 'TO', 'DOWNTO', 'DO', 'ENDFOR',
	'WHILE', 'ENDWHILE', 'REPEAT', 'UNTIL',
)

t_VAR = r'VAR'
t_BEGIN = r'BEGIN'
t_END = r'END'
t_COMMA = r','
t_COLON = r':'
t_SEMICOLON = r';'
t_ASSIGN = r'ASSIGN'
t_ID = r'[_a-z]+'
t_READ = r'READ'
t_WRITE = r'WRITE'
t_PLUS = r'PLUS'
t_MINUS = r'MINUS'
t_MULT = r'TIMES'
t_DIV = r'DIV'
t_MOD = r'MOD'
t_EQUALS = r'EQ'
t_NEQUALS = r'NEQ'
t_LESS = r'LE'
t_GREATER = r'GE'
t_LESSEQ = r'LEQ'
t_GREATEREQ = r'GEQ'
t_PAREN_OPEN = r'\['
t_PAREN_CLOSE = r'\]'
t_IF = r'IF'
t_THEN = r'THEN'
t_ELSE = r'ELSE'
t_ENDIF = r'ENDIF'
t_FOR = r'FOR'
t_FROM = r'FROM'
t_TO = r'TO'
t_DOWNTO = r'DOWNTO'
t_DO = r'DO'
t_ENDFOR = r'ENDFOR'
t_WHILE = r'WHILE'
t_ENDWHILE = r'ENDWHILE'
t_REPEAT = r'REPEAT'
t_UNTIL = r'UNTIL'


def t_NUMBER(t):
	r'-?\d+'
	t.value = int(t.value)
	return t


def t_COMMENT(t):
	r'\([^\)]*\)'
	pass


t_ignore = ' \t'


def t_newline(t):
	r'\r?\n+'
	t.lexer.lineno += len(t.value)


def t_error(t):
	print("Illegal character '%s'" % t.value[0])
	t.lexer.skip(1)


def p_error(p):
	print("Syntax error in line %d" % p.lineno)


lexer = lex.lex()

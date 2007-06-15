"""
Methods to convert a simplified filter string into an SQL query
"""
import ply.lex as lex
import ply.yacc as yacc

class ParserSyntaxError(Exception):
   pass

# list of tokens
tokens = (
   'FIELD',
   'AND',
   'OR',
   'NOT',
   'EQUALS',
   'LIKE',
   'VALUE',
   'LPAREN',
   'RPAREN',
   'QUOTE'
   )

# reserved words
reserved = {
   'and'       : 'AND',
   'or'        : 'OR',
   'is'        : 'EQUALS',
   'contains'  : 'LIKE',
   'artist'    : 'FIELD',
   'album'     : 'FIELD',
   'title'     : 'FIELD',
   'genre'     : 'FIELD',
   'dirty'     : 'FIELD',
   }

# regexps
t_AND     = r'&'
t_OR      = r'\|'
t_EQUALS  = r'='
t_LIKE    = r'~'
t_LPAREN  = r'\(|\[|\{'
t_RPAREN  = r'\)|\]|\}'
t_QUOTE   = r'"|\''
t_ignore  =  ' \t\n'
def t_error(t):
   print "Illegal character '%s'" % t.value[0]
   t.lexer.skip(1)

def t_value(t):
   r'["\'].*?["\']'
   t.type  = 'VALUE'
   t.value = t.value[1:-1]
   return t

def t_ID(t):
   r'\w+'
   t.type = reserved.get(t.value, 'VALUE')
   return t

lex.lex()

# ----------------------------------------------------------------------

def p_statement(p):
   '''statement : expression
                | statement OR expression
                | statement AND expression
                | LPAREN statement RPAREN'''
   if len(p) == 2:
      p[0] = p[1]
   elif len(p) == 4 and p[2] in ['and', '&']:
      p[0] = "%s AND %s" % (p[1], p[3])
   elif len(p) == 4 and p[2] in ['or', '|']:
      p[0] = "%s OR %s" % (p[1], p[3])
   elif len(p) == 4 and p[1] in ['(', '{', '[']:
      p[0] = "(%s)" % p[2]
   return p[0]

def p_expression(p):
   '''expression : FIELD EQUALS VALUE
                | FIELD LIKE VALUE'''
   # map field names to correct db names (a=artist, s=song, b=album, g=genre)
   if p[1]   == 'artist': p[1] = 'a.name'
   elif p[1] == 'album':  p[1] = 'b.name'
   elif p[1] == 'song':   p[1] = 's.title'
   elif p[1] == 'genre':  p[1] = 'g.name'

   if p[2] in ['is', '=']:
      p[0] = "%s = '%s'" % (p[1], p[3])
   elif p[2] in ['contains', '~']:
      p[0] = "%s LIKE '%%%s%%'" % (p[1], p[3])

def p_error(t):
   raise ParserSyntaxError("Syntax error at '%s'" % t.value)

yacc.yacc()

# ----------------------------------------------------------------------

def getTokens(data):
   lex.input(data)
   while(1):
      tok = lex.token()
      if not tok: break
      print tok

def parseQuery(data):
   return yacc.parse(data)

if __name__ == "__main__":
   testinput = [
      '(genre = rock | genre = "Heavy Metal" or genre = Industrial) & title ~ wicked',
      'artist is "Nine Inch Nails" or artist is "Black Sabbath" or artist is Clawfinger or album contains "Nativity in Black" or artist is Incubus'
   ]
   for line in testinput:
      print 80*"="
      print 'Simplified query: "%s"' % line.strip()
      print 80*"-"
      print "result:", parseQuery(line)
      print


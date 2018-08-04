# pylint: disable=invalid-name
#
# ply has a naming convention which is not PEP8 compliant. Which is why the
# invalid-name message is disabled.
"""
Methods to convert a simplified filter string into an SQL query
"""
import logging

import ply.lex
import ply.yacc

LOG = logging.getLogger(__name__)


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
    'and': 'AND',
    'or': 'OR',
    'is': 'EQUALS',
    'contains': 'LIKE',
    'artist': 'FIELD',
    'album': 'FIELD',
    'title': 'FIELD',
    'genre': 'FIELD',
    'dirty': 'FIELD',
}

# regexps
t_AND = r'&'
t_OR = r'\|'
t_EQUALS = r'='
t_LIKE = r'~'
t_LPAREN = r'\(|\[|\{'
t_RPAREN = r'\)|\]|\}'
t_QUOTE = r'"|\''
t_ignore = ' \t\n\r'


def t_error(t):
    LOG.debug("Skipping illegal character %r", t.value[0])
    t.lexer.skip(1)


def t_value(t):
    r'["\'].*?["\']'
    t.type = 'VALUE'
    t.value = t.value[1:-1]
    return t


def t_ID(t):
    r'\w+'
    t.type = reserved.get(t.value, 'VALUE')
    return t


ply.lex.lex()

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
    if p[1] == 'artist':
        p[1] = 'artist.name'
    elif p[1] == 'album':
        p[1] = 'album.name'
    elif p[1] == 'title':
        p[1] = 'song.title'
    elif p[1] == 'genre':
        p[1] = 'genre.name'

    if p[2] in ['is', '=']:
        p[0] = "%s = '%s'" % (p[1], p[3])
    elif p[2] in ['contains', '~']:
        p[0] = "%s LIKE '%s'" % (p[1], p[3].replace('*', '%'))


def p_error(t):
    raise ParserSyntaxError("Syntax error at '%s'" % t.value)


ply.yacc.yacc()

# ----------------------------------------------------------------------


def get_tokens(data):
    '''
    Helper function to retrieve the tokens from a query input.

    Useful for debugging
    '''
    ply.lex.input(data)
    while True:
        tok = ply.lex.token()
        if not tok:
            break
        yield tok


def parse_query(data):
    return ply.yacc.parse(data)

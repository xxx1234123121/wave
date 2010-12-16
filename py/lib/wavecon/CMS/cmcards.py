"""
Overview
--------

This module provides functions for interacting with CMS cmcards files.
Currently, it contains a parser for deconstructing a cmcards file into a python
dict.

**Development Status:**
  **Last Modified:** December 16, 2010 by Charlie Sharpsteen

"""


#------------------------------------------------------------------------------
#  Imports from Python 2.7 standard library
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
#  Imports from third party libraries
#------------------------------------------------------------------------------
from pyparsing import( ParserElement, Literal, Keyword, Word, Group, Dict,
    Combine, Optional, Suppress, ZeroOrMore, OneOrMore, nums, alphanums,
    quotedString, restOfLine, lineEnd, removeQuotes)


#------------------------------------------------------------------------------
#  Imports from other CMS submodules
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
#  cmcards parser
#------------------------------------------------------------------------------

# Token Transformation Functions
#===============================
def classifyAtom(tokens):
  atom = tokens[0]
  if atom == 'ON' or atom == 'YES':
    return True
  elif atom == 'OFF' or atom == 'NO':
    return False
  else:
    return atom


# Token Definitions
#==================

# Every component of the parser inherits from ParserElement. Setting the
# whitespace characters here means that the parser will be line-oriented. By
# default it would use ' \t\r\n' which means that the parser would continue
# matching tokens accross line boundaries. Since the num_int, atom and
# config_key tokens are similar, this behavior poses a problem.
ParserElement.setDefaultWhitespaceChars(' \t')

comment_char = Literal('!')
config_key = Word(alphanums + '_')
jdate = Combine(Literal('0') + Word(nums))
num_int = Word(nums).\
  setParseAction(lambda tokens: int(tokens[0]))
num_dble = Word(nums + '.').\
  setParseAction(lambda tokens: float(tokens[0]))
string_data = quotedString.\
  setParseAction(removeQuotes)
atom = Word(alphanums).\
  setParseAction(classifyAtom)
end_of_file = Keyword('END_PARAMETERS')


# Parser Components
#==================

# The data contained on each line is a whitespace-delimited series of
# components.  The config_data parser tries to match each of the components
# listed below and returns the first match. In the case where a number could
# match both the pattern for an integer and a float the longest match is used.
# In the case of a tie, an integer is returned.  This prevents 3.75 from being
# split into 3 and 0.75.
config_data = Group(OneOrMore(quotedString | jdate | (num_int ^ num_dble) | atom))

config_line = Group( config_key + config_data ) + Suppress(lineEnd)
comment = comment_char + Optional(restOfLine)

cmcards_parser = Dict(
  ZeroOrMore( config_line | Suppress(comment) | Suppress(lineEnd) )
) + Suppress(end_of_file)

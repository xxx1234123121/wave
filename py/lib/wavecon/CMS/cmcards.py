"""
Overview
--------

This module provides functions for interacting with CMS cmcards files.
Currently, it contains a parser for deconstructing the cmcards into a python
dict.

**Development Status:**
  **Last Modified:** December 15, 2010 by Charlie Sharpsteen

"""


#------------------------------------------------------------------------------
#  Imports from Python 2.7 standard library
#------------------------------------------------------------------------------
from datetime import datetime
from os import path


#------------------------------------------------------------------------------
#  Imports from third party libraries
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
#  Imports from other CMS submodules
#------------------------------------------------------------------------------
from pyparsing import *

#------------------------------------------------------------------------------
#  cmcards parser
#------------------------------------------------------------------------------
comment_char = Literal('!')
jdate = Combine(Literal('0') + Word(nums))
num_dble = Word(nums + '.').setParseAction(lambda tokens: float(tokens[0]))
string_data = quotedString.setParseAction(removeQuotes)
atom = Keyword('ON') | Keyword('OFF') | Keyword('EXPLICIT') | Keyword('IMPLICIT')

config_key = Word(alphanums + '_')
config_data = Group(OneOrMore(quotedString | jdate | num_dble | atom))

comment = comment_char + Optional(restOfLine)
config_line = Group(config_key + config_data + Suppress(lineEnd))

cmcards_parser = Dict(
  ZeroOrMore(
    config_line | Suppress(comment)
  )
)

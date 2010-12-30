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
from datetime import timedelta 


#------------------------------------------------------------------------------
#  Imports from third party libraries
#------------------------------------------------------------------------------
from pyparsing import( ParserElement, Literal, Keyword, Word, Group, Dict,
    Combine, Optional, Suppress, ZeroOrMore, OneOrMore, nums, alphanums,
    quotedString, restOfLine, lineEnd, removeQuotes)


#------------------------------------------------------------------------------
#  Imports from other CMS submodules
#------------------------------------------------------------------------------
from wavecon.util import ISODateString
from wavecon.config import CMS_TEMPLATES, CMSConfig

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

#------------------------------------------------------------------------------
#  cmcards generator
#------------------------------------------------------------------------------
DEFAULT_SIM_PARAMS = {
  'sim_name': 'humboldt-example',
  'sim_label': 'test_run',
  'sim_starttime': ISODateString('2010-12-01T00:00:00'),
  'sim_runtime': 24.0,
  'sim_timestep': 1.0,
  'sim_ramptime': 0.25
}

def gen_cmcards_file(output_path, params = DEFAULT_SIM_PARAMS):
  cmcards_template = CMS_TEMPLATES.get_template('FLOW.cmcards')
  cmcards_config = CMSConfig(params['sim_name']).load_sim_config()

  cmcards_config['sim_start_date'] = params['sim_starttime'].strftime('%y%j')
  cmcards_config['sim_start_hour'] = params['sim_starttime'].strftime('%H')

  # Godawful, ugly code coming up---avert your eyes!
  sim_output_times = [0.0, 0.0, 0.0]
  n_tstep = 1
  sim_endtime = params['sim_starttime'] + timedelta(hours = params['sim_runtime'])
  time_step = params['sim_timestep']
  while (params['sim_starttime'] + timedelta(hours = time_step)) <= sim_endtime:
    sim_output_times.append(time_step)
    sim_output_times.append(time_step)
    sim_output_times.append(0.0)

    time_step += params['sim_timestep']
    n_tstep += 1

  sim_output_times.insert(0, n_tstep)
  sim_output_times = ' '.join(str(x) for x in sim_output_times)

  cmcards_config['sim_output_times'] = sim_output_times
  cmcards_config.update(params)

  with open(output_path, 'w') as cmcards_output:
    cmcards_output.writelines(cmcards_template.render(**cmcards_config))

  return None


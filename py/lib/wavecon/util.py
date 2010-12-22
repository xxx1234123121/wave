"""
Overview
--------

Common functions that don't really have any other place to be.


**Development Status:**
  **Last Modified:** December 22, 2010 by Charlie Sharpsteen
"""
#------------------------------------------------------------------------------
#  Conversion of compass directions
#------------------------------------------------------------------------------
from math import degrees, radians
def degrees_to_compass(deg_angle):
  angle = 90 - deg_angle
  if angle < 0:
    angle = angle + 360

  return angle


def compass_degrees(rad_angle):
  return degrees_to_compass(degrees(rad_angle))


def compass_to_degrees(comp_angle):
  if comp_angle > 0:
    comp_angle = comp_angle - 360

  return 90 - comp_angle

def compass_to_angle(comp_angle):
  return radians(compass_to_degrees(comp_angle))

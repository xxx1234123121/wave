#!/usr/bin/env python

import os,sys
libdir = os.path.abspath('.')+'/../lib/'
sys.path.insert( 0, libdir )
from wavecon import GETman
from wavecon.config import CMSconfig

if __name__ == '__main__':

    GETman.getWAVE(CMSconfig)
    GETman.getWIND(CMSconfig)

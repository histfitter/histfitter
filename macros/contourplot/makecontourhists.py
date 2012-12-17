#!/bin/env python

import sys,os,ROOT

ROOT.gROOT.ProcessLine('#include "contourmacros/m0_vs_m12_nofloat.C"')

#/********************************
#
#REMEMBER that this file uses summary_harvest_tree_description.h 
#to determine how to read your list files.  You will need to regenerate
#that file in order to read a list file with a different format from
#makelistfiles.C
#
#********************************/

if len(sys.argv)>1:
    if sys.argv[1]!='-b': infiles = sys.argv[1:]
    elif len(sys.argv)>2: infiles = sys.argv[2:]
    else:
        print 'Please specify an input file'
        sys.exit(1)
print 'Using files',infiles

for afile in infiles:
    if ',' in afile:
        for bfile in afile.split(','): ROOT.m0_vs_m12_nofloat(bfile)
    else: ROOT.m0_vs_m12_nofloat(afile)


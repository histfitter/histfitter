#!/bin/env python

import os,sys,ROOT

print 'Running makecontourplots'

if len(sys.argv)>1:
    if sys.argv[1]!='-b': infiles = sys.argv[1:]
    elif len(sys.argv)>2: infiles = sys.argv[2:]
    else:
        print 'Please specify an input file(s)'
        sys.exit(1)
print 'Using files',infiles

if 'MSUGRA' in infiles:
    ROOT.gROOT.ProcessLine('#include "contourmacros/SUSY_m0_vs_m12_all_withBand_cls_new.C"')
else:
    execfile( 'contourmacros/compare_limits_SM.py' )

print 'Calling over to macro'
compare_limits_SM( infiles , 'Multijet Options' , 21. , beginString='MultiJet_' , endString='_Gtt')


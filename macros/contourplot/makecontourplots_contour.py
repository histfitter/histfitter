#!/bin/env python

import os,sys,ROOT

print 'Running makecontourplots'

if len(sys.argv)>1:
    #if sys.argv[1]!='-b': infiles = sys.argv[1:]
    outputname = sys.argv[1]
    if len(sys.argv)>2: infiles = sys.argv[2:]
else:
    print 'Please specify an input file(s)'
    sys.exit(1)
print 'Using files',infiles

if len(infiles)>1:
    file_up = infiles[1]
else:
    file_up = None
   
if len(infiles)>2:
    file_down = infiles[2]
else:
    file_down = None   

print 'Calling over to macro'

#if 'HiggsSU' in infiles[0]:
#    ROOT.gROOT.LoadMacro("contourmacros/SUSY_m0_vs_m12_all_withBand_cls_new.C")
#    ROOT.limit_plot( infiles[0] , file_up , file_down, "", 'hard 1-lepton + jets + E_{T}^{miss}', 14.3, False, 1, True, False, True, False )
#else:
execfile( 'contourmacros/limit_plot_SM.py' )
if not 'HiggsSU' in infiles[0]:
    execfile("summary_harvest_tree_description.py")
else: 
    execfile("summary_harvest_tree_description_HiggsSU.py")
#limit_plot_SM( infiles[0] , file_up , file_down, outputname , 'hard 1-lepton + jets + E_{T}^{miss}', 20.3, True, False, True )
limit_plot_SM( infiles[0] , file_up , file_down, outputname , 'Combination', 20.3, True, False, True )


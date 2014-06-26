#!/bin/env python

import os,sys,ROOT,math

if len(sys.argv)>1:
    if sys.argv[1]!='-b': infile = sys.argv[1]
    elif len(sys.argv)>2: infile = sys.argv[2]
    else:
        print 'Please specify an input file'
        sys.exit(1)
print 'Using file',infile

ROOT.gSystem.Load('libSusyFitter.so')

# input root file with HypoTestInverterResults, 
# as obtained from running: 
# SusyFitter.py -f python/MySimpleChannelConfig.py

if 'GG1step' in infile or ('onestep' in infile and not 'SS_' in infile):
    # search for objects labelled
    format     = 'hypo_SM_GG1step_%f_%f_%f'
    
    # interpret %f's above respectively as (seperated by ':')
    interpretation = 'm0:mch:m12'
    
    # cut string on m0 and m12 value, eg "m0>1200"
    cutStr = '1'
    #cutStr = 'm12==60' # accept only certain LSP masses (for one-step decays)
    #cutStr = 'm12!=60' # accept only certain LSP masses (for one-step decays)
    outputfile = ROOT.CollectAndWriteHypoTestResults( infile, format, interpretation, cutStr ) ;
    
    #cutStr = 'm12!=60' # accept only certain LSP masses (for one-step decays)
    #outputfile = ROOT.CollectAndWriteHypoTestResults( infile, format, interpretation, cutStr ) ;

if 'SS1step' in infile or ('onestep' in infile and not 'GG_' in infile):
    # search for objects labelled
    format     = 'hypo_SM_SS1step_%f_%f_%f'
    
    # interpret %f's above respectively as (seperated by ':')
    interpretation = 'm0:mch:m12'
    
    # cut string on m0 and m12 value, eg "m0>1200"
    #cutStr = 'm12==60' # accept only certain LSP masses (for one-step decays)
    cutStr = '1'
    outputfile = ROOT.CollectAndWriteHypoTestResults( infile, format, interpretation, cutStr ) ;
    
    #cutStr = 'm12!=60' # accept only certain LSP masses (for one-step decays)
    #outputfile = ROOT.CollectAndWriteHypoTestResults( infile, format, interpretation, cutStr ) ;

if 'Gtt' in infile:
    # search for objects labelled
    format     = 'hypo_Gtt_%f_%f'
    
    # interpret %f's above respectively as (seperated by ':')
    interpretation = 'm0:m12'

    # cut string on m0 and m12 value, eg "m0>1200"
    cutStr = '1' # accept only certain LSP masses (for one-step decays)
    outputfile = ROOT.CollectAndWriteHypoTestResults( infile, format, interpretation, cutStr ) ;

if 'Higgsino' in infile:
    # search for objects labelled
    format     = 'hypo_Higgsino_%f_%f'

    # interpret %f's above respectively as (seperated by ':')
    interpretation = 'm0:m12'

    # cut string on m0 and m12 value, eg "m0>1200"
    cutStr = '1' # accept only certain LSP masses (for one-step decays)
    outputfile = ROOT.CollectAndWriteHypoTestResults( infile, format, interpretation, cutStr ) ;

if 'GG2CNsl' in infile:
    # search for objects labelled
    #format = 'hypo_SM_GG2CNsl_%f_%f_%f_%f'
    format = 'hypo_SM_GG2CNsl_%f_%f_%f'

    # interpret %f's above respectively as (seperated by ':')
    #interpretation = 'm0:mch:mno:m12'
    interpretation = 'm0:mch:m12'

    # cut string on m0 and m12 value, eg "m0>1200"
    cutStr = '1' # accept only certain LSP masses (for one-step decays)
    outputfile = ROOT.CollectAndWriteHypoTestResults( infile, format, interpretation, cutStr ) ;

if 'SS2CNsl' in infile:
    # search for objects labelled
    #format = 'hypo_SM_SS2CNsl_%f_%f_%f_%f'
    format = 'hypo_SM_SS2CNsl_%f_%f_%f'

    # interpret %f's above respectively as (seperated by ':')
    #interpretation = 'm0:mch:mno:m12'
    interpretation = 'm0:mch:m12'

    # cut string on m0 and m12 value, eg "m0>1200"
    cutStr = '1' # accept only certain LSP masses (for one-step decays)
    outputfile = ROOT.CollectAndWriteHypoTestResults( infile, format, interpretation, cutStr ) ;
    
if 'GG2WWZZ' in infile:
    # search for objects labelled
    #format = 'hypo_SM_GG2CNsl_%f_%f_%f_%f'
    format = 'hypo_SM_GG2WWZZ_%f_%f_%f'

    # interpret %f's above respectively as (seperated by ':')
    #interpretation = 'm0:mch:mno:m12'
    interpretation = 'm0:mch:m12'

    # cut string on m0 and m12 value, eg "m0>1200"
    cutStr = '1' # accept only certain LSP masses (for one-step decays)
    outputfile = ROOT.CollectAndWriteHypoTestResults( infile, format, interpretation, cutStr ) ;

if 'SS2WWZZ' in infile:
    # search for objects labelled
    #format = 'hypo_SM_SS2CNsl_%f_%f_%f_%f'
    format = 'hypo_SM_SS2WWZZ_%f_%f_%f'

    # interpret %f's above respectively as (seperated by ':')
    #interpretation = 'm0:mch:mno:m12'
    interpretation = 'm0:mch:m12'

    # cut string on m0 and m12 value, eg "m0>1200"
    cutStr = '1' # accept only certain LSP masses (for one-step decays)
    outputfile = ROOT.CollectAndWriteHypoTestResults( infile, format, interpretation, cutStr ) ;    
    
if 'HiggsSU' in infile:
    # search for objects labelled
    #format = 'hypo_SM_SS2CNsl_%f_%f_%f_%f'
    format = 'hypo_HiggsSU_%f_%f'

    # interpret %f's above respectively as (seperated by ':')
    #interpretation = 'm0:mch:mno:m12'
    interpretation = 'm0:m12'

    # cut string on m0 and m12 value, eg "m0>1200"
    cutStr = '1' # accept only certain LSP masses (for one-step decays)
    outputfile = ROOT.CollectAndWriteHypoTestResults( infile, format, interpretation, cutStr ) ; 
    
if 'pMSSM' in infile:
    # search for objects labelled
    #format = 'hypo_SM_SS2CNsl_%f_%f_%f_%f'
    format = 'hypo_pMSSM_%f'

    # interpret %f's above respectively as (seperated by ':')
    #interpretation = 'm0:mch:mno:m12'
    interpretation = 'm0'

    # cut string on m0 and m12 value, eg "m0>1200"
    cutStr = '1' # accept only certain LSP masses (for one-step decays)
    outputfile = ROOT.CollectAndWriteHypoTestResults( infile, format, interpretation, cutStr ) ;     
       
if 'SoftLepton' in infile:
    # search for objects labelled
    format     = 'hypo_%f_%f_%f'
    
    # interpret %f's above respectively as (seperated by ':')
    interpretation = 'm0:mch:m12'
    
    # cut string on m0 and m12 value, eg "m0>1200"
    #cutStr = 'm12==60' # accept only certain LSP masses (for one-step decays)
    cutStr = '1'
    outputfile = ROOT.CollectAndWriteHypoTestResults( infile, format, interpretation, cutStr ) ;
    
    #cutStr = 'm12!=60' # accept only certain LSP masses (for one-step decays)
    #outputfile = ROOT.CollectAndWriteHypoTestResults( infile, format, interpretation, cutStr ) ;
    
    
# load the listfile in root with:
# root -l summary_harvest_tree_description.h
# or look directly at the outputfile in vi.


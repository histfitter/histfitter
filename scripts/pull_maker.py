#!/bin/env python
"""
 * Project : HistFitter - A ROOT-based package for statistical data analysis      *
 * Package : HistFitter                                                           *
 * Script  : pull_maker.py                                                        *
 *                                                                                *
 * Description:                                                                   *
 *      Script for producing after-fit profiling/pulling plot for all             *          
 *       parameters floating in the fit, taking fit log as input                  *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group                                                          *
 *      Zachary Marshall, LBNL, Berkeley <zmarshal@cern.ch>                       *
 *      Emma Sian Kuwertz, KTH, Stockholm <ekuwertz@cern.ch>                      *
 *      Evgeniy Khramov, JINR, Dubna <Evgeniy.Khramov@cern.ch>                    *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.
"""

import ROOT,os
ROOT.SetSignalPolicy( ROOT.kSignalFast )
ROOT.gROOT.SetBatch(True)

import sys, getopt

def main(argv):
    """
    main function call

    @param argv Arguments from user to define input file (-i <inputFile>) and output file name (-o <outputName>)
    """
    inputfile = ''
    outputfile = 'test_out'
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print 'pull_maker.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'pull_maker.py -i <inputfile> -o <outputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        print 'Input file is "', inputfile
        print 'Output file is "', outputfile

    if not inputfile:
        print "No input file defined, please define with '-i <InputFile>'"
        sys.exit(2)

    uncRes = [[],[],[],[]]
        
    log = open(inputfile,'r')
    switchOn = False
    muIDX = -1
    for aline in log.readlines():
        if 'FinalValue' in aline:
            switchOn = True
            uncRes = [[],[],[],[]]
            muIDX = -1
            continue
        if '------------' in aline: continue
        if switchOn:
            if 'gamma_stat' in aline: continue
            if 'QCDNorm' in aline: continue
            if 'mu_' in aline and muIDX<0:
                muIDX=len(uncRes[0])
            if len(aline.strip())<3:
                switchOn=False
                continue
                              
            if 'mu_' in aline:
                uncRes[0] += [ aline.split()[0]+'-1' ]
                uncRes[1] += [ float(aline.split()[2])-1.]
            if 'alpha_' in aline:
                uncRes[0] += [ aline.split()[0].replace('alpha_','') ]
                uncRes[1] += [ float(aline.split()[2]) ]
            if ' +/- ' in aline:
                uncRes[2] += [ float(aline.split()[4]) ]
                uncRes[3] += [ float(aline.split()[4]) ]
            else:
                if len(aline.strip())<2: continue
                brief = (aline.split()[3].split('(')[1].split(')')[0]).replace('--','-')
                uncRes[2] += [ abs(float(brief.split(',')[0])) ]
                uncRes[3] += [ abs(float(brief.split(',')[1])) ]
                if uncRes[2][-1]<0.00001: uncRes[2][-1]=uncRes[3][-1]
                if uncRes[3][-1]<0.00001: uncRes[3][-1]=uncRes[2][-1]
 
    if len(uncRes[1])==0:
        print 'Set inputfile=',inputfile,' failed - no errors found. Stopping here.'
        exit(1)
    
    from array import array
    y = array('d',uncRes[1])
    yep = array('d',uncRes[2])
    yem = array('d',uncRes[3])
    x = array('d', [ a for a in xrange( len(uncRes[1]) ) ] )
    xe = array('d', [ 0 for a in xrange( len(uncRes[1]) ) ] )
    
    c = ROOT.TCanvas('Pulls_'+outputfile,'',1200,600)
    c.SetBottomMargin(0.42)
    c.SetTopMargin(0.03)
    c.SetRightMargin(0.02)
    c.SetLeftMargin(0.06)
    
    frame = ROOT.TH2D('frame_'+outputfile,'',len(uncRes[1]),-0.5,len(uncRes[1])-0.5,5,-3,3)
    frame.SetYTitle('Uncertainty After Fit')
    frame.SetXTitle('')
    frame.Draw()
    frame.GetYaxis().SetTitleOffset(0.5)
    
    eg = ROOT.TGraphAsymmErrors(len(uncRes[1]),x,y,xe,xe,yem,yep)
    eg.Draw('sameP')
    
    pone = ROOT.TLine(-0.5,1,len(uncRes[1])-0.5,1)
    pone.SetLineStyle(3)
    pone.Draw('same')
    zero = ROOT.TLine(-0.5,0,len(uncRes[1])-0.5,0)
    zero.SetLineStyle(2)
    zero.Draw('same')
    mone = ROOT.TLine(-0.5,-1,len(uncRes[1])-0.5,-1)
    mone.SetLineStyle(3)
    mone.Draw('same')
    
    mul = ROOT.TLine(muIDX-0.5,-3,muIDX-0.5,3)
    mul.SetLineStyle(4)
    mul.Draw('same')
    
    for abin in xrange(len(uncRes[1])):
        frame.GetXaxis().SetBinLabel( abin+1 , uncRes[0][abin] )
    frame.GetXaxis().LabelsOption('v')
    
    c.SaveAs(outputfile+'.eps')
    c.SaveAs(outputfile+'.pdf')

if __name__ == "__main__":
    main(sys.argv[1:])

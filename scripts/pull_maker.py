#!/bin/env python

import ROOT
ROOT.SetSignalPolicy( ROOT.kSignalFast )
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.LoadMacro("/afs/cern.ch/atlas/project/cern/susy2/SPyRoot/susy12a_razor_p1328/HistFitter/macros/AtlasStyle.C")
ROOT.SetAtlasStyle()

#doSignal = False
#for doSignal in [True,False]:
for doSignal in [False]:
    for aset in [ 'test_Razor_2leptonFit_newBase']:

                  
        uncRes = [[],[],[],[]]
        
        #        log = open( 'logs/test_'+aset+('' if not doSignal else '_signal')+'.log' , 'r' )
        log = open( 'logs/'+aset+('' if not doSignal else '_signal')+'.log' , 'r' )
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
                    continue #break
                              
                #                 alpha_BJes    3.3586e-01 +/-  5.94e-01

                #print aline 
                if 'mu_' in aline:
                    uncRes[0] += [ aline.split()[0]+'-1' ]
                    uncRes[1] += [ float(aline.split()[2-(0 if doSignal else 0)])-1. ]
                if 'alpha_' in aline:
                    uncRes[0] += [ aline.split()[0].replace('alpha_','') ]
                    uncRes[1] += [ float(aline.split()[2-(0 if doSignal else 0)]) ]
                if ' +/- ' in aline:
                    uncRes[2] += [ float(aline.split()[4-(0 if doSignal else 0)]) ]
                    uncRes[3] += [ float(aline.split()[4-(0 if doSignal else 0)]) ]
                else:
                    if len(aline.strip())<2: continue
                    #print "aline: ", aline
                    brief = (aline.split()[3-(0 if doSignal else 0)].split('(')[1].split(')')[0]).replace('--','-')
                    uncRes[2] += [ abs(float(brief.split(',')[0])) ]
                    uncRes[3] += [ abs(float(brief.split(',')[1])) ]
                    if uncRes[2][-1]<0.00001: uncRes[2][-1]=uncRes[3][-1]
                    if uncRes[3][-1]<0.00001: uncRes[3][-1]=uncRes[2][-1]
 
        if len(uncRes[1])==0:
            print 'Set',aset,'failed - no errors found.  Continuing'
            continue
        
        from array import array
        y = array('d',uncRes[1])
        yep = array('d',uncRes[2])
        yem = array('d',uncRes[3])
        x = array('d', [ a for a in xrange( len(uncRes[1]) ) ] )
        xe = array('d', [ 0 for a in xrange( len(uncRes[1]) ) ] )
        
        c = ROOT.TCanvas('Pulls_'+aset,'',1200,600)
        c.SetBottomMargin(0.42)
        c.SetTopMargin(0.03)
        c.SetRightMargin(0.02)
        c.SetLeftMargin(0.06)
        
        frame = ROOT.TH2D('frame_'+aset,'',len(uncRes[1]),-0.5,len(uncRes[1])-0.5,5,-3,3)
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
        
        c.SaveAs('pull_plots/pull_afterFit_test'+(aset.replace('.','_'))+('' if not doSignal else '_signal')+'.eps')
        c.SaveAs('pull_plots/pull_afterFit_test'+(aset.replace('.','_'))+('' if not doSignal else '_signal')+'.pdf')


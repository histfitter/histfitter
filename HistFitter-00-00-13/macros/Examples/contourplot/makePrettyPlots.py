# script written by Zach Marshall, modified by Moritz Backes
import sys
import sys,os,ROOT
from ROOT import *
from summary_harvest_tree_description import *
from array import array
def prettyPlots( outDir = '.' , gridNumber = 4 , type = 'cls' ):
    if gridNumber==7:
        print 'Re-running grid 7 with subsets...'
        for i in xrange(0,5):
             print i
             prettyPlots( outDir , 70+i )
        return
    if outDir=='': outDir = '.'

    import GridPlotUtils
    GridProcess = {
      1 :  'qq' , # qq -> qq NN
                  #    
      2 :  'gg' , # gg -> qq qq NN
                  #
      3 :  'gg' , # gg -> qqW qqW NN
      4 :  'gg' , # gg -> qqW qqW NN
      5 :  'gg' , # gg -> qqW qqW NN
                  # 
      6 :  'gg' , # gg -> qqWZ qqWZ NN
                  #
      7 :  'qg' , # qg -> qq q NN
                  #
      9 :  'gg' , # gg -> qqZ qqW NN
      10 : 'gg' , # gg -> qqZ qqW NN
      11 : 'gg' , # gg -> qqZ qqW NN
                  #
      12 : 'qq' , # qq -> qZ qW NN
      13 : 'qq' , # qq -> qZ qW NN
      14 : 'qq' , # qq -> qZ qW NN
                  #
      15 : 'qq' , # qq -> qW qW NN
      16 : 'qq' , # qq -> qW qW NN
      17 : 'qq' , # qq -> qW qW NN
                  #
      18 : 'cc' , # CC -> W W NN 
                  #
      19 : 'qg' , # gq -> qqW qW NN 
      20 : 'qg' , # gq -> qqW qW NN 
      21 : 'qg' , # gq -> qqW qW NN 
                  # 
      22 : 'qg' , # gq -> qq q WZ NN 
      23 : 'qg' , # gq -> qq q WZ NN 
      24 : 'qg' , # gq -> qq q WZ NN 
                  }
    if gridNumber>24:
        setNumber=gridNumber-70
        gridNumber=7
        sqMassDiff = [10,25,50,75,100]
    gridNumber = int(gridNumber)
    if not gridNumber in GridProcess.keys() or ('setNumber' in dir() and setNumber<0):
        print 'Grid',gridNumber,'not in',GridProcess.keys()
        return
    topY = 800.1
    botX = 235
    diff = 55
    if gridNumber==1:
        gridTitleStr = '2-Body Direct Decay'
        gridProcStr = '#tilde{q}#tilde{q}#rightarrowqq#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}'
    elif gridNumber==2:
        gridTitleStr = '3-Body Direct Decay'
        gridProcStr = '#tilde{g}#tilde{g}#rightarrowqqqq#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}'
    elif gridNumber==3:
        gridTitleStr = '1-Step Decay, x=1/4'
        gridProcStr = '#tilde{g}#tilde{g}#rightarrowqqqqWW#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}'
    elif gridNumber==4:
        gridTitleStr = '1-Step Decay, x=1/2'
        gridProcStr = '#tilde{g}#tilde{g}#rightarrowqqqqWW#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}'
    elif gridNumber==5:
        gridTitleStr = '1-Step Decay, x=3/4'
        gridProcStr = '#tilde{g}#tilde{g}#rightarrowqqqqWW#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}'
    elif gridNumber==6:
        gridTitleStr = '2-Step Decay'
        gridProcStr = '#tilde{g}#tilde{g}#rightarrowqqqqWZWZ#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}'
    elif gridNumber==7:
        gridTitleStr = 'Associated Production, m_{sq}-m_{LSP} = %i GeV'%(sqMassDiff[setNumber])
        gridProcStr = '#tilde{g}#tilde{q}#rightarrowqqq#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}'
    elif gridNumber==9:
        gridTitleStr = '1-Step Decay WZ, x=1/4'
        gridProcStr = '#tilde{g}#tilde{g}#rightarrowqqqqWZ#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}'
    elif gridNumber==10:
        gridTitleStr = '1-Step Decay WZ, x=1/2'
        gridProcStr = '#tilde{g}#tilde{g}#rightarrowqqqqWZ#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}'
    elif gridNumber==11:
        gridTitleStr = '1-Step Decay WZ, x=3/4'
        gridProcStr = '#tilde{g}#tilde{g}#rightarrowqqqqWZ#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}'
    elif gridNumber==12:
        gridTitleStr = '1-Step Decay, x=1/4'
        gridProcStr = '#tilde{q}#tilde{q}#rightarrowqqWZ#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}'
    elif gridNumber==13:
        gridTitleStr = '1-Step Decay, x=1/2'
        gridProcStr = '#tilde{q}#tilde{q}#rightarrowqqWZ#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}'
    elif gridNumber==14:
        gridTitleStr = '1-Step Decay, x=3/4'
        gridProcStr = '#tilde{q}#tilde{q}#rightarrowqqWZ#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}'
    elif gridNumber==15:
        gridTitleStr = '1-Step Decay, x=1/4'
        gridProcStr = '#tilde{q}#tilde{q}#rightarrowqqWW#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}'
    elif gridNumber==16:
        gridTitleStr = '1-Step Decay, x=1/2'
        gridProcStr = '#tilde{q}#tilde{q}#rightarrowqqWW#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}'
    elif gridNumber==17:
        gridTitleStr = '1-Step Decay, x=3/4'
        gridProcStr = '#tilde{q}#tilde{q}#rightarrowqqWW#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}'
    elif gridNumber==18:
        topY = 900
        botX = 100
        diff = 60
        gridTitleStr = '2-Body Chargino Decay'
        gridProcStr = '#tilde{#chi}^{+}_{1}#tilde{#chi}^{-}_{1}#rightarrowWW#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}'
    elif gridNumber==19:
        gridTitleStr = '1-Step Decays, x=1/4'
        gridProcStr = '#tilde{g}#tilde{q}#rightarrowqqqWW#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}'
    elif gridNumber==20:
        gridTitleStr = '1-Step Decays, x=1/2'
        gridProcStr = '#tilde{g}#tilde{q}#rightarrowqqqWW#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}'
    elif gridNumber==21:
        gridTitleStr = '1-Step Decays, x=3/4'
        gridProcStr = '#tilde{g}#tilde{q}#rightarrowqqqWW#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}'
    elif gridNumber==22:
        gridTitleStr = '1-Step Decays, x=1/4'
        gridProcStr = '#tilde{g}#tilde{q}#rightarrowqqqWZ#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}'
        gridProcStr2 = 'm_{#tilde{#chi}_{2}^{0}}=m_{#tilde{#chi}_{1}^{#pm}}, m_{#tilde{g}}=m_{#tilde{q}}'
    elif gridNumber==23:
        gridTitleStr = '1-Step Decays, x=1/2'
        gridProcStr = '#tilde{g}#tilde{q}#rightarrowqqqWZ#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}'
        gridProcStr2 = 'm_{#tilde{#chi}_{2}^{0}}=m_{#tilde{#chi}_{1}^{#pm}}, m_{#tilde{g}}=m_{#tilde{q}}'
    elif gridNumber==24:
        gridTitleStr = '1-Step Decays, x=3/4'
        gridProcStr = '#tilde{g}#tilde{q}#rightarrowqqqWZ#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}'
        gridProcStr2 = 'm_{#tilde{#chi}_{2}^{0}}=m_{#tilde{#chi}_{1}^{#pm}}, m_{#tilde{g}}=m_{#tilde{q}}'
    label = ROOT.TLatex(botX+50,topY-diff,gridTitleStr)
    label2 = ROOT.TLatex(botX+50,topY-diff*2,gridProcStr)
    if 'gridProcStr2' in dir():
        label3 = ROOT.TLatex(botX+50,topY-diff*3,gridProcStr2)

    #xsecFile = ROOT.TFile.Open('l_p601_%i_RootFiles.root'%gridNumber)
    xsecFile = ROOT.TFile.Open("/afs/cern.ch/atlas/project/cern/susy/users/mbackes/SusyFitterDev/macros/contourplot/MySoftOneLeptonKtScaleFitMetMeff_SM_GG_onestepCC_R17_Output_upperlimit__1_harvest_list.root")

    sr3jl = []


    sr3jl += [xsecFile.Get('excludedXsec')]


    #if gridNumber==3 or gridNumber==4 or gridNumber==5:
    #exclFile3jl = ROOT.TFile.Open('/afs/cern.ch/atlas/project/cern/susy1/SPyRoot/Combination/macros/LP2011/1lepton/sm%isr3jl_smooth_list_graphs.root'%gridNumber)
    exclFile3jl = ROOT.TFile.Open('/afs/cern.ch/atlas/project/cern/susy/users/mbackes/SusyFitterDev/macros/contourplot/MySoftOneLeptonKtScaleFitMetMeffR17_Output_hypotest__1_harvest_list_graphs.root')
    
    
    obsName = 'contour_obscls' 
    expName = 'contour_expcls' 
    u1sName = 'contour_expcls_u1s' 
    d1sName = 'contour_expcls_d1s' 

    sr3jl += [exclFile3jl.Get(obsName)]
    sr3jl += [exclFile3jl.Get(expName)]
    sr3jl += [exclFile3jl.Get(u1sName)]
    sr3jl += [exclFile3jl.Get(d1sName)]

    labelIdx = ['3JL']
    labelString = ['s1lsj SR']
    index = 0
    for plotSet in [sr3jl]:
        print plotSet
        label4 = ROOT.TLatex(botX+50,topY-diff* (4 if 'gridProcStr2' in dir() else 3),labelString[index])
        label5 = ROOT.TLatex(botX+50,topY-diff* (5 if 'gridProcStr2' in dir() else 4),'L^{int} = 1.04 fb^{-1}, #sqrt{s}=7 TeV')
        c1 = ROOT.TCanvas("c1","c1 %s, grid %i" % (labelIdx[index], gridNumber),1600,1200)
        c1.SetLeftMargin(0.13)
        c1.SetBottomMargin(0.13)
        if not plotSet[0]: 
            print 'Skipping Grid',gridNumber,'set',labelIdx[index]
            index += 1
            continue
        frame = ROOT.TH2D('frame%s%i'%(labelIdx[index],gridNumber),'',2,botX,topY,2,0,topY)
        frame.Draw()
        frame.GetXaxis().SetLabelSize(0.04)
        frame.GetXaxis().SetTitleSize(0.04)
        frame.GetYaxis().SetLabelSize(0.04)
        frame.GetYaxis().SetTitleSize(0.04)
        frame.GetZaxis().SetLabelSize(0.04)
        frame.GetZaxis().SetTitleSize(0.04)

        plotSet[0].Draw("sameCOLZ")
        #till (get ticks back)
        hAxis = frame.Clone()
        hAxis.GetYaxis().SetTitleOffset( 50. )
        hAxis.GetYaxis().SetLabelOffset( 50. )
        hAxis.GetXaxis().SetTitleOffset( 50. )
        hAxis.GetXaxis().SetLabelOffset( 50. )
        hAxis.Draw("AXISSAME") # redraw the axis
        # done, till
        if GridProcess[gridNumber]=='gg' or GridProcess[gridNumber]=='qg': frame.GetXaxis().SetTitle("m_{gluino} [GeV]")
        if GridProcess[gridNumber]=='qq': frame.GetXaxis().SetTitle("m_{squark} [GeV]")
        if GridProcess[gridNumber]=='cc': frame.GetXaxis().SetTitle("m_{chargino} [GeV]")
        frame.GetZaxis().SetLabelSize(0.04)
        frame.GetZaxis().SetTitleSize(0.04)
        plotSet[0].GetZaxis().SetLabelSize(0.04)
        plotSet[0].GetZaxis().SetTitleSize(0.04)
        plotSet[0].GetZaxis().SetTitle('Cross Section Excluded at 95% CL [pb]') #(#sigma #times #varepsilon #times A) Excluded at 95% CL [pb]')
        plotSet[0].GetZaxis().SetTitleOffset(1.2)

        frame.GetYaxis().SetTitle("m_{LSP} [GeV]")
        #plotSet[0].SetMaximum(0.15)
        l1 = ROOT.TLine(botX,botX,topY,topY)
        l1.SetLineStyle(3)
        l1.Draw()

        label.Draw()
        label2.Draw()
        if ('gridProcStr2' in dir()):
            label3.Draw()
        label4.Draw()
        label5.Draw()

        rs.myMarkerLine(0.21,0.66,'Observed 95% CL',0.03,ROOT.kRed,0.03,1,0.02,2)
        rs.myMarkerLine(0.21,0.61,'Expected',0.03,ROOT.kBlue,0.03,2,0.02,2)
        rs.myMarkerLine(0.21,0.56,'Expected #pm1#sigma',0.03,ROOT.kBlue,0.03,3,0.02,2)

        #plotSet[0].GetYaxis().SetRangeUser(0,topY)
        #plotSet[0].GetXaxis().SetRangeUser(botX,topY)
        c1.SetLogz()
        plotSet[0].SetMinimum( 0.05 ) # 5 fb
        plotSet[0].SetMaximum( 500 ) # 5.0 nb

        #contourLines = GridPlotUtils.genContourHist( plotSet[0], [0.1,0.5,1,5] )
        #contourLines.SetLineColor(kGray)
        #contourLines.Draw("CONT3 SAME")

        try:
            plotSet[1].SetLineColor(ROOT.kRed)
            plotSet[1].Draw("same")
        except: pass
        try:
            plotSet[2].SetLineStyle(2)
            plotSet[2].SetLineColor(ROOT.kBlue)
            plotSet[2].Draw("same")
        except: pass
        try:
            plotSet[3].SetLineStyle(3)
            plotSet[3].SetLineColor(ROOT.kBlue)
            plotSet[3].Draw("same")
        except: pass
        try:
            plotSet[4].SetLineStyle(3)
            plotSet[4].SetLineColor(ROOT.kBlue)
            plotSet[4].Draw("same")
        except: pass
        rs.ATLAS_LABEL(0.43,0.88,ROOT.kBlack,0.05)
        rs.myText( 0.56,0.88, 1,"Work in Progress", size=0.05)
        
        c1.Update()

        #c1.SaveAs("%s/FinalExcl_%s_Grid%i%s.jpg"%(outDir,labelIdx[index],gridNumber,'' if gridNumber!=7 else '_'+str(setNumber)))
        c1.SaveAs("%s/FinalExcl_%s%s_Grid%i%s.eps"%(outDir,type,labelIdx[index],gridNumber,'' if gridNumber!=7 else '_'+str(setNumber)))
        c1.SaveAs("%s/FinalExcl_%s%s_Grid%i%s.gif"%(outDir,type,labelIdx[index],gridNumber,'' if gridNumber!=7 else '_'+str(setNumber)))
        c1.SaveAs("%s/FinalExcl_%s%s_Grid%i%s.C"%(outDir,type,labelIdx[index],gridNumber,'' if gridNumber!=7 else '_'+str(setNumber)))
        index += 1



execfile("../../common_susy11b/setAtlasStyle2.py")
rs.style.SetPadRightMargin( 0.17 )
ROOT.gROOT.ForceStyle()
import GridPlotUtils
#GridPlotUtils.setPalette(name='brown2', ncontours=999)
ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetTextSize(0.03)
prettyPlots( '' ,  4 , 'cls' )



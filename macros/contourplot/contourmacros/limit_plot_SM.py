#!/bin/env python

import ROOT
ROOT.gROOT.ProcessLine('#include "contourmacros/CombinationGlob.C"')
ROOT.CombinationGlob.Initialize()

#execfile("summary_harvest_tree_description_SM.py")


def limit_plot_SM( file_nominal, file_up=None, file_down=None , outputfilename='', prefix=None, lumi=21, drawFirstObs=False, allObs=False, firstOneSigma=False, upperlimit=True, printCLs=False ): 

    #if not 'HiggsSU' in file_nominal:
    #    execfile("summary_harvest_tree_description_SM.py")
    #else: 
    #    execfile("summary_harvest_tree_description_HiggsSU.py")

    print_theo = True
    
    if file_up==None or file_down==None:
        print_theo = False
        print "No up or down variations given! Proceed without them."

    #Note: All curves loaded here are 1-2 lepton limits of previous analyses. Remove these lines or take them from the HistFitterUser/MET_jets_leptons/macros directory

    if '_GG1stepx12' in file_nominal:
        from contourmacros.GG2012x12 import exclusion_graph
    elif '_GG1stepgridx' in file_nominal:
        from contourmacros.GG2012gridx import exclusion_graph
    elif '_SS1stepx12' in file_nominal:
        from contourmacros.SS2012x12 import exclusion_graph
    elif '_SS1stepgridx' in file_nominal:
        from contourmacros.SS2012gridx import exclusion_graph	  
    else: from contourmacros.GG2012gridx import exclusion_graph
    
    if 'HiggsSU' in file_nominal:
        ROOT.gROOT.LoadMacro("../../../HistFitterUser/common/ATLAS_EPS_contours.C")

    print "Here"
    twostepexclusion=ROOT.TGraph()
    if 'SS2WWZZ' in file_nominal:
        SS2WWZZ_file = ROOT.TFile.Open("contourmacros/Merged_Output_hypotest_SM_SS_twostep_ALL_Nominal__1_harvest_list.root_contours.root")
        twostepexclusion_curve = SS2WWZZ_file.Get("gr_contour_obs")
    elif 'GG2WWZZ' in file_nominal:
        GG2WWZZ_file = ROOT.TFile.Open("contourmacros/Merged_Output_hypotest_SM_GG_twostep_ALL_Nominal__1_harvest_list.root_contours.root")
        twostepexclusion_curve = GG2WWZZ_file.Get("gr_contour_obs")
        twostepexclusion_curve.SetPoint(twostepexclusion_curve.GetN(),0.,0.)
    if 'GG2WWZZ' in file_nominal or 'SS2WWZZ' in file_nominal:
        twostepexclusion_curve.SetFillColor(18)
        twostepexclusion_curve.SetLineWidth(2)
        twostepexclusion_curve.SetMarkerStyle(21)
        twostepexclusion_curve.SetMarkerSize(0.3)
        twostepexclusion_curve.SetFillStyle(1001)
        twostepexclusion_curve.SetLineColor(0)

    
    graph_pre = exclusion_graph()
    graph = graph_pre.Clone()
    #graph.SetDirectory(0)

    print 'Producing contour plot based on ', file_nominal

    firstObs = None
    firstExp = None
    firstPOneSigma = None
    firstMOneSigma = None
    histosOrig = []

    f = ROOT.TFile.Open(file_nominal,'READ')
    firstObs = f.Get( 'sigp1clsf' )
    firstExp = f.Get( 'sigp1expclsf' )
    firstPOneSigma = f.Get( 'sigclsu1s' )
    firstMOneSigma = f.Get( 'sigclsd1s' )
    print firstPOneSigma
    for hizzie in [firstObs,firstExp,firstPOneSigma,firstMOneSigma]: hizzie.SetDirectory(0)
    f.Close()    
    
    if print_theo:
        f_up = ROOT.TFile.Open(file_up,'READ')
        upObs = f_up.Get( 'sigp1clsf' ) 
        upObs.SetDirectory(0)
        f_up.Close()
        f_down = ROOT.TFile.Open(file_down,'READ')
        downObs = f_down.Get( 'sigp1clsf' ) 
        downObs.SetDirectory(0)
        f_down.Close() 
        histosOrig = [upObs, downObs]      


    firstObsH = FixAndSetBorders(file_nominal, firstObs , 'firstObsH' , '' , 0 )
    firstExpH = FixAndSetBorders(file_nominal, firstExp , 'firstExpH' , '' , 0 )
    if print_theo:
        histos = []
        for h in histosOrig: histos += [ FixAndSetBorders(file_nominal, h , h.GetName()+'H' , '' , 0 ) ]

    firstPOneSigmaG=ROOT.TGraph()
    firstMOneSigmaG=ROOT.TGraph()
    

    if firstOneSigma: # Only need these for the +/-1 sigma band
        firstPOneSigmaG_pre = ContourGraph( FixAndSetBorders(file_nominal, firstPOneSigma , 'firstPOneSigmaG' , '' , 0 ) )
        if firstPOneSigmaG_pre!=None: firstPOneSigmaG = firstPOneSigmaG_pre.Clone()
        firstMOneSigmaG_pre = ContourGraph( FixAndSetBorders(file_nominal, firstMOneSigma , 'firstMOneSigmaG' , '' , 0 ) )
        if firstMOneSigmaG_pre!=None: firstMOneSigmaG = firstMOneSigmaG_pre.Clone()
        if firstMOneSigmaG.GetN()==0 or firstPOneSigmaG.GetN()==0: firstOneSigma=False

    
    # set text style
    ROOT.gStyle.SetPaintTextFormat(".2g")

    # Start drawing
    c = ROOT.TCanvas('LimitPlot','A limit plot', 0 , 0 , ROOT.CombinationGlob.StandardCanvas[0] , ROOT.CombinationGlob.StandardCanvas[1] )

    # create and draw the frame2 
    if '_Gtt_' in file_nominal:
        frame2 = ROOT.TH2F('frame2', 'Simplified model limit for comparisons', 100, 500., 1300., 100, 25., 700. )
        frame2.SetXTitle( "m_{#tilde{g}} [GeV]" )
        frame2.SetYTitle( "m_{#tilde{#chi}^{0}_{1}} [GeV]" )
    elif '_GG1step' in file_nominal and not 'gridx' in file_nominal:
        frame2 = ROOT.TH2F('frame2', 'Simplified model limit for comparisons', 100, 225., 1500., 100, 25., 1025. )
        frame2.SetXTitle( "m_{#tilde{g}} [GeV]" )
        frame2.SetYTitle( "m_{#tilde{#chi}^{0}_{1}} [GeV]" )
    elif '_GG2' in file_nominal:
        frame2 = ROOT.TH2F('frame2', 'Simplified model limit for comparisons', 100, 225., 1500., 100, 35., 1025. )
        frame2.SetXTitle( "m_{#tilde{g}} [GeV]" )
        frame2.SetYTitle( "m_{#tilde{#chi}^{0}_{1}} [GeV]" )	
    elif 'SoftLepton' in file_nominal:
        frame2 = ROOT.TH2F('frame2', 'Simplified model limit for comparisons', 100, 0., 1500., 100, 0., 1025. )
        frame2.SetXTitle( "m_{#tilde{g}} [GeV]" )
        frame2.SetYTitle( "m_{#tilde{#chi}^{0}_{1}} [GeV]" )
    elif '_GG1step' in file_nominal and 'gridx' in file_nominal:
        frame2 = ROOT.TH2F('frame2', 'Simplified model limit for comparisons', 63,240,1500,75,0.,1.5 )
        frame2.SetXTitle( "m_{#tilde{g}} [GeV]" )
        frame2.SetYTitle( "X = ( m_{#tilde{#chi}^{#pm}_{1}} - m_{#tilde{#chi}^{0}_{1}} ) / ( m_{#tilde{g}} - m_{#tilde{#chi}^{0}_{1}} ) " )    
    elif '_SS1step' in file_nominal and not 'gridx' in file_nominal:
        frame2 = ROOT.TH2F('frame2', 'Simplified model limit for comparisons', 100, 225., 1250., 100, 25., 1025. )
        frame2.SetXTitle( "m_{#tilde{q}} [GeV]" )
        frame2.SetYTitle( "m_{#tilde{#chi}^{0}_{1}} [GeV]" )
    elif '_SS2CNsl' in file_nominal:
        frame2 = ROOT.TH2F('frame2', 'Simplified model limit for comparisons', 100, 225., 1250., 100, 35., 1025. )
        frame2.SetXTitle( "m_{#tilde{q}} [GeV]" )
        frame2.SetYTitle( "m_{#tilde{#chi}^{0}_{1}} [GeV]" )	
    elif '_SS2WWZZ' in file_nominal:
        frame2 = ROOT.TH2F('frame2', 'Simplified model limit for comparisons', 100, 225., 1500., 100, 35., 1025. )
        frame2.SetXTitle( "m_{#tilde{q}} [GeV]" )
        frame2.SetYTitle( "m_{#tilde{#chi}^{0}_{1}} [GeV]" )	
    elif 'SS1step' in file_nominal and 'gridx' in file_nominal:
        frame2 = ROOT.TH2F('frame2', 'Simplified model limit for comparisons', 48,240,1200,75,0.,1.5)# 100, 225., 1500., 100, 0, 1. )
        frame2.SetXTitle( "m_{#tilde{q}} [GeV]" )
        frame2.SetYTitle( "X = ( m_{#tilde{#chi}^{#pm}_{1}} - m_{#tilde{#chi}^{0}_{1}} ) / ( m_{#tilde{q}} - m_{#tilde{#chi}^{0}_{1}} ) " )
    elif '_Higgsino_' in file_nominal:
        frame2 = ROOT.TH2F('frame2', 'Simplified model limit for comparisons', 100, 125., 650., 100, 75., 600. )
        frame2.SetXTitle( "Light Stop Mass [GeV]" )
        frame2.SetYTitle( "LSP Mass [GeV]" )
    elif 'HiggsSU' in file_nominal:
        frame2 = ROOT.TH2F('frame2', 'm_{0} vs m_{12} - ATLAS work in progress', 100, 100., 6000., 100, 300., 800 )
        frame2.SetXTitle( "m_{0} [GeV]" )
        frame2.SetYTitle( "m_{1/2} [GeV]" )
    else:
        frame2 = ROOT.TH2F('frame2', 'Simplified model limit for comparisons', 100, 225., 1500., 100, 25., 1025. )
        frame2.SetXTitle( "m_{#tilde{g}} [GeV]" )
        frame2.SetYTitle( "m_{#tilde{#chi}^{0}_{1}} [GeV]" )

    ROOT.CombinationGlob.SetFrameStyle2D( frame2, 1.0 )

    frame2.GetYaxis().SetTitleOffset(1.35)
 
    frame2.GetXaxis().SetTitleFont( 42 )
    frame2.GetYaxis().SetTitleFont( 42 )
    frame2.GetXaxis().SetLabelFont( 42 )
    frame2.GetYaxis().SetLabelFont( 42 )
 
    frame2.GetXaxis().SetTitleSize( 0.04 )
    frame2.GetYaxis().SetTitleSize( 0.04 )
    frame2.GetXaxis().SetLabelSize( 0.04 )
    frame2.GetYaxis().SetLabelSize( 0.04 )
 
    frame2.Draw()
    
    if '1step' in file_nominal: 
        graph.Draw("Fsame")     
    if 'GG2WWZZ' in file_nominal or 'SS2WWZZ' in file_nominal:
        twostepexclusion_curve.Draw("Fsame") 
    
    # Set up the legend
    #leg = ROOT.TLegend(0.15,0.65,0.37,0.85)
    leg = ROOT.TLegend(0.14,0.6,0.37,0.74)
    if 'gridx' in file_nominal:
        leg = ROOT.TLegend(0.61,0.71,0.91,0.85)
    if 'HiggsSU' in file_nominal:
        leg = ROOT.TLegend(0.65,0.7,0.92,0.915)
    leg.SetTextSize( ROOT.CombinationGlob.DescriptionTextSize );
    leg.SetTextSize( 0.03 );
    leg.SetTextFont( 42 );
    leg.SetFillColor( 0 );
    leg.SetFillStyle(1001);

    if 'HiggsSU' in file_nominal:
        f4 = ROOT.TFile.Open("../../../HistFitterUser/common/mSugraGridtanbeta30_gluinoSquarkMasses.root" , "READ" )
        histSq = f4.Get( "mSugraGrid_squarkMasses" )
        histGl = f4.Get( "mSugraGrid_gluinoMasses" )
        histSq.SetDirectory(0)
        histGl.SetDirectory(0)
        f4.Close()
        
        c.cd()

        histSquarkMass   = FixAndSetBorders(file_nominal, histSq, "SquarkMass", "SquarkMass", 10000 )
        histGluinoMass   = FixAndSetBorders(file_nominal, histGl, "GluinoMass", "GluinoMass", 10000 )
  
        DrawContourMassLine( histSquarkMass, 1000.0 )  
        DrawContourMassLine( histSquarkMass, 1200.0 , 17)    
        DrawContourMassLine( histSquarkMass, 1400.0 )
        DrawContourMassLine( histSquarkMass, 1600.0 , 17)
        DrawContourMassLine( histSquarkMass, 1800.0 )
        DrawContourMassLine( histSquarkMass, 2000.0 , 17)   
        DrawContourMassLine( histSquarkMass, 2200.0 )      
        DrawContourMassLine( histSquarkMass, 2400.0 , 17)
        DrawContourMassLine( histSquarkMass, 2600.0 )
        DrawContourMassLine( histSquarkMass, 2800.0 , 17)
        DrawContourMassLine( histSquarkMass, 3000.0 )   
        DrawContourMassLine( histSquarkMass, 3200.0 , 17)       
        DrawContourMassLine( histSquarkMass, 3400.0 )
        DrawContourMassLine( histSquarkMass, 3600.0 , 17)
        DrawContourMassLine( histSquarkMass, 3800.0 )
        DrawContourMassLine( histSquarkMass, 4000.0, 17 ) 
        DrawContourMassLine( histSquarkMass, 4200.0 )       
        DrawContourMassLine( histSquarkMass, 4400.0 , 17)
        DrawContourMassLine( histSquarkMass, 4600.0 )
        DrawContourMassLine( histSquarkMass, 4800.0, 17)
        DrawContourMassLine( histSquarkMass, 5000.0 ) 
        DrawContourMassLine( histSquarkMass, 5200.0 , 17)       
        DrawContourMassLine( histSquarkMass, 5400.0 )
        DrawContourMassLine( histSquarkMass, 5600.0 , 17)
        DrawContourMassLine( histSquarkMass, 5800.0 )
        DrawContourMassLine( histSquarkMass, 6000.0, 17 )                       
        DrawContourMassLine( histSquarkMass, 6200.0 )       
        DrawContourMassLine( histSquarkMass, 6400.0 , 17)
        DrawContourMassLine( histSquarkMass, 6600.0 )
        DrawContourMassLine( histSquarkMass, 6800.0, 17)

        DrawContourMassLine( histGluinoMass, 800.0 )
        DrawContourMassLine( histGluinoMass, 900.0 , 17) 
        DrawContourMassLine( histGluinoMass, 1000.0 ) 
        DrawContourMassLine( histGluinoMass, 1100.0 , 17)  
        DrawContourMassLine( histGluinoMass, 1200.0 )  
        DrawContourMassLine( histGluinoMass, 1300.0 , 17)      
        DrawContourMassLine( histGluinoMass, 1400.0 )
        DrawContourMassLine( histGluinoMass, 1500.0 , 17)
        DrawContourMassLine( histGluinoMass, 1600.0 ) 
        DrawContourMassLine( histGluinoMass, 1700.0 , 17)
        DrawContourMassLine( histGluinoMass, 1800.0 )
        DrawContourMassLine( histGluinoMass, 1900.0 , 17)
        DrawContourMassLine( histGluinoMass, 2000.0 )  

        s1000 = ROOT.TLatex( 355, 375, "#tilde{q} (1000 GeV)" )
        s1000.SetTextAlign( 11 )
        s1000.SetTextAngle(-65)
        s1000.SetTextSize( 0.025 )
        s1000.SetTextColor( 16 )
        s1000.Draw() 
        s1400 = ROOT.TLatex( 960, 390, "#tilde{q} (1400 GeV)" )
        s1400.SetTextAlign( 11 )
        s1400.SetTextAngle(-77)
        s1400.SetTextSize( 0.025 )
        s1400.SetTextColor( 16 )
        s1400.Draw()   
        s1600 = ROOT.TLatex( 1440, 390, "#tilde{q} (1600 GeV)" )
        s1600.SetTextAlign( 11 )
        s1600.SetTextAngle(-82)
        s1600.SetTextSize( 0.025 )
        s1600.SetTextColor( 16 )
        s1600.Draw()    

        g1000 = ROOT.TLatex( 850, 413, "#tilde{g} (1000 GeV)" );
        g1000.SetTextAlign( 11 )
        g1000.SetTextAngle(-11)
        g1000.SetTextSize( 0.025 )
        g1000.SetTextColor( 16 )
        g1000.Draw()
        g1200 = ROOT.TLatex( 850, 508, "#tilde{g} (1200 GeV)" )
        g1200.SetTextAlign( 11 )
        g1200.SetTextAngle(-11)
        g1200.SetTextSize( 0.025 )
        g1200.SetTextColor( 16 )
        g1200.Draw()
        g1400 = ROOT.TLatex( 1650, 584, "#tilde{g} (1400 GeV)" )
        g1400.SetTextAlign( 11 )
        g1400.SetTextAngle(-11) 
        g1400.SetTextSize( 0.025 )
        g1400.SetTextColor( 16 )
        g1400.Draw()
        g1600 = ROOT.TLatex( 1650, 680, "#tilde{g} (1600 GeV)" )
        g1600.SetTextAlign( 11 )
        g1600.SetTextAngle(-11)
        g1600.SetTextSize( 0.025 )
        g1600.SetTextColor( 16 )
        g1600.Draw() 

    # Draw the +/- 1 sigma yellow band 
    if firstOneSigma: 
        grshadeExp = DrawExpectedBand( firstPOneSigmaG , firstMOneSigmaG , ROOT.CombinationGlob.c_DarkYellow , 1001 , 0).Clone()
        grshadeExp.Draw("Fsame")

    colors = [ ROOT.CombinationGlob.c_DarkGreen, ROOT.CombinationGlob.c_DarkRed ,
               ROOT.CombinationGlob.c_DarkOrange , ROOT.CombinationGlob.c_DarkGray , ROOT.CombinationGlob.c_BlueT3, ROOT.CombinationGlob.c_DarkPink , ROOT.CombinationGlob.c_VDarkYellow, ROOT.CombinationGlob.c_HiggsGreen,
               ROOT.CombinationGlob.c_LightPink , ROOT.CombinationGlob.c_LightYellow, ROOT.CombinationGlob.c_Black ]
               
    c_myYellow   = ROOT.TColor.GetColor("#ffe938")
    c_myRed      = ROOT.TColor.GetColor("#aa000")
    c_myExp      = ROOT.TColor.GetColor("#28373c")       

    #colors = [ ROOT.CombinationGlob.c_DarkGreen , ROOT.CombinationGlob.c_DarkGray , ROOT.CombinationGlob.c_BlueT3 , ROOT.CombinationGlob.c_DarkRed ,
    #           ROOT.CombinationGlob.c_DarkOrange , ROOT.CombinationGlob.c_DarkPink , ROOT.CombinationGlob.c_VDarkYellow ]
    #if len(colors)<len(histos):
    #    print 'Only have',len(colors),'colors for',len(histos),'histograms.  Will crash...'

    newHists = []
    
    if print_theo:   
        print len(histos)
        print histos
        for i in xrange(len(histos)):
            print i
            (leg,anewhist) = DrawContourLine95( leg, histos[i], '' , c_myRed , 3, 2 )
            newHists += [anewhist]

    if drawFirstObs:
        (leg,anewhist) = DrawContourLine95( leg, firstObsH, 'Observed limit (#pm1 #sigma^{SUSY}_{theory})', ROOT.CombinationGlob.c_DarkRed,1,4)
        newHists += [anewhist]
        #(leg,anewhist) = DummyLegendExpected( leg, 'Observed limit (#pm1 #sigma^{SUSY}_{theory})', c_myRed, 1001, ROOT.CombinationGlob.c_DarkRed, 1, 4 )
        newHists += [anewhist]

    if firstOneSigma:
        (leg,anewhist) = DrawContourLine95( leg, firstExpH, '', c_myExp, 6, 2 )
        newHists += [anewhist]
        (leg,anewhist) = DummyLegendExpected( leg, 'Expected limit (#pm1 #sigma_{exp})', ROOT.CombinationGlob.c_DarkYellow, 1001, c_myExp, 6, 2 )
        newHists += [anewhist]
    else:
        #(leg,anewhist) = DrawContourLine95( leg, firstExpH, file_nominal.split('_Higgsino')[0].split('MultiJet_')[1], ROOT.CombinationGlob.c_DarkBlueT3, 6 )
        (leg,anewhist) = DrawContourLine95( leg, firstExpH, 'Expected', c_myExp, 6, 2 )
        newHists += [anewhist]

    c.cd()
    c.Update()
    
    #if 'GG2WWZZ' in file_nominal or 'SS2WWZZ' in file_nominal:
    #    twostepexclusion_curve.Draw("Fsame") 

    # legend
    textSizeOffset = +0.000;
    xmax = frame2.GetXaxis().GetXmax()
    xmin = frame2.GetXaxis().GetXmin()
    ymax = frame2.GetYaxis().GetXmax()
    ymin = frame2.GetYaxis().GetXmin()
    dx   = xmax - xmin
    dy   = ymax - ymin

    # Label the decay process
    Leg0 = None
    if   '_GG1step' in file_nominal and not 'gridx' in file_nominal: Leg0 = ROOT.TLatex( xmin, ymax + dy*0.025, "#tilde{g}-#tilde{g} #rightarrowqqqqWW#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}, x=1/2" ) ##tilde{g}-#tilde{g}, #tilde{g}#rightarrow q#bar{q}'W#tilde{#chi}_{1}^{0}" )
    if   '_GG1step' in file_nominal and 'gridx' in file_nominal: Leg0 = ROOT.TLatex( xmin, ymax + dy*0.025, "#tilde{g}-#tilde{g} #rightarrowqqqqWW#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}, m_{#tilde{#chi}_{1}^{0}} = 60 GeV" ) ##tilde{g}-#tilde{g}, #tilde{g}#rightarrow q#bar{q}'W#tilde{#chi}_{1}^{0}" )    
    elif '_SS1step' in file_nominal and not 'gridx' in file_nominal: Leg0 = ROOT.TLatex( xmin, ymax + dy*0.025, "#tilde{q}-#tilde{q} #rightarrow qqWW#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}, x=1/2" )
    elif '_SS1step' in file_nominal and 'gridx' in file_nominal: Leg0 = ROOT.TLatex( xmin, ymax + dy*0.025, "#tilde{q}-#tilde{q} #rightarrow qqWW#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}, m_{#tilde{#chi}_{1}^{0}} = 60 GeV" )    
    elif '_GG2CNsl' in file_nominal:          Leg0 = ROOT.TLatex( xmin, ymax + dy*0.025, "#tilde{g}-#tilde{g} decays via sleptons/sneutrinos: #tilde{g}#tilde{g}#rightarrow qqqq(llll/lll#nu/ll#nu#nu/l#nu#nu#nu/#nu#nu#nu#nu)#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}" )
    elif '_SS2CNsl' in file_nominal:          Leg0 = ROOT.TLatex( xmin, ymax + dy*0.025, "#tilde{q}-#tilde{q} decays via sleptons/sneutrinos: #tilde{q}#tilde{q}#rightarrow qq(llll/lll#nu/ll#nu#nu/l#nu#nu#nu/#nu#nu#nu#nu)#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}" )
    elif '_GG2WWZZ' in file_nominal:          Leg0 = ROOT.TLatex( xmin, ymax + dy*0.025, "#tilde{g}-#tilde{g} decays via WWZZ: #tilde{g}#tilde{g}#rightarrow qqqq#tilde{#chi}_{1}^{#pm}#tilde{#chi}_{1}^{#pm} #rightarrow qqqqWZWZ#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}" )
    elif '_SS2WWZZ' in file_nominal:          Leg0 = ROOT.TLatex( xmin, ymax + dy*0.025, "#tilde{q}-#tilde{q} decays via WWZZ: #tilde{q}#tilde{q}#rightarrow qq#tilde{#chi}_{1}^{#pm}#tilde{#chi}_{1}^{#pm} #rightarrow qqWZWZ#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}" )
    elif '_Gtt_' in file_nominal:         Leg0 = ROOT.TLatex( xmin, ymax + dy*0.025, "#tilde{g}-#tilde{g}, #tilde{g}#rightarrow t#bar{t}#tilde{#chi}_{1}^{0}" )
    elif '_Higgsino_' in file_nominal:    Leg0 = ROOT.TLatex( xmin, ymax + dy*0.025, "Higgsino Simplified Model" )
    elif 'HiggsSU' in file_nominal: Leg0 = ROOT.TLatex( xmin, ymax + dy*0.025, "MSUGRA/CMSSM: tan#beta = 30, A_{0}= -2m_{0}, #mu>0" )
    else: Leg0 = ROOT.TLatex( xmin, ymax + dy*0.025, "#tilde{g}-#tilde{g} #rightarrow qqqqWW#tilde{#chi}_{1}^{0}#tilde{#chi}_{1}^{0}, x=1/2" )
    


    if Leg0 is not None:
        Leg0.SetTextAlign( 11 );
        Leg0.SetTextFont( 42 );
        Leg0.SetTextSize( ROOT.CombinationGlob.DescriptionTextSize);
        Leg0.SetTextColor( 1 );
        Leg0.AppendPad();

    #Leg3 = ROOT.TLatex( (xmin+xmax)*0.6, ymax + dy*0.025, 'Expected Limit Comparison' )
    #Leg3.SetTextAlign( 11 );
    #Leg3.SetTextFont( 42 );
    #Leg3.SetTextSize( ROOT.CombinationGlob.DescriptionTextSize);
    #Leg3.SetTextColor( 1 );
    #Leg3.AppendPad();


    #frame2.Draw( 'sameaxis' )
    #leg.Draw( 'same' )
    
    if 'HiggsSU' in file_nominal:
        staulsp = ROOT.TGraph()
        noRGE = ROOT.TGraph()  
        noEWSB = ROOT.TGraph() 
        tachyon = ROOT.TGraph()   
        negmasssq = ROOT.TGraph() 
        
        ROOT.msugraThExcl("../../../HistFitterUser/common/msugra_status_tanb30.txt", staulsp, negmasssq, noRGE, noEWSB, tachyon, "../../../HistFitterUser/common/mSugraGridtanbeta30_charginoMasses.root")
        
        c.cd()
        
        staulsp.SetFillColor(ROOT.CombinationGlob.c_LightGreen)
        staulsp.Draw("FSAME")
        staulsp.Draw("LSAME")
              
        c.Update()
        leg.AddEntry( staulsp, "Stau LSP","F" )

    leg.Draw( 'same' )
    Leg1 = ROOT.TLatex()
    Leg1.SetNDC()
    Leg1.SetTextAlign( 11 )
    Leg1.SetTextFont( 42 )
    Leg1.SetTextSize( ROOT.CombinationGlob.DescriptionTextSize )
    Leg1.SetTextColor( 1 )
    if not 'HiggsSU' in file_nominal: Leg1.DrawLatex(0.16,0.75, '#int L dt = %2.1f fb^{-1}, #sqrt{s}=8 TeV'%(lumi) )
    else: Leg1.DrawLatex(0.33,0.87, '#int L dt = %2.1f fb^{-1}, #sqrt{s}=8 TeV'%(lumi) )
    Leg1.AppendPad()

    Leg2 = ROOT.TLatex()
    Leg2.SetNDC()
    Leg2.SetTextAlign( 11 )
    Leg2.SetTextSize( ROOT.CombinationGlob.DescriptionTextSize )
    Leg2.SetTextColor( 1 )
    Leg2.SetTextFont(42)
    if prefix is not None: 
        if not 'HiggsSU' in file_nominal: Leg2.DrawLatex(0.16,0.82,prefix)
        else: Leg2.DrawLatex(0.33,0.81,prefix)
        Leg2.AppendPad()
        
    c.Update()

    frame2.Draw( 'sameaxis' )
    #leg.Draw( 'same' )

    # Diagonal line
    diagonal = None 
    if '_Gtt_' in file_nominal:            diagonal = ROOT.TLine(500., 500.-2*172.5, 700.+2*172.5, 700.)
    elif '_Higgsino_' in file_nominal:     diagonal = ROOT.TLine(125., 125., 600., 600. )
    elif ("SS" in file_nominal and not 'gridx' in file_nominal) or ("GG" in file_nominal and not 'gridx' in file_nominal) and not 'WWZZ' in file_nominal: diagonal = ROOT.TLine(225., 225., 1025., 1025.)
    elif 'WWZZ' in file_nominal:
        diagonal = ROOT.TLine(225., 225., 1025., 1025.)
    if diagonal: 
        diagonal.SetLineStyle(2)
        if not '_m12EE60_' in file_nominal: diagonal.Draw()
    
    gtt = ROOT.TLatex(550,590,"m_{#tilde{g}} < m_{#tilde{#chi}^{0}_{1}}")
    if "SS" in file_nominal:
        gtt.SetText(750,780,"m_{#tilde{q}} < m_{#tilde{#chi}^{0}_{1}}")
    if "GG" in file_nominal:
        gtt.SetText(750,790,"m_{#tilde{g}} < m_{#tilde{#chi}^{0}_{1}}")
    #else: gtt.SetText(550,590,"m_{#tilde{g}} < m_{#tilde{#chi}^{0}_{1}}")

    gtt.SetTextSize(0.03)
    gtt.SetTextColor(14)
    gtt.SetTextAngle(43)
    if "SS" in file_nominal:
        gtt.SetTextAngle(40)
    gtt.SetTextFont(42)

    if not "gridx" in file_nominal and not "Higgs" in file_nominal:
        gtt.Draw("same")    
        
              
    leg2 = ROOT.TLegend(0.61,0.85,0.91,0.92)    
    leg2.SetTextSize( ROOT.CombinationGlob.DescriptionTextSize );
    leg2.SetTextSize( 0.03 );
    leg2.SetTextFont( 42 );
    leg2.SetFillColor( 0 );
    leg2.SetFillStyle(1001);
    #leg2.AddEntry(graph,"#splitline{1-2 lepton(s)+ jets + E_{T}^{miss}}{arxiv:1208.4688}","F")
    if '1step' in file_nominal:
        leg2.AddEntry(graph,"PRD 86 (2012) 092002","F")
    elif "WWZZ" in file_nominal:
        leg2.AddEntry(twostepexclusion_curve,"PRD 86 (2012) 092002","F")
    if '1step' in file_nominal or 'WWZZ' in file_nominal: 
        leg2.Draw("same")


    # update the canvas
    c.Update()
    
    clslimits = ROOT.TLatex()
    #clslimits = ROOT.TLatex(360,887-197,"All limits at 95% CL_{S}")
    clslimits.SetNDC()
    clslimits.SetTextSize(0.03)
    clslimits.SetTextFont(42)
    if not 'gridx' in file_nominal and not 'HiggsSU' in file_nominal:
        clslimits.DrawLatex(0.15,0.55,"All limits at 95% CL_{S}") 
    elif 'HiggsSU' in file_nominal:
        clslimits.DrawLatex(0.7,0.65,"All limits at 95% CL_{S}")
    else:
        clslimits.DrawLatex(0.17,0.7,"All limits at 95% CL_{S}")  

    if print_theo:
        obsPOneSigma = ROOT.TLine()
        obsPOneSigma.SetLineStyle(3)
        obsPOneSigma.SetLineWidth(2)
        obsPOneSigma.SetLineColor(c_myRed)
        if not 'gridx' in file_nominal and not 'HiggsSU' in file_nominal:
            obsPOneSigma.DrawLineNDC(0.149,0.715,0.187,0.715)
        elif 'HiggsSU' in file_nominal:
            obsPOneSigma.DrawLineNDC(0.66,0.89,0.708,0.89)    
        else:
            obsPOneSigma.DrawLineNDC(0.6215,0.825,0.67445,0.825)

        obsMOneSigma = ROOT.TLine()
        obsMOneSigma.SetLineStyle(3)
        obsMOneSigma.SetLineWidth(2)
        obsMOneSigma.SetLineColor(c_myRed)
        if not 'gridx' in file_nominal and not 'HiggsSU' in file_nominal:
            obsMOneSigma.DrawLineNDC(0.149,0.695,0.187,0.695)
        elif 'HiggsSU' in file_nominal:
            obsMOneSigma.DrawLineNDC(0.66,0.87,0.708,0.87)
        else: 
            obsMOneSigma.DrawLineNDC(0.6215,0.805,0.67445,0.805)
  
    atlasLabel = ROOT.TLatex()
    atlasLabel.SetNDC()
    atlasLabel.SetTextFont(72)
    atlasLabel.SetTextColor(ROOT.kBlack)
    atlasLabel.SetTextSize( 0.05 )

    #if "gridx" in file_nominal: 
    #    atlasLabel.DrawLatex(0.6, 0.85,"ATLAS")
    #else:
    if not 'HiggsSU' in file_nominal: atlasLabel.DrawLatex(0.16, 0.87,"ATLAS")
    else: atlasLabel.DrawLatex(0.19, 0.87,"ATLAS")
    atlasLabel.AppendPad()

    progressLabel = ROOT.TLatex()
    progressLabel.SetNDC()
    progressLabel.SetTextFont(42)
    progressLabel.SetTextColor(ROOT.kBlack)
    progressLabel.SetTextSize( 0.05 )

    #if "gridx" in file_nominal: 
    #    progressLabel.DrawLatex(0.76, 0.85,"Internal")
    #else:
    #print 0.115*696*ROOT.gPad.GetWh()/(472*ROOT.gPad.GetWw())
    if not "HiggsSU" in file_nominal: progressLabel.DrawLatex(0.16+0.115*696*ROOT.gPad.GetWh()/(472*ROOT.gPad.GetWw()), 0.87,"Internal")
    #else: progressLabel.DrawLatex(0.19, 0.81,"Internal")
    else: 
        progressLabel.SetTextSize( 0.04 )
        progressLabel.DrawLatex(0.19, 0.82,"Internal")
    progressLabel.AppendPad()

    c.Update()    
    
    if printCLs:
    
        listTree = harvesttree(file_nominal.replace(".root",""))                          
        nentries = listTree.GetEntries()
                           
        pointLabel = ROOT.TLatex()
        pointLabel.SetTextSize(0.02)
        pointLabel.SetTextFont(42)

        for entry in range(nentries):
            listTree.GetEntry(entry)
            mstop = listTree.m0
            mchargino = listTree.m12
            if 'HiggsSU' in file_nominal and mchargino < 300.: continue
            CLs = listTree.CLs
            if not 'gridx' in file_nominal and (mstop < frame2.GetXaxis().GetXmin() or mstop>frame2.GetXaxis().GetXmax() or mchargino>frame2.GetYaxis().GetXmax()-5. or mchargino<frame2.GetYaxis().GetXmin()):
                continue
            if 'gridx' in file_nominal and (mstop < frame2.GetXaxis().GetXmin() or mstop>frame2.GetXaxis().GetXmax()-5. or mchargino>frame2.GetYaxis().GetXmax() or mchargino<frame2.GetYaxis().GetXmin()):
                continue    
            if CLs<0.05:
                pointLabel.SetTextColor(ROOT.kRed)
                pointLabel.DrawLatex(mstop,mchargino,"#bf{%1.2f}" % (CLs))
            else:
                pointLabel.SetTextColor(14)
                pointLabel.DrawLatex(mstop,mchargino,"%1.2f" % (CLs))

    if upperlimit and not 'HiggsSU' in file_nominal:
        listTree = harvesttree(file_nominal.replace("Nominal_hypotest","upperlimit").replace(".root","2"))                          
        nentries = listTree.GetEntries()
                           
        pointLabel = ROOT.TLatex()
        pointLabel.SetTextSize(0.02)
        pointLabel.SetTextFont(42)

        for entry in range(nentries):
            listTree.GetEntry(entry)
            mstop = listTree.m0
            mchargino = listTree.m12
            if 'HiggsSU' in file_nominal: continue
            if not 'gridx' in file_nominal and (mstop < frame2.GetXaxis().GetXmin() or mstop>frame2.GetXaxis().GetXmax() or mchargino>frame2.GetYaxis().GetXmax()-5. or mchargino<frame2.GetYaxis().GetXmin()):
                continue
            if 'gridx' in file_nominal and (mstop < frame2.GetXaxis().GetXmin() or mstop>frame2.GetXaxis().GetXmax()-5. or mchargino>frame2.GetYaxis().GetXmax() or mchargino<frame2.GetYaxis().GetXmin()):
                continue
            exXsec = listTree.excludedXsec
            pointLabel.SetTextColor(14)
            if exXsec >= 1.:
                pointLabel.DrawLatex(mstop,mchargino,"%1.0f" % (exXsec))		
            else:
                pointLabel.DrawLatex(mstop,mchargino,"%1.2f" % (exXsec))


    # create plots
    # store histograms to output file
    if outputfilename=='':
        outFileNom = 'plots/limit_'+file_nominal.replace('.root','')
    else:
        outFileNom = 'plots/limit_'+outputfilename
    if allObs: outFileNom += '_OBS'
    else:      outFileNom += '_EXP'
    ROOT.CombinationGlob.imgconv( c, outFileNom );

    del leg
    del frame2


def MirrorBorders( hist ):
    numx = hist.GetNbinsX()
    numy = hist.GetNbinsY()
  
    # corner points
    hist.SetBinContent(0,0,hist.GetBinContent(1,1))
    hist.SetBinContent(numx+1,numy+1,hist.GetBinContent(numx,numy))
    hist.SetBinContent(numx+1,0,hist.GetBinContent(numx,1))
    hist.SetBinContent(0,numy+1,hist.GetBinContent(1,numy))

    # Fix the other points 
    for i in xrange(1,numx+1):
        hist.SetBinContent(i,0,	   hist.GetBinContent(i,1));
        hist.SetBinContent(i,numy+1, hist.GetBinContent(i,numy));
    for i in xrange(1,numy+1):
        hist.SetBinContent(0,i,      hist.GetBinContent(1,i));
        hist.SetBinContent(numx+1,i, hist.GetBinContent(numx,i));


def AddBorders( hist, name='StupidName', title='StupidTitle'):
    nbinsx = hist.GetNbinsX()
    nbinsy = hist.GetNbinsY()
  
    xbinwidth = ( hist.GetXaxis().GetBinCenter(nbinsx) - hist.GetXaxis().GetBinCenter(1) ) / float(nbinsx-1)
    ybinwidth = ( hist.GetYaxis().GetBinCenter(nbinsy) - hist.GetYaxis().GetBinCenter(1) ) / float(nbinsy-1)
  
    xmin = hist.GetXaxis().GetBinCenter(0) - xbinwidth/2. 
    xmax = hist.GetXaxis().GetBinCenter(nbinsx+1) + xbinwidth/2. 
    ymin = hist.GetYaxis().GetBinCenter(0) - ybinwidth/2. 
    ymax = hist.GetYaxis().GetBinCenter(nbinsy+1) + ybinwidth/2. 
  
    hist2 = ROOT.TH2F(name, title, nbinsx+2, xmin, xmax, nbinsy+2, ymin, ymax);
  
    for ibin1 in xrange(hist.GetNbinsX()+2):
        for ibin2 in xrange(hist.GetNbinsY()+2):
            hist2.SetBinContent( ibin1+1, ibin2+1, hist.GetBinContent(ibin1,ibin2) );
  
    return hist2


def SetBorders( hist, val=0 ):
    numx = hist.GetNbinsX()
    numy = hist.GetNbinsY()
  
    for i in xrange(numx+2):
        hist.SetBinContent(i,0,val);
        hist.SetBinContent(i,numy+1,val);
    for i in xrange(numy+2):
        hist.SetBinContent(0,i,val);
        hist.SetBinContent(numx+1,i,val);


def FixAndSetBorders(file_nominal, hist, name='hist3', title='hist3', val=0 ):
    hist0 = hist.Clone() # histogram we can modify
    
    #if not "gridx" in file_nominal:
    if "HiggsSU" in file_nominal:
        MirrorBorders( hist0 ) # mirror values of border bins into overflow bins
    
    hist1 = AddBorders( hist0, "hist1", "hist1" );   
    # add new border of bins around original histogram,
    # ... so 'overflow' bins become normal bins
    SetBorders( hist1, val );                              
    # set overflow bins to value 1
    
    histX = AddBorders( hist1, "histX", "histX" )
    # add new border of bins around original histogram,
    # ... so 'overflow' bins become normal bins
    
    hist3 = histX.Clone()
    hist3.SetName( name )
    hist3.SetTitle( title )
    
    del hist0, hist1, histX
    return hist3 # this can be used for filled contour histograms


def DrawContourLine95( leg, hist, text='', linecolor=ROOT.kBlack, linestyle=2, linewidth=2 ):
    # contour plot
    h = hist.Clone()
    h.SetContour(1)
    pval = ROOT.CombinationGlob.cl_percent[1]
    signif = ROOT.TMath.NormQuantile(1-pval)
    h.SetContourLevel( 0, signif )
  
    #print linewidth, linestyle
    h.SetLineColor( linecolor )
    h.SetLineWidth( linewidth )
    h.SetLineStyle( linestyle )
    #h.Print()
    h.Draw( "samecont3" );
    
    if text is not '': leg.AddEntry(h,text,'l')
    return leg,h


def ContourGraph( hist ):
    gr0 = ROOT.TGraph()
    h = hist.Clone()
    #h.Print()
    h.GetYaxis().SetRangeUser(20,1000)
    h.GetXaxis().SetRangeUser(100,6100)
    gr = gr0.Clone(h.GetName())
    h.SetContour( 1 )
 
    pval = ROOT.CombinationGlob.cl_percent[1]
    signif = ROOT.TMath.NormQuantile(1-pval)
    h.SetContourLevel( 0, signif )
    h.Draw("CONT LIST")
    h.SetDirectory(0)
    ROOT.gPad.Update()
 
    contours = ROOT.gROOT.GetListOfSpecials().FindObject("contours")
    #print contours
    list0 = contours[0]
    #list0.Print()
    if list0.GetEntries()==0:
        return None

    #list.Print()
    gr = list0[0]
    #gr.Print()
    #grTmp = ROOT.TGraph()

    for k in xrange(list0.GetSize()):
        if gr.GetN() < list0[k].GetN(): gr = list0[k]
 
    gr.SetName(hist.GetName())
    #print gr
    #gr.Print()
    return gr;


def DrawExpectedBand( gr1, gr2, fillColor, fillStyle, cut = 0):

    number_of_bins = max(gr1.GetN(),gr2.GetN());
   
    gr1N = gr1.GetN();
    gr2N = gr2.GetN();

    N = number_of_bins;
   
    xx0 = ROOT.Double(0)
    yy0 = ROOT.Double(0)
    x0 = ROOT.Double(0)
    y0 = ROOT.Double(0)    
    xx1 = ROOT.Double(0)
    yy1 = ROOT.Double(0)
   
    x1=[]
    y1=[]
    x2=[]
    y2=[]    
   
    for j in xrange(gr1N):
        gr1.GetPoint(j,xx0,yy0)
        x1 += [float(xx0)]
        y1 += [float(yy0)]
    if gr1N < N:
        for i in xrange(gr1N,N):
            x1 += [ float(x1[gr1N-1]) ]
            y1 += [ float(y1[gr1N-1]) ]
   
    for j in xrange(gr2N):
        gr2.GetPoint(j,xx1,yy1)
        x2 += [float(xx1)]
        y2 += [float(yy1)]
    if gr2N < N:
        for i in xrange(gr2N,N):
            x2 += [float( x2[gr1N-1]) ]
            y2 += [ float(y2[gr1N-1]) ]
            
    #print x1,x2,y1,y2

    grshade = ROOT.TGraphAsymmErrors(2*N)
    for i in xrange(N):
        if x1[i] > cut:
            grshade.SetPoint(i,x1[i],y1[i])
        if x2[N-i-1] > cut:
            grshade.SetPoint(N+i,x2[N-i-1],y2[N-i-1])
   
    #grshade.Print()
   
    # Apply the cut in the shade plot if there is something that doesnt look good...
    Nshade = grshade.GetN()
    for j in xrange(Nshade):
        grshade.GetPoint(j,x0,y0)
        if x0!=0 and y0!=0 :
            x00 = x0
            y00 = y0
            break
            
    #print x00, y00
   
    for j in xrange(Nshade):
        grshade.GetPoint(j,x0,y0)
        if x0 == 0 and y0 == 0:
            grshade.SetPoint(j,x00,y00)
   
    #grshade.Print()
   
    # Now draw the plot...
    grshade.SetFillStyle(fillStyle);
    grshade.SetFillColor(fillColor);
    grshade.SetMarkerStyle(21);
    #grshade.Draw("Fsame");
    return grshade;


def DummyLegendExpected(leg, what,  fillColor, fillStyle, lineColor, lineStyle, lineWidth):
    gr = ROOT.TGraph()
    gr.SetFillColor(fillColor)
    gr.SetFillStyle(fillStyle)
    gr.SetLineColor(lineColor)
    gr.SetLineStyle(lineStyle)
    gr.SetLineWidth(lineWidth)
    leg.AddEntry(gr,what,"LF")
    return leg,gr


def InterpretNames(filename):
     name = filename.split('_hypotest')[0].split('OneLepton_')[1]
     if "GG1stepx12" in name: name = name.split('_GG1stepx12')[0]
     if "GG1stepgridx" in name: name = name.split('_GG1stepgridx')[0]
     if "SS1stepx12" in name: name = name.split('_SS1stepx12')[0]
     if "SS1stepgridx" in name: name = name.split('_SS1stepgridx')[0]
     if "GG2WWZZ" in name: name = name.split('_GG2WWZZ')[0]
     if "GG2CNsl" in name: name = name.split('_GG2CNsl')[0]
     if "SS2WWZZ" in name: name = name.split('_SS2WWZZ')[0]
     if "SS2CNsl" in name: name = name.split('_SS2CNsl')[0]
     
     print name
     if name=="combined_5_6_jets": descriptionname="3, 5, 6 jets SRs combined, default"
     elif name=="combined_5_6_jets_onebin": descriptionname="3, 5, 6 jets SRs combined, one bin"
     elif name=="combined_5_6_loose_onebin": descriptionname="relaxed 3, 5, 6 jets SRs combined, one bin"
     elif name=="combined_5_6_jets_met3jet": descriptionname="3 (fit in E_{T}^{miss}), 5, 6 jets SRs combined"
     elif name=="combined_5_6_jets_met3jet_2": descriptionname="3 (fit in E_{T}^{miss}, hard m_{eff} cut), 5, 6 jets SRs combined"     
     elif name=="combined_5_6_jets_met3jet_onebin": descriptionname="3 (fit in E_{T}^{miss}), 5, 6 jets SRs combined, one bin"
     elif name=="combined_5_6_jets_meffonly": descriptionname="3, 5, 6 jets SRs combined, shape fit in m_{eff}" 
     elif name=="combined_5_6_jets_bjetveto": descriptionname="3, 5, 6 jets SRs combined, b-jet veto" 
     elif name=="combined_3_6_7_jets_onebin": descriptionname="3, 6, 7 jets SRs combined, one bin"
     elif name=="combined_3_6_7_jets": descriptionname="3, 6, 7 jets SRs combined" 
     elif name=="combined_3_5_jets": descriptionname="3 and 5 jets SRs combined" 
     elif name=="combined_20sys" or name=="combined_20sys_2": descriptionname="3, 5, 6 jets SRs combined, 20 % syst." 
     elif name=="combined_50sys" or name=="combined_50sys_2": descriptionname="3, 5, 6 jets SRs combined, 50 % syst." 
     elif name=="combined_80sys" or name=="combined_80sys_2": descriptionname="3, 5, 6 jets SRs combined, 80 % syst."
     elif name=="combined_30sys_2": descriptionname="3, 5, 6 jets SRs combined, 30 % syst."   
     elif name=="3jetSR_exclu": descriptionname="3 jet SR, exclusive"
     elif name=="3jetSR_inclu": descriptionname="3 jet SR, inclusive"
     elif name=="5jetSR_exclu": descriptionname="5 jet SR, exclusive"
     elif name=="5jetSR_inclu": descriptionname="5 jet SR, inclusive" 
     elif name=="6jetSR_exclu": descriptionname="6 jet SR, exclusive"
     elif name=="6jetSR_inclu": descriptionname="6 jet SR, inclusive" 
     elif name=="combined_5_6_jets_met3jet_mt6jet": descriptionname="shape fit: E_{T}^{miss} (3 jets SR), m_{eff} (5 jets SR), m_{T} (6 jets SR)" 
     elif name=="combined_5_6_jets_met3jet_mt6jet_met250": descriptionname="shape fit: E_{T}^{miss} (3 jets SR), m_{eff} (5 jets SR), m_{T} (6 jets SR), lower E_{T}^{miss} cut in 6 jets SR"   
     elif name=="combined_5_6_jets_met3jet_mt6jet_mt120": descriptionname="shape fit: E_{T}^{miss} (3 jets SR), m_{eff} (5 jets SR), m_{T} (6 jets SR), lower m_{T} cut in 6 jets SR" 
     elif name=="combined_5_6_jets_met3jet_mt5jet": descriptionname="shape fit: E_{T}^{miss} (3 jets SR), m_{T} (5 jets SR), m_{eff} (6 jets SR)" 
     elif name=="combined_5_6_jets_met3jet_mt6jet_mt130_met300": descriptionname="shape fit: E_{T}^{miss} (3 jets SR), m_{eff} (5 jets SR), m_{T} (6 jets SR); m_{T} > 130 GeV and E_{T}^{miss} > 300 GeV"  
     elif name=="combined_5_6_jets_met3jet_mt6jet_mt130": descriptionname="shape fit: E_{T}^{miss} (3 jets SR), m_{eff} (5 jets SR), m_{T} (6 jets SR); m_{T} > 130 GeV"  
     else: descriptionname = "No description found"
     
     
     return descriptionname
     
hh=[]     

def DrawContourMassLine(hist, mass, color=14 ):

  h = ROOT.TH2F( hist )
  hh.append(h)
  h.SetContour( 1 )
  h.SetContourLevel( 0, mass )

  h.SetLineColor( color )
  h.SetLineStyle( 7 )
  h.SetLineWidth( 1 )
  #h.Print("range")
  h.Draw( "samecont3" )
  
  return
  

#!/bin/env python

import ROOT
ROOT.gROOT.ProcessLine('#include "contourmacros/CombinationGlob.C"')
ROOT.CombinationGlob.Initialize()

def compare_limits_SM( fileList , prefix=None, lumi=21, drawFirstObs=False, allObs=False, firstOneSigma=False , beginString='MultiJet_' , endString='_Gtt' ): 

    print 'Overlaying limits from files',fileList

    firstObs = None
    firstExp = None
    firstPOneSigma = None
    firstMOneSigma = None
    histosOrig = []
    for afile in fileList:
        f = ROOT.TFile.Open(afile,'READ')
        if firstObs==None: # First file
            firstObs = f.Get( 'sigp1clsf' )
            firstExp = f.Get( 'sigp1expclsf' )
            firstPOneSigma = f.Get( 'sigclsu1s' )
            firstMOneSigma = f.Get( 'sigclsd1s' )
            for hizzie in [firstObs,firstExp,firstPOneSigma,firstMOneSigma]: hizzie.SetDirectory(0)
        else: 
            if allObs: histosOrig += [ f.Get( 'sigp1clsf' ) ]
            else:      histosOrig += [ f.Get( 'sigp1expclsf' ) ]
            histosOrig[-1].SetDirectory(0)
        f.Close()

    firstObsH = FixAndSetBorders( firstObs , 'firstObsH' , '' , 0 )
    firstExpH = FixAndSetBorders( firstExp , 'firstExpH' , '' , 0 )
    histos = []
    for h in histosOrig: histos += [ FixAndSetBorders( h , h.GetName()+'H' , '' , 0 ) ]

    if firstOneSigma: # Only need these for the +/-1 sigma band
        firstPOneSigmaG = ContourGraph( FixAndSetBorders( firstPOneSigma , 'firstPOneSigmaG' , '' , 0 ) )
        firstMOneSigmaG = ContourGraph( FixAndSetBorders( firstMOneSigma , 'firstMOneSigmaG' , '' , 0 ) )

    # set text style
    ROOT.gStyle.SetPaintTextFormat(".2g")

    # Start drawing
    c = ROOT.TCanvas('LimitPlot','A limit plot', 0 , 0 , ROOT.CombinationGlob.StandardCanvas[0] , ROOT.CombinationGlob.StandardCanvas[1] )

    # create and draw the frame 
    if '_Gtt_' in fileList[0]:
        frame = ROOT.TH2F('frame', 'Simplified model limit for comparisons', 100, 500., 1300., 100, 75., 700. )
        frame.SetXTitle( "Gluino Mass [GeV]" )
        frame.SetYTitle( "LSP Mass [GeV]" )
    elif '_SM_GG_onestepCC_' in fileList[0] and 'NE60' in fileList[0]:
        frame = ROOT.TH2F('frame', 'Simplified model limit for comparisons', 100, 225., 1500., 100, 75., 1025. )
        frame.SetXTitle( "Gluino Mass [GeV]" )
        frame.SetYTitle( "LSP Mass [GeV]" )
    elif '_SM_SS_onestepCC_' in fileList[0] and 'NE60' in fileList[0]:
        frame = ROOT.TH2F('frame', 'Simplified model limit for comparisons', 100, 225., 1500., 100, 75., 1025. )
        frame.SetXTitle( "Squark Mass [GeV]" )
        frame.SetYTitle( "LSP Mass [GeV]" )
    elif '_SM_GG_onestepCC_' in fileList[0] and 'EE60' in fileList[0]:
        frame = ROOT.TH2F('frame', 'Simplified model limit for comparisons', 100, 225., 1500., 100, 0, 1. )
        frame.SetXTitle( "Gluino Mass [GeV]" )
        frame.SetYTitle( "x, Mass Splitting" )
    elif '_SM_SS_onestepCC_' in fileList[0] and 'EE60' in fileList[0]:
        frame = ROOT.TH2F('frame', 'Simplified model limit for comparisons', 100, 225., 1500., 100, 0, 1. )
        frame.SetXTitle( "Squark Mass [GeV]" )
        frame.SetYTitle( "x, Mass Splitting" )
    elif '_Higgsino_' in fileList[0]:
        frame = ROOT.TH2F('frame', 'Simplified model limit for comparisons', 100, 125., 650., 100, 75., 600. )
        frame.SetXTitle( "Light Stop Mass [GeV]" )
        frame.SetYTitle( "LSP Mass [GeV]" )
    elif '_SMGG2CNsl_' in fileList[0]:
        frame = ROOT.TH2F('frame', 'Simplified model limit for comparisons', 100, 250., 1500., 100, 45., 800. )
        frame.SetXTitle( "Gluino Mass [GeV]" )
        frame.SetYTitle( "LSP Mass [GeV]" )
    elif '_SMSS2CNsl_' in fileList[0]:
        frame = ROOT.TH2F('frame', 'Simplified model limit for comparisons', 100, 250., 1500., 100, 45., 800. )
        frame.SetXTitle( "Squark Mass [GeV]" )
        frame.SetYTitle( "LSP Mass [GeV]" )
    else:
        frame = ROOT.TH2F('frame', 'Simplified model limit for comparisons', 100, 100., 3750., 100, 115., 700. )
        frame.SetXTitle( "m_{0} [GeV]" )
        frame.SetYTitle( "m_{1/2} [GeV]" )

    ROOT.CombinationGlob.SetFrameStyle2D( frame, 1.0 )

    frame.GetYaxis().SetTitleOffset(1.35)
 
    frame.GetXaxis().SetTitleFont( 42 )
    frame.GetYaxis().SetTitleFont( 42 )
    frame.GetXaxis().SetLabelFont( 42 )
    frame.GetYaxis().SetLabelFont( 42 )
 
    frame.GetXaxis().SetTitleSize( 0.04 )
    frame.GetYaxis().SetTitleSize( 0.04 )
    frame.GetXaxis().SetLabelSize( 0.04 )
    frame.GetYaxis().SetLabelSize( 0.04 )
 
    frame.Draw()
    
    # Set up the legend
    leg = ROOT.TLegend(0.15,0.55,0.37,0.85)
    leg.SetTextSize( ROOT.CombinationGlob.DescriptionTextSize );
    leg.SetTextSize( 0.03 );
    leg.SetTextFont( 42 );
    leg.SetFillColor( 0 );
    leg.SetFillStyle(1001);

    # Draw the +/- 1 sigma yellow band 
    if firstOneSigma: grshadeExp = DrawExpectedBand( firstPOneSigmaG , firstMOneSigmaG , ROOT.CombinationGlob.c_DarkYellow , 1001 , 0).Clone()

    colors = [ ROOT.CombinationGlob.c_DarkGreen , ROOT.CombinationGlob.c_DarkGray , ROOT.CombinationGlob.c_BlueT3 , ROOT.CombinationGlob.c_DarkRed ,
               ROOT.CombinationGlob.c_DarkOrange , ROOT.CombinationGlob.c_DarkPink , ROOT.CombinationGlob.c_VDarkYellow, ROOT.CombinationGlob.c_HiggsGreen,
               ROOT.CombinationGlob.c_LightPink , ROOT.CombinationGlob.c_LightYellow, ROOT.CombinationGlob.c_Black ]

    #colors = [ ROOT.CombinationGlob.c_DarkGreen , ROOT.CombinationGlob.c_DarkGray , ROOT.CombinationGlob.c_BlueT3 , ROOT.CombinationGlob.c_DarkRed ,
    #           ROOT.CombinationGlob.c_DarkOrange , ROOT.CombinationGlob.c_DarkPink , ROOT.CombinationGlob.c_VDarkYellow ]
    if len(colors)<len(histos):
        print 'Only have',len(colors),'colors for',len(histos),'histograms.  Will crash...'

    newHists = []
    for i in xrange(len(histos)):
        if allObs:
            (leg,anewhist) = DrawContourLine95( leg, histos[i], fileList[i+1].split(endString)[0].split(beginString)[1], colors[i], 1, 1 )
            newHists += [anewhist]
        else:
            (leg,anewhist) = DrawContourLine95( leg, histos[i], fileList[i+1].split(endString)[0].split(beginString)[1], colors[i], 6, 1 )
            newHists += [anewhist]

    if drawFirstObs:
        (leg,anewhist) = DrawContourLine95( leg, firstObsH, 'Observed limit (#pm1 #sigma^{SUSY}_{theory})', ROOT.CombinationGlob.c_DarkRed,1,2)
        newHists += [anewhist]

    if firstOneSigma:
        (leg,anewhist) = DrawContourLine95( leg, firstExpH, '', ROOT.CombinationGlob.c_DarkBlueT3, 6 )
        newHists += [anewhist]
        (leg,anewhist) = DummyLegendExpected( leg, 'Expected limit (#pm1 #sigma_{exp})', ROOT.CombinationGlob.c_DarkYellow, 1001, ROOT.CombinationGlob.c_DarkBlueT3, 6, 2 )
        newHists += [anewhist]
    else:
        (leg,anewhist) = DrawContourLine95( leg, firstExpH, fileList[0].split(endString)[0].split(beginString)[1], ROOT.CombinationGlob.c_DarkBlueT3, 6 )
        newHists += [anewhist]

    c.cd()
    c.Update()
    
    # legend
    textSizeOffset = +0.000;
    xmax = frame.GetXaxis().GetXmax()
    xmin = frame.GetXaxis().GetXmin()
    ymax = frame.GetYaxis().GetXmax()
    ymin = frame.GetYaxis().GetXmin()
    dx   = xmax - xmin
    dy   = ymax - ymin

    # Label the decay process
    Leg0 = None
    if   '_GG_onestepCC' in fileList[0]: Leg0 = ROOT.TLatex( xmin, ymax + dy*0.025, "#tilde{g}-#tilde{g}, #tilde{g}#rightarrow q#bar{q}'W#tilde{#chi}_{1}^{0}" )
    elif '_SS_onestepCC' in fileList[0]: Leg0 = ROOT.TLatex( xmin, ymax + dy*0.025, "#tilde{q}-#tilde{q}, #tilde{q}#rightarrow #bar{q}'W#tilde{#chi}_{1}^{0}" )
    elif '_GG_' in fileList[0]:          Leg0 = ROOT.TLatex( xmin, ymax + dy*0.025, "#tilde{g}-#tilde{g}, #tilde{g}#rightarrow q#bar{q}'#tilde{#chi}_{1}^{0}" )
    elif '_SS_' in fileList[0]:          Leg0 = ROOT.TLatex( xmin, ymax + dy*0.025, "#tilde{s}-#tilde{s}, #tilde{s}#rightarrow q#tilde{#chi}_{1}^{0}" )
    elif '_Gtt_' in fileList[0]:         Leg0 = ROOT.TLatex( xmin, ymax + dy*0.025, "#tilde{g}-#tilde{g}, #tilde{g}#rightarrow t#bar{t}#tilde{#chi}_{1}^{0}" )
    elif '_Higgsino_' in fileList[0]:    Leg0 = ROOT.TLatex( xmin, ymax + dy*0.025, "Higgsino Simplified Model" )
    elif '_SMSS2CNsl_' in fileList[0]:   Leg0 = ROOT.TLatex( xmin, ymax + dy*0.025, "Two-step #tilde{q}-#tilde{q} Simplified Model" )
    elif '_SMGG2CNsl_' in fileList[0]:   Leg0 = ROOT.TLatex( xmin, ymax + dy*0.025, "Two-step #tilde{g}-#tilde{g} Simplified Model" )

    if Leg0 is not None:
        Leg0.SetTextAlign( 11 );
        Leg0.SetTextFont( 42 );
        Leg0.SetTextSize( ROOT.CombinationGlob.DescriptionTextSize);
        Leg0.SetTextColor( 1 );
        Leg0.AppendPad();

    Leg3 = ROOT.TLatex( (xmin+xmax)*0.5, ymax + dy*0.025, 'Expected Limit Comparison' )
    Leg3.SetTextAlign( 11 );
    Leg3.SetTextFont( 42 );
    Leg3.SetTextSize( ROOT.CombinationGlob.DescriptionTextSize);
    Leg3.SetTextColor( 1 );
    Leg3.AppendPad();

    Leg1 = ROOT.TLatex()
    Leg1.SetNDC()
    Leg1.SetTextAlign( 11 )
    Leg1.SetTextFont( 42 )
    Leg1.SetTextSize( ROOT.CombinationGlob.DescriptionTextSize )
    Leg1.SetTextColor( 1 )
    Leg1.DrawLatex(0.17,0.87, 'L^{int} = %2.1f fb^{-1}'%(lumi) )
    Leg1.AppendPad()

    Leg2 = ROOT.TLatex()
    Leg2.SetNDC()
    Leg2.SetTextAlign( 11 )
    Leg2.SetTextSize( ROOT.CombinationGlob.DescriptionTextSize )
    Leg2.SetTextColor( 1 )
    Leg2.SetTextFont(42)
    if prefix is not None: 
        Leg2.DrawLatex(0.33,0.87,prefix)
        Leg2.AppendPad()

    frame.Draw( 'sameaxis' )
    leg.Draw( 'same' )

    # Diagonal line
    diagonal = None 
    if '_Gtt_' in fileList[0]:            diagonal = ROOT.TLine(500., 500.-2*172.5, 700.+2*172.5, 700.)
    elif '_Higgsino_' in fileList[0]:     diagonal = ROOT.TLine(125., 125., 600., 600. )
    elif '_SMSS2CNsl_' in fileList[0] or '_SMGG2CNsl_' in fileList[0]: diagonal = ROOT.TLine( 250. , 250. , 800. , 800. )
    else:                                 diagonal = ROOT.TLine(225., 225., 1025., 1025.)
    diagonal.SetLineStyle(2)
    if not '_m12EE60_' in fileList[0]: diagonal.Draw()

    # update the canvas
    c.Update()

    # create plots
    # store histograms to output file
    outFileNom = 'plots/limit_compare_'+fileList[0].replace('.root','')
    if allObs: outFileNom += '_OBS'
    else:      outFileNom += '_EXP'
    ROOT.CombinationGlob.imgconv( c, outFileNom );

    del leg;
    del frame;


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


def FixAndSetBorders( hist, name='hist3', title='hist3', val=0 ):
    hist0 = hist.Clone() # histogram we can modify
    
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
  
    h.SetLineColor( linecolor )
    h.SetLineWidth( linewidth )
    h.SetLineStyle( linestyle )
    h.Draw( "samecont3" );
    
    if text is not '': leg.AddEntry(h,text,'l')
    return leg,h


def ContourGraph( hist ):
    gr0 = ROOT.TGraph()
    h = hist.Clone()
    h.GetYaxis().SetRangeUser(250,700)
    h.GetXaxis().SetRangeUser(50,4000)
    gr = gr0.Clone(h.GetName())
    h.SetContour( 1 )
 
    pval = ROOT.CombinationGlob.cl_percent[1]
    signif = ROOT.TMath.NormQuantile(1-pval)
    h.SetContourLevel( 0, signif )
    h.Draw("CONT LIST")
    h.SetDirectory(0)
    ROOT.gPad.Update()
 
    contours = ROOT.gROOT.GetListOfSpecials().FindObject("contours")
    list = contours[0]
    gr = list[0]
    grTmp = ROOT.TGraph()

    for k in xrange(list.GetSize()):
        if gr.GetN() < list[k].GetN(): gr = list[k]
 
    gr.SetName(hist.GetName())
    return gr;


def DrawExpectedBand( gr1, gr2, fillColor, fillStyle, cut = 0):
    number_of_bins = max(gr1.GetN(),gr2.GetN());
   
    gr1N = gr1.GetN();
    gr2N = gr2.GetN();

    N = number_of_bins;
   
    for j in xrange(gr1N):
        gr1.GetPoint(j,xx0,yy0);
        x1 += [xx0]
        y1 += [yy0]
    if gr1N < N:
        for i in xrange(gr1N,N):
            x1 += [ x1[gr1N-1] ]
            y1 += [ y1[gr1N-1] ]
   
    for j in xrange(gr2N):
        gr2.GetPoint(j,xx1,yy1)
        x2 += [xx1]
        y2 += [yy1]
    if gr2N < N:
        for i in xrange(gr2N,N):
            x2 += [ x2[gr1N-1] ]
            y2 += [ y2[gr1N-1] ]

    grshade = ROOT.TGraphAsymmErrors(2*N)
    for i in xrange(N):
        if x1[i] > cut:
            grshade.SetPoint(i,x1[i],y1[i])
        if x2[N-i-1] > cut:
            grshade.SetPoint(N+i,x2[N-i-1],y2[N-i-1])
   
    # Apply the cut in the shade plot if there is something that doesnt look good...
    Nshade = grshade.GetN();
    for j in xrange(Nshade):
        grshade.GetPoint(j,x0,y0)
        if x0!=0 and y0!=0 :
            x00 = x0
            y00 = y0
            break
   
    for j in xrange(Nshade):
        grshade.GetPoint(j,x0,y0)
        if x0 == 0 and y0 == 0:
            grshade.SetPoint(j,x00,y00)
   
    # Now draw the plot...
    grshade.SetFillStyle(fillStyle);
    grshade.SetFillColor(fillColor);
    grshade.SetMarkerStyle(21);
    grshade.Draw("F");
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


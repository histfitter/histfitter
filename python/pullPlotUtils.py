"""
 **********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Class  : PullPlotUtils                                                         *
 * Created: November 2012                                                         *
 *                                                                                *
 * Description:                                                                   *
 *      Functions to make pull plots                                              *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************
"""

"""
A module to generate pull plots. Import and overwrite getSampleColor and getRegionColor to define your own plot. Call makePullPlot() to make the plot. The other functions are all internal.
"""

import ROOT
from ROOT import *
ROOT.PyConfig.IgnoreCommandLineOptions = True
gSystem.Load("libSusyFitter.so")
#gROOT.Reset()
ROOT.gROOT.SetBatch(True)
from pValue import * # to compute significance as in https://github.com/dcasadei/psde

import os, string, pickle, copy
from math import sqrt

def getSampleColor(sample):
    """
    Get colour for a sample

    @param sample The sample to return the colour for
    """
    return 1

def getRegionColor(region):
    """
    Get colour for a region

    @param region The region to return the colour for
    """
    return 1

def PoissonError(obs):
    """
    Return the Poisson uncertainty on a number

    @param obs The number to calculate the uncertainty for
    reference from ATLAS Statistics Forum: http://www.pp.rhul.ac.uk/~cowan/atlas/ErrorBars.pdf
    """
    posError = TMath.ChisquareQuantile(1. - (1. - 0.68)/2. , 2.* (obs + 1.)) / 2. - obs
    negError = obs - TMath.ChisquareQuantile((1. - 0.68)/2., 2.*obs) / 2
    symError = abs(posError-negError)/2.
    return (posError,negError,symError)

def MakeBox(color=4, offset=0, pull=-1, horizontal=False, doPreFit=False, error=0):
    graph = TGraphErrors(1) if doPreFit else TGraph(4)
    if horizontal:
        if doPreFit:
            graph.SetPoint(0, 0.5+offset, pull)
            graph.SetPointError(0, 0., error)
        else:
            graph.SetPoint(0,0.1+offset,0);
            graph.SetPoint(1,0.1+offset,pull);
            graph.SetPoint(2,0.9+offset,pull);
            graph.SetPoint(3,0.9+offset,0);
    else:
        if doPreFit:
            graph.SetPoint(0, pull, 0.3+offset)
            graph.SetPoint(1, pull, 0.7+offset)
        else:
            graph.SetPoint(0,0,0.3+offset);
            graph.SetPoint(1,pull,0.3+offset);
            graph.SetPoint(2,pull,0.7+offset);
            graph.SetPoint(3,0,0.7+offset);
    graph.SetFillColor(color);
    graph.SetLineColor(color);
    graph.SetLineWidth(2);
    graph.SetLineStyle(1);
    graph.SetMarkerStyle(20);
    return graph

def GetFrame(outFileNamePrefix,Npar,ytitle="(n_{obs} - n_{pred}) / #sigma_{tot}",horizontal=False):
    offset = 0.;
    if horizontal:
        frame =TH2D("frame"+outFileNamePrefix, "",
                    Npar,0.,Npar,80,-4.,4.);
        frame.GetYaxis().SetTitleSize( 0.09 );
        frame.GetYaxis().SetTitleOffset(0.5)
        frame.GetYaxis().SetRangeUser( -3.5, 3.5 );
        frame.GetXaxis().SetLabelOffset( 0.05 );
        frame.GetXaxis().SetLabelSize( 0.12 );
        frame.GetYaxis().SetLabelSize( 0.09 );
        frame.GetYaxis().SetNdivisions(4)
        frame.SetYTitle(ytitle);
    else:
        frame =TH2D( "frame"+outFileNamePrefix, outFileNamePrefix,
                                1, -3.5, 3.5,
                                Npar, -offset, Npar+offset );

        scale = 1.0;
        frame.SetLabelOffset( 0.012, "Y" );# label offset on x axis
        frame.GetYaxis().SetTitleOffset( 1.25 );
        frame.GetXaxis().SetTitleSize( 0.06 );
        frame.GetYaxis().SetTitleSize( 0.06 );
        frame.GetXaxis().SetLabelSize( 0.06 );
        frame.GetYaxis().SetLabelSize( 0.07 );
        Npar = len(regionList)

        frame.SetLineColor(0);
        frame.SetTickLength(0,"Y");
        frame.SetXTitle( ytitle+"          " );
        frame.SetLabelOffset( 0.001, "X" );
        frame.SetTitleOffset( 1. , "X");
        frame.SetTitleSize( 0.06, "X" );
        frame.GetYaxis().CenterLabels( 1 );
        frame.GetYaxis().SetNdivisions( frame.GetNbinsY()+10, 1 );

        # global style settings
        gPad.SetTicks();
        frame.SetLabelFont(42,"X");
        frame.SetTitleFont(42,"X");
        frame.SetLabelFont(42,"Y");
        frame.SetTitleFont(42,"Y");
    return copy.deepcopy(frame)

def GetBoxes(all, results, renamedRegions, frame, doBlind, horizontal=False, doPreFit=False):
    counter = 0
    myr = reversed(results)
    if horizontal:
        myr = results
    for info in myr:
        name = info[0].replace(" ","")
        name = info[0].replace("_cuts","")

        if name in list(renamedRegions.keys()):
            name = renamedRegions[name]

        if ( (name.find("SR") >= 0)  and doBlind) or (name.find("CR") >= 0 and not doPreFit):
            counter += 1
            continue

        if horizontal:
            for bin in range(1,frame.GetNbinsX()+2):
                if frame.GetXaxis().GetBinLabel(bin) != name: continue
                counter = bin - 1
                break
            #frame.GetXaxis().SetBinLabel(counter+1,name);
        else:
            frame.GetYaxis().SetBinLabel(counter+1,name);

        color = getRegionColor(name)

        graph = MakeBox(offset=counter, pull=float(info[1]), color=color, horizontal=horizontal, doPreFit=doPreFit, error=info[7] if len(info) >= 8 else 0) 
        if doPreFit and "CR" in name:
          graph.SetMarkerColor(kRed)
          graph.SetLineColor(kRed)
          graph.SetMarkerStyle(8)
          graph.SetMarkerSize(1)
          graph.Draw("0PZE")
        else:
          graph.Draw("LF")

        counter += 1
        all.append(graph)

    return

def MakeHist(regionList, renamedRegions, results, hdata, hbkg, hbkgUp, hbkgDown, graph_bkg, graph_bkg2, graph_bkg3, graph_data, graph_pull, hbkgComponents):
    max = 0
    min = 99999999999.
    for counter in range(len(regionList)):#loop over all the regions
        nObs = 0
        nExp = 0
        nExpEr = 0
        nExpTotEr = 0
        nExpStatEr = 0
        nExpStatErUp = 0
        nExpStatErDo = 0
        nExpTotErUp = 0
        nExpTotErDo = 0
        pull = 0

        name = regionList[counter].replace(" ","")
        if name in list(renamedRegions.keys()):
            name = renamedRegions[name]

        for info in results: #extract the information
            if regionList[counter] in info[0]:
                nObs = info[2]
                nExp = info[3]
                nExpEr = info[4]

                if nExp>0:
                    nExpStatEr = sqrt(nExp)
                pEr = PoissonError(nObs)
                nExpStatErUp = pEr[0]
                nExpStatErDo = pEr[1]

                if name.find("CR") < 0:
                    nExpTotEr = sqrt(nExpEr*nExpEr)
                    nExpTotErUp = sqrt(nExpEr*nExpEr)
                    nExpTotErDo = sqrt(nExpEr*nExpEr)
                else:
                    nExpTotEr = nExpEr
        
                if (nObs-nExp) >= 0 and nExpTotErUp != 0:
                    pull = (nObs-nExp)/nExpTotErUp
                if (nObs-nExp) <= 0 and nExpTotErDo != 0:
                    pull = (nObs-nExp)/nExpTotErDo
                if nObs == 0 and nExp == 0:
                    pull = 0
                    nObs = -100
                    nPred = -100
                    nExpEr = 0
                    nExpTotEr = 0
                    nExpStatEr = 0
                    nExpStatErUp = 0
                    nExpStatErDo = 0
                    nExpTotErUp = 0
                    nExpTotErDo = 0

                #bkg components
                compInfo = info[6]
                for i in range(len(compInfo)):
                    hbkgComponents[i].SetBinContent(counter+1,compInfo[i][1])

                break

        if nObs>max: max = nObs
        if nExp+nExpTotErUp > max: max = nExp+nExpTotErUp
        if nObs<min and nObs != 0: min = nObs
        if nExp<min and nExp != 0: min = nExp

        graph_bkg.SetPoint(counter, hbkg.GetBinCenter(counter+1), nExp)
        graph_bkg.SetPointError(counter, 0.5, 0.5, nExpStatErDo, nExpStatErUp)
        graph_bkg2.SetPoint(counter, hbkg.GetBinCenter(counter+1), nExp)
        graph_bkg2.SetPointError(counter, 0.5, 0.5, nExpEr, nExpEr)
        graph_bkg3.SetPoint(counter, hbkg.GetBinCenter(counter+1), nExp)
        graph_bkg3.SetPointError(counter, 0.5, 0.5, 0, 0)
        graph_data.SetPoint(counter, hbkg.GetBinCenter(counter+1), nObs)
        if not nObs > 0: nObs = 0
        graph_data.SetPointError(counter, 0., 0, sqrt(nObs), sqrt(nObs))

        graph_pull.SetPoint(counter, hbkg.GetBinCenter(counter+1), pull)
        graph_pull.SetPointError(counter, 0., 0, 0, 0)

        hdata.GetXaxis().SetBinLabel(counter+1, name)
        hdata.SetBinContent(counter+1, -1000)
        hdata.SetBinError(counter+1, 0.00001)
        hbkg.SetBinContent(counter+1, nExp)
        hbkg.SetBinError(counter+1, nExpStatEr)

        hbkgUp.SetBinContent(counter+1, nExp+nExpTotErUp)
        hbkgDown.SetBinContent(counter+1, nExp-nExpTotErDo)

    hdata.SetMaximum(1.3*max)
    #if min<=0: min=0.5
    #hdata.SetMinimum(0.95*min)
    hdata.SetMinimum(0.)
    #hdata.SetMinimum(0.1)
    return

def MakeHistPullPlot(samples, regionList, outFileNamePrefix, hresults, renamedRegions, doBlind, outDir="", minimum=0.1, maximum=None, logy=True, doSignificance=False):
    print("========================================", outFileNamePrefix)
    ROOT.gStyle.SetOptStat(0000);
    Npar=len(regionList)

    hdata = TH1D(outFileNamePrefix, outFileNamePrefix, Npar, 0, Npar);
    hdata.GetYaxis().SetTitle("Events")
    hdata.GetYaxis().SetTitleSize( 0.065 )
    hdata.GetYaxis().SetTitleOffset( 0.5 )
    hdata.GetXaxis().SetLabelSize( 0.06 )
    hdata.GetYaxis().SetLabelSize( 0.05 )
    hdata.SetMarkerStyle(20)
    hbkg = TH1D("hbkg", "hbkg", Npar, 0, Npar);
    hbkg.SetLineColor(1)
    hbkg.SetLineWidth(2)

    hbkgUp = TH1D("hbkgUp", "hbkgUp", Npar, 0, Npar);
    hbkgUp.SetLineStyle(0)
    hbkgUp.SetLineWidth(0)

    hbkgDown = TH1D("hbkgDown", "hbkgDown", Npar, 0, Npar);
    hbkgDown.SetLineStyle(0)
    hbkgDown.SetLineWidth(0)

    hbkgComponents = []
    samples.replace(" ","") #remove spaces, and split by comma => don't split by ", "
    for sam in samples.split(","):
        h = TH1D("hbkg"+sam, "hbkg"+sam, Npar, 0, Npar)
        h.SetFillColor(getSampleColor(sam))
        hbkgComponents.append(h)

    graph_bkg = TGraphAsymmErrors(Npar)
    graph_bkg.SetFillColor(1)
    graph_bkg2 = TGraphAsymmErrors(Npar)
    graph_bkg2.SetFillColor(1)
    graph_bkg2.SetLineWidth(2)
    graph_bkg2.SetFillStyle(3004)

    graph_bkg3 = TGraphAsymmErrors(Npar)
    graph_bkg3.SetFillColor(kCyan+1)
    graph_data = TGraphAsymmErrors(Npar)
    graph_data.SetFillColor(kCyan+1)

    graph_pull = TGraphAsymmErrors(Npar)

    MakeHist(regionList,  renamedRegions,  hresults, hdata, hbkg, hbkgDown, hbkgUp, graph_bkg, graph_bkg2, graph_bkg3, graph_data, graph_pull, hbkgComponents)

    myleg = TLegend(0.49,0.60,0.81,0.84)
    myleg.SetNColumns(2)
    myleg.SetBorderSize(0)
    myleg.SetFillStyle(0)
    myleg.AddEntry(graph_data, renamedRegions.get("data", "data"), "p")
    myleg.AddEntry(graph_bkg2, renamedRegions.get("bkg2", "total background"), "fl")
    # add background in same order as above
    for h, sample in zip(hbkgComponents, samples.split(",")):
      myleg.AddEntry(h, renamedRegions.get(sample, sample), "f")

    c = TCanvas("c"+outFileNamePrefix, outFileNamePrefix, 1000, 600);
    upperPad = ROOT.TPad("upperPad", "upperPad", 0.001, 0.35, 0.995, 0.995)
    lowerPad = ROOT.TPad("lowerPad", "lowerPad", 0.001, 0.001, 0.995, 0.35)

    upperPad.SetFillColor(0);
    upperPad.SetBorderMode(0);
    upperPad.SetBorderSize(2);
    upperPad.SetTicks()
    upperPad.SetTopMargin   ( 0.1 );
    upperPad.SetRightMargin ( 0.11 );
    upperPad.SetBottomMargin( 0.0025 );
    upperPad.SetLeftMargin( 0.10 );
    upperPad.SetFrameBorderMode(0);
    upperPad.SetFrameBorderMode(0);
    if logy: upperPad.SetLogy()
    upperPad.Draw()

    lowerPad.SetGridx();
    lowerPad.SetGridy();
    lowerPad.SetFillColor(0);
    lowerPad.SetBorderMode(0);
    lowerPad.SetBorderSize(2);
    lowerPad.SetTickx(1);
    lowerPad.SetTicky(1);
    lowerPad.SetTopMargin   ( 0.003 );
    lowerPad.SetRightMargin ( 0.11 );
    lowerPad.SetBottomMargin( 0.5 );
    lowerPad.SetLeftMargin( 0.10 );
    lowerPad.Draw()

    c.SetFrameFillColor(ROOT.kWhite)

    upperPad.cd()

    if minimum: hdata.SetMinimum(minimum)
    if maximum: hdata.SetMaximum(maximum)
    hdata.Draw("E0")
    myleg.Draw()
    stack = THStack("stack","stack")
    for h in reversed(hbkgComponents):
        stack.Add(h)
    stack.Draw("same")
    hbkg.Draw("hist,same")
    hbkgUp.Draw("hist,same")
    hbkgDown.Draw("hist,same")

    graph_bkg2.Draw("2")
    graph_data.SetMarkerStyle(20)
    graph_data.Draw("E0,P,Z")
    graph_data.Draw("E0,Z")
    hdata.Draw("E0,same")
    hdata.Draw("E0,same,axis")

    lumiText = TLatex()
    lumiText.SetNDC()
    lumiText.SetTextAlign( 11 )
    lumiText.SetTextFont( 42 )
    lumiText.SetTextSize( 0.06 )
    lumiText.SetTextColor( 1 )
    lumiText.DrawLatex(0.15, 0.7, "#sqrt{{s}}=13 TeV, {0:0.1f} fb^{{-1}}".format(getattr(MakeHistPullPlot,'luminosity',10.0)))
    lumiText.DrawLatex(0.15,0.8, "#bf{#it{ATLAS}} Internal")

    lowerPad.cd()

    # Draw frame with pulls
    if doSignificance:
        frame = GetFrame(outFileNamePrefix,Npar,"Significance",horizontal=True)
    else:
        frame = GetFrame(outFileNamePrefix,Npar,horizontal=True)
    for bin in range(1,hdata.GetNbinsX()+1):
        frame.GetXaxis().SetBinLabel(bin,hdata.GetXaxis().GetBinLabel(bin))
    if "CR" in outFileNamePrefix:
      frame.GetYaxis().SetRangeUser( 0, 2.3 )
      frame.GetYaxis().SetTitle("t#bar{t} norm. factor")
      frame.Draw("histo")
    else:
      frame.Draw();
    all = []
    GetBoxes(all, hresults, renamedRegions, frame, doBlind, True, doPreFit=bool("CR" in outFileNamePrefix))

    if doBlind:
        c.Print(os.path.join(outDir, "histpull_"+outFileNamePrefix+"_blindSR.eps"))
        c.Print(os.path.join(outDir, "histpull_"+outFileNamePrefix+"_blindSR.png"))
        c.Print(os.path.join(outDir, "histpull_"+outFileNamePrefix+"_blindSR.pdf"))
    else:
        c.Print(os.path.join(outDir, "histpull_"+outFileNamePrefix+".eps"))
        c.Print(os.path.join(outDir, "histpull_"+outFileNamePrefix+".png"))
        c.Print(os.path.join(outDir, "histpull_"+outFileNamePrefix+".pdf"))

    return

def makePullPlot(pickleFilename, regionList, samples, renamedRegions, outputPrefix, doBlind=True, outDir="",plotSignificance="",):
    """
    Make a pull plot from a pickle file of results

    @param pickleFilename Filename to open
    @param regionList List of regions to dxraw pulls for
    @param samples List of samples in each region
    @param renamedRegions List of renamed regions; dict of old => new names
    @param outputPrefix Prefix for the output file
    @param doBlind Blind the SR or not?
    @param plotSignificance: arxiv or atlas for recommendation to use to calculate significance
                             leave blank if no significance is calculated
    """
    try:
        picklefile = open(pickleFilename,'rb')
    except OSError:
        print("Cannot open pickle %s, continuing to next" % pickleFilename)
        return

    mydict = pickle.load(picklefile)

    #print len(mydict["names"])
    #print len(mydict["nobs"])

    results1 = []
    results2 = []
    for region in mydict["names"]:
        # TODO: this is pretty bad. we should zip all these things.
        index = mydict["names"].index(region)
        try:
            nbObs = mydict["nobs"][index]
        except:
            nbObs = 0

        #if "CR" in region:
        #  nbExp = mydict["TOTAL_MC_EXP_BKG_events"][index]
        #  nbExpEr = mydict["TOTAL_MC_EXP_BKG_err"][index]
        #  #nbExpPostFit = mydict["TOTAL_FITTED_bkg_events"][index]
        #else:
        nbExp = mydict["TOTAL_FITTED_bkg_events"][index]
        nbExpEr = mydict["TOTAL_FITTED_bkg_events_err"][index]
        #  #nbExpPostFit = 0

        pEr = PoissonError(nbObs)
        totEr = sqrt(nbExpEr*nbExpEr+pEr[2]*pEr[2])
        totErDo = sqrt(nbExpEr*nbExpEr+pEr[1]*pEr[1])
        totErUp = sqrt(nbExpEr*nbExpEr+pEr[0]*pEr[0])

        pEr_pull = PoissonError(nbExp)
        totEr_pull = sqrt(nbExpEr*nbExpEr+pEr_pull[2]*pEr_pull[2])
        totErDo_pull = sqrt(nbExpEr*nbExpEr+pEr_pull[1]*pEr_pull[1])
        totErUp_pull = sqrt(nbExpEr*nbExpEr+pEr_pull[0]*pEr_pull[0])

        if plotSignificance == "arxiv":
            #calculates significance from https://arxiv.org/abs/1111.2062
            print("plot significance in the bottom panel")
            pValue = pValuePoissonError(int(nbObs), nbExp, nbExpEr*nbExpEr)
            print("pval:", pValue)
            if pValue < 0.5:
                pull = pValueToSignificance(pValue, nbObs>nbExp )
                print(pull)
            else:
                pull = 0.0001
                print("pull at zero!")
        elif plotSignificance == "atlas":
            #significance calculated from https://cds.cern.ch/record/2643488
            # relabel variables to match CDS formula
            print('calculating significance from W. Buttinger and M.Lefebvre recommendation')
            factor1 = nbObs*log( (nbObs*(nbExp+nbExpEr**2))/(nbExp**2+nbObs*nbExpEr**2) )
            factor2 = (nbExp**2/nbExpEr**2)*log( 1 + (nbExpEr**2*(nbObs-nbExp))/(nbExp*(nbExp+nbExpEr**2)) )

            if nbObs < nbExp:
                pull  = -sqrt(2*(factor1 - factor2))
            else:
                pull  = sqrt(2*(factor1 - factor2))
            print(pull)

        else:
            print("plot pull = (obs-exp)/err in the bottom panel")
            if (nbObs-nbExp) > 0 and totErUp_pull != 0:
                pull = (nbObs-nbExp)/totErUp_pull
            if (nbObs-nbExp) <= 0 and totErDo_pull != 0:
                pull = (nbObs-nbExp)/totErDo_pull
            print(pull)
            if -0.02 < pull < 0: pull = -0.02 ###ATT: ugly
            if 0 < pull < 0.02:  pull = 0.02 ###ATT: ugly

        nbExpComponents = []
        for sam in samples.split(","):
            #if "CR" in region:
            #    nbExpComponents.append((sam, mydict["MC_exp_events_"+sam][index] ))
            #else:
            nbExpComponents.append((sam, mydict["Fitted_events_"+sam][index] ))

        if "SR" in region and doBlind:
            nbObs = -100
            pull = 0

        if "CR" in region:
            pull = mydict["Fitted_events_ttbar"][index]/mydict["MC_exp_events_ttbar"][index]
            print("ttbar SF: ", pull)
        else:
            print(f"{region:s}: {pull}")

        print(f"region: {region} nObs {nbObs}")

        results1.append((region,pull,nbObs,nbExp,nbExpEr,totEr,nbExpComponents))

    #pull
    if plotSignificance =="":
        MakeHistPullPlot(samples, regionList, outputPrefix, results1, renamedRegions, doBlind, outDir, 0.1)
    else:
        MakeHistPullPlot(samples, regionList, outputPrefix, results1, renamedRegions, doBlind, outDir, 0.1, None, True,True)
    # return the results array in case you want to use this somewhere else
    return results1

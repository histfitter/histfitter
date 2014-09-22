"""
 **********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Class  : GenerateToys                                                          *
 * Created: November 2012                                                         *
 *                                                                                *
 * Description:                                                                   *
 *      Function to generate toyMC RooDataSet                                     *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************
"""

from ROOT import TH1D, RooRealVar, RooArgList, RooArgSet, RooFit, RooDataHist, RooHistPdf

def generate(histList, varName, varLow, varHigh, histSig="", weightSig=0.):
    """
    Generate toy data

    @param histList List of histograms
    @param varname Variable name to use
    @param varLow Lower edge of left bin
    @param varHigh Upper edge of right bin
    @param histSig Optional signal histogram
    @param weightSig Optional signal weight
    """
    
    testHist_pred = TH1D()
    for (iHist, hist) in enumerate(histList):
        if not iHist:
            testHist_pred = hist.Clone("hPRED")
        else:
            testHist_pred.Add(hist)

    testHist_pred_ds = TH1D("hPSDATA", "hPSDATA", testHist_pred.GetNbinsX(), testHist_pred.GetXaxis().GetBinLowEdge(1), testHist_pred.GetXaxis().GetBinUpEdge(testHist_pred.GetNbinsX()))

    nEvents_pred = int(testHist_pred.Integral())
    print "nEvents_pred = %d" % nEvents_pred

    var = RooRealVar(varName, varName, varLow, varHigh)

    dh_pred = RooDataHist("dhPSDATA", "dhPSDATA", RooArgList(var), RooFit.Import(testHist_pred))

    ph_pred = RooHistPdf("phPSDATA", "phPSDATA", RooArgSet(var), dh_pred)

    ds_pred = ph_pred.generate(RooArgSet(var), nEvents_pred)

    testHist_pred_ds = ds_pred.fillHistogram(testHist_pred_ds, RooArgList(var))

    return testHist_pred_ds

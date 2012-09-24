from ROOT import TH1D,RooRealVar,RooArgList,RooArgSet,RooFit,RooDataHist,RooHistPdf

def generate(histList,varName,varLow,varHigh,histSig="",weightSig=0.):
    testHist_pred = TH1D()
    for (iHist,hist) in enumerate(histList):
        if not iHist:
            testHist_pred = hist.Clone("hPRED")
        else:
            testHist_pred.Add(hist)

    testHist_pred_ds = TH1D("hPSDATA","hPSDATA",testHist_pred.GetNbinsX(),testHist_pred.GetXaxis().GetBinLowEdge(1),testHist_pred.GetXaxis().GetBinUpEdge(testHist_pred.GetNbinsX()))

    nEvents_pred = int(testHist_pred.Integral())
    print "nEvents_pred = %d" % nEvents_pred

    var = RooRealVar(varName,varName,varLow,varHigh)

    dh_pred = RooDataHist("dhPSDATA","dhPSDATA",RooArgList(var),RooFit.Import(testHist_pred))

    ph_pred = RooHistPdf("phPSDATA","phPSDATA",RooArgSet(var),dh_pred)

    ds_pred = ph_pred.generate(RooArgSet(var),nEvents_pred)

    testHist_pred_ds = ds_pred.fillHistogram(testHist_pred_ds,RooArgList(var))

    return testHist_pred_ds

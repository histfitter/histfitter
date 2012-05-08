from ROOT import gROOT,gSystem,TFile,TH1F
import sys

gROOT.Reset()

variables = ["cuts","meff","met","mt","nJets","nBJets"]

systematics = ["NoSys","JESup","JESdown"]

samples = {"data":["data"],
           "signal":["signal"],
           "wz":["WJets","ZgammaJets","DiBoson"],
           "top":["TTbar","SingleTop"],
           "qcd":["Multijetdataest"]} 

regions = {"meff":"MeffR",
           "met":"MetR",
           "mt":"MtR",
           "nJets":"jR",
           "nBJets":"BjR"}

inputFile = TFile("./data/1Ele_3Jet_JEStest.root","READ")
outputFile = TFile("./data/1Ele_3Jet_JEStest_norm.root","RECREATE")

histos = {}

for var in variables:
    for sam in samples.keys():
        histo = TH1F()
        for syst in systematics:
            for (iPro,pro) in enumerate(samples[sam]):

                histPro = TH1F()

                if var == "cuts":
                    histPro = inputFile.Get("h_"+var+"AvgMu_"+syst+"_"+pro)
                else:
                    histPro = inputFile.Get("h_"+var+"AvgMu_"+regions[var]+"_"+syst+"_"+pro)

                if syst == "NoSys":
                    if iPro == 0:

                        histTitle = sam+"_"+var
                        nBins = histPro.GetNbinsX()
                        lowBin = histPro.GetXaxis().GetBinLowEdge(1)
                        highBin = histPro.GetXaxis().GetBinUpEdge(histPro.GetNbinsX())

                        histo = TH1F("h_"+histTitle,histTitle,nBins,lowBin,highBin)

                    histo.Add(histPro)
                elif not sam == "data" and not sam == "qcd":
                    if iPro == 0:

                        histTitle = sam+"_"+var+"_"+syst
                        nBins = histPro.GetNbinsX()
                        lowBin = histPro.GetXaxis().GetBinLowEdge(1)
                        highBin = histPro.GetXaxis().GetBinUpEdge(histPro.GetNbinsX())

                        histo = TH1F("h_"+histTitle,histTitle,nBins,lowBin,highBin)

                    histo.Add(histPro)

                histos[histo.GetTitle()] = histo

            if not syst == "NoSys" and not (sam == "data" or sam == "qcd"):

                try:
                    sysIntegral = histo.Integral()
                    nomIntegral = histos[sam+"_"+var].Integral()
                    normFactor = nomIntegral / sysIntegral
                    histo.Scale(normFactor)
                    print sam,var,syst,1./normFactor
                
                
                except ZeroDivisionError:
                    print "zero division",sam,syst,var
                    inputFile.Close()
                    sys.exit()

                outputFile.cd()
                histo.Write()

            elif syst == "NoSys":
                outputFile.cd()
                histo.Write()

            
inputFile.Close()

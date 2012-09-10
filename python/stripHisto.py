from ROOT import gROOT, TFile, TH1F

gROOT.Reset()

rootFile = TFile("./data/MTvsMET.root", "READ")

getNames = ["hDATA",
            "hSIG",
            "hWZ",
            "htt",
            "hQCD_WR",
            "hQCD_WR_low",
            "hQCD_WR_high",
            "hQCD_TR",
            "hQCD_TR_low",
            "hQCD_TR_high",
            "hQCD_SR",
            "hQCD_SR_low",
            "hQCD_SR_high"]

outFile = TFile("./data/MTvsMET_2CR1SR.root", "RECREATE")


newHists = []

for histName in getNames:
    hist = rootFile.Get(histName)
    newHist = TH1F(hist.GetName(), hist.GetTitle(), 3, 0.0, 3.0)
    newHist.SetBinContent(1, hist.GetBinContent(1))
    newHist.SetBinContent(2, hist.GetBinContent(2))
    newHist.SetBinContent(3, hist.GetBinContent(10))
    newHists.append(newHist)

outFile.cd()

for hist in newHists:
    hist.Write()

outFile.Close()

rootFile.Close()

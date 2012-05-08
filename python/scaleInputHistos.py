from ROOT import gROOT,gSystem,TFile,TH1D
import sys

gROOT.Reset()

if not len(sys.argv) == 5:
    print "usage is scaleInputHistos.py inputFileName outputFileName oldLumi newLumi"
    sys.exit(1)

inputFile = TFile(sys.argv[1],"READ")

outputFile = TFile(sys.argv[2],"RECREATE")

oldLumi = float(sys.argv[3])
newLumi = float(sys.argv[4])

keyIter = inputFile.GetListOfKeys().MakeIterator()

key = keyIter.Next()

newHists = []

while key:
    hist = TH1D(inputFile.Get(key.GetName()))
    hist.Scale(newLumi/oldLumi)
    newHists.append(hist)
    key = keyIter.Next()

outputFile.cd()
for hist in newHists:
    hist.Write()

outputFile.Close()

inputFile.Close()

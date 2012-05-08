from ROOT import gROOT,gSystem,TFile,TH1D
import sys

gROOT.Reset()

if not (len(sys.argv) == 2 or len(sys.argv) == 3):
    print "usage is extractConfigOverallSysValues.py inputFileName {CR,SR}"
    sys.exit(1)

inputFile = TFile(sys.argv[1],"READ")

doCR = False
doSR = False

try:
    if sys.argv[2] == "CR":
        doCR = True
    elif sys.argv[2] == "SR":
        doSR = True
except IndexError:
    pass

keyIter = inputFile.GetListOfKeys().MakeIterator()

key = keyIter.Next()

while key:
    if key.GetName().find("low") == -1 and key.GetName().find("high") == -1:
        try:
            nomHist = TH1D(inputFile.Get(key.GetName()))
            highHist = TH1D(inputFile.Get(key.GetName()+"_high"))
            lowHist = TH1D(inputFile.Get(key.GetName()+"_low"))
            try:
                highRatio = highHist.Integral() / nomHist.Integral()
                lowRatio = lowHist.Integral() / nomHist.Integral()
                #print key.GetName(),"high = ",highRatio,"low = ",lowRatio
                if key.GetName().startswith("hQCD_"):
                    tmp=key.GetName()[5:]
                    if doCR:
                        if not key.GetName().find("ChanCR") == -1:
                            print "for",key.GetName()
                            print '      <OverallSys Name="NormQCD_%s" High="%f" Low="%f" />'%(tmp,highRatio,lowRatio)
                            pass
                    elif doSR:
                        if not key.GetName().find("ChanSR") == -1:
                            print "for",key.GetName()
                            print '      <OverallSys Name="NormQCD_%s" High="%f" Low="%f" />'%(tmp,highRatio,lowRatio)
                            pass
                    else:
                        if key.GetName().find("ChanCR") == -1 and key.GetName().find("ChanSR") == -1:
                            print "for",key.GetName()
                            print '      <OverallSys Name="NormQCD_%s" High="%f" Low="%f" />'%(tmp,highRatio,lowRatio)
                            pass
            except ZeroDivisionError:
                pass
                #print "ZeroDivisionError for",key.GetName()
        except TypeError:
            highJESHist = TH1D(inputFile.Get(key.GetName()+"_JES_high"))
            lowJESHist = TH1D(inputFile.Get(key.GetName()+"_JES_low"))
            highWTHHist = TH1D(inputFile.Get(key.GetName()+"_WZTheory_high"))
            lowWTHHist = TH1D(inputFile.Get(key.GetName()+"_WZTheory_low"))
            highTTHHist = TH1D(inputFile.Get(key.GetName()+"_TopTheory_high"))
            lowTTHHist = TH1D(inputFile.Get(key.GetName()+"_TopTheory_low"))
            try:
                highJESRatio = highJESHist.Integral() / nomHist.Integral()
                lowJESRatio = lowJESHist.Integral() / nomHist.Integral()
                highWTHRatio = highWTHHist.Integral() / nomHist.Integral()
                lowWTHRatio = lowWTHHist.Integral() / nomHist.Integral()
                highTTHRatio = highTTHHist.Integral() / nomHist.Integral()
                lowTTHRatio = lowTTHHist.Integral() / nomHist.Integral()
                #print key.GetName(),"JES high = ",highJESRatio,"low = ",lowJESRatio
                #print key.GetName(),"WTH high = ",highWTHRatio,"low = ",lowWTHRatio
                #print key.GetName(),"TTH high = ",highTTHRatio,"low = ",lowTTHRatio
                if doCR:
                    if not key.GetName().find("ChanCR") == -1:
                        if highJESRatio and lowJESRatio:
                            print "for",key.GetName()
                            print '      <OverallSys Name="JES_CR" High="%f" Low="%f" />'%(highJESRatio,lowJESRatio)
                        if highWTHRatio and lowWTHRatio:
                            print "for",key.GetName()
                            print '      <OverallSys Name="WTH" High="%f" Low="%f" />'%(highWTHRatio,lowWTHRatio)
                        if highTTHRatio and lowTTHRatio:
                            print "for",key.GetName()
                            print '      <OverallSys Name="TTH" High="%f" Low="%f" />'%(highTTHRatio,lowTTHRatio)
                elif doSR:
                    if not key.GetName().find("ChanSR") == -1:
                        if highJESRatio and lowJESRatio:
                            print "for",key.GetName()
                            print '      <OverallSys Name="JES_SR" High="%f" Low="%f" />'%(highJESRatio,lowJESRatio)
                        if highWTHRatio and lowWTHRatio:
                            print "for",key.GetName()
                            print '      <OverallSys Name="WTH" High="%f" Low="%f" />'%(highWTHRatio,lowWTHRatio)
                        if highTTHRatio and lowTTHRatio:
                            print "for",key.GetName()
                            print '      <OverallSys Name="TTH" High="%f" Low="%f" />'%(highTTHRatio,lowTTHRatio)
                else:
                    if key.GetName().find("ChanSR") == -1 and key.GetName().find("ChanCR") == -1:
                        if highJESRatio and lowJESRatio:
                            print "for",key.GetName()
                            print '      <OverallSys Name="JES" High="%f" Low="%f" />'%(highJESRatio,lowJESRatio)
                        if highWTHRatio and lowWTHRatio:
                            print "for",key.GetName()
                            print '      <OverallSys Name="WTH" High="%f" Low="%f" />'%(highWTHRatio,lowWTHRatio)
                        if highTTHRatio and lowTTHRatio:
                            print "for",key.GetName()
                            print '      <OverallSys Name="TTH" High="%f" Low="%f" />'%(highTTHRatio,lowTTHRatio)                    


            except ZeroDivisionError:
                pass
                #print "ZeroDivisionError for",key.GetName()
    key = keyIter.Next()

inputFile.Close()

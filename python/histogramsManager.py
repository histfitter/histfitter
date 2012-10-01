from ROOT import TH1F

class HistogramsManager:
    """
    Manager class to store histograms and utilies
    """

    def __init__(self):
        return

    def generateHistoName(self):
        return

    def buildUserHisto(self, hName, xmin, binValues):
        
        h = TH1F(hName, hName, len(binValues), xmin, xmin+float(len(binValues)))
        for val in binValues:
            h.SetBinContent(iBin+1, val)
            pass
        return h
    
    def buildUserHistoSysFromHist(self, hName, binErr, hNom):
        if hNom.GetNbinsX() != len(binErr):
            raise ValueError("hNom and binErr must have same length in buildUserHistoSysFromHist()")
        
        #binErr is the relative errors
        xmin = hNom.GetXaxis().GetXmin()
        h = TH1F(hName, hName, len(binErr), xmin, xmin+float(len(binErr)))
        for iBin in xrange(hNom.GetNbinsX()):
            val=hNom.GetBinContent(iBin+1)*binErr[iBin]
            h.SetBinContent(iBin+1, val)
            pass
        return h

histMgr = HistogramsManager()

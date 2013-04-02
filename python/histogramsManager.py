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
        for iBin, val in enumerate(binValues):
            h.SetBinContent(iBin+1, val)
            pass
        return h

    def floatToArray(self,err,hNom):
        binErrs=[]
        for i in xrange(hNom.GetNbinsX()):
            binErrs.append(err)
        return binErrs

    def buildUserOverallSysFromHist(self, hName, err, hNom):
        if isinstance(err,float):
            binErrs=self.floatToArray(err,hNom)
        elif isinstance(err,list) and len(err)==1:
            binErrs=self.floatToArray(err[0],hNom)
        else:
            raise TypeError("err in buildUserOverallSysFromHist can only be a number or a list of len==1")
        return self.buildUserHistoSysFromHist(hName,binErrs,hNom)

    def buildUserHistoSysFromHist(self, hName, binErrs, hNom):
        if isinstance(binErrs,float):
            binErrs=self.floatToArray(binErrs,hNom)
        elif isinstance(binErrs,list):
            if len(binErrs)==1:
                binErrs=self.floatToArray(binErrs[0],hNom)
            elif hNom.GetNbinsX() != len(binErrs):
                raise ValueError("hNom and binErrs must have same length in buildUserHistoSysFromHist()")
        else:
            raise TypeError("binErrs of type %s is not supported"%type(binErrs))
         
        #binErrs is the relative errors
        xmin = hNom.GetXaxis().GetXmin()
        xmax = hNom.GetXaxis().GetXmax()
        #h = TH1F(hName, hName, len(binErrs), xmin, xmin+float(len(binErrs)))
        h = TH1F(hName, hName, len(binErrs), xmin, xmax)
        for iBin in xrange(hNom.GetNbinsX()):
            val=hNom.GetBinContent(iBin+1)*binErrs[iBin]
            h.SetBinContent(iBin+1, val)
            pass
        return h

histMgr = HistogramsManager()

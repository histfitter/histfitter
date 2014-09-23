"""
 **********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Class  : HistogramsManager                                                     *
 * Created: November 2012                                                         *
 *                                                                                *
 * Description:                                                                   *
 *      class to store histograms and utilities                                   *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************
"""

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
        """ 
        Build a histogram from the arguments. Number of bins is calculated from the length of binValues; the upper edge is calculated as xmin+len(binValues).

        @param hName Name of the histogram
        @param xmin Left edge of lower bin
        @param binValues Bin content in a list
        """
        h = TH1F(hName, hName, len(binValues), xmin, xmin+float(len(binValues)))
        for iBin, val in enumerate(binValues):
            h.SetBinContent(iBin+1, val)
            pass
        return h

    def floatToArray(self, err, h):
        """
        Return an array filled with values of 'err' with length equal to the number of x-axis bins of the histogram 
        
        @param err The value to use
        @param h A histogram to determine the number of x-axis bin of
        """

        binErrs=[]
        for i in xrange(h.GetNbinsX()):
            binErrs.append(err)
        return binErrs

    def buildUserOverallSysFromHist(self, hName, err, hNom):
        """
        Build a userOverAllSys from a nominal-value histogram and an error

        @param hName Name of the histogram
        @param err The error to use
        @param hNom The nominal-value histogram to construct the error for
        """
        if isinstance(err,float):
            binErrs = self.floatToArray(err,hNom)
        elif isinstance(err,list) and len(err) == 1:
            binErrs = self.floatToArray(err[0],hNom)
        else:
            raise TypeError("err in buildUserOverallSysFromHist can only be a number or a list of len==1")
        return self.buildUserHistoSysFromHist(hName, binErrs, hNom)

    def buildUserHistoSysFromHist(self, hName, binErrs, hNom):
        """
        Build a userHistoSys from a nominal-value histogram and an error, either an array or a float

        @param hName Name of the histogram
        @param err The error to use; either a list of bin-by-bin errors or a number
        @param hNom The nominal-value histogram to construct the error for
        """
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

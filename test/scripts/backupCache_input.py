"""
 **********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 *                                                                                *
 * Description:                                                                   *
 *      Python script to create an input ROOT files for the BackupCacheExample.py *
 *      configuration. Based on arXiV: [1809.11105].                              *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************
"""

import sys
import ROOT
from array import array
from ctypes import c_double

edges = {}
content = {}
errors = {}

SSZCReeEdges = array('d',[30,46,70,107,164,251,385,588,900])
SSZCRmmEdges = array('d',[10, 110, 270, 663, 1629])
SSZSRmmEdges = array('d',[400, 533, 711, 949, 1265, 1687, 2249, 3000, 4000])

edges["SSZCRee"] = SSZCReeEdges
edges["SSZCRmm"] = SSZCRmmEdges
edges["SSZSRmm"] = SSZSRmmEdges

SSZCReeData = [4, 11, 29, 47, 97, 67, 32, 17]
SSZCRmmData = [19, 56, 35, 9]
SSZSRmmData = [1,2,1,0,1,0,0,0]
contentData = {}
contentData["SSZCRee"] = SSZCReeData
contentData["SSZCRmm"] = SSZCRmmData
contentData["SSZSRmm"] = SSZSRmmData
content["Data"] = contentData

SSZCReeDY = [3.73141,2.79385,12.3528,46.9712,35.4671,31.4135,13.0329,8.397657]
SSZCReeDYErr = [1.55116,2.24227,3.85081,16.4837,16.5406,8.82658,2.20148,0.725788]
contentDY = {}
contentDY["SSZCRee"] = SSZCReeDY
content["SherpaDY221"] = contentDY
errorsDY = {}
errorsDY["SSZCRee"] = SSZCReeDYErr
errors["SherpaDY221"] = errorsDY

SSZCReeDiboson = [0.957352,2.76823,5.77898,12.4511,16.9316,13.372,9.65705,7.85562]
SSZCReeDibosonErr = [0.247681,0.257408,0.332118,0.511809,0.901763,0.50265,0.519117,0.590059]
SSZCRmmDiboson = [12.7376,36.6527,30.0965,7.80733]
SSZCRmmDibosonErr = [0.785144,0.842417,1.16414,0.62106]
SSZSRmmDiboson = [0.409023,0.227055,0.69857,0.519877,0.260704,0.100111,0.0742864,0.00256888]
SSZSRmmDibosonErr = [0.180793,0.0261992,0.135367,0.132438,0.0969434,0.0616987,0.0623639,0.00218721]
contentDB = {}
contentDB["SSZCRee"] = SSZCReeDiboson
contentDB["SSZCRmm"] = SSZCRmmDiboson
contentDB["SSZSRmm"] = SSZSRmmDiboson
content["dibosonSherpa"] = contentDB
errorsDB = {}
errorsDB["SSZCRee"] = SSZCReeDibosonErr
errorsDB["SSZCRmm"] = SSZCRmmDibosonErr
errorsDB["SSZSRmm"] = SSZSRmmDibosonErr
errors["dibosonSherpa"] = errorsDB

SSZCReeTop = [0.00821939,0.479264,2.27356,3.49508,6.65957,5.95597,2.87216,0.898622]
SSZCReeTopErr = [0.00392479,0.201347,0.597126,0.64871,1.00286,1.19304,0.622758,0.287019]
SSZCRmmTop = [0.918484,1.75598,1.2122,0.299642]
SSZCRmmTopErr = [0.0724927,0.0926004,0.0928907,0.0435881]
SSZSRmmTop = [0.00780762,0.0301227,0.034865,0.0439469,0.0186894,0.00426742,0,0]
SSZSRmmTopErr = [0.00455171,0.0118977,0.0162047,0.0176378,0.0101351,0.00348863,0,0]
contentTop = {}
contentTop["SSZCRee"] = SSZCReeTop
contentTop["SSZCRmm"] = SSZCRmmTop
contentTop["SSZSRmm"] = SSZSRmmTop
content["top_physics"] = contentTop
errorsTop = {}
errorsTop["SSZCRee"] = SSZCReeTopErr
errorsTop["SSZCRmm"] = SSZCRmmTopErr
errorsTop["SSZSRmm"] = SSZSRmmTopErr
errors["top_physics"] = errorsTop

SSZCReeFakes = [0.622575,2.64707,15.9221,22.6294,33.748,20.0333,19.8587,5.55986]
SSZCReeFakesErr = [0.717546,2.0035,3.27882,5.25105,5.24191,4.42596,3.67209,2.0007]
SSZCRmmFakes = [6.96086,17.8173,11.7191,1.14308]
SSZCRmmFakesErr = [2.3236,3.79825,3.05168,1.02517]
SSZSRmmFakes = [0,1.86172,0,0,0,0,0,0]
SSZSRmmFakesErr = [0,1.32676,0.00292439,0.00222235,0,0,0,0]
contentFakes = {}
contentFakes["SSZCRee"] = SSZCReeFakes
contentFakes["SSZCRmm"] = SSZCRmmFakes
contentFakes["SSZSRmm"] = SSZSRmmFakes
content["fakes"] = contentFakes
errorsFakes = {}
errorsFakes["SSZCRee"] = SSZCReeFakesErr
errorsFakes["SSZCRmm"] = SSZCRmmFakesErr
errorsFakes["SSZSRmm"] = SSZSRmmFakesErr
errors["fakes"] = errorsFakes

regions = [["SSZCRee","Mjj"],["SSZCRmm","Mjj"],["SSZSRmm","HT"]]
samples = ["Data","SherpaDY221","dibosonSherpa","top_physics","fakes"]


if __name__ == "__main__":
    outfile = ROOT.TFile(sys.argv[1], "RECREATE")

    for s in samples:
        values = content[s]
        err = errors[s] if s in list(errors.keys()) else None
        for r in regions:
            if not r[0] in list(values.keys()):
                continue
            if s == "Data":
                name = f"h{s}_{r[0]}_obs_{r[1]}"
                nameNorm = f"h{s}_{r[0]}Norm"
            else:
                name = f"h{s}Nom_{r[0]}_obs_{r[1]}"
                nameNorm = f"h{s}Nom_{r[0]}Norm"
            h = ROOT.TH1F(name, name, len(edges[r[0]]) - 1, edges[r[0]])
            hNorm = ROOT.TH1F(nameNorm, nameNorm, 1, 0.5, 1.5)
            v = values[r[0]]
            e = err[r[0]] if err else None
            for i in range(1, h.GetNbinsX() + 1):
                h.SetBinContent(i, v[i - 1])
                if e:
                    h.SetBinError(i, e[i - 1])
            NormErr = c_double(0.0)
            hNorm.SetBinContent(1, h.IntegralAndError(0, h.GetNbinsX(), NormErr, ""))
            hNorm.SetBinError(1, NormErr.value)
            h.Write()
            hNorm.Write()

    outfile.Close()

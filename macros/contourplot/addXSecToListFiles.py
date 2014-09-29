from math import sqrt
from ROOT import *
import os
theFile = TFile.Open('/afs/cern.ch/atlas/groups/susy/SignalCrossSectionsUncert/SimplModels/SignalUncertainties-SM_GG_onestep_Moriond2012_v0.root')

tt = theFile.Get('SignalUncertainties')


def extractCrossSection( Mass, tol = 0.1, finalState = 2, finalState2 = -1 ):
    xsec = 0.
    for i in xrange(tt.GetEntries()):
        tt.GetEntry(i)
        if abs(Mass - tt.mgluino) < tol and (tt.finalState == finalState or tt.finalState == finalState2):
            #print tt.Mass
            xsec += tt.crossSection
            pass
        pass
    return xsec 



def addXSecToListFiles(listFile="/afs/cern.ch/atlas/project/cern/susy/users/mbackes/SusyFitterDev/macros/contourplot/MySoftOneLeptonKtScaleFitMetMeff_SM_GG_onestepCC_R17_Output_upperlimit__1_harvest_list"):
    #listFile="/afs/cern.ch/atlas/project/cern/susy/users/mbackes/SusyFitterDev/macros/contourplot/MySoftOneLeptonKtScaleFitMetMeff_SM_GG_onestepCC_R17_Output_upperlimit__1_harvest_list"
    inFile = open(listFile, 'r')    
    lines = inFile.readlines()
    inFile.close()
    outFile = open(listFile, 'w')    
    for line in lines:
        mgluino = line.split(" ")[-3]
        upperLimit = line.split(" ")[-12]
        xsec = extractCrossSection(float(mgluino))
        excludedXsec = float(upperLimit) * (xsec)
        outFile.write(line.replace("-999007. -999007.",str(xsec)+" "+str(excludedXsec)))

##     # update tree description accordingly
##     treeDescriptionFiles = ['summary_harvest_tree_description.h','summary_harvest_tree_description.py'] 

##     for treeDescriptionFile in treeDescriptionFiles:
##         inFile = open(treeDescriptionFile, 'r')    
##         lines = inFile.readlines()
##         inFile.close()       

##         outFile = open(treeDescriptionFile, 'w')
        
##         for line in lines:
##             if 'description =' in line:
##                 print line
##                 line = line.replace("\n","")
##                 line = line.replace(":",":^")
##                 splitLine = line.split("^")
##                 splitLine[-1] = splitLine[-1].replace(";","")
##                 splitLine[-1] = splitLine[-1].replace('"',"")
##                 splitLine += [':xsec']
##                 splitLine += [':excludedXsec"']
##                 line = ''
##                 for split in splitLine:
##                     line += split
##                 if ".C" in treeDescriptionFile:
##                     line += ";"
##                 line += " \n"
##                 print line
                    
##             outFile.write(line)
            
##         outFile.close()
        
    


addXSecToListFiles()

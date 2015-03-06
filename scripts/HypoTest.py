#!/usr/bin/env python

import sys, commands
import os, os.path
import shutil
import glob

from ROOT import gROOT,gSystem,gDirectory,RooAbsData,RooRandom,RooWorkspace,TFile,RooFitResult

from math import fabs,isnan

## batch mode
sys.argv.insert(1, '-b')
gROOT.Reset()
gROOT.SetBatch(True)
del sys.argv[1]
gSystem.Load("libSusyFitter.so")
gROOT.Reset()

def min_CLs(hypo):
    CLs=1.
    for i in range(0,hypo.ArraySize()):
        if hypo.GetResult(i).CLs()<CLs: CLs = hypo.GetResult(i).CLs()
    return CLs
    
def max_CLs(hypo):
    CLs=0.
    for i in range(0,hypo.ArraySize()):
        if hypo.GetResult(i).CLs()>CLs: CLs = hypo.GetResult(i).CLs()
    return CLs
    

def RedoScan(w,testStatType,hypo):
    maxX=hypo.GetLastXValue()
    #del hypo
    #hypo=0
    
    n=hypo.ArraySize()
    print "Available points: ",str(n)
    print "Recalculate x"
    if n>=2 and not isnan(hypo.GetResult(n-2).CLs()) and not isnan(hypo.GetLastResult().CLs()):
        diffCLs=fabs(hypo.GetResult(n-2).CLs()-hypo.GetLastResult().CLs())
        diffX=(maxX-hypo.GetXValue(n-2))
        newX=maxX
        newCLs=hypo.GetLastResult().CLs()
        while newCLs>0.05:
            newX+=diffX
            newCLs-=diffCLs
        newX = newX*1.2
    else: newX=2.*maxX

    del hypo
    hypo=0
    
    print "Redo scan with a larger x range: 0, ",str(newX)
    hypo = RooStats.DoHypoTestInversion(w,1,2,testStatType,True,20,0.,newX)
    #if ( hypo!=0 ):
    #    hypo.ExclusionCleanup()
        #if hypo.GetLastResult().CLs()>0.05:
        #    hypo = RedoScan(w,testStatType,hypo.GetLastXValue()) 
    
    return hypo   
    

def doHypoTest(fixSigXSec, SigXSecSysnsigma,sigSamples):

    outfileName="results/"+sigSamples[0]+"_hypotest.root"
    if SigXSecSysnsigma > 0.:
        outPrefix = "Up"
    elif SigXSecSysnsigma == 0.:
        outPrefix = "Nominal"
    elif SigXSecSysnsigma < 0.:
        outPrefix = "Down"
    
    outfile = TFile.Open("results/"+sigSamples[0]+"_"+outPrefix+"_hypotest.root","UPDATE");
    if not outfile:
        print "ERROR TFile <"+ outfileName+"> could not be opened"
        #return

    #inFile = "results/MyOneLeptonKtScaleFitR17_Sig_"+sigSamples[0]+"_combined_NormalMeasurement_model.root"
    infile_list=glob.glob("results/*"+sigSamples[0]+"_combined_BasicMeasurement_model.root")
    print infile_list
    if len(infile_list)!=1:
        print "ERROR: More than one file given - please give only one file."
        sys.exit(1)
    #inFileName = commands.getstatusoutput("ls results/*"+sigSamples[0]+"_combined_BasicMeasurement_model.root")[1]
    
    inFileName = infile_list[0]
    inFile = TFile.Open(inFileName)
    if not inFile:
        print "ERROR TFile could not be opened"
        outfile.Close()
        #return
        
    w = inFile.Get("combined")
    #Util.ReadWorkspace(inFile,"combined")
    #w=gDirectory.Get("w")	
    if not w:
        print "workspace 'combined' does not exist in file"
        #return

    print "Processing analysis "+sigSamples[0]
    
    Util.SetInterpolationCode(w,4)

    if(fixSigXSec and not sigSamples[0] == "" ):
        w.var("alpha_SigXSec").setVal(SigXSecSysnsigma)
        w.var("alpha_SigXSec").setConstant(True)
  
    #set Errors of all parameters to 'natural' values before plotting/fitting
    Util.resetAllErrors(w)

  
    #Do first fit and save fit result in order to control fit quality
  
    fitresult = Util.doFreeFit( w , 0, False, True )
  
    if (fitresult):
        outfile.cd()
        hypName="fitTo_"+sigSamples[0]
        fitresult.SetName(hypName);
        fitresult.Print()
        fitresult.Write()
        print ">>> Now storing RooFitResult <"+hypName+">"
   
    hypo = RooStats.DoHypoTestInversion(w,configMgr.nTOYs,configMgr.calculatorType,3)
  
    if (hypo):     
        outfile.cd()
        hypName2="hypo_"+sigSamples[0]
        hypo.SetName(hypName2)
        hypo.Write()
        print ">>> Now storing HypoTestInverterResult <"+hypName2+">"
        del(hypo)

    print ">>> Done. Stored HypoTestInverterResult and fit result in file <"+outfileName+">"
        
    outfile.Close()

    pass

    return 0



if __name__ == "__main__":
    from configManager import configMgr
    configMgr.readFromTree = False
    configMgr.executeHistFactory=False
    configMgr.calculatorType=0
    configMgr.nTOYS=1000
    runInterpreter = False
    runFit = False
    printLimits = False
    doHypoTests = False
    fixSigXSec = False
    sigSamples = []
    
    print "\n * * * Welcome to HistFitter * * *\n"

    import os, sys
    import getopt
    from ROOT import RooStats,Util 
    def usage():
        print "HistFitter.py [-i] [-t] [-w] [-f] [-l] [-l] [-p] [-n nTOYs] [-s seed] [-g gridPoint]\n"
        print "(all OFF by default. Turn steps ON with options)"
        print "-t re-create histograms from TTrees (default: %s)"%(configMgr.readFromTree)
        print "-w re-create workspace from histograms (default: %s)"%(configMgr.executeHistFactory)
        print "-f fit the workspace (default: %s)"%(configMgr.executeHistFactory)
        print "-n <nTOYs> sets number of TOYs (<=0 means to use real data, default: %i)"%configMgr.nTOYs
        print "-s <number> set the random seed for toy generation (default is CPU clock: %i)" % configMgr.toySeed
        print "-c <number> set the calculator type (0 = toys, 2 = asymptotic calculator)" 
        print "-a use Asimov dataset for fitting and plotting (default: %i)" % configMgr.useAsimovSet
        print "-i stays in interactive session after executing the script (default %s)"%runInterpreter
        print "-v verbose level (1: minimal, 2: print histogram names, 3: print XML files, default: %i)"%configMgr.verbose
        print "-l make limit plot of workspace (default %s)" % printLimits
        print "-p run hypothesis test on workspace (default %s)" % doHypoTests
        print "-g <grid points to be processed> - give as comma separated list (default: %s)" % str(sigSamples)
        print "-x fix cross signal section parameter and run nominal, +- 1 sigma"
        print "\nAlso see the README file.\n"
        print "Command examples:"
        print "HistFitter.py -i python/MySusyFitterConfig.py           #only runs initialization in interactive mode (try e.g.: configMgr.<tab>)"
        print "HistFitter.py -t -w -f python/MySusyFitterConfig.py     #runs all steps (TTree->Histos->Workspace->Fit) in batch mode"
        print "HistFitter.py -f -i python/MySusyFitterConfig.py        #only fit and plot, using existing workspace, in interactive session"
        print "\nNote: examples of input TTrees can be found in /afs/cern.ch/atlas/groups/susy/1lepton/samples/"
        sys.exit(0)        
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "twfin:c:s:v:alpg:x")
    except:
        usage()

    for opt,arg in opts:
        if opt == '-t':
            configMgr.readFromTree=True
        elif opt == '-w':
            configMgr.executeHistFactory=True
        elif opt == '-f':
            runFit=True
        elif opt == '-n': 
            configMgr.nTOYs = int(arg)
        elif opt == '-c': 
            configMgr.calculatorType = int(arg)       
        elif opt == '-i':
            runInterpreter = True
        elif opt == '-v':
            configMgr.setVerbose( int(arg) )
        elif opt == '-l':
            printLimits = True
        elif opt == '-p':
            doHypoTests = True
        elif opt == '-s':
            configMgr.toySeedSet = True
            configMgr.toySeed = int(arg)
            RooRandom.randomGenerator().SetSeed(int(arg))
        elif opt == '-a':
            configMgr.useAsimovSet = True
        elif opt == '-g':
            sigSamples = arg.split(',')
        elif opt == '-x':
            fixSigXSec = True

        pass
    gROOT.SetBatch(not runInterpreter)


    if configMgr.calculatorType == 2:
        configMgr.nTOYs = -1

    
        
    
    print "------------------------ Now running hypo test :"
    print "calculatorType : ", configMgr.calculatorType
    print "nToys : ", configMgr.nTOYs
    print "fixSigXSec : ",fixSigXSec
    
    ## outdir
    #outdir = 'test/'
    #outdir = '/afs/cern.ch/atlas/project/cern/susy/users/jlorenz/'+sigSamples[0]+'_hypotestresult/'
    



    if doHypoTests:
        if( fixSigXSec ):        
            doHypoTest(fixSigXSec, 0.,sigSamples)
            doHypoTest(fixSigXSec, 1.,sigSamples)
            doHypoTest(fixSigXSec,-1.,sigSamples)
        else:
            doHypoTest(fixSigXSec, 0.,sigSamples)



    if printLimits:
        outfileName="results/"+sigSamples[0]+"_upperlimit.root"
        outfile = TFile.Open("results/"+sigSamples[0]+"_upperlimit.root","UPDATE");
        if not outfile:
           print "ERROR TFile <"+ outfileName+"> could not be opened"
           #return

        #inFile = "results/MyOneLeptonKtScaleFitR17_Sig_"+sigSamples[0]+"_combined_NormalMeasurement_model.root"
#        inFile = TFile.Open("results/MyOneLeptonKtScaleFitR17_Sig_"+sigSamples[0]+"_combined_NormalMeasurement_model.root")
##        inFile = TFile.Open("results/Combined_KFactorFit_5Channel_Final_dilepton_"+sigSamples[0]+"_combined_BasicMeasurement_model.root")
#        inFile = TFile.Open("results/Combined_KFactorFit_5Channel_Sig_"+sigSamples[0]+"_combined_BasicMeasurement_model.root")
        inFileName = commands.getstatusoutput("ls results/*"+sigSamples[0]+"_combined_BasicMeasurement_model.root")[1]
        inFile = TFile.Open(inFileName)
        if not inFile:
           print "ERROR TFile could not be opened"
           outfile.Close()
          #return

        w = inFile.Get("combined")

        #Util.ReadWorkspace(inFile,"combined")
        #w=gDirectory.Get("w")
        if not w:
           print "workspace 'combined' does not exist in file"
           #return

        Util.SetInterpolationCode(w,4)

        # reset all nominal values
        Util.resetAllValues(w)
        Util.resetAllErrors(w)
        Util.resetAllNominalValues(w)


        w.var("alpha_SigXSec").setVal(0.)
        w.var("alpha_SigXSec").setConstant(True)

        #Util.SetInterpolationCode(w,4)
  
        print "Processing analysis "+sigSamples[0]

        #if 'onestepCC' in sigSamples[0] and int(sigSamples[0].split("_")[3])>900:
        #    w.var("mu_SIG").setMax(50000.)
        #    print "Gluino mass above 900 - extending mu_SIG range \n"


        ## first asumptotic limit, to get a quick but reliable estimate for the upper limit
        ## dynamic evaluation of ranges
        testStatType=3
        calcType=2 #asympt
        nToys=1000
        nPoints=20 #mu sampling
        hypo = RooStats.DoHypoTestInversion(w,1,2,testStatType,True,20,0,-1)

        # then reevaluate with proper settings

        if ( hypo!=0 ):
            hypo.ExclusionCleanup()
    
            i=0 
            while (i<5):
                if min_CLs(hypo)>0.05: 
                    print "Starting rescan iteration: "+str(i)           
                    hypo = RedoScan(w,testStatType,hypo)
                    if ( hypo!=0 ):
                        hypo.ExclusionCleanup()
                else:
                    break
                i+=1    


        if ( hypo!=0 ):
            eul2 = 1.10 * hypo.GetExpectedUpperLimit(2)
            del hypo
            hypo=0
            hypo = RooStats.DoHypoTestInversion(w,nToys,calcType,testStatType,True,nPoints,0,eul2)
            nPointsRemoved = hypo.ExclusionCleanup();
            print "ExclusionCleanup() removed "+str(nPointsRemoved)+" scan point(s) for hypo test inversion: "+hypo.GetName()


        ##store ul as nice plot ..
        if ( hypo!=0 ):
            RooStats.AnalyzeHypoTestInverterResult( hypo,calcType,testStatType,True,nPoints, sigSamples[0], "_"+sigSamples[0]+".eps")
                  

        ##save complete hypotestinverterresult to file
        if(hypo!=0):
            outfile.cd()
            if hypo.ArraySize()>0 and (min_CLs(hypo)>0.05 or max_CLs(hypo)<0.05):
                print "ERROR Final CLs value not below threshold of 0.05 or initial CLs value not above threshold of 0.05 - upper limit scan most likely failed."
                print "ERROR Will store result only for debugging purposes - do not use it in contour plots!"
                hypName="debug_"+sigSamples[0]
            elif hypo.ArraySize()==0:
                print "ERROR All fits seem to have failed - cannot compute upper limit!"
                hypName="debug_"+sigSamples[0]
            else:
                hypName="hypo_"+sigSamples[0]
            hypo.SetName(hypName)
            print ">>> Now storing HypoTestInverterResult <" +hypName+ ">"
            hypo.Write()
                            

        if (hypo!=0):
            del hypo

        inFile.Close()
            
        outfile.Close()

        pass



    
    if runInterpreter:
        from code import InteractiveConsole
        from ROOT import Util
        cons = InteractiveConsole(locals())
        cons.interact("Continuing interactive session... press Ctrl+d to exit")
        pass

    print "Leaving HypoTest... Bye!"

#!/usr/bin/env python

import sys
import os, os.path
import shutil

from ROOT import gROOT,gSystem,gDirectory,RooAbsData,RooRandom,RooWorkspace,TFile,RooFitResult
## batch mode
sys.argv.insert(1, '-b')
gROOT.Reset()
gROOT.SetBatch(True)
del sys.argv[1]
gSystem.Load("libSusyFitter.so")
gROOT.Reset()


if __name__ == "__main__":
    from configManager import configMgr
    from prepareHistos import TreePrepare,HistoPrepare
    configMgr.readFromTree = False
    configMgr.executeHistFactory=False
    runInterpreter = False
    runFit = False
    printLimits = False
    doHypoTests = False
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
        print "-a use Asimov dataset for fitting and plotting (default: %i)" % configMgr.useAsimovSet
        print "-i stays in interactive session after executing the script (default %s)"%runInterpreter
        print "-v verbose level (1: minimal, 2: print histogram names, 3: print XML files, default: %i)"%configMgr.verbose
        print "-l make limit plot of workspace (default %s)" % printLimits
        print "-p run hypothesis test on workspace (default %s)" % doHypoTests
        print "-g <grid points to be processed> - give as comma separated list (default: %s)" % str(sigSamples)
        print "\nAlso see the README file.\n"
        print "Command examples:"
        print "HistFitter.py -i python/MySusyFitterConfig.py           #only runs initialization in interactive mode (try e.g.: configMgr.<tab>)"
        print "HistFitter.py -t -w -f python/MySusyFitterConfig.py     #runs all steps (TTree->Histos->Workspace->Fit) in batch mode"
        print "HistFitter.py -f -i python/MySusyFitterConfig.py        #only fit and plot, using existing workspace, in interactive session"
        print "\nNote: examples of input TTrees can be found in /afs/cern.ch/atlas/groups/susy/1lepton/samples/"
        sys.exit(0)        
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "twfin:s:v:alpg:")
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
        pass
    gROOT.SetBatch(not runInterpreter)
    
    print configMgr.nTOYs
    
    ## outdir
    #outdir = 'test/'
    #outdir = '/afs/cern.ch/atlas/project/cern/susy/users/jlorenz/'+sigSamples[0]+'_hypotestresult/'
    

    if doHypoTests:
        outfileName="results/MyOneLeptonKtScaleFitR17_Output_hypotest.root"
        outfile = TFile.Open("results/MyOneLeptonKtScaleFitR17_Output_hypotest.root","UPDATE");
        if not outfile:
           print "ERROR TFile <"+ outfileName+"> could not be opened"
	   #return

        #inFile = "results/MyOneLeptonKtScaleFitR17_Sig_"+sigSamples[0]+"_combined_NormalMeasurement_model.root"
        inFile = TFile.Open("results/MyOneLeptonKtScaleFitR17_Sig_"+sigSamples[0]+"_combined_NormalMeasurement_model.root")
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
  

  
        #Do first fit and save fit result in order to control fit quality
  
        fitresult = Util.doFreeFit( w , 0, False, True )
  
        if (fitresult):
           outfile.cd()
           hypName="fitTo_"+sigSamples[0]
           fitresult.SetName(hypName);
           fitresult.Print()
           fitresult.Write()
           print ">>> Now storing RooFitResult <"+hypName+">"
   
        hypo = RooStats.DoHypoTestInversion(w,1000,0,3)
  
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


    
    if runInterpreter:
        from code import InteractiveConsole
        from ROOT import Util
        cons = InteractiveConsole(locals())
        cons.interact("Continuing interactive session... press Ctrl+d to exit")
        pass

    print "Leaving HypoTest... Bye!"

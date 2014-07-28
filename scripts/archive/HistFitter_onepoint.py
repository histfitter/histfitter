#!/usr/bin/env python

import sys
import os, os.path
import shutil

from ROOT import gROOT,gSystem,gDirectory,RooAbsData,RooRandom,RooWorkspace 
## batch mode
sys.argv.insert(1, '-b')
gROOT.Reset()
gROOT.SetBatch(True)
del sys.argv[1]
gSystem.Load("libSusyFitter.so")
gROOT.Reset()

def GenerateFitAndPlot(tl):
    from ROOT import Util
    from ROOT import RooExpandedFitResult
    print "\n***GenerateFitAndPlot for TopLevelXML %s***\n"%tl.name

    w = Util.GetWorkspaceFromFile(tl.wsFileName,"combined")
    Util.SaveInitialSnapshot(w)
    #   Util.ReadWorkspace(w, tl.wsFileName,"combined")

    plotChannels = ""
    for reg in tl.validationChannels:
        if len(plotChannels)>0:
            plotChannels+=","
            pass
        plotChannels+=reg
    plotChannels = "ALL"

    fitChannels = ""
    for reg in tl.bkgConstrainChannels:
        if len(fitChannels)>0:
            fitChannels+=","
            pass
        fitChannels+=reg
        pass

    fitChannelsCR = fitChannels
    for reg in tl.signalChannels:
        if len(fitChannels)>0:
            fitChannels+=","
            pass
        fitChannels+=reg
    #fitChannels = "ALL"

    lumiConst = not tl.signalSample

    # fit toy MC if specified. When left None, data is fit by default
    toyMC = None
    if configMgr.toySeedSet and not configMgr.useAsimovSet:    # generate a toy dataset
        print "INFO : generating toy MC set for fitting and plotting. Seed = %i" % configMgr.toySeed
        RooRandom.randomGenerator().SetSeed( configMgr.toySeed )
        toyMC = Util.GetToyMC() # this generates one toy dataset
        pass
    elif configMgr.useAsimovSet and not configMgr.toySeedSet:  # 
        print "INFO : using Asimov set for fitting and plotting."
        toyMC = Util.GetAsimovSet(w) # this returns the asimov set
        pass
    else:
        print "INFO : using data for fitting and plotting."

    ## MB : turn on all JES bins. Some are turned off by HistFactory by default
    if True:
        if w.var("gamma_J3_bin_0")!=None: w.var("gamma_J3_bin_0").setConstant(False)
        if w.var("gamma_J3_bin_1")!=None: w.var("gamma_J3_bin_1").setConstant(False)
        if w.var("gamma_J3_bin_2")!=None: w.var("gamma_J3_bin_2").setConstant(False)
        if w.var("gamma_J3_bin_3")!=None: w.var("gamma_J3_bin_3").setConstant(False)
        if w.var("gamma_J3_bin_4")!=None: w.var("gamma_J3_bin_4").setConstant(False)
        if w.var("gamma_J3_bin_5")!=None: w.var("gamma_J3_bin_5").setConstant(False)
        #if w.var("gamma_J4_bin_0")!=None: w.var("gamma_J4_bin_0").setConstant(False)
        #if w.var("gamma_J4_bin_1")!=None: w.var("gamma_J4_bin_1").setConstant(False)
        if w.var("gamma_J4_bin_2")!=None: w.var("gamma_J4_bin_2").setConstant(False)
        if w.var("gamma_J4_bin_3")!=None: w.var("gamma_J4_bin_3").setConstant(False)
        if w.var("gamma_J4_bin_4")!=None: w.var("gamma_J4_bin_4").setConstant(False)
        if w.var("gamma_J4_bin_5")!=None: w.var("gamma_J4_bin_5").setConstant(False)
        if w.var("gamma_JC_bin_0")!=None: w.var("gamma_JC_bin_0").setConstant(False)
        if w.var("gamma_JC_bin_1")!=None: w.var("gamma_JC_bin_1").setConstant(False)
        if w.var("gamma_JC_bin_2")!=None: w.var("gamma_JC_bin_2").setConstant(False)
        if w.var("gamma_JC_bin_3")!=None: w.var("gamma_JC_bin_3").setConstant(False)
        if w.var("gamma_JC_bin_4")!=None: w.var("gamma_JC_bin_4").setConstant(False)
        if w.var("gamma_JC_bin_5")!=None: w.var("gamma_JC_bin_5").setConstant(False)
        if w.var("gamma_JC_bin_6")!=None: w.var("gamma_JC_bin_6").setConstant(False)
        # Soft lepton
    #    if w.var("gamma_JSS_bin_0")!=None: w.var("gamma_JSS_bin_0").setConstant(False)

    # set Errors of all parameters to 'natural' values before plotting/fitting

    Util.resetAllErrors(w)
    mu_Top = w.var("mu_Top")
    print "mu_Top: "
    print mu_Top
    if mu_Top:
        mu_Top.setError(0.001)
    else:
        mu_Top = w.var("mu_Top_Np0")
        if mu_Top:
            mu_Top.setError(0.001)
        mu_Top = w.var("mu_Top_Np1")
        if mu_Top:
            mu_Top.setError(0.001)
        mu_Top = w.var("mu_Top_Np2")
        if mu_Top:
            mu_Top.setError(0.001)
        mu_Top = w.var("mu_Top_Np3")
        if mu_Top:
            mu_Top.setError(0.001)
        mu_Top = w.var("mu_Top_Np4")
        if mu_Top:
            mu_Top.setError(0.001)
        mu_Top = w.var("mu_Top_Np5")
        if mu_Top:
            mu_Top.setError(0.001)
    mu_WZ = w.var("mu_WZ")
    mu_WZpT0GeV   = w.var("mu_WZpT0GeV")
    if mu_WZ:
        mu_WZ.setError(0.001)
    elif mu_WZpT0GeV:
        mu_WZpT0GeV = w.var("mu_WZpT0GeV")
        mu_WZpT0GeV.setError(0.001)
        mu_WZpT0GeV = w.var("mu_WZpT50GeV")
        mu_WZpT0GeV.setError(0.001)
        mu_WZpT0GeV = w.var("mu_WZpT100GeV")
        mu_WZpT0GeV.setError(0.001)
        mu_WZpT0GeV = w.var("mu_WZpT150GeV")
        mu_WZpT0GeV.setError(0.001)
        mu_WZpT0GeV = w.var("mu_WZpT200GeV")
        mu_WZpT0GeV.setError(0.001)
        mu_WZpT0GeV = w.var("mu_WZpT250GeV")
        mu_WZpT0GeV.setError(0.001)
    else:
        mu_WZ = w.var("mu_WZ_Np0")
        mu_WZ.setError(0.001)
        mu_WZ = w.var("mu_WZ_Np1")
        mu_WZ.setError(0.001)
        mu_WZ = w.var("mu_WZ_Np2")
        mu_WZ.setError(0.001)
        mu_WZ = w.var("mu_WZ_Np3")
        mu_WZ.setError(0.001)
        mu_WZ = w.var("mu_WZ_Np4")
        mu_WZ.setError(0.001)
        mu_WZ = w.var("mu_WZ_Np5")
        mu_WZ.setError(0.001)
    
    # set the flag for plotting ratio or pull distribution under the plot
    plotRatio = True  # plotRatio = False means that a pull distribution will be drawn

    # get a list of all floating parameters for all regions
    simPdf = w.pdf("simPdf");
    mc  = Util.GetModelConfig(w)
    obsSet = mc.GetObservables()
    floatPars = Util.getFloatParList(simPdf, obsSet)
    # create an RooExpandedFitResult encompassing all the regions/parameters & save it to workspace
    expResultBefore = RooExpandedFitResult(floatPars)
    #    expResultBefore.Print()
    Util.ImportInWorkspace(w,expResultBefore,"RooExpandedFitResult_beforeFit")
    # plot before fit
    #Util.PlotPdfWithComponents(w,tl.name,plotChannels,"beforeFit_ORIGINAL",None,toyMC)
    Util.PlotPdfWithComponents(w,tl.name,plotChannels,"beforeFit",expResultBefore,toyMC,plotRatio)
    #return

    # fit of CRs only
    # resultCR = Util.FitPdf(w,fitChannelsCR,lumiConst,toyMC)
    # load original snapshot
    #    w.loadSnapshot('snapshot_paramsVals_initial')
    # fit of all regions
    result = Util.FitPdf(w,fitChannels,lumiConst,toyMC)
    # create an RooExpandedFitResult encompassing all the regions/parameters with the result & save it to workspace
    expResultAfter = RooExpandedFitResult(result, floatPars)
    Util.ImportInWorkspace(w,expResultAfter,"RooExpandedFitResult_afterFit")
    # plot after fit
    #Util.PlotPdfWithComponents(w,tl.name,plotChannels,"afterFit_ORIGINAL",result,toyMC)
    Util.PlotPdfWithComponents(w,tl.name,plotChannels,"afterFit",expResultAfter,toyMC,plotRatio)
    # plot each component of each region separately with propagated error after fit  (interesting for debugging)
    #    Util.PlotSeparateComponents(tl.name,plotChannels,"afterFit",result,toyMC)
    # plot correlation matrix for result
    #Util.PlotCorrelationMatrix(result)
    # Util.GetCorrelations(result, 0.85)
    #     plotPLL = False
    #     Util.PlotNLL(w, result, plotPLL, "", toyMC)
    
    if toyMC:
        Util.WriteWorkspace(w, tl.wsFileName,toyMC.GetName())
    else:
        Util.WriteWorkspace(w, tl.wsFileName)
            
    try:
        if not result == None:
            result.Print()
            return result
    except:
        pass
    return

def GetLimits(tl,f):
    from ROOT import RooStats,Util
    #w=gDirectory.Get("w")

    print "analysis name: ",tl.name
    print "workspace name: ",tl.wsFileName

    if not ("SU" in tl.name):
        print "Do no hypothesis test for bkg only or discovery fit!\n"
        return

    print "Need to load workspace"
    Util.ReadWorkspace(tl.wsFileName,"combined")
    w=gDirectory.Get("w")
    

    result = RooStats.MakeUpperLimitPlot(tl.name,w,2,3,1000,True,20,True)

    if not result==0:
        result.Print() 
        print result.UpperLimit()
        
    return



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
    def usage():
        print "HistFitter.py [-i] [-t] [-w] [-f] [-l] [-l] [-p] [-n nTOYs] [-s seed] [-g gridPoint] <configuration_file>\n"
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
        print "HistFitter.py -s 666 -f python/MySusyFitterConfig.py    #fit a TOY dataset (from seed=666) and prints RooFitResult"
        print "\nNote: examples of input TTrees can be found in /afs/cern.ch/atlas/groups/susy/1lepton/samples/"
        sys.exit(0)        
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "twfin:s:v:alpg:")
        configFile = str(args[0])
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
        elif opt == '-a':
            configMgr.useAsimovSet = True
        elif opt == '-g':
            sigSamples = arg.split(',')    
        pass
    gROOT.SetBatch(not runInterpreter)
    

    #mandatory user-defined configuration
    execfile(configFile)

    #standard execution from now on. 
    configMgr.initialize()
        
    #runs Trees->histos and/or histos->workspace according to specifications
    if configMgr.readFromTree or configMgr.executeHistFactory:
        configMgr.executeAll()

    if runFit:
        for i in range(0,len(configMgr.topLvls)-1):
	#if len(configMgr.topLvls)>1:
            r=GenerateFitAndPlot(configMgr.topLvls[i])
            #for idx in range(len(configMgr.topLvls)):
            #    r=GenerateFitAndPlot(configMgr.topLvls[idx]) #1])
            pass
        #configMgr.cppMgr.fitAll()
        print "\nr0=GenerateFitAndPlot(configMgr.topLvls[0])"
        print "r1=GenerateFitAndPlot(configMgr.topLvls[1])"
        print "r2=GenerateFitAndPlot(configMgr.topLvls[2])"
        pass
    
    if printLimits:
        configMgr.cppMgr.doUpperLimitAll()
        #for tl in configMgr.topLvls:
        #    GetLimits(tl,f)
        #    pass
        
        pass

    if doHypoTests:
        configMgr.cppMgr.doHypoTestAll()
        pass

    if configMgr.nTOYs>0 and doHypoTests==False and printLimits==False and runFit==False:
        RooRandom.randomGenerator().SetSeed( configMgr.toySeed )
        configMgr.cppMgr.runToysAll()
        pass
        
    if runInterpreter:
        from code import InteractiveConsole
        from ROOT import Util
        cons = InteractiveConsole(locals())
        cons.interact("Continuing interactive session... press Ctrl+d to exit")
        pass

    print "Leaving HistFitter... Bye!"

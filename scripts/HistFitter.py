#!/usr/bin/env python
from ROOT import gROOT,gSystem,gDirectory,RooAbsData,RooRandom,RooWorkspace
gSystem.Load("libSusyFitter.so")
gROOT.Reset()

def GenerateFitAndPlot(tl):
    from configManager import configMgr

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

    # set Errors of all parameters to 'natural' values before plotting/fitting
    Util.resetAllErrors(w)

    # normFactors (such as mu_Top, mu_WZ, etc) need to have their errors set to a small number for the before the fit plots
    normList =  configMgr.normList
    for norm in normList:
        if norm in tl.measurements[0].paramSettingDict.keys():
            if tl.measurements[0].paramSettingDict[norm][0]:
                continue
        normfac = w.var(norm)
        if normfac:
            normfac.setError(0.001)
            print "Uncertainty on parameter: ", norm, " set to 0.001"
            
            
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
    Util.PlotCorrelationMatrix(result)
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


def GetLimits():
    from ROOT import RooStats,Util
    w=gDirectory.Get("w")
    #RooStats.DoHypoTestInversion(w,"ModelConfig" ,"","obsData",2,3)
    r = RooStats.DoHypoTest(w,"ModelConfig" ,"","obsData",2,3)
    print "\n Significance: "
    print r.Significance()
    print "\n p-value for null asumption: "
    print r.NullPValue()
    print " +- "
    print r.NullPValueError()
    print "\n"



if __name__ == "__main__":
    from configManager import configMgr
    from prepareHistos import TreePrepare,HistoPrepare
    configMgr.readFromTree = False
    configMgr.executeHistFactory=False
    runInterpreter = False
    runFit = False
    printLimits = False
    doHypoTests = False
 
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
        print "-g <grid points to be processed> - give as comma separated list"
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
        if len(configMgr.topLvls)>0:
            r=GenerateFitAndPlot(configMgr.topLvls[0])
            #for idx in range(len(configMgr.topLvls)):
            #    r=GenerateFitAndPlot(configMgr.topLvls[idx]) #1])
            pass
        #configMgr.cppMgr.fitAll()
        print "\nr0=GenerateFitAndPlot(configMgr.topLvls[0])"
        print "r1=GenerateFitAndPlot(configMgr.topLvls[1])"
        print "r2=GenerateFitAndPlot(configMgr.topLvls[2])"
        pass
        
    if printLimits:
        for tl in configMgr.topLvls:
            if len(tl.validationChannels)>0:
                raise(Exception,"Validation regions should be turned off for setting an upper limit!")
            pass
        configMgr.cppMgr.doUpperLimitAll()
        #GetLimits()
        pass

    if doHypoTests:
        for tl in configMgr.topLvls:
            if len(tl.validationChannels)>0:
                raise(Exception,"Validation regions should be turned off for doing hypothesis test!")
            pass
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

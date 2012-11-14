#!/usr/bin/env python
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from ROOT import gROOT,gSystem,gDirectory,RooAbsData,RooRandom,RooWorkspace
gSystem.Load("libSusyFitter.so")
from ROOT import ConfigMgr
gROOT.Reset()
import sys

from logger import Logger
log = Logger('HistFitter')

def enum(typename, field_names):
    "Create a new enumeration type"

    if isinstance(field_names, str):
        field_names = field_names.replace(',', ' ').split()
    d = dict((reversed(nv) for nv in enumerate(field_names)), __slots__ = ())
    return type(typename, (object,), d)()


def GenerateFitAndPlotCPP(fc, drawBeforeFit, drawAfterFit, drawCorrelationMatrix, drawSeparateComponents, drawLogLikelihood):
    from ROOT import Util
    
    log.debug("GenerateFitAndPlotCPP: drawBeforeFit %s " % drawBeforeFit) 
    log.debug("GenerateFitAndPlotCPP: drawAfterFit %s " % drawAfterFit) 
    log.debug("GenerateFitAndPlotCPP: drawCorrelationMatrix %s " % drawCorrelationMatrix) 
    log.debug("GenerateFitAndPlotCPP: drawSeparateComponents %s " % drawSeparateComponents)
    log.debug("GenerateFitAndPlotCPP: drawLogLikelihood %s " % drawLogLikelihood)

    #    from configManager import configMgr
    Util.GenerateFitAndPlot(fc.name, drawBeforeFit, drawAfterFit, drawCorrelationMatrix, drawSeparateComponents, drawLogLikelihood)

def GenerateFitAndPlot(fc, drawBeforeAfterFit):
    from configManager import configMgr

    from ROOT import Util
    from ROOT import RooExpandedFitResult
    log.info("\n***GenerateFitAndPlot for TopLevelXML %s***\n" % fc.name)

    w = Util.GetWorkspaceFromFile(fc.wsFileName, "combined")
    Util.SaveInitialSnapshot(w)
    #   Util.ReadWorkspace(w, fc.wsFileName,"combined")

    plotChannels = ""
    for reg in fc.validationChannels:
        if len(plotChannels) > 0:
            plotChannels += ","
            pass
        plotChannels += reg
    plotChannels = "ALL"

    fitChannels = ""
    for reg in fc.bkgConstrainChannels:
        if len(fitChannels) > 0:
            fitChannels += ","
            pass
        fitChannels += reg
        pass

    fitChannelsCR = fitChannels
    for reg in fc.signalChannels:
        if len(fitChannels) > 0:
            fitChannels += ","
            pass
        fitChannels += reg
    #fitChannels = "ALL"

    #hack to be fixed at HistFactory level (check again with ROOT 5.34)
    lumiConst = True
    if fc.signalSample and not fc.hasDiscovery:
        lumiConst = False

    # fit toy MC if specified. When left None, data is fit by default
    toyMC = None
    if configMgr.toySeedSet and not configMgr.useAsimovSet:
        # generate a toy dataset
        log.info("generating toy MC set for fitting and plotting." \
              " Seed = %i" % configMgr.toySeed)
        toyMC = Util.GetToyMC()   # this generates one toy dataset
        pass
    elif configMgr.useAsimovSet and not configMgr.toySeedSet:
        log.info("using Asimov set for fitting and plotting.")
        toyMC = Util.GetAsimovSet(w)  # this returns the asimov set
        pass
    else:
        log.info("using data for fitting and plotting.")

    # set Errors of all parameters to 'natural' values before plotting/fitting
    Util.resetAllErrors(w)

    # AK: now done in Util.resetAllErrors()
    #     # normFactors (such as mu_Top, mu_WZ, etc) need to have their errors set
    #     # to a small number for the before the fit plots
    #     normList = configMgr.normList
    #     for norm in normList:
    #         if norm in fc.measurements[0].paramSettingDict.keys():
    #             if fc.measurements[0].paramSettingDict[norm][0]:
    #                 continue
    #         normfac = w.var(norm)
    #         if normfac:
    #             normfac.setError(0.001)
    #             print "Uncertainty on parameter: ", norm, " set to 0.001"

    # set the flag for plotting ratio or pull distribution under the plot
    # plotRatio = False means that a pull distribution will be drawn
    plotRatio = True

    # get a list of all floating parameters for all regions
    simPdf = w.pdf("simPdf")
    mc = Util.GetModelConfig(w)
    obsSet = mc.GetObservables()
    floatPars = Util.getFloatParList(simPdf, obsSet)

    # create an RooExpandedFitResult encompassing all the
    # regions/parameters & save it to workspace
    expResultBefore = RooExpandedFitResult(floatPars)
    Util.ImportInWorkspace(w, expResultBefore,
                            "RooExpandedFitResult_beforeFit")
    
    # plot before fit
    if drawBeforeAfterFit:
        Util.PlotPdfWithComponents(w, fc.name, plotChannels, "beforeFit",
                                   expResultBefore, toyMC, plotRatio)

    # fit of all regions
    result = Util.FitPdf(w, fitChannels, lumiConst, toyMC)

    # create an RooExpandedFitResult encompassing all the regions/parameters
    # with the result & save it to workspace
    expResultAfter = RooExpandedFitResult(result, floatPars)
    Util.ImportInWorkspace(w, expResultAfter, "RooExpandedFitResult_afterFit")

    # plot after fit
    if drawBeforeAfterFit:
        Util.PlotPdfWithComponents(w, fc.name, plotChannels, "afterFit",
                                   expResultAfter, toyMC, plotRatio)
        #plot each component of each region separately with propagated
        #error after fit  (interesting for debugging)
        #Util.PlotSeparateComponents(fc.name, plotChannels,
        #                             "afterFit", result,toyMC)

        # plot correlation matrix for result
        Util.PlotCorrelationMatrix(result)
        # plot likelihood
        #    plotPLL = False
        #         Util.PlotNLL(w, expResultAfter, plotPLL, "", toyMC)

    if toyMC:
        Util.WriteWorkspace(w, fc.wsFileName, toyMC.GetName())
    else:
        Util.WriteWorkspace(w, fc.wsFileName)

    try:
        if not result == None:
            result.Print()
            return result
    except:
        pass
    return



if __name__ == "__main__":
    from configManager import configMgr
    from prepareHistos import TreePrepare, HistoPrepare

    configMgr.readFromTree = False
    configMgr.executeHistFactory = False
    runInterpreter = False
    runFit = False
    printLimits = False
    doHypoTests = False
    doUL = True           # default is exclusion. goes toegether with doHypoTests
    drawBeforeFit              = False
    drawAfterFit              = False
    drawCorrelationMatrix         = False
    drawSeparateComponents = False
    drawLogLikelihood               = False
    pickedSRs = []
    runToys = False

    FitType = enum('FitType','Discovery , Exclusion , Background')
    myFitType=FitType.Background
    doValidation = False
    
    print "\n * * * Welcome to HistFitter * * *\n"

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("configFile", help="configuration file to execute")
    parser.add_argument("-L", "--log-level", help="set log level", choices=["VERBOSE", "DEBUG", "INFO", "WARNING", "ERROR", "FATAL", "ALWAYS"])
    parser.add_argument("-F", "--fit-type", help="type of fit to run", choices=["bkg", "disc", "excl"])
    parser.add_argument("-t", "--create-histograms", help="re-create histograms from TTrees", action="store_true", default=configMgr.readFromTree)
    parser.add_argument("-w", "--create-workspace", help="re-create workspace from histograms", action="store_true", default=configMgr.executeHistFactory)
    parser.add_argument("-x", "--use-XML", help="write XML files by hand and call hist2workspace on them, instead of directly writing workspaces", action="store_true", default=configMgr.writeXML)
    parser.add_argument("-f", "--fit", help="fit the workspace", action="store_true", default=configMgr.executeHistFactory)
    parser.add_argument("-n", "--num_toys", type=int, help="set the number of toys, <=0 means to use real data", default=configMgr.nTOYs)
    parser.add_argument("-s", "--seed", type=int, help="set the random seed for toy generation", default=configMgr.toySeed)
    parser.add_argument("-a", "--use-asimov", help="use Asimov dataset for fitting and plotting", action="store_true", default=configMgr.useAsimovSet)
    parser.add_argument("-i", "--interactive", help="remain in interactive mode after running", action="store_true", default=runInterpreter)
    parser.add_argument("-l", "--limit-plot", help="make limit plot of workspace", action="store_true", default=printLimits)
    parser.add_argument("-p", "--hypotest", help="run exclusion hypothesis test", action="store_true", default=doHypoTests)
    parser.add_argument("-z", "--discovery-hypotest", help="run discovery hypothesis test", action="store_true", default=not doUL)
    parser.add_argument("-g", "--grid_points", help="grid points to process (comma-seperated)")
    parser.add_argument("-r", "--regions", help="signal regions to process (comma-seperated)", default="all")
    
    # note that we cannot make -d and -D the same due to http://bugs.python.org/issue9338
    # if we do so, specifying -d without argument would, if -d is the last option, eat the configFile as draw option
    # i.e. "HistFitter -f -d configFile.py" would fail, "HistFitter -d -f configFile.py" would work 
    # (a workaround using "-f -d -- configFile.py" exists but it would confuse users)
    # --GJ 14/11/2012 
    parser.add_argument("-d", action="store_true", help="draw before/after plots")
    parser.add_argument("-D", "--draw", choices=["allPlots", "before","after", "corrMatrix", "sepComponents", "likelihood"], help="specify plots to draw")
    
    parser.add_argument("-b", "--background", help="when doing hypotest, set background levels to values, form of bkgParName,value")
    parser.add_argument("-0", "--no-empty", help="do not draw empty bins when drawing", action="store_true")
    parser.add_argument("-T", "--run-toys", help="run toys (default with mu)", action="store_true")
    parser.add_argument("-V", "--validation", help="include validation regions", action="store_true")

    args = parser.parse_args()
   
    if args.fit_type == "bkg":
        myFitType = FitType.Background
    elif args.fit_type == "excl":
        myFitType = FitType.Exclusion
    elif args.fit_type == "disc":
        myFitType = FitType.Discovery

    if args.validation:
        doValidation = True

    if args.create_histograms:
        configMgr.readFromTree = True

    if args.create_workspace:
        configMgr.executeHistFactory = True

    if args.use_XML:
        configMgr.writeXML = True

    if args.fit:
        runFit = True

    configMgr.nTOYs = args.num_toys

    if args.interactive:
        runInterpreter = True

    if args.log_level:
        log.setLevel(args.log_level, True) #do not add a default to args.log_level or we will always lock it

    if args.limit_plot:
        printLimits = True

    if args.hypotest:
        doHypoTests = True

    if args.discovery_hypotest:
        doHypoTests = True
        doUL = False

    if args.d:
        drawBeforeFit = True
        drawAfterFit = True
    
    if args.draw:
        drawArgs = args.draw
        if len(drawArgs) == 1 and drawArgs[0] == "allPlots":
            drawBeforeFit = True
            drawAfterFit = True
            drawCorrelationMatrix = True
            drawSeparateComponents = True
            drawLogLikelihood = True
        elif len(drawArgs)>0:
            for drawArg in drawArgs:
                if drawArg == "before":
                    drawBeforeFit = True
                elif drawArg == "after":
                    drawAfterFit = True
                elif drawArg == "corrMatrix":
                    drawCorrelationMatrix = True
                elif drawArg == "sepComponents":
                    drawSeparateComponents = True
                elif drawArg == "likelihood":
                    drawLogLikelihood = True
                else:
                    log.fatal("Wrong draw argument: %s\n  Possible draw arguments are 'allPlots' or comma separated 'before, after, corrMatrix, sepComponents, likelihood'" % drawArg) #should now be caught by argparse --GJ 7/11/2012

    if args.no_empty:
        configMgr.removeEmptyBins = True

    if args.seed != 0: #0 is default because type is int
        configMgr.toySeedSet = True
        configMgr.toySeed = args.seed

    if args.use_asimov:
        configMgr.useAsimovSet = True

    if args.grid_points and args.grid_points != "":
        sigSamples = args.grid_points.split(",")

    if args.regions and args.regions != "" and args.regions != "all":
        pickedSRs = args.regions.split(",")
    else:
        pickedSRs = [] #MB: used by 0-lepton fit

    if len(pickedSRs)>0: log.info("Selected signal regions: %s" % pickedSRs) 

    if args.run_toys:
        runToys = True

    if args.background:
        bkgArgs = args.background.split(',')
        if len(bkgArgs) == 2:
            configMgr.SetBkgParName(bkgArgs[0])
            configMgr.SetBkgCorrVal(float(bkgArgs[1]))
            configMgr.SetBkgChlName("")
        elif len(bkgArgs) >= 3 and len(bkgArgs) % 3 == 0:
            for iChan in xrange(len(bkgArgs) / 3):
                iCx = iChan * 3
                configMgr.AddBkgChlName(bkgArgs[iCx])
                configMgr.AddBkgParName(bkgArgs[iCx+1])
                configMgr.AddBkgCorrVal(float(bkgArgs[iCx+2]))
                continue
        
    gROOT.SetBatch(not runInterpreter)

    #mandatory user-defined configuration
    execfile(args.configFile)

    #standard execution from now on.
    configMgr.initialize()

    # initialize: set the toy seed
    RooRandom.randomGenerator().SetSeed(configMgr.toySeed)

    #runs Trees->histos and/or histos->workspace according to specifications
    if configMgr.readFromTree or configMgr.executeHistFactory:
        configMgr.executeAll()

    if runFit:
        if len(configMgr.fitConfigs) > 0:
      #      r = GenerateFitAndPlot(configMgr.fitConfigs[0], drawBeforeAfterFit)
            #r=GenerateFitAndPlot(configMgr.fitConfigs[1],drawBeforeAfterFit)
            #r=GenerateFitAndPlot(configMgr.fitConfigs[2],drawBeforeAfterFit)
            #for idx in range(len(configMgr.fitConfigs)):
            #    r=GenerateFitAndPlot(configMgr.fitConfigs[idx],drawBeforeAfterFit)
            r = GenerateFitAndPlotCPP(configMgr.fitConfigs[0], drawBeforeFit, drawAfterFit, drawCorrelationMatrix, drawSeparateComponents, drawLogLikelihood)
            pass
        #configMgr.cppMgr.fitAll()
        log.info("\nr0=GenerateFitAndPlot(configMgr.fitConfigs[0],False)")
        log.info("r1=GenerateFitAndPlot(configMgr.fitConfigs[1],False)")
        log.info("r2=GenerateFitAndPlot(configMgr.fitConfigs[2],False)")
        log.info(" OR \nGenerateFitAndPlotCPP(configMgr.fitConfigs[0], drawBeforeAfterFit, drawCorrelationMatrix, drawSeparateComponents, drawLogLikelihood)")
        log.info("   where drawBeforeAfterFit, drawCorrelationMatrix, drawSeparateComponents, drawLogLikelihood are booleans")

        pass

    if printLimits:
        for fc in configMgr.fitConfigs:
            if len(fc.validationChannels) > 0:
                raise(Exception, "Validation regions should be turned off for setting an upper limit!")
            pass
        configMgr.cppMgr.doUpperLimitAll()
        pass

    if doHypoTests:
        for fc in configMgr.fitConfigs:
            if len(fc.validationChannels) > 0:
                raise(Exception,"Validation regions should be turned off for doing hypothesis test!")
            pass
        configMgr.cppMgr.doHypoTestAll('results/',doUL)
        pass

    if runToys and configMgr.nTOYs > 0 and doHypoTests == False and printLimits == False and runFit == False:
        configMgr.cppMgr.runToysAll()
        pass

    if runInterpreter:
        from code import InteractiveConsole
        from ROOT import Util
        cons = InteractiveConsole(locals())
        cons.interact("Continuing interactive session... press Ctrl+d to exit")
        pass

    log.info("Leaving HistFitter... Bye!")

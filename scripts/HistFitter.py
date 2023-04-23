#!/usr/bin/env python
"""
 * Project : HistFitter - A ROOT-based package for statistical data analysis      *
 * Package : HistFitter                                                           *
 * Script  : HistFitter.py                                                        *
 * Created : November 2012                                                        *
 *                                                                                *
 * Description:                                                                   *
 *              Top-level control script for all commands/run-conditions          *   
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group                                                          *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
"""

import os

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.SetMemoryPolicy( ROOT.kMemoryStrict )

from ROOT import gROOT,gSystem,gDirectory,RooAbsData,RooRandom,RooWorkspace
ROOT.gSystem.Load(f"{os.getenv('HISTFITTER')}/lib/libSusyFitter.so")
from ROOT import ConfigMgr
#gROOT.Reset()

import argparse
import sys

from logger import Logger
log = Logger('HistFitter')

def GenerateFitAndPlotCPP(fc, anaName, drawBeforeFit, drawAfterFit, drawStackPlots, storeSingleFiles, storeMergedFile, drawCorrelationMatrix, drawSeparateComponents, drawLogLikelihood, minos, minosPars, doFixParameters, fixedPars, ReduceCorrMatrix, noFit, plotInterpolation):
    """ 
    function call to top-level C++ side function Util.GenerateFitAndPlot()

    @param fc FitConfig name connected to fit and plot details
    @param anaName Analysis name defined in config file, mainly used for output file/dir naming
    @param drawBeforeFit Boolean deciding whether before-fit plots are produced
    @param drawAfterFit Boolean deciding whether after-fit plots are produced
    @param drawStackPlots Boolean deciding whether stacked before/after plots are produced, or just the individual histograms are stored
    @param storeSingleFiles Boolean deciding whether single files will be created for each before/after plot
    @param storeMergedFile Boolean deciding whether a central file will be created for all before/after plots
    @param drawCorrelationMatrix Boolean deciding whether correlation matrix plot is produced
    @param drawSeparateComponents Boolean deciding whether separate component (=sample) plots are produced
    @param drawLogLikelihood Boolean deciding whether log-likelihood plots are produced
    @param minos Boolean deciding whether asymmetric errors are calculated, eg whether MINOS is run
    @param minosPars When minos is called, defining what parameters need asymmetric error calculation
    @param doFixParameters Boolean deciding if some parameters are fixed to a value given or not
    @param fixedPars String of parameter1:value1,parameter2:value2 giving information on which parameter to fix to which value if dofixParameter == True
    @param ReduceCorrMatrix Boolean deciding whether reduced correlation matrix plot is produced
    @param noFit Don't re-run fit but use after-fit workspace
    @param plotInterpolation plot the interpolation scheme
    """
    
    from ROOT import Util
    
    log.debug('GenerateFitAndPlotCPP: anaName %s ' % anaName)
    log.debug("GenerateFitAndPlotCPP: drawBeforeFit %s " % drawBeforeFit) 
    log.debug("GenerateFitAndPlotCPP: drawAfterFit %s " % drawAfterFit)
    log.debug("GenerateFitAndPlotCPP: drawStackPlots %s " % drawStackPlots)
    log.debug("GenerateFitAndPlotCPP: storeSingleFiles %s " % storeSingleFiles)
    log.debug("GenerateFitAndPlotCPP: storeMergedFile %s " % storeMergedFile)
    log.debug("GenerateFitAndPlotCPP: drawCorrelationMatrix %s " % drawCorrelationMatrix) 
    log.debug("GenerateFitAndPlotCPP: drawSeparateComponents %s " % drawSeparateComponents)
    log.debug("GenerateFitAndPlotCPP: drawLogLikelihood %s " % drawLogLikelihood)
    log.debug("GenerateFitAndPlotCPP: minos %s " % minos)
    log.debug("GenerateFitAndPlotCPP: minosPars %s " % minosPars)
    log.debug("GenerateFitAndPlotCPP: doFixParameters %s " % doFixParameters)
    log.debug("GenerateFitAndPlotCPP: fixedPars %s " % fixedPars)
    log.debug("GenerateFitAndPlotCPP: ReduceCorrMatrix %s " % ReduceCorrMatrix)
    log.debug(f"GenerateFitAndPlotCPP: noFit {noFit}")
    log.debug(f"GenerateFitAndPlotCPP: plotInterpolation {plotInterpolation}")
    
    Util.GenerateFitAndPlot(fc.name, anaName, drawBeforeFit, drawAfterFit, drawStackPlots, storeSingleFiles, storeMergedFile, drawCorrelationMatrix,
                            drawSeparateComponents, drawLogLikelihood, minos, minosPars, doFixParameters, fixedPars, ReduceCorrMatrix, noFit, plotInterpolation)

if __name__ == "__main__":
    """
    Main function call starts here ....
    """
    
    from configManager import configMgr
    
    """
    set some default options
    """
    configMgr.readFromTree = False
    configMgr.executeHistFactory = False
    runInterpreter = False
    runFit = False
    printLimits = False
    doHypoTests = False
    doDiscoveryHypoTests = False
    drawBeforeFit = False
    drawAfterFit = False
    drawCorrelationMatrix = False
    drawSeparateComponents = False
    drawLogLikelihood = False
    drawSystematics = False
    drawInterpolation = False
    pickedSRs = []
    runToys = False
    runMinos = False
    minosPars = ""
    doCodeProfiling = False
    doFixParameters = False
    fixedPars = ""
    
    FitType = configMgr.FitType #enum('FitType','Discovery , Exclusion , Background')
    myFitType=FitType.Background
    doValidation = False
    
    print("\n * * * Welcome to HistFitter * * *\n")

    """
    Definition of all options and defaults given as arguments
    """
    mode_helper = { "bkg": "Run background-only fit",
                       "excl": "Run exclusion fit (model-dependent fit)",
                       "model-dep": "Run exclusion fit (model-dependent fit) (alias of excl)",
                       "disc": "Run discovery fit (model-independent fit)",
                       "model-indep": "Run discovery fit (model-indepndent fit) (alias of disc)"}

    parser = argparse.ArgumentParser(description="HistFitter options:")
    parser.add_argument("configFile", nargs="+", help="configuration file to execute")
    parser.add_argument("-L", "--log-level", help="set log level", choices=["VERBOSE", "DEBUG", "INFO", "WARNING", "ERROR", "FATAL", "ALWAYS"])
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="an alias of -L VERBOSE")
    parser.add_argument("-F", "--fit-type", help="type of fit to run: bkg (background-only fit), excl (exclusion fit / model-dependent fit), disc (discovery fit / model-independent fit), model-dep (alias of excl), model-indep (alias of disc)", choices=["bkg", "excl", "disc", "model-dep", "model-indep"]) 
    parser.add_argument("-t", "--create-histograms", help="re-create histograms from TTrees", action="store_true", default=configMgr.readFromTree)
    parser.add_argument("-w", "--create-workspace", help="re-create workspace from histograms", action="store_true", default=configMgr.executeHistFactory)
    parser.add_argument("-x", "--use-XML", help="write XML files by hand and call hist2workspace on them, instead of directly writing workspaces", action="store_true", default=configMgr.writeXML)
    parser.add_argument("-f", "--fit", help="fit the workspace", action="store_true", default=configMgr.executeHistFactory)
    parser.add_argument("--fitname", dest="fitname", help="workspace name for fit (not specified takes 1st available fitConfig)", default="")
    parser.add_argument("-m", "--minos", help="run minos for asymmetric error calculation, optionally give parameter names for which minos should be run, space separated. For all params, use ALL", metavar="PARAM")
    parser.add_argument("-n", "--num_toys", type=int, help="set the number of toys, <=0 means to use real data", default=configMgr.nTOYs)
    parser.add_argument("-s", "--seed", type=int, help="set the random seed for toy generation", default=configMgr.toySeed)
    parser.add_argument("-a", "--use-asimov", help="use Asimov dataset for fitting and plotting", action="store_true", default=configMgr.useAsimovSet)
    parser.add_argument("-i", "--interactive", help="remain in interactive mode after running", action="store_true", default=runInterpreter)
    parser.add_argument("-l", "--limit-plot", help="make limit plot of workspace", action="store_true", default=printLimits)
    parser.add_argument("-p", "--hypotest", help="run exclusion hypothesis test", action="store_true", default=doHypoTests)
    parser.add_argument("-z", "--discovery-hypotest", help="run discovery hypothesis test", action="store_true", default=doDiscoveryHypoTests)
    parser.add_argument("-g", "--grid_points", help="grid points to process (comma-separated)")
    parser.add_argument("-r", "--regions", help="signal regions to process (comma-separated)", default="all")
    parser.add_argument("-R", "--rebin", help="rebin all histograms to proxy x-axis bins [0, 1, 2, ... N] and unfold them post-fit", action="store_true", default=False)

    """
    note that we cannot make -d and -D the same due to http://bugs.python.org/issue9338
    if we do so, specifying -d without argument would, if -d is the last option, eat the configFile as draw option
    i.e. 'HistFitter -f -d configFile.py' would fail, 'HistFitter -d -f configFile.py' would work 
    (a workaround using '-f -d -- configFile.py' exists but it would confuse users)
    --GJ 14/11/2012
    """
    parser.add_argument("-d", action="store_true", help="draw before/after plots")
    parser.add_argument("-D", "--draw", help="specify plots to draw, comma separated; choose from "+str(["allPlots", "before","after", "corrMatrix", "correlationMatrix", "sepComponents", "separateComponents", "likelihood", "systematics", "plotInterpolation"]))
    parser.add_argument("-syst", "--systematics", help="specify the systematics to be considered with '-D systematics' option, comma separated;")
    
    parser.add_argument("-b", "--background", help="when doing hypotest, set background levels to values, form of bkgParName,value")
    parser.add_argument("-0", "--no-empty", help="do not draw empty bins when drawing", action="store_true")
    parser.add_argument("-T", "--run-toys", help="run toys (default with mu)", action="store_true")
    parser.add_argument("-V", "--validation", help="include validation regions", action="store_true")
    parser.add_argument("-c", "--cmd", help="python commands to process (semi-colon-separated)")
    parser.add_argument("-u", "--userArg", help="arbitrary user argument(s)", default="")
    parser.add_argument("-A", "--use-archive-histfile", help="use backup histogram cache file", action="store_true")
    parser.add_argument("-P", "--run-profiling", help="Run a python profiler during main HistFitter execution", action="store_true")
    parser.add_argument("-C", "--constant", help="Set parameters to constant in the fit, Give list of parameters and their values as parameter1:value1,parameter2:value2:...", metavar="PARAM")
    
    HistFitterArgs = parser.parse_args()

    """
    process all the arguments/options
    """
    if not os.path.exists(HistFitterArgs.configFile[0]) and not os.path.isfile(HistFitterArgs.configFile[0]):
        log.fatal(f"Specified input file '{HistFitterArgs.configFile[0]}' does not exist or is not a file")
        sys.exit(-1)

    if HistFitterArgs.fit_type == "bkg":
        myFitType = FitType.Background
        log.info("Will run in background-only fit mode")
    elif HistFitterArgs.fit_type == "excl" or HistFitterArgs.fit_type == "model-dep":
        myFitType = FitType.Exclusion
        log.info("Will run in exclusion (model-dependent) fit mode")
    elif HistFitterArgs.fit_type == "disc" or HistFitterArgs.fit_type == "model-indep":
        myFitType = FitType.Discovery
        log.info("Will run in discovery (model-independent) fit mode")
    
    # Combining -p and -z can give funny results. It's not recommend. We stop the user from doing this and
    # force them to execute in two steps.
    if HistFitterArgs.hypotest and HistFitterArgs.discovery_hypotest:
        log.error("You specified both -p and -z in the options. This can currently lead to unexpected results for the obtained CLs values for the -p option.")
        log.error("Please run these two steps separately - there is no need to regenerate the workspace, so there is no overhead to do so.")
        sys.exit()

    configMgr.myFitType = myFitType
 
    if HistFitterArgs.validation:
        doValidation = True

    if HistFitterArgs.use_archive_histfile:
        configMgr.useHistBackupCacheFile = True

    if HistFitterArgs.run_profiling:
        doCodeProfiling = True

    if HistFitterArgs.create_histograms:
        configMgr.readFromTree = True

    if HistFitterArgs.create_workspace:
        configMgr.executeHistFactory = True

    if HistFitterArgs.use_XML:
        configMgr.writeXML = True

    if HistFitterArgs.fit:
        runFit = True

    configMgr.userArg = HistFitterArgs.userArg
    configMgr.nTOYs = HistFitterArgs.num_toys

    if HistFitterArgs.interactive:
        runInterpreter = True

    if HistFitterArgs.verbose:
        log.setLevel("VERBOSE", True)
    elif HistFitterArgs.log_level:
        log.setLevel(HistFitterArgs.log_level, True) #do not add a default to HistFitterArgs.log_level or we will always lock it

    if HistFitterArgs.limit_plot:
        printLimits = True

    if HistFitterArgs.hypotest:
        configMgr.doHypoTest = True
        doHypoTests = True

    if HistFitterArgs.discovery_hypotest:
        configMgr.doDiscoveryHypoTest = True
        doDiscoveryHypoTests = True

    if HistFitterArgs.d:
        drawBeforeFit = True
        drawAfterFit = True
    
    if HistFitterArgs.draw:
        drawArgs = HistFitterArgs.draw.split(",")
        if len(drawArgs) == 1 and (drawArgs[0] == "allPlots" or drawArgs[0] == "all"):
            drawBeforeFit = True
            drawAfterFit = True
            drawCorrelationMatrix = True
            drawSeparateComponents = True
            drawLogLikelihood = True
            drawSystematics = True
            drawInterpolation = True
        elif len(drawArgs)>0:
            for drawArg in drawArgs:
                if drawArg == "before":
                    drawBeforeFit = True
                elif drawArg == "after":
                    drawAfterFit = True
                elif drawArg == "corrMatrix" or drawArg == "correlationMatrix":
                    drawCorrelationMatrix = True
                elif drawArg == "sepComponents" or drawArg == "separateComponents":
                    drawSeparateComponents = True
                elif drawArg == "likelihood":
                    drawLogLikelihood = True
                elif drawArg == "systematics":
                    drawSystematics = True
                elif drawArg == "plotInterpolation":
                    drawInterpolation = True
                else:
                    log.fatal("Wrong draw argument: '%s'. Possible draw arguments are 'allPlots' or comma separated 'before after corrMatrix correlationMatrix sepComponents separateComponents likelihood'" % drawArg) 

    if drawInterpolation and not os.path.isdir("./interpolation"): 
        os.mkdir("./interpolation")

    if HistFitterArgs.no_empty:
        configMgr.removeEmptyBins = True

    if HistFitterArgs.seed != 0: #0 is default because type is int
        configMgr.toySeedSet = True
        configMgr.toySeed = HistFitterArgs.seed

    if HistFitterArgs.use_asimov:
        configMgr.useAsimovSet = True

    if HistFitterArgs.rebin:
        configMgr.rebin = True

    if HistFitterArgs.grid_points and HistFitterArgs.grid_points != "":
        sigSamples = HistFitterArgs.grid_points.split(",")
        log.info("Grid points specified: %s" % sigSamples)

    if HistFitterArgs.regions and HistFitterArgs.regions != "" and HistFitterArgs.regions != "all":
        pickedSRs = HistFitterArgs.regions.split(",")
    else:
        pickedSRs = [] #MB: used by 0-lepton fit

    if len(pickedSRs) > 0: 
        log.info("Selected signal regions: %s" % pickedSRs) 

    if HistFitterArgs.run_toys:
        runToys = True

    if HistFitterArgs.background:
        bkgArgs = HistFitterArgs.background.split(',')
        if len(bkgArgs) == 2:
            configMgr.SetBkgParName(bkgArgs[0])
            configMgr.SetBkgCorrVal(float(bkgArgs[1]))
            configMgr.SetBkgChlName("")
        elif len(bkgArgs) >= 3 and len(bkgArgs) % 3 == 0:
            for iChan in range(len(bkgArgs) / 3):
                iCx = iChan * 3
                configMgr.AddBkgChlName(bkgArgs[iCx])
                configMgr.AddBkgParName(bkgArgs[iCx+1])
                configMgr.AddBkgCorrVal(float(bkgArgs[iCx+2]))
                continue

    if HistFitterArgs.minos:
        runMinos = True
        
        minosArgs = HistFitterArgs.minos.split(",")
        for idx, arg in enumerate(minosArgs):
            if arg.lower() == "all":
                minosArgs[idx] = "all"

        minosPars = ",".join(minosArgs)
        
    if HistFitterArgs.constant:
        doFixParameters = True
        fixedPars =  HistFitterArgs.constant
        

    if HistFitterArgs.cmd:
        log.info("Python commands executed: %s" % HistFitterArgs.cmd)
        exec(HistFitterArgs.cmd) ## python execute

    gROOT.SetBatch(not runInterpreter)

    """
    mandatory user-defined configuration file
    """
    exec(compile(open(HistFitterArgs.configFile[0], "rb").read(), HistFitterArgs.configFile[0], 'exec')) #[0] since any extra arguments (sys.argv[-1], etc.) are caught here

    """
    standard execution from now on
    """
    configMgr.initialize()
    RooRandom.randomGenerator().SetSeed(configMgr.toySeed)
    ReduceCorrMatrix = configMgr.ReduceCorrMatrix

    """
    runs Trees->histos and/or histos->workspace according to specifications
    """
    if configMgr.readFromTree or configMgr.executeHistFactory:
        if doCodeProfiling:
            import cProfile
            cProfile.run('configMgr.executeAll()')
        else:
            configMgr.executeAll()

    """
    shows systematics
    """
    if drawSystematics:
       from ROOT import Util
       if not os.path.isdir("./plots"): 
          log.info("no directory './plots' found - attempting to create one")
          os.mkdir("./plots")
       for fC in configMgr.fitConfigs:
           for chan in fC.channels:
               for sam in chan.sampleList:
                if not sam.isData:
                  if HistFitterArgs.systematics:
                      Systs = HistFitterArgs.systematics
                  else:
                      log.info("no systematic has been specified.... all the systematics will be considered")
                      print(sam.systDict)
                      Systs = ""
                      for i in list(sam.systDict.keys()): 
                          Systs+=i
                          if 'Norm' in sam.systDict[i].method or 'norm' in sam.systDict[i].method: Systs+="Norm"
                          Systs+=","
                      if Systs!="": Systs=Systs[:-1]
                  if Systs != "": Util.plotUpDown(configMgr.histCacheFile,sam.name,Systs,chan.regionString,chan.variableName)

    """
    runs fitting and plotting, by calling C++ side functions
    """
    if runFit or HistFitterArgs.draw:
        idx = 0
        if len(configMgr.fitConfigs) == 0:
            log.fatal("No fit configurations found!")
        
        runAll = True
        if HistFitterArgs.fitname != "": # user specified a fit name
            fitFound = False
            for (i, config) in enumerate(configMgr.fitConfigs):
                if configMgr.fitConfigs[i].name == HistFitterArgs.fitname:
                    idx = i
                    fitFound = True
                    runAll = False
                    log.info("Found fitConfig with name %s at index %d" % (HistFitterArgs.fitname, idx))
                    break
                    
            if not fitFound:
                log.fatal("Unable to find fitConfig with name %s, bailing out" % HistFitterArgs.fitname)

        noFit = False
        if not runFit: noFit = True

        for i in range(len(configMgr.fitConfigs)):
            if not runAll and i != idx:
                log.debug(f"Skipping fit config {configMgr.fitConfigs[i].name}")
                continue

            log.info("Running on fitConfig %s" % configMgr.fitConfigs[i].name)
            log.info(f"Setting noFit = {noFit}")
            r = GenerateFitAndPlotCPP(configMgr.fitConfigs[i], configMgr.analysisName, drawBeforeFit, drawAfterFit, configMgr.plotStacked, configMgr.storeSinglePlotFiles, configMgr.storeMergedPlotFile, 
                                      drawCorrelationMatrix, drawSeparateComponents, drawLogLikelihood, runMinos, minosPars, doFixParameters, fixedPars, ReduceCorrMatrix, noFit, drawInterpolation)
        
        log.debug(" GenerateFitAndPlotCPP(configMgr.fitConfigs[%d], configMgr.analysisName, drawBeforeFit, drawAfterFit, configMgr.plotStacked, configMgr.storeSinglePlotFiles, configMgr.storeMergedPlotFile, drawCorrelationMatrix, drawSeparateComponents, drawLogLikelihood, runMinos, minosPars, doFixParameters, fixedPars, ReduceCorrMatrix, noFit, drawInterpolation)" % idx)
        log.debug("   where drawBeforeFit, drawAfterFit, drawCorrelationMatrix, drawSeparateComponents, drawLogLikelihood, ReduceCorrMatrix, noFit, drawInterpolation are booleans")
        pass

    """
    calculating and printing upper limits for model-(in)dependent signal fit configurations (aka Exclusion/Discovery fit setup)
    """
    if printLimits:
        for fc in configMgr.fitConfigs:
            if len(fc.validationChannels) > 0:
                raise Exception
            pass
        configMgr.cppMgr.doUpperLimitAll()
        pass

    """
    run exclusion or discovery hypotest
    """
    if doHypoTests or doDiscoveryHypoTests:
        for fc in configMgr.fitConfigs:
            if len(fc.validationChannels) > 0 and not (fc.signalSample is None or 'Bkg' in fc.signalSample):
                raise Exception
            pass
        
        if doDiscoveryHypoTests:
            configMgr.cppMgr.doHypoTestAll('results/', False)
        
        if doHypoTests:
            configMgr.cppMgr.doHypoTestAll('results/', True)

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

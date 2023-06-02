// vim: ts=4:sw=4
/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Namespace: Util                                                                *
 *                                                                                *
 * Description:                                                                   *
 *      Implementation (see header for description)                               *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva, Switzerland                               *
 *      Lorenzo Moneta, CERN, Geneva  <Lorenzo.Moneta@cern.h>                     *
 *           See: FitPdf()                                                        *
 *      Wouter Verkerke, Nikhef, Amsterdam <verkerke@nikhef.nl>                   *
 *           See: getPropagatedError()                                            *
 *                                                                                *
 * See corresponding .h file for author and license information                   *
 **********************************************************************************/
#include <memory>

#include "Utils.h"
#include "ConfigMgr.h"
#include "TMsgLogger.h"
#include "ChannelStyle.h"
#include "HistogramPlotter.h"

#include "TMap.h"
#include "TString.h"
#include "TObjString.h"
#include "TObjArray.h"

#include "RooArgSet.h"
#include "TIterator.h"
#include "RooAbsReal.h"
#include "RooAbsPdf.h"
#include "RooAbsArg.h"
#include "RooFitResult.h"
#include "RooRealVar.h"
#include "RooWorkspace.h"
#include "RooSimultaneous.h"
#include "RooProdPdf.h"
#include "RooAddPdf.h"
#include "RooDataSet.h"
#include "RooPlot.h"
#include "RooProduct.h"
#include "RooMCStudy.h"
#include "Roo1DTable.h"
#include "RooCategory.h"
#include "RooRealSumPdf.h"
#include "RooGaussian.h"
#include "RooCurve.h"
#include "RooHist.h"
#include "RooMinimizer.h"
#include "RooConstVar.h"
#include "RooNumIntConfig.h"
#include "RooMinimizer.h"
#include "RooFormulaVar.h"
#include "RooNLLVar.h"

#include "RooStats/ModelConfig.h"
#include "RooStats/ProfileLikelihoodTestStat.h"
#include "RooStats/ProfileLikelihoodCalculator.h"
#include "RooStats/LikelihoodInterval.h"
#include "RooStats/ToyMCSampler.h"
#include "RooStats/SamplingDistPlot.h"
#include "RooStats/HypoTestInverterResult.h"
#include "RooStats/HypoTestResult.h"
#include "RooStats/RooStatsUtils.h"
#include "RooStats/HistFactory/PiecewiseInterpolation.h"

#include "TAxis.h"
#include "TArrow.h"
#include "TF1.h"
#include "TH1F.h"
#include "TH2D.h"
#include "TTree.h"
#include "TBranch.h"
#include "TGraph2D.h"
#include "TGraphAsymmErrors.h"
#include "TPad.h"
#include "TGaxis.h"
#include "TStyle.h"

#include "TVectorD.h"
#include "TFile.h"
#include "TLine.h"
#include "TLatex.h"
#include "TCanvas.h"
#include "TLegend.h"
#include "TLegendEntry.h"

#include "TROOT.h"


#include <iostream>
#include <fstream>
#include <vector>

using namespace std;
using namespace RooFit;
using namespace RooStats;

namespace Util {
  static TMsgLogger Logger("Util");
  bool deactivateBinnedLikelihood = false;
}

//_____________________________________________________________________________
double Util::looseToTightVal(const TString& reg, TMap* map){
  double nLMT=((TObjString*)map->GetValue("DATA_DATA_"+reg+"lmt"))->GetString().Atof();
  double nTopTight=((TObjString*)map->GetValue("MC_tt_"+reg))->GetString().Atof();
  double nWTight=((TObjString*)map->GetValue("MC_WZ_"+reg))->GetString().Atof();
  double LtoTeffFake=((TObjString*)map->GetValue("LtoTeffFake_QCD"+reg+"_"+reg+"lmt"))->GetString().Atof();
  double LtoTeffReal_tt=((TObjString*)map->GetValue("LtoTeffReal_tt_"+reg+"lmt"))->GetString().Atof();
  double LtoTeffReal_W=((TObjString*)map->GetValue("LtoTeffReal_WZ_"+reg+"lmt"))->GetString().Atof();
  double fBTagTop=((TObjString*)map->GetValue("btag_sep_tt"))->GetString().Atof();
  double fBTagWZ=((TObjString*)map->GetValue("btag_sep_WZ"))->GetString().Atof();

  double nTop=nTopTight * (LtoTeffReal_tt-1.0);
  double nWZ=nWTight * (LtoTeffReal_W-1.0);
  if(reg=="TR"){
    nTop=nTop*fBTagTop;
    nWZ=nWZ*fBTagWZ;
  }
  else if(reg=="WR"){
    nTop=nTop*(1.0-fBTagTop);
    nWZ=nWZ*(1.0-fBTagWZ);
  }

  double val=(nLMT-nTop-nWZ)/LtoTeffFake;
  return val;
}

//_____________________________________________________________________________
double Util::looseToTightErr(const TString& reg, TMap* map){
    double nLMT=((TObjString*)map->GetValue("DATA_DATA_"+reg+"lmt"))->GetString().Atof();
    double LtoTeffFake=((TObjString*)map->GetValue("LtoTeffFake_QCD"+reg+"_"+reg+"lmt"))->GetString().Atof();
    double err=sqrt(nLMT)/LtoTeffFake; //incomplete and temporary
    return err;
}

//_____________________________________________________________________________
double Util::getNonQcdVal(const TString& proc, const TString& reg, TMap* map,const TString& opt){
    TString prefix="MC_";
    if(proc=="DATA"){ prefix="DATA_"; }

    double val=((TObjString*)map->GetValue(prefix+proc+opt+"_"+reg))->GetString().Atof();

    //exception #1: WTR, overwrite val
    if((reg=="WR" || reg=="TR") && proc!="DATA"){
        double mcVal=val;
        double fBTag=((TObjString*)map->GetValue("btag_sep_"+proc))->GetString().Atof();
        if(reg=="TR"){ val=mcVal*fBTag; }
        else if(reg=="WR"){ val=mcVal*(1.0-fBTag); }
    }
    return val;
}




//_____________________________________________________________________________
void Util::GenerateFitAndPlot(TString fcName, TString anaName, Bool_t drawBeforeFit, Bool_t drawAfterFit,
        Bool_t doStackPlots, Bool_t storeSingleFiles, Bool_t storeMergedFile,
        Bool_t plotCorrelationMatrix,
        Bool_t plotSeparateComponents, Bool_t plotNLL, Bool_t minos, TString minosPars,
        Bool_t doFixParameters, TString fixedPars, bool ReduceCorrMatrix, bool noFit, bool plotInterpolation){

    ConfigMgr* mgr = ConfigMgr::getInstance();
    FitConfig* fc = mgr->getFitConfig(fcName);

    Logger << kINFO << " GenerateFitAndPlot for FitConfig = " << fc->m_name << GEndl;
    Logger << kINFO << "     analysisName = " << anaName << GEndl;
    Logger << kINFO << "     drawBeforeFit = " << drawBeforeFit << GEndl;
    Logger << kINFO << "     drawAfterFit = " << drawAfterFit << GEndl;
    Logger << kINFO << "     doStackPlots = " << doStackPlots << GEndl;
    Logger << kINFO << "     storeSingleFiles = " << storeSingleFiles << GEndl;
    Logger << kINFO << "     storeMergedFile = " << storeMergedFile << GEndl;
    Logger << kINFO << "     plotCorrelationMatrix = " << plotCorrelationMatrix << GEndl;
    Logger << kINFO << "     plotSeparateComponents = " << plotSeparateComponents << GEndl;
    Logger << kINFO << "     plotNLL = " << plotNLL << GEndl;
    Logger << kINFO << "     minos = " << minos << GEndl;
    Logger << kINFO << "     minosPars = " << minosPars << GEndl;
    Logger << kINFO << "     doFixParameters = " << doFixParameters << GEndl;
    Logger << kINFO << "     fixedPars = " << fixedPars << GEndl;
    Logger << kINFO << "     ReduceCorrMatrix = " << ReduceCorrMatrix << GEndl;
    Logger << kINFO << "     noFit = " << noFit << GEndl;
    Logger << kINFO << "     plotInterpolation = " << plotInterpolation << GEndl;

    auto inputFilename = fc->m_inputWorkspaceFileName;
    Logger << kINFO << " Will read workspace from filename " << inputFilename << GEndl;

    if(noFit) {
        // TOOD: might not work when using ToyMC
        inputFilename.ReplaceAll(".root","_afterFit.root");
        Logger << kINFO << " Updated input filename to " << inputFilename << GEndl;

        //if (suffix != "") { //comes from ToyMC::GetName()
            //TString suff =  "_" + suffix + ".root";
            //outFileName.ReplaceAll(".root",suff);
        //}
    }

    RooWorkspace* w = GetWorkspaceFromFile(inputFilename, "combined");
    if(w==NULL){
        Logger << kWARNING << "     RooWorkspace('combined') does not exist, trying workspace('w')" << GEndl;
        w = GetWorkspaceFromFile(inputFilename, "w");
        if(w) {
            Logger << kWARNING << "Managed to find workspace 'w'!" << GEndl;
        }
    }

    if(w==NULL){
        Logger << kERROR << "     Cannot find RooWorkspace, quitting " << GEndl;
        return;
    }

    Util::SetInterpolationCode(w,4);
    if (not noFit ) {
        // only modify the workspace when actually fitting
        SaveInitialSnapshot(w);
    }

    TString plotChannels = "ALL";

    // fit only in CRs and SRs, not in VR
    TString fitChannels = "";
    for(unsigned int i=0; i <fc->m_bkgConstrainChannels.size(); i++){
        if (fitChannels.Length() > 0)   fitChannels += ",";
        fitChannels += fc->m_bkgConstrainChannels[i];
    }

    for(unsigned int i=0; i <fc->m_signalChannels.size(); i++){
        if (fitChannels.Length() > 0)   fitChannels += ",";
        fitChannels += fc->m_signalChannels[i];
    }

    //hack to be fixed at HistFactory level (check again with ROOT 5.34)
    // Bool_t lumiConst = kTRUE;
    //if (fc->m_signalChannels.size() > 0)
    Bool_t lumiConst = kFALSE;

    //  fit toy MC if specified. When left None, data is fit by default
    RooAbsData* toyMC = NULL;
    if(not noFit) {
        if( mgr->m_seed != 0 && !mgr->m_useAsimovSet){
            // generate a toy dataset
            Logger << kINFO << " Util::GenerateFitAndPlot() : generating toy MC set for fitting and plotting.      Seed =" << mgr->m_seed << GEndl;
            toyMC = GetToyMC();    // this generates one toy dataset
        } else if (mgr->m_useAsimovSet && mgr->m_seed == 0 ){
            Logger << kINFO << " Util::GenerateFitAndPlot() : using Asimov set for fitting and plotting." << GEndl;
            toyMC = GetAsimovSet(w);  // this returns the asimov set
        } else {
            Logger << kINFO << " Util::GenerateFitAndPlot()  : using data for fitting and plotting." <<  GEndl;
        }
    }

    // set Errors of all parameters to 'natural' values before plotting/fitting
    resetAllErrors(w);

    // get a list of all floating parameters for all regions
    RooAbsPdf* simPdf = w->pdf("simPdf");
    ModelConfig*  mc = GetModelConfig(w);
    const RooArgSet* obsSet = mc->GetObservables();
    RooArgList floatPars = getFloatParList(*simPdf, *obsSet);

    // create an RooExpandedFitResult encompassing all the
    // regions/parameters & save it to workspace
    RooExpandedFitResult* expResultBefore;
    if(not noFit) {
        expResultBefore = new RooExpandedFitResult(floatPars);
        ImportInWorkspace(w, expResultBefore, "RooExpandedFitResult_beforeFit");
    } else {
        // retrieve from the workspace
        expResultBefore = static_cast<RooExpandedFitResult*>( w->genobj("RooExpandedFitResult_beforeFit") );
        LoadSnapshotInWorkspace(w, "snapshot_paramsVals_RooExpandedFitResult_beforeFit");
    }

    // fire up a plotter

    // plot before fit
    if (drawBeforeFit) {
        HistogramPlotter h(w, fc->m_name);
        h.setAnalysisName(anaName);
        h.setPlotRegions(plotChannels);
        h.setPlotComponents(true);
        h.setPlotSeparateComponents(false);
        h.setDoStackPlots(doStackPlots);
        h.setStoreSingleFiles(storeSingleFiles);
        h.setStoreMergedFile(storeMergedFile);
        h.setOutputPrefix("beforeFit");
        h.setFitResult(expResultBefore);
        h.setInputData(toyMC);

        h.Initialize();
        h.PlotRegions();
    }

    // perform fit
    RooFitResult* result = nullptr;
    RooExpandedFitResult* expResultAfter = nullptr;
    if(not noFit) {
        //fit of all regions
        result = FitPdf(w, fitChannels, lumiConst, toyMC, "", minos, minosPars, doFixParameters, fixedPars);

        if (result == NULL) {
            Logger << kERROR << "PlotNLL(): running FitPdf() failed!" << GEndl;
            return;
        }

        // create an RooExpandedFitResult encompassing all the regions/parameters
        //  with the result & save it to workspace
        expResultAfter = new RooExpandedFitResult(result, floatPars);
        ImportInWorkspace(w, expResultAfter, "RooExpandedFitResult_afterFit");
    } else {
        // load back the fit result
        expResultAfter = static_cast<RooExpandedFitResult*>( w->genobj("RooExpandedFitResult_afterFit") );
        LoadSnapshotInWorkspace(w, "snapshot_paramsVals_RooExpandedFitResult_afterFit");
    }

    // plot after fit
    if (drawAfterFit) {
        HistogramPlotter h(w, fc->m_name);
        h.setAnalysisName(anaName);
        h.setPlotRegions(plotChannels);
        h.setPlotComponents(true);
        h.setPlotSeparateComponents(false);
        h.setDoStackPlots(doStackPlots);
        h.setStoreSingleFiles(storeSingleFiles);
        h.setStoreMergedFile(storeMergedFile);
        h.setOutputPrefix("afterFit");
        h.setFitResult(expResultAfter);
        h.setInputData(toyMC);

        // plot each component of each region separately with propagated
        // error after fit  (interesting for debugging)
        if(plotSeparateComponents) {
            h.setPlotSeparateComponents(true);
        }

        h.Initialize();
        h.PlotRegions();
    }

    //plot correlation matrix for result
    if(plotCorrelationMatrix) {
        //PlotCorrelationMatrix(result, anaName, ReduceCorrMatrix);
        PlotCorrelationMatrix(expResultAfter, anaName, ReduceCorrMatrix);
    }

    // plot likelihood
    Bool_t plotPLL = minos;
    if(plotNLL) {
        PlotNLL(w, expResultAfter, plotPLL, anaName, "", toyMC, minosPars, fitChannels, lumiConst);
    }

    if(not noFit) {
        // only write out output workspace if we've run a fit
        if (toyMC) {
            WriteWorkspace(w, inputFilename, toyMC->GetName());
        } else {
            WriteWorkspace(w, inputFilename);
        }
    }
    if (result){
        result->Print("v");
        PlotFitParameters(result,anaName);
    }

    // plot the interpolation of nuisance parameters
    if (plotInterpolation) {
        plotInterpolationScheme(w);
    }


}

///////////////

//_____________________________________________________________________________
void Util::GeneratePlots(TString filename, TString anaName, Bool_t drawBeforeFit, Bool_t drawAfterFit, Bool_t plotCorrelationMatrix,
        Bool_t plotSeparateComponents, Bool_t plotNLL, Bool_t minos, TString minosPars,
        Bool_t doFixParameters, TString fixedPars, bool ReduceCorrMatrix){

    const bool noFit = true; // we never re-fit an existing afterFit workspace

    Logger << kINFO << " GeneratePlots for filename = " << filename << GEndl;
    Logger << kINFO << "     analysisName = " << anaName << GEndl;
    Logger << kINFO << "     drawBeforeFit = " << drawBeforeFit << GEndl;
    Logger << kINFO << "     drawAfterFit = " << drawAfterFit << GEndl;
    Logger << kINFO << "     plotCorrelationMatrix = " << plotCorrelationMatrix << GEndl;
    Logger << kINFO << "     plotSeparateComponents = " << plotSeparateComponents << GEndl;
    Logger << kINFO << "     plotNLL = " << plotNLL << GEndl;
    Logger << kINFO << "     minos = " << minos << GEndl;
    Logger << kINFO << "     minosPars = " << minosPars << GEndl;
    Logger << kINFO << "     doFixParameters = " << doFixParameters << GEndl;
    Logger << kINFO << "     fixedPars = " << fixedPars << GEndl;
    Logger << kINFO << "     ReduceCorrMatrix = " << ReduceCorrMatrix << GEndl;

    auto inputFilename = filename;
    Logger << kINFO << " Will read workspace from filename " << inputFilename << GEndl;

    if(noFit) {
        // TOOD: might not work when using ToyMC
        inputFilename.ReplaceAll(".root","_afterFit.root");
        Logger << kINFO << " Updated input filename to " << inputFilename << GEndl;

        //if (suffix != "") { //comes from ToyMC::GetName()
            //TString suff =  "_" + suffix + ".root";
            //outFileName.ReplaceAll(".root",suff);
        //}
    }

    RooWorkspace* w = GetWorkspaceFromFile(inputFilename, "combined");
    if(w==NULL){
        Logger << kWARNING << "     RooWorkspace('combined') does not exist, trying workspace('w')" << GEndl;
        w = GetWorkspaceFromFile(inputFilename, "w");
        if(w) {
            Logger << kWARNING << "Managed to find workspace 'w'!" << GEndl;
        }
    }

    if(w==NULL){
        Logger << kERROR << "     Cannot find RooWorkspace, quitting " << GEndl;
        return;
    }

    Util::SetInterpolationCode(w,4);
    if (not noFit ) {
        // only modify the workspace when actually fitting
        SaveInitialSnapshot(w);
    }

    TString plotChannels = "ALL";

    //// fit only in CRs and SRs, not in VR
    //TString fitChannels = "";
    //for(unsigned int i=0; i <fc->m_bkgConstrainChannels.size(); i++){
        //if (fitChannels.Length() > 0)   fitChannels += ",";
        //fitChannels += fc->m_bkgConstrainChannels[i];
    //}

    //for(unsigned int i=0; i <fc->m_signalChannels.size(); i++){
        //if (fitChannels.Length() > 0)   fitChannels += ",";
        //fitChannels += fc->m_signalChannels[i];
    //}

    //hack to be fixed at HistFactory level (check again with ROOT 5.34)
    // Bool_t lumiConst = kTRUE;
    //if (fc->m_signalChannels.size() > 0)
    Bool_t lumiConst = kFALSE;

    //  fit toy MC if specified. When left None, data is fit by default
    RooAbsData* toyMC = NULL;
/*    if(not noFit) {*/
        //if( mgr->m_seed != 0 && !mgr->m_useAsimovSet){
            //// generate a toy dataset
            //Logger << kINFO << " Util::GenerateFitAndPlot() : generating toy MC set for fitting and plotting.      Seed =" << mgr->m_seed << GEndl;
            //toyMC = GetToyMC();    // this generates one toy dataset
        //} else if (mgr->m_useAsimovSet && mgr->m_seed == 0 ){
            //Logger << kINFO << " Util::GenerateFitAndPlot() : using Asimov set for fitting and plotting." << GEndl;
            //toyMC = GetAsimovSet(w);  // this returns the asimov set
        //} else {
            //Logger << kINFO << " Util::GenerateFitAndPlot()  : using data for fitting and plotting." <<  GEndl;
        //}
    /*}*/

    // set Errors of all parameters to 'natural' values before plotting/fitting
    resetAllErrors(w);

    // get a list of all floating parameters for all regions
    RooAbsPdf* simPdf = w->pdf("simPdf");
    ModelConfig*  mc = GetModelConfig(w);
    const RooArgSet* obsSet = mc->GetObservables();
    RooArgList floatPars = getFloatParList(*simPdf, *obsSet);

    // create an RooExpandedFitResult encompassing all the
    // regions/parameters & save it to workspace
    RooExpandedFitResult* expResultBefore;
    if(not noFit) {
        expResultBefore = new RooExpandedFitResult(floatPars);
        ImportInWorkspace(w, expResultBefore, "RooExpandedFitResult_beforeFit");
    } else {
        // retrieve from the workspace
        expResultBefore = static_cast<RooExpandedFitResult*>( w->genobj("RooExpandedFitResult_beforeFit") );
        LoadSnapshotInWorkspace(w, "snapshot_paramsVals_RooExpandedFitResult_beforeFit");
    }

    // plot before fit
    if (drawBeforeFit)
        PlotPdfWithComponents(w, "beforeFit", anaName, plotChannels, "beforeFit", expResultBefore, toyMC);

    RooFitResult* result = nullptr;
    RooExpandedFitResult* expResultAfter = nullptr;
    //if(not noFit) {
        ////fit of all regions
        //result = FitPdf(w, fitChannels, lumiConst, toyMC, "", minos, minosPars, doFixParameters, fixedPars);

        //if (result == NULL) {
            //Logger << kERROR << "PlotNLL(): running FitPdf() failed!" << GEndl;
            //return;
        //}

        //// create an RooExpandedFitResult encompassing all the regions/parameters
        ////  with the result & save it to workspace
        //expResultAfter = new RooExpandedFitResult(result, floatPars);
        //ImportInWorkspace(w, expResultAfter, "RooExpandedFitResult_afterFit");
    //} else {
        // load back the fit result
        expResultAfter = static_cast<RooExpandedFitResult*>( w->genobj("RooExpandedFitResult_afterFit") );
        LoadSnapshotInWorkspace(w, "snapshot_paramsVals_RooExpandedFitResult_afterFit");
    //}

    // plot after fit
    if (drawAfterFit) {
        PlotPdfWithComponents(w, "afterFit", anaName, plotChannels, "afterFit", expResultAfter, toyMC);
    }

    // plot each component of each region separately with propagated
    // error after fit  (interesting for debugging)
    if(plotSeparateComponents) {
        //PlotSeparateComponents(w, fc->m_name, anaName, plotChannels, "afterFit", result, toyMC);
        PlotSeparateComponents(w, "afterFit_separateComponents", anaName, plotChannels, "afterFit", expResultAfter, toyMC);
    }

    //plot correlation matrix for result
    if(plotCorrelationMatrix) {
        //PlotCorrelationMatrix(result, anaName, ReduceCorrMatrix);
        PlotCorrelationMatrix(expResultAfter, anaName, ReduceCorrMatrix);
    }

    // plot likelihood
    Bool_t plotPLL = minos;
    if(plotNLL) {
        //PlotNLL(w, expResultAfter, plotPLL, anaName, "", toyMC, minosPars, fitChannels, lumiConst);
        PlotNLL(w, expResultAfter, plotPLL, anaName, "", toyMC, minosPars, "ALL", lumiConst);
    }

    if(not noFit) {
        // only write out output workspace if we've run a fit
        if (toyMC) {
            WriteWorkspace(w, inputFilename, toyMC->GetName());
        } else {
            WriteWorkspace(w, inputFilename);
        }
    }
    if (result)
        result->Print("v");
}


//_____________________________________________________________________________
void Util::SaveInitialSnapshot(RooWorkspace* w){

    if(w==NULL){
        Logger << kINFO << "Util::SaveInitialSnapshot():   workspace does not exist" << GEndl;
        return;
    }

    w->SetName("w");
    w->SetTitle("w");

    // save snapshot before any fit has been done
    RooSimultaneous* pdf = (RooSimultaneous*) w->pdf("simPdf");
    if(pdf==NULL){
      pdf = (RooSimultaneous*) w->pdf("combPdf");
    }
    if(pdf==NULL){
        Logger << kWARNING << "Util::SaveInitialSnapshot():   not saving the initial snapshot as cannot find pdf (simPdf or combPdf) in workspace" << GEndl;
        return;
    }

    RooAbsData* data = (RooAbsData*) w->data("obsData");
    RooArgSet* params = (RooArgSet*) pdf->getParameters(*data) ;
    if(!w->getSnapshots().find("snapshot_paramsVals_initial")) {
        w->saveSnapshot("snapshot_paramsVals_initial",*params);
    } else {
        Logger << kWARNING << "Snapshot 'snapshot_paramsVals_initial' already exists in  workspace, will not overwrite it" << GEndl;
    }

    // Put workspace in the global directory
    gDirectory->Add(w);

}


//_____________________________________________________________________________
void Util::LoadSnapshotInWorkspace(RooWorkspace* w,TString snapshot){

    Bool_t loaded =  w->loadSnapshot(snapshot);

    if (loaded){
        Logger << kINFO << "workspace loaded" << GEndl;
        return;
    } else {
        Logger << kWARNING << "Util.LoadSnapshotInWorkspace() did not find snapshot named "  << snapshot << ", check your workspace file" << GEndl;
    }

    return;

}


//_____________________________________________________________________________
void Util::WriteWorkspace(RooWorkspace* w, TString outFileName, TString suffix){

    if(w==NULL){
        Logger << kERROR << "Workspace not found, not writing workspace to file" << GEndl;
        return;
    }

    outFileName.ReplaceAll(".root","_afterFit.root");

    if (suffix != "") {
        TString suff =  "_" + suffix + ".root";
        outFileName.ReplaceAll(".root",suff);
    }

    w->SetName("w");
    w->SetTitle("w");

    w->writeToFile(outFileName.Data());

    Logger << kINFO << " Util::WriteWorkspace():   have written workspace to file " <<  outFileName << GEndl;

    return;
}


/*
 * The FitPdf() function is (partially) taken from the function
 * RooStats::ProfileLikelihoodTestStat::GetMinNLL()
 * See: http://root.cern.ch/root/html534/src/RooStats__ProfileLikelihoodTestStat.cxx.html
 * ((http://root.cern.ch/drupal/content/license))
 */

//_____________________________________________________________________________
RooFitResult* Util::FitPdf( RooWorkspace* w, TString fitRegions, Bool_t lumiConst, RooAbsData* inputData, TString suffix, Bool_t minos, TString minosPars, Bool_t doFixParameters, TString fixedPars)
{

    Logger << kINFO << " ------ Starting FitPdf with parameters:    fitRegions = " <<  fitRegions << GEndl;
    Logger << kINFO <<  "    inputData = " << inputData << "  suffix = " << suffix  << "  minos = " << minos << "  minosPars = " << minosPars  << " doFixParameters = " << doFixParameters << " fixedPars = " << fixedPars << GEndl;

    // enable internal likelihood offsetting for enhanced numeric precision
    RooStats::UseNLLOffset(true);

    RooMsgService::instance().getStream(1).removeTopic(NumIntegration);

    if(!w){
        Logger << kERROR << "Workspace not found, no fitting performed" << GEndl;
        return NULL;
    }

    if(!deactivateBinnedLikelihood) {
        RooFIter iter = w->components().fwdIterator();
        RooAbsArg* arg;
        while ((arg = iter.next())) {
            if (arg->IsA() == RooRealSumPdf::Class()) {
                arg->setAttribute("BinnedLikelihood");
                cout << "Activating binned likelihood attribute for " << arg->GetName() << endl;
            }
        }
    }

    RooSimultaneous* pdf = static_cast<RooSimultaneous*>(w->pdf("simPdf"));

    RooAbsData* data = ( inputData!=0 ? inputData : static_cast<RooAbsData*>(w->data("obsData")) );
    if(!data) {
        Logger << kFATAL << "Can't find RooAbsData 'data' in workspace. Are you attempting to run a blinded fit but did you not add a (dummy) data sample?" << GEndl;
        return NULL;
    }

    RooCategory* regionCat = (RooCategory*) w->cat("channelCat");
    if(!regionCat) {
        Logger << kERROR << "Can't find RooCategory 'channelCat' in workspace" << GEndl;
        return NULL;
    }

    RooAbsCategory* absRegionCat = static_cast<RooAbsCategory*>(regionCat);
    if(!absRegionCat) {
        Logger << kERROR << "Can't cast RooAbsCategory 'channelCat' from workspace" << GEndl;
        return NULL;
    }

    Logger << kINFO << "Will dump channelCat as RooAbsCategory now:" << GEndl;
    absRegionCat->Print("v");

    //auto table = data->table(*((RooAbsCategory*)regionCat));
    auto table = data->table(*absRegionCat);
    if(!table) {
        Logger << kERROR << "data->table(channelCat) returned NULL" << GEndl;
        return NULL;
    }

    Logger << kINFO << "Will dump table for channelCat now:" << GEndl;
    table->Print("v");

    if (lumiConst) {
        RooRealVar* lumi = (RooRealVar*) w->var("Lumi");
        if (lumi!=NULL) lumi->setConstant(lumiConst);
    }

    //fixing parameters to certain values
    if (doFixParameters && fixedPars != "") {
     std::vector<TString> fixedParsVector = Tokens(fixedPars,",");
     for (unsigned int j=0; j<fixedParsVector.size(); j++) {
         std::vector<TString> fixedParsPair = Tokens(fixedParsVector[j],":");
         if (fixedParsPair.size() != 2) {
             Logger << kERROR << " Util::FitPdf() fixing parameters to constant: wrong arguments given: " <<  fixedParsVector[j] << GEndl;
             Logger << kERROR << " Util::FitPdf() Ignore this and continue." << GEndl;
             continue;
         }
         RooRealVar* var = (RooRealVar*) w->var(fixedParsPair[0]);
         if(var==NULL)  Logger << kWARNING << " Util::FitPdf()   could not find parameter(" << fixedParsPair[0] << ") in workspace while trying to fix this parameter" << GEndl;
         else {
             Logger << kINFO << " Util::FitPdf() Setting parameter " <<  fixedParsPair[0] << " to constant value " << fixedParsPair[1].Atof() << GEndl;
             var->setVal(fixedParsPair[1].Atof());
             var->setConstant(kTRUE);
         }
     }
    }

    // Construct an empty simultaneous pdf using category regionCat as index
    RooSimultaneous* simPdfFitRegions = pdf;
    RooDataSet* dataFitRegions = (RooDataSet*) data;

    std::vector<TString> fitRegionsVec = GetRegionsVec(fitRegions, regionCat);

    unsigned int numFitRegions = fitRegionsVec.size();
    std::vector<RooDataSet*> dataVec;
    std::vector<RooAbsPdf*> pdfVec;

    for(unsigned int iVec=0; iVec<numFitRegions; iVec++){
        TString regionCatLabel = fitRegionsVec[iVec];
        if( regionCat->setLabel(regionCatLabel,kTRUE)){
            Logger << kWARNING << " Label '" << regionCatLabel << "' is not a state of channelCat (see Table) " << GEndl;
        } else{
            // dataset for each channel/region/category
            TString dataCatLabel = Form("channelCat==channelCat::%s",regionCatLabel.Data());
            RooDataSet* regionData = (RooDataSet*) data->reduce(dataCatLabel.Data());
            dataVec.push_back(regionData);
            // pdf for each channel/region/category
            RooAbsPdf* regionPdf = (RooAbsPdf*) pdf->getPdf(regionCatLabel.Data());
            pdfVec.push_back(regionPdf);
        }
    }


    if(dataVec.empty()){
        Logger << kERROR << "   NONE OF THE REGIONS ARE SPECIFIED IN DATASET, NO FIT WILL BE PERFORMED" << GEndl;
        return 0;
    }
    else if(pdfVec.empty()){
        Logger << kERROR << "   NONE OF THE REGIONS ARE SPECIFIED IN SIMULTANEOUS PDF, NO FIT WILL BE PERFORMED" << GEndl;
        return 0;
    }
    else{
        // Construct a simultaneous dataset for all fit regions
        dataFitRegions = (RooDataSet*) dataVec[0]->Clone("dataFitRegions");
        for(unsigned int jVec=1; jVec<dataVec.size(); jVec++){
            dataFitRegions->append(*dataVec[jVec]);
        }
        // Construct a simultaneous pdf using category regionCat as index
        simPdfFitRegions = new RooSimultaneous("simPdfFitRegions","simultaneous pdf only for fit regions",*regionCat) ;
        for(unsigned int kVec=0; kVec<pdfVec.size(); kVec++){
            simPdfFitRegions->addPdf(*pdfVec[kVec],fitRegionsVec[kVec].Data());
        }
    }

    w->import(*simPdfFitRegions,kTRUE);
    gDirectory->Add(simPdfFitRegions);

    // find parameters requested for Minos
    RooArgSet* minosParams = new RooArgSet();
    if(minosPars != "" && minos && minosPars != "all"  && minosPars != "ALL"){
        std::vector<TString> parsVec = Tokens(minosPars,",");
        for(unsigned int i=0; i<parsVec.size();i++){
            RooRealVar* var = (RooRealVar*) w->var(parsVec[i]);
            if(var==NULL)  Logger << kWARNING << " Util::FitPdf()   could not find parameter(" << parsVec[i] << ") in workspace while setting up minos" << GEndl;
            else{
                minosParams->add(*var);
            }
        }
    }

    // fit pdf to data
    RooFitResult* r = 0;

    TString datasetname = data->GetName();
    Logger << kINFO << " Utils::FitPdf() using datasetname = " << datasetname << GEndl;

    RooAbsPdf* pdf_FR = simPdfFitRegions;
    RooDataSet* data_FR = dataFitRegions;

    RooArgSet* allParams = pdf_FR->getParameters(data_FR);
    RooStats::RemoveConstantParameters(allParams);

    RooStats::ModelConfig* mc = Util::GetModelConfig( w );
    const RooArgSet* globObs = mc->GetGlobalObservables();

    RooAbsReal* nll = (RooNLLVar*) pdf_FR->createNLL(*data_FR, RooFit::GlobalObservables(*globObs), RooFit::Offset(true) );

    int minimPrintLevel = 1; //verbose;

    RooMinimizer minim(*nll);
    int strategy = ROOT::Math::MinimizerOptions::DefaultStrategy();
    minim.setStrategy( strategy);
    // enable internal likelihood offsetting for enhanced numeric precision
    minim.setOffsetting(true);
    // use tolerance - but never smaller than 1 (default in RooMinimizer)
    double tol =  ROOT::Math::MinimizerOptions::DefaultTolerance();
    tol = std::max(tol, 1.0); // 1.0 is the minimum value used in RooMinimizer
    minim.setEps( tol );

    //LM: RooMinimizer.setPrintLevel has +1 offset - so subtruct  here -1
    minim.setPrintLevel(minimPrintLevel-1);
    int status = -1;
    minim.optimizeConst(2);
    TString minimizer = "Minuit2"; //ROOT::Math::MinimizerOptions::DefaultMinimizerType();
    TString algorithm = ROOT::Math::MinimizerOptions::DefaultMinimizerAlgo();

    Logger << kINFO << "Util::FitPdf()  ........ using " << minimizer << " / " << algorithm << GEndl;
    Logger << kINFO << " with strategy  " << strategy << " and tolerance " << tol << GEndl;


    for (int tries = 1, maxtries = 4; tries <= maxtries; ++tries) {
        status = minim.minimize(minimizer, algorithm);
        if (status%1000 == 0) {  // ignore erros from Improve
            break;
        } else {
            if (tries == 1) {
                Logger << kINFO << "    ----> Doing a re-scan first" << GEndl;
                minim.minimize(minimizer,"Scan");
            }
            if (tries == 2) {
                if (ROOT::Math::MinimizerOptions::DefaultStrategy() == 0 ) {
                    Logger << kINFO << "    ----> trying with strategy = 1" << GEndl;
                    minim.setStrategy(1);
                }
                else
                    tries++; // skip this trial if stratehy is already 1
            }
            if (tries == 3) {
                Logger << kINFO << "    ----> trying with improve" << GEndl;
                minimizer = "Minuit";
                algorithm = "migradimproved";
            }
        }
    }

    if (status%100 == 0) { // ignore errors in Hesse or in Improve
        // only calculate minos errors if fit with Migrad converged
        if(minos && (minosPars == "all" || minosPars == "ALL")){
            minim.hesse();
            minim.minos();
        }
        else if(minos && minosPars!="" && minosParams->getSize()>0){
            minim.hesse();
            minim.minos(*minosParams);
        }
        else {
            minim.hesse();
        }

        // save fit result
        r = minim.save();
    }
    else {
        Logger << kERROR << "FIT FAILED !- return a NaN NLL " << GEndl;
    }

    if (r!=0) r->Print("v");

    TString fitName = data_FR->GetName();
    for(unsigned int iVec=0; iVec<fitRegionsVec.size(); iVec++){
        if(iVec ==0)  fitName += "_fitRegions";
        fitName += "_" + fitRegionsVec[iVec];
    }

    TString resultname = Form("RooFitResult_%s",fitName.Data());
    if(suffix!= "") resultname += "_" + suffix;
    if (r!=0) {
        r->SetName(resultname.Data());
        w->import(*r,kTRUE) ;
        gDirectory->Add(r);
    }

    // save snapshot after fit has been done
    RooArgSet* params = (RooArgSet*) pdf_FR->getParameters(*data_FR) ;
    w->saveSnapshot(Form("snapshot_paramsVals_%s",resultname.Data()),*params);

    return r;
}


//_____________________________________________________________________________
void
Util::SetInterpolationCode(RooWorkspace* w, Int_t code)
{
    if(w==NULL){
        Logger << kERROR << "Workspace is NULL. Return." << GEndl;
        return;
    }

    RooArgSet funcs = w->allFunctions();
    TIterator* iter = funcs.createIterator() ;

    RooAbsArg* parg(0);
    while((parg=(RooAbsArg*)iter->Next())) {
        if ( parg->ClassName()!=TString("PiecewiseInterpolation") ) { continue; }
        PiecewiseInterpolation* p = (PiecewiseInterpolation*)w->function( parg->GetName() ); // something I can modifiy :)
        p->setAllInterpCodes(code);
    }

    delete iter;
}


//_____________________________________________________________________________
RooAbsData*
Util::GetAsimovSet( RooWorkspace* inputws  )
{
    RooWorkspace* w(0);
    if (inputws!=NULL) { w = inputws; }
    else { w = (RooWorkspace*) gDirectory->Get("w"); }

    if(w==NULL){
        Logger << kERROR << "Workspace not found, no Asimov set found. Return." << GEndl;
        return 0;
    }

    RooAbsData* data = w->data("asimovData");
    if (data==NULL) {
        Logger << kERROR << "No Asimov set found. Return." << GEndl;
        return 0;
    }

    return data;
}


//_____________________________________________________________________________
    RooAbsData*
Util::GetToyMC( RooWorkspace* inputws  )
{
    RooWorkspace* w(0);
    if (inputws!=NULL) { w = inputws; }
    else { w = (RooWorkspace*) gDirectory->Get("w"); }
    if(w==NULL){
        Logger << kERROR << "Workspace not found, no toy dataset generated." << GEndl;
        return 0;
    }

    RooStats::ModelConfig* mc = Util::GetModelConfig( w );
    if (mc==NULL) {
        Logger << kERROR << "No model config found. Return." << GEndl;
        return 0;
    }

    RooAbsPdf* pdf = mc->GetPdf();
    if (pdf==NULL) {
        Logger << kERROR << "No pdf found. Return." << GEndl;
        return 0;
    }

    RooAbsData* data = w->data("obsData");
    if (data==NULL) {
        Logger << kERROR << "No dataset found. Return." << GEndl;
        return 0;
    }

    const RooArgSet* obsSet = mc->GetObservables();
    if (obsSet==NULL) {
        Logger << kERROR << "No observables found. Return." << GEndl;
        return 0;
    }

    Logger << kINFO << "Util::GetToyMC() : now generating toy MC set with # events : " << data->sumEntries() << GEndl;

    RooAbsData* toymc = pdf->generate( *obsSet, RooFit::NumEvents(int(data->sumEntries())), RooFit::AutoBinned(false) );

    return toymc;
}

//_____________________________________________________________________________________________________________________________________
vector<TString> Util::GetRegionsVec(TString regions, RooCategory* regionCat){

    std::vector<TString> regionsVec;
    std::vector<TString> regionsAllVec = TokensALL(regionCat);
    std::vector<TString> regionsRequestedVec = Tokens(regions,",");

    if(regions=="ALL"){ regionsVec = regionsAllVec;
    } else {
        for(unsigned int iReg=0; iReg<regionsAllVec.size(); iReg++){
            for(unsigned int jReg=0; jReg<regionsRequestedVec.size(); jReg++){
                if( regionsAllVec[iReg].EqualTo(regionsRequestedVec[jReg]) ) {
                    regionsVec.push_back(regionsAllVec[iReg]);
                }
            }
        }
    }

    return regionsVec;
}



//_____________________________________________________________________________________________________________________________________
void Util::DecomposeWS(const char* infile, const char* wsname, const char* outfile)
{

    Logger << kINFO << " ------ Util::DecomposeWS with parameters:   infile " << infile << "  wsname = " << wsname << "  outfile = " << outfile  << GEndl;

    TString fileName(infile);
    if (fileName.IsNull()) {
        Logger << kERROR << "Input filename is empty. Exit." << GEndl;
        return;
    }

    // open file and check if input file exists
    TFile * file = TFile::Open(fileName);

    // if input file was specified but not found, quit
    if(!file && !TString(infile).IsNull()){
        Logger << kERROR << "file " << fileName << " not found" << GEndl;
        return;
    }

    if(!file){
        // if it is still not there, then we can't continue
        Logger << kERROR << "Not able to open input file" <<GEndl;
        return;
    }

    RooWorkspace* w = (RooWorkspace *)file->Get(wsname);

    if (!w) {
        // if it is still not there, then we can't continue
        Logger << kERROR << "Not able to retrieve workspace" <<GEndl;
        return;
    }

    RooSimultaneous* pdf = (RooSimultaneous*) w->pdf("simPdf");

    RooAbsData* data = ( (RooAbsData*)w->data("obsData") );

    RooCategory* regionCat = (RooCategory*) w->cat("channelCat");
    data->table(*((RooAbsCategory*)regionCat))->Print("v");

    TString plotRegions = "ALL";
    std::vector<TString> regionsVec = GetRegionsVec(plotRegions, regionCat);

    unsigned  int numPlots = regionsVec.size();

    RooWorkspace* wcomb = new RooWorkspace(wsname);

    TString allObs;

    // iterate over all the regions
    for(unsigned int iVec=0; iVec<numPlots; iVec++){

        TString regionCatLabel = regionsVec[iVec];
        if( regionCat->setLabel(regionCatLabel,kTRUE)){
            Logger << kINFO << " Label '" << regionCatLabel << "' is not a state of channelCat (see Table) " << GEndl;
        }else{
            RooAbsPdf* regionPdf = (RooAbsPdf*) pdf->getPdf(regionCatLabel.Data());

            TString dataCatLabel = Form("channelCat==channelCat::%s",regionCatLabel.Data());
            RooDataSet* regionData = (RooDataSet*) data->reduce(dataCatLabel.Data());
            if(regionPdf==NULL || regionData==NULL){
                Logger << kWARNING << " Either the Pdf or the Dataset do not have an appropriate state for the region = " << regionCatLabel << ", check the Workspace file" << GEndl;
                Logger << kWARNING << " regionPdf = " << regionPdf << "   regionData = " << regionData << GEndl;
                continue;
            }

            RooRealVar* regionVar =(RooRealVar*) ((RooArgSet*) regionPdf->getObservables(*regionData))->find(Form("obs_x_%s",regionCatLabel.Data()));
            RooDataSet* rdata = (RooDataSet*)regionData->reduce(RooArgSet(*regionVar,*w->var("weightVar")));

            wcomb->import( *rdata, Rename( TString("obsData_")+TString(regionVar->GetName()) ), RenameVariable(regionVar->GetName(),"obs"), RecycleConflictNodes(true) );
            wcomb->import( *regionPdf, RenameVariable(regionVar->GetName(),"obs"), RecycleConflictNodes(true) );

        }
    }

    wcomb->writeToFile(outfile);

    file->Close();
}


//__________________________________________________________________________________________________________________________________________________________
void Util::PlotPdfWithComponents(RooWorkspace* w, TString fcName, TString anaName, TString plotRegions, TString outputPrefix, RooFitResult* rFit, RooAbsData* inputData)
{
    HistogramPlotter h(w, fcName);
    h.setAnalysisName(anaName);
    h.setPlotRegions(plotRegions);
    h.setPlotComponents(true);
    h.setOutputPrefix(outputPrefix);
    h.setFitResult(rFit);
    h.setInputData(inputData);
    h.setPlotSeparateComponents(true); //TODO: hack

    h.Initialize();
    h.PlotRegions();
}

//_____________________________________________________________________________________________________________________________________
void Util::PlotSeparateComponents(RooWorkspace* w,TString fcName, TString anaName, TString plotRegions,TString outputPrefix, RooFitResult* rFit, RooAbsData* inputData)
{
    if(rFit==NULL){
        Logger << kWARNING << " Running PlotSeparateComponents() without a RooFitResult is pointless, I'm done" << GEndl ;
        return;
    }

    Bool_t plotComponents=true;
    ConfigMgr* mgr = ConfigMgr::getInstance();
    FitConfig* fc = mgr->getFitConfig(fcName);

    Logger << kINFO << " ------ Starting PlotSeparateComponents with parameters:   analysisName = " << fcName << GEndl;
    Logger << kINFO << "    fitRegions = " <<  plotRegions <<  "  plotComponents = " << plotComponents << "  outputPrefix = " << outputPrefix  << GEndl;

    if(w==NULL){
        Logger << kWARNING << " Workspace not found, no plotting performed" << GEndl;
        return;
    }
    RooSimultaneous* pdf = (RooSimultaneous*) w->pdf("simPdf");

    RooAbsData* data = ( inputData!=0 ? inputData : (RooAbsData*)w->data("obsData") );
    RooCategory* regionCat = (RooCategory*) w->cat("channelCat");
    data->table(*((RooAbsCategory*)regionCat))->Print("v");

    if(plotRegions =="") plotRegions = "ALL";
    std::vector<TString> regionsVec = GetRegionsVec(plotRegions, regionCat);

    unsigned  int numRegions = regionsVec.size();
    TCanvas* canVec[numRegions];

    for(unsigned int iVec=0; iVec<numRegions; iVec++){

        TString regionCatLabel = regionsVec[iVec];
        if( regionCat->setLabel(regionCatLabel,kTRUE)){
            Logger << kWARNING << " Label '" << regionCatLabel << "' is not a state of channelCat (see Table) " << GEndl;
        } else{
            RooAbsPdf* regionPdf = (RooAbsPdf*) pdf->getPdf(regionCatLabel.Data());
            TString dataCatLabel = Form("channelCat==channelCat::%s",regionCatLabel.Data());
            RooAbsData* regionData = (RooAbsData*) data->reduce(dataCatLabel.Data());
            ChannelStyle style = fc->getChannelStyle(regionCatLabel);
            if(regionPdf==NULL || regionData==NULL){
                Logger << kERROR << " Either the Pdf or the Dataset do not have an appropriate state for the region = " << regionCatLabel << ", check the Workspace file" << GEndl;
                Logger << kERROR << " regionPdf = " << regionPdf << "   regionData = " << regionData << GEndl;
                continue;
            }
            RooRealVar* regionVar =(RooRealVar*) ((RooArgSet*) regionPdf->getObservables(*regionData))->find(Form("obs_x_%s",regionCatLabel.Data()));
            // get all components/samples in this region

            vector<double> regionCompFracVec = GetAllComponentFracInRegion(w, regionCatLabel, regionPdf, regionVar);
            vector<TString> regionCompNameVec = GetAllComponentNamesInRegion(regionCatLabel, regionPdf);
            Int_t numComps = regionCompNameVec.size();

            // divide the canvas
            Int_t canVecDivX = 1;
            Int_t canVecDivY = 1;
            if(numComps>0){
                canVecDivX = ((Int_t) (sqrt(numComps)));
                canVecDivY = ((Int_t) (sqrt(numComps)+0.5));

                if(canVecDivX<1)
                    canVecDivX = 1;
                if(canVecDivY<1)
                    canVecDivY = 1;
            }

            TString canName=Form("can_%s_%s_separateComponents",regionCatLabel.Data(),outputPrefix.Data());
            canVec[iVec] = new TCanvas(canName,canName,600,600); // .c_str())
            canVec[iVec]->Divide(canVecDivX , canVecDivY);

            //iterate over all samples and plot
            for( unsigned int iComp=0; iComp<regionCompFracVec.size(); iComp++){
                TString component =  regionCompNameVec[iComp];
                RooPlot* frame =  regionVar->frame();
                frame->SetName(Form("frame_%s_%s_%s",regionCatLabel.Data(),regionCompNameVec[iComp].Data(),outputPrefix.Data()));
                Int_t  compPlotColor = ( (fc!=0) ? style.getSampleColor(regionCompNameVec[iComp]) : static_cast<int>(iComp) );
                TString  compShortName  = ( (fc!=0) ? style.getSampleName(regionCompNameVec[iComp])  : "" );

                // normalize pdf to number of expected events, not to number of events in dataset
                double normCount = regionPdf->expectedEvents(*regionVar);

                if (rFit != NULL)
                    regionPdf->plotOn(frame,Components(regionCompNameVec[iComp].Data()),VisualizeError(*rFit),FillColor(kCyan),Precision(1e-5),Normalization(1,RooAbsReal::RelativeExpected));

                regionPdf->plotOn(frame,Components(regionCompNameVec[iComp].Data()),LineColor(compPlotColor),Normalization(regionCompFracVec[iComp]*normCount,RooAbsReal::NumEvent),Precision(1e-5));

                canVec[iVec]->cd(iComp+1);
                frame->SetMinimum(0.);
                frame->Draw();

                TLegend* leg = new TLegend(0.55,0.65,0.85,0.9,"");
                leg->SetFillStyle(0);
                leg->SetFillColor(0);
                leg->SetBorderSize(0);
                TLegendEntry* entry=leg->AddEntry("","Prop. Fit Error","f") ;
                entry->SetMarkerColor(kCyan);
                entry->SetMarkerStyle();
                entry->SetFillColor(kCyan);
                entry->SetFillStyle(1001);
                entry=leg->AddEntry("",compShortName.Data(),"l") ;
                entry->SetLineColor(compPlotColor);
                leg->Draw();
            }

            canVec[iVec]->SaveAs("results/"+anaName+"/"+canName+".pdf");
            canVec[iVec]->SaveAs("results/"+anaName+"/"+canName+".eps");
        }
    }
}



//_____________________________________________________________________________________________________________________________________
void Util::PlotNLL(RooWorkspace* w, RooFitResult* rFit, Bool_t plotPLL, TString anaName, TString outputPrefix, RooAbsData* inputData, TString plotPars, TString fitRegions, Bool_t lumiConst)
{
    if(rFit==NULL){
        Logger << kWARNING << " Running PlotNLL() without a RooFitResult is pointless, I'm done" << GEndl ;
        return;
    }

    Logger << kINFO << " ------ Starting PlotNLL with parameters: " << GEndl;
    Logger << kINFO << "  outputPrefix = " << outputPrefix  << GEndl;

    if(!w){
        Logger << kINFO << " Workspace not found, no plotting performed" << GEndl;
        return;
    }

    if(!deactivateBinnedLikelihood) {
        RooFIter iter = w->components().fwdIterator();
        RooAbsArg* arg;
        while ((arg = iter.next())) {
            if (arg->IsA() == RooRealSumPdf::Class()) {
                arg->setAttribute("BinnedLikelihood");
                cout << "Activating binned likelihood attribute for " << arg->GetName() << endl;
            }
        }
    }


    RooSimultaneous* pdf = (RooSimultaneous*) w->pdf("simPdf");

    RooAbsData* data = ( inputData!=0 ? inputData : (RooAbsData*)w->data("obsData") );
    RooCategory* regionCat = (RooCategory*) w->cat("channelCat");
    data->table(*((RooAbsCategory*)regionCat))->Print("v");

    if (lumiConst) {
        RooRealVar* lumi = (RooRealVar*) w->var("Lumi");
        if (lumi!=NULL) lumi->setConstant(lumiConst);
    }

    // Construct an empty simultaneous pdf using category regionCat as index
    RooSimultaneous* simPdfFitRegions = pdf;
    RooDataSet* dataFitRegions = (RooDataSet*) data;

    std::vector<TString> fitRegionsVec = GetRegionsVec(fitRegions, regionCat);

    unsigned int numFitRegions = fitRegionsVec.size();
    std::vector<RooDataSet*> dataVec;
    std::vector<RooAbsPdf*> pdfVec;

    for(unsigned int iVec=0; iVec<numFitRegions; iVec++){
        TString regionCatLabel = fitRegionsVec[iVec];
        if( regionCat->setLabel(regionCatLabel,kTRUE)){
            Logger << kWARNING << " Label '" << regionCatLabel << "' is not a state of channelCat (see Table) " << GEndl;
        } else{
            // dataset for each channel/region/category
            TString dataCatLabel = Form("channelCat==channelCat::%s",regionCatLabel.Data());
            RooDataSet* regionData = (RooDataSet*) data->reduce(dataCatLabel.Data());
            dataVec.push_back(regionData);
            // pdf for each channel/region/category
            RooAbsPdf* regionPdf = (RooAbsPdf*) pdf->getPdf(regionCatLabel.Data());
            pdfVec.push_back(regionPdf);
        }
    }

    if(dataVec.empty()){
        Logger << kERROR << "   NONE OF THE REGIONS ARE SPECIFIED IN DATASET, NO FIT WILL BE PERFORMED" << GEndl;
        return;
    }
    else if(pdfVec.empty()){
        Logger << kERROR << "   NONE OF THE REGIONS ARE SPECIFIED IN SIMULTANEOUS PDF, NO FIT WILL BE PERFORMED" << GEndl;
        return;
    }
    else{
        // Construct a simultaneous dataset for all fit regions
        dataFitRegions = (RooDataSet*) dataVec[0]->Clone("dataFitRegions");
        for(unsigned int jVec=1; jVec<dataVec.size(); jVec++){
            dataFitRegions->append(*dataVec[jVec]);
        }
        // Construct a simultaneous pdf using category regionCat as index
        simPdfFitRegions = new RooSimultaneous("simPdfFitRegions","simultaneous pdf only for fit regions",*regionCat) ;
        for(unsigned int kVec=0; kVec<pdfVec.size(); kVec++){
            simPdfFitRegions->addPdf(*pdfVec[kVec],fitRegionsVec[kVec].Data());
        }
    }


    // find parameters requested for plotting
    RooArgSet* plotParams = new RooArgSet();
    if(plotPars != "") {
        std::vector<TString> parsVec = Tokens(plotPars,",");
        for(unsigned int i=0; i<parsVec.size();i++){
            RooRealVar* var = (RooRealVar*) w->var(parsVec[i]);
            if(var==NULL)  Logger << kWARNING << " Util::PlotNLL() could not find parameter(" << parsVec[i] << ") in workspace while setting up minos" << GEndl;
            else{
                plotParams->add(*var);
            }
        }
    }

    // Get all parameters of result
    RooArgList  fpf =  rFit->floatParsFinal();

    RooStats::ModelConfig* mc = Util::GetModelConfig( w );
    const RooArgSet* globObs = mc->GetGlobalObservables();

    // Create Log Likelihood
    RooAbsReal* nll = simPdfFitRegions->createNLL(*dataFitRegions,NumCPU(2), RooFit::GlobalObservables(*globObs), RooFit::Offset(true)) ;

    unsigned int numParsP = plotParams->getSize();
    if (numParsP==0) { numParsP = fpf.getSize(); }

    unsigned int numPars = fpf.getSize();
    if(numPars<1){
        Logger << kWARNING << "Util::PlotNLL rFit contains no floating parameters" << GEndl;
        return;
    }
    Logger << kINFO << "Util::PlotNLL rFit contains no floating parameters: " << numParsP << GEndl;

    TCanvas* canVec[numPars];

    // loop over all floating pars
    for(unsigned int iPar=0, jPar=0; iPar<numPars ; iPar++){
        RooAbsArg* arg = fpf.at(iPar);

        if ( (plotParams->getSize()>0) && plotParams->find(arg->GetName())==0 ) { continue; }
        if ( !arg->InheritsFrom("RooRealVar") ) { continue; }

        jPar++; // special counter when selecting parameters

        RooRealVar* par = (RooRealVar*) arg;
        TString parName = par->GetName();

        //    if ( parName.Contains("gamma_stat_TR5JMu_cuts_bin_0") ){
        Logger << kINFO << "Plotting NLL for par = " << parName << GEndl;

        // set parameter range to readable range
        double minRange = par->getMin();
        double maxRange = par->getMax();
        if(minRange < 0.){
            par->setMin(-3.);
            par->setMax(3.);
        } else {
            par->setMin(minRange);
            par->setMax(2.);
        }

        RooPlot* frame = par->frame();
        nll->plotOn(frame, ShiftToZero() );
        frame->SetMinimum(0.);
        // To be able to see the 1/2 sigma
        frame->SetMaximum(2.5);

        //const char* curvename = 0;
        RooCurve* curve = (RooCurve*) frame->findObject(nullptr, RooCurve::Class()) ;

        TGraph* nllCurve = static_cast<TGraph*>(curve->Clone());
        nllCurve->SetName(TString("nll_")+parName);

        Double_t curveMax = curve->getYAxisMax();
        // safety for weird RooPlots where curve goes to infinity in first/last bin(s)
        if (curveMax > 0. && !std::isinf(curveMax) && !std::isnan(curveMax) )  { ; } // frame->SetMaximum(curveMax * 2.);
        else if(curveMax > 0. && (std::isinf(curveMax) || std::isnan(curveMax))){

            for(Int_t iBin=1;  iBin < curve->GetN()-1; iBin++){
                Double_t xBin = 0.;
                Double_t yBin = -1.;
                curve->GetPoint(iBin,xBin,yBin) ;
                if(std::isinf(yBin)  || std::isnan(yBin)){
                    curve->RemovePoint(iBin);
                    Logger << kWARNING << " Removing bin = " << iBin  << " as it was either inf or nan from NLL plot for parameter = " << parName<< GEndl;
                    iBin--;
                }
            }

            Int_t iBin = 1;
            Double_t xFirstBin = 0.;
            Double_t yFirstBin = -1.;
            while ( (yFirstBin<0 || std::isinf(yFirstBin)  || std::isnan(yFirstBin) )&& iBin < curve->GetN()-1){
                iBin++;
                curve->GetPoint(iBin,xFirstBin,yFirstBin) ;
                if(std::isinf(yFirstBin)  || std::isnan(yFirstBin)){
                    curve->RemovePoint(iBin);
                    Logger << kWARNING << " Removing bin = " << iBin  << " as it was either inf or nan from NLL plot for parameter = " << parName<< GEndl;
                }
            }
            iBin = curve->GetN()-1;
            Double_t xLastBin = 0.;
            Double_t yLastBin = -1.;
            while ( (yLastBin < 0 || std::isinf(yLastBin) || std::isnan(yLastBin) ) && iBin >0){
                iBin--;
                curve->GetPoint(iBin,xLastBin,yLastBin) ;
                if(std::isinf(yLastBin)  || std::isnan(yLastBin)){
                    curve->RemovePoint(iBin);
                    Logger << kWARNING << " Removing bin = " << iBin  << " as it was either inf or nan from NLL plot for parameter = " << parName<< GEndl;
                }
            }
            curveMax = yLastBin>yFirstBin ? yLastBin : yFirstBin;
        }

        // plot cosmetics
        int firstbin = frame->GetXaxis()->GetFirst();
        int lastbin = frame->GetXaxis()->GetLast();
        double xmax = frame->GetXaxis()->GetBinUpEdge(lastbin) ;
        double xmin = frame->GetXaxis()->GetBinLowEdge(firstbin) ;

        TLine* l1 = new TLine(xmin, 2., xmax, 2.);
        TLine* l2 = new TLine(xmin, 0.5, xmax, 0.5);

        l1->SetLineStyle(3);
        l2->SetLineStyle(3);

        frame->addObject(l1);
        frame->addObject(l2);

        RooAbsReal* pll(0);
        TGraph *pllCurve = 0;
        if(plotPLL) {
            pll = nll->createProfile(*par) ;
            pll->plotOn(frame, LineColor(kRed), LineStyle(kDashed), NumCPU(4));
            //const char* curvename = 0;
            RooCurve* curve = (RooCurve*) frame->findObject(nullptr, RooCurve::Class()) ;

            pllCurve = static_cast<TGraph*>(curve->Clone());
            pllCurve->SetName(TString("nll_")+parName);
        }


        TString canName=Form("can_NLL_%s_%s_%s", outputPrefix.Data(), rFit->GetName(), parName.Data());
        canVec[iPar] = new TCanvas(canName, canName, 600, 600);
        canVec[iPar]->cd();
        frame->Draw();

        TLegend* leg = new TLegend(0.55, 0.65, 0.85, 0.9, "");
        leg->SetFillStyle(0);
        leg->SetFillColor(0);
        leg->SetBorderSize(0);
        TLegendEntry* entry=leg->AddEntry("", "NLL", "l") ;
        entry->SetLineColor(kBlue);
        if(plotPLL) {
            entry=leg->AddEntry("", "PLL", "l") ;
            entry->SetLineColor(kRed);
            entry->SetLineStyle(kDashed);
        }
        leg->Draw();

        // update plot
        canVec[iPar]->Draw();

        // reset parameter range to previous values
        par->setMin(minRange);
        par->setMax(maxRange);

        if (plotPLL) {
            delete pll; pll=0;
        }

        canVec[iPar]->SaveAs("results/"+anaName+"/"+canName+".pdf");
        canVec[iPar]->SaveAs("results/"+anaName+"/"+canName+".C");
        canVec[iPar]->SaveAs("results/"+anaName+"/"+canName+".eps");

        TString fname("results/"+anaName+"/"+canName+".root");
        TFile *f = TFile::Open(fname, "RECREATE");
        nllCurve->Write();
        if(pllCurve) { pllCurve->Write(); }
        f->Close();
        //  }

    }

    delete nll ;

}

//_____________________________________________________________________________
TH2D* Util::PlotCorrelationMatrix(RooFitResult* rFit, TString anaName,  bool ReduceMatrix){


    if(rFit==NULL){
        Logger << kWARNING << "Running PlotCorrelationMatrix() without a RooFitResult is pointless, I'm done" << GEndl ;
        throw 1 ;
    }

    Logger << kINFO << " ------ Starting PlotCorrelationMatrix() " << GEndl;

    Int_t numPars = rFit->floatParsFinal().getSize();

    TString canName = Form("c_corrMatrix_%s",rFit->GetName());
    TCanvas* c_corr = new TCanvas(canName.Data(),canName.Data(),600,400); // .c_str())

    Double_t orig_MarkerSize =  gStyle->GetMarkerSize();
    Int_t orig_MarkerColor =  gStyle->GetMarkerColor();
    const char* orig_PaintTextFormat = gStyle->GetPaintTextFormat() ;
    Double_t orig_LabelSize = gStyle->GetLabelSize();

    gStyle->SetPalette(105) ;
    gStyle->SetMarkerSize(1.45);
    gStyle->SetMarkerColor(kWhite);
    gStyle->SetPaintTextFormat("4.2f") ;

    if(numPars<5)    gStyle->SetMarkerSize(1.4);
    else if(numPars<10)    gStyle->SetMarkerSize(1.1);
    else if(numPars<20)    gStyle->SetMarkerSize(0.85);
    else if(numPars<40)    gStyle->SetMarkerSize(0.5);
    else     gStyle->SetMarkerSize(0.25);

    TH2D* h_corr = (TH2D*) rFit->correlationHist(Form("h_corr_%s",rFit->GetName()));
    int nbins = h_corr->GetNbinsX();

    for (int xbin=1; xbin<nbins+1; xbin++) {
        TString labelX = h_corr->GetXaxis()->GetBinLabel(xbin);
        if(labelX.Contains("Lumi") || labelX.Contains("mcstat") || labelX.Contains("gamma_stat")){
            labelX.ReplaceAll("gamma_shape_mcstat","#gamma");
            labelX.ReplaceAll("gamma_stat","#gamma");
            labelX.ReplaceAll("_cuts_bin_0","");}
        if(labelX.Contains("mu")){
            labelX.ReplaceAll("mu","#mu");}
        if(labelX.Contains("alpha")){
            labelX.ReplaceAll("alpha","#alpha");}
        h_corr->GetXaxis()->SetBinLabel(xbin,labelX);
    }

    for (int ybin=1; ybin<nbins+1; ybin++) {
        TString labelY = h_corr->GetYaxis()->GetBinLabel(ybin);
         if(labelY.Contains("Lumi") || labelY.Contains("mcstat") || labelY.Contains("gamma_stat")){
            labelY.ReplaceAll("gamma_shape_mcstat","#gamma");
            labelY.ReplaceAll("gamma_stat","#gamma");
            labelY.ReplaceAll("_cuts_bin_0","");}
         if(labelY.Contains("mu")){
            labelY.ReplaceAll("mu","#mu");}
         if(labelY.Contains("alpha")){
            labelY.ReplaceAll("alpha","#alpha");}
        h_corr->GetYaxis()->SetBinLabel(ybin,labelY);
    }

    if (ReduceMatrix) {
      // Cleanup corrMattrix from rows and columns with content less then corrThres
      vector <int> rm_idx; rm_idx.clear();
      double corrThresh[3] = {0.01,0.1,0.2};
      int index_x=0, index_y=0, Thresh1Counter;//, Thresh0Counter, Thresh2Counter;
      bool fillHistY, fillHistX;

      // Look for rows and columns indices to remove
      for (int ix=1; ix<nbins+1; ix++) {
        //Thresh0Counter = 0;
        Thresh1Counter = 0;
        //Thresh2Counter = 0;
        for (int iy=1; iy<nbins+1; iy++) {
          if (ix==((nbins+1)-iy)) continue;
          //if (fabs(h_corr->GetBinContent(ix,iy))>=corrThresh[0]) Thresh0Counter++;
          if (fabs(h_corr->GetBinContent(ix,iy))>=corrThresh[1]) Thresh1Counter++;
          //if (fabs(h_corr->GetBinContent(ix,iy))>=corrThresh[2]) Thresh2Counter++;
        }
        //if ( Thresh0Counter<(nbins+1)/5. && Thresh1Counter<(nbins+1)/10. && Thresh2Counter==0 ) rm_idx.push_back(ix);
        if ( Thresh1Counter==0 ) rm_idx.push_back(ix);
      }

      int nrm_idx = rm_idx.size();
      int newSize = numPars-nrm_idx;
      TH2D* h_corr_reduced = new TH2D("h_corr_reduced","h_corr_reduced",newSize,0,newSize,newSize,0,newSize);

      // Copy original matrix to the new without empty rows and columns
      for (int ix=1; ix<nbins+1; ix++) {
        index_y=0;
        fillHistX=false;
        for (int iy=1; iy<nbins+1; iy++) {
          fillHistY=true;
          for (int irm=0; irm<nrm_idx; irm++) {
            if ( ix==rm_idx.at(irm) || iy==((nbins+1)-rm_idx.at(irm)) ) fillHistY=false;
          }
          if (fillHistY) {
            h_corr_reduced->Fill(index_x,index_y,h_corr->GetBinContent(ix,iy));
            index_y++;
            if (index_x==0) h_corr_reduced->GetYaxis()->SetBinLabel(index_y,h_corr->GetYaxis()->GetBinLabel(iy));
            fillHistX=true;
          }
        }
        if (fillHistX) {
          index_x++;
          h_corr_reduced->GetXaxis()->SetBinLabel(index_x,h_corr->GetXaxis()->GetBinLabel(ix));
        }
      }

      h_corr = h_corr_reduced;
      numPars = newSize;
    }

    Double_t labelSize = orig_LabelSize;
    if(numPars<5) labelSize = 0.05;
    else if(numPars<10)   labelSize = 0.04;
    else if(numPars<20)   labelSize = 0.025;
    else if(numPars<40)   labelSize = 0.02;
    else labelSize = 0.015;

    h_corr->GetXaxis()->SetLabelSize(labelSize);
    h_corr->GetYaxis()->SetLabelSize(labelSize);
    h_corr->GetXaxis()->LabelsOption("v");

    gPad->SetLeftMargin(0.18);
    gPad->SetRightMargin(0.13);

    gStyle->SetMarkerSize(orig_MarkerSize);
    gStyle->SetMarkerColor(orig_MarkerColor);
    gStyle->SetPaintTextFormat(orig_PaintTextFormat) ;
    gStyle->SetLabelSize(orig_LabelSize);
    gStyle->SetOptStat(00000000);

    h_corr->Draw("colz");
    h_corr->Draw("textsame");

    c_corr->SaveAs("results/"+anaName+"/"+canName+".pdf");
    c_corr->SaveAs("results/"+anaName+"/"+canName+".eps");

    return h_corr;

}

//_____________________________________________________________________________
TH2D* Util::GetCorrelations(RooFitResult* rFit, double threshold, TString anaName) {
    TH2D* h_corr = Util::PlotCorrelationMatrix(rFit, anaName);

    unsigned int nBinsX = h_corr->GetNbinsX();
    unsigned int nBinsY = h_corr->GetNbinsY();

    for(unsigned int iBinY = 1; iBinY <= nBinsY; iBinY++){
        for(unsigned int iBinX = 1; iBinX <= nBinsX && iBinX <= (nBinsX-iBinY); iBinX++){
            if(fabs(h_corr->GetBinContent(iBinX,iBinY)) > threshold){
                Logger << kWARNING << " High correlation coefficient between:   par1 = " << h_corr->GetXaxis()->GetBinLabel(iBinX) << "  and par2 = "
                    << h_corr->GetYaxis()->GetBinLabel(iBinY) << " "
                    << " val = " << h_corr->GetBinContent(iBinX,iBinY) << GEndl;
            }
        }
    }

    return h_corr;
}



//_____________________________________________________________________________
vector<TString> Util::Tokens(TString aline,TString aDelim)
{
    Int_t i;
    TObjArray* InObjArray;
    TObjString* os;
    TString s;
    vector<TString> OutStringVec;
    OutStringVec.clear();

    InObjArray=aline.Tokenize(aDelim);
    for ( i=0; i<InObjArray->GetEntriesFast(); i++ )
    {
        os=(TObjString*)InObjArray->At(i);
        s=os->GetString();
        OutStringVec.push_back(s);
    }
    return OutStringVec;
}


//_____________________________________________________________________________
vector<TString> Util::TokensALL(RooCategory* cat)
{

    vector<TString> OutStringVec;
    OutStringVec.clear();
    TIterator* iter = cat->typeIterator() ;
    RooCatType* catType ;
    while( (catType = (RooCatType*) iter->Next())) {
        TString regionCatLabel = catType->GetName();
        OutStringVec.push_back(regionCatLabel);
    }

    return OutStringVec;

}



//__________________________________________________________________________________________________________________________________________________________
Double_t Util::GetComponentFrac(RooWorkspace* w, const char* Component, const char* RRSPdfName, RooRealVar* observable){

    // Components are now the shape (func) * scaleFactor (coef)
    TString coefName = TString(Component).ReplaceAll("_shapes", "_scaleFactors");

    RooAbsReal*  i_RRSPdf = ((RooAbsPdf*)w->pdf(RRSPdfName))->createIntegral(RooArgSet(*observable));
    RooProduct* func_prod = dynamic_cast<RooProduct*>(w->obj(Component)->Clone());
    RooAbsReal* i_coeficient = dynamic_cast<RooAbsReal*>(w->obj(coefName));
    func_prod->addTerm(i_coeficient);   

    RooAbsReal*  i_component  =   func_prod->createIntegral(RooArgSet(*observable));

    // Get total integral and integral of component
    Double_t Int_RRSPdf = i_RRSPdf->getVal();
    Double_t Int_func = i_component->getVal();
    Double_t Int_coef = i_coeficient->getVal();

    Logger << kDEBUG << "GetComponnentFrac: component = "<<Component << ", RRSPdf val = " << Int_RRSPdf << ", func val = " << Int_func << ", coef val = " << Int_coef << GEndl;

    Double_t componentFrac = 0.;
    if(Int_RRSPdf != 0.) componentFrac =  Int_func / Int_RRSPdf; 

    delete  i_RRSPdf;
    delete  i_component;
    delete func_prod;

    return componentFrac;
}



//________________________________________________________________________________________________
RooWorkspace* Util::GetWorkspaceFromFile( const TString& infile, const TString& wsname ) {
    TFile* file = TFile::Open(infile.Data(), "READ");
    if (!file || file->IsZombie()) {
        Logger << kERROR << "Cannot open file: " << infile << GEndl;
        return NULL;
    }
    file->cd();

    TObject* obj = file->Get( wsname.Data() ) ;
    if (obj==0) {
        Logger << kERROR << "Cannot open workspace <" << wsname << "> in file <" << infile << ">" << GEndl;
        file->Close();
        return NULL;
    }

    if (obj->ClassName()!=TString("RooWorkspace")) { // much faster than dynamic cast
        Logger << kERROR << "Cannot open workspace <" << wsname << "> in file <" << infile << ">" << GEndl;
        file->Close();
        return NULL;
    }

    RooWorkspace* w = (RooWorkspace*)( obj );
    if ( w==0 ) {
        Logger << kERROR << "Cannot open workspace <" << wsname << "> in file <" << infile << ">" << GEndl;
        file->Close();
        return NULL;
    }

    return w;
}


//________________________________________________________________________________________________
RooStats::ModelConfig* Util::GetModelConfig( const RooWorkspace* w, const TString& mcName  ) {
    if (w==0) {
        Logger << kERROR << "Workspace is a null pointer." << GEndl;
        return NULL;
    }

    TObject* obj = w->obj( mcName.Data() ) ;
    if (obj==0) {
        Logger << kERROR << "Cannot open ModelConfig <" << mcName << "> from workspace." << GEndl;
        return NULL;
    }

    RooStats::ModelConfig* mc = (RooStats::ModelConfig *)(obj);
    if ( mc==0 ) {
        Logger << kERROR << "Cannot open ModelConfig <" << mcName << "> from workspace" << GEndl;
        return NULL;
    }

    return mc;
}


//________________________________________________________________________________________________
    RooRealVar*
Util::GetPOI( const RooWorkspace* w  )
{
    if(w==0){
        Logger << kERROR << "Input workspace is null!" << GEndl;
        return NULL;
    }

    RooStats::ModelConfig* mc = Util::GetModelConfig(w);
    if(mc==0){
        Logger << kERROR << "ModelConfig is null!" << GEndl;
        return NULL;
    }

    const RooArgSet* poiSet = mc->GetParametersOfInterest();
    RooRealVar* firstPOI = ( poiSet!=0 ? (RooRealVar*) poiSet->first() : 0 );

    return firstPOI;
}


//________________________________________________________________________________________________
    RooFitResult*
Util::doFreeFit( RooWorkspace* w, RooDataSet* inputdata, const bool& verbose, const bool& resetAfterFit, bool hesse, Bool_t minos, TString minosPars )
{
    // fit to reset the workspace

    if(w==0){
        Logger << kERROR << "Input workspace is null!" << GEndl;
        return NULL;
    }

    if(!deactivateBinnedLikelihood) {
        RooFIter iter = w->components().fwdIterator();
        RooAbsArg* arg;
        while ((arg = iter.next())) {
            if (arg->IsA() == RooRealSumPdf::Class()) {
                arg->setAttribute("BinnedLikelihood");
                cout << "Activating binned likelihood attribute for " << arg->GetName() << endl;
            }
        }
    }

    RooStats::ModelConfig* mc = Util::GetModelConfig(w);

    if(mc==0){
        Logger << kERROR << "ModelConfig is null!" << GEndl;
        return NULL;
    }

    /// get pdf and dataset
    RooDataSet* data(0);
    if (inputdata!=0) {
        data = inputdata;
    }
    else
        data = dynamic_cast<RooDataSet*>(w->data("obsData")); // default: fit to data
    if (verbose) data->Print();

    RooAbsPdf* pdf = mc->GetPdf();

    if((data==0)||(pdf==0)){
        Logger << kERROR << "data set or pdf not found" <<GEndl;
        return NULL;
    }

    if (resetAfterFit) {
        // save snapshot before any fit has been done
        RooArgSet* params = (RooArgSet*) pdf->getParameters(*data) ;
        if(!w->loadSnapshot("snapshot_paramsVals_initial")) {
            w->saveSnapshot("snapshot_paramsVals_initial",*params);
        } else {
            Logger << kWARNING << "Snapshot 'snapshot_paramsVals_initial' already exists in  workspace, will not overwrite it" << GEndl;
        }
    }

    /////////////////////////////////////////////////////////////

    RooArgSet* allParams = pdf->getParameters(data);
    RooStats::RemoveConstantParameters(allParams);

    const RooArgSet* globObs = mc->GetGlobalObservables();

    RooAbsReal* nll = (RooNLLVar*) pdf->createNLL(*data, RooFit::GlobalObservables(*globObs), RooFit::Offset(true));

    // find parameters requested for Minos
    RooArgSet* minosParams = new RooArgSet();
    if(minosPars != "" && minos && minosPars != "all"  && minosPars != "ALL"){
      std::vector<TString> parsVec = Tokens(minosPars,",");
      for(unsigned int i=0; i<parsVec.size();i++){
        RooRealVar* var = (RooRealVar*) w->var(parsVec[i]);
        if(var==NULL)  Logger << kWARNING << " Util::doFreeFit()   could not find parameter(" << parsVec[i] << ") in workspace while setting up minos" << GEndl;
        else{
          minosParams->add(*var);
        }
      }
    }


    int minimPrintLevel = verbose;

    RooMinimizer minim(*nll);
    int strategy = ROOT::Math::MinimizerOptions::DefaultStrategy();
    minim.setStrategy( strategy);

    // use tolerance - but never smaller than 1 (default in RooMinimizer)
    double tol =  ROOT::Math::MinimizerOptions::DefaultTolerance();
    tol = std::max(tol,1.0); // 1.0 is the minimum value used in RooMinimizer
    minim.setEps( tol );

    //LM: RooMinimizer.setPrintLevel has +1 offset - so subtruct  here -1
    minim.setPrintLevel(minimPrintLevel-1);
    minim.optimizeConst(2);

    TString minimizer = "Minuit2"; //ROOT::Math::MinimizerOptions::DefaultMinimizerType();
    TString algorithm = ROOT::Math::MinimizerOptions::DefaultMinimizerAlgo();

    int status = -1;

    // require covQual = 3 from any fit while retrying?
    bool requireGoodCovQual = true;

    Logger << kINFO << "Util::doFreeFit()  ........ using " << minimizer << " / " << algorithm
        << " with strategy  " << strategy << " and tolerance " << tol << GEndl;

    for (int tries = 1, maxtries = 5; tries <= maxtries; ++tries) {
        //   status = minim.minimize(fMinimizer, ROOT::Math::MinimizerOptions::DefaultMinimizerAlgo().c_str());
        status = minim.minimize(minimizer, algorithm);

        if (status%1000 == 0) {  // ignore erros from Improve

            // if desired, is the covariance matrix OK?
            std::unique_ptr<RooFitResult> res(minim.save());
            if(!requireGoodCovQual || res->covQual() == 3){
                break;
            } else {
                Logger << kINFO << " status OK but covariance matrix not at full accuracy, retrying" << GEndl;
            }
        }

        if (tries == 1) {
            Logger << kINFO << "    ----> Doing a re-scan first" << GEndl;
            minim.minimize(minimizer,"Scan");
        } else if (tries == 2) {
            if (strategy == 0) {
                Logger << kINFO << "    ----> trying with strategy = 1" << GEndl;
                strategy = 1;
                minim.setStrategy(strategy);
            } else {
                tries++; // skip this trial if stratehy is already 1
            }
        } else if (tries == 3) {
            if (strategy == 1) {
                Logger << kINFO << "    ----> trying with strategy = 2" << GEndl;
                strategy = 2;
                minim.setStrategy(strategy);
            } else {
                tries++; // skip this trial if stratehy is already 2
            }
        } else if (tries == 4) {
            Logger << kINFO << "    ----> trying with improve" << GEndl;
            minimizer = "Minuit";
            algorithm = "migradimproved";
        }
    }

    std::unique_ptr<RooFitResult> res(minim.save());
    if( requireGoodCovQual && res->covQual() != 3 && !hesse ) {
        Logger << kINFO << "status OK but covariance matrix not at full accuracy, will retry with HESSE to improve" << GEndl;
        hesse = true;
    }

    RooFitResult * result = 0;

    if (status%100 == 0 ) { // ignore errors in Hesse or in Improve
        // only calculate minos errors if fit with Migrad converged
        Logger << kINFO <<  "status: " << status << ", hesse = " << hesse <<" minos = " << minos << " minosPars = " << minosPars << GEndl;

        if(hesse || minos ) {
            minim.hesse();
        }

        if(minos && (minosPars == "all" || minosPars == "ALL")) {
            minim.minos();
        } else if(minos && minosPars != "" && minosParams->getSize() > 0) {
            minim.minos(*minosParams);
        }

        // save fit result
        // ignore errors in Hesse or in Improve if minos option not activated
        result  = minim.save();
    }
    else {
        Logger << kERROR << "FIT FAILED !- return a NaN NLL " << GEndl;
    }

    //////////////////////////////////////////////////////////////

    if (resetAfterFit) {
        w->loadSnapshot("snapshot_paramsVals_initial");
    }

    return result;
}


//________________________________________________________________________________________________
    RooMCStudy*
Util::GetMCStudy( const RooWorkspace* w )
{
    if (w==0) {
        Logger << kERROR << "Input workspace is null. Return." << GEndl;
        return NULL;
    }

    RooStats::ModelConfig* mc = Util::GetModelConfig(w);

    if(mc==0){
        Logger << kERROR << "ModelConfig is null!" << GEndl;
        return NULL;
    }

    RooAbsPdf* pdf = mc->GetPdf();
    const RooArgSet* obsset = mc->GetObservables();

    if((pdf==0)||(obsset==0)){
        Logger << kERROR << "pdf or observables not found" <<GEndl;
        return NULL;
    }

    // caller owns mcstudy
    return ( new RooMCStudy( *pdf, *obsset, RooFit::Save(true) ) ) ;
}





//________________________________________________________________________________________________
// ATLAS specific - FIXME ; remove for public release
void Util::ATLASLabel(Double_t x,Double_t y,const char* text,Color_t color)
{

    TLatex l;
    l.SetNDC();
    l.SetTextFont(72);
    l.SetTextColor(color);

    double delx = 0.115*696*gPad->GetWh()/(472*gPad->GetWw());

    l.DrawLatex(x,y,"ATLAS");
    if (text) {
        TLatex p;
        p.SetNDC();
        p.SetTextFont(42);
        p.SetTextColor(color);
        p.DrawLatex(x+delx,y,text);
        //    p.DrawLatex(x,y,"#sqrt{s}=900GeV");
    }
}


//________________________________________________________________________________________________
void Util::AddText(Double_t x,Double_t y,char* text,Color_t color)
{

    TLatex l;
    l.SetNDC();
    l.SetTextFont(72);
    l.SetTextColor(color);

    double delx = 0.115*696*gPad->GetWh()/(472*gPad->GetWw());

    if (text) {
        TLatex p;
        p.SetNDC();
        p.SetTextFont(42);
        p.SetTextColor(color);
        p.DrawLatex(x+delx,y,text);
    }
}

void Util::AddTextLabel(Double_t x, Double_t y, const char* text, Color_t color)
{

    TLatex l;
    l.SetNDC();
    l.SetTextFont(72);
    l.SetTextColor(color);

    double delx = 0.115 * 696 * gPad->GetWh() / (472 * gPad->GetWw());

    if (text) {
        TLatex p;
        p.SetNDC();
        p.SetTextFont(42);
        p.SetTextColor(color);
        p.DrawLatex(x + delx, y, text);
    }
}

//_____________________________________________________________________________
RooAbsReal* Util::GetComponent(RooWorkspace* w, TString component, TString region, bool exactRegionName, TString rangeName){

    std::vector<TString> componentVec = Tokens(component,",");
    if(componentVec.size() <1) { Logger << kWARNING << " componentVec.size() < 1, for components = " << component << GEndl; }

    if(w==NULL){
        Logger << kERROR << " Workspace not found, no GetComponent performed" << GEndl;
        return NULL;
    }

    RooCategory* regionCat = (RooCategory*) w->cat("channelCat");
    TString regionFullName;
    if(exactRegionName){
        Logger << kINFO << "GetComponent(): using exact region name: " << region << GEndl;
        regionFullName = region;
    } else {
        regionFullName = GetFullRegionName(regionCat, region);
    }

    RooSimultaneous* pdf = (RooSimultaneous*) w->pdf("simPdf");
    RooAbsPdf* regionPdf = (RooAbsPdf*) pdf->getPdf(regionFullName.Data());

    RooAbsData* data = (RooAbsData*)w->data("obsData");
    TString dataCatLabel = Form("channelCat==channelCat::%s",regionFullName.Data());
    RooAbsData* regionData = (RooAbsData*) data->reduce(dataCatLabel.Data());

    if(regionPdf==NULL || regionData==NULL){
        Logger << kERROR << " Either the Pdf or the Dataset do not have an appropriate state for the region = " << region << ", check the Workspace file" << GEndl;
        Logger << kERROR << " regionPdf = " << regionPdf << "   regionData = " << regionData << GEndl;
        return NULL;
    }
    RooRealVar* regionVar =(RooRealVar*) ((RooArgSet*) regionPdf->getObservables(*regionData))->find(Form("obs_x_%s",regionFullName.Data()));

    // find the correct RooProduct
    vector<TString> regionCompNameVec = GetAllComponentNamesInRegion(regionFullName, regionPdf);
    RooArgList compFuncList;
    RooArgList compCoefList;
    for(unsigned int iReg=0; iReg<regionCompNameVec.size(); iReg++){
        for(unsigned int iComp=0; iComp< componentVec.size(); iComp++){
            Logger << kDEBUG << " GetComponent: regionCompNameVec[" << iReg << "] = " << regionCompNameVec[iReg] << " componentVec[" << iComp << "] = " << componentVec[iComp] << GEndl;
            TString target = componentVec[iComp]+"_"+regionFullName;
            if(  regionCompNameVec[iReg].Contains(target.Data())) {
                TString func_name = regionCompNameVec[iReg];
                TString coef_name = func_name;
                coef_name.ReplaceAll("_shapes", "_scaleFactors");
                compFuncList.add(*(RooProduct*)w->obj(func_name));
                compCoefList.add(*(RooProduct*)w->obj(coef_name));
            }
        }
    }

    if (compFuncList.getSize()==0 || compCoefList.getSize()==0 || compCoefList.getSize()!=compFuncList.getSize()){
        Logger << kERROR << " Something wrong with compFuncList or compCoefList in Util::GetComponent(w," << component << "," << region
            << ") " << GEndl << "         compFuncList.getSize() = " << compFuncList.getSize() << " compCoefList.getSize() = " << compCoefList.getSize() << GEndl;
        return NULL;
    }

    TString compName = "comps";
    for(unsigned int iVec=0; iVec<componentVec.size(); iVec++){
        compName += "_" + componentVec[iVec];
    }

    RooRealSumPdf* compRRS = new RooRealSumPdf(Form("RRS_region_%s_%s",region.Data(),compName.Data()),Form("RRS_region_%s_%s",region.Data(),compName.Data()),compFuncList,compCoefList);
    if(!compRRS){
        Logger << kERROR << " Cannot create a RooRealSumPdf in Util::GetComponent() "<< GEndl;
        return NULL;
    }

    RooAbsReal* compFunc;
    if(rangeName==""){
      compFunc = compRRS->createIntegral(RooArgSet(*regionVar));
    }
    else{
      compFunc = compRRS->createIntegral(RooArgSet(*regionVar),rangeName);
    }


    if(compFunc == NULL){
        Logger << kERROR << " compRooProduct not found for region(" << regionFullName << "), component(" << component << ")   RETURNING COMPONENTS WILL BE WRONG " << GEndl ;
        return NULL;
    }

    RooFormulaVar* form_frac = new RooFormulaVar("form_fracError","@0",RooArgList(*compFunc));
    if(rangeName==""){
      form_frac->SetName(Form("form_frac_region_%s_%s",region.Data(),compName.Data()));
      form_frac->SetTitle(Form("form_frac_region_%s_%s",region.Data(),compName.Data()));
    }
    else{
      form_frac->SetName(Form("form_frac_region_%s_%s_%s",region.Data(),compName.Data(),rangeName.Data()));
      form_frac->SetTitle(Form("form_frac_region_%s_%s_%s",region.Data(),compName.Data(),rangeName.Data()));
    }


    Logger << kINFO << " Adding " << form_frac->GetName() << " to workspace" << GEndl;
    w->import( *form_frac,kTRUE);
    gDirectory->Add(form_frac);

    return form_frac;

}


//_____________________________________________________________________________
Double_t Util::GetComponentFracInRegion(RooWorkspace* w, TString component, TString region){

    std::vector<TString> componentVec = Tokens(component,",");
    if(componentVec.size() <1) {
        Logger << kWARNING << " componentVec.size() < 1, for components = " << component << GEndl;
    }

    if(w==NULL){
        Logger << kERROR << " Workspace not found, no GetComponent performed" << GEndl;
        return 0;
    }

    RooCategory* regionCat = (RooCategory*) w->cat("channelCat");
    TString regionFullName = GetFullRegionName(regionCat, region);

    RooSimultaneous* pdf = (RooSimultaneous*) w->pdf("simPdf");
    RooAbsPdf* regionPdf = (RooAbsPdf*) pdf->getPdf(regionFullName.Data());

    RooAbsData* data = (RooAbsData*)w->data("obsData");
    TString dataCatLabel = Form("channelCat==channelCat::%s",regionFullName.Data());
    RooAbsData* regionData = (RooAbsData*) data->reduce(dataCatLabel.Data());

    if(regionPdf==NULL || regionData==NULL){
        Logger << kERROR << " Either the Pdf or the Dataset do not have an appropriate state for the region = " << region << ", check the Workspace file" << GEndl;
        Logger << kERROR << " regionPdf = " << regionPdf << "   regionData = " << regionData << GEndl;
        return 0;
    }

    RooRealVar* regionVar =(RooRealVar*) ((RooArgSet*) regionPdf->getObservables(*regionData))->find(Form("obs_x_%s",regionFullName.Data()));

    // Check if component isn't found
    vector<TString> regionCompNameVec = GetAllComponentNamesInRegion(regionFullName, regionPdf);
    bool found_comp = false;
    for(unsigned int iReg=0; iReg<regionCompNameVec.size(); iReg++){
        for(unsigned int iComp=0; iComp< componentVec.size(); iComp++){
            TString target = componentVec[iComp]+"_"+regionFullName;
            if (regionCompNameVec[iReg].Contains(target.Data())) found_comp = true;
        }
    }

    if(!found_comp){
        Logger << kERROR << "Something went wrong, no components found for "<<component.Data()<<GEndl;
        return 0;
    }

    // get the full RRSPdf of this region
    TString RRSPdfName = Form("%s_model",regionFullName.Data());

    TString compName = "comps";
    for(unsigned int iVec=0; iVec<componentVec.size(); iVec++){
        compName += "_" + componentVec[iVec];
    }



    double componentFrac = 0.;
    for(unsigned int iReg=0; iReg<regionCompNameVec.size(); iReg++){
        for(unsigned int iComp=0; iComp< componentVec.size(); iComp++){
            TString target = componentVec[iComp]+"_"+regionFullName;
            if(  regionCompNameVec[iReg].Contains(target.Data())) {
                componentFrac += GetComponentFrac(w,regionCompNameVec[iReg],RRSPdfName,regionVar) ;
            }
        }
    }

    return componentFrac;

}


//_____________________________________________________________________________
RooAbsPdf* Util::GetRegionPdf(RooWorkspace* w, TString region){  //, unsigned int bin){

    if(w==NULL){
        Logger << kERROR << " Workspace not found, no GetRegionPdf performed" << GEndl;
        return NULL;
    }

    RooCategory* regionCat = (RooCategory*) w->cat("channelCat");
    TString regionFullName = GetFullRegionName(regionCat, region);

    RooSimultaneous* pdf = (RooSimultaneous*) w->pdf("simPdf");
    RooAbsPdf* regionPdf = (RooAbsPdf*) pdf->getPdf(regionFullName.Data());

    if(regionPdf==NULL){
        Logger << kERROR << " The Simultaneous Pdf  does not have an appropriate state for the region = " << region << ", check the Workspace file" << GEndl;
        Logger << kERROR << " regionPdf = " << regionPdf << GEndl;
        return NULL;
    }

    return regionPdf;

}


//_____________________________________________________________________________
RooRealVar* Util::GetRegionVar(RooWorkspace* w, TString region){

    if(w==NULL){
        Logger << kERROR << " Workspace not found, no GetComponent performed" << GEndl;
        return NULL;
    }

    RooCategory* regionCat = (RooCategory*) w->cat("channelCat");
    TString regionFullName = GetFullRegionName(regionCat, region);

    RooSimultaneous* pdf = (RooSimultaneous*) w->pdf("simPdf");
    RooAbsPdf* regionPdf = (RooAbsPdf*) pdf->getPdf(regionFullName.Data());

    RooAbsData* data = (RooAbsData*)w->data("obsData");
    TString dataCatLabel = Form("channelCat==channelCat::%s",regionFullName.Data());
    RooAbsData* regionData = (RooAbsData*) data->reduce(dataCatLabel.Data());

    if(regionPdf==NULL || regionData==NULL){
        Logger << kERROR << " Either the Pdf or the Dataset do not have an appropriate state for the region = " << region << ", check the Workspace file" << GEndl;
        Logger << kERROR << " regionPdf = " << regionPdf << "   regionData = " << regionData << GEndl;
        return NULL;
    }
    RooRealVar* regionVar =(RooRealVar*) ((RooArgSet*) regionPdf->getObservables(*regionData))->find(Form("obs_x_%s",regionFullName.Data()));

    return regionVar;

}


//__________________________________________________________________________________________
TString Util::GetFullRegionName(RooCategory* regionCat,  TString regionShortName){

    std::vector<TString> regionsAllVec = TokensALL(regionCat);

    TString regionFullName;
    Int_t foundReg = 0;
    for(unsigned int iReg=0; iReg<regionsAllVec.size(); iReg++){
        if( regionsAllVec[iReg].Contains(regionShortName) && foundReg==0) {
            regionFullName = regionsAllVec[iReg];
            foundReg++;
        }
        else if( regionsAllVec[iReg].Contains(regionShortName) && foundReg>0){
            foundReg++;
        }
    }

    if(foundReg>1)
        Logger << kWARNING << "Util.GetFullRegionName() found more then one region in workspace with shortname = " << regionShortName
            << " \n Please use full region names (like WREl_meffInc) insted of shortnames (like WR) " << GEndl;

    return regionFullName;
}

//__________________________________________________________________________________________
vector<TString> Util::GetAllComponentNamesInRegion(TString region, RooAbsPdf* regionPdf){

    TString RRSPdfName = Form("%s_model",region.Data());
    RooRealSumPdf* RRSPdf = (RooRealSumPdf*) regionPdf->getComponents()->find(RRSPdfName);

    if(RRSPdf==NULL){
        Logger << kERROR << " Util::GetAllComponentNamesInRegion() cannot find a RooRealSumPdf named " <<  RRSPdfName << GEndl ;
        vector<TString> vec;
        return vec;
    }

    RooArgList RRSComponentsList =  RRSPdf->funcList();

    RooLinkedListIter iter = RRSComponentsList.iterator() ;
    RooProduct* component;
    vector<TString> compNameVec;
    compNameVec.clear();

    while( (component = (RooProduct*) iter.Next())) {
        TString  componentName = component->GetName();
        compNameVec.push_back(componentName);
    }

    return compNameVec;
}




//__________________________________________________________________________________________
vector<double> Util::GetAllComponentFracInRegion(RooWorkspace* w, TString region, RooAbsPdf* regionPdf, RooRealVar* obsRegion){

    TString RRSPdfName = Form("%s_model",region.Data());
    RooRealSumPdf* RRSPdf = (RooRealSumPdf*) regionPdf->getComponents()->find(RRSPdfName);

    RooArgList RRSComponentsList =  RRSPdf->funcList();

    RooLinkedListIter iter = RRSComponentsList.iterator() ;
    RooProduct* component;
    vector<double> compFracVec;
    compFracVec.clear();

    while( (component = (RooProduct*) iter.Next())) {
        TString  componentName = component->GetName();
        double componentFrac = GetComponentFrac(w,componentName,RRSPdfName,obsRegion) ;
        compFracVec.push_back(componentFrac);
    }

    return compFracVec;
}


/*
 * Adopted from: RooAbsReal::getPropagatedError()
 * by Wouter Verkerke
 * See: http://root.cern.ch/root/html534/src/RooAbsReal.h.html
 * (http://roofit.sourceforge.net/license.txt)
 */


//_____________________________________________________________________________
double Util::getPropagatedError(RooAbsReal* var, const RooFitResult& fr, const bool& doAsym)
{
    Logger << kDEBUG << " GPP for variable = " << var->GetName() << GEndl;

    // Clone self for internal use
    RooAbsReal* cloneFunc = var; //(RooAbsReal*) var->cloneTree();
    RooArgSet* errorParams = cloneFunc->getObservables(fr.floatParsFinal()) ;
    RooArgSet* nset = cloneFunc->getParameters(*errorParams) ;

    // Make list of parameter instances of cloneFunc in order of error matrix
    RooArgList paramList ;
    const RooArgList& fpf = fr.floatParsFinal() ;
    vector<int> fpf_idx ;
    for (Int_t i=0 ; i<fpf.getSize() ; i++) {
        RooAbsArg* par = errorParams->find(fpf[i].GetName()) ;
        if (par ) {
            if (! par->isConstant() ) {
                paramList.add(*par) ;
                fpf_idx.push_back(i) ;
            }
        }
    }

    vector<Double_t> plusVar, minusVar ;

    TMatrixDSym V( fr.covarianceMatrix() ) ;

    for (Int_t ivar=0 ; ivar<paramList.getSize() ; ivar++) {

        RooRealVar& rrv = (RooRealVar&)fpf[fpf_idx[ivar]] ;

        int newI = fpf_idx[ivar];

        Double_t cenVal = rrv.getVal() ;
        Double_t errHes = sqrt(V(newI,newI)) ;

        Double_t errHi = rrv.getErrorHi();
        Double_t errLo = rrv.getErrorLo();
        Double_t errAvg = (TMath::Abs(errLo) + TMath::Abs(errHi))/2.0;

        Double_t errVal = errHes;
        if (doAsym) { errVal = errAvg; }

        Logger << kDEBUG << " GPP:  par = " << rrv.GetName() << " cenVal = " << cenVal << " errSym = " << errHes << " errAvgAsym = " << errAvg << GEndl;

        // Make Plus variation
        ((RooRealVar*)paramList.at(ivar))->setVal(cenVal+errVal) ;
        plusVar.push_back(cloneFunc->getVal(nset)) ;

        // Make Minus variation
        ((RooRealVar*)paramList.at(ivar))->setVal(cenVal-errVal) ;
        minusVar.push_back(cloneFunc->getVal(nset)) ;

        ((RooRealVar*)paramList.at(ivar))->setVal(cenVal) ;

    }

    TMatrixDSym C(paramList.getSize()) ;
    vector<double> errVec(paramList.getSize()) ;
    for (int i=0 ; i<paramList.getSize() ; i++) {
        int newII = fpf_idx[i];
        errVec[i] = sqrt(V(newII,newII)) ;
        for (int j=i ; j<paramList.getSize() ; j++) {
            int newJ = fpf_idx[j];
            C(i,j) = V(newII,newJ)/sqrt(V(newII,newII)*V(newJ,newJ)) ;
            C(j,i) = C(i,j) ;
        }
    }

    // Make vector of variations
    TVectorD F(plusVar.size()) ;
    for (unsigned int j=0 ; j<plusVar.size() ; j++) {
        F[j] = (plusVar[j]-minusVar[j])/2 ;
    }

    if(Logger.GetMinLevel() < kDEBUG) {
        F.Print();
        C.Print();
    }

    // Calculate error in linear approximation from variations and correlation coefficient
    Double_t sum = F*(C*F) ;

    Logger << kDEBUG << " GPP : sum = " << sqrt(sum) << GEndl;

    return sqrt(sum) ;
}


//_____________________________________________________________________________
void
Util::resetAllErrors( RooWorkspace* wspace )
{
    RooStats::ModelConfig* mc  = Util::GetModelConfig(wspace);
    if (mc==0) return;

    const RooArgSet* obsSet = mc->GetObservables();
    if (obsSet==0) return;

    RooAbsPdf* pdf = mc->GetPdf();
    if (pdf==0) return;

    RooArgList floatParList = Util::getFloatParList( *pdf, *obsSet );

    Util::resetError(wspace,floatParList);
}


//_____________________________________________________________________________
void
Util::resetAllValues( RooWorkspace* wspace )
{
    RooStats::ModelConfig* mc  = Util::GetModelConfig(wspace);
    if (mc==0) return;

    const RooArgSet* obsSet = mc->GetObservables();
    if (obsSet==0) return;

    RooAbsPdf* pdf = mc->GetPdf();
    if (pdf==0) return;

    RooArgList floatParList = Util::getFloatParList( *pdf, *obsSet );

    Util::resetValue(wspace,floatParList);
}


//_____________________________________________________________________________
void
Util::resetAllNominalValues( RooWorkspace* wspace )
{
    RooStats::ModelConfig* mc  = Util::GetModelConfig(wspace);
    if (mc==0) return;

    const RooArgSet* gobsSet = mc->GetGlobalObservables();
    if (gobsSet==0) return;

    gobsSet->Print("v");

    Util::resetNominalValue( wspace,*gobsSet );
}


//_____________________________________________________________________________
RooArgList
Util::getFloatParList( const RooAbsPdf& pdf, const RooArgSet& obsSet )
{
    RooArgList floatParList;

    const RooArgSet* pars = pdf.getParameters( obsSet );
    if (pars==0) { return floatParList; }

    TIterator* iter = pars->createIterator() ;
    RooAbsArg* arg ;
    while( (arg=(RooAbsArg*)iter->Next()) ) {
        if(arg->InheritsFrom("RooRealVar") && !arg->isConstant()){
            floatParList.add( *arg );
        }
    }
    delete iter;

    return floatParList;
}



//_____________________________________________________________________________
void
Util::resetError( RooWorkspace* wspace, const RooArgList& parList, const RooArgList& vetoList )

{
    /// For the given workspace,
    /// find the input systematic with
    /// the given name and shift that
    /// systematic by 1-sigma

    Logger << kINFO << " starting with workspace: " << wspace->GetName() << "   parList.getSize(): " << parList.getSize() << "  vetoList.size() = " << vetoList.getSize() << GEndl;

    TIterator* iter = parList.createIterator() ;
    RooAbsArg* arg ;
    while( (arg=(RooAbsArg*)iter->Next()) ) {

        std::string UncertaintyName;
        if(arg->InheritsFrom("RooRealVar") && !arg->isConstant()){
            UncertaintyName = arg->GetName();
        } else { continue; }

        if ( vetoList.FindObject( UncertaintyName.c_str() )!=0 ) { continue; }

        RooRealVar* var = wspace->var( UncertaintyName.c_str() );
        if( ! var ) {
            Logger << kERROR << "Could not find variable: " << UncertaintyName
                << " in workspace: " << wspace->GetName() << ": " << wspace
                << GEndl;
        }

        // Initialize
        double val_hi  = FLT_MAX;
        double val_low = FLT_MIN;
        double sigma = 0.;
        bool resetRange(false);

        if( UncertaintyName == "" ) {
            Logger << kERROR << "No Uncertainty Name provided" << GEndl;
            throw -1;
        }
        // If it is a standard (gaussian) uncertainty
        else if( string(UncertaintyName).find("alpha")!=string::npos ){
            // Assume the values are +1, -1
            val_hi  =  1.0;
            val_low = -1.0;
            sigma = 1.0;
            resetRange = true;
        }
        // If it is Lumi:
        else if( UncertaintyName == "Lumi" ) {
            // Get the Lumi's constraint term:
            RooGaussian* lumiConstr = (RooGaussian*) wspace->pdf("lumiConstraint");
            if(!lumiConstr){
                Logger << kERROR << "Could not find wspace->pdf('lumiConstraint') "
                    << " in workspace: " << wspace->GetName() << ": " << wspace
                    << " when trying to reset error for parameter: Lumi"
                    << GEndl;
                continue;
            }

            double val_nom = lumiConstr->getMean().getVal();
            sigma = lumiConstr->getSigma().getVal();

            val_hi  = val_nom + sigma;
            val_low = val_nom - sigma;
            resetRange = true;
        }
        // If it is a stat uncertainty (gamma)
        else if( string(UncertaintyName).find("gamma")!=string::npos ){

            // Get the constraint and check its type:
            RooAbsReal* constraint = (RooAbsReal*) wspace->obj( (UncertaintyName+"_constraint").c_str() );
            std::string ConstraintType ="";
            if(constraint != 0){ ConstraintType=constraint->IsA()->GetName(); }

            if( ConstraintType == "" ) {
                Logger << kINFO << "Assuming parameter :" << UncertaintyName << ": is a ShapeFactor and so unconstrained" << GEndl;
                continue;
            }
            else if( ConstraintType == "RooGaussian" ){
                RooAbsReal* sigmaVar = (RooAbsReal*) wspace->obj( (UncertaintyName+"_sigma").c_str() );
                sigma = sigmaVar->getVal();

                // Symmetrize shifts
                val_hi = 1 + sigma;
                val_low = 1 - sigma;
                resetRange = true;
            }
            else if( ConstraintType == "RooPoisson" ){
                RooAbsReal* nom_gamma = (RooAbsReal*) wspace->obj( ("nom_" + UncertaintyName).c_str() );
                double nom_gamma_val = nom_gamma->getVal();

                sigma = 1/TMath::Sqrt( nom_gamma_val );
                val_hi = 1 + sigma;
                val_low = 1 - sigma;
                resetRange = true;
            }
            else {
                Logger << kERROR << "Strange constraint type for Stat Uncertainties: " << ConstraintType << GEndl;
                throw -1;
            }

        } // End Stat Error
        else {
            // Some unknown uncertainty
            Logger << kINFO << "Couldn't identify type of uncertainty for parameter: " << UncertaintyName << ". Assuming a normalization factor." << GEndl;
            Logger << kINFO << "Setting uncertainty to 0.0001 before the fit for parameter: " << UncertaintyName << GEndl;
            sigma = 0.0001;
            val_low = var->getVal() - sigma;
            val_hi = var->getVal() + sigma;
            resetRange = false;
        }

        var->setError(abs(sigma));
        if (resetRange) {
            double minrange = var->getMin();
            double maxrange = var->getMax();
            double newmin = var->getVal() - 6.*sigma;
            double newmax = var->getVal() + 6.*sigma;
            if (minrange<newmin) var->setMin(newmin);
            if (newmax<maxrange) var->setMax(newmax);
        }

        Logger << kINFO << "Uncertainties on parameter: " << UncertaintyName
            << " low: "  << val_low
            << " high: " << val_hi
            << " sigma: " << sigma
            << " min range: " << var->getMin()
            << " max range: " << var->getMax()
            << GEndl;

        // Done
    } // end loop

    delete iter ;
}


//_____________________________________________________________________________
    void
Util::resetValue( RooWorkspace* wspace, const RooArgList& parList, const RooArgList& vetoList )

{
    /// For the given workspace,
    /// find the input systematic with
    /// the given name and shift that
    /// systematic by 1-sigma

    TIterator* iter = parList.createIterator() ;
    RooAbsArg* arg ;
    while( (arg=(RooAbsArg*)iter->Next()) ) {

        std::string UncertaintyName;
        if(arg->InheritsFrom("RooRealVar") && !arg->isConstant()){
            UncertaintyName = arg->GetName();
        } else { continue; }

        if ( vetoList.FindObject( UncertaintyName.c_str() )!=0 ) { continue; }

        RooRealVar* var = wspace->var( UncertaintyName.c_str() );
        if( ! var ) {
            Logger << kERROR << "Could not find variable: " << UncertaintyName
                << " in workspace: " << wspace->GetName() << ": " << wspace
                << GEndl;
        }

        // Initialize
        double valnom = 0.;

        if( UncertaintyName == "" ) {
            Logger << kERROR << "No Uncertainty Name provided" << GEndl;
            throw -1;
        }
        // If it is a standard (gaussian) uncertainty
        else if( string(UncertaintyName).find("alpha")!=string::npos ) {
            valnom = 0.0;
        }
        // If it is Lumi:
        else if( UncertaintyName == "Lumi" ) {
            valnom = 1.0;
        }
        // If it is a stat uncertainty (gamma)
        else if( string(UncertaintyName).find("gamma")!=string::npos ){
            valnom = 1.0;
        } // End Stat Error
        else {
            // Some unknown uncertainty
            valnom = 1.0;
        }

        var->setVal(valnom);
        // Done
    } // end loop

    delete iter ;
}


//_____________________________________________________________________________
    void
Util::resetNominalValue( RooWorkspace* wspace, const RooArgSet& globSet )
{
    /// For the given workspace,
    /// find the input systematic with
    /// the given name and shift that
    /// systematic by 1-sigma

    TIterator* iter = globSet.createIterator() ;
    RooAbsArg* arg ;
    while( (arg=(RooAbsArg*)iter->Next()) ) {

        TString UncertaintyName;
        if(arg->InheritsFrom("RooRealVar") && arg->isConstant()){
            UncertaintyName = arg->GetName();
        } else { continue; }

        RooRealVar* var = wspace->var( UncertaintyName.Data() );
        if( ! var ) {
            Logger << kERROR << "Could not find variable: " << UncertaintyName
                << " in workspace: " << wspace->GetName() << ": " << wspace
                << GEndl;
        }

        // Initialize
        double valnom = 0.;

        if( UncertaintyName == "" ) {
            Logger << kERROR << "No Uncertainty Name provided" << GEndl;
            throw -1;
        }
        // If it is Lumi:
        else if( UncertaintyName == TString("nominalLumi") ) {
            valnom = 1.0;
        }
        // If it is a standard (gaussian) uncertainty
        else if( string(UncertaintyName).find("gamma")!=string::npos ){
            valnom = 1.0;
        }
        // If it is a standard (gaussian) uncertainty
        else if ( UncertaintyName.BeginsWith("nom") ) {
            valnom = 0.0;
        }
        var->setVal(valnom);

        Logger << kDEBUG << "Now resetting: " << UncertaintyName << " to " << valnom << GEndl;
        // Done
    } // end loop

    delete iter ;
}


//______________________________________________________________________________________________
void Util::ImportInWorkspace( RooWorkspace* wspace, TObject* obj, TString name) {

    if(obj){

        if(name && obj->InheritsFrom("TNamed") ) {
            ((TNamed*) obj)->SetName(name.Data());
            ((TNamed*) obj)->SetTitle(name.Data());
        }

        wspace->import(*obj,kTRUE) ;
    }
    else{
        Logger << kWARNING << "Util::Import called with a NULL pointer, nothing will be imported" << GEndl;
    }

    // save snapshot
    RooSimultaneous* pdf = (RooSimultaneous*) wspace->pdf("simPdf");
    RooAbsData* data = (RooAbsData*)wspace->data("obsData");
    RooArgSet* params = (RooArgSet*) pdf->getParameters(*data) ;

    wspace->saveSnapshot(Form("snapshot_paramsVals_%s",name.Data()),*params);

}


//________________________________________________________________________________________________________________________________________
void Util::RemoveEmptyDataBins( RooPlot* frame){

    // histname=0 means that the last RooHist is taken from the RooPlot
    const char* histname = 0;

    // Find histogram object
    RooHist* hist = (RooHist*) frame->findObject(histname,RooHist::Class()) ;
    if (!hist) {
        Logger << kERROR << " Util::RemoveEmptyDataBins(" << frame->GetName() << ") cannot find histogram" << GEndl ;
        return ;
    }

    for(Int_t i=0; i<hist->GetN(); i++){
        Double_t x,y;
        hist->GetPoint(i,x,y) ;

        if( fabs(y)< 0.0000001 && hist->GetErrorYhigh(i) > 0.){
            hist->RemovePoint(i);
            if(i != hist->GetN()) --i;
        }
    }

    return;

}

//________________________________________________________________________________________________________________________________________
RooHist* Util::MakeRatioHist(RooPlot *frame, const char* histname, const char* pdfname, bool useAverage) {
    // Find all curve objects with the name "pdfname" or the name of the last
    // plotted curve (there might be multiple in the case of multi-range fits).
    std::vector<RooCurve*> curves;

    std::vector<TObject*> objects;
    for(size_t i = frame->numItems() - 1; i > 0; i--) objects.push_back(frame->getObject(i));
    
    for(TObject* obj : objects) {
        if(obj->IsA() == RooCurve::Class()) {
            // If no pdfname was passed, we take by default the last curve and all
            // other curves that have the same name
            if((!pdfname || pdfname[0] == '\0') || std::string(pdfname) == obj->GetName()) {
                pdfname = obj->GetName();
                curves.push_back(static_cast<RooCurve*>(obj));
            }
        }
    }
    
    if (curves.empty()) {
        Logger << kERROR << "RooPlotRatioHistGenerator::ratioHist(" << frame->GetName() << ") cannot find pdf curve" << GEndl ;
        return nullptr;
    }
    
    // Find histogram object
    auto hist = static_cast<RooHist*>(frame->findObject(histname, RooHist::Class()));
    if (!hist) {
        Logger << kERROR << "RooPlotRatioHistGenerator::ratioHist(" << frame->GetName() << ") cannot find histogram" << GEndl ;
        return nullptr;
    }
    

    // ---------------------------------------------------------------------------
    // Implementation of:
    // auto residHist = hist->createEmptyResidHist(*curves.front(), normalize);

    // Copy all non-content properties from hist1
    auto ratioHist = std::make_unique<RooHist>(hist->getNominalBinWidth());
    ratioHist->SetName(Form("pull_%s_%s", hist->GetName(), curves.front()->GetName()));
    ratioHist->SetTitle(Form("Pull of %s and %s", hist->GetTitle(), curves.front()->GetTitle()));
    // ---------------------------------------------------------------------------
    

    // We consider all curves with the same name as long as the ranges don't
    // overlap, to create also the full residual plot in multi-range fits.
    std::vector<std::pair<double, double>> coveredRanges;
    for(RooCurve* curve : curves) {
        const double xmin = curve->GetPointX(0);
        const double xmax = curve->GetPointX(curve->GetN() - 1);
    
        for(auto const& prevRange : coveredRanges) {
            const double pxmin = prevRange.first;
            const double pxmax = prevRange.second;
            // If either xmin or xmax is within any previous range, the ranges
            // overloap and it makes to sense to also consider this curve for the
            // residuals (i.e., they can't come from a multi-range fit).
            if((pxmax > xmin && pxmin <= xmin) || (pxmax > xmax && pxmin <= xmax)) {
                continue;
            }
        }
    
        coveredRanges.emplace_back(xmin, xmax);
    
        
        // ---------------------------------------------------------------------------
        // Implementation of:
        // hist->fillResidHist(*residHist, *curve, normalize, useAverage);

        // Determine range of curve
        Double_t xstart, xstop, y;
        curve->GetPoint(0, xstart, y);
        curve->GetPoint(curve->GetN() - 1, xstop, y) ;
        
        // Add histograms, calculate Poisson confidence interval on sum value
        for(Int_t i = 0 ; i < hist->GetN() ; i++) {
            Double_t x, point;
            hist->GetPoint(i, x, point) ;
        
            // Only calculate pull for bins inside curve range
            if (x < xstart || x > xstop) continue ;
        
            Double_t yy ;
            Double_t dyl = hist->GetErrorYlow(i) ;
            Double_t dyh = hist->GetErrorYhigh(i) ;

            if (useAverage) {
                Double_t exl = hist->GetErrorXlow(i);
                Double_t exh = hist->GetErrorXhigh(i) ;
                if (exl <= 0) exl = hist->GetErrorX(i);
                if (exh <= 0) exh = hist->GetErrorX(i);
                if (exl <= 0) exl = 0.5 * hist->getNominalBinWidth();
                if (exh <= 0) exh = 0.5 * hist->getNominalBinWidth();

                yy = point / curve->average(x - exl, x + exh) ;
                dyl /= curve->average(x - exl, x + exh);
                dyh /= curve->average(x - exl, x + exh);
            } else {
                yy = point / curve->interpolate(x);
                dyl /= curve->interpolate(x);
                dyh /= curve->interpolate(x);
            }

            // Don't add a ratio plot point if there's no data in the bin
            if (std::abs(point) < 0.000001) continue;
        
            ratioHist->addBinWithError(x, yy, dyl, dyh);
        }
        // ---------------------------------------------------------------------------
    }
    ratioHist->GetHistogram()->GetXaxis()->SetRangeUser(frame->GetXaxis()->GetXmin(), frame->GetXaxis()->GetXmax());
    ratioHist->GetHistogram()->GetXaxis()->SetTitle(frame->GetXaxis()->GetTitle());
    ratioHist->GetHistogram()->GetYaxis()->SetTitle("Data / curve");
    return ratioHist.release();
}

//________________________________________________________________________________________________________________________________________
RooHist* Util::MakeRatioOrPullHist(RooAbsData *regionData, RooAbsPdf *regionPdf, RooRealVar *regionVar, bool makePull /*false*/) {
	// data/pdf ratio histograms are plotted by RooPlot.ratioHist() through a dummy frame
	RooPlot* frame_dummy = regionVar->frame();
	regionData->plotOn(frame_dummy, RooFit::DataError(RooAbsData::Poisson));

	// normalize pdf to number of expected events, not to number of events in dataset
	regionPdf->plotOn(frame_dummy, RooFit::Normalization(1, RooAbsReal::RelativeExpected),
								     RooFit::Precision(1e-5));

	if(makePull) {
        //return static_cast<RooHist*>(frame_dummy->pullHist());
        return static_cast<RooHist*>(frame_dummy->pullHist());
	}

    // Ratio hist
    return static_cast<RooHist*>(MakeRatioHist(frame_dummy, nullptr, nullptr, false));
}

//________________________________________________________________________________________________________________________________________
RooCurve* Util::MakePdfErrorRatioHist(RooAbsData* regionData, RooAbsPdf* regionPdf, RooRealVar* regionVar, RooFitResult* rFit, Double_t Nsigma){

    RooPlot* frame = regionVar->frame();
    regionData->plotOn(frame, RooFit::DataError(RooAbsData::Poisson));

    // normalize pdf to number of expected events, not to number of events in dataset
    regionPdf->plotOn(frame, Normalization(1, RooAbsReal::RelativeExpected), Precision(1e-5));
    RooCurve* curveNom = (RooCurve*) frame->findObject(nullptr, RooCurve::Class()) ;
    if (!curveNom) {
        Logger << kERROR << "Util::MakePdfErrorRatioHist(" << frame->GetName() << ") cannot find curveNom" << curveNom->GetName() << GEndl ;
        return 0 ;
    }

    if(rFit != NULL) {
        regionPdf->plotOn(frame, Normalization(1, RooAbsReal::RelativeExpected),
                                 Precision(1e-5),
                                 FillColor(kBlue-5),
                                 FillStyle(3004),
                                 DrawOption("F"),
                                 VisualizeError(*rFit, Nsigma));
    }

    // Find curve object
    RooCurve* curveError = (RooCurve*) frame->findObject(nullptr, RooCurve::Class()) ;
    if (!curveError) {
        Logger << kERROR << "Util::makePdfErrorRatioHist(" << frame->GetName() << ") cannot find curveError" << GEndl ;
        return 0 ;
    }

    RooCurve* ratioBand = new RooCurve ;
    ratioBand->SetName(Form("%s_ratio_errorband", curveNom->GetName())) ;
    ratioBand->SetLineWidth(1) ;
    ratioBand->SetLineColor(kBlue-5);
    ratioBand->SetFillColor(kBlue-5);
    ratioBand->SetFillStyle(3004);

    Int_t j = 0;
    Bool_t bottomCurve = kFALSE;
    for(Int_t i=1; i < curveError->GetN()-1; ++i){
        Double_t x = 0.;
        Double_t y = 0.;
        curveError->GetPoint(i, x, y) ;

        // errorBand curve has twice as many points as does a normal/nominal (pdf) curve
        //  first it walks through all +1 sigma points (topCurve), then the -1 sigma points (bottomCurve)
        //   to divide the errorCurve by the pdfCurve, we need to count back for the pdfCurve once we're in the middle of errorCurve
        if( i >= (curveNom->GetN()-1) ) bottomCurve = kTRUE;

        Double_t xNom = x;
        Double_t yNom = y;

        // each errorCurve has two more points just outside the plot, so we need to treat them separately
        if( i == (curveNom->GetN() - 1) ||  i == curveNom->GetN() ){
            ratioBand->addPoint(x, 0.);
            continue;
        }


        if( bottomCurve){
            curveNom->GetPoint(j,xNom,yNom);
            j--;
        } else {
            j++;
            curveNom->GetPoint(j,xNom,yNom);
        }

        // only divide by yNom if it is non-zero
        if(  fabs(yNom) > 0.00001 ){
            ratioBand->addPoint(x, (y / yNom));
        } else {
            ratioBand->addPoint(x, 0.);
        }
    }

    return ratioBand;
}



//_____________________________________________________________________________
void Util::SetPdfParError(RooWorkspace* w, double Nsigma){

    RooStats::ModelConfig* mc  = Util::GetModelConfig(w);
    if (mc==0) return;

    const RooArgSet* obsSet = mc->GetObservables();
    if (obsSet==0) return;

    RooAbsPdf* pdf = mc->GetPdf();
    if (pdf==0) return;

    RooArgList floatParList = Util::getFloatParList( *pdf, *obsSet );

    TIterator* iter = floatParList.createIterator() ;
    RooAbsArg* arg ;
    while( (arg=(RooAbsArg*)iter->Next()) ) {

        TString parName;
        if(arg->InheritsFrom("RooRealVar") && !arg->isConstant()){
            parName = arg->GetName();
        } else { continue; }

        RooRealVar* par = (RooRealVar*) w->var(parName.Data());

        Double_t cenVal = par->getVal();
        Double_t errVal = par->getError();
        par->setVal(cenVal + Nsigma * errVal);

    }
}




//_____________________________________________________________________________
RooAbsReal* Util::CreateNLL( RooWorkspace* w, TString fitRegions, Bool_t lumiConst)
{
    if(w==NULL){
        Logger << kERROR << "Workspace not found, no fitting performed" << GEndl;
        return NULL;
    }
    RooSimultaneous* pdf = (RooSimultaneous*) w->pdf("simPdf");

    RooAbsData* data = (RooAbsData*)w->data("obsData") ;
    RooCategory* regionCat = (RooCategory*) w->cat("channelCat");

    data->table(*((RooAbsCategory*)regionCat))->Print("v");

    if (lumiConst) {
        RooRealVar* lumi = (RooRealVar*) w->var("Lumi");
        if (lumi!=NULL) lumi->setConstant(lumiConst);
    }

    // Construct an empty simultaneous pdf using category regionCat as index
    RooSimultaneous* simPdfFitRegions = pdf;
    RooDataSet* dataFitRegions = (RooDataSet*) data;

    std::vector<TString> fitRegionsVec = GetRegionsVec(fitRegions, regionCat);

    unsigned int numFitRegions = fitRegionsVec.size();
    std::vector<RooDataSet*> dataVec;
    std::vector<RooAbsPdf*> pdfVec;

    for(unsigned int iVec=0; iVec<numFitRegions; iVec++){
        TString regionCatLabel = fitRegionsVec[iVec];
        if( regionCat->setLabel(regionCatLabel,kTRUE)){
            Logger << kWARNING << " Label '" << regionCatLabel << "' is not a state of channelCat (see Table) " << GEndl;
        } else{
            // dataset for each channel/region/category
            TString dataCatLabel = Form("channelCat==channelCat::%s",regionCatLabel.Data());
            RooDataSet* regionData = (RooDataSet*) data->reduce(dataCatLabel.Data());
            dataVec.push_back(regionData);
            // pdf for each channel/region/category
            RooAbsPdf* regionPdf = (RooAbsPdf*) pdf->getPdf(regionCatLabel.Data());
            pdfVec.push_back(regionPdf);
        }
    }

    if(dataVec.empty()){
        Logger << kERROR << "   NONE OF THE REGIONS ARE SPECIFIED IN DATASET, NO FIT WILL BE PERFORMED" << GEndl;
        return 0;
    }
    else if(pdfVec.empty()){
        Logger << kERROR << "   NONE OF THE REGIONS ARE SPECIFIED IN SIMULTANEOUS PDF, NO FIT WILL BE PERFORMED" << GEndl;
        return 0;
    }
    else{
        // Construct a simultaneous dataset for all fit regions
        dataFitRegions = (RooDataSet*) dataVec[0]->Clone("dataFitRegions");
        for(unsigned int jVec=1; jVec<dataVec.size(); jVec++){
            dataFitRegions->append(*dataVec[jVec]);
        }
        // Construct a simultaneous pdf using category regionCat as index
        simPdfFitRegions = new RooSimultaneous("simPdfFitRegions","simultaneous pdf only for fit regions",*regionCat) ;
        for(unsigned int kVec=0; kVec<pdfVec.size(); kVec++){
            simPdfFitRegions->addPdf(*pdfVec[kVec],fitRegionsVec[kVec].Data());
        }
    }

    RooAbsPdf* pdf_FR = simPdfFitRegions;
    RooDataSet* data_FR = dataFitRegions;

    RooStats::ModelConfig* mc = Util::GetModelConfig( w );
    const RooArgSet* globObs = mc->GetGlobalObservables();

    RooAbsReal* nll = (RooNLLVar*) pdf_FR->createNLL(*data_FR, RooFit::GlobalObservables(*globObs) );

    return nll;
}



    TString
Util::scanStrForFloats(const TString& toscan, const TString& format)
{
    int narg1 = format.CountChar('%');
    TString wsid;
    std::vector<float> wsarg(10);

    int narg2 = sscanf( toscan.Data(), format.Data(), &wsarg[0],&wsarg[1],&wsarg[2],&wsarg[3],&wsarg[4],&wsarg[5],&wsarg[6],&wsarg[7],&wsarg[8],&wsarg[9] );

    if ( !(narg1==narg2 && narg2>0) ) {
        Logger << kERROR << "Util::scanStringForFloats incorrect lengths" << GEndl;
        return wsid;
    }

    wsarg.resize(narg2);
    wsid.Clear();  // form unique ws id
    for (int i=0; i<narg2; ++i) {
        if (i!=0) wsid += "_" ;
        wsid += Form("%.0f", wsarg[i] );
    }

    return wsid;
}

//---------------------------------------------------------------------------------------

TGraph* Util::getErrorBand(TH1F* hNom, TH1F* hHigh, TH1F* hLow){

   vector<double> nom(0), high(0), low(0);
   vector<double> X(0), ErrXl(0), ErrXh(0);

   for(int i=1;i<=hNom->GetNbinsX();i++){

      X.push_back(hNom->GetBinCenter(i));
      ErrXl.push_back(hNom->GetBinWidth(i)/2);
      ErrXh.push_back(hNom->GetBinWidth(i)/2);
      nom.push_back(hNom->GetBinContent(i));
      //case in which high > nominal and nominal > low
      if(hHigh->GetBinContent(i)>hNom->GetBinContent(i) && hNom->GetBinContent(i)>hLow->GetBinContent(i)){
        high.push_back(hHigh->GetBinContent(i)-hNom->GetBinContent(i));
        low.push_back(hNom->GetBinContent(i)-hLow->GetBinContent(i));
      }
      //case in which low > nominal and nominal > high
      else if(hLow->GetBinContent(i)>hNom->GetBinContent(i) && hNom->GetBinContent(i)>hHigh->GetBinContent(i)){
        high.push_back(hLow->GetBinContent(i)-hNom->GetBinContent(i));
        low.push_back(hNom->GetBinContent(i)-hHigh->GetBinContent(i));
      }
      //case in which low and high > nominal
      else if(hLow->GetBinContent(i)>hNom->GetBinContent(i) && hHigh->GetBinContent(i)>hNom->GetBinContent(i)){
        if(hHigh->GetBinContent(i)>=hLow->GetBinContent(i)){
          high.push_back(hHigh->GetBinContent(i)-hNom->GetBinContent(i));
          low.push_back(0.);
        }
        else{
          high.push_back(hLow->GetBinContent(i)-hNom->GetBinContent(i));
          low.push_back(0.);
        }
      }
      //case in which low and high < nominal
      else if(hLow->GetBinContent(i)<hNom->GetBinContent(i) && hHigh->GetBinContent(i)<hNom->GetBinContent(i)){
        if(hHigh->GetBinContent(i)>=hLow->GetBinContent(i)){
          high.push_back(0.);
          low.push_back(hNom->GetBinContent(i)-hLow->GetBinContent(i));
        }
        else{
          high.push_back(0.);
          low.push_back(hNom->GetBinContent(i)-hHigh->GetBinContent(i));
        }
      }
      //all other cases
      else{
        if(hNom->GetBinContent(i) == hHigh->GetBinContent(i)){
          if(hNom->GetBinContent(i)>hLow->GetBinContent(i)){
            high.push_back(0.);
            low.push_back(hNom->GetBinContent(i)-hLow->GetBinContent(i));
          }
          else{
            high.push_back(hLow->GetBinContent(i)-hNom->GetBinContent(i));
            low.push_back(0.);
          }
        }
        else{
          if(hNom->GetBinContent(i)>hHigh->GetBinContent(i)){
            high.push_back(0.);
            low.push_back(hNom->GetBinContent(i)-hHigh->GetBinContent(i));
          }
          else{
            high.push_back(hHigh->GetBinContent(i)-hNom->GetBinContent(i));
            low.push_back(0);
          }
        }
      }
   }


   TGraph* g = new TGraph();
   for(unsigned int i=0;i<X.size();i++){
     g->SetPoint(2*i,X[i]-ErrXl[i],nom[i]+high[i]);
     g->SetPoint(2*i+1,X[i]+ErrXh[i],nom[i]+high[i]);
   }

   int Ntmp = g->GetN();

   for(unsigned int i=0;i<X.size();i++){
    g->SetPoint(Ntmp+2*i,X[X.size()-1-i]+ErrXh[X.size()-1-i],nom[X.size()-1-i]-low[X.size()-1-i]);
    g->SetPoint(Ntmp+2*i+1,X[X.size()-1-i]-ErrXl[X.size()-1-i],nom[X.size()-1-i]-low[X.size()-1-i]);
   }

   g->SetFillColor(kYellow);

   return g;

}

void Util::plotDistribution(TFile* f, TString hNomName, TString Syst, TString NameSample, TString Region, TString Var){


   TH1F* hNom = (TH1F*)f->Get(hNomName);

   TString syst_name = Syst;
   TString norm = "";
   if (syst_name.EndsWith("Norm")) {
      syst_name.ReplaceAll("Norm","");
      norm = "Norm";
   }

   TString hHighName = hNomName;
   hHighName.ReplaceAll("Nom",syst_name+"High");
   TH1F* hHigh = (TH1F*)f->Get(hHighName+norm);

   TString hLowName = hNomName;
   hLowName.ReplaceAll("Nom",syst_name+"Low");
   TH1F* hLow = (TH1F*)f->Get(hLowName+norm);

   if(!hHigh || !hLow){
     Logger << kWARNING << syst_name << " systematic (with or without normalization) has not been found  " << GEndl;
     return;
   }

   TH1F* hNomClone = (TH1F*)hNom->Clone();
   for(int i=1;i<=hNomClone->GetNbinsX();i++){
       if(hNom->GetBinContent(i)>0) hNomClone->SetBinError(i,hNom->GetBinError(i)/hNom->GetBinContent(i));
       hNomClone->SetBinContent(i,1);

   }

   TH1F* hHighClone = (TH1F*)hHigh->Clone();
   hHighClone->Divide(hNom);
   for(int i=1;i<=hHighClone->GetNbinsX();i++){
       hHighClone->SetBinError(i,0.);
   }
   TH1F* hLowClone = (TH1F*)hLow->Clone();
   hLowClone->Divide(hNom);
   for(int i=1;i<=hLowClone->GetNbinsX();i++){
       hLowClone->SetBinError(i,0.);
   }

   for(int i=1;i<=hNom->GetNbinsX();i++){
      if(hNom->GetBinContent(i)<=0){
        if(hLow->GetBinContent(i)<=0 && hHigh->GetBinContent(i)<=0){
             hLowClone->SetBinContent(i,1.);
             hHighClone->SetBinContent(i,1);
        }
        else if(hLow->GetBinContent(i)<=0 && hHigh->GetBinContent(i)>0) hHighClone->SetBinContent(i,10);
        else if(hLow->GetBinContent(i)>0 && hHigh->GetBinContent(i)<=0) hLowClone->SetBinContent(i,10);
        else{
         if(hHigh->GetBinContent(i)>hLow->GetBinContent(i)){
            hHighClone->SetBinContent(i,10);
            hLowClone->SetBinContent(i,1.);
         }
         else{
            hLowClone->SetBinContent(i,10);
            hHighClone->SetBinContent(i,1.);
         }
        }

      }
   }




   TCanvas* c = new TCanvas(NameSample+"_"+Syst+"Syst_"+Region+"_Dist",NameSample+" "+Syst+" Syst ("+Region+") Dist",600,400);

   TPad* pad1 = new TPad("pad1","pad1",0.0,0.3,1.0,1.0,0);
   pad1->Draw();
   pad1->cd();

   TLegend* leg = new TLegend(0.65,0.7,0.85,0.85,"");
   leg->SetFillStyle(0);
   leg->SetFillColor(0);
   leg->SetBorderSize(0);


   TGraph* g = getErrorBand(hNom,hHigh,hLow);
   g->SetName(Syst+" Syst");
   g->SetTitle(Syst+" Syst");
   g->GetXaxis()->SetTitle(Var);
   g->GetYaxis()->SetTitle("Entries");
   g->GetYaxis()->SetTitleSize(0.045);
   leg->AddEntry(g,"","f");
   g->Draw("APF2");

   hNom->SetMarkerStyle(20);
   leg->AddEntry(hNom,"Nom [MCStatError]","l");
   hNom->Draw("samep");

   hHigh->SetLineColor(kCyan-3);
   hHigh->SetLineStyle(kDashed);
   hHigh->SetLineWidth(2.);
   leg->AddEntry(hHigh,Syst+" High","l");
   hHigh->Draw("same");

   hLow->SetLineColor(kMagenta-3);
   hLow->SetLineStyle(kDotted);
   hLow->SetLineWidth(2.);
   leg->AddEntry(hLow,Syst+" Low","l");
   hLow->Draw("same");

   leg->Draw();

   c->cd();
   TPad* pad2 = new TPad("pad2","pad2",0.0,0.0,1.0,0.365,0);
   pad2->SetTopMargin(0.1);
   pad2->SetBottomMargin(0.2);
   pad2->Draw();
   pad2->cd();

   TGraph* gClone = getErrorBand(hNomClone,hHighClone,hLowClone);
   gClone->GetXaxis()->SetLabelSize(0.08);
   gClone->GetXaxis()->SetTitleSize(0.08);
   gClone->GetXaxis()->SetTitle(Var);
   gClone->GetYaxis()->SetTitle("#Delta X/X[%]");
   gClone->GetYaxis()->SetTitleOffset(0.5);
   gClone->GetYaxis()->SetTitleSize(0.08);
   gClone->GetYaxis()->SetRangeUser(0,2.);
   gClone->GetYaxis()->SetLabelSize(0.06);
   double minY=11., maxY=0;
   for(int i=0;i<gClone->GetN();i++){
      double x,y;
      gClone->GetPoint(i,x,y);
      if(y<minY) minY=y;
      if(y>maxY) maxY=y;
   }
   if(maxY>2.) maxY=2.;
   gClone->GetYaxis()->SetRangeUser(minY-0.01,maxY+0.01);
   gClone->Draw("APF2");

   hNomClone->SetMarkerStyle(20);
   hNomClone->Draw("samep");

   hHighClone->SetLineColor(kCyan-3);
   hHighClone->SetLineStyle(kDashed);
   hHighClone->SetLineWidth(2.);
   hHighClone->Draw("same");

   hLowClone->SetLineColor(kMagenta-3);
   hLowClone->SetLineStyle(kDotted);
   hLowClone->SetLineWidth(2.);
   hLowClone->Draw("same");


   c->SaveAs(Form("plots/%s.eps",c->GetName()));
   c->SaveAs(Form("plots/%s.root",c->GetName()));

}

void Util::plotSystematics(TFile* f,TString hNomName, vector<TString> Syst, TString NameSample, TString Region, TString Var){

   TH1F* h = (TH1F*)f->Get(hNomName);
   if(!h) return;
   float Nom = h->Integral();

   const int NBins = Syst.size();
   TH1F* hSystNom = new TH1F("hSystNom","hSystNom",NBins,0,NBins);
   TH1F* hSystHigh = new TH1F("hSystHigh","hSystHigh",NBins,0,NBins);
   TH1F* hSystLow = new TH1F("hSystLow","hSystLow",NBins,0,NBins);


   for(int i=1;i<=NBins;i++){

      TString syst_name = Syst[i-1];
      TString norm = "";
      if (syst_name.EndsWith("Norm")) {
        syst_name.ReplaceAll("Norm","");
        norm = "Norm";
      }


      hSystNom->SetBinContent(i,Nom);
      TString hHighName = hNomName;
      hHighName.ReplaceAll("Nom",syst_name+"High");
      TH1F* hH = (TH1F*)f->Get(hHighName+norm);

      TString hLowName = hNomName;
      hLowName.ReplaceAll("Nom",syst_name+"Low");
      TH1F* hL = (TH1F*)f->Get(hLowName+norm);

      if(!hH || !hL){
        Logger << kWARNING << syst_name <<" systematic (with or without normalization) has not been found" << GEndl;
        hSystHigh->SetBinContent(i,Nom);
        hSystLow->SetBinContent(i,Nom);
      }
      else{
        hSystHigh->SetBinContent(i,hH->Integral());
        hSystLow->SetBinContent(i,hL->Integral());
      }
   }


   TCanvas* c = new TCanvas(NameSample+"_AllSyst_"+Region,NameSample+" All Syst ("+Region+")",600,400);

   TLegend* leg = new TLegend(0.65,0.7,0.85,0.85,"");
   leg->SetFillStyle(0);
   leg->SetFillColor(0);
   leg->SetBorderSize(0);


   TGraph* g = getErrorBand(hSystNom,hSystHigh,hSystLow);
   g->SetName("Syst");
   g->SetTitle("Syst");
   g->GetHistogram()->GetXaxis()->Set(NBins,0,NBins);
   for(int i=1;i<=NBins;i++) g->GetHistogram()->GetXaxis()->SetBinLabel(i,Syst[i-1]);
   g->GetXaxis()->SetTitle(Var);
   g->GetYaxis()->SetTitle("Entries");
   g->GetYaxis()->SetTitleOffset(1.25);
   leg->AddEntry(g,"","f");
   g->Draw("APF2");

   hSystNom->SetLineWidth(2.);
   leg->AddEntry(hSystNom,"Nom","l");
   hSystNom->Draw("same");

   hSystHigh->SetLineColor(kCyan-3);
   hSystHigh->SetLineStyle(kDashed);
   hSystHigh->SetLineWidth(2.);
   leg->AddEntry(hSystHigh,"High Syst","l");
   hSystHigh->Draw("same");

   hSystLow->SetLineColor(kMagenta-3);
   hSystLow->SetLineStyle(kDotted);
   hSystLow->SetLineWidth(2.);
   leg->AddEntry(hSystLow,"Low Syst","l");
   hSystLow->Draw("same");

   leg->Draw();

   c->SaveAs(Form("plots/%s.eps",c->GetName()));
   c->SaveAs(Form("plots/%s.root",c->GetName()));


}

void Util::plotUpDown(TString FileName, TString NameSample, TString SystName, TString Region, TString Var){

 TFile* f = TFile::Open(FileName.Data(), "READ");
 if (f->IsZombie()) {
        Logger << kERROR << "Cannot open file: " << FileName << GEndl;
        return;
 }
 f->cd();

 //Loading the nominal histo
 TString hNomName = "h"+NameSample+"Nom_"+Region+"_obs_"+Var;
 int NBins = -1;
 TH1F* h = (TH1F*)f->Get(hNomName);
 if(h!=0) NBins = h->GetNbinsX();
 delete h;


 //Taking systematic labels
 if(NBins>0){
  vector<TString> Syst(0);

  TObjArray* Obj = SystName.Tokenize(",");
  if(Obj->LastIndex()>-1){
   for(int i=0;i<=Obj->GetLast();i++)   Syst.push_back(((TObjString*)Obj->At(i))->String());
  }
  else{
   Syst.push_back(SystName);
  }


  if(NBins>0){
   for(unsigned int i=0;i<Syst.size();i++) plotDistribution(f,hNomName,Syst[i],NameSample,Region,Var);
  }

  plotSystematics(f,hNomName,Syst,NameSample,Region,Var);

 }
 else Logger << kWARNING << " No nominal histogram for  " << NameSample << GEndl;

 //f->Close();
 //delete f;

}

//-------------------------------------------------------------------------------------------------------
void Util::PlotFitParameters(RooFitResult* r, TString anaName){

 RooArgList ListParams = r->floatParsFinal();

 vector<TString> alpha_parNames, mcstat_parNames, mu_parNames;
 vector<double> N, errN;
 vector<double> alpha_parVals,alpha_parHighErrors,alpha_parLowErrors;
 vector<double> mcstat_parVals,mcstat_parHighErrors,mcstat_parLowErrors;
 vector<double> mu_parVals,mu_parHighErrors,mu_parLowErrors;

 int count=0;

 for(int i=0;i<ListParams.getSize();i++){
    RooRealVar* x = (RooRealVar*) ListParams.at(ListParams.getSize()-i-1);
    //cout<<x->GetName()<<" "<<x->getVal()<<" +- "<<x->getAsymErrorHi()<<" "<<x->getAsymErrorLo()<<endl;
    TString tmpName = x->GetName();
    if(tmpName.Contains("alpha")){
      tmpName.ReplaceAll("alpha","#alpha");
      count+=2;
      alpha_parNames.push_back(tmpName);
      alpha_parVals.push_back(x->getVal());
      alpha_parHighErrors.push_back(x->getAsymErrorHi());
      if(x->getAsymErrorLo()!=0) alpha_parLowErrors.push_back(fabs(x->getAsymErrorLo()));
      else alpha_parLowErrors.push_back(x->getAsymErrorHi());
      N.push_back(count);
      errN.push_back(0);
    }else if(tmpName.Contains("Lumi") || tmpName.Contains("mcstat") || tmpName.Contains("gamma_stat")){
      tmpName.ReplaceAll("gamma_shape_mcstat","#gamma");
      tmpName.ReplaceAll("gamma_stat","#gamma");
      count+=2;
      mcstat_parNames.push_back(tmpName);
      mcstat_parVals.push_back(x->getVal()-1);
      mcstat_parHighErrors.push_back(x->getAsymErrorHi());
      if(x->getAsymErrorLo()!=0) mcstat_parLowErrors.push_back(fabs(x->getAsymErrorLo()));
      else mcstat_parLowErrors.push_back(x->getAsymErrorHi());
      N.push_back(count);
      errN.push_back(0);
    }else{
      tmpName.ReplaceAll("mu","#mu");
      count+=2;
      mu_parNames.push_back(tmpName);
      mu_parVals.push_back(x->getVal()-1);
      mu_parHighErrors.push_back(x->getAsymErrorHi());
      if(x->getAsymErrorLo()!=0) mu_parLowErrors.push_back(fabs(x->getAsymErrorLo()));
      else mu_parLowErrors.push_back(x->getAsymErrorHi());
      N.push_back(count);
      errN.push_back(0);
    }
 }

 vector<TString> parNames;
 parNames.insert(parNames.end(), alpha_parNames.begin(), alpha_parNames.end());
 parNames.insert(parNames.end(), mcstat_parNames.begin(), mcstat_parNames.end());
 parNames.insert(parNames.end(), mu_parNames.begin(), mu_parNames.end());
 vector<double> parVals, parHighErrors, parLowErrors;
 parVals.insert(parVals.end(), alpha_parVals.begin(), alpha_parVals.end());
 parVals.insert(parVals.end(), mcstat_parVals.begin(), mcstat_parVals.end());
 parVals.insert(parVals.end(), mu_parVals.begin(), mu_parVals.end());
 parHighErrors.insert(parHighErrors.end(), alpha_parHighErrors.begin(), alpha_parHighErrors.end());
 parHighErrors.insert(parHighErrors.end(), mcstat_parHighErrors.begin(), mcstat_parHighErrors.end());
 parHighErrors.insert(parHighErrors.end(), mu_parHighErrors.begin(), mu_parHighErrors.end());
 parLowErrors.insert(parLowErrors.end(), alpha_parLowErrors.begin(), alpha_parLowErrors.end());
 parLowErrors.insert(parLowErrors.end(), mcstat_parLowErrors.begin(), mcstat_parLowErrors.end());
 parLowErrors.insert(parLowErrors.end(), mu_parLowErrors.begin(), mu_parLowErrors.end());



 TCanvas* c_np = new TCanvas("fit_parameters","fit_parameters",1200,800);
 c_np->cd();
 TPad* p_np = new TPad("p_np","p_np",0,1,1,0.,0);
 p_np->SetLeftMargin(0.3);
 p_np->Draw();
 p_np->cd();

 TGraphAsymmErrors* g = new TGraphAsymmErrors(N.size(),&(parVals[0]),&(N[0]),&(parLowErrors[0]),&(parHighErrors[0]),&(errN[0]),&(errN[0]));
 g->GetHistogram()->GetYaxis()->Set(count/2,1,count+1);
 for(unsigned int i=1;i<=N.size();i++) g->GetHistogram()->GetYaxis()->SetBinLabel(i,parNames[i-1]);
 g->GetHistogram()->GetYaxis()->SetRangeUser(1,count+1);
 g->GetHistogram()->GetYaxis()->SetTickLength(0.);
 g->GetHistogram()->GetYaxis()->SetLabelSize(0.035);
 g->GetHistogram()->GetXaxis()->SetRangeUser(-1.5,1.5);
 g->GetHistogram()->GetXaxis()->SetTitle("#alpha");
 g->SetName("fit_results");
 g->SetTitle("");
 g->SetMarkerStyle(8);
 g->SetMarkerSize(2);
 g->SetLineWidth(1);
 g->Draw("AP");

 vector<double> _N, _errN;
 vector<double> _parVals, _parHighErrors, _parLowErrors;
 for(unsigned int i=1;i<=mcstat_parVals.size()+mu_parVals.size();i++){
     _N.push_back(alpha_parVals.size()*2+2*i);
     _errN.push_back(0);
 }
 _parVals.insert(_parVals.end(), mcstat_parVals.begin(), mcstat_parVals.end());
 _parVals.insert(_parVals.end(), mu_parVals.begin(), mu_parVals.end());
 _parHighErrors.insert(_parHighErrors.end(), mcstat_parHighErrors.begin(), mcstat_parHighErrors.end());
 _parHighErrors.insert(_parHighErrors.end(), mu_parHighErrors.begin(), mu_parHighErrors.end());
 _parLowErrors.insert(_parLowErrors.end(), mcstat_parLowErrors.begin(), mcstat_parLowErrors.end());
 _parLowErrors.insert(_parLowErrors.end(), mu_parLowErrors.begin(), mu_parLowErrors.end());

 TGraph* _g = new TGraph(_N.size(),&(_parVals[0]),&(_N[0]));
 _g->SetName("_fit_results");
 _g->SetTitle("");
 _g->SetMarkerStyle(8);
 _g->SetMarkerColor(kBlue);
 _g->SetMarkerSize(2);
 _g->Draw("Psame");


 TGraph* yMCstatBand = new TGraph();
 yMCstatBand->SetPoint(0,-1,0);
 yMCstatBand->SetPoint(1,-1,count+2);
 yMCstatBand->SetPoint(2,1,count+2);
 yMCstatBand->SetPoint(3,1,0);
 yMCstatBand->SetFillColor(kYellow);
 yMCstatBand->SetFillStyle(3352);

 TLine* lMCstat = new TLine(0,1,0,count+1);
 lMCstat->SetLineStyle(8);
 c_np->Update();

 TGaxis *axis1 = new TGaxis(p_np->GetUxmin(),p_np->GetUymax(),p_np->GetUxmax(),p_np->GetUymax(),p_np->GetUxmin()+1,p_np->GetUxmax()+1,510,"-L");
 axis1->SetLineColor(kBlue);
 axis1->SetLabelColor(kBlue);
 axis1->SetTitle("#gamma / #mu");
 axis1->SetTitleColor(kBlue);
 axis1->Draw("same");

 yMCstatBand->Draw("Fsame");
 lMCstat->Draw("same");
 g->Draw("Psame");
 _g->Draw("Psame");

 c_np->SaveAs("results/"+anaName+"/"+c_np->GetName()+".root");

}


//-------------------------------------------------------------------------------------------------------
TH1* Util::ComponentToHistogram(RooRealSumPdf* component, RooRealVar* variable, RooFitResult *fitResult) {
    // Build a TH1-based histogram from a pdf, an observable and a fit result

    // Get the stepsize and build a histogram according to the binning of the variable
    auto stepsize = variable->getBinning().averageBinWidth();

    // this line is throwing an error when trying to save individual parts
    auto hist = component->createHistogram(Form("hist_%s", component->GetName()), *variable);

    // Remember original variable value to reset later
    const double origVal = variable->getVal();

    // Now loop over the bins and fill them
    // Skip the under- and overflow bins because they don't exist in RooFit.
    for(int i=1; i < hist->GetNbinsX()+1; ++i) {
        variable->setBin(i-1);

        // Now get the value and the error
        auto sum = component->getVal();
        auto err = component->getPropagatedError(*fitResult);

        // and put them in the histogram
        hist->SetBinContent(i, sum);
        hist->SetBinError(i, err);
    }

    // Reset original variable value
    variable->setVal(origVal);

    hist->Scale(stepsize);

    return hist;
}

void Util::ScaleGraph(TGraphAsymmErrors *g, TH1* h) {
    if (g->GetN() != h->GetNbinsX() ) {
        Logger << kERROR << "Cannot multiply graph with " << g->GetN() << " points with histogram with " << h->GetNbinsX() << " points" << GEndl ;
        throw 1 ;
    }

    for(int i=0; i < g->GetN(); ++i) {
        // TGraphs are 0-indexed, TH1s are 1-indexed.
        int j = i+1;

        double x, y;
        g->GetPoint(i, x, y);

        g->SetPoint(i, x, y * h->GetBinContent(j));
        g->SetPointEYhigh(i, g->GetErrorYhigh(i) * h->GetBinContent(j));
        g->SetPointEYlow(i, g->GetErrorYlow(i) * h->GetBinContent(j));
    }

    return;
}

void Util::plotInterpolationScheme(RooWorkspace *w) {

    RooAbsData* data = w->data("obsData");
    RooArgSet funcs = w->allFunctions();
    TIterator* iter = funcs.createIterator() ;

    gDirectory->pwd();
    TDirectory* currentDir = gDirectory->CurrentDirectory();

    TFile* interpFile = new TFile("interpolation/interpFile.root","RECREATE");
    interpFile->cd();

    gStyle->SetOptStat(0);
    gStyle->SetOptTitle(0);

    RooAbsArg* parg(0);
    while((parg=(RooAbsArg*)iter->Next())) {
        if ( parg->ClassName()!=TString("PiecewiseInterpolation") ) { continue; }
        PiecewiseInterpolation* p = (PiecewiseInterpolation*)w->function( parg->GetName() );
        p->printAllInterpCodes();
        const RooArgList paramList =  p->paramList();
        const RooArgSet* observables = p->getObservables(data);
        TString obsName = TString( observables->contentsString() );
        TString sampleName= TString( parg->GetName() );
        for (int iParam = 0; iParam < paramList.getSize(); iParam++){
            TString parNameTemp = TString( paramList.at(iParam)->GetName() );
            TCanvas tempc(obsName+sampleName+parNameTemp,obsName+sampleName+parNameTemp,600,600);
            tempc.cd();
            TH2D* tempHisto = (TH2D*) p->createHistogram(obsName+","+parNameTemp);
            int nominalBin = tempHisto->GetYaxis()->FindBin(0.);
            TH1D* nominalHisto = tempHisto->ProjectionX(obsName+sampleName+parNameTemp+"nominal",nominalBin,nominalBin);
            nominalHisto->Write();
            tempHisto->Draw("SURF");
            tempc.Print("interpolation/"+sampleName+"_"+obsName+"_"+parNameTemp+".pdf");
            tempHisto->Write();
            for (int iBin = 1; iBin <= tempHisto->GetNbinsX(); iBin++){
                TString projectionName = obsName+sampleName+parNameTemp + std::to_string(iBin).c_str();
                TH1D* projectionY = tempHisto->ProjectionY(projectionName,iBin,iBin);
                TCanvas tempcProj(obsName+sampleName+projectionName,obsName+sampleName+projectionName,600,600);
                tempcProj.SetBottomMargin(0.15);
                tempcProj.SetLeftMargin(0.2);
                tempcProj.cd();
                projectionY->Draw("line");
                projectionY->GetXaxis()->SetTitle(parNameTemp);
                projectionY->GetXaxis()->SetTitleOffset(1.5);
                projectionY->GetXaxis()->SetRangeUser(-2,2);
                projectionY->GetYaxis()->SetTitle(obsName+" bin "+std::to_string(iBin).c_str());
                projectionY->GetYaxis()->SetTitleOffset(2.5);
                // Draw lines
                tempcProj.Update();
                double ymax = gPad->GetUymax();
                double ymin = gPad->GetUymin();
                double xmax = gPad->GetUxmax();
                double xmin = gPad->GetUxmin();
                double nominalVal = (projectionY->GetBinContent(projectionY->FindBin(0))+projectionY->GetBinContent(projectionY->FindBin(0)-1))/2.;
                TLine* line1 = new TLine(-1,ymin,-1,ymax);
                TLine* line2 = new TLine(1,ymin,1,ymax);
                TLine* line3 = new TLine(0,ymin,0,ymax);
                TLine* line4 = new TLine(xmin,nominalVal,xmax,nominalVal);
                line1->Draw();
                line2->Draw();
                line3->Draw();
                line4->Draw();
                projectionY->Draw("line same");
                projectionY->SetLineWidth(2);
                // Save canvas
                if (tempHisto->GetNbinsX()==1)
                    tempcProj.Print("interpolation/"+sampleName+"_"+obsName+"_"+parNameTemp+"_perBin.pdf");
                else if (iBin==1)
                    tempcProj.Print("interpolation/"+sampleName+"_"+obsName+"_"+parNameTemp+"_perBin.pdf(");
                else if (iBin>1 && iBin <tempHisto->GetNbinsX())
                    tempcProj.Print("interpolation/"+sampleName+"_"+obsName+"_"+parNameTemp+"_perBin.pdf");
                else
                    tempcProj.Print("interpolation/"+sampleName+"_"+obsName+"_"+parNameTemp+"_perBin.pdf)");
                projectionY->Write();
            }
        }
    }

    interpFile->Close();
    currentDir->cd();

}


//________________________________________________________________________________________________
void Util::getExpectedCLsFromHypoTest(HypoTestInverterResult* HTIR, int index, double *q)
{
    // Get expected CLs
    // See https://root.cern.ch/doc/master/HypoTestInverterPlot_8cxx_sourcehtml#l00150
    bool resultIsAsymptotic = ( !HTIR->GetNullTestStatDist(0) &&!HTIR->GetAltTestStatDist(0) );
    double p[7];
    double nsig1 = 1;
    double nsig2 = 2;
    p[0] = ROOT::Math::normal_cdf(-nsig2);
    p[1] = ROOT::Math::normal_cdf(-nsig1);
    p[2] = 0.5;
    p[3] = ROOT::Math::normal_cdf(nsig1);
    p[4] = ROOT::Math::normal_cdf(nsig2);

    SamplingDistribution * s = HTIR->GetExpectedPValueDist(index);
    const std::vector<double> & values = s->GetSamplingDistribution();
    
    if (resultIsAsymptotic) {
        double maxSigma = 5;//HTIR->fgAsymptoticMaxSigma;
        double dsig = 2* maxSigma/ (values.size() -1) ;
        int  i0 = (int) TMath::Floor ( ( -nsig2 +  maxSigma )/dsig + 0.5);
        int  i1 = (int) TMath::Floor ( (-nsig1 +  maxSigma )/dsig + 0.5);
        int  i2 = (int) TMath::Floor ( ( maxSigma)/dsig + 0.5);
        int  i3 = (int) TMath::Floor ( ( nsig1 + maxSigma)/dsig + 0.5);
        int  i4 = (int) TMath::Floor ( ( nsig2 + maxSigma)/dsig + 0.5);
        q[0] = values[i0];
        q[1] = values[i1];
        q[2] = values[i2];
        q[3] = values[i3];
        q[4] = values[i4];
    }
    else
    {
        double * x = const_cast<double *>(&values[0]); // need to changeTMath::Quantiles
        TMath::Quantiles(values.size(), 5, x,q,p,false);
    }
    //float CLsExp = q[2];
    //float CLsExpUp = q[1];
    //float CLsExpDw = q[3];
    delete s;

}

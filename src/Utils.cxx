// vim: ts=4:sw=4
#include "Utils.h"
#include "ConfigMgr.h"
#include "TMsgLogger.h"
#include "ChannelStyle.h"

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
#include "SigmaLR.h"
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
#include "RooMinuit.h"

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

#include "TF1.h"
#include "TH2D.h"
#include "TTree.h"
#include "TBranch.h"
#include "TGraph2D.h"
#include "TGraphAsymmErrors.h"
#include "TPad.h"
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

using namespace std;
using namespace RooFit;
using namespace RooStats;

namespace Util {
    static TMsgLogger Logger("Util");
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
//void Util::GenerateFitAndPlot(TString fcName, Bool_t drawBeforeFit, Bool_t drawAfterFit, Bool_t plotCorrelationMatrix, Bool_t plotSeparateComponents, Bool_t plotNLL ){
void Util::GenerateFitAndPlot(TString fcName, TString anaName, Bool_t drawBeforeFit, Bool_t drawAfterFit, Bool_t plotCorrelationMatrix, Bool_t plotSeparateComponents, Bool_t plotNLL, Bool_t minos, TString minosPars ){

  
    //RooAbsReal::defaultIntegratorConfig()->setEpsRel(1e-9) ;
    //RooAbsReal::defaultIntegratorConfig()->setEpsAbs(1e-9) ;

    ConfigMgr* mgr = ConfigMgr::getInstance();
    FitConfig* fc = mgr->getFitConfig(fcName);

    Logger << kINFO << " GenerateFitAndPlot for FitConfig = " << fc->m_name << GEndl;
    Logger << kINFO << "     analysisName = " << anaName << GEndl;
    Logger << kINFO << "     drawBeforeFit = " << drawBeforeFit << GEndl;
    Logger << kINFO << "     drawAfterFit = " << drawAfterFit << GEndl;
    Logger << kINFO << "     plotCorrelationMatrix = " << plotCorrelationMatrix << GEndl;
    Logger << kINFO << "     plotSeparateComponents = " << plotSeparateComponents << GEndl;
    Logger << kINFO << "     plotNLL = " << plotNLL << GEndl;
    Logger << kINFO << "     minos = " << minos << GEndl;
    Logger << kINFO << "     minosPars = " << minosPars << GEndl;

    RooWorkspace* w = GetWorkspaceFromFile(fc->m_inputWorkspaceFileName, "combined");
    if(w==NULL){
      Logger << kWARNING << "     RooWorkspace('combined') does not exist, trying workspace('w')" << GEndl;
      w = GetWorkspaceFromFile(fc->m_inputWorkspaceFileName, "w");
    }

    if(w==NULL){
      Logger << kERROR << "     Cannot find RooWorkspace, quitting " << GEndl;
      return;
    }

    Util::SetInterpolationCode(w,4); // MB 20130408: overwrite default - change from piece-wise linear to 6th order poly interp + linear extrapolation (also used in Higgs group)
    SaveInitialSnapshot(w);

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
    Bool_t lumiConst = kTRUE;
    //if (fc->m_signalChannels.size() > 0) 
        lumiConst = kFALSE;

    //  fit toy MC if specified. When left None, data is fit by default
    RooAbsData* toyMC = NULL;
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

    // set Errors of all parameters to 'natural' values before plotting/fitting
    resetAllErrors(w);

    // get a list of all floating parameters for all regions
    RooAbsPdf* simPdf = w->pdf("simPdf");
    ModelConfig*  mc = GetModelConfig(w);
    const RooArgSet* obsSet = mc->GetObservables();
    RooArgList floatPars = getFloatParList(*simPdf, *obsSet);

    // create an RooExpandedFitResult encompassing all the
    // regions/parameters & save it to workspace
    RooExpandedFitResult* expResultBefore = new RooExpandedFitResult(floatPars);
    ImportInWorkspace(w, expResultBefore, "RooExpandedFitResult_beforeFit");

    // plot before fit
    if (drawBeforeFit)
      PlotPdfWithComponents(w, fc->m_name, anaName, plotChannels, "beforeFit", expResultBefore, toyMC);

    //fit of all regions
    RooFitResult*  result = FitPdf(w, fitChannels, lumiConst, toyMC, "", minos, minosPars);

    if (result==NULL) return;
    
    // create an RooExpandedFitResult encompassing all the regions/parameters
    //  with the result & save it to workspace
    RooExpandedFitResult* expResultAfter = new RooExpandedFitResult(result, floatPars);
    ImportInWorkspace(w, expResultAfter, "RooExpandedFitResult_afterFit");
 
    // plot after fit
    if (drawAfterFit)
      PlotPdfWithComponents(w, fc->m_name, anaName, plotChannels, "afterFit", expResultAfter, toyMC);
    

    // plot each component of each region separately with propagated
    // error after fit  (interesting for debugging)
    if(plotSeparateComponents) 
        PlotSeparateComponents(w, fc->m_name, anaName, plotChannels,"afterFit", result,toyMC);

    //plot correlation matrix for result
    if(plotCorrelationMatrix)  
        PlotCorrelationMatrix(result, anaName);

    // plot likelihood
    Bool_t plotPLL = minos;
    if(plotNLL) {
      PlotNLL(w, expResultAfter, plotPLL, anaName, "", toyMC, minosPars, fitChannels, lumiConst);
    }

    if (toyMC) 
        WriteWorkspace(w, fc->m_inputWorkspaceFileName, toyMC->GetName());
    else 
        WriteWorkspace(w, fc->m_inputWorkspaceFileName);

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
    RooAbsData* data = (RooAbsData*) w->data("obsData");
    RooArgSet* params = (RooArgSet*) pdf->getParameters(*data) ;
    if(!w->loadSnapshot("snapshot_paramsVals_initial")) {
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


//_____________________________________________________________________________
RooFitResult* Util::FitPdf( RooWorkspace* w, TString fitRegions, Bool_t lumiConst, RooAbsData* inputData, TString suffix, Bool_t minos, TString minosPars)
{

    Logger << kINFO << " ------ Starting FitPdf with parameters:    fitRegions = " <<  fitRegions << GEndl;
    Logger << kINFO <<  "    inputData = " << inputData << "  suffix = " << suffix  << "  minos = " << minos << "  minosPars = " << minosPars  << GEndl;

    RooMsgService::instance().getStream(1).removeTopic(NumIntegration);

    //RooWorkspace* w = (RooWorkspace*) gDirectory->Get("w");
    if(w==NULL){ 
        Logger << kERROR << "Workspace not found, no fitting performed" << GEndl;
        return NULL; 
    }
    RooSimultaneous* pdf = (RooSimultaneous*) w->pdf("simPdf");
    // pdf->Print("t");

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
    //    if( datasetname.Contains("asimov")){
    //r = simPdfFitRegions->fitTo(*dataFitRegions,Save(),SumW2Error(kFALSE)); //MB no verbose :) ,Verbose(kTRUE));
    
    RooAbsPdf* pdf_FR = simPdfFitRegions;
    RooDataSet* data_FR = dataFitRegions;

    RooArgSet* allParams = pdf_FR->getParameters(data_FR);
    RooStats::RemoveConstantParameters(allParams);

    RooStats::ModelConfig* mc = Util::GetModelConfig( w );
    const RooArgSet* globObs = mc->GetGlobalObservables();

    RooAbsReal* nll = (RooNLLVar*) pdf_FR->createNLL(*data_FR, RooFit::GlobalObservables(*globObs), RooFit::Offset(true) ); //, RooFit::CloneData(kFALSE),RooFit::Constrain(*allParams),RooFit::SumW2Error(kFALSE));

    int minimPrintLevel = 1; //verbose;

    RooMinimizer minim(*nll);
    int strategy = ROOT::Math::MinimizerOptions::DefaultStrategy();
    minim.setStrategy( strategy);
    // use tolerance - but never smaller than 1 (default in RooMinimizer)
    double tol =  ROOT::Math::MinimizerOptions::DefaultTolerance();
    tol = std::max(tol,1.0); // 1.0 is the minimum value used in RooMinimizer
    minim.setEps( tol );
    //LM: RooMinimizer.setPrintLevel has +1 offset - so subtruct  here -1
    minim.setPrintLevel(minimPrintLevel-1);
    int status = -1;
    minim.optimizeConst(2);
    TString minimizer = "Minuit2"; //ROOT::Math::MinimizerOptions::DefaultMinimizerType(); 
    //TString minimizer = ROOT::Math::MinimizerOptions::DefaultMinimizerType(); 
    TString algorithm = ROOT::Math::MinimizerOptions::DefaultMinimizerAlgo(); 

    Logger << kINFO << "Util::FitPdf()  ........ using " << minimizer << " / " << algorithm << GEndl; 
    Logger << kINFO << " with strategy  " << strategy << " and tolerance " << tol << GEndl;


    //bool kickApplied(false);
    for (int tries = 1, maxtries = 4; tries <= maxtries; ++tries) {
        //	 status = minim.minimize(fMinimizer, ROOT::Math::MinimizerOptions::DefaultMinimizerAlgo().c_str());
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
            /*
            if (tries == 4 && !kickApplied) {
                Logger << kINFO << "    ----> trying fit with different starting values" << GEndl;
                RooFitResult* tmpResult = minim.save();
                const RooArgList& randList = tmpResult->randomizePars();
                *allParams = randList;
                delete tmpResult;
                tries=0;          // reset the fit cycle
                kickApplied=true; // do kick only once
            }
            */
        }
    }

    //RooFitResult * result = 0; 
    //double val(0);
	
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
      //val = r->minNll();
    }
    else { 
      Logger << kERROR << "FIT FAILED !- return a NaN NLL " << GEndl;
      //val =  TMath::QuietNaN();       
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
    //TCanvas* canVec[numPlots];
    //  RooPlot* frameVec[numPlots];

    //   RooAddPdf* combinedPdf = new RooAddPdf();
    //   RooDataSet* combinedData = new RooDataSet();
    //   RooRealVar* firstVar;
    //   RooRealVar* replaceVar;
    //   RooAbsPdf* firstPdf ;

    //   RooAbsPdf* replacePdf ;
    //   RooArgList* coefList;
    //   RooArgList* pdfList;

    RooWorkspace* wcomb = new RooWorkspace(wsname);

    TString allObs;

    // iterate over all the regions 
    for(unsigned int iVec=0; iVec<numPlots; iVec++){

        TString regionCatLabel = regionsVec[iVec];
        if( regionCat->setLabel(regionCatLabel,kTRUE)){  
            Logger << kINFO << " Label '" << regionCatLabel << "' is not a state of channelCat (see Table) " << GEndl; 
        }else{
            RooAbsPdf* regionPdf = (RooAbsPdf*) pdf->getPdf(regionCatLabel.Data());
            //regionPdf->Print();

            TString dataCatLabel = Form("channelCat==channelCat::%s",regionCatLabel.Data());
            RooDataSet* regionData = (RooDataSet*) data->reduce(dataCatLabel.Data());
            if(regionPdf==NULL || regionData==NULL){
                Logger << kWARNING << " Either the Pdf or the Dataset do not have an appropriate state for the region = " << regionCatLabel << ", check the Workspace file" << GEndl;
                Logger << kWARNING << " regionPdf = " << regionPdf << "   regionData = " << regionData << GEndl;  
                continue;
            }

            // regionData->Print("v");

            RooRealVar* regionVar =(RooRealVar*) ((RooArgSet*) regionPdf->getObservables(*regionData))->find(Form("obs_x_%s",regionCatLabel.Data()));
            //wcomb->import(*regionVar,RenameVariable(firstVar->GetName(),"obs"),RecycleConflictNodes(true) ) ;
            RooDataSet* rdata = (RooDataSet*)regionData->reduce(RooArgSet(*regionVar,*w->var("weightVar")));

            wcomb->import( *rdata, Rename( TString("obsData_")+TString(regionVar->GetName()) ), RenameVariable(regionVar->GetName(),"obs"), RecycleConflictNodes(true) );
            wcomb->import( *regionPdf, RenameVariable(regionVar->GetName(),"obs"), RecycleConflictNodes(true) );

        }
    }

    //  cout << GEndl << GEndl;

    wcomb->writeToFile(outfile);

    file->Close();
}


//__________________________________________________________________________________________________________________________________________________________
void Util::PlotPdfSumWithComponents(RooWorkspace* w, TString fcName, TString anaName, TString plotRegions, TString outputPrefix, RooFitResult* rFit, RooAbsData* inputData)
{

    Bool_t plotComponents=true;
    ConfigMgr* mgr = ConfigMgr::getInstance();
    FitConfig* fc __attribute__((unused)) = mgr->getFitConfig(fcName);

    cout << endl << endl << " ------ Starting Plot with parameters:   analysisName = " << fcName 
        << "    plotRegions = " <<  plotRegions <<  "  plotComponents = " << plotComponents << "  outputPrefix = " << outputPrefix  << endl << endl;

    RooMsgService::instance().getStream(1).removeTopic(NumIntegration);
    RooMsgService::instance().getStream(1).removeTopic(Plotting);


    if(w==NULL){ Logger << kERROR << " Workspace not found, no plotting performed" << GEndl << GEndl; return; }
    RooSimultaneous* pdf = (RooSimultaneous*) w->pdf("simPdf");
    //pdf->Print("t");

    RooAbsData* data = ( inputData!=0 ? inputData : (RooAbsData*)w->data("obsData") ); 

    RooCategory* regionCat = (RooCategory*) w->cat("channelCat");
    data->table(*((RooAbsCategory*)regionCat))->Print("v");

    if(plotRegions =="") plotRegions = "ALL";
    std::vector<TString> regionsVec = GetRegionsVec(plotRegions, regionCat);


    Logger << kWARNING << "Util::PlotPdfSumWithComponents() : " << plotRegions << GEndl;

    unsigned  int numPlots = regionsVec.size();  
    // TCanvas* canVec[numPlots];
    //  RooPlot* frameVec[numPlots];

    RooAddPdf* combinedPdf __attribute__((unused)) = new RooAddPdf();
    RooDataSet* combinedData __attribute__((unused)) = new RooDataSet();
    //RooRealVar* firstVar;
    //RooRealVar* replaceVar;
    //RooAbsPdf* firstPdf ;
    //RooAbsPdf* replacePdf ;
    //RooArgList* coefList;
    //RooArgList* pdfList;

    RooWorkspace* wcomb = new RooWorkspace("wcombination");

    TString allObs;

    // iterate over all the regions 
    for(unsigned int iVec=0; iVec<numPlots; iVec++){

        Logger << kWARNING << "Util::PlotPdfSumWithComponents() : " << regionsVec[iVec] << GEndl;

        TString regionCatLabel = regionsVec[iVec];
        if( regionCat->setLabel(regionCatLabel,kTRUE)){  Logger << kWARNING << GEndl << " Label '" << regionCatLabel << "' is not a state of channelCat (see Table) " << endl << endl << GEndl; }
        else{
            RooAbsPdf* regionPdf = (RooAbsPdf*) pdf->getPdf(regionCatLabel.Data());
            Logger << kINFO << " region pdf = " << GEndl;
            regionPdf->Print();

            TString dataCatLabel = Form("channelCat==channelCat::%s",regionCatLabel.Data());
            RooDataSet* regionData = (RooDataSet*) data->reduce(dataCatLabel.Data());
            if(regionPdf==NULL || regionData==NULL){ 
                Logger << kWARNING << " Either the Pdf or the Dataset do not have an appropriate state for the region = " << regionCatLabel << ", check the Workspace file" << GEndl;
                Logger << kWARNING << " regionPdf = " << regionPdf << "   regionData = " << regionData << GEndl;  
                continue; 
            }

            regionData->Print("v");

            RooRealVar* regionVar =(RooRealVar*) ((RooArgSet*) regionPdf->getObservables(*regionData))->find(Form("obs_x_%s",regionCatLabel.Data()));

            //wcomb->import(*regionVar,RenameVariable(firstVar->GetName(),"obs"),RecycleConflictNodes(true) ) ;

            RooDataSet* rdata = (RooDataSet*)regionData->reduce(RooArgSet(*regionVar,*w->var("weightVar")));

            wcomb->import( *rdata, Rename( TString("obsData_")+TString(regionVar->GetName()) ), RenameVariable(regionVar->GetName(),"obs"), RecycleConflictNodes(true) );  
            wcomb->import( *regionPdf, RenameVariable(regionVar->GetName(),"obs"), RecycleConflictNodes(true) );

        }
    }

    cout << endl << endl; 

    wcomb->writeToFile("wsmod.root");

}




//__________________________________________________________________________________________________________________________________________________________
void Util::PlotPdfWithComponents(RooWorkspace* w, TString fcName, TString anaName, TString plotRegions, TString outputPrefix, RooFitResult* rFit, RooAbsData* inputData)
{
    ConfigMgr* mgr = ConfigMgr::getInstance();
    FitConfig* fc = mgr->getFitConfig(fcName);

    Util::PlotPdfWithComponents(w, fc, anaName, plotRegions, outputPrefix, rFit, inputData);
}

//__________________________________________________________________________________________________________________________________________________________
void Util::PlotPdfWithComponents(RooWorkspace* w, FitConfig* fc, TString anaName, TString plotRegions, TString outputPrefix, RooFitResult* rFit, RooAbsData* inputData)
{
    Bool_t plotComponents=true;
    ConfigMgr* mgr = ConfigMgr::getInstance();
    std::string plotRatio = mgr->m_plotRatio;
    Logger << kINFO << " ------ Starting Plot with parameters:   analysisName = " << fc->m_name << " and " << anaName << GEndl; 
    Logger << kINFO << "    plotRegions = " <<  plotRegions <<  "  plotComponents = " << plotComponents << "  outputPrefix = " << outputPrefix  << GEndl;

    RooMsgService::instance().getStream(1).removeTopic(NumIntegration);
    RooMsgService::instance().getStream(1).removeTopic(Plotting);


    if(w==NULL){ 
        Logger << kERROR << "Workspace not found, no plotting performed" << GEndl; 
        return; 
    }
    RooSimultaneous* pdf = (RooSimultaneous*) w->pdf("simPdf");
    //pdf->Print("t");

    RooAbsData* data = ( inputData!=0 ? inputData : (RooAbsData*)w->data("obsData") ); 

    RooCategory* regionCat = (RooCategory*) w->cat("channelCat");
    data->table(*((RooAbsCategory*)regionCat))->Print("v");

    if(plotRegions =="") plotRegions = "ALL";
    std::vector<TString> regionsVec = GetRegionsVec(plotRegions, regionCat);

    unsigned  int numPlots = regionsVec.size();  
    TCanvas* canVec[numPlots];
    //  RooPlot* frameVec[numPlots];

    // iterate over all the regions 
    for(unsigned int iVec=0; iVec<numPlots; iVec++){
        TString regionCatLabel = regionsVec[iVec];

        if( regionCat->setLabel(regionCatLabel,kTRUE)){
            Logger << kINFO << " Label '" << regionCatLabel << "' is not a state of channelCat (see Table) " << GEndl; 
        } else {
            RooAbsPdf* regionPdf = (RooAbsPdf*) pdf->getPdf(regionCatLabel.Data());
            TString dataCatLabel = Form("channelCat==channelCat::%s",regionCatLabel.Data());
            RooAbsData* regionData = (RooAbsData*) data->reduce(dataCatLabel.Data());
            ChannelStyle style = fc->getChannelStyle(regionCatLabel);

            if(regionPdf==NULL || regionData==NULL){ 
                Logger << kWARNING << " Either the Pdf or the Dataset do not have an appropriate state for the region = " << regionCatLabel << ", check the Workspace file" << GEndl;
                Logger << kWARNING << " regionPdf = " << regionPdf << "   regionData = " << regionData << GEndl;  
                continue; 
            }
            RooRealVar* regionVar =(RooRealVar*) ((RooArgSet*) regionPdf->getObservables(*regionData))->find(Form("obs_x_%s",regionCatLabel.Data()));

            //create plot
            RooPlot* frame =  regionVar->frame(); 
            frame->SetName(Form("frame_%s_%s",regionCatLabel.Data(),outputPrefix.Data()));
            //  data->plotOn(frame,Cut(dataCatLabel),RooFit::DataError(RooAbsData::Poisson),MarkerColor(fc->getDataColor()),LineColor(fc->getDataColor()));

            regionData->plotOn(frame,RooFit::DataError(RooAbsData::Poisson),MarkerColor(style.getDataColor()),LineColor(style.getDataColor()));
            if(style.getRemoveEmptyBins()){
                Logger << kINFO << "RemoveEmptyDataBins() removing empty bin points from data histogram on plot " << frame->GetName() << GEndl;
                RemoveEmptyDataBins(w, frame);
            }
            //RemoveEmptyDataBins(w, frame);

            // normalize pdf to number of expected events, not to number of events in dataset
	    //  double normCount = regionPdf->expectedEvents(*regionVar);
            //regionPdf->plotOn(frame,Normalization(normCount,RooAbsReal::NumEvent),Precision(1e-5),LineColor(style.getTotalPdfColor()));
            regionPdf->plotOn(frame,Normalization(1,RooAbsReal::RelativeExpected),Precision(1e-5),LineColor(style.getTotalPdfColor()));

            // plot components
            if(plotComponents)  
	      AddComponentsToPlot(w, fc, frame, regionPdf, regionData, regionVar, regionCatLabel.Data(),style);

            // visualize error of fit
            if(rFit != NULL) { 	
                //regionPdf->plotOn(frame,Normalization(normCount,RooAbsReal::NumEvent),Precision(1e-5),FillColor(style.getErrorFillColor()),FillStyle(style.getErrorFillStyle()),LineColor(style.getErrorLineColor()),LineStyle(style.getErrorLineStyle()),VisualizeError(*rFit));
                regionPdf->plotOn(frame,Normalization(1,RooAbsReal::RelativeExpected),Precision(1e-5),FillColor(style.getErrorFillColor()),FillStyle(style.getErrorFillStyle()),LineColor(style.getErrorLineColor()),LineStyle(style.getErrorLineStyle()),VisualizeError(*rFit));
            }

            // re-plot data and pdf, so they are on top of error and components
            //regionPdf->plotOn(frame,Normalization(normCount,RooAbsReal::NumEvent),Precision(1e-5),LineColor(style.getTotalPdfColor()));
            regionPdf->plotOn(frame,Normalization(1,RooAbsReal::RelativeExpected),Precision(1e-5),LineColor(style.getTotalPdfColor()));

            regionData->plotOn(frame,RooFit::DataError(RooAbsData::Poisson),MarkerColor(style.getDataColor()),LineColor(style.getDataColor()));
            if(style.getRemoveEmptyBins()) RemoveEmptyDataBins(w, frame);
            //RemoveEmptyDataBins(w, frame);

            TString canName=Form("can_%s_%s",regionCatLabel.Data(),outputPrefix.Data());
            canVec[iVec] = new TCanvas(canName,canName, 700, 600);

            // two pads, one for 'standard' plot, one for data/MC ratio
            TPad *pad1 = new TPad(Form("%s_pad1",canName.Data()),Form("%s_pad1",canName.Data()),0.,0.305,.99,1);
            pad1->SetBottomMargin(0.005);
            pad1->SetFillColor(kWhite);
            pad1->SetTickx();
            pad1->SetTicky();
            TPad *pad2 = new TPad(Form("%s_pad2",canName.Data()),Form("%s_pad2",canName.Data()),0.,0.01,.99,0.295);
            pad2->SetTopMargin(0.005);
            pad2->SetBottomMargin(0.3);
            pad2->SetFillColor(kWhite);

            if(style.getLogY()) pad1->SetLogy();
            pad1->Draw();
            pad2->Draw();

            pad1->cd();

            frame->SetMinimum(style.getMinY());
	
            if( fabs(style.getMaxY() + 999.) > 0.000001){
                frame->SetMaximum(style.getMaxY());
            }

            // draw frame
            frame->SetTitle(""); 
            frame->GetXaxis()->SetLabelSize(0.); 
            frame->Draw();

            // add cosmetics
            if( (fabs(style.getATLASLabelX() + 1.) > 0.000001) &&  (fabs(style.getATLASLabelY() + 1.) > 0.000001) ){
                ATLASLabel(style.getATLASLabelX(),style.getATLASLabelY(),style.getATLASLabelText()) ; //"for approval");
            }

            if( style.getShowLumi() ){
                Float_t lumi =  style.getLumi(); 
                AddText(0.175,0.775,Form("#int Ldt = %.1f fb^{-1}",lumi));
            }

            // uncomments to label the channel
            //if (canName.Contains("Mu")) AddText(0.05,0.60,"1 muon, #geq 7 jets");
            //else if (canName.Contains("El")) AddText(0.05,0.60,"1 electron, #geq 7 jets");

            TLegend* leg = style.getTLegend();
            // default TLegend built from sample names/colors
            if(leg == NULL){
                leg = new TLegend(0.5,0.44,0.895,0.895,"");
                leg->SetFillStyle(0);
                leg->SetFillColor(0);
                leg->SetBorderSize(0);
                TLegendEntry* entry=leg->AddEntry("","Data 2012 (#sqrt{s}=8 TeV)","p") ;
                entry->SetMarkerColor(style.getDataColor());
                entry->SetMarkerStyle(20);
                entry=leg->AddEntry("","Standard Model","lf") ;
                entry->SetLineColor(style.getTotalPdfColor());
                entry->SetFillColor(style.getErrorFillColor());
                entry->SetFillStyle(style.getErrorFillStyle());

                // add components to legend
                TString RRSPdfName = Form("%s_model",regionCatLabel.Data()); 
                RooRealSumPdf* RRSPdf = (RooRealSumPdf*) regionPdf->getComponents()->find(RRSPdfName);
                RooArgList RRSComponentsList =  RRSPdf->funcList();
                RooLinkedListIter iter = RRSComponentsList.iterator() ;
                RooProduct* component;
                vector<TString> compNameVec;
                compNameVec.clear();
                while( (component = (RooProduct*) iter.Next())) { 
                    TString  componentName = component->GetName();
                    compNameVec.push_back(componentName);
                }

                char NP[10];
                TString NP_str;
                for( int iComp = (compNameVec.size()-1) ; iComp>-1; iComp--){
	    Int_t  compPlotColor    = ( (fc!=0) ? style.getSampleColor(compNameVec[iComp]) : iComp );
                    TString  compShortName  = ( (fc!=0) ? style.getSampleName(compNameVec[iComp])  : "" );

                    TString legName = compShortName; //"";
                    //if(compShortName.Contains("BG")) legName = "single top & diboson";
                    for (int inp=0; inp<6; inp++) {
                        sprintf(NP,"Np%d",inp);
                        NP_str = NP;
                        if(compShortName.Contains("WZ") && compShortName.Contains(NP)) legName = "WZ+"+NP_str;
                        if(compShortName.Contains("Top") && compShortName.Contains(NP)) legName = "t#bar{t}+"+NP_str;
                    }
                    //if(compShortName.Contains("QCD")) legName = "multijets (data estimate)";
                    if(compShortName.Contains("Discovery")) legName = "signal";
                    //
                    if(compShortName.Contains("WZpT0GeV"))   legName = "W/Z (p_{T}^{V,Truth}=0-50GeV)";
                    if(compShortName.Contains("WZpT50GeV"))  legName = "W/Z (p_{T}^{V,Truth}=50-100GeV)";
                    if(compShortName.Contains("WZpT100GeV")) legName = "W/Z (p_{T}^{V,Truth}=100-150GeV)";
                    if(compShortName.Contains("WZpT150GeV")) legName = "W/Z (p_{T}^{V,Truth}=150-200GeV)";
                    if(compShortName.Contains("WZpT200GeV")) legName = "W/Z (p_{T}^{V,Truth}=200-250GeV)";
                    if(compShortName.Contains("WZpT250GeV")) legName = "W/Z (p_{T}^{V,Truth}=250GeV-)";
                    //
                    entry=leg->AddEntry("",legName.Data(),"f") ;
                    entry->SetLineColor(compPlotColor);
                    entry->SetFillColor(compPlotColor);
                    entry->SetFillStyle(1001);
                }
            }
            leg->Draw();	
            //      frameVec[iVec]=frame;

            // now make/draw the ratio histogram
            pad2->cd();

            // data/pdf ratio histograms is plotted by RooPlot.ratioHist()
            RooPlot* frame_dummy =  regionVar->frame(); 
            data->plotOn(frame_dummy,Cut(dataCatLabel),RooFit::DataError(RooAbsData::Poisson));
            // normalize pdf to number of expected events, not to number of events in dataset
            //regionPdf->plotOn(frame_dummy,Normalization(normCount,RooAbsReal::NumEvent),Precision(1e-5));      
            regionPdf->plotOn(frame_dummy,Normalization(1,RooAbsReal::RelativeExpected),Precision(1e-5));

            // Construct a histogram with the ratio of the data w.r.t the pdf curve
            RooHist* hratio = NULL;
            if(plotRatio=="ratio")  hratio = (RooHist*) frame_dummy->ratioHist() ;
            else if(plotRatio=="pull") hratio = (RooHist*) frame_dummy->pullHist() ;
            hratio->SetMarkerColor(style.getDataColor());
            hratio->SetLineColor(style.getDataColor());

            // Construct a histogram with the ratio of the pdf curve w.r.t the pdf curve +/- 1 sigma
            RooCurve* hratioPdfError = new RooCurve;
            if (rFit != NULL)  hratioPdfError = MakePdfErrorRatioHist(w, regionData, regionPdf, regionVar, rFit);
            hratioPdfError->SetFillColor(style.getErrorFillColor());
            hratioPdfError->SetFillStyle(style.getErrorFillStyle());
            hratioPdfError->SetLineColor(style.getErrorLineColor());
            hratioPdfError->SetLineStyle(style.getErrorLineStyle());

            // Create a new frame to draw the residual distribution and add the distribution to the frame
            RooPlot* frame2 = regionVar->frame() ;
            if(plotRatio=="ratio")  hratio->SetTitle("Ratio Distribution");
            else  if(plotRatio=="pull") hratio->SetTitle("Pull Distribution");
            // only add PdfErrorsPlot when the plot shows ratio, not with pull
            if (rFit != NULL && plotRatio=="ratio")   frame2->addPlotable(hratioPdfError,"F");
            frame2->addPlotable(hratio,"P");

            // ratio plot cosmetics
            int firstbin = frame_dummy->GetXaxis()->GetFirst();
            int lastbin = frame_dummy->GetXaxis()->GetLast();
            double xmax = frame_dummy->GetXaxis()->GetBinUpEdge(lastbin) ;
            double xmin = frame_dummy->GetXaxis()->GetBinLowEdge(firstbin) ;

            TLine* l = new TLine(xmin,1.,xmax,1.);
            TLine* l2 = new TLine(xmin,0.5,xmax,0.5);
            TLine* l3 = new TLine(xmin,1.5,xmax,1.5);
            TLine* l4 = new TLine(xmin,2.,xmax,2.);
            TLine* l5 = new TLine(xmin,2.5,xmax,2.5);
            l->SetLineWidth(1);
            l->SetLineStyle(2);
            l2->SetLineStyle(3);
            l3->SetLineStyle(3);
            l4->SetLineStyle(3);
            l5->SetLineStyle(3);


            TLine* lp1 = new TLine(xmin,1.,xmax,1.);	
            TLine* lp2 = new TLine(xmin,2.,xmax,2.);	
            TLine* lp3 = new TLine(xmin,3.,xmax,3.);
            TLine* lp4 = new TLine(xmin,4.,xmax,4.);
            TLine* lp5 = new TLine(xmin,5.,xmax,5.);
            TLine* lp6 = new TLine(xmin,-1.,xmax,-1.);	
            TLine* lp7 = new TLine(xmin,-2.,xmax,-2.);	
            TLine* lp8 = new TLine(xmin,-3.,xmax,-3.);
            TLine* lp9 = new TLine(xmin,-4.,xmax,-4.);
            TLine* lp10 = new TLine(xmin,-5.,xmax,-5.);

            lp1->SetLineStyle(3);
            lp2->SetLineStyle(3);
            lp3->SetLineStyle(3);
            lp4->SetLineStyle(3);
            lp5->SetLineStyle(3);
            lp6->SetLineStyle(3);
            lp7->SetLineStyle(3);
            lp8->SetLineStyle(3);
            lp9->SetLineStyle(3);
            lp10->SetLineStyle(3);

            if(plotRatio=="ratio"){	
                frame2->addObject(l);
                frame2->addObject(l2);
                frame2->addObject(l3);
                frame2->addObject(l4);
                frame2->addObject(l5);
            } else if(plotRatio=="pull"){
                frame2->addObject(lp1);
                frame2->addObject(lp2);
                frame2->addObject(lp3);
                frame2->addObject(lp4);
                frame2->addObject(lp5);
                frame2->addObject(lp6);
                frame2->addObject(lp7);
                frame2->addObject(lp8);
                frame2->addObject(lp9);
                frame2->addObject(lp10);
            }

            Double_t lowerlimit = 0.; 
            Double_t upperlimit = 2.2; 
            if (plotRatio=="pull"){ 
                lowerlimit = -5.7; upperlimit = 5.7;
            }
	  
            frame2->SetMinimum(lowerlimit);
            frame2->SetMaximum(upperlimit);
	   
            if(plotRatio=="ratio") 
                frame2->GetYaxis()->SetTitle("Data / SM");
            else if(plotRatio=="pull")
                frame2->GetYaxis()->SetTitle("Pull");

            if(style.getTitleX() != "")  
                frame2->GetXaxis()->SetTitle(style.getTitleX());
            else  
                frame2->GetXaxis()->SetTitle(GetXTitle(regionVar)); //Name());

            if(style.getTitleY() != "")  
                frame->GetYaxis()->SetTitle(style.getTitleY());

            frame2->GetYaxis()->SetLabelSize(0.13);
            frame2->GetYaxis()->SetNdivisions(504);         
            frame2->GetXaxis()->SetLabelSize(0.13);
            frame2->GetYaxis()->SetTitleSize(0.14);
            frame2->GetXaxis()->SetTitleSize(0.14);
            frame2->GetYaxis()->SetTitleOffset(0.35);
            frame2->GetXaxis()->SetTitleOffset(1.);
            frame2->GetYaxis()->SetLabelOffset(0.01);
            frame2->GetXaxis()->SetLabelOffset(0.03);
            frame2->GetXaxis()->SetTickLength(0.06);

            frame2->SetTitle("");
            frame2->GetYaxis()->CenterTitle(); 
            frame2->Draw();

            canVec[iVec]->SaveAs("results/"+anaName+"/"+canName+".pdf");
            canVec[iVec]->SaveAs("results/"+anaName+"/"+canName+".eps");

        }
    }

}

//_____________________________________________________________________________
void Util::AddComponentsToPlot(RooWorkspace* w, FitConfig* fc, RooPlot* frame, RooAbsPdf* regionPdf, RooAbsData* regionData, RooRealVar* obsRegion, TString regionCatLabel, ChannelStyle style) {

    // regionPdf->Print("t");
    TString RRSPdfName = Form("%s_model",regionCatLabel.Data()); 
    RooRealSumPdf* RRSPdf = (RooRealSumPdf*) regionPdf->getComponents()->find(RRSPdfName);
    Logger << kINFO << "Adding Components of Region-Model = " << RRSPdfName << " to plot" << GEndl;

    RooArgList RRSComponentsList =  RRSPdf->funcList();
    //RRSComponentsList.Print("v");

    //  if (regionData!=0) regionData->Print();

    RooLinkedListIter iter = RRSComponentsList.iterator() ;
    RooProduct* component;
    vector<TString> compNameVec;
    vector <double> compFracVec;
    vector<TString> compStackNameVec;
    vector <double> compStackFracVec;
    compNameVec.clear();
    compStackNameVec.clear();
    compFracVec.clear();
    compStackFracVec.clear();

    TString binWidthName =  Form("binWidth_obs_x_%s_0",regionCatLabel.Data());
    RooRealVar* regionBinWidth = ((RooRealVar*) RRSPdf->getVariables()->find(Form("binWidth_obs_x_%s_0",regionCatLabel.Data()))) ;

    if(regionBinWidth==NULL){
        Logger << kWARNING << " bindWidth variable not found for region(" << regionCatLabel << "),   PLOTTING COMPONENTS WILL BE WRONG " << GEndl ;
    }

    while( (component = (RooProduct*) iter.Next())) { 
        TString  componentName = component->GetName();
        TString stackComponentName = componentName; 
        if(!compStackNameVec.empty()){  stackComponentName  = Form("%s,%s",compStackNameVec.back().Data() ,componentName.Data()); }
        compNameVec.push_back(componentName);
        compStackNameVec.push_back(stackComponentName);

        double componentFrac = GetComponentFrac(w,componentName,RRSPdfName,obsRegion,regionBinWidth) ;
        double stackComponentFrac = componentFrac; 
        if(!compStackFracVec.empty()){  stackComponentFrac  = compStackFracVec.back() + componentFrac; } 
        compFracVec.push_back(componentFrac);
        compStackFracVec.push_back(stackComponentFrac);

    }

    // normalize data to expected number of events 
    double normCount = regionPdf->expectedEvents(*obsRegion);

    for( int iVec = (compFracVec.size()-1) ; iVec>-1; iVec--){
        Int_t  compPlotColor = ( (fc!=0) ? style.getSampleColor(compNameVec[iVec]) : iVec );

        if(compPlotColor < 0) compPlotColor = kMagenta;

        regionPdf->plotOn(frame,Components(compStackNameVec[iVec].Data()),FillColor(compPlotColor),FillStyle(1001),DrawOption("F"),Normalization(compStackFracVec[iVec]*normCount,RooAbsReal::NumEvent),Precision(1e-5));

    }
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

    //vector<TString> samplesVec = fc->m_sampleNames;

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
            TString RRSPdfName = Form("%s_model",regionCatLabel.Data()); 
            RooRealSumPdf* RRSPdf = (RooRealSumPdf*) regionPdf->getComponents()->find(RRSPdfName);
            TString binWidthName =  Form("binWidth_obs_x_%s_0",regionCatLabel.Data());
            RooRealVar* regionBinWidth = ((RooRealVar*) RRSPdf->getVariables()->find(Form("binWidth_obs_x_%s_0",regionCatLabel.Data()))) ;
            if(regionBinWidth==NULL){
                Logger << kWARNING << " bindWidth variable not found for region(" << regionCatLabel << "),   PLOTTING COMPONENTS WILL BE WRONG " << GEndl ;
            }

            vector<double> regionCompFracVec = GetAllComponentFracInRegion(w, regionCatLabel, regionPdf, regionVar,regionBinWidth);
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

            //RooPlot* frameVec[numRegions][numComps];

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
                    regionPdf->plotOn(frame,Components(regionCompNameVec[iComp].Data()),VisualizeError(*rFit),FillColor(kCyan),Precision(1e-5),Normalization(regionCompFracVec[iComp]*normCount,RooAbsReal::NumEvent));

                regionPdf->plotOn(frame,Components(regionCompNameVec[iComp].Data()),LineColor(compPlotColor),Normalization(regionCompFracVec[iComp]*normCount,RooAbsReal::NumEvent),Precision(1e-5));

                canVec[iVec]->cd(iComp+1);
                frame->SetMinimum(0.);
                frame->Draw();
                //frameVec[iVec][iComp]=frame;

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

    if(w==NULL){ 
        Logger << kINFO << " Workspace not found, no plotting performed" << GEndl; 
        return; 
    }
    RooSimultaneous* pdf = (RooSimultaneous*) w->pdf("simPdf");

    RooAbsData* data = ( inputData!=0 ? inputData : (RooAbsData*)w->data("obsData") ); 
    RooCategory* regionCat = (RooCategory*) w->cat("channelCat");
    data->table(*((RooAbsCategory*)regionCat))->Print("v");

    ///////////////////////////////////////////////////////////////////

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
    
    /////////////////////////////////////////////////////////////////

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
      nll->plotOn(frame, ShiftToZero());
      frame->SetMinimum(0.);
      // To be able to see the 1/2 sigma
      frame->SetMaximum(2.5);
	
      const char* curvename = 0;
      RooCurve* curve = (RooCurve*) frame->findObject(curvename,RooCurve::Class()) ;
      //  frame->remove();
      Double_t curveMax = curve->getYAxisMax();
      // safety for weird RooPlots where curve goes to infinity in first/last bin(s)
      if (curveMax > 0. && !std::isinf(curveMax) && !std::isnan(curveMax) )  { ; } // frame->SetMaximum(curveMax * 2.); 
      else if(curveMax > 0. && (std::isinf(curveMax) || std::isnan(curveMax))){

// 	for(Int_t iBin=0;  iBin < curve->GetN(); iBin++){
//           Double_t xBin = 0.;
//           Double_t yBin = -1.;     
//           curve->GetPoint(iBin,xBin,yBin) ;
// 	  cout << "  BEFORE:   iBin = " << iBin << " xBin = " << xBin << " yBin = " << yBin << endl;		    
//         }
	

	// 	cout << endl << " BEFORE  curve->GetN() = " << curve->GetN() << endl;
	for(Int_t iBin=1;  iBin < curve->GetN()-1; iBin++){
          Double_t xBin = 0.;
          Double_t yBin = -1.;     
          curve->GetPoint(iBin,xBin,yBin) ;
	  //	  cout << " iBin = " << iBin << " xBin = " << xBin << " yBin = " << yBin << endl;		    
          if(std::isinf(yBin)  || std::isnan(yBin)){
            curve->RemovePoint(iBin);
            Logger << kWARNING << " Removing bin = " << iBin  << " as it was either inf or nan from NLL plot for parameter = " << parName<< GEndl;
	    iBin--;
          }
        }	
	   
// 	cout << " AFTER  curve->GetN() = " << curve->GetN() << endl;
// 	for(Int_t iBin=0;  iBin < curve->GetN(); iBin++){
//           Double_t xBin = 0.;
//           Double_t yBin = -1.;     
//           curve->GetPoint(iBin,xBin,yBin) ;
// 	  cout  << "  AFTER:   iBin = " << iBin << " xBin = " << xBin << " yBin = " << yBin << endl;		    
//         }	

        Int_t iBin = 1;
        Double_t xFirstBin = 0.;
        Double_t yFirstBin = -1.;	
        while ( (yFirstBin<0 || std::isinf(yFirstBin)  || std::isnan(yFirstBin) )&& iBin < curve->GetN()-1){
          iBin++;
          curve->GetPoint(iBin,xFirstBin,yFirstBin) ;
	  //	  cout << endl << " iBin = " << iBin << " xFirstBin = " << xFirstBin << " yFirstBin = " << yFirstBin << endl;		    
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
	  //	  cout << endl << " iBin = " << iBin << " xLastBin = " << xLastBin << " yLastBin = " << yLastBin << endl;		    
	  if(std::isinf(yLastBin)  || std::isnan(yLastBin)){
            curve->RemovePoint(iBin);
            Logger << kWARNING << " Removing bin = " << iBin  << " as it was either inf or nan from NLL plot for parameter = " << parName<< GEndl;
          }
        }
        curveMax = yLastBin>yFirstBin ? yLastBin : yFirstBin;      
        //frame->SetMaximum(curveMax * 2. ); 
      }
      //else { frame->SetMaximum(1000.); }

      // plot cosmetics
      int firstbin = frame->GetXaxis()->GetFirst();
      int lastbin = frame->GetXaxis()->GetLast();
      double xmax = frame->GetXaxis()->GetBinUpEdge(lastbin) ;
      double xmin = frame->GetXaxis()->GetBinLowEdge(firstbin) ;
	
      //  cout << " firstbin = " << firstbin << " lastbin = " << lastbin << " xmax = " << xmax << " xmin = " << xmin << endl;

      TLine* l1 = new TLine(xmin,2.,xmax,2.);
      TLine* l2 = new TLine(xmin,0.5,xmax,0.5);
	
      l1->SetLineStyle(3);
      l2->SetLineStyle(3);
	
      frame->addObject(l1);
      frame->addObject(l2);
	
      RooAbsReal* pll(0);
      if(plotPLL) { 
        pll = nll->createProfile(*par) ;
        pll->plotOn(frame,LineColor(kRed),LineStyle(kDashed),NumCPU(4)); 
      }

      cout << " frame->GetMaximum() = " << frame->GetMaximum() << " frame->GetMinimum() = " << frame->GetMinimum() << endl;

      TString canName=Form("can_NLL_%s_%s_%s",outputPrefix.Data(),rFit->GetName(),parName.Data());
      canVec[iPar] = new TCanvas(canName,canName,600,600); 
      canVec[iPar]->cd();
      frame->Draw();  

      TLegend* leg = new TLegend(0.55,0.65,0.85,0.9,"");
      leg->SetFillStyle(0);
      leg->SetFillColor(0);
      leg->SetBorderSize(0);
      TLegendEntry* entry=leg->AddEntry("","NLL","l") ;
      entry->SetLineColor(kBlue);
      if(plotPLL) {	
        entry=leg->AddEntry("","PLL","l") ;
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
      canVec[iPar]->SaveAs("results/"+anaName+"/"+canName+".eps");
      //  }

    }

    delete nll ;

}

//_____________________________________________________________________________
TH2D* Util::PlotCorrelationMatrix(RooFitResult* rFit, TString anaName){


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

    gStyle->SetPalette(51) ;
    gStyle->SetMarkerSize(1.45);
    gStyle->SetMarkerColor(kWhite);
    gStyle->SetPaintTextFormat("4.2f") ;

    if(numPars<5)    gStyle->SetMarkerSize(1.4);
    else if(numPars<10)    gStyle->SetMarkerSize(1.1);
    else if(numPars<20)    gStyle->SetMarkerSize(0.85);
    else if(numPars<40)    gStyle->SetMarkerSize(0.5);
    else     gStyle->SetMarkerSize(0.25);


    TH2D* h_corr = (TH2D*) rFit->correlationHist(Form("h_corr_%s",rFit->GetName())); 

    Double_t labelSize = orig_LabelSize;
    if(numPars<5) labelSize = 0.05;
    else if(numPars<10)   labelSize = 0.04;
    else if(numPars<20)   labelSize = 0.025;
    else if(numPars<40)   labelSize = 0.02;
    else labelSize = 0.015;

    h_corr->GetXaxis()->SetLabelSize(labelSize);
    h_corr->GetYaxis()->SetLabelSize(labelSize);

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

    gStyle->SetMarkerSize(orig_MarkerSize);
    gStyle->SetMarkerColor(orig_MarkerColor);
    gStyle->SetPaintTextFormat(orig_PaintTextFormat) ;
    gStyle->SetLabelSize(orig_LabelSize);
    gStyle->SetOptStat(00000000);

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
TString Util::GetShortCompName(TString compName) {

    TString shortCompName = "empty";
    if(compName.Contains("WZ")) shortCompName = "WZ";
    else if(compName.Contains("Top"))   shortCompName = "Top";
    else if(compName.Contains("SU")) shortCompName = "SUSY"; 

    if(shortCompName == "empty"){ Logger << kWARNING << " component(" << compName << ")  in GetCompName not recognized " << GEndl; }

    return shortCompName;
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
Double_t Util::GetComponentFrac(RooWorkspace* w, const char* Component, const char* RRSPdfName, RooRealVar* observable, RooRealVar* binWidth){

    RooAbsReal*  i_RRSPdf = ((RooAbsPdf*)w->pdf(RRSPdfName))->createIntegral(RooArgSet(*observable));
    RooAbsReal*  i_component =   ((RooProduct*)w->obj(Component))->createIntegral(RooArgSet(*observable));

    Double_t Int_RRSPdf = i_RRSPdf->getVal();
    Double_t Int_component = i_component->getVal();

    Double_t componentFrac = 0.;
    if(Int_RRSPdf != 0.) componentFrac =  Int_component * binWidth->getVal() / Int_RRSPdf;

    delete  i_RRSPdf;
    delete  i_component;

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
RooStats::ModelConfig* Util::GetModelConfig( const RooWorkspace* w, const TString& mcName, const bool& verbose  ) {
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
Util::doFreeFit( RooWorkspace* w, RooDataSet* inputdata, const bool& verbose, const bool& resetAfterFit )
{
    // fit to reset the workspace

    if(w==0){
        Logger << kERROR << "Input workspace is null!" << GEndl;
        return NULL;
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

    /// do the fit
    //RooFitResult* result = pdf->fitTo(*data,Save()); //PrintLevel(verbose?1:-1),Verbose(verbose?1:0),Save());



    /////////////////////////////////////////////////////////////

    RooArgSet* allParams = pdf->getParameters(data);
    RooStats::RemoveConstantParameters(allParams);

    const RooArgSet* globObs = mc->GetGlobalObservables();

    RooAbsReal* nll = (RooNLLVar*) pdf->createNLL(*data, RooFit::GlobalObservables(*globObs), RooFit::Offset(true)); //, RooFit::CloneData(kFALSE),RooFit::Constrain(*allParams));

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
    int status = -1;
    minim.optimizeConst(2);
    TString minimizer = ROOT::Math::MinimizerOptions::DefaultMinimizerType(); 
    TString algorithm = ROOT::Math::MinimizerOptions::DefaultMinimizerAlgo(); 

    Logger << kINFO << "Util::doFreeFit()  ........ using " << minimizer << " / " << algorithm 
        << " with strategy  " << strategy << " and tolerance " << tol << GEndl;

    //bool kickApplied(false);
    for (int tries = 1, maxtries = 4; tries <= maxtries; ++tries) {
        //	 status = minim.minimize(fMinimizer, ROOT::Math::MinimizerOptions::DefaultMinimizerAlgo().c_str());
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
            } /*
            if (tries == 4 && !kickApplied) {
                Logger << kINFO << "    ----> trying fit with different starting values" << GEndl;
                RooFitResult* tmpResult = minim.save();
                const RooArgList& randList = tmpResult->randomizePars();
                *allParams = randList;
                delete tmpResult;
                tries=0;          // reset the fit cycle
                kickApplied=true; // do kick only once
            } */
        }
    }

    RooFitResult * result = 0; 
    //double val(0);

    if (status%100 == 0) { // ignore errors in Hesse or in Improve
        result = minim.save();
        //val = result->minNll();
    }
    else { 
        Logger << kERROR << "FIT FAILED !- return a NaN NLL " << GEndl;
        //val =  TMath::QuietNaN();       
    }

    //minim.optimizeConst(false);
    //if (result) delete result;

    //if (verbose < 2) RooMsgService::instance().setGlobalKillBelow(msglevel);  

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
    return ( new RooMCStudy( *pdf, *obsset, RooFit::FitOptions("r") ) ) ;
}





//________________________________________________________________________________________________
void Util::ATLASLabel(Double_t x,Double_t y,const char* text,Color_t color) 
{

    TLatex l; //l.SetTextAlign(12); l.SetTextSize(tsize); 
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

    TLatex l; //l.SetTextAlign(12); l.SetTextSize(tsize); 
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



//_____________________________________________________________________________
RooAbsReal* Util::GetComponent(RooWorkspace* w, TString component, TString region, bool exactRegionName){  //, unsigned int bin){

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

    // get the binWidth variable, to be multiplied with component RooProduct, for a complete component RooFormulaVar, as used in RooRealSumPdf
    TString binWidthName =  Form("binWidth_obs_x_%s_0",regionFullName.Data());
    RooRealVar* regionBinWidth = ((RooRealVar*) regionPdf->getVariables()->find(Form("binWidth_obs_x_%s_0",regionFullName.Data()))) ;

    if(regionBinWidth==NULL){
        Logger << kWARNING << " bindWidth variable not found for region(" << regionFullName << "),   RETURNING COMPONENTS WILL BE WRONG " << GEndl ;
        return NULL;
    }

    // find the correct RooProduct
    vector<TString> regionCompNameVec = GetAllComponentNamesInRegion(regionFullName, regionPdf);
    RooArgList compFuncList;
    RooArgList compCoefList;
    for(unsigned int iReg=0; iReg<regionCompNameVec.size(); iReg++){
      for(unsigned int iComp=0; iComp< componentVec.size(); iComp++){
	Logger << kDEBUG << " GetComponent: regionCompNameVec[" << iReg << "] = " << regionCompNameVec[iReg] << " componentVec[" << iComp << "] = " << componentVec[iComp] << GEndl;
	TString target = "_"+componentVec[iComp]+"_";
	if(  regionCompNameVec[iReg].Contains(target.Data())) {
	  compFuncList.add(*(RooProduct*)w->obj(regionCompNameVec[iReg]));
	  compCoefList.add(*regionBinWidth);
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
    RooAbsReal* compFunc = compRRS->createIntegral(RooArgSet(*regionVar));

    if(compFunc == NULL){
        Logger << kERROR << " compRooProduct not found for region(" << regionFullName << "), component(" << component << ")   RETURNING COMPONENTS WILL BE WRONG " << GEndl ;
        return NULL;
    }

    RooFormulaVar* form_frac = new RooFormulaVar("form_fracError","@0",RooArgList(*compFunc));
    form_frac->SetName(Form("form_frac_region_%s_%s",region.Data(),compName.Data()));
    form_frac->SetTitle(Form("form_frac_region_%s_%s",region.Data(),compName.Data()));

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

    // get the binWidth variable, to be multiplied with component RooProduct, for a complete component RooFormulaVar, as used in RooRealSumPdf
    TString binWidthName =  Form("binWidth_obs_x_%s_0",regionFullName.Data());
    RooRealVar* regionBinWidth = ((RooRealVar*) regionPdf->getVariables()->find(Form("binWidth_obs_x_%s_0",regionFullName.Data()))) ;

    if(regionBinWidth==NULL){
        Logger << kWARNING << " bindWidth variable not found for region(" << regionFullName << "),   RETURNING COMPONENTS WILL BE WRONG " << GEndl ;
        return 0;
    }

    // find the correct RooProduct
    vector<TString> regionCompNameVec = GetAllComponentNamesInRegion(regionFullName, regionPdf);
    RooArgList compFuncList;
    RooArgList compCoefList;
    for(unsigned int iReg=0; iReg<regionCompNameVec.size(); iReg++){
        for(unsigned int iComp=0; iComp< componentVec.size(); iComp++){
	  TString target = "_"+componentVec[iComp]+"_";
	  if(  regionCompNameVec[iReg].Contains(target.Data())) {
	    compFuncList.add(*(RooProduct*)w->obj(regionCompNameVec[iReg]));
	    compCoefList.add(*regionBinWidth);
	  }
        } 
    }

    if (compFuncList.getSize()==0 || compCoefList.getSize()==0 || compCoefList.getSize()!=compFuncList.getSize()){
        Logger << kERROR << " Something wrong with compFuncList or compCoefList in Util::GetComponent() "<< GEndl;
        return 0.;
    }

    TString compName = "comps";
    for(unsigned int iVec=0; iVec<componentVec.size(); iVec++){
        compName += "_" + componentVec[iVec];
    }

    // get the full RRSPdf of this region
    TString RRSPdfName = Form("%s_model",regionFullName.Data()); 

    double componentFrac = 0.;
    for(unsigned int iReg=0; iReg<regionCompNameVec.size(); iReg++){
        for(unsigned int iComp=0; iComp< componentVec.size(); iComp++){
	  TString target = "_"+componentVec[iComp]+"_";
	  if(  regionCompNameVec[iReg].Contains(target.Data())) {
	    componentFrac += GetComponentFrac(w,regionCompNameVec[iReg],RRSPdfName,regionVar,regionBinWidth) ;
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




// //_____________________________________________________________________________
// RooAbsReal* Util::GetRegionPdfIntegral(RooWorkspace* w, TString region){  //, unsigned int bin){

//   if(w==NULL){ cout << GEndl << " Workspace not found, no GetRegionPdf performed" << endl << GEndl; return NULL; }

//   RooCategory* regionCat = (RooCategory*) w->cat("channelCat");
//   TString regionFullName = GetFullRegionName(regionCat, region);

//   RooSimultaneous* pdf = (RooSimultaneous*) w->pdf("simPdf");
//   RooAbsPdf* regionPdf = (RooAbsPdf*) pdf->getPdf(regionFullName.Data());

//   RooAbsData* data = (RooAbsData*)w->data("obsData"); 
//   TString dataCatLabel = Form("channelCat==channelCat::%s",regionFullName.Data());
//   RooAbsData* regionData = (RooAbsData*) data->reduce(dataCatLabel.Data());

//   if(regionPdf==NULL || regionData==NULL){ 
//     cout << " Either the Pdf or the Dataset do not have an appropriate state for the region = " << region << ", check the Workspace file" << GEndl;
//     cout << " regionPdf = " << regionPdf << "   regionData = " << regionData << GEndl;  
//     return NULL; 
//   }
//   RooRealVar* regionVar =(RooRealVar*) ((RooArgSet*) regionPdf->getObservables(*regionData))->find(Form("obs_x_%s",regionFullName.Data()));

//   RooAbsReal* regionPdfInt = regionPdf->createIntegral(RooArgSet(*regionVar));

//   if(regionPdfInt == NULL){
//     cout << " region pdf integral not found in region(" << regionFullName << ")   RETURNING COMPONENTS WILL BE WRONG " << GEndl ;
//     return NULL;
//   }

//   cout << " Adding " << regionPdfInt->GetName() << " to workspace" << GEndl;
//   w->import( *regionPdfInt,kTRUE);
//   gDirectory->Add(regionPdfInt);

//   return regionPdfInt;

// }


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
vector<double> Util::GetAllComponentFracInRegion(RooWorkspace* w, TString region, RooAbsPdf* regionPdf, RooRealVar* obsRegion,RooRealVar* regionBinWidth){

    TString RRSPdfName = Form("%s_model",region.Data()); 
    RooRealSumPdf* RRSPdf = (RooRealSumPdf*) regionPdf->getComponents()->find(RRSPdfName);

    RooArgList RRSComponentsList =  RRSPdf->funcList();

    RooLinkedListIter iter = RRSComponentsList.iterator() ;
    RooProduct* component;
    vector<double> compFracVec;
    compFracVec.clear();

    while( (component = (RooProduct*) iter.Next())) { 
        TString  componentName = component->GetName();
        double componentFrac = GetComponentFrac(w,componentName,RRSPdfName,obsRegion,regionBinWidth) ;
        compFracVec.push_back(componentFrac);
    }

    return compFracVec;
}


//_____________________________________________________________________________
double Util::GetPropagatedError(RooAbsReal* var, const RooFitResult& fr, const bool& doAsym) 
{

    // copied from RooAbsReal : fixed bug in reducedCovarianceMatrix (!)
    // add more text (sometimes) ;)

    // Calculate error on self by propagated errors on parameters with correlations as given by fit result
    // The linearly propagated error is calculated as follows
    //                                    T           
    // error(x) = F_a(x) * Corr(a,a') F_a'(x)
    //
    // where     F_a(x) = [ f(x,a+da) - f(x,a-da) ] / 2, with f(x) this function and 'da' taken from the fit result
    //       Corr(a,a') = the correlation matrix from the fit result
    //

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
    // For the given workspace,
    // find the input systematic with
    // the given name and shift that
    // systematic by 1-sigma

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
	    // Get the uncertainty on the Lumi:
            RooRealVar* lumiSigma = (RooRealVar*) lumiConstr->findServer(0);
            sigma = lumiSigma->getVal();

            RooRealVar* nominalLumi = wspace->var("nominalLumi");
            double val_nom = nominalLumi->getVal();

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
            /*
               cout << string(UncertaintyName) << endl;
               cout << "here1" << endl;
               cout << "constraint " << constraint << endl;
               cout << "constraint->IsA() " << constraint->IsA() << endl;
               cout << constraint->IsA()->GetName() << endl;
               cout << "here2" << endl;
               */
            if( ConstraintType == "" ) {
                //cout << "Error: Strange constraint type for Stat Uncertainties " << ConstraintType << GEndl;
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
        //var->setErrorHi(abs(sigma));
        //var->setErrorLo(-abs(sigma));
        //if( ShiftUp ) var->setVal( val_hi );
        //else          var->setVal( val_low );
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
    // For the given workspace,
    // find the input systematic with
    // the given name and shift that
    // systematic by 1-sigma

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
    // For the given workspace,
    // find the input systematic with
    // the given name and shift that
    // systematic by 1-sigma

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
        else if ( UncertaintyName.BeginsWith("nom_gamma_stat") ) {
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
void Util::RemoveEmptyDataBins(RooWorkspace* w, RooPlot* frame){

    //Logger << kINFO << " Util::RemoveEmptyDataBins() " << GEndl ;

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

        //cout << " i = " << i << "   x= " << x << " y = " << y << GEndl;

        if( fabs(y)< 0.0000001 && hist->GetErrorYhigh(i) > 0.){
            //      hist->SetPointError(i,hist->GetErrorXlow(i),hist->GetErrorXhigh(i),hist->GetErrorYlow(i),0.) ;
            //  cout << " removing point i = " << i << GEndl;
            hist->RemovePoint(i);
            // RemovePoint makes GetN() one less, hence to loop over all points, "i" has to become one lower (only not for the last bin to protect against infinite loop)
            if(i != hist->GetN()) --i;
        }
    }

    return;

}



//________________________________________________________________________________________________________________________________________
RooCurve* Util::MakePdfErrorRatioHist(RooWorkspace* w, RooAbsData* regionData, RooAbsPdf* regionPdf, RooRealVar* regionVar, RooFitResult* rFit, Double_t Nsigma){

    // curvename=0 means that the last RooCurve is taken from the RooPlot
    const char* curvename = 0;

    RooPlot* frame =  regionVar->frame(); 
    regionData->plotOn(frame, RooFit::DataError(RooAbsData::Poisson));

    // normalize pdf to number of expected events, not to number of events in dataset
    double normCount = regionPdf->expectedEvents(*regionVar);
    //regionPdf->plotOn(frame,Normalization(normCount,RooAbsReal::NumEvent),Precision(1e-5));
    regionPdf->plotOn(frame,Normalization(1,RooAbsReal::RelativeExpected),Precision(1e-5));
    RooCurve* curveNom = (RooCurve*) frame->findObject(curvename,RooCurve::Class()) ;
    if (!curveNom) {
        Logger << kERROR << "Util::MakePdfErrorRatioHist(" << frame->GetName() << ") cannot find curveNom" << curveNom->GetName() << GEndl ;
        return 0 ;
    }

    if(rFit != NULL) regionPdf->plotOn(frame,Normalization(normCount,RooAbsReal::NumEvent),Precision(1e-5),FillColor(kBlue-5),FillStyle(3004),VisualizeError(*rFit,Nsigma));

    // Find curve object
    RooCurve* curveError = (RooCurve*) frame->findObject(curvename,RooCurve::Class()) ;
    if (!curveError) {
        Logger << kERROR << "Util::makePdfErrorRatioHist(" << frame->GetName() << ") cannot find curveError" << GEndl ;
        return 0 ;
    }

    RooCurve* ratioBand = new RooCurve ;
    ratioBand->SetName(Form("%s_ratio_errorband",curveNom->GetName())) ;
    ratioBand->SetLineWidth(1) ;
    ratioBand->SetLineColor(kBlue-5);
    ratioBand->SetFillColor(kBlue-5);
    ratioBand->SetFillStyle(3004);
    
    Int_t j = 0;
    Bool_t bottomCurve = kFALSE;
    for(Int_t i=1; i<curveError->GetN()-1; i++){
        Double_t x = 0.;
        Double_t y = 0.;
        curveError->GetPoint(i,x,y) ;
      
        // errorBand curve has twice as many points as does a normal/nominal (pdf) curve
        //  first it walks through all +1 sigma points (topCurve), then the -1 sigma points (bottomCurve)
        //   to divide the errorCurve by the pdfCurve, we need to count back for the pdfCurve once we're in the middle of errorCurve
        if( i >= (curveNom->GetN()-1) ) bottomCurve = kTRUE;

        Double_t xNom = x;
        Double_t yNom = y;

        // each errorCurve has two more points just outside the plot, so we need to treat them separately
        if( i == (curveNom->GetN() - 1) ||  i == curveNom->GetN() ){
          //  xNom = x;
          //  yNom = 0.;
            ratioBand->addPoint(x, 0.);   
	    //            ratioBand->addPoint(x,((y - yNom) / y + 1.) );
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
	  //            ratioBand->addPoint(x, (y - yNom) / yNom + 1.);  
	  ratioBand->addPoint(x, (y / yNom));  
        } else { 
	  //            ratioBand->addPoint(x, (y - yNom));       	    
	  ratioBand->addPoint(x, 0.);       	    
        }
    }

    return ratioBand;
}



//_____________________________________________________________________________
void Util::SetPdfParError(RooWorkspace* w, RooAbsPdf* regionPdf, double Nsigma){

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
TString Util::GetXTitle(RooRealVar* regionVar){

    TString varName = regionVar->GetName();
    TString outName = varName;

    if( varName.Contains("_met/meff")) outName = "E_{T}^{miss}/m_{eff}"; 
    else if( varName.Contains("_met")) outName = "E_{T}^{miss} [GeV]";
    else if( varName.Contains("_mt")) outName = "m_{T} [GeV]";
    else if( varName.Contains("_cuts")) outName = "Region";
    else if( varName.Contains("_nBJet50")) outName = "N b-jets (p_{T}>50 GeV)";
    else if( varName.Contains("_nBJet30")) outName = "N b-jets (p_{T}>30 GeV)";
    else if( varName.Contains("_nBJet")) outName = "N b-jets (p_{T}>20 GeV)";
    else if( varName.Contains("_nJet50")) outName = "N jets (p_{T}>50 GeV)";
    else if( varName.Contains("_nJet30")) outName = "N jets (p_{T}>30 GeV)";
    else if( varName.Contains("_nJet")) outName = "N jets";
    else if( varName.Contains("_MR")) outName = "M_{R}' [GeV]";
    else if( varName.Contains("_mll")) outName = "m_{ll} [GeV]";
    else if( varName.Contains("_Wpt")) outName = "p_{T}^{W} [GeV]";
    else if( varName.Contains("_Zpt")) outName = "p_{T}^{Z} [GeV]";
    else if( varName.Contains("_ht")) outName = "H_{T} [GeV]";
    else if( varName.Contains("_meff6")) outName = "6-jet Effective Mass [GeV]";
    else if( varName.Contains("_meff4")) outName = "4-jet Effective Mass [GeV]";
    else if( varName.Contains("_meff")) outName = "m_{eff} [GeV]";
    else if( varName.Contains("_R")) outName = "R";
    else if(  varName.Contains("_Wpt")) outName = "p_{T}^{W} [GeV]"; 
    else if(  varName.Contains("_Zpt")) outName = "p_{T}^{Z} [GeV]"; 
    else if(  varName.Contains("_lep1Pt")) outName = "Leading lepton p_{T} [GeV]";
    else if(  varName.Contains("_lep2Pt")) outName = "p_{T}^{lep2} [GeV]"; 
    else if(  varName.Contains("_jet1Pt")) outName = "Leading jet p_{T} [GeV]";
    else if(  varName.Contains("_jet2Pt")) outName = "p_{T}^{jet2} [GeV]"; 
    else if(  varName.Contains("_jet3Pt")) outName = "p_{T}^{jet3} [GeV]"; 
    else if(  varName.Contains("_jet4Pt")) outName = "p_{T}^{jet4} [GeV]"; 
    else if(  varName.Contains("_jet5Pt")) outName = "p_{T}^{jet5} [GeV]"; 
    else if(  varName.Contains("_jet6Pt")) outName = "p_{T}^{jet6} [GeV]"; 
    else if(  varName.Contains("_jet7Pt")) outName = "p_{T}^{jet7} [GeV]";  
    return outName;
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



void
Util::PlotYieldPLL(RooWorkspace* w, RooAbsReal* nll, RooAbsReal* bkgf, RooFitResult* r)
{
  // naive first estimate of bkg value and (large) 2-sigma error.
  double bval = bkgf->getVal();
  double berr = ( r!=0 ? Util::GetPropagatedError(bkgf,*r) : 4.0 * TMath::Sqrt(bval) );
  if (bval==0 && berr==0) { berr = 2.0; }

  double floatParInitVal[10000] ;
  char   floatParName[10000][100] ;
  int nFloatParInitVal(0) ;
  RooArgList ral_floats = r->floatParsFinal() ;
  TIterator* floatParIter = ral_floats.createIterator() ;
  {
    RooRealVar* par ;
    while ( (par = (RooRealVar*) floatParIter->Next()) ) {
      sprintf( floatParName[nFloatParInitVal], "%s", par->GetName() ) ;
      floatParInitVal[nFloatParInitVal] = par->getVal() ;
      nFloatParInitVal++ ;
    }
  }


  // scan parameter
  RooRealVar* b = new RooRealVar("b", "background yield", bval, (bval-berr>=0 ? bval-berr : 0.0), bval+berr);

  // lagrange constant
  RooRealVar* width = new RooRealVar("width", "lagrange constant", 100.);
  
  printf("\n\n Unbiased best value for new POI %s is : %7.1f\n\n", bkgf->GetName(), bkgf->getVal() ) ;
  double best_poi_val = bkgf->getVal() ;
  
  char minuit_formula[10000] ;
  sprintf( minuit_formula, "%s+%s*(%s-%s)*(%s-%s)",
	   nll->GetName(),
	   width->GetName(),
	   bkgf->GetName(), b->GetName(),
	   bkgf->GetName(), b->GetName()
	   ) ;

  char weight_formula[10000] ;
  sprintf( weight_formula, "%s*(%s-%s)*(%s-%s)",
           width->GetName(),
           bkgf->GetName(), b->GetName(),
           bkgf->GetName(), b->GetName()
           ) ;

  
  printf("\n\n Creating new minuit variable with formula: %s\n\n", minuit_formula ) ;
  RooFormulaVar* new_minuit_var = new RooFormulaVar("new_minuit_var", minuit_formula,
						    RooArgList( *nll,
								*width,
								*bkgf, *b,
								*bkgf, *b
								) ) ;

  RooFormulaVar* weight_var = new RooFormulaVar("weight_var", weight_formula,
                                                    RooArgList( *width,
                                                                *bkgf, *b,
                                                                *bkgf, *b
                                                                ) ) ; 
  
  printf("\n\n Current value is %.2f\n\n",
	 new_minuit_var->getVal() ) ;
  
  RooMinuit* rminuit = new RooMinuit( *new_minuit_var ) ;

  //RooMinuit* rminuit = new RooMinuit( *nll ) ;

//////////////////////////

  if (false) {
    RooStats::ModelConfig* mc = Util::GetModelConfig(w);

    if(mc==0){
        Logger << kERROR << "ModelConfig is null!" << GEndl;
        return;
    }

    RooAbsPdf* pdf = mc->GetPdf();
    const RooArgSet* obsset = mc->GetObservables();

    if((pdf==0)||(obsset==0)){
        Logger << kERROR << "pdf or observables not found" <<GEndl;
        return;
    }

    TIterator* iter = obsset->createIterator() ;
    RooAbsArg* arg ;
    while( (arg=(RooAbsArg*)iter->Next()) ) {
        if(arg->InheritsFrom("RooRealVar") && !arg->isConstant()){
            TString UncertaintyName = arg->GetName();
            RooRealVar* var = w->var( UncertaintyName.Data() );
            var->setConstant();
        }
    }
    delete iter;
  }

////////////////////////////

  if (true) {
    rminuit->migrad();
    rminuit->hesse();

    return; 
  }
    
  RooAbsReal* plot_var = nll ;
  
  printf("\n\n Current value is %.2f\n\n",
	 plot_var->getVal() ) ;
  
  //rminuit->setPrintLevel(verbLevel-1) ;
  //if ( verbLevel <=0 ) { rminuit->setNoWarn() ; }
  

  //-- If POI range is -1 to -1, automatically determine the range using the set value.

  int npoiPoints = 50;

  double poiMinVal = -1.;
  double poiMaxVal = -1.;
  double startPoiVal = bkgf->getVal();

  if ( poiMinVal < 0. && poiMaxVal < 0. ) {
    
    printf("\n\n Automatic determination of scan range.\n\n") ;
    
    if ( startPoiVal <= 0. ) {
      printf("\n\n *** POI starting value zero or negative %g.  Quit.\n\n\n", startPoiVal ) ;
      return ;
    }
    
    poiMinVal = startPoiVal - 3.5 * sqrt(startPoiVal) ;
    poiMaxVal = startPoiVal + 6.0 * sqrt(startPoiVal) ;
    
    if ( poiMinVal < 0. ) { poiMinVal = 0. ; }
    
    printf("    Start val = %g.   Scan range:   %g  to  %g\n\n", startPoiVal, poiMinVal, poiMaxVal ) ;
        
  }
  


  //----------------------------------------------------------------------------------------------


  double poiVals_scanDown[1000] ;
  double nllVals_scanDown[1000] ;
       
  //-- Do scan down from best value.

  printf("\n\n +++++ Starting scan down from best value.\n\n") ;

  double minNllVal(1.e9) ;

  for ( int poivi=0; poivi < npoiPoints/2 ; poivi++ ) {

    ////double poiValue = poiMinVal + poivi*(poiMaxVal-poiMinVal)/(1.*(npoiPoints-1)) ;
    double poiValue = best_poi_val - poivi*(best_poi_val-poiMinVal)/(1.*(npoiPoints/2-1)) ;

    b -> setVal( poiValue ) ;
    b -> setConstant( kTRUE ) ;
    
    //+++++++++++++++++++++++++++++++++++

    rminuit->migrad() ;
    rminuit->hesse() ;
    RooFitResult* rfr = rminuit->save() ;

    //+++++++++++++++++++++++++++++++++++


    //if ( verbLevel > 0 ) { rfr->Print("v") ; }
        
    float fit_minuit_var_val = rfr->minNll() ;
    
    printf(" %02d : poi constraint = %.2f : allvars : MinuitVar, createNLL, PV, POI :    %.5f   %.5f   %.5f\n",
	   poivi, b->getVal(), fit_minuit_var_val, nll->getVal(), bkgf->getVal() ) ;
    cout << flush ;
        
    poiVals_scanDown[poivi] = bkgf->getVal() ;
    nllVals_scanDown[poivi] = weight_var->getVal() ; // plot_var->getVal() ;
    
    if ( nllVals_scanDown[poivi] < minNllVal ) { minNllVal = nllVals_scanDown[poivi] ; }
    
    delete rfr ;
    
  } // poivi


  printf("\n\n +++++ Resetting floats to best fit values.\n\n") ;

  for ( int pi=0; pi<nFloatParInitVal; pi++ ) {
    RooRealVar* par = w->var( floatParName[pi] ) ;
    par->setVal( floatParInitVal[pi] ) ;
  } // pi.
  



  printf("\n\n +++++ Starting scan up from best value.\n\n") ;
  
  //-- Now do scan up.
  
  double poiVals_scanUp[1000] ;
  double nllVals_scanUp[1000] ;
  
  for ( int poivi=0; poivi < npoiPoints/2 ; poivi++ ) {
    
    double poiValue = best_poi_val + poivi*(poiMaxVal-best_poi_val)/(1.*(npoiPoints/2-1)) ;
    
    b -> setVal( poiValue ) ;
    b -> setConstant( kTRUE ) ;
    
    
    //+++++++++++++++++++++++++++++++++++
    
    rminuit->migrad() ;
    rminuit->hesse() ;
    RooFitResult* rfr = rminuit->save() ;
    
    //+++++++++++++++++++++++++++++++++++
        
    float fit_minuit_var_val = rfr->minNll() ;
    
    printf(" %02d : poi constraint = %.2f : allvars : MinuitVar, createNLL, PV, POI :   %.5f   %.5f   %.5f\n",
	   poivi, b->getVal(), fit_minuit_var_val, nll->getVal(), bkgf->getVal() ) ;
    cout << flush ;
    
    poiVals_scanUp[poivi] = bkgf->getVal() ;
    nllVals_scanUp[poivi] = weight_var->getVal() ;  // plot_var->getVal() ;
    
    if ( nllVals_scanUp[poivi] < minNllVal ) { minNllVal = nllVals_scanUp[poivi] ; }
    
    delete rfr ;
        
  } // poivi
  
  

       double poiVals[1000] ;
       double nllVals[1000] ;

       int pointCount(0) ;
       for ( int pi=0; pi<npoiPoints/2; pi++ ) {
          poiVals[pi] = poiVals_scanDown[(npoiPoints/2-1)-pi] ;
          nllVals[pi] = nllVals_scanDown[(npoiPoints/2-1)-pi] ;
          pointCount++ ;
       }
       for ( int pi=1; pi<npoiPoints/2; pi++ ) {
          poiVals[pointCount] = poiVals_scanUp[pi] ;
          nllVals[pointCount] = nllVals_scanUp[pi] ;
          pointCount++ ;
       }
       npoiPoints = pointCount ;

       printf("\n\n --- TGraph arrays:\n") ;
       for ( int i=0; i<npoiPoints; i++ ) {
          printf("  %2d : poi = %6.1f, nll = %g\n", i, poiVals[i], nllVals[i] ) ;
       }
       printf("\n\n") ;

       double nllDiffVals[1000] ;

       double poiAtMinlnL(-1.) ;
       double poiAtMinusDelta2(-1.) ;
       double poiAtPlusDelta2(-1.) ;
       for ( int poivi=0; poivi < npoiPoints ; poivi++ ) {
          nllDiffVals[poivi] = 2.*(nllVals[poivi] - minNllVal) ;
          double poiValue = poiMinVal + poivi*(poiMaxVal-poiMinVal)/(1.*npoiPoints) ;
          if ( nllDiffVals[poivi] < 0.01 ) { poiAtMinlnL = poiValue ; }
          if ( poiAtMinusDelta2 < 0. && nllDiffVals[poivi] < 2.5 ) { poiAtMinusDelta2 = poiValue ; }
          if ( poiAtMinlnL > 0. && poiAtPlusDelta2 < 0. && nllDiffVals[poivi] > 2.0 ) { poiAtPlusDelta2 = poiValue ; }
       } // poivi

       printf("\n\n Estimates for poi at delta ln L = -2, 0, +2:  %g ,   %g ,   %g\n\n", poiAtMinusDelta2, poiAtMinlnL, poiAtPlusDelta2 ) ;


  

       ///////////////////////////////////////////////////////////////////


       //--- Main canvas

       TCanvas* cscan = (TCanvas*) gDirectory->FindObject("cscan") ;
       if ( cscan == 0x0 ) {
          printf("\n Creating canvas.\n\n") ;
          cscan = new TCanvas("cscan","Delta nll") ;
       }


       char gname[1000] ;

       TGraph* graph = new TGraph( npoiPoints, poiVals, nllDiffVals ) ;
       sprintf( gname, "scan_%s", bkgf->GetName() ) ;
       graph->SetName( gname ) ;

       double poiBest(-1.) ;
       double poiMinus1stdv(-1.) ;
       double poiPlus1stdv(-1.) ;
       double poiMinus2stdv(-1.) ;
       double poiPlus2stdv(-1.) ;
       double twoDeltalnLMin(1e9) ;

       int nscan(1000) ;
       for ( int xi=0; xi<nscan; xi++ ) {

          double x = poiVals[0] + xi*(poiVals[npoiPoints-1]-poiVals[0])/(nscan-1) ;

          double twoDeltalnL = graph -> Eval( x, 0, "S" ) ;

          if ( poiMinus1stdv < 0. && twoDeltalnL < 1.0 ) { poiMinus1stdv = x ; printf(" set m1 : %d, x=%g, 2dnll=%g\n", xi, x, twoDeltalnL) ;}
          if ( poiMinus2stdv < 0. && twoDeltalnL < 4.0 ) { poiMinus2stdv = x ; printf(" set m2 : %d, x=%g, 2dnll=%g\n", xi, x, twoDeltalnL) ;}
          if ( twoDeltalnL < twoDeltalnLMin ) { poiBest = x ; twoDeltalnLMin = twoDeltalnL ; }
          if ( twoDeltalnLMin < 0.3 && poiPlus1stdv < 0. && twoDeltalnL > 1.0 ) { poiPlus1stdv = x ; printf(" set p1 : %d, x=%g, 2dnll=%g\n", xi, x, twoDeltalnL) ;}
          if ( twoDeltalnLMin < 0.3 && poiPlus2stdv < 0. && twoDeltalnL > 4.0 ) { poiPlus2stdv = x ; printf(" set p2 : %d, x=%g, 2dnll=%g\n", xi, x, twoDeltalnL) ;}

          if ( xi%100 == 0 ) { printf( " %4d : poi=%6.2f,  2DeltalnL = %6.2f\n", xi, x, twoDeltalnL ) ; }

       }
       printf("\n\n POI estimate :  %g  +%g  -%g    [%g,%g],   two sigma errors: +%g  -%g   [%g,%g]\n\n",
               poiBest,
               (poiPlus1stdv-poiBest), (poiBest-poiMinus1stdv), poiMinus1stdv, poiPlus1stdv,
               (poiPlus2stdv-poiBest), (poiBest-poiMinus2stdv), poiMinus2stdv, poiPlus2stdv
               ) ;

       const char* new_poi_name = bkgf->GetName();

       printf(" %s val,pm1sig,pm2sig: %7.2f  %7.2f  %7.2f  %7.2f  %7.2f\n",
	      bkgf->GetName(), poiBest, (poiPlus1stdv-poiBest), (poiBest-poiMinus1stdv), (poiPlus2stdv-poiBest), (poiBest-poiMinus2stdv) ) ;

       double ymax = 10.;
       char htitle[1000] ;
       sprintf(htitle, "%s profile likelihood scan: -2ln(L/Lm)", new_poi_name ) ;
       TH1F* hscan = new TH1F("hscan", htitle, 10, poiMinVal, poiMaxVal ) ;
       hscan->SetMinimum(0.) ;
       hscan->SetMaximum(ymax) ;


       hscan->DrawCopy() ;
       graph->SetLineColor(4) ;
       graph->SetLineWidth(3) ;
       graph->Draw("CP") ;
       gPad->SetGridx(1) ;
       gPad->SetGridy(1) ;
       cscan->Update() ;

       TLine* line = new TLine() ;
       line->SetLineColor(2) ;
       line->DrawLine(poiMinVal, 1., poiPlus1stdv, 1.) ;
       line->DrawLine(poiMinus1stdv,0., poiMinus1stdv, 1.) ;
       line->DrawLine(poiPlus1stdv ,0., poiPlus1stdv , 1.) ;

       TText* text = new TText() ;
       text->SetTextSize(0.04) ;
       char tstring[1000] ;

       sprintf( tstring, "%s = %.1f +%.1f -%.1f", new_poi_name, poiBest, (poiPlus1stdv-poiBest), (poiBest-poiMinus1stdv) ) ;
       text -> DrawTextNDC( 0.15, 0.85, tstring ) ;

       sprintf( tstring, "68%% interval [%.1f,  %.1f]", poiMinus1stdv, poiPlus1stdv ) ;
       text -> DrawTextNDC( 0.15, 0.78, tstring ) ;


       char hname[1000] ;
       sprintf( hname, "hscanout_%s", new_poi_name ) ;
       TH1F* hsout = new TH1F( hname,"scan results",4,0.,4.) ;
       double obsVal(-1.) ;
       hsout->SetBinContent(1, obsVal ) ;
       hsout->SetBinContent(2, poiPlus1stdv ) ;
       hsout->SetBinContent(3, poiBest ) ;
       hsout->SetBinContent(4, poiMinus1stdv ) ;
       TAxis* xaxis = hsout->GetXaxis() ;
       xaxis->SetBinLabel(1,"Observed val.") ;
       xaxis->SetBinLabel(2,"Model+1sd") ;
       xaxis->SetBinLabel(3,"Model") ;
       xaxis->SetBinLabel(4,"Model-1sd") ;

       char outrootfile[10000] ;
       sprintf( outrootfile, "scan-ff-bs-%s.root", new_poi_name ) ;

       char outpdffile[10000] ;
       sprintf( outpdffile, "scan-ff-bs-%s.pdf", new_poi_name ) ;

       cscan->Update() ; cscan->Draw() ;

       printf("\n Saving %s\n", outpdffile ) ;
       cscan->SaveAs( outpdffile ) ;



       //--- save in root file

       printf("\n Saving %s\n", outrootfile ) ;
       TFile fout(outrootfile,"recreate") ;
       graph->Write() ;
       hsout->Write() ;
       fout.Close() ;
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



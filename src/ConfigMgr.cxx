// vim: ts=4:sw=4
/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Class  : ConfigMgr                                                             *
 * Created: December 2011                                                         *
 *                                                                                *
 * Description:                                                                   *
 *      Implementation (see header for description)                               *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/

//SusyFitter includes
#include "TMsgLogger.h"
#include "ConfigMgr.h"
#include "Utils.h"
#include "StatTools.h"

//Root/RooFit/RooStats includes
#include "TSystem.h"
#include "TFile.h"
#include "TTree.h"
#include "RooMCStudy.h"
#include "RooFitResult.h"
//#include "RooStats/HypoTestInverterResult.h"
#include "RooRandom.h"
#include "RooRealIntegral.h"


using namespace std;


//_______________________________________________________________________________________
ConfigMgr::ConfigMgr() : m_logger("ConfigMgrCPP") { 
    m_nToys = 1000;
    m_calcType = 0;
    m_testStatType = 3;
    m_status = "Unkwn";
    m_saveTree=false;
    m_doHypoTest=false;
    m_useCLs=true;
    m_useScanRange=false;
    m_scanRangeMin=-1;
    m_scanRangeMax=-1;
    m_fixSigXSec=false;
    m_runOnlyNominalXSec=false;
    m_doUL=true;
    m_seed=0;
    m_nPoints=10;
    m_muValGen=0.0;  
    m_removeEmptyBins=false;
    m_useAsimovSet=false;
    m_plotRatio="ratio"; //options: "ratio", "pull", "none"
}


//_______________________________________________________________________________________
FitConfig* ConfigMgr::addFitConfig(const TString& name){
    FitConfig* fc = new FitConfig(name);
    m_fitConfigs.push_back(fc);
    return m_fitConfigs.at(m_fitConfigs.size()-1);
}


//_______________________________________________________________________________________
FitConfig* ConfigMgr::getFitConfig(const TString& name){
    for(unsigned int i=0; i<m_fitConfigs.size(); i++) {
        if(m_fitConfigs.at(i)->m_name==name){
            return m_fitConfigs.at(i);
        }
    }
    m_logger << kWARNING << "unkown FitConfig object named '"<<name<<"'" << GEndl;
    return 0;
}


//_______________________________________________________________________________________
Bool_t ConfigMgr::checkConsistency() {
    if(m_fitConfigs.size()==0) {
        m_status = "empty";
        return false;
    }
    //to-do: add check for duplicated fit regions
    m_status = "OK";
    return true;
}


//_______________________________________________________________________________________
void ConfigMgr::initialize() {  
    if(m_saveTree || m_doHypoTest){
        if(m_outputFileName.Length()>0) {
            TFile fileOut(m_outputFileName,"RECREATE");
            fileOut.Close();
        } else {
            m_logger << kERROR << "in ConfigMgr: no outputFileName specified." << GEndl;
        }
    }
    return;
}


//_______________________________________________________________________________________
void ConfigMgr::fitAll() {
    for(unsigned int i=0; i<m_fitConfigs.size(); i++) {
        fit ( m_fitConfigs.at(i) );
    }

    return;
}


//_______________________________________________________________________________________
void ConfigMgr::fit(int i) {
    return fit(m_fitConfigs.at(i));
}


//_______________________________________________________________________________________
void ConfigMgr::fit(FitConfig* fc) {
    TString outfileName = m_outputFileName;
    outfileName.ReplaceAll(".root","_fitresult.root");
    TFile* outfile = TFile::Open(outfileName,"UPDATE");
    if(!outfile){ 
        m_logger << kERROR << "TFile <" << outfileName << "> could not be opened" << GEndl; 
        return; 
    }

    TFile* inFile = TFile::Open(fc->m_inputWorkspaceFileName);
    if(!inFile) { 
        m_logger << kERROR << "TFile could not be opened" << GEndl; 
        return; 
    }

    RooWorkspace* w = (RooWorkspace*)inFile->Get("combined");
    if(w == NULL) { 
        m_logger << kERROR << "workspace 'combined' does not exist in file" << GEndl; 
        return; 
    }

    RooFitResult* fitresult = Util::doFreeFit( w );

    if(fitresult) {	
        outfile->cd();
        TString hypName="fitTo_"+fc->m_signalSampleName;
        fitresult->SetName(hypName);
        fitresult->Write();
        m_logger << kINFO << "Now storing RooFitResult <" << hypName << ">" << GEndl;
    }

    inFile->Close();  
    outfile->Close();

    m_logger << kINFO << "Done. Stored fit result in file <" << outfileName << ">" << GEndl;

    return;
}


//_______________________________________________________________________________________
void ConfigMgr::doHypoTestAll(TString outdir, Bool_t doUL) {
    for(unsigned int i=0; i<m_fitConfigs.size(); i++) {
        doHypoTest( m_fitConfigs.at(i), outdir, 0., doUL );
        if( m_fixSigXSec && !m_runOnlyNominalXSec && doUL ){
            double SigXSecSysnsigma = 1.;
            doHypoTest( m_fitConfigs.at(i), outdir, SigXSecSysnsigma, doUL );
            doHypoTest( m_fitConfigs.at(i), outdir, SigXSecSysnsigma*(-1.), doUL );
        }     
    }

    return;
}


//_______________________________________________________________________________________
void ConfigMgr::doHypoTest(int i , TString outdir, double SigXSecSysnsigma, Bool_t doUL) {
    return doHypoTest( m_fitConfigs.at(i), outdir, SigXSecSysnsigma, doUL );
}


//_______________________________________________________________________________________
void ConfigMgr::doHypoTest(FitConfig* fc, TString outdir, double SigXSecSysnsigma, Bool_t doUL) {
    TString outfileName = m_outputFileName;
    TString suffix = "_hypotest.root";

    if ( m_fixSigXSec ){
        TString SigXSec = ( SigXSecSysnsigma > 0.? "Up" : ( SigXSecSysnsigma < 0. ? "Down" : "Nominal" ));
        suffix = "_fixSigXSec"+SigXSec+"_hypotest.root";
    }

    outfileName.ReplaceAll(".root", suffix);
    outfileName.ReplaceAll("results/",outdir);
    TFile* outfile = TFile::Open(outfileName,"UPDATE");
    if (!outfile) { 
        m_logger << kERROR << "TFile <" << outfileName << "> could not be opened" << GEndl; 
        return; 
    }

    TFile* inFile = TFile::Open(fc->m_inputWorkspaceFileName);
    if (!inFile) { 
        m_logger << kERROR << "TFile <" << fc->m_inputWorkspaceFileName << "> could not be opened" << GEndl; 
        return; 
    }

    RooWorkspace* w = (RooWorkspace*)inFile->Get("combined");
    if (w == NULL) { 
        m_logger << kERROR << "workspace 'combined' does not exist in file" << GEndl; 
        return; 
    }

    // piece-wise linear to 6th order poly interp + linear extrapolation (also used in Higgs group)
    Util::SetInterpolationCode(w,4); 

    m_logger << kINFO << "Processing analysis " << fc->m_signalSampleName << GEndl;

    if ((fc->m_signalSampleName).Contains("Bkg") || (fc->m_signalSampleName) == "") {
        m_logger << kINFO << "No hypothesis test performed for background fits." << GEndl;
        inFile->Close();  
        outfile->Close(); 
        return;
    }

    if(m_fixSigXSec && fc->m_signalSampleName != "" && w->var("alpha_SigXSec") != NULL){
        w->var("alpha_SigXSec")->setVal(SigXSecSysnsigma);
        w->var("alpha_SigXSec")->setConstant(true);
    }

    // set Errors&values of all parameters to 'natural' values before plotting/fitting
    Util::resetAllErrors(w);
    Util::resetAllValues(w);
    Util::resetAllNominalValues(w);

    bool useCLs = true;  
    int npoints = 1;   
    double poimin = 1.0;  
    double poimax = 1.0; 
    bool doAnalyze = false;
    bool useNumberCounting = false;
    TString modelSBName = "ModelConfig";
    TString modelBName;
    const char * dataName = "obsData";                 
    const char * nuisPriorName = 0;

    if ( !m_bkgParNameVec.empty()) {
        m_logger << kINFO << "Performing bkg correction for bkg-only toys." << GEndl;
        modelBName = makeCorrectedBkgModelConfig(w,modelSBName);
    }

    /// 1. Do first fit and save fit result in order to control fit quality
    RooFitResult* fitresult = Util::doFreeFit( w, 0, false, true ); // reset fit paremeters after the fit ...

    if(fitresult) {	
        outfile->cd();
        TString hypName = "fitTo_"+fc->m_signalSampleName;
        fitresult->SetName(hypName);
        fitresult->Print();
        fitresult->Write();
        m_logger << kINFO << "Now storing RooFitResult <" << hypName << ">" << GEndl;
    }

    /// 2. the hypothesis test
    RooStats::HypoTestResult* htr(0);
    RooStats::HypoTestInverterResult* result(0);

    if (doUL) { /// a. exclusion
        result = RooStats::DoHypoTestInversion(w, 
                m_nToys,m_calcType,m_testStatType,
                useCLs, 
                npoints,poimin,poimax,
                doAnalyze,
                useNumberCounting, 
                modelSBName.Data(), modelBName.Data(),
                dataName, 
                nuisPriorName ) ;
        if(result) { result->UseCLs(useCLs); }
    } else {  // b. discovery 
        // MB: Hack, needed for ProfileLikeliHoodTestStat to work properly.
        if (m_testStatType==3) { 
            m_logger << kWARNING << "Discovery mode --> Need to change test-statistic type " 
		     << "from one-sided to two-sided for RooStats to work." << GEndl; 
            m_logger << kWARNING << "(Note: test is still one-sided.)" << GEndl; 
            m_testStatType=2; 
        } 

        htr = RooStats::DoHypoTest(w, doUL, m_nToys, m_calcType, m_testStatType, modelSBName, modelBName, dataName, 
                useNumberCounting, nuisPriorName);
        if (htr!=0) {
            htr->Print(); 
            result = new RooStats::HypoTestInverterResult();
            result->Add(0,*htr);
            result->UseCLs(false);
        }
    }

    /// 3. Storage
    if ( result!=0 ) {	
        outfile->cd();
        TString hypName="hypo_"+fc->m_signalSampleName;
        if(fc->m_hypoTestName.Length() > 0){ hypName="hypo_"+fc->m_hypoTestName; }
        
        //// give discovery HypoTestInverterResult a different name
        if(!doUL && fc->m_hypoTestName.Length() > 0 ) { hypName = "hypo_discovery_" + fc->m_hypoTestName; }
        else if(!doUL) { hypName="hypo_discovery_"+fc->m_signalSampleName; }
        
        result->SetName(hypName);
        result->Write();
        m_logger << kINFO << "Now storing HypoTestInverterResult <" << hypName << ">" << GEndl;
        delete result;
    }

    if ( htr!=0 ) {	
        outfile->cd();
        TString hypName="discovery_htr_"+fc->m_signalSampleName;
        if(fc->m_hypoTestName.Length() > 0){ hypName="discovery_htr_"+fc->m_hypoTestName; }
        htr->SetName(hypName);
        htr->Write();
        m_logger << kINFO << "Now storing HypoTestResult <" << hypName << ">" << GEndl;
        delete htr;
    }

    m_logger << kINFO << "Done. Stored HypoTest(Inverter)Result and fit result in file <" << outfileName << ">" << GEndl;

    inFile->Close();  
    outfile->Close();

    return;
}


//_______________________________________________________________________________________
TString ConfigMgr::makeCorrectedBkgModelConfig( RooWorkspace* w, const char* modelSBName ) {
    TString bModelStr;

    if ( m_bkgCorrValVec.size()!=m_bkgParNameVec.size() || 
            m_bkgCorrValVec.size()!=m_chnNameVec.size() || 
            m_chnNameVec.size()!=m_bkgParNameVec.size() ) {
        m_logger << kERROR << "Incorrect vector sizes for bkg correction value(s)." << GEndl; 
        return bModelStr; 
    }

    RooStats::ModelConfig* sbModel = Util::GetModelConfig( w, modelSBName );
    if (sbModel == NULL) { 
        m_logger << kERROR << "No signal model config found. Return." << GEndl;
        return bModelStr; 
    }

    RooRealVar * poi = dynamic_cast<RooRealVar*>(sbModel->GetParametersOfInterest()->first());
    if (!poi) { 
        m_logger << kERROR << "No signal strength parameter found. Return." << GEndl; 
        return bModelStr; 
    }

    double oldpoi = poi->getVal();
    poi->setVal(0); /// MB : turn off the signal component

    const RooArgSet* tPoiSet = sbModel->GetParametersOfInterest();
    const RooArgSet* prevSnapSet = sbModel->GetSnapshot();

    RooArgSet newSnapSet;
    if (tPoiSet!=0) 
        newSnapSet.add(*tPoiSet); // make sure this is the full poi set.

    std::vector<double> prevbknorm;

    for (unsigned int i=0; i<m_bkgParNameVec.size(); ++i) {
        RooRealVar *totbk = w->var( m_bkgParNameVec[i].c_str() );
        if (!totbk) { 
            m_logger << kERROR << "No bkg strength parameter found. Return." << GEndl; 
            return bModelStr; 
        }

        prevbknorm.push_back( totbk->getVal() );

        RooAbsPdf* bkpdf  = Util::GetRegionPdf( w, m_chnNameVec[i] ); 
        RooRealVar* bkvar = Util::GetRegionVar( w, m_chnNameVec[i] );
        RooRealIntegral* bkint = (RooRealIntegral *)bkpdf->createIntegral( RooArgSet(*bkvar) );

        double oldtotbk = bkint->getVal(); 

        /// MB : do the bkg reset here
        totbk->setVal( m_bkgCorrValVec[i] / oldtotbk );

        newSnapSet.add(*totbk);  // new bkg parameter should also be included
    }

    if ((prevSnapSet!=0)) {
        // add all remaining parameters from old snapshot
        TIterator* vrItr = prevSnapSet->createIterator();
        RooRealVar* vr(0);
        for (Int_t i=0; (vr = (RooRealVar*)vrItr->Next()); ++i) {
            if (vr==0) 
                continue;

            TString vrName = vr->GetName();
            RooRealVar* par = (RooRealVar*)newSnapSet.find(vrName.Data());

            if (par==0) { 
                newSnapSet.add(*vr); // add back if not already present 
            } 
        }
        delete vrItr;
    }

    bModelStr = TString(modelSBName)+TString("_with_poi_0");
    RooStats::ModelConfig* bModel = Util::GetModelConfig( w, bModelStr.Data() );
    if (bModel) { 
        m_logger << kERROR << "Bkg model config already defined. Return." << GEndl; 
        return bModelStr; 
    }

    bModel = (RooStats::ModelConfig*) sbModel->Clone();
    bModel->SetName(bModelStr.Data());      

    bModel->SetSnapshot( newSnapSet );
    /// MB : and reimport the configuration into the WS
    w->import( *bModel );

    /// reset
    poi->setVal(oldpoi);
    for (unsigned int i=0; i<m_bkgParNameVec.size(); ++i) {
        RooRealVar *totbk = w->var( m_bkgParNameVec[i].c_str() );
        totbk->setVal( prevbknorm[i] );
    }

    /// Important: this resets both mu_sig and mu_bkg !
    sbModel->SetSnapshot( newSnapSet );

    // pass on the name of the bkg model config
    return bModelStr;
}


//_______________________________________________________________________________________
void ConfigMgr::doUpperLimitAll() {
    for(unsigned int i=0; i<m_fitConfigs.size(); i++) {
        doUpperLimit( m_fitConfigs.at(i) );
    }
    return;
}


//_______________________________________________________________________________________
void ConfigMgr::doUpperLimit(int i) {
    return doUpperLimit(m_fitConfigs.at(i));
}


//_______________________________________________________________________________________
void ConfigMgr::doUpperLimit(FitConfig* fc) {
    TString outfileName = m_outputFileName;
    outfileName.ReplaceAll(".root","_upperlimit.root");
    TFile* outfile = TFile::Open(outfileName,"UPDATE");
    if(outfile->IsZombie()) { 
        m_logger << kERROR << "TFile <" << outfileName << "> could not be opened" << GEndl; 
        return; 
    }

    TFile* inFile = TFile::Open(fc->m_inputWorkspaceFileName);
    if(!inFile){ 
        m_logger << kERROR << "doUL : TFile <" << fc->m_inputWorkspaceFileName << "> could not be opened" << GEndl; 
        return; 
    }

    RooWorkspace* w = (RooWorkspace*)inFile->Get("combined");
    if(w == NULL){ 
        m_logger << kERROR << "workspace 'combined' does not exist in file" << GEndl; 
        return; 
    }

    if ((fc->m_signalSampleName).Contains("Bkg") || (fc->m_signalSampleName) == "") {
        m_logger << kINFO << "No hypothesis test performed for background fits." << GEndl;
        inFile->Close();  
        outfile->Close(); 
        return;
    }

    // 6th order poly interp + linear extrapolation (also used in Higgs group)
    Util::SetInterpolationCode(w,4);

    // reset all nominal values
    Util::resetAllValues(w) ;
    Util::resetAllErrors(w) ;
    Util::resetAllNominalValues(w) ;

    // fix x-section uncertainty
    if(m_fixSigXSec && fc->m_signalSampleName != "" && w->var("alpha_SigXSec") != NULL){
        w->var("alpha_SigXSec")->setVal(0);
        w->var("alpha_SigXSec")->setConstant(true);
    }

    /// here we go ...
    
    RooStats::HypoTestInverterResult* hypo = nullptr;
    if (!m_useScanRange) {
        /// first asymptotic limit, to get a quick but reliable estimate for the upper limit
        /// dynamic evaluation of ranges
        hypo = RooStats::DoHypoTestInversion(w, 1, 2, m_testStatType, m_useCLs, 20, 0, -1); 
    }

    /// then reevaluate with proper settings
    if ( hypo!=0 || m_useScanRange) {
        double minRange = -1;
        double maxRange = -1;
        if (m_useScanRange) { // next fit is done between the user defined values
            minRange = m_scanRangeMin;
            maxRange = m_scanRangeMax;
        }
        else { // next fit is done between 0 and the expected upper limit + 2 sigma
            (void) hypo->ExclusionCleanup();             
            
            int i=0; 
            while (i<5) {
                if (min_CLs(hypo)>0.05) { 
                    m_logger << kINFO << "Starting rescan iteration: " << i << GEndl;           
                    hypo = RedoScan(w,hypo);
                    if ( hypo!=0 ) { (void) hypo->ExclusionCleanup(); }
                }
                else { break; }
                i+=1;
            }
            minRange = 0;
            maxRange = 1.10 * hypo->GetExpectedUpperLimit(2);
            delete hypo; hypo=0;
        }
        
        hypo = RooStats::DoHypoTestInversion(w, m_nToys, m_calcType, m_testStatType, m_useCLs, m_nPoints, minRange, maxRange);
        int nPointsRemoved = hypo->ExclusionCleanup();
        if (nPointsRemoved > 0) {
            m_logger << kWARNING << "ExclusionCleanup() removed " << nPointsRemoved 
                << " scan point(s) for hypo test inversion: " << hypo->GetName() << GEndl;
        }

        if (m_useScanRange) {
            if ((1.2 * hypo->GetExpectedUpperLimit(2)) > m_scanRangeMax) {
                m_logger << kWARNING << "Scan Range is too near to the upper limit + 2 sigma! (calc exp limit + 2 sigma: " << hypo->GetExpectedUpperLimit(2)
                 << ", set range: " << m_scanRangeMax << ")" << GEndl;
            }
        }
    }       
        

    /// store ul as nice plot ..
    if ( hypo!=0 ) {
        TString outputPrefix = TString(gSystem->DirName(outfileName))+"/"+fc->m_signalSampleName.Data();
        RooStats::AnalyzeHypoTestInverterResult( hypo, m_calcType, m_testStatType, m_useCLs, m_nPoints, outputPrefix, ".eps") ;
    }

    // save complete hypotestinverterresult to file
    if(hypo){
        outfile->cd();
        TString hypName; //="hypo_"+fc->m_signalSampleName;
        if (hypo->ArraySize()>0 && min_CLs(hypo)>0.05) {
                m_logger << kERROR << "Final CLs value not below threshold of 0.05  - upper limit scan most likely failed." << GEndl;
                m_logger << kERROR << "Will store result only for debugging purposes - do not use it in contour plots!" << GEndl;
                hypName="debug_"+fc->m_signalSampleName;
        }
        else if (hypo->ArraySize()>0 && max_CLs(hypo)<0.05) {
                m_logger << kERROR << "Initial CLs value not above threshold of 0.05 - upper limit scan most likely failed." << GEndl;
                m_logger << kERROR << "Will store result only for debugging purposes - do not use it in contour plots!" << GEndl;
                if (!std::isnan(hypo->GetResult(0)->CLs())) { m_logger << kINFO << "Try rescan in range (0," << hypo->GetXValue(0) << ")" << GEndl; }             
                hypName="debug_"+fc->m_signalSampleName;
        }        
        else if (hypo->ArraySize()==0) {
                m_logger << kERROR << "All fits seem to have failed - cannot compute upper limit!" << GEndl;
                hypName="debug_"+fc->m_signalSampleName;
        }
        else {
                hypName="hypo_"+fc->m_signalSampleName;
        }
        hypo->SetName(hypName);
        m_logger << kINFO << "Now storing HypoTestInverterResult <" << hypName << ">" << GEndl;
        hypo->Write();
    }

    if (hypo!=0) { 
        delete hypo; 
    }

    inFile->Close();
    outfile->Close();

    m_logger << kINFO << "Done. Stored upper limit in file <" << outfileName << ">" << GEndl;

    return;
}


//_______________________________________________________________________________________
void ConfigMgr::runToysAll() {
    for(unsigned int i=1; i<m_fitConfigs.size(); i++) {
        runToys ( m_fitConfigs.at(i) );
    }
    return;
}


//_______________________________________________________________________________________
void ConfigMgr::runToys(int i) {
    return runToys(m_fitConfigs.at(i));
}


//_______________________________________________________________________________________
void ConfigMgr::runToys(FitConfig* fc) {
    TFile* inFile = TFile::Open(fc->m_inputWorkspaceFileName);
    if(!inFile){ 
        m_logger << kERROR << "TFile could not be opened" << GEndl; 
        return; 
    }

    RooWorkspace* w = (RooWorkspace*)inFile->Get("combined");
    if(w == NULL){ 
        m_logger << kERROR << "workspace 'combined' does not exist in file" << GEndl; 
        return; 
    }

    /// here we go ...
    m_seed = RooRandom::randomGenerator()->GetSeed(); // m_seed );
    bool doDataFitFirst = true;
    bool storeToyResults = true;
    TString toyoutfile =  fc->m_inputWorkspaceFileName;
    toyoutfile.ReplaceAll(".root","");  
    toyoutfile =  TString::Format("%s_toyResults_seed=%d_ntoys=%d.root",toyoutfile.Data(),m_seed,m_nToys);  

    /// storage performed inside function
    TTree* dummy = RooStats::toyMC_gen_fit( w, m_nToys, m_muValGen, doDataFitFirst, storeToyResults, toyoutfile );
    delete dummy;

    return;
}

//_______________________________________________________________________________________
double ConfigMgr::min_CLs(RooStats::HypoTestInverterResult* hypo) {
    double CLs=1.;
    for (int i=0; i<hypo->ArraySize(); i++) {
        if (hypo->GetResult(i)->CLs()<CLs) { CLs = hypo->GetResult(i)->CLs();}
    }
    return CLs;    
}

//_______________________________________________________________________________________
double ConfigMgr::max_CLs(RooStats::HypoTestInverterResult* hypo) {
    double CLs=1.;
    for (int i=0; i<hypo->ArraySize(); i++) {
        if (hypo->GetResult(i)->CLs()>CLs) { CLs = hypo->GetResult(i)->CLs();}
    }
    return CLs;    
}

//_______________________________________________________________________________________
RooStats::HypoTestInverterResult* ConfigMgr::RedoScan(RooWorkspace* w, RooStats::HypoTestInverterResult* hypo) {
    double maxX=hypo->GetLastXValue();
    double newX = maxX;
    
    int n=hypo->ArraySize();
    m_logger << kINFO << "Available points: " << n << GEndl;
    m_logger << kINFO << "Recalculate x" << GEndl;
    if (n>=2 && !std::isnan(hypo->GetResult(n-2)->CLs()) && !std::isnan(hypo->GetLastResult()->CLs())) {
        double diffCLs = fabs(hypo->GetResult(n-2)->CLs()-hypo->GetLastResult()->CLs());
        double diffX = maxX-hypo->GetXValue(n-2);
        double newCLs = hypo->GetLastResult()->CLs();
        while (newCLs>0.05) {
            newX += diffX;
            newCLs -= diffCLs;
        }
        newX = newX*1.2;
    }
    else {
        newX=2.*maxX;
    }
    
    delete hypo; hypo=0;
    
    m_logger << kINFO <<  "Redo scan with a larger x range: 0, " << newX << GEndl;
    hypo = RooStats::DoHypoTestInversion(w,1,2,m_testStatType,true,20,0.,newX);
    
    return hypo;  
}
    
//_______________________________________________________________________________________
void ConfigMgr::finalize(){
    return;
}


//_______________________________________________________________________________________
/// Initialization of singleton
ConfigMgr *ConfigMgr::_singleton = NULL;

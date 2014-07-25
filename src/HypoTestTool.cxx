// vim: ts=4:sw=4
/* -*- mode: c++ -*- */

/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Class  : HypoTestTool                                                          *
 *                                                                                *
 * Description:                                                                   *
 *      Implementation (see header for description)                               *
 *                                                                                *
 *      Adapted from RooStats.StandardHypoTestInvDemo. Original author(s):        *
 *                                                                                *
 *      Lorenzo Moneta        <Lorenzo.Moneta@cern.ch> - CERN, Switzerland        *
 *                                                                                *
 * Copyright (c):                                                                 *
 *      CERN, Switzerland                                                         *
 *                                                                                *
 * http://root.cern.ch/root/html534/tutorials/roostats/StandardHypoTestInvDemo.C.html 
 *                                                                                *
 * (http://root.cern.ch/drupal/content/license)                                   *
 **********************************************************************************/

#include "HypoTestTool.h"
#include "TMsgLogger.h"

#include "TSystem.h"
#include "TFile.h"
#include "RooWorkspace.h"
#include "RooAbsPdf.h"
#include "RooRealVar.h"
#include "RooDataSet.h"
#include "RooStats/ModelConfig.h"
#include "RooRandom.h"
#include "TGraphErrors.h"
#include "TGraphAsymmErrors.h"
#include "TCanvas.h"
#include "TLine.h"
#include "TROOT.h"

#include "RooStats/AsymptoticCalculator.h"
#include "RooStats/HybridCalculator.h"
#include "RooStats/FrequentistCalculator.h"
#include "RooStats/ToyMCSampler.h"
#include "RooStats/HypoTestPlot.h"

#include "RooStats/NumEventsTestStat.h"
#include "RooStats/ProfileLikelihoodTestStat.h"
#include "RooStats/SimpleLikelihoodRatioTestStat.h"
#include "RooStats/RatioOfProfiledLikelihoodsTestStat.h"
#include "RooStats/MaxLikelihoodEstimateTestStat.h"

#include "RooStats/HypoTestInverterResult.h"
#include "RooStats/HypoTestResult.h"
#include "RooStats/HypoTestInverterPlot.h"

using namespace RooFit;
using namespace RooStats;

/* Options:
 *  bool plotHypoTestResult = true;          // plot test statistic result at each point
 *  bool writeResult = true;                 // write HypoTestInverterResult in a file 
 *  TString resultFileName;                  // file with results (by default is built automatically using teh ws input file name)
 *  bool optimize = true;                    // optmize evaluation of test statistic 
 *  bool useVectorStore = true;              // convert data to use new roofit data store 
 *  bool generateBinned = false;             // generate binned data sets 
 *  bool noSystematics = false;              // force all systematics to be off (i.e. set all nuisance parameters as constat to their nominal values)
 *  double nToysRatio = 2;                   // ratio Ntoys S+b/ntoysB
 *  double maxPOI = -1;                      // max value used of POI (in case of auto scan) 
 *  bool useProof = false;                    // use Proof Light when using toys (for freq or hybrid)
 *  int nworkers = 4;                        // number of worker for Proof
 *  bool rebuild = false;                    // re-do extra toys for computing expected limits and rebuild test stat
 *  // distributions (N.B this requires much more CPU (factor is equivalent to nToyToRebuild)
 *  int nToyToRebuild = 100;                 // number of toys used to rebuild 
 *  int initialFit = -1;                     // do a first  fit to the model (-1 : default, 0 skip fit, 1 do always fit) 
 *  int randomSeed = -1;                     // random seed (if = -1: use default value, if = 0 always random )
 *  // NOTE: Proof uses automatically a random seed   
 *  std::string massValue = "";              // extra string to tag output file of result 
 *  std::string  minimizerType = "";         // minimizer type (default is what is in ROOT::Math::MinimizerOptions::DefaultMinimizerType()
 *  int   printLevel = 0;                    // print level for debugging PL test statistics and calculators  
 */

//_______________________________________________________________________________________
RooStats::HypoTestTool::HypoTestTool() : m_hc(0), m_calc(0),
    mPlotHypoTestResult(true),
    mWriteResult(true),
    mOptimize(true),
    mUseVectorStore(true),
    mGenerateBinned(true),
    mUseProof(false),
    mRebuild(false),
    mNWorkers(4),
    mNToyToRebuild(100),
    mPrintLevel(0),
    mInitialFit(1),
    mRandomSeed(-1),
    mNToysRatio(2),
    mMaxPoi(-1),
    mMassValue(""),
    mMinimizerType("Minuit2"),
    mResultFileName(),
    mNoSystematics(false),
    mConfLevel(0.95),
    m_logger("HypoTestTool")
{
}


//_______________________________________________________________________________________
void
RooStats::HypoTestTool::SetParameter(const char * name, bool value){
    //
    // set boolean parameters
    //

    std::string s_name(name);

    if (s_name.find("PlotHypoTestResult") != std::string::npos) mPlotHypoTestResult = value;
    if (s_name.find("WriteResult") != std::string::npos) mWriteResult = value;
    if (s_name.find("Optimize") != std::string::npos) mOptimize = value;
    if (s_name.find("UseVectorStore") != std::string::npos) mUseVectorStore = value;
    if (s_name.find("GenerateBinned") != std::string::npos) mGenerateBinned = value;
    if (s_name.find("UseProof") != std::string::npos) mUseProof = value;
    if (s_name.find("Rebuild") != std::string::npos) mRebuild = value;

    return;
}


//_______________________________________________________________________________________
void
RooStats::HypoTestTool::SetParameter(const char * name, int value){
    //
    // set integer parameters
    //

    std::string s_name(name);

    if (s_name.find("NWorkers") != std::string::npos) mNWorkers = value;
    if (s_name.find("NToyToRebuild") != std::string::npos) mNToyToRebuild = value;
    if (s_name.find("PrintLevel") != std::string::npos) mPrintLevel = value;
    if (s_name.find("InitialFit") != std::string::npos) mInitialFit = value;
    if (s_name.find("RandomSeed") != std::string::npos) mRandomSeed = value;

    return;
}



//_______________________________________________________________________________________
void
RooStats::HypoTestTool::SetParameter(const char * name, double value){
    //
    // set double precision parameters
    //

    std::string s_name(name);

    if (s_name.find("NToysRatio") != std::string::npos) mNToysRatio = value;
    if (s_name.find("MaxPOI") != std::string::npos) mMaxPoi = value;
    if (s_name.find("ConfidenceLevel") != std::string::npos) mConfLevel = value;

    return;
}



//_______________________________________________________________________________________
void
RooStats::HypoTestTool::SetParameter(const char * name, const char * value){
    //
    // set string parameters
    //

    std::string s_name(name);

    if (s_name.find("MassValue") != std::string::npos) mMassValue.assign(value);
    if (s_name.find("MinimizerType") != std::string::npos) mMinimizerType.assign(value);
    if (s_name.find("ResultFileName") != std::string::npos) mResultFileName = value;

    return;
}


//_______________________________________________________________________________________
void
RooStats::HypoTestTool::AnalyzeResult( HypoTestInverterResult * r,
        int calculatorType,
        int testStatType, 
        bool useCLs,  
        int npoints,
        const char* outfilePrefix,
        const char* outfiletype
        ) 
{ 
    if (r==0) {
        m_logger << kERROR << "Input HypoTestInverterResult is empty. Exit." << GEndl;
        return;
    }

    // analyize result produced by the inverter, optionally save it in a file 

    double upperLimit = r->UpperLimit();
    double ulError = r->UpperLimitEstimatedError();

    m_logger << kINFO << "The computed upper limit is: " << upperLimit << " +/- " << ulError << GEndl;

    // compute expected limit
    m_logger << kINFO << " expected limit (median) " << r->GetExpectedUpperLimit(0) << GEndl;
    m_logger << kINFO << " expected limit (-1 sig) " << r->GetExpectedUpperLimit(-1) << GEndl;
    m_logger << kINFO << " expected limit (+1 sig) " << r->GetExpectedUpperLimit(1) << GEndl;
    m_logger << kINFO << " expected limit (-2 sig) " << r->GetExpectedUpperLimit(-2) << GEndl;
    m_logger << kINFO << " expected limit (+2 sig) " << r->GetExpectedUpperLimit(2) << GEndl;

    // write result in a file 
    // write to a file the results
    const char *  calcType = (calculatorType == 0) ? "Freq" : (calculatorType == 1) ? "Hybr" : "Asym";
    const char *  limitType = (useCLs) ? "CLs" : "Cls+b";
    const char * scanType = (npoints < 0) ? "auto" : "grid";
    if (mResultFileName.IsNull())
        mResultFileName = TString::Format("%s_%s_%s_%s_ts%d.root",outfilePrefix,calcType,limitType,scanType,testStatType);      
    //strip the / from the filename
    if (mMassValue.size()>0) {
        mResultFileName += mMassValue.c_str();
        mResultFileName += "_";
    }

    if (mWriteResult) {
        TFile * fileOut = new TFile(mResultFileName,"RECREATE");
        r->Write();
        fileOut->Close();  
    }

    // plot the result ( p values vs scan points) 
    std::string typeName = "";
    if (calculatorType == 0 )
        typeName = "Frequentist";
    if (calculatorType == 1 )
        typeName = "Hybrid";   
    else if (calculatorType == 2 || calculatorType == 3) { 
        typeName = "Asymptotic";
        mPlotHypoTestResult = false; 
    }

    const char * resultName = r->GetName();
    TString plotTitle = TString::Format("%s CL Scan for workspace %s",typeName.c_str(),resultName);
    HypoTestInverterPlot *plot = new HypoTestInverterPlot("HTI_Result_Plot",plotTitle,r);

    // plot in a new canvas with style
    TString c1Name = TString::Format("%s_Scan",typeName.c_str());
    TCanvas *c_sig = new TCanvas(c1Name); 
    c_sig->SetLogy(false);

    plot->Draw("CLb 2CL");  // plot all and Clb

    TPave *pave = (TPave*)c_sig->GetPrimitive("TPave");
    pave->SetLineColor(0);
    pave->SetBorderSize(0);
    pave->SetFillColor(0);
    c_sig->Update();

    //split mResultFileName - it might contain a directory
    TString outputDir = TString(gSystem->DirName(mResultFileName))+"/";
    TString ULfilename = TString("upperlimit_cls_poi_") + gSystem->BaseName(mResultFileName) + outfiletype;
    m_logger << kINFO << " writing result plot to " << TString(outputDir+ULfilename).Data() << GEndl; 
    c_sig->SaveAs( TString(outputDir+ULfilename).Data() );

    const int nEntries = r->ArraySize();

    // plot test statistics distributions for the two hypothesis 
    if (mPlotHypoTestResult) { 
        TCanvas * c2 = new TCanvas();
        if (nEntries > 1) { 
            int ny = TMath::CeilNint( sqrt(nEntries) );
            int nx = TMath::CeilNint(double(nEntries)/ny);
            c2->Divide( nx,ny);
        }
        for (int i=0; i<nEntries; i++) {
            if (nEntries > 1) c2->cd(i+1);
            SamplingDistPlot * pl = plot->MakeTestStatPlot(i);
            pl->SetLogYaxis(true);
            pl->Draw();
        }
        c2->SaveAs( (TString::Format("%scls_distribution_%s%s", outputDir.Data(), gSystem->BaseName(mResultFileName), outfiletype)) );
    }
}


//_______________________________________________________________________________________
/* internal routine to run the inverter
 * The inverter assumes to exclude the signal model
 */
HypoTestInverterResult *
RooStats::HypoTestTool::RunHypoTestInverter(RooWorkspace * w,
        const char * modelSBName, const char * modelBName, 
        const char * dataName, int type,  int testStatType, 
        bool useCLs, int npoints, double poimin, double poimax, int ntoys,
        bool useNumberCounting,
        const char * nuisPriorName )
{
    m_logger << kINFO << ">>> Running HypoTestInverter on the workspace " << w->GetName() << GEndl;

    bool ok = this->SetupHypoTestInverter(w, modelSBName, modelBName, dataName, type, testStatType, 
            useCLs, npoints, poimin, poimax, ntoys, useNumberCounting, nuisPriorName );
    if (!ok) {
        return 0;
    }

    /// by now m_calc has been setup okay ...
    TStopwatch tw; 
    tw.Start();
    HypoTestInverterResult * r = m_calc->GetInterval();

    m_logger << kINFO << "Time to perform limit scan \n";
    tw.Print();

    if (mRebuild) {
        m_calc->SetCloseProof(1);
        tw.Start();
        SamplingDistribution * limDist = m_calc->GetUpperLimitDistribution(true,mNToyToRebuild);
        m_logger << kINFO << "Time to rebuild distributions " << GEndl;
        tw.Print();

        if (limDist) { 
            m_logger << kINFO << "expected up limit " << limDist->InverseCDF(0.5) << " +/- " 
                << limDist->InverseCDF(0.16) << "  " 
                << limDist->InverseCDF(0.84) << "\n"; 

            // update r to a new updated result object containing the rebuilt expected p-values distributions
            // (it will not recompute the expected limit)
            if (r) delete r;  // need to delete previous object since GetInterval will return a cloned copy
            r = m_calc->GetInterval();

        }
        else 
            m_logger << kINFO << "ERROR : failed to re-build distributions " << GEndl; 
    }

    m_logger << kINFO << ">>> Done running HypoTestInverter on the workspace " << w->GetName() << GEndl;

    return r;
}


//_______________________________________________________________________________________
/// internal routine to run the hypothesis test
HypoTestResult*
RooStats::HypoTestTool::RunHypoTest(RooWorkspace * w, bool doUL,
        const char * modelSBName, const char * modelBName, 
        const char * dataName, int type, int testStatType, 
        int ntoys,
        bool useNumberCounting,
        const char * nuisPriorName )
{
    bool ok = this->SetupHypoTestCalculator(w, doUL, modelSBName, modelBName, dataName, type, testStatType, 
            ntoys, useNumberCounting, nuisPriorName );
    if (!ok) {
        return 0;
    }

    /// by now m_calc has been setup okay ...

    m_logger << kINFO << ">>> Running HypoTestCalculator on the workspace " << w->GetName() << GEndl;

    TStopwatch tw; 
    tw.Start();
    HypoTestResult * r = m_hc->GetHypoTest();
    tw.Print();

    m_logger << kINFO << ">>> Done running HypoTestCalculator on the workspace " << w->GetName() << GEndl;

    if (doUL) { r->SetBackgroundAsAlt(); }

    return r;
}


//_______________________________________________________________________________________
bool
RooStats::HypoTestTool::SetupHypoTestCalculator(RooWorkspace * w, bool doUL,
        const char * modelSBName, const char * modelBName, 
        const char * dataName, int type,  int testStatType, 
        int ntoys,
        bool useNumberCounting,
        const char * nuisPriorName ) 
{
    m_logger << kINFO << ">>> Setting up HypoTestCalculator on the workspace <" << w->GetName() << ">" << GEndl;
    m_logger << kINFO << ">>> Setting up HypoTest for : " << (doUL ? "exclusion" : "discovery") << GEndl;

    RooAbsData * data = w->data(dataName); 
    if (!data) { 
        Error("HypoTestTool","Not existing data %s",dataName);
        return false;
    }
    else 
        m_logger << kINFO << "Using data set " << dataName << GEndl;

    ModelConfig* bModel = (ModelConfig*) w->obj(modelBName);
    ModelConfig* sbModel = (ModelConfig*) w->obj(modelSBName);

    if (!sbModel) {
        Error("HypoTestTool","Not existing ModelConfig %s",modelSBName);
        return false;
    }
    // check the model 
    if (!sbModel->GetPdf()) { 
        Error("HypoTestTool","Model %s has no pdf ",modelSBName);
        return false;
    }
    if (!sbModel->GetParametersOfInterest()) {
        Error("HypoTestTool","Model %s has no poi ",modelSBName);
        return false;
    }
    if (!sbModel->GetObservables()) {
        Error("HypoTestTool","Model %s has no observables ",modelSBName);
        return false;
    }
    if (!sbModel->GetSnapshot() ) { 
        Info("HypoTestTool","Model %s has no snapshot  - make one using model poi",modelSBName);
        RooRealVar * var = dynamic_cast<RooRealVar*>(sbModel->GetParametersOfInterest()->first());
        if (var) {
	  Info("HypoTestTool","Setting poi to 1.0");
	  var->setVal(1.0);
        }
        sbModel->SetSnapshot( *sbModel->GetParametersOfInterest() );
    }

    // case of no systematics
    // remove nuisance parameters from model
    if (mNoSystematics) { 
        const RooArgSet * nuisPar = sbModel->GetNuisanceParameters();
        if (nuisPar && nuisPar->getSize() > 0) { 
            m_logger << kINFO << "HypoTestTool" << "  -  Switch off all systematics by setting them constant to their initial values" << GEndl;
            RooStats::SetAllConstant(*nuisPar);
        }
        const RooArgSet * bnuisPar = bModel->GetNuisanceParameters();
        if (bnuisPar) 
            RooStats::SetAllConstant(*bnuisPar);
    }

    if (!bModel || bModel == sbModel) {
        Info("HypoTestTool","The background model %s does not exist",modelBName);
        Info("HypoTestTool","Copy it from ModelConfig %s and set POI to zero",modelSBName);
        bModel = (ModelConfig*) sbModel->Clone();
        bModel->SetName(TString(modelSBName)+TString("_with_poi_0"));
        if(!bModel->GetParametersOfInterest()->first()){
            m_logger << kERROR << "HypoTestTool: sbModel has no POI!" << GEndl;
            return false;
        }
        
        RooRealVar * var = dynamic_cast<RooRealVar*>(bModel->GetParametersOfInterest()->first());
        if (!var){
          Info("HypoTestTool","Cast failed");
          m_logger << kINFO << "HypoTestTool: Cast failed part 2" << GEndl;
          return false;
        }
        double oldval = var->getVal();
        var->setVal(0);
        bModel->SetSnapshot( RooArgSet(*var)  );
        var->setVal(oldval);
    }
    else { 
        if (!bModel->GetSnapshot() ) { // MB : note, this resets all parameters! 

            Info("HypoTestTool","Model %s has no snapshot  - make one using model poi and 0 values ",modelBName);
            RooRealVar * var = dynamic_cast<RooRealVar*>(bModel->GetParametersOfInterest()->first());
            if (var) { 
                double oldval = var->getVal();
                var->setVal(0);
                bModel->SetSnapshot( RooArgSet(*var)  );
                var->setVal(oldval);

                Error("HypoTestTool","Model %s has no valid poi",modelBName);
                return false;
            }         
        } else { // reset
            sbModel->GetSnapshot();
        }
    }

    // check model  has global observables when there are nuisance pdf
    // for the hybrid case the globobs are not needed
    if (type != 1 ) { 
        bool hasNuisParam = (sbModel->GetNuisanceParameters() && sbModel->GetNuisanceParameters()->getSize() > 0);
        bool hasGlobalObs = (sbModel->GetGlobalObservables() && sbModel->GetGlobalObservables()->getSize() > 0);
        if (hasNuisParam && !hasGlobalObs ) {  
            // try to see if model has nuisance parameters first 
            RooAbsPdf * constrPdf = RooStats::MakeNuisancePdf(*sbModel,"nuisanceConstraintPdf_sbmodel");
            if (constrPdf) { 
                Warning("StandardHypoTestInvDemo","Model %s has nuisance parameters but no global observables associated",sbModel->GetName());
                Warning("StandardHypoTestInvDemo","\tThe effect of the nuisance parameters will not be treated correctly ");
            }
        }
    }

    // run first a data fit 
    const RooArgSet * poiSet = sbModel->GetParametersOfInterest();
    RooRealVar *poi = (RooRealVar*)poiSet->first();

    m_logger << kINFO << "HypoTestTool : POI initial value:   " << poi->GetName() << " = " << poi->getVal()   << GEndl;  

    //poi->setRange(0,100);

    // fit the data first (need to use constraint )
    bool doFit = mInitialFit;
    if (testStatType == 0 && mInitialFit == -1) doFit = false;  // case of LEP test statistic
    if (type == 3  && mInitialFit == -1) doFit = false;         // case of Asymptoticcalculator with nominal Asimov
    if (!doUL) doFit = false;                                   // case of discovery: don't want to adjust s+b toys
    double poihat = 0;

    if (doFit)  { 
        // do the fit : By doing a fit the POI snapshot (for S+B)  is set to the fit value
        // and the nuisance parameters nominal values will be set to the fit value. 
        // This is relevant when using LEP test statistics
        const RooArgSet* prevSnapSet = sbModel->GetSnapshot();
        const RooArgSet* tPoiSet = sbModel->GetParametersOfInterest();

        Info( "StandardHypoTestInvDemo"," Doing a first fit to the observed data ");
        if (mMinimizerType.size()==0) mMinimizerType = ROOT::Math::MinimizerOptions::DefaultMinimizerType();
        else 
            ROOT::Math::MinimizerOptions::SetDefaultMinimizer(mMinimizerType.c_str());
        Info("StandardHypoTestInvDemo","Using %s as minimizer for computing the test statistic",
                ROOT::Math::MinimizerOptions::DefaultMinimizerType().c_str() );
        RooArgSet constrainParams;
        if (sbModel->GetNuisanceParameters() ) constrainParams.add(*sbModel->GetNuisanceParameters());
        RooStats::RemoveConstantParameters(&constrainParams);
        TStopwatch tw;
        tw.Start();
        Bool_t verbose = (m_logger.GetMinLevel() <= kDEBUG) ? kTRUE : kFALSE;
        RooFitResult * fitres = sbModel->GetPdf()->fitTo(*data,InitialHesse(false), Hesse(false),
                Minimizer(mMinimizerType.c_str(),"Migrad"), Strategy(0), Verbose(verbose),
                PrintLevel(mPrintLevel+1), Constrain(constrainParams), Save(true) );
        if (fitres->status() != 0) { 
            Warning("StandardHypoTestInvDemo","Fit to the model failed - try with strategy 1 and perform first an Hesse computation");
            fitres = sbModel->GetPdf()->fitTo(*data,InitialHesse(true), Hesse(false),Minimizer(mMinimizerType.c_str(),"Migrad"), 
                    Strategy(1), PrintLevel(mPrintLevel+1), Constrain(constrainParams), Save(true), Verbose(verbose) );
        }
        if (fitres->status() != 0) 
            Warning("StandardHypoTestInvDemo"," Fit still failed - continue anyway.....");

        poihat  = poi->getVal();
        m_logger << kINFO << "StandardHypoTestInvDemo - Best Fit value : " << poi->GetName() << " = "  
            << poihat << " +/- " << poi->getError() << GEndl;
        m_logger << kINFO << "Time for fitting : "; tw.Print(); 

        RooArgSet newSnapSet;
        if (tPoiSet!=0) newSnapSet.add(*tPoiSet); // make sure this is the full poi set.

        if ((prevSnapSet!=0)) {
            // add all remaining parameters from old snapshot
            TIterator* vrItr = prevSnapSet->createIterator();
            RooRealVar* vr(0);
            for (Int_t i=0; (vr = (RooRealVar*)vrItr->Next()); ++i) {
                if (vr==0) continue;
                TString vrName = vr->GetName();
                RooRealVar* par = (RooRealVar*)newSnapSet.find(vrName.Data());
                if (par==0) { newSnapSet.add(*vr); } // add if not yet present 
            }
            delete vrItr;
        }

        //save best fit value in the poi snapshot 
        //sbModel->SetSnapshot(*sbModel->GetParametersOfInterest());
        sbModel->SetSnapshot(newSnapSet);
        m_logger << kINFO << "StandardHypoTestInvo: snapshot of S+B Model " << sbModel->GetName() 
            << " is set to the best fit value" << GEndl;  
    }

    // and reset poi
    poi->setVal(poihat);

    // build test statistics and hypotest calculators for running the inverter 

    // print a message in case of LEP test statistics because it affects result by doing or not doing a fit 
    if (testStatType == 0) {
        if (!doFit) 
            Info("StandardHypoTestInvDemo","Using LEP test statistic - an initial fit is not done and the TS will use the nuisances at the model value");
        else 
            Info("StandardHypoTestInvDemo","Using LEP test statistic - an initial fit has been done and the TS will use the nuisances at the best fit value");
    }

    // MB: this sets up the null and one hypothesis tests
    ModelConfig* nullModel = ( doUL ? sbModel : bModel );
    ModelConfig* altModel  = ( doUL ? bModel : sbModel );

    // build test statistics and hypotest calculators for running the inverter 
    SimpleLikelihoodRatioTestStat* slrts(0);
    if (testStatType == 0) {
        slrts = new SimpleLikelihoodRatioTestStat(*nullModel->GetPdf(),*altModel->GetPdf());

        // null parameters must includes snapshot of poi plus the nuisance values 
        RooArgSet nullParams(*nullModel->GetSnapshot());
        if (nullModel->GetNuisanceParameters()) nullParams.add(*nullModel->GetNuisanceParameters());
        if (nullModel->GetSnapshot()) slrts->SetNullParameters(nullParams);
        RooArgSet altParams(*altModel->GetSnapshot());
        if (altModel->GetNuisanceParameters()) altParams.add(*altModel->GetNuisanceParameters());
        if (altModel->GetSnapshot()) slrts->SetAltParameters(altParams);

        slrts->SetReuseNLL(mOptimize);
    }  

    // ratio of profile likelihood - need to pass snapshot for the alt
    RatioOfProfiledLikelihoodsTestStat* ropl(0);
    if (testStatType == 1) {
        ropl = new RatioOfProfiledLikelihoodsTestStat(*nullModel->GetPdf(), *altModel->GetPdf(), altModel->GetSnapshot());
        ropl->SetSubtractMLE(false);
        ropl->SetPrintLevel(mPrintLevel);
        ropl->SetMinimizer(mMinimizerType.c_str());
        ropl->SetReuseNLL(mOptimize);
        if (mOptimize) ropl->SetStrategy(0);
    }  

    ProfileLikelihoodTestStat* profll(0);
    if (testStatType == 2 || testStatType==3) {
        profll = new ProfileLikelihoodTestStat(*nullModel->GetPdf());
        if (testStatType == 3) { 
            profll->SetOneSided(1);
            if (!doUL) profll->SetOneSidedDiscovery(1);
        }
        profll->SetMinimizer(mMinimizerType.c_str());
        profll->SetPrintLevel(mPrintLevel);
        profll->SetReuseNLL(mOptimize);
        if (mOptimize) profll->SetStrategy(0);
        profll->SetLOffset();
    }

    if (mMaxPoi > 0) poi->setMax(mMaxPoi);  // increase limit

    MaxLikelihoodEstimateTestStat* maxll(0);
    if (testStatType == 4) {
        maxll = new MaxLikelihoodEstimateTestStat(*nullModel->GetPdf(),*poi); 
    }  

    // create the HypoTest calculator class 
    this->ResetHypoTestCalculator(); // first clear

    if (type == 0) m_hc = new FrequentistCalculator(*data, *altModel, *nullModel);
    else if (type == 1) m_hc = new HybridCalculator(*data, *altModel, *nullModel);
    else if (type == 2) m_hc = new AsymptoticCalculator(*data, *altModel, *nullModel);
    else if (type == 3) m_hc = new AsymptoticCalculator(*data, *altModel, *nullModel, true);  // for using Asimov data generated with nominal values 
    else {
        Error("HypoTestTool","Invalid - calculator type = %d supported values are only :\n\t\t\t 0 (Frequentist) , 1 (Hybrid) , 2 (Asymptotic) ",type);
        return false;
    }

    // set the test statistic 
    TestStatistic * testStat = 0;
    if (testStatType == 0) {
        testStat = slrts;
    }
    if (testStatType == 1) {
        testStat = ropl;
    }
    if (testStatType == 2 || testStatType == 3) { 
        testStat = profll;
    }
    if (testStatType == 4) {
        testStat = maxll;
    }
    if (testStat == 0) { 
        Error("HypoTestTool","Invalid - test statistic type = %d supported values are only :\n\t\t\t 0 (SLR) , 1 (Tevatron) , 2 (PLR), 3 (PLR1), 4(MLE)",testStatType);
        return false;
    }  

    ToyMCSampler *toymcs = (ToyMCSampler*)m_hc->GetTestStatSampler();
    if (toymcs) { 
        if (useNumberCounting) toymcs->SetNEventsPerToy(1);
        toymcs->SetTestStatistic(testStat);

        if (data->isWeighted() && !mGenerateBinned) { 
            Info("HypoTestTool","Data set is weighted, nentries = %d and sum of weights = %8.1f but toy generation is unbinned - it would be faster to set mGenerateBinned to true\n",
                    data->numEntries(), data->sumEntries());
        }
        toymcs->SetGenerateBinned(mGenerateBinned);

        toymcs->SetUseMultiGen(mOptimize);

        if (mGenerateBinned &&  nullModel->GetObservables()->getSize() > 2) { 
            Warning("HypoTestTool","generate binned is activated but the number of ovservable is %d. Too much memory could be needed for allocating all the bins",
                    nullModel->GetObservables()->getSize() );

            // set the random seed if needed
            if (mRandomSeed >= 0) RooRandom::randomGenerator()->SetSeed(mRandomSeed); 
        } 
    }

    if (type == 1) { 
        HybridCalculator *hhc = dynamic_cast<HybridCalculator*> (m_hc);
        assert(hhc);

        hhc->SetToys( static_cast<Int_t>(ntoys), static_cast<Int_t>(ntoys/mNToysRatio) ); // can use less ntoys for b hypothesis 

        // remove global observables from ModelConfig (this is probably not needed anymore in 5.32)
        altModel->SetGlobalObservables(RooArgSet() );
        nullModel->SetGlobalObservables(RooArgSet() );

        // check for nuisance prior pdf in case of nuisance parameters 
        if (altModel->GetNuisanceParameters() || nullModel->GetNuisanceParameters() ) {

            // fix for using multigen (does not work in this case)
            toymcs->SetUseMultiGen(false);
            ToyMCSampler::SetAlwaysUseMultiGen(false);

            RooAbsPdf * nuisPdf = 0; 
            if (nuisPriorName) nuisPdf = w->pdf(nuisPriorName);
            // use prior defined first in altModel (then in nullModel)
            if (!nuisPdf)  { 
                Info("HypoTestTool","No nuisance pdf given for the HybridCalculator - try to deduce  pdf from the model");
                if (altModel->GetPdf() && altModel->GetObservables() ) 
                    nuisPdf = RooStats::MakeNuisancePdf(*altModel,"nuisancePdf_bmodel");
                else 
                    nuisPdf = RooStats::MakeNuisancePdf(*nullModel,"nuisancePdf_sbmodel");
            }   
            if (!nuisPdf ) {
                if (altModel->GetPriorPdf())  { 
                    nuisPdf = altModel->GetPriorPdf();
                    Info("HypoTestTool","No nuisance pdf given - try to use %s that is defined as a prior pdf in the B model",nuisPdf->GetName());            
                }
                else { 
                    Error("HypoTestTool","Cannnot run Hybrid calculator because no prior on the nuisance parameter is specified or can be derived");
                    return false;
                }
            }
            assert(nuisPdf);
            Info("HypoTestTool","Using as nuisance Pdf ... " );
            nuisPdf->Print();

            const RooArgSet * nuisParams = (altModel->GetNuisanceParameters() ) ? altModel->GetNuisanceParameters() : nullModel->GetNuisanceParameters();
            RooArgSet * np = nuisPdf->getObservables(*nuisParams);
            if (np->getSize() == 0) { 
                Warning("HypoTestTool","Prior nuisance does not depend on nuisance parameters. They will be smeared in their full range");
            }
            delete np;

            hhc->ForcePriorNuisanceAlt(*nuisPdf);
            hhc->ForcePriorNuisanceNull(*nuisPdf);  
        }
    } 
    else if (type == 2 || type == 3) { 
        if (testStatType == 3) ((AsymptoticCalculator*) m_hc)->SetOneSided(true);  
        if (testStatType != 2 && testStatType != 3)  
            Warning("StandardHypoTestInvDemo","Only the PL test statistic can be used with AsymptoticCalculator - use by default a two-sided PL");
        ((AsymptoticCalculator*) m_hc)->SetQTilde(true); // bug in roostats. Need to turn on explicitly.
        ((AsymptoticCalculator*) m_hc)->SetPrintLevel(mPrintLevel+1); 
    }
    else if (type == 0 || type == 1) 
        ((FrequentistCalculator*) m_hc)->SetToys( static_cast<Int_t>(ntoys), static_cast<Int_t>(ntoys/mNToysRatio) ); 

    // Get the result
    RooMsgService::instance().getStream(1).removeTopic(RooFit::NumIntegration);

    m_logger << kINFO << ">>> Done setting up HypoTestCalculator on the workspace " << w->GetName() << GEndl;

    return true;
}


//_______________________________________________________________________________________
bool
RooStats::HypoTestTool::SetupHypoTestInverter(RooWorkspace * w,
        const char * modelSBName, const char * modelBName, 
        const char * dataName, int type,  int testStatType, 
        bool useCLs, int npoints, double poimin, double poimax, 
        int ntoys,
        bool useNumberCounting,
        const char * nuisPriorName ){

    m_logger << kINFO << ">>> Setting up HypoTestInverter on the workspace " << w->GetName() << GEndl;

    bool ok = this->SetupHypoTestCalculator(w, true, modelSBName, modelBName, dataName, type, testStatType,   
            ntoys, useNumberCounting, nuisPriorName ); /// MB : Note the true : always assuming exclusion here

    if (!ok) {
        return 0;
    }

    /// by now m_hc has been setup okay ...

    this->ResetHypoTestInverter();
    m_calc = new HypoTestInverter(*m_hc);

    m_calc->SetConfidenceLevel(mConfLevel); /// default = 95% CL

    m_calc->UseCLs(useCLs);
    m_calc->SetVerbose(true);

    // can speed up using proof-lite
    if (mUseProof && mNWorkers > 1) { 
        ToyMCSampler *toymcs = (ToyMCSampler*)m_hc->GetTestStatSampler();
        ProofConfig pc(*w, mNWorkers, "", kFALSE);
        toymcs->SetProofConfig(&pc);    // enable proof
    }

    // get models from WS
    // get the modelConfig out of the file
    ModelConfig* sbModel = (ModelConfig*) w->obj(modelSBName);

    if (!sbModel) {
        Error("HypoTestTool","Not existing ModelConfig %s",modelSBName);
        return false;
    }
    // check the model 
    if (!sbModel->GetPdf()) { 
        Error("HypoTestTool","Model %s has no pdf ",modelSBName);
        return false;
    }
    if (!sbModel->GetParametersOfInterest()) {
        Error("HypoTestTool","Model %s has no poi ",modelSBName);
        return false;
    }
    if (!sbModel->GetObservables()) {
        Error("HypoTestTool","Model %s has no observables ",modelSBName);
        return false;
    }
    if (!sbModel->GetSnapshot() ) { 
        Info("HypoTestTool","Model %s has no snapshot  - make one using model poi",modelSBName);
        sbModel->SetSnapshot( *sbModel->GetParametersOfInterest() );
    }

    // get poi values
    const RooArgSet * poiSet = sbModel->GetParametersOfInterest();
    RooRealVar *poi = (RooRealVar*)poiSet->first();
    double poihat  = poi->getVal();

    if (npoints > 0) {
        if (poimin > poimax) { 
            // if no min/max given scan between MLE and +4 sigma 
            if (poimin>poihat) { poimin = poihat - 4 * poi->getError(); }
            if (poimin<0) { poimin = 0; }
            poimax = ( poihat +  20 * poi->getErrorHi() );
        }
        m_logger << kINFO << "Doing a fixed scan  in interval : " << poimin << " , " << poimax << GEndl;
        if ( poimax > poi->getMax() ) { poi->setMax( poimax ); }
        m_calc->SetFixedScan(npoints,poimin,poimax);
    }
    else { 
        m_logger << kINFO << "Doing an  automatic scan  in interval : " << poi->getMin() << " , " << poi->getMax() << GEndl;
    }

    m_logger << kINFO << ">>> Done setting up HypoTestInverter on the workspace " << w->GetName() << GEndl;

    return true;
}




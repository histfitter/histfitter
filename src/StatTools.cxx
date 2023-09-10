// vim: ts=4:sw=4

// STL include(s)
#include <iostream>
#include <fstream>

// ROOT include(s)
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
#include "RooDataSet.h"
#include "RooProduct.h"
#include "RooMCStudy.h"
#include "Roo1DTable.h"
#include "RooCategory.h"
#include "RooRealSumPdf.h"
#include "RooMinimizer.h"
#include "RooPlot.h"
#include "RooNLLVar.h"

#include "RooStats/ModelConfig.h"
#include "RooStats/ProfileLikelihoodTestStat.h"
#include "RooStats/ProfileLikelihoodCalculator.h"
#include "RooStats/LikelihoodInterval.h"
#include "RooStats/ToyMCSampler.h"
//#include "RooStats/SamplingDistPlot.h"
#include "RooStats/HypoTestInverterResult.h"
#include "RooStats/HypoTestResult.h"

#include "TF1.h"
#include "TH2D.h"
#include "TTree.h"
#include "TBranch.h"
#include "TGraph2D.h"
#include "TStyle.h"

#include "TVectorD.h"
#include "TFile.h"
#include "TLine.h"
#include "TLatex.h"
#include "TCanvas.h"
#include "TLegend.h"
#include "TLegendEntry.h"


// HistFitter include(s)
#include "StatTools.h"
#include "Utils.h"
#include "CombineWorkSpaces.h"
#include "TMsgLogger.h"
#include "HypoTestTool.h"

using namespace std;
using namespace RooFit;
using namespace RooStats;

using hf::kVERBOSE;
using hf::kDEBUG;
using hf::kINFO;
using hf::kWARNING;
using hf::kERROR;
using hf::kFATAL;
using hf::kALWAYS;


static hf::TMsgLogger StatToolsLogger("StatTools");

//________________________________________________________________________________________________
// the caller owns the returned dataset.
TTree* RooStats::toyMC_gen_fit( RooWorkspace* w, const int& nexp, const double& muVal, const bool& doDataFitFirst, const bool& storetoys, const TString& toyoutfile ) {
    // basic checks 
    if (w==0) {
        StatToolsLogger << kERROR << "Input workspace is null. Return." << GEndl;
        return NULL;
    }

    RooStats::ModelConfig* mc = hf::Util::GetModelConfig(w);
    if(mc==0){
        StatToolsLogger << kERROR << "ModelConfig is null!" << GEndl;
        return NULL;
    }
    mc->Print();

    // reset (bkg) parameters to values found in data
    if (doDataFitFirst) {
        RooFitResult* result = hf::Util::doFreeFit(w,0,false) ;
        delete result;
    }

    // silence the output
    //RooMsgService::instance().setGlobalKillBelow(ERROR); 
    RooMsgService::instance().setGlobalKillBelow(StatToolsLogger.GetRooFitMsgLevel()); 

    // to avoid effects from boundary and simplify asymptotic comparison, set min=-max
    RooRealVar* poi = hf::Util::GetPOI(w);
    Bool_t allowNegativeMu=kTRUE;
    if (allowNegativeMu && (muVal>=0)) poi->setMin(-1*poi->getMax());

    // reset poi val to be used in toy generation
    if (poi!=0 && muVal>=0) { poi->setVal(muVal); }

    // setup roomcstudy. This is only used for storage of PE fit results.
    RooMCStudy* mcstudy = hf::Util::GetMCStudy(w); 

    ///////////////////////////////////////////////////////////////////////////////////
    // Now setup the toy mc sampler. This provides the datasets to be fitted.
    ///////////////////////////////////////////////////////////////////////////////////

    int nPOI = mc->GetParametersOfInterest()->getSize();
    if(nPOI>1){
        StatToolsLogger << kWARNING << "not sure what to do with other parameters of interest, but here are their values" << GEndl;
        mc->GetParametersOfInterest()->Print("v");
    }

    // create the test stat sampler
    ProfileLikelihoodTestStat ts(*mc->GetPdf());

    // create and configure the ToyMCSampler
    ToyMCSampler sampler(ts,nexp);
    sampler.SetPdf(*mc->GetPdf());
    sampler.SetObservables(*mc->GetObservables());
    sampler.SetGlobalObservables(*mc->GetGlobalObservables());
    //sampler.SetGenerateAutoBinned(false); // MB: temporary fix. Zero weights not working for simpdf-data set
    //sampler.SetGenerateBinned(false); // dito
    sampler.SetParametersForTestStat(*mc->GetParametersOfInterest()); // set POI value for evaluation

    RooArgSet poiAndNuisance;
    poiAndNuisance.add(*mc->GetParametersOfInterest());
    poiAndNuisance.add(*mc->GetNuisanceParameters());
    RooArgSet* nullParams = (RooArgSet*) poiAndNuisance.snapshot(); 

    // will be used as start values of fit
    w->saveSnapshot("paramsToFitPE",poiAndNuisance);

    StatToolsLogger << kINFO << "Parameter values used for generation " << GEndl;
    nullParams->Print("v");

    /////////////////////////////////////////////////////////////////////////////////////////////////////
    // Start the toy loop 

    /*
       for (int i=0; i<nexp; ++i) {

       if ((i%10)==0) {
       StatToolsLogger << kINFO << "Now processing : " << i << "/" << nexp << GEndl;
       }

    // reset starting values of fit
    w->loadSnapshot("paramsToFitPE");

    RooAbsData* toyMC = sampler.GenerateToyData( *nullParams ); // note: this generates and *sets* the global measurements of the pdf 
    RooFitResult* rfresult = mc->GetPdf()->fitTo( *toyMC, PrintLevel(-1), Verbose(0), Save(), Extended(), NumCPU(2), Minos() ); // which are used here in the fit.

    if (mcstudy!=0) { mcstudy->addFitResult(*rfresult); }
    //delete rfresult; // RooMCStudy keeps pointer to roofitresult
    delete toyMC;
    }
    */


    RooNLLVar * fNLL = NULL;
    for (int i=0; i<nexp; ++i) {

        if ((i%10)==0) {
            StatToolsLogger << kINFO << "Now processing : " << i << "/" << nexp << GEndl;
        }

        // reset starting values of fit
        w->loadSnapshot("paramsToFitPE");

        RooAbsData* toyMC = sampler.GenerateToyData( *nullParams ); // note: this generates and *sets* the global measurements of the pdf 

        //cout << "num entries = " << toyMC->numEntries() << " sum entries = " << toyMC->sumEntries() << GEndl; 
        //toyMC->Print("v");
        //RooAbsData* subset = toyMC->reduce("channelCat==channelCat::S3_meffInc");
        //subset->Print("v");
        //cout << "S3 = " << subset->sumEntries() << GEndl;

        if (fNLL == NULL) {
            fNLL = (RooNLLVar*) mc->GetPdf()->createNLL( *toyMC, RooFit::Extended(), RooFit::CloneData(kFALSE), RooFit::Constrain(*mc->GetPdf()->getParameters(*toyMC)) );
        } else {
            fNLL->setData( *toyMC );
        }

        RooMinimizer minim(*fNLL);
        minim.setMinimizerType("Minuit2");
        minim.setStrategy(0);
        minim.setEps(max(1., ::ROOT::Math::MinimizerOptions::DefaultTolerance()));
        minim.optimizeConst(true);
        minim.setVerbose(false);
        minim.setPrintLevel(-1);

        for(int counter = 0;counter<4;counter++) {
            int status = minim.minimize("Minuit", "Minimize");
            //int status = minim.minos();
            if (status == 0) {
                break;
            }
            else {
                if (counter > 1) {
                    StatToolsLogger << kINFO << "Scanning" << GEndl;
                    minim.minimize("Minuit2", "Scan");
                }
                if (counter > 2) {
                    StatToolsLogger << kINFO << "Trying with strategy = 1" << GEndl;
                    minim.setStrategy(1);
                }
            }
        }

        RooFitResult *rfresult = minim.save();
        if (mcstudy!=0) { mcstudy->addFitResult(*rfresult); }

        delete toyMC;
    }

    if (fNLL != NULL) { 
        delete fNLL; 
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////////
    // End the toy loop 

    // reset the silencer
    RooMsgService::instance().reset();

    /// convert results into ttree
    TTree* mcstree = RooStats::ConvertMCStudyResults( mcstudy );

    // store toy study results?
    if (storetoys) {
        StatToolsLogger << kINFO << "Storing MC study under : " << toyoutfile << GEndl;
        TFile* outfile = TFile::Open(toyoutfile.Data(),"RECREATE");
        outfile->cd();
        if (mcstudy!=0) { mcstree->Write(); }
        outfile->Close();
    }

    delete mcstudy; // cleanup
    return mcstree; // note: owned by caller!
}

//________________________________________________________________________________________________
TTree* RooStats::ConvertMCStudyResults( RooMCStudy* mcstudy ){
    const RooDataSet& toymc = mcstudy->fitParDataSet();

    /// initialize the ttree
    TTree* myTree = new TTree("mcstree","mcstree");

    Int_t covQual=0, status=0;
    Float_t minNll=0;
    myTree->Branch( "covQual", &covQual, "covQual/I" );
    myTree->Branch( "status",  &status,  "status/I" );
    myTree->Branch( "minNll",  &minNll,  "minNll/F" );

    std::vector<Float_t> varVals;
    const RooArgSet* args = toymc.get();
    varVals.resize( args->getSize(), -999. );

    RooRealVar* var(0);
    TIterator* varItr = args->createIterator();
    for (Int_t i=0; (var = (RooRealVar*)varItr->Next()); ++i) {
        TString varName = var->GetName();
        TString varNameF = TString(var->GetName()) + "/F";
        myTree->Branch( varName.Data(), &varVals[i], varName.Data() ); 
    }
    delete varItr;

    /// and fill the tree by looping over mcstudy
    for(int iToy=0; iToy<toymc.numEntries(); iToy++) {
        covQual = mcstudy->fitResult(iToy)->covQual();
        status  = mcstudy->fitResult(iToy)->status();
        minNll  = mcstudy->fitResult(iToy)->minNll();

        toymc.get(iToy); // this resets args to new value
        varItr = args->createIterator();
        for (Int_t i=0; (var=(RooRealVar*)varItr->Next()); ++i) { varVals[i] = var->getVal(); }
        delete varItr;

        myTree->Fill();  
    }

    return myTree;
}

//________________________________________________________________________________________________
RooStats::HypoTestInverterResult* RooStats::DoHypoTestInversion(RooWorkspace* w,
        int ntoys,
        int calculatorType ,
        int testStatType , 
        bool useCLs ,  
        int npoints ,   
        double poimin ,  
        double poimax , 
        bool doAnalyze,
        bool useNumberCounting ,
        const char* modelSBName ,
        const char* modelBName,
        const char* dataName , 
        const char* nuisPriorName,
        bool generateAsimovDataForObserved,
        int nCPUs)
{
    /*
       Other Parameter to pass in tutorial
       apart from standard for filename, ws, modelconfig and data

       type = 0 Freq calculator 
       type = 1 Hybrid calculator
       type = 2 Asymptotic calculator  
       type = 3 Asymptotic calculator using nominal Asimov data sets (not using fitted parameter values but nominal ones)

       testStatType = 0 LEP
       = 1 Tevatron 
       = 2 Profile Likelihood
       = 3 Profile Likelihood one sided (i.e. = 0 if mu < mu_hat)

       useCLs          scan for CLs (otherwise for CLs+b)    

npoints:        number of points to scan , for autoscan set npoints = -1 

poimin,poimax:  min/max value to scan in case of fixed scans 
(if min > max, try to find automatically)                           

ntoys:         number of toys to use 

useNumberCounting:  set to true when using number counting events 

nuisPriorName:   name of prior for the nnuisance. This is often expressed as constraint term in the global model
It is needed only when using the HybridCalculator (type=1)
If not given by default the prior pdf from ModelConfig is used. 

extra options are available as global paramwters of the macro. They major ones are: 

plotHypoTestResult   plot result of tests at each point (TS distributions) (defauly is true)
useProof             use Proof   (default is true) 
writeResult          write result of scan (default is true)
rebuild              rebuild scan for expected limits (require extra toys) (default is false)
generateBinned       generate binned data sets for toys (default is false) - be careful not to activate with 
a too large (>=3) number of observables 
nToyRatio            ratio of S+B/B toys (default is 2)
*/

    if (w == NULL) {
        StatToolsLogger << kERROR << "input workspace is NULL - Exit." << GEndl;
        return 0;
    }

    HypoTestTool calc;
    calc.SetParameter("EnableDetailedOutput", true);

    // set parameters
    /*
       calc.SetParameter("PlotHypoTestResult", plotHypoTestResult);
       calc.SetParameter("WriteResult", writeResult);
       calc.SetParameter("Optimize", optimize);
       calc.SetParameter("UseVectorStore", useVectorStore);
       calc.SetParameter("GenerateBinned", generateBinned);
       calc.SetParameter("NToysRatio", nToysRatio);
       calc.SetParameter("MaxPOI", maxPOI);
       calc.SetParameter("UseProof", useProof);
       calc.SetParameter("EnableDetailedOutput", true);
       calc.SetParameter("NWorkers", nworkers);
       calc.SetParameter("Rebuild", rebuild);
       calc.SetParameter("NToyToRebuild", nToyToRebuild);
       calc.SetParameter("MassValue", massValue.c_str());
       calc.SetParameter("MinimizerType", minimizerType.c_str());
       calc.SetParameter("PrintLevel", printLevel);
       calc.SetParameter("InitialFit",initialFit);
       calc.SetParameter("ResultFileName",resultFileName);
       calc.SetParameter("RandomSeed",randomSeed);
       */
    if (nCPUs > 1){
        StatToolsLogger << kINFO << "setting use of PROOF to true, nCPUs=" << nCPUs << GEndl; 
        calc.SetParameter("UseProof", true);
        calc.SetParameter("NWorkers", nCPUs);
    }

    calc.SetParameter("GenerateAsimovDataForObserved", generateAsimovDataForObserved);

    HypoTestInverterResult* r = 0;  
    r = calc.RunHypoTestInverter( w, modelSBName, modelBName,
            dataName, calculatorType, testStatType, useCLs,
            npoints, poimin, poimax,  
            ntoys, useNumberCounting, nuisPriorName );    
    if (!r) { 
        StatToolsLogger << kERROR << "Error running the HypoTestInverter - Exit " << GEndl;
        return 0;          
    }

    if (doAnalyze) 
        calc.AnalyzeResult( r, calculatorType, testStatType, useCLs, npoints, w->GetName() );

    return r;
}

//________________________________________________________________________________________________
RooStats::HypoTestInverterResult* RooStats::DoHypoTestInversionAutoScan(RooWorkspace* w,
        int ntoys,
        int calculatorType ,
        int testStatType , 
        bool useCLs ,  
        int npoints ,   
        double poimin ,  
        double poimax , 
        bool doAnalyze,
        bool useNumberCounting ,
        const char* modelSBName ,
        const char* modelBName,
        const char* dataName , 
        const char* nuisPriorName,
        bool generateAsimovDataForObserved,
        int nCPUs,
        std::vector<double> hints)
{
    UNUSED(poimin);
    UNUSED(poimax);

    double initial_guess_mult = 1; // multi POI error by this much for first guess

    if (w == NULL) {
        StatToolsLogger << kERROR << "input workspace is NULL - Exit." << GEndl;
        return 0;
    }

    
    HypoTestTool calc;
    calc.SetParameter("EnableDetailedOutput", true);
    
    
    if (nCPUs > 1){
        StatToolsLogger << kINFO << "setting use of PROOF to true, nCPUs=" << nCPUs << GEndl; 
        calc.SetParameter("UseProof", true);
        calc.SetParameter("NWorkers", nCPUs);
    }

    calc.SetParameter("GenerateAsimovDataForObserved", generateAsimovDataForObserved);

    // return value
    HypoTestInverterResult* r = 0; 
    
    // Initial estimate of poi value to test
    RooFitResult* result = hf::Util::doFreeFit(w,0,false) ;
    delete result;

    ModelConfig* sbModel = (ModelConfig*) w->obj(modelSBName);
    RooRealVar *poi = (RooRealVar*)sbModel->GetParametersOfInterest()->first();
    double poihat = poi->getVal();
    double poiup = poihat + initial_guess_mult*fabs(poi->getError()); 
    //std::cout<<"POI val after fit "<<poihat << " errorLo = " << poi->getErrorLo()<< " errorHi = " << poi->getErrorHi()<< " error = " << poi->getError()<<std::endl;


    HypoTestInverterResult* r_asym = NULL;
    HypoTestInverterResult* r_temp = NULL;

    // Asymptotic UL first
    int method = 0; // Auto scan method
    std::vector<double> test_pois = {poiup};    
    if (hints.size() > 0) 
    {
        test_pois = hints;// if we were given hints, just use those
        method = 1;
    }

    std::map<double, HypoTestInverterResult*> map_poi_hti;

    // Loop through points
    double test_point = 0;
    while (test_point >= 0)
    {
        HypoTestInverterResult* r_test = calc.RunHypoTestInverter( 
            w, modelSBName, modelBName,
            dataName, 2, testStatType, useCLs,
            1, test_point, test_point+10.,  
            ntoys, useNumberCounting, nuisPriorName ); 

        map_poi_hti.emplace(test_point, r_test);

        
        if (r_temp) 
        {
            r_temp->Add(*r_test);
            //delete r_test;
        }
        else
        {
            r_temp = static_cast<HypoTestInverterResult*>(r_test->Clone());
        }
        
        // Get next test point, based on extrapolating 
        test_point = nextTestPOI(test_pois, r_temp, method);
        // Switch to refining test points once the line above has converged
        if (test_point < 0 and method == 0 ) 
        {
            method = 1;
            test_point = nextTestPOI(test_pois, r_temp, method);
        }
        //std::cout<<"Asym TEST POINT "<<test_point<<std::endl;
    }
    delete r_temp;
    r_temp = NULL;

    // Put test points in order of POI, otherwise ROOT removes them
    r_asym = map_poi_hti.begin()->second; // need something to start adding to
    std::map<double, HypoTestInverterResult*>::iterator it;
    for (it = std::next(map_poi_hti.begin()); it != map_poi_hti.end(); it++)
    {
        r_asym->Add( *(it->second) );
        delete it->second;
    }

    // We're only running asymptotics, so set that as the return value.
    if (calculatorType == 2) r = r_asym;
    
    // Toy based UL
    if (calculatorType == 0) 
    {
        method = 0;
        map_poi_hti.clear();

        // Seed values from asymptotic UL
        double UL_obs_asymm = r_asym->UpperLimit();
        //double UL_exp_asymm = r_asym->GetExpectedUpperLimit(0);
        double UL_exp_up_asymm = r_asym->GetExpectedUpperLimit(1);
        double UL_exp_dw_asymm = r_asym->GetExpectedUpperLimit(-1);

        // List of POIs to evaluate
        //double sigma2_up = UL_exp_asymm + 2*fabs(UL_exp_asymm-UL_exp_up_asymm);
        //double sigma2_dw = UL_exp_asymm - 2*fabs(UL_exp_asymm-UL_exp_dw_asymm);
        // Ignore the 2 sigma band.  If we want to guarantee that also goes below the CLs threshold, then add the points commented out below
        std::vector<double> test_pois = {UL_obs_asymm, UL_exp_up_asymm, UL_exp_dw_asymm}; //, sigma2_up, sigma2_dw};
        

        HypoTestInverterResult* r_toy = NULL;

        // Loop through test points
        double test_point = 0;
        while (test_point >= 0)
        {
            HypoTestInverterResult* r_test = calc.RunHypoTestInverter( 
                w, modelSBName, modelBName,
                dataName, 0, testStatType, useCLs,
                1, test_point, test_point+10.,  
                ntoys, useNumberCounting, nuisPriorName ); 

            map_poi_hti.emplace(test_point, r_test);

            if (r_temp) 
            {
                r_temp->Add(*r_test);
                //delete r_test;
            }
            else
            {
                r_temp = static_cast<HypoTestInverterResult*>(r_test->Clone());
            }

            // Get next test point, based on extrapolating 
            test_point = nextTestPOI(test_pois, r_temp, method);
            // Switch to refining test points once the line above has converged
            if (test_point < 0 and method == 0 ) 
            {
                method = 1;
                test_point = nextTestPOI(test_pois, r_temp, method);
            }            
        }
        delete r_temp;
        r_temp = NULL;

        // Put test points in order of POI, otherwise ROOT removes them
        r_toy = map_poi_hti.begin()->second; // need something to start adding to
        std::map<double, HypoTestInverterResult*>::iterator it;
        for (it = std::next(map_poi_hti.begin()); it != map_poi_hti.end(); it++)
        {
            r_toy->Add( *(it->second) );
            delete it->second;
        }


        r = r_toy;

    }

    // Exit if not asymptotics or toys
    if (calculatorType == 1)
    {
        StatToolsLogger << kERROR <<"Error in HypoTestInverter, calculator type 1 not supported for AutoScan."  << GEndl;
        return 0;
    }

    if (!r) { 
        StatToolsLogger << kERROR << "Error running the HypoTestInverter - Exit " << GEndl;
        return 0;          
    }

    if (doAnalyze) 
        calc.AnalyzeResult( r, calculatorType, testStatType, useCLs, npoints, w->GetName() );

    return r;
}



//________________________________________________________________________________________________
RooStats::HypoTestResult* RooStats::DoHypoTest(RooWorkspace* w, 
        bool doUL,
        int ntoys,
        int calculatorType,
        int testStatType, 
        const char * modelSBName ,
        const char * modelBName ,
        const char * dataName ,                 
        bool useNumberCounting ,
        const char * nuisPriorName ) {
    /*
       Other Parameter to pass in tutorial
       apart from standard for filename, ws, modelconfig and data

       type = 0 Freq calculator 
       type = 1 Hybrid calculator
       type = 2 Asymptotic calculator  

       testStatType = 0 LEP
       = 1 Tevatron 
       = 2 Profile Likelihood
       = 3 Profile Likelihood one sided (i.e. = 0 if mu < mu_hat)

       useCLs          scan for CLs (otherwise for CLs+b)    

ntoys:         number of toys to use 

useNumberCounting:  set to true when using number counting events 

nuisPriorName:   name of prior for the nnuisance. This is often expressed as constraint term in the global model
It is needed only when using the HybridCalculator (type=1)
If not given by default the prior pdf from ModelConfig is used. 

extra options are available as global paramwters of the macro. They major ones are: 

plotHypoTestResult   plot result of tests at each point (TS distributions) (defauly is true)
useProof             use Proof   (default is true) 
writeResult          write result of scan (default is true)
rebuild              rebuild scan for expected limits (require extra toys) (default is false)
generateBinned       generate binned data sets for toys (default is false) - be careful not to activate with 
a too large (>=3) number of observables 
nToyRatio            ratio of S+B/B toys (default is 2)


*/

    if (w == NULL) {
        StatToolsLogger << kERROR << "input workspace is NULL - Exit." << GEndl;
        return 0;
    }

    HypoTestTool calc;
    calc.SetParameter("EnableDetailedOutput", true);

    // set parameters
    /*
       calc.SetParameter("PlotHypoTestResult", plotHypoTestResult);
       calc.SetParameter("WriteResult", writeResult);
       calc.SetParameter("Optimize", optimize);
       calc.SetParameter("UseVectorStore", useVectorStore);
       calc.SetParameter("GenerateBinned", generateBinned);
       calc.SetParameter("NToysRatio", nToysRatio);
       calc.SetParameter("MaxPOI", maxPOI);
       calc.SetParameter("UseProof", useProof);
       calc.SetParameter("EnableDetailedOutput", true);
       calc.SetParameter("Nworkers", nworkers);
       calc.SetParameter("Rebuild", rebuild);
       calc.SetParameter("NToyToRebuild", nToyToRebuild);
       calc.SetParameter("MassValue", massValue.c_str());
       calc.SetParameter("MinimizerType", minimizerType.c_str());
       calc.SetParameter("PrintLevel", printLevel);
       */

    HypoTestResult * r = 0;  
    r = calc.RunHypoTest(w, doUL, modelSBName, modelBName,
            dataName, calculatorType, testStatType, 
            ntoys, useNumberCounting, nuisPriorName );    
    if (!r) { 
        StatToolsLogger << kERROR << "Error running the HypoTestCalculator - Exit " << GEndl;
        return 0;          
    }

    if (doUL) { 
        r->SetBackgroundAsAlt(); 
    }

    // set p-value and sensitivity

    return r;
}

//________________________________________________________________________________________________
void RooStats::AnalyzeHypoTestInverterResult(const char* infile , 
        const char* resultName ,
        int calculatorType ,
        int testStatType , 
        bool useCLs ,  
        int npoints,
        const char* outfilePrefix,
        const char* plotType
        ) {

    TString fileName(infile);
    if (fileName.IsNull()) { 
        StatToolsLogger << kERROR << "Input filename is empty. Exit." << GEndl;
        return;
    }

    // open file and check if input file exists
    TFile * file = TFile::Open(fileName); 

    // if input file was specified but not found, quit
    if(!file && !TString(infile).IsNull()){
        StatToolsLogger << kERROR << "file " << fileName << " not found" << GEndl;
        return;
    } 

    if(!file){
        // if it is still not there, then we can't continue
        StatToolsLogger << kERROR << "Not able to run hist2workspace to create example input" <<GEndl;
        return;
    }

    HypoTestInverterResult * r = 0;  
    // case workspace is not present look for the inverter result
    StatToolsLogger << kINFO << "Reading an HypoTestInverterResult with name " << resultName << " from file " << fileName << GEndl;
    r = dynamic_cast<HypoTestInverterResult*>( file->Get(resultName) ); //
    if (!r) { 
        StatToolsLogger << kERROR << "File " << fileName << " does not contain a workspace or an HypoTestInverterResult - Exit " 
            << GEndl;
        file->ls();
        return; 
    }

    return AnalyzeHypoTestInverterResult( r, calculatorType, testStatType, useCLs, npoints, outfilePrefix, plotType );
}


//________________________________________________________________________________________________
void RooStats::AnalyzeHypoTestInverterResult(RooStats::HypoTestInverterResult* r, 
        int calculatorType,
        int testStatType , 
        bool useCLs ,  
        int npoints,
        const char* outfilePrefix,
        const char* plotType
        ) {
    if (!r) { 
        StatToolsLogger << kERROR << "No valid HypoTestInverterResult provided - Exit " << GEndl;
        return; 
    }

    //////////////////////////////////////////////////////////////////////////////////////////

    HypoTestTool calc;
    calc.SetParameter("EnableDetailedOutput", true);

    // set parameters
    /*
       calc.SetParameter("PlotHypoTestResult", plotHypoTestResult);
       calc.SetParameter("WriteResult", writeResult);
       calc.SetParameter("Optimize", optimize);
       calc.SetParameter("UseVectorStore", useVectorStore);
       calc.SetParameter("GenerateBinned", generateBinned);
       calc.SetParameter("NToysRatio", nToysRatio);
       calc.SetParameter("MaxPOI", maxPOI);
       calc.SetParameter("UseProof", useProof);
       calc.SetParameter("EnableDetailedOutput", true);
       calc.SetParameter("Nworkers", nworkers);
       calc.SetParameter("Rebuild", rebuild);
       calc.SetParameter("NToyToRebuild", nToyToRebuild);
       calc.SetParameter("MassValue", massValue.c_str());
       calc.SetParameter("MinimizerType", minimizerType.c_str());
       calc.SetParameter("PrintLevel", printLevel);
       */

    calc.AnalyzeResult( r, calculatorType, testStatType, useCLs, npoints, outfilePrefix, plotType );

    return;
}

//________________________________________________________________________________________________
RooStats::HypoTestInverterResult* RooStats::MakeUpperLimitPlot(const char* fileprefix,
        RooWorkspace* w,
        int calculatorType ,
        int testStatType , 
        int ntoys,
        bool useCLs ,  
        int npoints ) {
    /// first asumptotic limit, to get a quick but reliable estimate for the upper limit
    /// dynamic evaluation of ranges
    RooStats::HypoTestInverterResult* hypo = DoHypoTestInversion(w, 1, 2, testStatType, useCLs, 20, 0, -1);  
    int nPointsRemoved = hypo->ExclusionCleanup();
    if(nPointsRemoved > 0) {
        StatToolsLogger << kWARNING << "MakeUpperLimitPlot(): ExclusionCleanup() removed " << nPointsRemoved << " scan point(s) for hypo test inversion (quick scan): " << hypo->GetName() << GEndl;
    } 

    /// then reevaluate with proper settings
    if ( hypo!=0 ) { 
        double eul2 = 1.10 * hypo->GetExpectedUpperLimit(2);
        delete hypo; hypo=0;
        //cout << "INFO grepme : nToys=" << ntoys << " calcType=" << calculatorType << " testStatType=" << testStatType << " useCLs=" << useCLs << " nPoints=" << npoints << " eul2=" << eul2 << std::endl;
        hypo = DoHypoTestInversion(w, ntoys, calculatorType, testStatType, useCLs, npoints, 0, eul2); 
    }

    /// store ul as nice plot ..
    if ( hypo!=0 ) {
        hypo->ExclusionCleanup();
        nPointsRemoved = hypo->ExclusionCleanup();
        if(nPointsRemoved > 0) {
            StatToolsLogger << kWARNING << "MakeUpperLimitPlot(): ExclusionCleanup() removed " << nPointsRemoved << " scan point(s) for hypo test inversion: " << hypo->GetName() << GEndl;
        }

        AnalyzeHypoTestInverterResult( hypo, calculatorType, testStatType, useCLs, npoints, fileprefix, ".eps") ;
    }

    return hypo;
}

//________________________________________________________________________________________________
hf::LimitResult RooStats::get_Pvalue(const RooStats::HypoTestInverterResult* fResults, bool doUL ) {
    // MB : code taken from HypoTestInverterPlot::MakeExpectedPlot()

    const int nEntries = fResults->ArraySize();

    // MB 20131216: bit of a hack, but we now need to know if running in discovery or exclusion mode. 
    // poi==0 is assumed convention for discovery.
    if (doUL && nEntries==1 && fResults->GetXValue(0)==0 ) {
        doUL = false;
        StatToolsLogger << kWARNING << "Change of setting: assumption of running in discovery mode. doUL = " << doUL << GEndl;
    }

    //cout << "---------------------------------> nEntries " << nEntries << GEndl;

    double nsig1(1.0);
    double nsig2(2.0);
    nsig1 = std::abs(nsig1);
    nsig2 = std::abs(nsig2);
    //bool doFirstBand = (nsig1 > 0);
    //bool doSecondBand = (nsig2 > nsig1);

    // sort the arrays based on the x values
    std::vector<unsigned int> index(nEntries);
    //TMath::SortItr(fResults->fXValues.begin(), fResults->fXValues.end(), index.begin(), false);
    index[0] = 0; // MB : assume only one entry - HACK

    double p[5]; 
    double q[5];
    std::vector<double> qv;
    qv.resize(11,-1.0);

    hf::LimitResult upperLimitResult;

    if (nEntries>1 and doUL){ // clearly an upper limit result

        RooStats::HypoTestInverterResult* myfResults = const_cast<RooStats::HypoTestInverterResult*>(fResults);
        double upperLimit = myfResults->UpperLimit();
        double ulError = myfResults->UpperLimitEstimatedError();

        StatToolsLogger << kINFO << "The computed upper limit is: " << upperLimit << " +/- " << ulError << GEndl;
        StatToolsLogger << kINFO << " expected limit (median) " << myfResults->GetExpectedUpperLimit(0) << GEndl;
        StatToolsLogger << kINFO << " expected limit (-1 sig) " << myfResults->GetExpectedUpperLimit(-1) << GEndl;
        StatToolsLogger << kINFO << " expected limit (+1 sig) " << myfResults->GetExpectedUpperLimit(1) << GEndl;
        StatToolsLogger << kINFO << " expected limit (-2 sig) " << myfResults->GetExpectedUpperLimit(-2) << GEndl;
        StatToolsLogger << kINFO << " expected limit (+2 sig) " << myfResults->GetExpectedUpperLimit(2) << GEndl;

        upperLimitResult.SetUpperLimit(myfResults->UpperLimit());
        upperLimitResult.SetUpperLimitEstimatedError(myfResults->UpperLimitEstimatedError());
        upperLimitResult.SetExpectedUpperLimit(myfResults->GetExpectedUpperLimit(0));
        upperLimitResult.SetExpectedUpperLimitPlus1Sig(myfResults->GetExpectedUpperLimit(1));
        upperLimitResult.SetExpectedUpperLimitPlus2Sig(myfResults->GetExpectedUpperLimit(2));
        upperLimitResult.SetExpectedUpperLimitMinus1Sig(myfResults->GetExpectedUpperLimit(-1));
        upperLimitResult.SetExpectedUpperLimitMinus2Sig(myfResults->GetExpectedUpperLimit(-2));
    }

    // MPB: this is called after running HistFitter with -l option --> attached upper limit results or returm call to default constructor
    if (nEntries!=1) { 
        return upperLimitResult;   
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // Only 1 HypoTestResult from now on ... 
    // Could be discovery or exclusion case
    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    p[0] = ROOT::Math::normal_cdf(-nsig2);
    p[1] = ROOT::Math::normal_cdf(-nsig1);
    p[2] = 0.5;
    p[3] = ROOT::Math::normal_cdf(nsig1);
    p[4] = ROOT::Math::normal_cdf(nsig2);

    bool resultIsAsymptotic = ( !fResults->GetNullTestStatDist(0) && !fResults->GetAltTestStatDist(0) ); 
    hf::LimitResult dummyResult;
    dummyResult.SetP0( -1 );
    dummyResult.SetP1( -1 );
    dummyResult.SetCLs( -1 );

    /// 1. exclusion case
    if (doUL) {
        int i = index[0]; // i is the order index 

        SamplingDistribution * s = fResults->GetExpectedPValueDist(i) ;
        if (!s) { 
            StatToolsLogger << kERROR << "Sampling distribution is empty. Exit." << GEndl;
            return dummyResult;
            //exit(1); 
        } 
        const std::vector<double> & values = s->GetSamplingDistribution();

        /// expected p-values
        // special case for asymptotic results (cannot use TMath::quantile in that case)
        if (resultIsAsymptotic) { 
            double maxSigma = 5; // == HypoTestInverterResult::fgAsymptoticMaxSigma; // MB: HACK
            double dsig = 2.*maxSigma / (values.size() -1) ;         
            int  i0 = (int) TMath::Floor ( ( -nsig2 + maxSigma )/dsig + 0.5 );
            int  i1 = (int) TMath::Floor ( ( -nsig1 + maxSigma )/dsig + 0.5 );
            int  i2 = (int) TMath::Floor ( ( maxSigma )/dsig + 0.5 );
            int  i3 = (int) TMath::Floor ( ( nsig1 + maxSigma )/dsig + 0.5 );
            int  i4 = (int) TMath::Floor ( ( nsig2 + maxSigma )/dsig + 0.5 );
            q[0] = values[i0];
            q[1] = values[i1];
            q[2] = values[i2];
            q[3] = values[i3];
            q[4] = values[i4];
        } else { 
            double * x = const_cast<double *>( &values[0] ); // need to change TMath::Quantiles
            TMath::Quantiles(values.size(), 5, x, q, p, false);
        }

        /// store useful quantities for reuse later ...
        /// http://root.cern.ch/root/html532/src/RooStats__HypoTestInverterPlot.cxx.html#197
        for (int j=0; j<5; ++j) { qv[j]=q[j]; }

        delete s; s=0;
    }
    /// 2. discovery case
    else {
        if (resultIsAsymptotic) {

            SamplingDistribution *s = fResults->GetExpectedPValueDist(0) ;
            if (!s) { 
                StatToolsLogger << kERROR << "Sampling distribution is empty. Exit." << GEndl;
                return dummyResult;
                //exit(1); 
            } 
            const std::vector<double> values = s->GetSamplingDistribution();

            double maxSigma = 5; // == HypoTestInverterResult::fgAsymptoticMaxSigma; // MB: HACK
            double dsig = 2.*maxSigma / (values.size() -1) ;         
            int  i0 = (int) TMath::Floor ( ( -nsig2 + maxSigma )/dsig + 0.5 );
            int  i1 = (int) TMath::Floor ( ( -nsig1 + maxSigma )/dsig + 0.5 );
            int  i2 = (int) TMath::Floor ( ( maxSigma )/dsig + 0.5 );
            int  i3 = (int) TMath::Floor ( ( nsig1 + maxSigma )/dsig + 0.5 );
            int  i4 = (int) TMath::Floor ( ( nsig2 + maxSigma )/dsig + 0.5 );
            qv[0] = values[i0];
            qv[1] = values[i1];
            qv[2] = values[i2];
            qv[3] = values[i3];
            qv[4] = values[i4];

            delete s; //we own this - see https://root.cern.ch/root/html/src/RooStats__HypoTestInverterResult.cxx.html#Xhee2
        } else {
            RooStats::HypoTestResult* oneresult = new RooStats::HypoTestResult( *fResults->GetResult(0) ) ;

            SamplingDistribution* t = oneresult->GetAltDistribution() ;
            unsigned int sampleSize = t->GetSamplingDistribution().size() ;
            const std::vector<double> values = t->GetSamplingDistribution();

            int idx[5];
            double ts[5]; 
            for (int j=0; j<5; ++j) {
                idx[j] = (int) TMath::Floor ( p[j] * sampleSize + 0.5 );
                ts[j] = values[idx[j]];	      
                oneresult->SetTestStatisticData( ts[j] );
                qv[j] = oneresult->NullPValue() ;
                //cout << idx[j] << " " << ts[j] << " " << pexp[j] << std::endl;
                // for storage later
            }

            delete t;
            delete oneresult; 
        }
    }

    // store info into parsable limitresult object

    /// observed p-values
    double p0 = fResults->GetResult(0)->NullPValue();
    qv[5]  = fResults->CLs(0) ; //
    qv[7]  = fResults->CLb(0) ; //
    qv[9]  = fResults->CLsplusb(0) ; //
    qv[6]  = fResults->CLsError(0) ; //
    qv[8]  = fResults->CLbError(0) ; //
    qv[10] = fResults->CLsplusbError(0) ; //

    /// And pass on to limitresult object
    hf::LimitResult result;
    result.SetP0(     p0 );
    result.SetP1(     qv[9] );
    result.SetCLs(    qv[5] );
    if (doUL) { /// exclusion 
        result.SetCLsd2S( qv[0] );  
        result.SetCLsd1S( qv[1] );
        result.SetCLsexp( qv[2] );
        result.SetCLsu1S( qv[3] );
        result.SetCLsu2S( qv[4] );
    } else { ///  discovery
        result.SetP0d2S( qv[0] );
        result.SetP0d1S( qv[1] );
        result.SetP0exp( qv[2] );
        result.SetP0u1S( qv[3] );
        result.SetP0u2S( qv[4] );
    }

    return result;
}

//________________________________________________________________________________________________
hf::LimitResult RooStats::get_Pvalue(     RooWorkspace* w,
        bool doUL, // = true, // true = exclusion, false = discovery
        int ntoys, //=1000,
        int calculatorType, // = 0,
        int testStatType, // = 3,  
        const char * modelSBName, // = "ModelConfig",
        const char * modelBName, // = "",
        const char * dataName, // = "obsData",
        bool useCLs, // = true ,   
        bool useNumberCounting, // = false,
        const char * nuisPriorName) // = 0  
{
    hf::LimitResult lres;

    double muVal = ( doUL ? 1.0 : 0.0 );

    if (doUL) { // exclusion
        RooStats::HypoTestInverterResult* result = DoHypoTestInversion(w, 
                ntoys, calculatorType, testStatType, 
                useCLs, 
                1, muVal, muVal, // test of single point only
                false, // no plots 
                useNumberCounting, 
                modelSBName, modelBName,
                dataName, 
                nuisPriorName ) ;
        if (result==0) { return lres; }    
        lres = RooStats::get_Pvalue( result );

    } else {  // discovery
        if (testStatType==3) {
            // MB: Hack, needed for ProfileLikeliHoodTestStat to work properly.
            if (testStatType==3) { 
                StatToolsLogger << kWARNING << "Discovery mode --> Need to change test-statistic type from one-sided to two-sided for RooStats to work." << GEndl; 
                StatToolsLogger << kWARNING << "(Note: test is still one-sided.)" << GEndl; 
                testStatType=2; 
            } 
        }

        RooStats::HypoTestResult* result = DoHypoTest(w,doUL,ntoys,calculatorType,testStatType,modelSBName,modelBName,dataName,
                useNumberCounting,nuisPriorName);
        if (result == 0) { 
            return lres; 
        }

        lres = RooStats::get_Pvalue( result );
    }

    return lres;
}

//________________________________________________________________________________________________
hf::LimitResult RooStats::get_Pvalue( const RooStats::HypoTestResult* fResult, bool doUL )
{
    RooStats::HypoTestInverterResult* hti = new RooStats::HypoTestInverterResult();
    if (doUL) { // exclusion test
        hti->Add( 1.0, *fResult );
    } else { // discovery
        hti->Add( 0.0, *fResult );
    }  
    hti->UseCLs(doUL);

    return RooStats::get_Pvalue( hti, doUL );
}

//________________________________________________________________________________________________
double RooStats::get_Presult(  RooWorkspace* w,
        bool doUL, // = true, // true = exclusion, false = discovery
        int ntoys, //=1000,
        int calculatorType, // = 0,
        int testStatType, // = 3,  
        const char * modelSBName, // = "ModelConfig",
        const char * modelBName, // = "",
        const char * dataName, // = "obsData",
        bool useCLs, // = true ,   
        bool useNumberCounting, // = false,
        const char * nuisPriorName) // = 0 
{
    double pvalue(-1.);

    RooStats::HypoTestResult* result = RooStats::get_htr(w,doUL,ntoys,calculatorType,testStatType,
            modelSBName,modelBName,dataName,
            useCLs,useNumberCounting,nuisPriorName);
    if (result!=0) { result->Print(); }
    else { return pvalue; }

    // set relevant p-value
    if (!doUL) { 
        pvalue = result->NullPValue(); 
    } else {
        result->SetBackgroundAsAlt(); 
        if (useCLs) { pvalue = result->CLs(); }
        else        { pvalue = result->CLsplusb(); }
    }

    delete result;

    return pvalue;
}


//________________________________________________________________________________________________
RooStats::HypoTestResult* RooStats::get_htr(  RooWorkspace* w,
        bool doUL, // = true, // true = exclusion, false = discovery
        int ntoys, //=1000,
        int calculatorType, // = 0,
        int testStatType, // = 3,  
        const char * modelSBName, // = "ModelConfig",
        const char * modelBName, // = "",
        const char * dataName, // = "obsData",
	bool /*useCLs*/, // = true ,   
        bool useNumberCounting, // = false,
        const char * nuisPriorName) // = 0 
{
    if (!doUL && testStatType==3) {
        // MB: Hack, needed for ProfileLikeliHoodTestStat to work properly.
        if (testStatType==3) { 
            StatToolsLogger << kWARNING << "Discovery mode --> Need to change test-statistic type from one-sided to two-sided for RooStats to work." << GEndl; 
            StatToolsLogger << kWARNING << "(Note: test is still one-sided.)" << GEndl; 
            testStatType=2; 
        } 
    }

    RooStats::HypoTestResult* result = RooStats::DoHypoTest(w,doUL,ntoys,calculatorType,testStatType,
            modelSBName,modelBName,dataName,
            useNumberCounting,nuisPriorName);
    return result;
}



//________________________________________________________________________________________________
double RooStats::nextTestPOI(std::vector<double> &test_pois, HypoTestInverterResult *HTIR, int method)
{
    double CLs_threshold = 0.05; // CLs value used to evaluate UL
    double nextPoint = -1.; // default
    double overshoot_fraction = 1.1; // Next poi value via linear extrapolatoin is multiplied by this to coverge faster

    // Run all of the input suggested points first
    if (test_pois.size() > 0) 
    {
        nextPoint = test_pois.back();
        test_pois.pop_back();
        return nextPoint;
    }
    else
    {
        // Predict crossing point and evaluate, this only goes forwards
        if (method == 0) 
        {
            // Get previous results to make prediction
            int lastResult = HTIR->ArraySize()-1;            
            double CLsObs = HTIR->GetYValue(lastResult);
            double poi_val = HTIR->GetXValue(lastResult);
            double lastCLsObs = HTIR->GetYValue(lastResult - 1);
            double last_poi_val = HTIR->GetXValue(lastResult - 1);

            // Get expected CLs
            double q[7];
            hf::Util::getExpectedCLsFromHypoTest(HTIR, lastResult, q);            
            //double CLsExp = q[2]; // technically not needed since we require down to cross
            //double CLsExpUp = q[1]; // technically not needed since we require down to cross
            double CLsExpDw = q[3];

            hf::Util::getExpectedCLsFromHypoTest(HTIR, lastResult-1, q);
            //double CLsExp_Last = q[2];
            //double CLsExpUp_Last = q[1];
            double CLsExpDw_Last = q[3];            

            // debug
            //bool resultIsAsymptotic = ( !HTIR->GetNullTestStatDist(0) && !HTIR->GetAltTestStatDist  (0) );
            //std::cout<<"Toys="<<!resultIsAsymptotic << " CLsObs = " << CLsObs << " CLsExp = "<<CLsExp<< " CLsExpUp = "<<CLsExpUp<< " CLsExpDw = "<<CLsExpDw<< " CLsExp_Last = "<<CLsExp_Last << " CLsExpUp_Last = "<<CLsExpUp_Last << " CLsExpDw_Last = "<<CLsExpDw_Last<<   std::endl;

            
            if (CLsObs > CLs_threshold)            
            {
                // linear extrapolation from last point.  here is where something fancier could be done
                double m = (lastCLsObs - CLsObs) / (last_poi_val - poi_val);
                double b = CLsObs - m*poi_val;
                nextPoint = (CLs_threshold - b) / m;

                test_pois.push_back(nextPoint*overshoot_fraction);
                return nextTestPOI(test_pois, HTIR, 0);
            }
            else if (CLsExpDw > CLs_threshold)
            {
                // linear extrapolation from last point.  here is where something fancier could be done
                double m = (CLsExpDw_Last - CLsExpDw) / (last_poi_val - poi_val);
                double b = CLsExpDw - m*poi_val;
                nextPoint = (CLs_threshold - b) / m;

                test_pois.push_back(nextPoint*overshoot_fraction);
                return nextTestPOI(test_pois, HTIR, 0);
            }
            else 
            {   
                return -1;
            }

        } // end method 0

        // Check if points we've evaluated are close to crossings, if not predict new points and test those
        if (method == 1)
        {

            // Should have already run a few points
            if (HTIR->ArraySize() < 2)
            {
                StatToolsLogger << kERROR << "Not enough points evaluated already to compute UL" << GEndl;
                return -1;
            }
            

            // Tested POI values
            std::vector<double> tested_POIs;
            int nAboveCLsThreshold = 0;
            int nAboveCLsExpUpThreshold = 0;

            for (int i = 0; i < HTIR->ArraySize(); i++) 
            {
                //std::cout<<"tested POIs = " << HTIR->GetXValue(i)<<std::endl;
                tested_POIs.push_back(HTIR->GetXValue(i) );

                // Get expected CLs
                double q[7];
                hf::Util::getExpectedCLsFromHypoTest(HTIR, i, q);            
                //double CLsExp = q[2];
                double CLsExpUp = q[1];
                //double CLsExpDw = q[3];

                if (HTIR->GetYValue(i) > CLs_threshold) nAboveCLsThreshold++;
                if (CLsExpUp > CLs_threshold) nAboveCLsExpUpThreshold++;                
            }

            // If the first POI test (0) is the only one above the CLs threshold, it's probably not a good limit, try halfway
            if (nAboveCLsThreshold == 1)
            {
                std::sort(tested_POIs.begin(), tested_POIs.end());
                std::vector<double> valuesToTest = {tested_POIs[1] / 2}; // this is the closest point to 0
                return nextTestPOI(valuesToTest, HTIR, 1);
            } else if (nAboveCLsExpUpThreshold == 1 )
            {
                std::sort(tested_POIs.begin(), tested_POIs.end());
                std::vector<double> valuesToTest = {tested_POIs[1] / 2}; // this is the closest point to 0
                return nextTestPOI(valuesToTest, HTIR, 1);
            }

            // Current UL estimate
            double UL_obs = HTIR->UpperLimit();
            double UL_exp = HTIR->GetExpectedUpperLimit(0);
            double UL_exp_1sig_up = HTIR->GetExpectedUpperLimit(1);
            double UL_exp_1sig_dw =  HTIR->GetExpectedUpperLimit(-1);

            // Check how close we were and run another test if not close enough
            std::vector<double> valuesToTest = {UL_obs, UL_exp, UL_exp_1sig_up, UL_exp_1sig_dw};
            for (auto &test : tested_POIs)
            { // cls_threshold should be the poi error thresd.. JDL todo
                if (fabs( test - UL_obs ) / UL_obs < CLs_threshold) valuesToTest.erase(std::remove(valuesToTest.begin(), valuesToTest.end(), UL_obs), valuesToTest.end());

                if (fabs( test - UL_exp ) / UL_exp < CLs_threshold) valuesToTest.erase(std::remove(valuesToTest.begin(), valuesToTest.end(), UL_exp), valuesToTest.end());

                if (fabs( test - UL_exp_1sig_up ) / UL_exp_1sig_up < CLs_threshold) valuesToTest.erase(std::remove(valuesToTest.begin(), valuesToTest.end(), UL_exp_1sig_up), valuesToTest.end());

                //std::cout<< "down diff " << ((fabs( test - UL_exp_1sig_dw ) / UL_exp_1sig_dw) < CLs_threshold) <<std::endl;

                if (fabs( test - UL_exp_1sig_dw ) / UL_exp_1sig_dw < CLs_threshold) 
                {
                    valuesToTest.erase(std::remove(valuesToTest.begin(), valuesToTest.end(), UL_exp_1sig_dw), valuesToTest.end());
                }

            }

            // debug 
            //std::cout<<"method 1 values " << " UL_obs "<<UL_obs << " UL_exp " << UL_exp << " UL_exp_1sig_up " << UL_exp_1sig_up << " UL_exp_1sig_dw " << UL_exp_1sig_dw<<std::endl;
            //for (auto &i: valuesToTest) std::cout<<" values to test " <<i <<std::endl;

            if (valuesToTest.size() > 0) return nextTestPOI(valuesToTest, HTIR, 1);           
        }

    }
    
    return -1;
}

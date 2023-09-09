// vim: ts=4:sw=4
#ifndef HF_STATTOOLS_H
#define HF_STATTOOLS_H

// STL include(s)
#include <iostream>
#include <vector>

// ROOT include(s)
#include "TString.h"

// HistFitter include(s)
#include "LimitResult.h"

class TMap;
class TTree;

class RooAbsReal;
class RooFitResult;
class RooDataSet;
class RooWorkspace;
class RooRealVar;
class RooAbsPdf;
class RooAbsData;
class RooSimultaneous;
class RooCategory;
class RooPlot;
class RooFitResult;
class RooMCStudy;
class RooDataSet;

namespace RooStats {
    class HypoTestResult;
    class HypoTestInverterResult;
    class ModelConfig;
}


namespace RooStats
{
    TTree* toyMC_gen_fit( RooWorkspace* w, const int& nexp, const double& muVal=-1.0, const bool& doDataFitFirst=true,
            const bool& storetoys=false, const TString& toyoutfile="toyResults.root" );
    TTree* ConvertMCStudyResults( RooMCStudy* mcstudy );

    RooStats::HypoTestInverterResult* DoHypoTestInversion( RooWorkspace* w,
                int ntoys=1000,
                int calculatorType = 0,
                int testStatType = 3,
                bool useCLs = true ,
                int npoints = 1,
                double poimin = 1.0,
                double poimax = 1.0,
                bool doAnalyze = false,
                bool useNumberCounting = false,
                const char * modelSBName = "ModelConfig",
                const char * modelBName = "",
                const char * dataName = "obsData",
                const char * nuisPriorName = 0,
                bool generateAsimovDataForObserved = false,
                int nCPUs = 1
                ) ;

    RooStats::HypoTestInverterResult* DoHypoTestInversionAutoScan( RooWorkspace* w,
                int ntoys=1000,
                int calculatorType = 0,
                int testStatType = 3, 
                bool useCLs = true ,  
                int npoints = 1,   
                double poimin = 1.0,
                double poimax = 1.0,
                bool doAnalyze = false,
                bool useNumberCounting = false,
                const char * modelSBName = "ModelConfig",
                const char * modelBName = "",
                const char * dataName = "obsData",                 
                const char * nuisPriorName = 0,
                bool generateAsimovDataForObserved = false,
                int nCPUs = 1,
                std::vector<double> hints = {});


    RooStats::HypoTestResult* DoHypoTest(RooWorkspace* w,
                bool doUL = true, // true = exclusion, false = discovery
                int ntoys=1000,
                int calculatorType = 0,
                int testStatType = 3,
                const char * modelSBName = "ModelConfig",
                const char * modelBName = "",
                const char * dataName = "obsData",
                bool useNumberCounting = false,
                const char * nuisPriorName = 0) ;

    double get_Presult( RooWorkspace* w,
                bool doUL = true, // true = exclusion, false = discovery
                int ntoys=1000,
                int calculatorType = 0,
                int testStatType = 3,
                const char * modelSBName = "ModelConfig",
                const char * modelBName = "",
                const char * dataName = "obsData",
                bool useCLs = true ,
                bool useNumberCounting = false,
                const char * nuisPriorName = 0) ;

    RooStats::HypoTestResult* get_htr( RooWorkspace* w,
                bool doUL = true, // true = exclusion, false = discovery
                int ntoys=1000,
                int calculatorType = 0,
                int testStatType = 3,
                const char * modelSBName = "ModelConfig",
                const char * modelBName = "",
                const char * dataName = "obsData",
                bool useCLs = true ,
                bool useNumberCounting = false,
                const char * nuisPriorName = 0) ;

    hf::LimitResult get_Pvalue(     RooWorkspace* w,
                bool doUL = true, // true = exclusion, false = discovery
                int ntoys = 1000,
                int calculatorType = 0,
                int testStatType = 3,
                const char * modelSBName = "ModelConfig",
                const char * modelBName = "",
                const char * dataName = "obsData",
                bool useCLs = true ,
                bool useNumberCounting = false,
                const char * nuisPriorName = 0) ;

    void AnalyzeHypoTestInverterResult(const char* infile,
            const char* resultName,
            int calculatorType,
            int testStatType ,
            bool useCLs ,
            int npoints,
            const char* outfilePrefix = "",
            const char* plotType = ".pdf"
            ) ;

    void AnalyzeHypoTestInverterResult(RooStats::HypoTestInverterResult* result,
            int calculatorType,
            int testStatType ,
            bool useCLs ,
            int npoints,
            const char* outfilePrefix = "",
            const char* plotType = ".pdf"
            ) ;

    RooStats::HypoTestInverterResult* MakeUpperLimitPlot(const char* fileprefix,
                RooWorkspace* w,
                int calculatorType = 0,
                int testStatType = 3,
                int ntoys=1000,
                bool useCLs = true ,
                int npoints = 20 ) ;

    hf::LimitResult get_Pvalue( const RooStats::HypoTestInverterResult* fResults, bool doUL=true );
    hf::LimitResult get_Pvalue( const RooStats::HypoTestResult* fResult, bool doUL=true );
    
    double nextTestPOI(std::vector<double> &test_pois, HypoTestInverterResult *HTIR, int method=0);

}  // end namespace RooStats

# endif  //HF_STATTOOLS_H

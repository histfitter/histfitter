// vim: ts=4:sw=4
#ifndef StatTools_hh
#define StatTools_hh

#include "TString.h"
#include <iostream>
#include <vector>
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
                int nCPUs = 1
                ) ;

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

    LimitResult get_Pvalue(     RooWorkspace* w,
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

    LimitResult get_Pvalue( const RooStats::HypoTestInverterResult* fResults, bool doUL=true );
    LimitResult get_Pvalue( const RooStats::HypoTestResult* fResult, bool doUL=true );
}

# endif

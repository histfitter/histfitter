// vim: ts=4:sw=4
/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Class  : ConfigMgr                                                             *
 * Created: December 2011                                                         *
 *                                                                                *
 * Description:                                                                   *
 * Simple C++ mirror of the python configManager.                                 *
 * Note that ConfigMgr is a singleton (like its python counter-part).             * 
 * Currently assumes uniform fit configuration for all TopLevelXMLs .             *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/

#ifndef CONFIGMGR_H
#define CONFIGMGR_H

#include <iostream>
#include <vector>
#include <string>
#include "TString.h"

#include "FitConfig.h"

//Root/RooFit/RooStats includes
#include "RooStats/HypoTestInverterResult.h"

class RooWorkspace;

class ConfigMgr {
    private:
        ConfigMgr();
        ~ConfigMgr(){}

    public:
        static ConfigMgr *getInstance () {
            if (NULL == _singleton){ _singleton =  new ConfigMgr; }
            return _singleton;
        }

        //Using this method is not recommended. Do it only if you really know what you are doing.
        static void _delete() {
            if (NULL != _singleton) {
                delete _singleton;
                _singleton = NULL;
            }
            return;
        }

        void initialize();

        void fitAll();
        void doHypoTestAll(TString outdir="results/", Bool_t doUL=true);
        void doUpperLimitAll();
        void runToysAll();

        void fit(int i);
        void fit(FitConfig* fc);
        void doHypoTest(int i, TString outdir="results/", double nsigma=0., Bool_t doUL=true);
        void doHypoTest(FitConfig* fc, TString outdir="results/", double nsigma=0., Bool_t doUL=true);
        void doUpperLimit(int i);
        void doUpperLimit(FitConfig* fc);
        void runToys(int i);
        void runToys(FitConfig* fc);
        
        //functions to allow the rescan for -l
        double min_CLs(RooStats::HypoTestInverterResult* hypo);
        double max_CLs(RooStats::HypoTestInverterResult* hypo);
        RooStats::HypoTestInverterResult* RedoScan(RooWorkspace* w, RooStats::HypoTestInverterResult* hypo);

        void finalize();
        Bool_t checkConsistency();

        FitConfig* addFitConfig(const TString& name);
        FitConfig* getFitConfig(const TString& name);

        TString makeCorrectedBkgModelConfig(RooWorkspace* w, const char* modelSBName="ModelConfig");

        //get/set methods
        void setNToys (const int& val) { m_nToys = val; }
        int  getNToys() { return m_nToys; }

        void setCalcType(const int& type) { m_calcType = type; }
        int  getCalcType() { return m_calcType; }

        void setTestStatType(const int& type) { m_testStatType = type; }
        int  getTestStatType() { return m_testStatType; }

        void setCLs(const bool& cls=true) { m_useCLs=cls; }
        bool getCLs() { return m_useCLs; }
        
        void setScanRange(const bool useScanRange, const float min=-1, const float max=-1) { m_useScanRange=useScanRange; m_scanRangeMin=min; m_scanRangeMax=max; }

        void setfixSigXSec(const bool& fix=true) { m_fixSigXSec = fix; }
        bool getfixSigXSec() { return m_fixSigXSec; }

        void setRunOnlyNominalXSec(const bool& fix=true) { m_runOnlyNominalXSec = fix; }
        bool getRunOnlyNominalXSec() { return m_runOnlyNominalXSec; }
        
        void setExclusion(const bool& cls=true) { m_doUL=cls; }
        bool getExclusion() { return m_doUL; }

        void setNPoints(const int& type) { m_nPoints = type; }
        int  getNPoints() { return m_nPoints; }

        void setSeed(const int& seed=0) { m_seed = seed; }
        int  getSeed() { return m_seed; }

        void setMuValGen(const double& val) { m_muValGen = val; }
        double getMuValGen() { return m_muValGen; }

        void setUseAsimovSet(const bool& useAsimov=false) { m_useAsimovSet=useAsimov; }
        bool getUseAsimovSet() { return m_useAsimovSet; }

        void SetBkgCorrVal(const double& val) { m_bkgCorrValVec.clear(); m_bkgCorrValVec.push_back(val); }
        void SetBkgParName(const char* par)   { m_bkgParNameVec.clear(); m_bkgParNameVec.push_back(par); }
        void SetBkgChlName(const char* par)   { m_chnNameVec.clear();    m_chnNameVec.push_back(par); }

        void AddBkgCorrVal(const double& val) { m_bkgCorrValVec.push_back(val); }
        void AddBkgParName(const char* par)   { m_bkgParNameVec.push_back(par); }
        void AddBkgChlName(const char* par)   { m_chnNameVec.push_back(par); }

        //void setLogLevel( TMsgLevel minLevel) { m_logger.SetMinLevel(minLevel); m_logger << minLevel << "log level set to " << m_logger.GetMinLevelStr() << GEndl; }
        //const std::map<TMsgLevel, std::string> getLogLevels() const { 
            //std::map<TMsgLevel, std::string> myMap(m_logger.GetLevelMap());
            //return myMap;
        //}

        //void writeLogMessage( TMsgLevel level, std::string message) { m_logger << level << message << GEndl; } //for python
    
        //class data members
    public:
        //Lazy... Why bother adding trivial get/set methods for all these guys?
        bool m_saveTree;
        bool m_doHypoTest;

        TString m_status;
        TString m_outputFileName;
        std::vector<FitConfig*> m_fitConfigs;
        int  m_seed;
        bool m_useAsimovSet;  
	std::string m_plotRatio;

    private:
        TMsgLogger m_logger;

        int  m_nToys;
        int  m_calcType;
        int  m_testStatType;
        bool m_useCLs;
        bool m_useScanRange;
        float m_scanRangeMin;
        float m_scanRangeMax; 
        bool m_fixSigXSec;
        bool m_runOnlyNominalXSec;
        bool m_doUL;
        int  m_nPoints;
        double m_muValGen;
        bool m_removeEmptyBins;
	
        std::vector<std::string> m_chnNameVec; 
        std::vector<std::string> m_bkgParNameVec;
        std::vector<double> m_bkgCorrValVec;

        static ConfigMgr *_singleton;
};

#endif

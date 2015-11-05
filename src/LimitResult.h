// vim: ts=4:sw=4
/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Class  : TEasyFormula                                                          *
 *                                                                                *
 * Description:                                                                   *
 *      Simple class for storing results from a hypothesis test.                  *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/

#ifndef LimitResult_hh
#define LimitResult_hh

#include <iostream>
#include <map>
#include "json.h"
#include "TString.h"

class LimitResult {
    private:
        double m_p0;
        double m_p1;
        double m_CLs;
        double m_CLsexp;
        int m_nexp;
        double m_sigma0;
        double m_sigma1;
        int m_mode;
        UInt_t m_seed;
        int m_fID;
        double m_CLsu1S;
        double m_CLsd1S;
        double m_CLsu2S;
        double m_CLsd2S;
        double m_upperLimit;
        double m_upperLimitEstimatedError;
        double m_expectedUpperLimit;
        double m_expectedUpperLimitPlus1Sig;
        double m_expectedUpperLimitPlus2Sig;
        double m_expectedUpperLimitMinus1Sig;
        double m_expectedUpperLimitMinus2Sig;

        double m_p0exp;
        double m_p0u1S;
        double m_p0d1S;
        double m_p0u2S;
        double m_p0d2S;

        std::string m_resultfilename;
        std::string m_comments;
        std::map<std::string,float> m_metadata;

    public:
        LimitResult(const std::string &name = std::string(""), const std::string &title = std::string(""));

        virtual ~LimitResult();

        double GetP0() const 				{ return m_p0; }; // p value at signal = 0
        double GetP0exp() const 			{ return m_p0exp; }; //
        double GetP0u1S() const 			{ return m_p0u1S; }; // 1 sigma upper and lower 
        double GetP0d1S() const 			{ return m_p0d1S; }; // from toys               
        double GetP0u2S() const                         { return m_p0u2S; }; // 1 sigma upper and lower 
        double GetP0d2S() const                         { return m_p0d2S; }; // from toys               

        double GetP1() const 				{ return m_p1; }; // p value at signal = 1

        double GetCLs() const 			{ return m_CLs; }; // 
        double GetCLsexp() const 			{ return m_CLsexp; }; //
        double GetCLsu1S() const 			{ return m_CLsu1S; }; // 1 sigma upper and lower 
        double GetCLsd1S() const 			{ return m_CLsd1S; }; // from toys               
        double GetCLsu2S() const                       { return m_CLsu2S; }; // 1 sigma upper and lower 
        double GetCLsd2S() const                       { return m_CLsd2S; }; // from toys               

        double GetSigma0() const                      { return m_sigma0; }
        double GetSigma1() const                      { return m_sigma1; }
        int    GetNExp() const 			{ return m_nexp; }
        int    GetMode() const 			{ return m_mode; }

        UInt_t GetSeed() const 			{ return m_seed; }
        int    GetfID() const 			{ return m_fID; }
        const std::map<std::string, float>& GetMetaData()  { return m_metadata; }

        double GetUpperLimit() const                      { return m_upperLimit; }
        double GetUpperLimitEstimatedError() const        { return m_upperLimitEstimatedError; }
        double GetExpectedUpperLimit() const              { return m_expectedUpperLimit; }
        double GetExpectedUpperLimitPlus1Sig() const              { return m_expectedUpperLimitPlus1Sig; }
        double GetExpectedUpperLimitPlus2Sig() const              { return m_expectedUpperLimitPlus2Sig; }
        double GetExpectedUpperLimitMinus1Sig() const              { return m_expectedUpperLimitMinus1Sig; }
        double GetExpectedUpperLimitMinus2Sig() const              { return m_expectedUpperLimitMinus2Sig; }


        void SetP0(double val)		{ m_p0 = val; }; // 
        void SetP0exp(double val)	{ m_p0exp = val; }; // 
        void SetP0u1S(double val)	{ m_p0u1S= val; }; // 1 sigma upper and lower 
        void SetP0d1S(double val)	{ m_p0d1S= val; }; // from toys                  
        void SetP0u2S(double val)        { m_p0u2S= val; }; // 1 sigma upper and lower 
        void SetP0d2S(double val)        { m_p0d2S= val; }; // from toys        

        void SetP1(double val)		{ m_p1 = val; }; // 

        void SetCLs(double val)		{ m_CLs = val; }; // 
        void SetCLsexp(double val)		{ m_CLsexp = val; }; // 
        void SetCLsu1S(double val)		{ m_CLsu1S= val; }; // 1 sigma upper and lower 
        void SetCLsd1S(double val)		{ m_CLsd1S= val; }; // from toys                  
        void SetCLsu2S(double val)             { m_CLsu2S= val; }; // 1 sigma upper and lower 
        void SetCLsd2S(double val)             { m_CLsd2S= val; }; // from toys        

        void SetSigma0(const double& sigma)           { m_sigma0=sigma; };
        void SetSigma1(const double& sigma)           { m_sigma1=sigma; };
        void SetNExp(const int& nexp) 		{ m_nexp=nexp; }
        void SetMode(const int& mode) 		{ m_mode=mode; }

        void SetSeed(const UInt_t& seed) 		{ m_seed=seed; }
        void SetfID(const int fID) 			{ m_fID=fID; }

        void SetUpperLimit(double val)                      { m_upperLimit = val; }
        void SetUpperLimitEstimatedError(double val)        { m_upperLimitEstimatedError = val; }
        void SetExpectedUpperLimit(double val)              { m_expectedUpperLimit = val; }
        void SetExpectedUpperLimitPlus1Sig(double val)      { m_expectedUpperLimitPlus1Sig = val; }
        void SetExpectedUpperLimitPlus2Sig(double val)      { m_expectedUpperLimitPlus2Sig = val; }
        void SetExpectedUpperLimitMinus1Sig(double val)     { m_expectedUpperLimitMinus1Sig = val; }
        void SetExpectedUpperLimitMinus2Sig(double val)     { m_expectedUpperLimitMinus2Sig = val; }

        void SetMetaData(const std::map<std::string,float>& metadata) { m_metadata=metadata; }

        // filename of saved file
        std::string GetResultFilename() const 		{ return m_resultfilename; }
        // comment string
        std::string GetComments() const 			{ return m_comments; }   
        // filename of saved file
        void SetResultFilename(const std::string & val)   { m_resultfilename = val; }
        // comment string
        void SetComments(const std::string & val) 	{ m_comments = val; }   

        void Summary();
        std::vector<std::string> GetKeys() const;
        std::map<std::string, float> GetData() const;
        JSON GetJSONData() const; 
        std::string GetSummaryString() const; 
        std::string GetDescriptionString() const;
        void AddMetaData(const std::map<std::string,float>& metadata); 
        void AddMetaData(const std::string&, float);
};

#endif

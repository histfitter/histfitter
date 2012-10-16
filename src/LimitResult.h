// vim: ts=4:sw=4
#ifndef LimitResult_hh
#define LimitResult_hh

// Simple class for holding results from a fit 

#include <iostream>
#include <map>
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


        TString m_resultfilename;
        TString m_comments;
        std::map<TString,float> m_metadata;
    public:
        LimitResult(const TString &name=TString(""), const TString &title=TString(""));

        virtual ~LimitResult();

        inline double GetP0() const 				{ return m_p0; }; // p value at signal = 0
        inline double GetP1() const 				{ return m_p1; }; // p value at signal = 1

        inline double GetCLs() const 			{ return m_CLs; }; // 
        inline double GetCLsexp() const 			{ return m_CLsexp; }; //
        inline double GetCLsu1S() const 			{ return m_CLsu1S; }; // 1 sigma upper and lower 
        inline double GetCLsd1S() const 			{ return m_CLsd1S; }; // from toys               
        inline double GetCLsu2S() const                       { return m_CLsu2S; }; // 1 sigma upper and lower 
        inline double GetCLsd2S() const                       { return m_CLsd2S; }; // from toys               

        inline double GetSigma0() const                      { return m_sigma0; }
        inline double GetSigma1() const                      { return m_sigma1; }
        inline int    GetNExp() const 			{ return m_nexp; }
        inline int    GetMode() const 			{ return m_mode; }

        inline UInt_t GetSeed() const 			{ return m_seed; }
        inline int    GetfID() const 			{ return m_fID; }
        inline const std::map<TString,float>& GetMetaData()  { return m_metadata; }

        inline double GetUpperLimit() const                      { return m_upperLimit; }
        inline double GetUpperLimitEstimatedError() const        { return m_upperLimitEstimatedError; }
        inline double GetExpectedUpperLimit() const              { return m_expectedUpperLimit; }
        inline double GetExpectedUpperLimitPlus1Sig() const              { return m_expectedUpperLimitPlus1Sig; }
        inline double GetExpectedUpperLimitPlus2Sig() const              { return m_expectedUpperLimitPlus2Sig; }
        inline double GetExpectedUpperLimitMinus1Sig() const              { return m_expectedUpperLimitMinus1Sig; }
        inline double GetExpectedUpperLimitMinus2Sig() const              { return m_expectedUpperLimitMinus2Sig; }


        inline void SetP0(const double & val)		{ m_p0 = val; }; // 
        inline void SetP1(const double & val)		{ m_p1 = val; }; // 

        inline void SetCLs(const double & val)		{ m_CLs = val; }; // 
        inline void SetCLsexp(const double & val)		{ m_CLsexp = val; }; // 
        inline void SetCLsu1S(const double & val)		{ m_CLsu1S= val; }; // 1 sigma upper and lower 
        inline void SetCLsd1S(const double & val)		{ m_CLsd1S= val; }; // from toys                  
        inline void SetCLsu2S(const double & val)             { m_CLsu2S= val; }; // 1 sigma upper and lower 
        inline void SetCLsd2S(const double & val)             { m_CLsd2S= val; }; // from toys        

        inline void SetSigma0(const double& sigma)           { m_sigma0=sigma; };
        inline void SetSigma1(const double& sigma)           { m_sigma1=sigma; };
        inline void SetNExp(const int& nexp) 		{ m_nexp=nexp; }
        inline void SetMode(const int& mode) 		{ m_mode=mode; }

        inline void SetSeed(const UInt_t& seed) 		{ m_seed=seed; }
        inline void SetfID(const int& fID) 			{ m_fID=fID; }

        inline void SetUpperLimit(const double & val)                      { m_upperLimit = val; }
        inline void SetUpperLimitEstimatedError(const double & val)        { m_upperLimitEstimatedError = val; }
        inline void SetExpectedUpperLimit(const double & val)              { m_expectedUpperLimit = val; }
        inline void SetExpectedUpperLimitPlus1Sig(const double & val)      { m_expectedUpperLimitPlus1Sig = val; }
        inline void SetExpectedUpperLimitPlus2Sig(const double & val)      { m_expectedUpperLimitPlus2Sig = val; }
        inline void SetExpectedUpperLimitMinus1Sig(const double & val)     { m_expectedUpperLimitMinus1Sig = val; }
        inline void SetExpectedUpperLimitMinus2Sig(const double & val)     { m_expectedUpperLimitMinus2Sig = val; }

        inline void SetMetaData(const std::map<TString,float>& metadata) { m_metadata=metadata; }

        // filename of saved file
        inline TString GetResultFilename() const 		{ return m_resultfilename; }
        // comment string
        inline TString GetComments() const 			{ return m_comments; }   
        // filename of saved file
        inline void SetResultFilename(const TString & val)   { m_resultfilename = val; }
        // comment string
        inline void SetComments(const TString & val) 	{ m_comments = val; }   

        void Summary();
        TString GetSummaryString() const; 
        TString GetDescriptionString() const;
        void AddMetaData(const std::map<TString,float>& metadata); 
};


#endif

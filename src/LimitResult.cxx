// vim: ts=4:sw=4
/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Class  : LimitResult                                                           *
 *                                                                                *
 * Description:                                                                   *
 *      Implementation (see header for description)                               *
 *                                                                                *
 * See corresponding .h file for author and license information                   *         
 *                                                                                *
 **********************************************************************************/

#include <iostream>
#include <sstream>
#include <iomanip>

#include "LimitResult.h"
#include "Significance.h"

template <typename T> std::string to_string_scientific(const T& t) { 
   std::ostringstream os; 
   os << std::scientific << std::setprecision(6) << t; 
   return os.str(); 
} 

//_____________________________________________________________________________
LimitResult::~LimitResult()
{
}


//_____________________________________________________________________________
LimitResult::LimitResult(const TString &name, const TString &title) :
    m_p0(-1),
    m_p1(-1),
    m_CLs(-1),
    m_CLsexp(-1),
    m_nexp(-1),
    m_sigma0(-1),
    m_sigma1(-1),
    m_mode(-1),
    m_seed(0),
    m_fID(-1),
    m_CLsu1S(-1),
    m_CLsd1S(-1),
    m_CLsu2S(-1),
    m_CLsd2S(-1),
    m_upperLimit(-1),
    m_upperLimitEstimatedError(-1),
    m_expectedUpperLimit(-1),
    m_expectedUpperLimitPlus1Sig(-1),
    m_expectedUpperLimitPlus2Sig(-1),
    m_expectedUpperLimitMinus1Sig(-1),
    m_expectedUpperLimitMinus2Sig(-1),
    m_p0exp(-1),
    m_p0u1S(-1),
    m_p0d1S(-1),
    m_p0u2S(-1),
    m_p0d2S(-1),
    m_resultfilename(""),
    m_comments("") {
    // dummy code: allow unused variable
    TString tmp=title; 
    tmp=name;
};


//_____________________________________________________________________________
void LimitResult::Summary() {
    std::cout << " Printing data for object: " << this << std::endl ;
    std::cout << " | p0:               "<<    GetP0() << "      sigma: " << StatTools::GetSigma(   GetP0())<<std::endl ;
    std::cout << " | p1:               "<<    GetP1() << "      sigma: " << StatTools::GetSigma(   GetP1())<<std::endl ;

    std::cout << " | CLs:               "<<    GetCLs() << "      sigma: " << StatTools::GetSigma(   GetCLs())<<std::endl ;
    std::cout << " | CLsexp:            "<<    GetCLsexp() << "      sigma: " << StatTools::GetSigma(   GetCLsexp())<<std::endl ;
    std::cout << " | CLsu1S (+1s)       "<< GetCLsu1S() << "      sigma: " << StatTools::GetSigma(GetCLsu1S())<<std::endl ;
    std::cout << " | CLsd1S (-1s)       "<< GetCLsd1S() << "      sigma: " << StatTools::GetSigma(GetCLsd1S())<<std::endl ;
    std::cout << " | CLsu2S (+2s)       "<< GetCLsu2S() << "      sigma: " << StatTools::GetSigma(GetCLsu2S())<<std::endl ;
    std::cout << " | CLsd2S (-2s)       "<< GetCLsd2S() << "      sigma: " << StatTools::GetSigma(GetCLsd2S())<<std::endl ;

    std::cout << " | Sigma0:   "<<       GetSigma0() << std::endl;
    std::cout << " | Sigma1:   "<<       GetSigma1() << std::endl;

    std::cout << " | NExp:     "<<         GetNExp() << std::endl;          
    std::cout << " | Mode:     "<<         GetMode() << std::endl;          
    std::cout << " | Seed:     "<<         GetSeed() << std::endl;  
    std::cout << " | fID:      "<<         GetfID() << std::endl;  

    std::cout << " | Upper Limit:  " << GetUpperLimit() << " +/- " << GetUpperLimitEstimatedError() << std::endl;
    std::cout << " | Expected Upper Limit:           " << GetExpectedUpperLimit()  << std::endl;
    std::cout << " | Expected Upper Limit (+1 sig):  " << GetExpectedUpperLimitPlus1Sig()  << std::endl;
    std::cout << " | Expected Upper Limit (+2 sig):  " << GetExpectedUpperLimitPlus2Sig()  << std::endl;
    std::cout << " | Expected Upper Limit (-1 sig):  " << GetExpectedUpperLimitMinus1Sig()  << std::endl;
    std::cout << " | Expected Upper Limit (-2 sig):  " << GetExpectedUpperLimitMinus2Sig()  << std::endl;

    std::cout << " | p0 value:                    " << GetP0()     << std::endl;
    std::cout << " | Expected p0 value:           " << GetP0exp() << std::endl;
    std::cout << " | Expected p0 value (+1 sig):  " << GetP0u1S() << std::endl;
    std::cout << " | Expected p0 value (+2 sig):  " << GetP0d1S() << std::endl;
    std::cout << " | Expected p0 value (-1 sig):  " << GetP0u2S() << std::endl;
    std::cout << " | Expected p0 value (-2 sig):  " << GetP0d2S() << std::endl;

    std::cout << " | results stored in: " <<GetResultFilename() << std::endl ;
    std::cout << " | Comments: "<<     GetComments() << std::endl;
}


//_____________________________________________________________________________
TString  LimitResult::GetSummaryString() const {
    TString summary;
    summary += Form(" %e %e %e",GetP0(),GetP1(),GetCLs());
    summary += Form(" %d %d",GetMode(),GetNExp());
    summary += Form(" %u",GetSeed());
    summary += Form(" %e",GetCLsexp());
    summary += Form(" %d %e %e",GetfID(),GetSigma0(),GetSigma1());
    // CLs bands:
    summary += Form(" %e %e %e %e",GetCLsu1S(),GetCLsd1S(),GetCLsu2S(),GetCLsd2S());
    // p0 bands:
    summary += Form(" %e %e %e %e %e",GetP0exp(),GetP0u1S(),GetP0d1S(),GetP0u2S(),GetP0d2S());
    // upper limits:
    summary += Form(" %e %e %e %e %e %e %e -999007. -999007.",GetUpperLimit(),
		    GetUpperLimitEstimatedError(),GetExpectedUpperLimit(),GetExpectedUpperLimitPlus1Sig(),
		    GetExpectedUpperLimitPlus2Sig(),GetExpectedUpperLimitMinus1Sig(),GetExpectedUpperLimitMinus2Sig());

    std::map<TString,float>::const_iterator itr=m_metadata.begin(), end=m_metadata.end();
    for (; itr!=end; ++itr) { summary += Form(" %f",itr->second); }
    return summary;
}

JSON LimitResult::GetJSONData() const {
    JSON summary = JSON::Object();
    
    summary["p0"] = GetP0(); 
    summary["p1"] = GetP1();
    summary["CLs"] = GetCLs();

    summary["mode"] = GetMode();
    summary["nexp"] = GetNExp();
    summary["seed"] = GetSeed();
    
    summary["CLsexp"] = GetCLsexp();
    summary["fID"] = GetfID();
    summary["sigma0"] = GetSigma0();
    summary["sigma1"] = GetSigma1();
    
    summary["clsu1s"] = GetCLsu1S(); 
    summary["clsd1s"] = GetCLsd1S(); 
    summary["clsu2s"] = GetCLsu2S(); 
    summary["clsd2s"] = GetCLsd2S(); 
    
    summary["p0exp"] = GetP0exp();
    summary["p0u1s"] = GetP0u1S();
    summary["p0d1s"] = GetP0d1S();
    summary["p0u2s"] = GetP0u2S();
    summary["p0d2s"] = GetP0d2S();
    
    summary["upperLimit"] = GetUpperLimit();
    summary["upperLimitEstimatedError"] = GetUpperLimitEstimatedError();
    summary["expectedUpperLimit"] = GetExpectedUpperLimit();
    summary["expectedUpperLimitPlus1Sig"] = GetExpectedUpperLimitPlus1Sig(); 
    summary["expectedUpperLimitPlus2Sig"] = GetExpectedUpperLimitPlus2Sig(); 
    summary["expectedUpperLimitMinus1Sig"] = GetExpectedUpperLimitMinus1Sig(); 
    summary["expectedUpperLimitMinus2Sig"] = GetExpectedUpperLimitMinus2Sig(); 
    summary["xsec"] = -999007.;
    summary["excludedXsec"] = -999007.;

    std::map<TString,float>::const_iterator itr=m_metadata.begin(), end=m_metadata.end();
    for (; itr!=end; ++itr)
        summary[itr->first.Data()] = itr->second;
    
    return summary;
}

//_____________________________________________________________________________
TString  LimitResult::GetDescriptionString() const {
    TString description;
    description += "p0:p1:CLs:"; //3
    description += "mode:nexp:";  //2
    description += "seed:";       //1 
    description += "CLsexp:";     //1
    description += "fID:sigma0:sigma1:";   //3
    description += "clsu1s:clsd1s:clsu2s:clsd2s:"; //4
    description += "p0exp:p0u1s:p0d1s:p0u2s:p0d2s:"; //5
    description += "upperLimit:upperLimitEstimatedError:expectedUpperLimit:expectedUpperLimitPlus1Sig:";
    description += "expectedUpperLimitPlus2Sig:expectedUpperLimitMinus1Sig:expectedUpperLimitMinus2Sig:";
    description += "xsec:excludedXsec"; //2

    std::map<TString,float>::const_iterator itr=m_metadata.begin(), end=m_metadata.end();
    for (; itr!=end; ++itr)
        description += Form(":%s",itr->first.Data());
    return description;
}


//_____________________________________________________________________________
void LimitResult::AddMetaData(const std::map<TString,float>& metadata) {
    std::map<TString,float>::const_iterator itr=metadata.begin(), end=metadata.end();
    for (; itr!=end; ++itr) { m_metadata[itr->first]=itr->second; }
}


// vim: ts=4:sw=4
#include "LimitResult.h"
#include "Significance.h"

LimitResult::~LimitResult()
{
}

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
    m_resultfilename(""),
    m_comments("") {
    // dummy code: allow unused variable
    TString tmp=title; 
    tmp=name;
};

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

    std::cout << " | results stored in: " <<GetResultFilename() << std::endl ;
    std::cout << " | Comments: "<<     GetComments() << std::endl;
}


TString  LimitResult::GetSummaryString() const {
    TString summary;
    summary += Form(" %lf %lf %lf",GetP0(),GetP1(),GetCLs());
    summary += Form(" %d %d",GetMode(),GetNExp());
    summary += Form(" %u",GetSeed());
    summary += Form(" %lf",GetCLsexp());
    summary += Form(" %d %lf %lf",GetfID(),GetSigma0(),GetSigma1());
    // CLs bands:
    summary += Form(" %lf %lf %lf %lf",GetCLsu1S(),GetCLsd1S(),GetCLsu2S(),GetCLsd2S());
    // upper limits:
    summary += Form(" %lf %lf %lf %lf %lf %lf %lf -999007. -999007.",GetUpperLimit(),GetUpperLimitEstimatedError(),GetExpectedUpperLimit(),GetExpectedUpperLimitPlus1Sig(),GetExpectedUpperLimitPlus2Sig(),GetExpectedUpperLimitMinus1Sig(),GetExpectedUpperLimitMinus2Sig());

    std::map<TString,float>::const_iterator itr=m_metadata.begin(), end=m_metadata.end();
    for (; itr!=end; ++itr) { summary += Form(" %f",itr->second); }
    return summary;
}

TString  LimitResult::GetDescriptionString() const {
    TString description;
    description += "p0:p1:CLs:"; //3
    description += "mode:nexp:";  //2
    description += "seed:";       //1 
    description += "CLsexp:";     //1
    description += "fID:sigma0:sigma1:";   //3
    description += "clsu1s:clsd1s:clsu2s:clsd2s:"; //4
    description += "upperLimit:upperLimitEstimatedError:expectedUpperLimit:expectedUpperLimitPlus1Sig:expectedUpperLimitPlus2Sig:expectedUpperLimitMinus1Sig:expectedUpperLimitMinus2Sig:xsec:excludedXsec"; //4

    std::map<TString,float>::const_iterator itr=m_metadata.begin(), end=m_metadata.end();
    for (; itr!=end; ++itr)
        description += Form(":%s",itr->first.Data());
    return description;
}

void LimitResult::AddMetaData(const std::map<TString,float>& metadata) {
    std::map<TString,float>::const_iterator itr=metadata.begin(), end=metadata.end();
    for (; itr!=end; ++itr) { m_metadata[itr->first]=itr->second; }
}


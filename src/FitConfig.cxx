// vim: ts=4:sw=4
////////////////////////////////////////////////////////////////////////
// Creation: January 2011, David Cote (CERN)                          //
// Simple C++ mirror of python TopLevelXML objects.                   //
////////////////////////////////////////////////////////////////////////

#include <iostream>
#include "FitConfig.h"
#include "TMsgLogger.h"

using namespace std;

FitConfig::FitConfig(){
}

FitConfig::FitConfig(const TString& name){
    m_Name=name;

    m_dataColor = kBlack;	     
    m_totalPdfColor = kBlue;
    m_errorLineColor = kBlue - 5;
    m_errorLineStyle = 1;    // AK: 1 = kSolid, which somehow does not compile    
    m_errorFillColor = kBlue - 5;
    m_errorFillStyle = 3004;
    m_legend = NULL;
    m_removeEmptyBins = false;   
}

Int_t FitConfig::getSampleColor(const TString& sample){
    for(unsigned int i = 0; i< m_sampleColors.size(); i++){
        if( sample.Contains(m_sampleNames[i].Data())){
            return m_sampleColors[i];
        }
    }
    (*TMsgLogger::getInstance()) << kWARNING << "getSampleColor unknown sample name: "<<sample << GEndl;
    return 0;
}


Float_t FitConfig::getLumi(){
    return m_Lumi;
}


TString FitConfig::getSampleName(const TString& sample){
    for(unsigned int i = 0; i< m_sampleNames.size(); i++){
        if( sample.Contains(m_sampleNames[i].Data())){
            return m_sampleNames[i];
        }
    }
    (*TMsgLogger::getInstance()) << kWARNING << "getSampleName unknown sample name: "<<sample << GEndl;
    return "";
}

void FitConfig::Print(){
    (*TMsgLogger::getInstance()) << kINFO << "*** Fit Config: " << m_Name << " ***" << GEndl;
    (*TMsgLogger::getInstance()) << kINFO << " inputWorkspaceFileName: " << m_inputWorkspaceFileName << GEndl;
    (*TMsgLogger::getInstance()) << kINFO << " signalSampleName: " << m_signalSampleName << GEndl;
    
    (*TMsgLogger::getInstance()) << kINFO << " sampleNames: ";
    for(unsigned int i = 0; i< m_sampleNames.size(); i++){ 
        (*TMsgLogger::getInstance()) << kINFO << m_sampleNames.at(i) << " "; 
    }
    (*TMsgLogger::getInstance()) << kINFO << " sampleColors: ";
    for(unsigned int i = 0; i< m_sampleColors.size(); i++){ 
        (*TMsgLogger::getInstance()) << kINFO << m_sampleColors.at(i) << " "; 
    }
    
    (*TMsgLogger::getInstance()) << kINFO << " signalChannels: ";
    for(unsigned int i = 0; i< m_signalChannels.size(); i++){ 
        (*TMsgLogger::getInstance()) << kINFO << m_signalChannels.at(i) << " "; 
    }
    
    (*TMsgLogger::getInstance()) << kINFO << " validationChannels: ";
    for(unsigned int i = 0; i< m_validationChannels.size(); i++){ 
        (*TMsgLogger::getInstance()) << kINFO << m_validationChannels.at(i) << " "; 
    }
    
    (*TMsgLogger::getInstance()) << kINFO << " bkgConstrainChannels: ";
    for(unsigned int i = 0; i< m_bkgConstrainChannels.size(); i++){ 
        (*TMsgLogger::getInstance()) << kINFO << m_bkgConstrainChannels.at(i) << " ";
    }
    
    return;
}

Double_t FitConfig::getChannelMinY(const TString& channel){
    Int_t idx = -1; 
    Bool_t channelFound = kFALSE;
    findChannel(channel, idx, channelFound); 

    if(channelFound && idx > -1 &&  ((unsigned int)idx) < m_channelsMinY.size()) 
        return m_channelsMinY[idx];
    
    return -9999.;
}

Double_t FitConfig::getChannelMaxY(const TString& channel){
    Int_t idx = -1; 
    Bool_t channelFound = kFALSE;
    findChannel(channel, idx, channelFound); 

    if(channelFound && idx > -1 && ((unsigned int)idx) < m_channelsMaxY.size()) 
        return m_channelsMaxY[idx];
    
    return -999.;
}


Int_t FitConfig::getChannelNBins(const TString& channel){
    Int_t idx = -1; 
    Bool_t channelFound = kFALSE;
    findChannel(channel, idx, channelFound); 

    if(channelFound && idx > -1 && ((unsigned int)idx) < m_channelsNBins.size()) 
        return m_channelsNBins[idx];
    
    return 999;
}


TString FitConfig::getChannelTitleX(const TString& channel){
    Int_t idx = -1; 
    Bool_t channelFound = kFALSE;
    findChannel(channel, idx, channelFound); 

    if(channelFound && idx > -1 && ((unsigned int)idx) < m_channelsTitleX.size()) 
        return m_channelsTitleX[idx];
    
    return "";
}

TString FitConfig::getChannelTitleY(const TString& channel){
    Int_t idx = -1; 
    Bool_t channelFound = kFALSE;
    findChannel(channel, idx, channelFound); 

    if(channelFound && idx > -1 && ((unsigned int)idx) < m_channelsTitleY.size()) 
        return m_channelsTitleY[idx];
    
    return "";
}

Bool_t  FitConfig::getChannelLogY(const TString& channel){
    Int_t idx = -1; 
    Bool_t channelFound = kFALSE;
    findChannel(channel, idx, channelFound); 

    if(channelFound && idx > -1 && ((unsigned int)idx) < m_channelsLogY.size()) 
        return m_channelsLogY[idx];
    
    return kFALSE;
}


Double_t FitConfig::getChannelATLASLabelX(const TString& channel){
    Int_t idx = -1; 
    Bool_t channelFound = kFALSE;
    findChannel(channel, idx, channelFound); 

    if(channelFound && idx > -1 && ((unsigned int)idx) < m_channelsATLASLabelX.size()) 
        return m_channelsATLASLabelX[idx];
    
    return -1.;
}


Double_t FitConfig::getChannelATLASLabelY(const TString& channel){
    Int_t idx = -1; 
    Bool_t channelFound = kFALSE;
    findChannel(channel, idx, channelFound); 

    if(channelFound && idx > -1 && ((unsigned int)idx) < m_channelsATLASLabelY.size()) 
        return m_channelsATLASLabelY[idx];
    
    return -1.;
}


TString FitConfig::getChannelATLASLabelText(const TString& channel){
    Int_t idx = -1; 
    Bool_t channelFound = kFALSE;
    findChannel(channel, idx, channelFound); 

    if(channelFound && idx > -1 && ((unsigned int)idx) < m_channelsATLASLabelText.size()) 
        return m_channelsATLASLabelText[idx];
    
    return "";
}

Bool_t  FitConfig::getChannelShowLumi(const TString& channel){
    Int_t idx = -1; 
    Bool_t channelFound = kFALSE;
    findChannel(channel, idx, channelFound); 

    if(channelFound && idx > -1 && ((unsigned int)idx) < m_channelsShowLumi.size()) 
        return m_channelsShowLumi[idx];
    
    return kFALSE;
}


void FitConfig::findChannel(const TString& channel, Int_t& idx, Bool_t& channelFound) {
    for(unsigned int i=0; i < m_channels.size(); i++){
        if(m_channels[i].EqualTo(channel) && !channelFound){
            idx = i;
            channelFound = kTRUE;
        } else if(m_channels[i].EqualTo(channel) && channelFound){
            (*TMsgLogger::getInstance()) << kWARNING << "FitConfig has found more then one channel with the name = " << channel << " check your code" << GEndl;
            for(unsigned int j=0; j < m_channels.size(); j++){
                (*TMsgLogger::getInstance()) << kINFO << "FitConfig m_channels[" << j << "] = " << m_channels[j] << GEndl;
            }
        }
    }

}

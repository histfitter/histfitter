// vim: ts=4:sw=4
////////////////////////////////////////////////////////////////////////
// Creation: January 2011, David Cote (CERN)                          //
// Simple C++ mirror of python TopLevelXML objects.                   //
////////////////////////////////////////////////////////////////////////

#include <iostream>
#include "FitConfig.h"

using namespace std;

FitConfig::FitConfig() : m_logger("FitConfig"){
}

FitConfig::FitConfig(const TString& name) : m_logger("FitConfig") {
    m_name=name;

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
    m_logger << kWARNING << "getSampleColor unknown sample name: "<<sample << GEndl;
    return 0;
}


Float_t FitConfig::getLumi(){
    return m_lumi;
}


TString FitConfig::getSampleName(const TString& sample){
    for(unsigned int i = 0; i< m_sampleNames.size(); i++){
        if( sample.Contains(m_sampleNames[i].Data())){
            return m_sampleNames[i];
        }
    }
    m_logger << kWARNING << "getSampleName unknown sample name: "<<sample << GEndl;
    return "";
}

void FitConfig::Print(){
    m_logger << kINFO << "*** Fit Config: " << m_name << " ***" << GEndl;
    m_logger << kINFO << " inputWorkspaceFileName: " << m_inputWorkspaceFileName << GEndl;
    m_logger << kINFO << " signalSampleName: " << m_signalSampleName << GEndl;
    
    m_logger << kINFO << " sampleNames: ";
    for(unsigned int i = 0; i< m_sampleNames.size(); i++){ 
        m_logger << kINFO << m_sampleNames.at(i) << " "; 
    }
    m_logger << kINFO << " sampleColors: ";
    for(unsigned int i = 0; i< m_sampleColors.size(); i++){ 
        m_logger << kINFO << m_sampleColors.at(i) << " "; 
    }
    
    m_logger << kINFO << " signalChannels: ";
    for(unsigned int i = 0; i< m_signalChannels.size(); i++){ 
        m_logger << kINFO << m_signalChannels.at(i) << " "; 
    }
    
    m_logger << kINFO << " validationChannels: ";
    for(unsigned int i = 0; i< m_validationChannels.size(); i++){ 
        m_logger << kINFO << m_validationChannels.at(i) << " "; 
    }
    
    m_logger << kINFO << " bkgConstrainChannels: ";
    for(unsigned int i = 0; i< m_bkgConstrainChannels.size(); i++){ 
        m_logger << kINFO << m_bkgConstrainChannels.at(i) << " ";
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
            m_logger << kWARNING << "FitConfig has found more then one channel with the name = " << channel << " check your code" << GEndl;
            for(unsigned int j=0; j < m_channels.size(); j++){
                m_logger << kINFO << "FitConfig m_channels[" << j << "] = " << m_channels[j] << GEndl;
            }
        }
    }

}

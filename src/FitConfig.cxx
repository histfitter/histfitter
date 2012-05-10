////////////////////////////////////////////////////////////////////////
// Creation: January 2011, David Cote (CERN)                          //
// Simple C++ mirror of python TopLevelXML objects.                   //
////////////////////////////////////////////////////////////////////////

#include "FitConfig.h"
#include <iostream>
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
}

Int_t FitConfig::getSampleColor(const TString& sample){
  for(unsigned int i = 0; i< m_sampleColors.size(); i++){
    if( sample.Contains(m_sampleNames[i].Data())){
      return m_sampleColors[i];
    }
  }
  cout<<"WARNING getSampleColor unknown sample name: "<<sample<<endl;
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
  cout<<"WARNING getSampleName unknown sample name: "<<sample<<endl;
  return "";
}

void FitConfig::Print(){
  cout<<"*** Fit Config: "<<m_Name<<" ***"<<endl;
  cout<<" inputWorkspaceFileName: "<<m_inputWorkspaceFileName<<endl;
  cout<<" signalSampleName: "<<m_signalSampleName<<endl;
  cout<<" sampleNames: ";
  for(unsigned int i = 0; i< m_sampleNames.size(); i++){ cout<<m_sampleNames.at(i)<<" "; }
  cout<<endl;
  cout<<" sampleColors: ";
  for(unsigned int i = 0; i< m_sampleColors.size(); i++){ cout<<m_sampleColors.at(i)<<" "; }
  cout<<endl;
  cout<<" signalChannels: ";
  for(unsigned int i = 0; i< m_signalChannels.size(); i++){ cout<<m_signalChannels.at(i)<<" "; }
  cout<<endl;
  cout<<" validationChannels: ";
  for(unsigned int i = 0; i< m_validationChannels.size(); i++){ cout<<m_validationChannels.at(i)<<" "; }
  cout<<endl;
  cout<<" bkgConstrainChannels: ";
  for(unsigned int i = 0; i< m_bkgConstrainChannels.size(); i++){ cout<<m_bkgConstrainChannels.at(i)<<" "; }
  cout<<endl;
  return;
}


Double_t FitConfig::getChannelMinY(const TString& channel){
  Int_t idx = -1; 
  Bool_t channelFound = kFALSE;
  findChannel(channel, idx, channelFound); 

  if(channelFound && idx > -1 &&  ((unsigned int)idx) < m_channelsMinY.size()) return m_channelsMinY[idx];
  return -9999.;
}

Double_t FitConfig::getChannelMaxY(const TString& channel){
  Int_t idx = -1; 
  Bool_t channelFound = kFALSE;
  findChannel(channel, idx, channelFound); 
  
  if(channelFound && idx > -1 && ((unsigned int)idx) < m_channelsMaxY.size()) return m_channelsMaxY[idx];
  return -999.;
}


Int_t FitConfig::getChannelNBins(const TString& channel){
  Int_t idx = -1; 
  Bool_t channelFound = kFALSE;
  findChannel(channel, idx, channelFound); 
  
  if(channelFound && idx > -1 && ((unsigned int)idx) < m_channelsNBins.size()) return m_channelsNBins[idx];
  return 999;
}


TString FitConfig::getChannelTitleX(const TString& channel){
  Int_t idx = -1; 
  Bool_t channelFound = kFALSE;
  findChannel(channel, idx, channelFound); 
  
  if(channelFound && idx > -1 && ((unsigned int)idx) < m_channelsTitleX.size()) return m_channelsTitleX[idx];
  return "";
}

TString FitConfig::getChannelTitleY(const TString& channel){
  Int_t idx = -1; 
  Bool_t channelFound = kFALSE;
  findChannel(channel, idx, channelFound); 
  
  if(channelFound && idx > -1 && ((unsigned int)idx) < m_channelsTitleY.size()) return m_channelsTitleY[idx];
  return "";
}

Bool_t  FitConfig::getChannelLogY(const TString& channel){
  Int_t idx = -1; 
  Bool_t channelFound = kFALSE;
  findChannel(channel, idx, channelFound); 
  
  if(channelFound && idx > -1 && ((unsigned int)idx) < m_channelsLogY.size()) return m_channelsLogY[idx];
  return kFALSE;
}


Double_t FitConfig::getChannelATLASLabelX(const TString& channel){
  Int_t idx = -1; 
  Bool_t channelFound = kFALSE;
  findChannel(channel, idx, channelFound); 
  
  if(channelFound && idx > -1 && ((unsigned int)idx) < m_channelsATLASLabelX.size()) return m_channelsATLASLabelX[idx];
  return -1.;
}


Double_t FitConfig::getChannelATLASLabelY(const TString& channel){
  Int_t idx = -1; 
  Bool_t channelFound = kFALSE;
  findChannel(channel, idx, channelFound); 
  
  if(channelFound && idx > -1 && ((unsigned int)idx) < m_channelsATLASLabelY.size()) return m_channelsATLASLabelY[idx];
  return -1.;
}
 

TString FitConfig::getChannelATLASLabelText(const TString& channel){
  Int_t idx = -1; 
  Bool_t channelFound = kFALSE;
  findChannel(channel, idx, channelFound); 
  
  if(channelFound && idx > -1 && ((unsigned int)idx) < m_channelsATLASLabelText.size()) return m_channelsATLASLabelText[idx];
  return "";
}

Bool_t  FitConfig::getChannelShowLumi(const TString& channel){
  Int_t idx = -1; 
  Bool_t channelFound = kFALSE;
  findChannel(channel, idx, channelFound); 
  
  if(channelFound && idx > -1 && ((unsigned int)idx) < m_channelsShowLumi.size()) return m_channelsShowLumi[idx];
  return kFALSE;
}


void FitConfig::findChannel(const TString& channel, Int_t& idx, Bool_t& channelFound){
  
  for(unsigned int i=0; i < m_channels.size(); i++){
    if(m_channels[i].EqualTo(channel) && !channelFound){
      idx = i;
      channelFound = kTRUE;
    } 
    else if(m_channels[i].EqualTo(channel) && channelFound){
      cout << endl << " *** FitConfig has found more then one channel with the name = " << channel << " check your code" << endl;
      for(unsigned int j=0; j < m_channels.size(); j++){
	cout << " *** FitConfig m_channels[" << j << "] = " << m_channels[j] << endl;
      }
    }
  }
  
}

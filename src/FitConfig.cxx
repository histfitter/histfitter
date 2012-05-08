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
  for(unsigned int i = 0; i< m_sampleColors.size(); i++){
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


// vim: ts=4:sw=4
/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Class  : FitConfig                                                             *
 * Created: January 2011                                                          *
 *                                                                                *
 * Description:                                                                   *
 *      Implementation (see header for description)                               *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/

#include <iostream>
#include "FitConfig.h"

using namespace std;


//_______________________________________________________________________________________
FitConfig::FitConfig() : m_logger("FitConfig"){
}


//_______________________________________________________________________________________
FitConfig::FitConfig(const TString& name) : m_logger("FitConfig") {
    m_name=name;
}


//_______________________________________________________________________________________
void FitConfig::Print(){
    m_logger << kINFO << "*** Fit Config: " << m_name << " ***" << GEndl;
    m_logger << kINFO << " inputWorkspaceFileName: " << m_inputWorkspaceFileName << GEndl;
    
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


//_______________________________________________________________________________________
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


//_______________________________________________________________________________________
ChannelStyle FitConfig::getChannelStyle(const TString& channel) {
  
  Int_t idx = 0;
  Bool_t channelFound = kFALSE;
  for(unsigned int i=0; i < m_channelsStyle.size(); i++){
    if(m_channelsStyle[i].getName().EqualTo(channel)){
      idx = i;
      channelFound = kTRUE;
    } 
  }
  
  if (channelFound){ return m_channelsStyle[idx];}
  else{ 
    m_logger << kINFO << "FitConfig channel = " << channel << " has no style defined, going for default" << GEndl;  
    for(unsigned int j=0; j < m_channels.size(); j++){
      m_logger << kINFO << "FitConfig m_channelsStyle[" << j << "] = " << m_channelsStyle[j].getName() << GEndl;
    }
    
    ChannelStyle* style = new ChannelStyle(channel);
    m_channelsStyle.push_back(*style);
    return *style;
  }
  
}

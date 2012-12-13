// vim: ts=4:sw=4
////////////////////////////////////////////////////////////////////////
// Creation: January 2011, David Cote (CERN)                          //
// Simple C++ mirror of python TopLevelXML objects.                   //
////////////////////////////////////////////////////////////////////////

#ifndef FITCONFIG_H
#define FITCONFIG_H

#include <iostream>
#include <vector>
#include "TString.h"
#include "TLegend.h"
#include "TMsgLogger.h"
#include "ChannelStyle.h"

class FitConfig {
 public:
  FitConfig();
  FitConfig(const TString& name);
  ~FitConfig(){}

  // per FitConfig options (in python equivalent to TopLevelXML)
  TString m_name;
  TString m_inputWorkspaceFileName;
  Float_t m_lumi;
  TString m_signalSampleName;

  std::vector<TString> m_signalChannels;
  std::vector<TString> m_validationChannels;
  std::vector<TString> m_bkgConstrainChannels;

  // channels and channel plotting styles
  std::vector<TString> m_channels;
  std::vector<ChannelStyle> m_channelsStyle;
  
  ChannelStyle getChannelStyle(const TString& channel);
  
  void findChannel(const TString& channel, Int_t& idx, Bool_t& channelFound);
  void Print();
  TString m_hypoTestName;

 private:
  TMsgLogger m_logger;
};

#endif

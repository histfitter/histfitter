// vim: ts=4:sw=4
/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Class  : FitConfig                                                             *
 * Created: January 2011                                                          *
 *                                                                                *
 * Description:                                                                   *
 *      C++ mirror class of python TopLevelXML objects.                           *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/

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

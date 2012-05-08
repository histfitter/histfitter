////////////////////////////////////////////////////////////////////////
// Creation: January 2011, David Cote (CERN)                          //
// Simple C++ mirror of python TopLevelXML objects.                   //
////////////////////////////////////////////////////////////////////////

#ifndef FITCONFIG_H
#define FITCONFIG_H

#include <iostream>
#include <vector>
#include "TString.h"


class FitConfig
{
public:
  FitConfig();
  FitConfig(const TString& name);
  ~FitConfig(){}

  Int_t getSampleColor(const TString& sample);
  TString getSampleName(const TString& sample);
  Float_t getLumi();
  void Print();

  TString m_Name;
  TString m_inputWorkspaceFileName;
  TString m_signalSampleName;
  Float_t m_Lumi;
  std::vector<Int_t> m_sampleColors;
  std::vector<TString> m_sampleNames;

  std::vector<TString> m_signalChannels;
  std::vector<TString> m_validationChannels;
  std::vector<TString> m_bkgConstrainChannels;

};

#endif

/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Class  : ChannelStyle                                                          *
 * Created: November 2012                                                         *
 *                                                                                *
 * Description:                                                                   *
 *      Class to set plot style for each channel                                  *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/

#ifndef CHANNELSTYLE_H
#define CHANNELSTYLE_H

#include <iostream>
#include <vector>
#include "TString.h"
#include "TLegend.h"
#include "TMsgLogger.h"

class ChannelStyle : public TObject{
 public:
  ChannelStyle();
  ChannelStyle(const TString& name);
  ~ChannelStyle(){}

  ClassDef(ChannelStyle,1) 

  // per sample options
  std::vector<Int_t> m_sampleColors;
  std::vector<TString> m_sampleNames;

  // get/set functions
  Int_t getSampleColor(const TString& sample);
  TString getSampleName(const TString& sample);
 
  void addSample(const TString& sample, const Int_t& color){
    m_sampleNames.push_back(sample);
    m_sampleColors.push_back(color);
  }
 
  Float_t getLumi(){ return m_lumi;}
  void setLumi(Double_t lumi){ m_lumi = lumi; }

  TString getEnergy(){ return m_energy;}
  void setEnergy(TString energy){ m_energy = energy; }

  TString getName(){ return m_name;}
  void setName(TString name){ m_name = name; }

  TString getTitle(){ return m_title;}
  void setTitle(TString title){ m_title = title; }

  Int_t getDataColor() { return m_dataColor; }
  void setDataColor(const Int_t& color) { m_dataColor = color; }

  Int_t getTotalPdfColor() { return m_totalPdfColor; }
  void setTotalPdfColor(const Int_t& color) { m_totalPdfColor = color; }

  Int_t getErrorLineColor() { return m_errorLineColor; }
  void setErrorLineColor(const Int_t& color) { m_errorLineColor = color; }

  Int_t getErrorLineStyle() { return m_errorLineStyle; }
  void setErrorLineStyle(const Int_t& style) { m_errorLineStyle = style; }

  Int_t getErrorFillColor() { return m_errorFillColor; }
  void setErrorFillColor(const Int_t& color) { m_errorFillColor = color; }

  Int_t getErrorFillStyle() { return m_errorFillStyle; }
  void setErrorFillStyle(const Int_t& style) { m_errorFillStyle = style; }

  Double_t getMinY(){ return m_minY; }
  void setMinY(Double_t miny) { m_minY = miny; }

  Double_t getMaxY(){ return m_maxY; }
  void setMaxY(Double_t maxy) { m_maxY = maxy; }

  Int_t getNBins() { return m_nBins; }
  void setNBins(Int_t nbins) { m_nBins = nbins; }

  TString getTitleX() { return m_titleX ; }
  void setTitleX(const TString&  title) { m_titleX = title; }

  TString getTitleY() { return m_titleY; }
  void setTitleY(const TString&  title) { m_titleY = title; }

  Bool_t getLogY() { return m_logY; }
  void setLogY(Bool_t doLogy = kFALSE) { m_logY = doLogy; }

  Double_t getATLASLabelX() { return m_ATLASLabelX;}
  void setATLASLabelX(Double_t x) { m_ATLASLabelX = x; }

  Double_t getATLASLabelY() { return m_ATLASLabelY;}
  void setATLASLabelY(Double_t y) { m_ATLASLabelY = y; }

  TString getATLASLabelText() { return m_ATLASLabelText;}
  void setATLASLabelText(const TString&  text) { m_ATLASLabelText = text; }

  Bool_t getShowLumi() { return m_showLumi;}
  void setShowLumi(Bool_t showlumi = kFALSE) { m_showLumi = showlumi; }

  Double_t getRegionLabelX() { return m_RegionLabelX;}
  void setRegionLabelX(Double_t x) { m_RegionLabelX = x; }

  Double_t getRegionLabelY() { return m_RegionLabelY;}
  void setRegionLabelY(Double_t y) { m_RegionLabelY = y; }

  TString getRegionLabelText() { return m_RegionLabelText;}
  void setRegionLabelText(const TString&  text) { m_RegionLabelText = text; }

  Double_t getLumiX() { return m_LumiX;}
  void setLumiX(Double_t x) { m_LumiX = x; }

  Double_t getLumiY() { return m_LumiY;}
  void setLumiY(Double_t y) { m_LumiY = y; }

  Double_t getXErrorSize() { return m_XErrorSize;}
  void setXErrorSize(Double_t x) { m_XErrorSize = x; }
  
  Bool_t getIntegerStyle() { return m_IntegerStyle;}
  void setIntegerStyle(Bool_t IntegerStyle = kFALSE) { m_IntegerStyle = IntegerStyle; }

  Double_t getArrowX() { return m_ArrowX;}
  void setArrowX(Double_t x) { m_ArrowX = x; }

  Double_t getArrowY() { return m_ArrowY;}
  void setArrowY(Double_t y) { m_ArrowY = y; }

  Double_t getArrowEnd() { return m_ArrowEnd;}
  void setArrowEnd(Double_t end) { m_ArrowEnd = end; }

  Double_t getArrowAngle() { return m_ArrowAngle;}
  void setArrowAngle(Double_t angle) { m_ArrowAngle = angle; }

  Double_t getArrowWidth() { return m_ArrowWidth;}
  void setArrowWidth(Double_t width) { m_ArrowWidth = width; }

  Int_t getArrowColor() { return m_ArrowColor; }
  void setArrowColor(const Int_t& color) { m_ArrowColor = color; }

  Bool_t getArrowRatio() { return m_ArrowRatio;}
  void setArrowRatio(Bool_t ArrowRatio = kFALSE) { m_ArrowRatio = ArrowRatio; }

  TLegend* getTLegend(){ return m_legend;}
  void setTLegend(TLegend* leg) { m_legend = leg; }
 
  Bool_t getRemoveEmptyBins() { return m_removeEmptyBins;}
  void setRemoveEmptyBins(Bool_t remove = kFALSE) { m_removeEmptyBins = remove; }

  Int_t setDefaultSampleColor() { return m_defaultSampleColor; }
  void setDefaultSampleColor(const Int_t& color) { m_defaultSampleColor = color; }

  inline TString  getText1() { return m_line1; }
  inline TString  getText2() { return m_line2; }
  inline Double_t getTextSize1() { return m_textsize1; }
  inline Double_t getTextSize2() { return m_textsize2; }

  inline void  setText1(const TString& text) { m_line1=text; }
  inline void  setText2(const TString& text) { m_line2=text; }
  inline void  setTextSize1(const Double_t& fsize) { m_textsize1=fsize; }
  inline void  setTextSize2(const Double_t& fsize) { m_textsize2=fsize; }

  using TObject::Print;
  virtual void Print();

private:
  
  TMsgLogger m_logger;  
  // per ChannelStyle options (in python equivalent to TopLevelXML)
  TString m_name;
  TString m_title;
  Float_t m_lumi;
  TString m_energy;

  Int_t m_dataColor;
  Int_t m_totalPdfColor;
  Int_t m_errorLineColor;
  Int_t m_errorLineStyle;
  Int_t m_errorFillColor;
  Int_t m_errorFillStyle;      
  TLegend* m_legend;
  Bool_t m_removeEmptyBins;    

  // per channel options
  Double_t m_minY;
  Double_t m_maxY;
  Int_t m_nBins;
  TString m_titleX;
  TString m_titleY;
  Bool_t m_logY;
  Double_t m_ATLASLabelX;
  Double_t m_ATLASLabelY;
  TString m_ATLASLabelText;
  Bool_t m_showLumi; 

  Double_t m_RegionLabelX;
  Double_t m_RegionLabelY;
  TString m_RegionLabelText;
  Double_t m_LumiX;
  Double_t m_LumiY;
  Double_t m_XErrorSize;
  Bool_t m_IntegerStyle;
  Double_t m_ArrowX;
  Double_t m_ArrowY;
  Double_t m_ArrowEnd;
  Double_t m_ArrowAngle;
  Double_t m_ArrowWidth;
  Int_t m_ArrowColor;
  Bool_t m_ArrowRatio;


  Int_t m_defaultSampleColor;
  Int_t m_defaultSampleCounter;

  TString  m_line1;
  Double_t m_textsize1;
  TString  m_line2;
  Double_t m_textsize2;

};

#endif

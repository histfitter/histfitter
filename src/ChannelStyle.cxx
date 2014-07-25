// vim: ts=4:sw=4
/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Class  : ChannelStyle                                                          *
 * Created: November 2012
 *                                                                                *
 * Description:                                                                   *
 *      Implementation (see header for description)                               *
 *                                                                                *
 * See corresponding .h file for author and license information                   *         
 *                                                                                *
 **********************************************************************************/

#include <iostream>
#include "ChannelStyle.h"

using namespace std;

ClassImp(ChannelStyle);


//_______________________________________________________________________________________
ChannelStyle::ChannelStyle() : m_logger("ChannelStyle"){
}


//_______________________________________________________________________________________
ChannelStyle::ChannelStyle(const TString& name) : m_logger("ChannelStyle") {
    m_name = name;
    m_title = "";
    m_dataColor = kBlack;	     
    m_totalPdfColor = kBlue;
    m_errorLineColor = kBlue - 5;
    m_errorLineStyle = 1;    // AK: 1 = kSolid, which somehow does not compile    
    m_errorFillColor = kBlue - 5;
    m_errorFillStyle = 3004;
    m_legend = NULL;
    m_removeEmptyBins = false;     

    m_minY = 0.05;
    m_maxY = -999.;
    m_nBins = -1;
    m_titleX = "";
    m_titleY = "";
    m_logY = kFALSE;
    m_ATLASLabelX = -1.;
    m_ATLASLabelY = -1.;
    m_ATLASLabelText = "";
    m_showLumi = kFALSE;
    m_lumi = -1.;

    m_defaultSampleColor = kRed-10;
    m_defaultSampleCounter = 0;

    m_line1 = "";
    m_line2 = "";
    m_textsize1 = 0.04;
    m_textsize2 = 0.04;
}


//_______________________________________________________________________________________
Int_t ChannelStyle::getSampleColor(const TString& sample){
  Bool_t sampleFound = kFALSE;
  for(unsigned int i = 0; i< m_sampleColors.size(); i++){
    m_logger << kDEBUG << "getSampleColor:  requested sample name: "<<sample  
	     << " , defined m_sampleNames[" << i << "]="<< m_sampleNames[i] << GEndl;
    TString target = "_"+m_sampleNames[i]+"_";
    if( sample.Contains(target.Data())){
      sampleFound = kTRUE;
      return m_sampleColors[i];
    }
  }
  
  if(!sampleFound){
    m_logger << kWARNING << "getSampleColor unknown sample name: "<<sample 
	     << ", will use default color and add this sample to ChannelStyle"<< GEndl;
    Int_t color = m_defaultSampleColor + m_defaultSampleCounter;
    addSample(sample, color);
    m_defaultSampleCounter++;
    return color;
  }
  
  return 0;
}


//_______________________________________________________________________________________
TString ChannelStyle::getSampleName(const TString& sample){
    for(unsigned int i = 0; i< m_sampleNames.size(); i++){
      m_logger << kDEBUG << "getSampleName: requested sample name: "<<sample  
	       << ", defined m_sampleNames[" << i << "]="<< m_sampleNames[i] << GEndl;
      TString target = "_"+m_sampleNames[i]+"_";
      if( sample.Contains(target.Data())){
            return m_sampleNames[i];
        }
    }
    m_logger << kWARNING << "getSampleName unknown sample name: "<<sample << GEndl;
    return "";
}


//_______________________________________________________________________________________
void ChannelStyle::Print(){
    m_logger << kINFO << "*** ChannelStyle: " << m_name << " ***" << GEndl;
        
    m_logger << kINFO << " sampleNames: ";
    for(unsigned int i = 0; i< m_sampleNames.size(); i++){ 
        m_logger << kINFO << m_sampleNames.at(i) << " "; 
    }
    m_logger << kINFO << " sampleColors: ";
    for(unsigned int i = 0; i< m_sampleColors.size(); i++){ 
        m_logger << kINFO << m_sampleColors.at(i) << " "; 
    }
    
    return;
}

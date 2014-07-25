/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Namespace: ValidationUtils                                                     *
 *                                                                                *
 * Description:                                                                   *
 *      Util functions for drawing validation plots                               *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/

#ifndef ValidationUtilsDEF
#define ValidationUtilsDEF

//Combination/trunk/Tools/CombinationGlob.h
#include "TCanvas.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TLine.h"
#include "TLatex.h"
#include "TLegend.h"
#include "TString.h"
#include "TColor.h"
#include "TROOT.h"
#include "TDirectory.h"
#include "TStyle.h"
#include "TGraph.h"
#include "TMath.h"

#include <iostream>
using std::cout;
using std::endl;

#include "XtraValues.h"

namespace ValidationUtils
{
  void Horizontal( TH1 *h, Int_t nbin, Bool_t kLINE, Int_t color, float yWidthScaleUp=0.12, float yWidthScaleDown=0.12  );
  void HorizontalElMu( TH1 *h, Int_t nbin, Bool_t kLINE, Int_t color, Int_t color2, float yWidthScale=0.25 );


  void SetCombinationStyle();

  // set style and remove existing canvas'
  void Initialize( Bool_t useCombinationStyle = kTRUE );

  // set frame styles
  void SetFrameStyle2D( TH1* frame, Float_t scale = 1.0 );
  
  void PullPlot3(XtraValues* inValsEl, XtraValues* inValsMu, const TString& outFileNamePrefix);
  void PullPlot4(XtraValues* inVals, const TString& outFileNamePrefix);
  void PullPlot5(XtraValues* inValsEl, XtraValues* inValsMu,  XtraValues* inValsEM, const TString& outFileNamePrefix);

}

#endif

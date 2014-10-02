/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Macro  : CombinationGlob.C                                                     *
 * Created: 12 June 2012                                                          *
 *                                                                                *
 * Description:                                                                   *
 *      class for stlye used in the contour plots                                 *                              
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/

// global Combination style settings
#ifndef Combination_CombinationGlob
#define Combination_CombinationGlob

#include "TObject.h"
#include "TString.h"
#include "TColor.h"
#include "TList.h"
#include "TROOT.h"
#include "TDirectory.h"
#include "TStyle.h"
#include "TH1.h"
#include "TH2.h"
#include "TClass.h"
#include "TKey.h"
#include "TLine.h"
#include "TLegend.h"
#include "TCanvas.h"
#include "TPad.h"
#include "TLatex.h"
#include "TFile.h"
#include "TImage.h"
#include "TGraph.h"
#include "TMarker.h"
#include "TImage.h"
#include "TMath.h"
#include "TSystem.h"
#include "contourmacros/CombinationConf.C"

#include <iostream>
using std::cout;
using std::endl;


namespace CombinationGlob {

   // ==========================================================================================
   // constants and enums

   // --- Estimators

   enum Estimator { kChi2 = 0, kDChi2, kDLike, kCL, kMaxEstimator, kPValue };

   static TString EstimatorHName[] = { "chi2", "dchi2", "dlike", "cl" };
   static TString EstimatorName[]  = { "chi-squared", "delta chi-squared", "delta likelihood", "1 - CL" };
   static TString EstimatorTitle[] = { "#chi^{2}", "#Delta#chi^{2}", "#Delta Likelihood", "1 - CL" };
   static Float_t EstimatorYmax[]  = { 30, 10, 1.1, 1.1 };

   // --- Packages

   enum GPackage { IsGSM = 0, IsGSUSY, IsG2HDM, IsCombination, IsGOblique };

   // --- Path names

   // logo
   const TString LogoPath[] = { "../../doc/images/gsm_logo_sep07.png", 
                                 "../../doc/images/gsusy_logo.png",
                                 "../../doc/images/g2hdb_logo.png" };

   // --- Style

   static Bool_t UsePaperStyle = CombinationConf::UsePaperStyle;
   enum ColorStyle { Greenish = 0, Bluish, Orangish, Redish, Grayish };

   // draw type (evolution)
   enum DrawType { FirstPass = 0, SecondPass, Full };

   // canvas size
   static Int_t StandardCanvas[] = { 700, 500 };

   // Text sise
   static Float_t DescriptionTextSize = 0.035;

   // --- user-defined colors
   static Int_t c_LHiggsGreen   = TColor::GetColor( "#dfff67" );
   static Int_t c_HiggsGreen    = TColor::GetColor( "#cfff47" );
   static Int_t c_DHiggsGreen   = TColor::GetColor( "#75Bf17" );
   static Int_t c_HiggsBlue     = TColor::GetColor( "#82CAFA" );
   static Int_t c_White         = TColor::GetColor( "#ffffff" );
   static Int_t c_LightYellow   = TColor::GetColor( "#ffff00" );
   static Int_t c_VLightYellow  = TColor::GetColor( "#ffffe0" );
   static Int_t c_DarkYellow    = TColor::GetColor( "#ffd700" );
   static Int_t c_VDarkYellow   = TColor::GetColor( "#ffa500" );
   static Int_t c_LightOrange   = TColor::GetColor( "#ffcc00" );
   static Int_t c_VLightOrange  = TColor::GetColor( "#ffdd44" );
   static Int_t c_DarkOrange    = TColor::GetColor( "#ff6600" );
   static Int_t c_VDarkOrange   = TColor::GetColor( "#aa4400" );
   static Int_t c_LightGreen    = TColor::GetColor( "#aaff33" );
   static Int_t c_VLightGreen   = TColor::GetColor( "#bdff66" );
   static Int_t c_DarkGreen     = TColor::GetColor( "#115000" );
   static Int_t c_VDarkGreen    = TColor::GetColor( "#114400" );
   static Int_t c_LightBlue     = TColor::GetColor( "#66aaff" );
   static Int_t c_DarkBlue      = TColor::GetColor( "#0000bb" );
   static Int_t c_VDarkBlue     = TColor::GetColor( "#000066" );
   static Int_t c_VLightRed     = TColor::GetColor( "#ffcccc" );
   static Int_t c_LightRed      = TColor::GetColor( "#ff3333" );
   static Int_t c_DarkRed       = TColor::GetColor( "#800000" );
   static Int_t c_NovelRed      = TColor::GetColor( "#dd0033" );

   static Int_t c_VLightPink    = TColor::GetColor( "#FFCCFF" );
   static Int_t c_LightPink     = TColor::GetColor( "#CC66FF" );
   static Int_t c_DarkPink      = TColor::GetColor( "#CC0099" );
   static Int_t c_VDarkPink      = TColor::GetColor( "#660066" );

   static Int_t c_BlueT0        = TColor::GetColor( "#112288" );
   static Int_t c_BlueT1        = TColor::GetColor( "#2255cc" );
   static Int_t c_BlueT2        = TColor::GetColor( "#4488dd" );
   static Int_t c_BlueT3        = TColor::GetColor( "#99bbff" );
   static Int_t c_BlueT4        = TColor::GetColor( "#99bbff" );
   static Int_t c_BlueT5        = TColor::GetColor( "#aaddff" );
   static Int_t c_NovelBlue     = TColor::GetColor( "#2244a5" );

   static Int_t c_DarkBlueT1    = TColor::GetColor( "#0000aa" );
   static Int_t c_DarkBlueT2    = TColor::GetColor( "#1122bb" );
   static Int_t c_DarkBlueT3    = TColor::GetColor( "#2233ee" );
   static Int_t c_DarkBlueT4    = TColor::GetColor( "#0022aa" );
   static Int_t c_DarkBlueT5    = TColor::GetColor( "#001177" );

   static Int_t c_VLightGray    = TColor::GetColor( "#eeeeee" );
   static Int_t c_MLightGray    = TColor::GetColor( "#dddddd" );
   static Int_t c_LightGray     = TColor::GetColor( "#aaaaaa" );
   static Int_t c_Gray          = TColor::GetColor( "#888888" );
   static Int_t c_DarkGray      = TColor::GetColor( "#555555" );
   static Int_t c_VDarkGray     = TColor::GetColor( "#333333" );
   static Int_t c_Black         = TColor::GetColor( "#000000" );

   static Int_t c_ExclusionCol  = TColor::GetColor( "#999999" );
   static Int_t c_ExclusionColL = TColor::GetColor( "#cccccc" );

   static Int_t c_VLightBkg     = TColor::GetColor( "#eeeeee" );

   // --- constants
   static Double_t cl_sigma[]   = { 3.17310522791349303e-01,
                                    4.55002597802489639e-02,
                                    2.69979614651120765e-03,
                                    6.33424887837306439e-05,
                                    5.73303137155808246e-07 };
   static Double_t cl_percent[] = { 0.32,
                                    0.05,
                                    0.01,
                                    0.001,
                                    5.73303137155808246e-07 };

   static Int_t    fcol_sigma[] = { c_BlueT2, c_BlueT3, c_BlueT5, c_LightBlue, c_BlueT5 };
   static Int_t    lcol_sigma[] = { c_DarkBlueT1, c_DarkBlueT2, c_DarkBlueT3, c_DarkBlueT4, c_DarkBlueT5 };

   // --- Words (as flags)

   enum Where { Top = 0, Bottom, Left, Right };

   // -----------------------------------------------

   // ==========================================================================================

   // set the style
   void Set1DPlotStyle( TH1* scan1Dhist ) 
   {
      // const Int_t FillColor__S = 38 + 150; // change of Color Scheme in ROOT-5.16.
      // convince yourself with gROOT->GetListOfColors()->Print()
      const Int_t FillColor__S = 38;
      const Int_t FillStyle__S = 1001;
      // const Int_t LineColor__S = 4 + 100;
      const Int_t LineColor__S = 4;
      const Int_t LineWidth__S = 2;

      if (scan1Dhist != NULL) {
         scan1Dhist->SetLineColor( LineColor__S );
         scan1Dhist->SetLineWidth( LineWidth__S );
         scan1Dhist->SetFillStyle( FillStyle__S );
         scan1Dhist->SetFillColor( FillColor__S );
      }    
   }

   // set frame styles
   void SetFrameStyle1D( TH1* frame, Float_t scale = 1.0 )
   {
      frame->SetLabelOffset( 0.012, "X" );// label offset on x axis
      frame->SetLabelOffset( 0.012, "Y" );// label offset on x axis
      frame->GetXaxis()->SetTitleOffset( 1.40 );
      frame->GetYaxis()->SetTitleOffset( 1.04 );
      frame->GetXaxis()->SetTitleSize( 0.045*scale );
      frame->GetYaxis()->SetTitleSize( 0.045*scale );
      Float_t labelSize = 0.04*scale;
      frame->GetXaxis()->SetLabelSize( labelSize );
      frame->GetYaxis()->SetLabelSize( labelSize );

      // global style settings
      gPad->SetTicks();
      gPad->SetLeftMargin  ( 0.103*scale );
      gPad->SetRightMargin ( 0.050*scale );
      gPad->SetBottomMargin( 0.132*scale  );
      //if ( UsePaperStyle )
         gPad->SetTopMargin( 0.060*scale  );
   }

   // set frame styles
   void SetFrameStyle2D( TH1* frame, Float_t scale = 1.0 )
   {
      frame->SetLabelOffset( 0.012, "X" );// label offset on x axis
      frame->SetLabelOffset( 0.012, "Y" );// label offset on x axis
      frame->GetXaxis()->SetTitleOffset( 1.33 );
      frame->GetYaxis()->SetTitleOffset( 1.25 );
      frame->GetXaxis()->SetTitleSize( 0.045*scale );
      frame->GetYaxis()->SetTitleSize( 0.045*scale );
      Float_t labelSize = 0.04*scale;
      frame->GetXaxis()->SetLabelSize( labelSize );
      frame->GetYaxis()->SetLabelSize( labelSize );

      // global style settings
      gPad->SetTicks();
      gPad->SetLeftMargin  ( 0.120*sqrt(scale) );
      gPad->SetRightMargin ( 0.050 );
      gPad->SetBottomMargin( 0.120*scale  );
      gPad->SetTopMargin( 0.060*scale  );
   }

   void DrawContour( TH2F* hist, Int_t nsigma, DrawType type = Full )
   {
      if (nsigma < 0 || nsigma > 5) {
         cout << "*** Error in CombinationGlob::DrawContour: nsigma out of range: " << nsigma 
              << "==> abort" << endl;
         exit(1);
      }
      nsigma--; // used as array index
   
      TH2F* h = new TH2F( *hist );
      h->SetContour( 1 );
      float cl;
      int   fcol, lcol;
      if (nsigma>=0) {
         cl   = cl_percent[nsigma];
         fcol = fcol_sigma[nsigma];
         lcol = lcol_sigma[nsigma];
      }
      else {
         cl   = 0.80;
         fcol = c_BlueT1;
         lcol = c_DarkBlue;
      }         

      h->SetContourLevel( 0, cl );
      if (type == FirstPass || type == Full) {
         h->SetFillColor( fcol );
         h->Draw( "samecont0" );
      
         h->SetLineWidth( 2 );
         h->SetLineColor( fcol );
         h->Draw( "samecont3" );
      }

      h->SetLineWidth( 1 );
      h->SetLineColor( lcol );
      h->Draw( "samecont3" );
   }

   void DrawBestValue( TH2F* hist, Int_t markerType = 20 )
   {
      Int_t mx, my, mz;
      hist->GetMaximumBin( mx, my, mz );
      Float_t x = hist->GetXaxis()->GetBinCenter( mx );
      Float_t y = hist->GetYaxis()->GetBinCenter( my );
      TMarker* marker = new TMarker( x, y, markerType );
      marker->SetMarkerColor( 1 );
      marker->SetMarkerSize ( 1 );
      marker->Draw();
   }

   void DrawTwoLineText( TH1* frame, Float_t xref, Float_t yref, TString ta, TString tb, Int_t col, Float_t dyadd = 0 )
   {
      Float_t dy = (frame->GetYaxis()->GetXmax() - frame->GetYaxis()->GetXmin())*0.1;

      TLatex* tta = new TLatex( xref, yref, ta );
      TLatex* ttb = new TLatex( xref, yref - dy*(0.013 + dyadd), tb );
      tta->SetTextColor( col );
      ttb->SetTextColor( col );
      tta->SetTextAlign( 11 );
      ttb->SetTextAlign( 13 );
      tta->SetTextSize( DescriptionTextSize );
      ttb->SetTextSize( DescriptionTextSize );
      tta->AppendPad();      
      ttb->AppendPad();      
   }

   void DrawThreeLineText( TH1* frame, Float_t xref, Float_t yref, TString ta, TString tb, TString tc, 
                      Int_t col, Float_t dyadd2 = 0, Float_t dyadd3 = 0 )
   {
      Float_t dy = (frame->GetYaxis()->GetXmax() - frame->GetYaxis()->GetXmin())*0.1;

      TLatex* tta = new TLatex( xref, yref, ta );
      TLatex* ttb = new TLatex( xref, yref - 1*dy*(0.25 + dyadd2), tb );
      TLatex* ttc = new TLatex( xref, yref - 2*dy*(0.25 + dyadd3), tc );
      tta->SetTextColor( col );
      ttb->SetTextColor( col );
      ttc->SetTextColor( col );
      tta->SetTextAlign( 11 );
      ttb->SetTextAlign( 11 );
      ttc->SetTextAlign( 11 );
      tta->SetTextSize( DescriptionTextSize );
      ttb->SetTextSize( DescriptionTextSize );
      ttc->SetTextSize( DescriptionTextSize );
      tta->AppendPad();      
      ttb->AppendPad();      
      ttc->AppendPad();      
   }


   void DrawFiveLineText( TH1* frame, Float_t xref, Float_t yref, TString ta, TString tb, TString tc, TString td, TString te,
                     Int_t col )
   {
      Float_t dy = (frame->GetYaxis()->GetXmax() - frame->GetYaxis()->GetXmin())*0.1;

      TLatex* tta = new TLatex( xref, yref, ta );
      TLatex* ttb = new TLatex( xref, yref - 1*dy*(0.5), tb );
      TLatex* ttc = new TLatex( xref, yref - 2*dy*(0.5), tc );
      TLatex* ttd = new TLatex( xref, yref - 3*dy*(0.5), td );
      TLatex* tte = new TLatex( xref, yref - 4*dy*(0.5), te );
      tta->SetTextColor( col );
      ttb->SetTextColor( col );
      ttc->SetTextColor( col );
      ttd->SetTextColor( col );
      tte->SetTextColor( col );
      tta->SetTextAlign( 11 );
      ttb->SetTextAlign( 11 );
      ttc->SetTextAlign( 11 );
      ttd->SetTextAlign( 11 );
      tte->SetTextAlign( 11 );
      tta->SetTextSize( DescriptionTextSize );
      ttb->SetTextSize( DescriptionTextSize );
      ttc->SetTextSize( DescriptionTextSize );
      ttd->SetTextSize( DescriptionTextSize );
      tte->SetTextSize( DescriptionTextSize );
      tta->AppendPad();
      ttb->AppendPad();
      ttc->AppendPad();
      ttd->AppendPad();
      tte->AppendPad();
   }

   void DrawSixLineText( TH1* frame, Float_t xref, Float_t yref, TString ta, TString tb, TString tc, TString td, TString te, TString tf,
                     Int_t col )
   {
      Float_t dy = (frame->GetYaxis()->GetXmax() - frame->GetYaxis()->GetXmin())*0.1;

      TLatex* tta = new TLatex( xref, yref, ta );
      TLatex* ttb = new TLatex( xref, yref - 1*dy*(0.5), tb );
      TLatex* ttc = new TLatex( xref, yref - 2*dy*(0.5), tc );
      TLatex* ttd = new TLatex( xref, yref - 3*dy*(0.5), td );
      TLatex* tte = new TLatex( xref, yref - 4*dy*(0.5), te );
      TLatex* ttf = new TLatex( xref, yref - 5*dy*(0.5), tf );
      tta->SetTextColor( col );
      ttb->SetTextColor( col );
      ttc->SetTextColor( col );
      ttd->SetTextColor( col );
      tte->SetTextColor( col );
      ttf->SetTextColor( col );
      tta->SetTextAlign( 11 );
      ttb->SetTextAlign( 11 );
      ttc->SetTextAlign( 11 );
      ttd->SetTextAlign( 11 );
      tte->SetTextAlign( 11 );
      ttf->SetTextAlign( 11 );
      tta->SetTextSize( DescriptionTextSize ); 
      ttb->SetTextSize( DescriptionTextSize );
      ttc->SetTextSize( DescriptionTextSize ); 
      ttd->SetTextSize( DescriptionTextSize );
      tte->SetTextSize( DescriptionTextSize );
      ttf->SetTextSize( DescriptionTextSize );
      tta->AppendPad();
      ttb->AppendPad();
      ttc->AppendPad();
      ttd->AppendPad();
      tte->AppendPad();
      ttf->AppendPad();
   }

   void ContourLegend( TH2* frame, const TString text, Bool_t AtTop = kTRUE )
   {
      Float_t dx = frame->GetXaxis()->GetXmax() - frame->GetXaxis()->GetXmin();
      Float_t dy = frame->GetYaxis()->GetXmax() - frame->GetYaxis()->GetXmin();
      TLatex* t = new TLatex( frame->GetXaxis()->GetXmax() - dx*0.03, 
                              (AtTop ? 
                               frame->GetYaxis()->GetXmax() - dy*0.04: 
                               frame->GetYaxis()->GetXmin() + dy*0.07), text );
      t->SetTextColor( c_DarkBlue );
      t->SetTextAlign( 33 );
      t->SetTextSize( DescriptionTextSize );
      t->AppendPad();      
   }
   
   void GetColor( ColorStyle cstyle, Int_t& clight, Int_t& cdark )
   {
      switch (cstyle) {
      case Greenish: clight = c_HiggsGreen;  cdark = c_DarkGreen;  break; 
      case Bluish  : clight = c_LightBlue;   cdark = c_DarkBlue;   break; 
      case Orangish: clight = c_LightOrange; cdark = c_DarkOrange; break; 
      case Redish  : clight = c_LightRed;    cdark = c_DarkRed;    break; 
      case Grayish : clight = c_VLightGray;   cdark = c_DarkGray;    break; 
      default:
         cout << "*** Error *** Unknow colour style: " << cstyle << endl;
         exit(1);
      }
   }


   void DrawMeasurement( TH2* frame, 
                         Float_t centralValue,
                         Float_t xmin, Float_t xmax, Float_t ymin, Float_t ymax, 
                         DrawType type = FirstPass,
                         TString displayText = "", 
                         TString measurementAxis = "X", 
                         ColorStyle cstyle = Greenish,
                         Float_t dxText = 0, Float_t dyText = 0, 
                         Where halignText = Right, Where valignText = Top )
   {
      // retrieve color
      Int_t clight = 0, cdark = 0;
      GetColor( cstyle, clight, cdark );

      // first or second pass ?
      if (type == FirstPass || type == Full) {
         Double_t x[5] = { xmin, xmin, xmax, xmax, xmin };
         Double_t y[5] = { ymin, ymax, ymax, ymin, ymin };
         TGraph *box = new TGraph( 5, x, y );
         box->SetLineColor( cdark );
         box->SetFillColor( clight );
         box->Draw("F");                          
      }
      if (type == SecondPass || type == Full) {
         TLine* louter = new TLine;
         TLine* linner = new TLine;
         louter->SetLineWidth( 1 );
         louter->SetLineColor( cdark );
         linner->SetLineWidth( 1 );
         linner->SetLineStyle( 3 );
         linner->SetLineColor( cdark );
         if (measurementAxis == "Y") { // measurement axis is "Y"
            louter->DrawLine( xmin, ymin, xmax, ymin );
            louter->DrawLine( xmin, ymax, xmax, ymax );
            linner->DrawLine( xmin, centralValue, xmax, centralValue );
         }
         else {
            louter->DrawLine( xmin, ymin, xmin, ymax );
            louter->DrawLine( xmax, ymin, xmax, ymax );
            linner->DrawLine( centralValue, ymin, centralValue, ymax );
         }

         // add legend
         Float_t dx = frame->GetXaxis()->GetXmax() - frame->GetXaxis()->GetXmin();
         Float_t dy = frame->GetYaxis()->GetXmax() - frame->GetYaxis()->GetXmin();
         TLatex* t = 0;
         if (measurementAxis == "Y") {
            t = new TLatex( frame->GetXaxis()->GetXmax() - dx*0.03 + dxText, 
                            ymax + dy*0.03 + dyText, 
                            displayText );
            t->SetTextAlign( (halignText == Right) ? 32 : 12 );
         }
         else {
            t = new TLatex( xmax + dx*0.03 + dxText, 
                            frame->GetYaxis()->GetXmax() - dy*0.04 + dyText, 
                            displayText );
            t->SetTextAlign( (valignText == Bottom) ? 11 : 13 );
         }
         t->SetTextColor( cdark );
         t->SetTextSize( DescriptionTextSize );
         t->AppendPad();      
      }
   }

   void DrawMeasurement( TH2* frame, 
                         Float_t xmin, Float_t xmax, Float_t ymin, Float_t ymax, 
                         DrawType type = FirstPass,
                         TString displayText = "", 
                         TString measurementAxis = "X", 
                         ColorStyle cstyle = Greenish,
                         Float_t dxText = 0, Float_t dyText = 0, 
                         Where halignText = Right, Where valignText = Top )
   {
      // interface for no central value given 
      Float_t centralValue = 0;
      if (measurementAxis == "X") centralValue = 0.5*(xmin + xmax);
      else                        centralValue = 0.5*(ymin + ymax);
   
      DrawMeasurement( frame, centralValue, 
                       xmin, xmax, ymin, ymax, type, displayText, measurementAxis,
                       cstyle, dxText, dyText, halignText, valignText );
   
   }

   // set frame styles
   void DrawLimit( Float_t xmin, Float_t xmax, Float_t ymin, Float_t ymax, Float_t limit,
                   Bool_t upperLimit = kTRUE, 
                   DrawType type = FirstPass,
                   TString displayText = "", Where whereToPut = Top, 
                   Where whereLeftRight = Right, Float_t delta = 0 )
   {
      // draw limit box in frame
      if (type == FirstPass) {
         Double_t x1 = upperLimit ? xmin  : limit;
         Double_t x2 = upperLimit ? limit : xmin;
         Double_t x[5] = { x1, x1, x2, x2, x1 };
         Double_t y[5] = { ymin, ymax, ymax, ymin, ymin };
     
         TGraph *box1 = new TGraph( 5, x, y );
         box1->SetLineColor( c_ExclusionCol );
         box1->SetFillColor( c_ExclusionCol );
         box1->Draw("F");

         TGraph *box2 = new TGraph( 5, x, y );
         box2->SetFillColor( c_ExclusionColL );
         box2->SetLineColor( c_ExclusionColL );
         box2->SetFillStyle( 3954 );
         box2->Draw("F");
      }
      else {
         // add separator line
         TLine* line = new TLine( limit, ymin, limit, ymax );
         line->SetLineWidth( 1 );
         line->SetLineColor( 2 );
         line->Draw();

         // add text
         if (displayText != "") {
            Float_t x = limit + (whereLeftRight == Left ? -0.025 : 0.008)*(xmax - xmin);
            Float_t y = ymax - 0.03*(ymax - ymin) + delta;
            if (whereToPut == Bottom) y = ymin + 0.03*(ymax - ymin) + delta;

            TLatex *text = new TLatex( x, y, displayText );
            text->SetTextColor( c_DarkRed );
            text->SetTextAlign( (whereToPut == Top ? 33 : 13) );
            text->SetTextAngle( 90 );
            text->SetTextSize( 0.037 );
            text->AppendPad();
         }
      }
   }

   void DrawLimitBand( Float_t xmin, Float_t xmax, Float_t ymin, Float_t ymax, 
                       Float_t limitMin, Float_t limitMax,
                       DrawType type = FirstPass,
                       TString displayText = "", Where whereToPut = Top, 
                       Where whereLeftRight = Right, Float_t delta = 0, Float_t delta2 = 0 )
   {
      // draw limit box in frame
      if (type == FirstPass) {
         Double_t x1 = limitMin;
         Double_t x2 = limitMax;
         Double_t x[5] = { x1, x1, x2, x2, x1 };
         Double_t y[5] = { ymin, ymax, ymax, ymin, ymin };
     
         TGraph *box1 = new TGraph( 5, x, y );
         box1->SetLineColor( c_ExclusionCol );
         box1->SetFillColor( c_ExclusionCol );
         box1->Draw("F");

         TGraph *box2 = new TGraph( 5, x, y );
         box2->SetFillColor( c_ExclusionColL );
         box2->SetLineColor( c_ExclusionColL );
         box2->SetFillStyle( 3954 );
         box2->Draw("F");
      }
      else {
         // add separator line
         TLine* lineMax = new TLine( limitMax, ymin, limitMax, ymax );
         lineMax->SetLineWidth( 1 );
         lineMax->SetLineColor( 2 );
         lineMax->Draw();

         TLine* lineMin = new TLine( limitMin, ymin, limitMin, ymax );
         lineMin->SetLineWidth( 1 );
         lineMin->SetLineColor( 2 );
         lineMin->Draw();

         // add text
         if (displayText != "") {
            Float_t x = limitMax + (whereLeftRight == Left ? -0.025 : 0.008)*(xmax - xmin) + delta2;
            Float_t y = ymax - 0.03*(ymax - ymin) + delta;
            if (whereToPut == Bottom) y = ymin + 0.03*(ymax - ymin) + delta;

            TLatex *text = new TLatex( x, y, displayText );
            text->SetTextColor( c_DarkRed );
            text->SetTextAlign( (whereToPut == Top ? 33 : 13) );
            text->SetTextAngle( 90 );
            text->SetTextSize( 0.037 );
            text->AppendPad();
         }
      }
   }

   void DrawLimitY( Float_t xmin, Float_t xmax, Float_t ymin, Float_t ymax, Float_t limit,
                    Bool_t upperLimit = kTRUE, 
                    DrawType type = FirstPass,
                    TString displayText = "", Int_t tcol = CombinationGlob::c_DarkBlue, 
                    Where whereToPut = Top, Where whereToPutX = Left )
   {
      // draw limit box in frame
      if (type == FirstPass) {
         Double_t y1 = upperLimit ? xmin  : limit;
         Double_t y2 = upperLimit ? limit : xmin;
         Double_t y[5] = { y1, y1, y2, y2, y1 };
         Double_t x[5] = { xmin, xmax, xmax, xmin, xmin };
     
         TGraph *box1 = new TGraph( 5, x, y );
         box1->SetLineColor( c_ExclusionCol );
         box1->SetFillColor( c_ExclusionCol );
         box1->Draw("F");

         TGraph *box2 = new TGraph( 5, x, y );
         box2->SetFillColor( c_ExclusionColL );
         box2->SetLineColor( c_ExclusionColL );
         box2->SetFillStyle( 3954 );
         box2->Draw("F");
      }
      else {
         // add separator line
         TLine* line = new TLine( xmin, limit, xmax, limit );
         line->SetLineWidth( 1 );
         line->SetLineColor( 2 );
         line->Draw();

         // add text
         if (displayText != "") {
            Float_t x = xmin + 0.025*(xmax - xmin);
            Float_t y = limit + 0.007*(ymax - ymin);
            
            TLatex *text = new TLatex( x, y, displayText );
            text->SetTextColor( c_DarkRed );
            text->SetTextAlign( 11 );
            text->SetTextSize( 0.037 );
            text->AppendPad();
         }
      }
   }

   void DrawLimitBandY( Float_t xmin, Float_t xmax, Float_t ymin, Float_t ymax, 
                        Float_t limitMin, Float_t limitMax,
                        DrawType type = FirstPass,
                        TString displayText = "", Where whereToPut = Top, 
                        Where whereLeftRight = Right, Float_t delta = 0, Float_t delta2 = 0 )
   {
      // draw limit box in frame
      if (type == FirstPass) {
         Double_t y1 = limitMin;
         Double_t y2 = limitMax;
         Double_t y[5] = { y1, y1, y2, y2, y1 };
         Double_t x[5] = { xmin, xmax, xmax, xmin, xmin };
     
         TGraph *box1 = new TGraph( 5, x, y );
         box1->SetLineColor( c_ExclusionCol );
         box1->SetFillColor( c_ExclusionCol );
         box1->Draw("F");

         TGraph *box2 = new TGraph( 5, x, y );
         box2->SetFillColor( c_ExclusionColL );
         box2->SetLineColor( c_ExclusionColL );
         box2->SetFillStyle( 3954 );
         box2->Draw("F");
      }
      else {
         // add separator line
         TLine* lineMax = new TLine( xmin, limitMax, xmax, limitMax );
         lineMax->SetLineWidth( 1 );
         lineMax->SetLineColor( 2 );
         lineMax->Draw();

         TLine* lineMin = new TLine( xmin, limitMin, xmax, limitMin );
         lineMin->SetLineWidth( 1 );
         lineMin->SetLineColor( 2 );
         lineMin->Draw();

         // add text
         if (displayText != "") {
            Float_t x = xmin + 0.025*(xmax - xmin) + delta;
            Float_t y = limitMax + 0.040*(ymax - ymin) + delta2;

            TLatex *text = new TLatex( x, y, displayText );
            text->SetTextColor( c_DarkRed );
            text->SetTextAlign( 11 );
            text->SetTextSize( 0.037 );
            text->AppendPad();
         }
      }
   }


   void DrawSigmas( TH1* frame, CombinationGlob::Estimator estimator, int nsigCLmax = 2, float tsize = 0.04 )
   {
      if (estimator == kDChi2) {
         TLine* l = new TLine;
         l->SetLineStyle( 2 );
         l->SetLineColor( 12 );
         for (Int_t i=1; i<10; i++) {
            Float_t sigma = i*i;
            if (sigma > frame->GetMaximum()) break;
         
            // draw the sigma line
            l->DrawLine( frame->GetXaxis()->GetXmin(), sigma, frame->GetXaxis()->GetXmax(), sigma );
         
            // draw the legend
            Float_t dx = frame->GetXaxis()->GetXmax() - frame->GetXaxis()->GetXmin();
            //Float_t dy = frame->GetMaximum() - frame->GetMinimum();
            TLatex* text = new TLatex( frame->GetXaxis()->GetXmax() + dx*0.01, sigma, Form( "%i#sigma",i ) );
            text->SetTextColor( 12 );
            text->SetTextAlign( 12 );
            text->SetTextSize( tsize );
            text->AppendPad();
         }
      }
      else if (estimator == kCL) {
         TLine* l = new TLine;
         l->SetLineStyle( 2 );
         l->SetLineColor( 12 );
         for (Int_t i=1; i<=nsigCLmax; i++) {
            Float_t sigma = i;
            Float_t P = TMath::Prob( sigma*sigma, 1 );
            if (P <= frame->GetYaxis()->GetXmin()) break;
         
            // draw the P line
            l->DrawLine( frame->GetXaxis()->GetXmin(), P, frame->GetXaxis()->GetXmax(), P );
         
            // draw the legend
            Float_t dx = frame->GetXaxis()->GetXmax() - frame->GetXaxis()->GetXmin();
            TLatex* text = new TLatex( frame->GetXaxis()->GetXmax() + dx*0.01, P, Form( "%i#sigma", Int_t(sigma) ) );
            text->SetTextColor( 12 );
            text->SetTextAlign( 12 );
            text->SetTextSize( tsize );
            text->AppendPad();
         }
      } 
      else if (estimator == kPValue) {
         TLine* l = new TLine;
         l->SetLineStyle( 2 );
         l->SetLineColor( 12 );
         for (Int_t i=1; i<4; i++) {
            Float_t sigma = i;
            Float_t P = TMath::Prob( sigma*sigma, 1 );
            if (P <= frame->GetYaxis()->GetXmin()) break;
         
            // draw the P line
            l->DrawLine( frame->GetXaxis()->GetXmin(), P, frame->GetXaxis()->GetXmax(), P );
         
            // draw the legend
            Float_t dx = frame->GetXaxis()->GetXmax() - frame->GetXaxis()->GetXmin();
            //Float_t dy = frame->GetMaximum() - frame->GetMinimum();
            TLatex* text = new TLatex( frame->GetXaxis()->GetXmax() + dx*0.01, P, Form( "%i#sigma", Int_t(sigma) ) );
            text->SetTextColor( 12 );
            text->SetTextAlign( 12 );
            text->SetTextSize( tsize );
            text->AppendPad();
         }
      }
      else {
         cout << "+++ Warning: cannot draw sigma indicators for estimator type: " << EstimatorName[estimator] << endl;
         return;
      }
   }
      
   void SetCombinationStyle() 
   {
      TStyle *CombinationStyle = gROOT->GetStyle("Combination");
      if(CombinationStyle!=0) {
         gROOT->SetStyle("Combination");
         return;
      }

      CombinationStyle = new TStyle(*gROOT->GetStyle("Plain")); // our style is based on Plain
      CombinationStyle->SetName("Combination");
      CombinationStyle->SetTitle("Combination style based on Plain with modifications define in CombinationGlob.C");
      gROOT->GetListOfStyles()->Add(CombinationStyle);
      gROOT->SetStyle("Combination");
 	
      CombinationStyle->SetLineStyleString( 5, "[52 12]" );
      CombinationStyle->SetLineStyleString( 6, "[22 12]" );
      CombinationStyle->SetLineStyleString( 7, "[22 10 7 10]" );

      // the pretty color palette of old
      CombinationStyle->SetPalette(1,0);

      // use plain black on white colors
      CombinationStyle->SetFrameBorderMode(0);
      CombinationStyle->SetCanvasBorderMode(0);
      CombinationStyle->SetPadBorderMode(0);
      CombinationStyle->SetPadColor(0);
      CombinationStyle->SetFillStyle(0);

      CombinationStyle->SetLegendBorderSize(0);

      // title properties
      // CombinationStyle->SetTitleW(.4);
      // CombinationStyle->SetTitleH(.10);
      // CombinationStyle->SetTitleY(.9);
      	
      //TColor::CreateColorWheel();	
      //TColor::CreateColorsGray();
      
      CombinationStyle->SetTitleFillColor(TColor::GetColorBright(33));
      if (!UsePaperStyle) {
         //CombinationStyle->SetFrameFillColor(TColor::GetColorBright(19));
         //CombinationStyle->SetCanvasColor(TColor::GetColorBright(21));
      }

      // set the paper & margin sizes
      CombinationStyle->SetPaperSize(20,26);
      CombinationStyle->SetPadTopMargin(0.10);
      CombinationStyle->SetPadRightMargin(0.05);
      CombinationStyle->SetPadBottomMargin(0.11);
      CombinationStyle->SetPadLeftMargin(0.12);

      // use bold lines and markers
      CombinationStyle->SetMarkerStyle(21);
      CombinationStyle->SetMarkerSize(0.3);
      CombinationStyle->SetHistLineWidth(1.85);
      CombinationStyle->SetLineStyleString(2,"[12 12]"); // postscript dashes

      // do not display any of the standard histogram decorations
      if (!UsePaperStyle) {
         CombinationStyle->SetOptTitle(0);
         //CombinationStyle->SetTitleH(0.052);
      }
      else 
         CombinationStyle->SetOptTitle(0);
      CombinationStyle->SetOptStat(0);
      CombinationStyle->SetOptFit(0);

      // put tick marks on top and RHS of plots
      CombinationStyle->SetPadTickX(1);
      CombinationStyle->SetPadTickY(1);
      return;
   }


   // set style and remove existing canvas'
   void Initialize( Bool_t useCombinationStyle = kTRUE )
   {
      // destroy canvas'
      TList * loc = (TList*)gROOT->GetListOfCanvases();
      TListIter itc(loc);
      TObject *o(0);
      while ((o = itc())) delete o;

      // set style
      if (!useCombinationStyle) {
         gROOT->SetStyle("Plain");
         gStyle->SetOptStat(0);
         return;
      }

      SetCombinationStyle();
   }


   // checks if file with name "fin" is already open, and if not opens one
   TFile* OpenFile( const TString& fin )
   {
      TFile* file = gDirectory->GetFile();
      if (file==0 || fin != file->GetName()) {
         if (file != 0) {
            gROOT->cd();
            file->Close();
         }
         cout << "--- Opening root file " << fin << " in read mode" << endl;
         file = TFile::Open( fin, "READ" );
      }
      else {
         file = gDirectory->GetFile();
      }

      file->cd();
      return file;
   }

   // used to create output file for canvas
   void imgconv( TCanvas* c, const TString & fname )
   {
      // return;
      if (NULL == c) {
         cout << "--- Error in CombinationGlob::imgconv: canvas is NULL" << endl;
      }
      else {
         // create directory if not existing
         TString f = fname;
         TString dir = f.Remove( f.Last( '/' ), f.Length() - f.Last( '/' ) );
         gSystem->mkdir( dir );

         TString pngName = fname + ".png";
         TString gifName = fname + ".gif";
         TString epsName = fname + ".eps";
         TString jpgName = fname + ".jpg";
         TString psName  = fname + ".ps";
         TString pdfName  = fname + ".pdf";
	 //TString CName  = fname + ".cxx";
         c->cd();
         // create eps (other option: c->Print( epsName ))
         c->Print(pngName, "png");
         c->Print(epsName, "eps");
         //c->Print(psName,  "ps");
         //c->Print(gifName, "gif");
         //c->Print(jpgName, "jpg");
         c->Print(pdfName, "pdf");
	 //c->Print(CName, "cxx");

         // c->Print(jpgName, "png");
         //          cout << "If you want to save the image as gif or png, please comment out "
         //               << "the corresponding lines (line no. 142+143) in combinationglob.C" << endl;
         //c->Print(gifName, "gif");
         
      }
   }
   
   void plot_logo( TString date, Float_t scale = 1.0, Float_t dx = 0, Float_t dy = 0, 
                   GPackage theGPackage = IsGSM, Bool_t onlyLogo = kFALSE )
   {
      if (UsePaperStyle) return;

      Int_t font = 40;

      Int_t color       = kRed;
      Float_t labelSize = 0.55;
      TString package    = "SM";
      TString package2   = "";

      if( theGPackage == IsG2HDM ){
         color     = kSpring-7;
         labelSize = 0.5;
         package2  = "2H";
         package   = "DM";
      }
      else if( theGPackage == IsCombination ){
         color     = kAzure+5;
         labelSize = 0.5;
         package2  = "";
         package   = "";  
      }
      else if( theGPackage == IsGOblique ){
         color     = kOrange+3;
         labelSize = 0.5;
         package2  = "B";
         package   = "SM";  
      }

      Float_t r = 15/3.6;

      gPad->Update();
      Float_t rpad = Float_t(gPad->GetWh()) / gPad->GetWw();
      r *= rpad;

      Float_t d = 0.95*gPad->GetTopMargin()*scale;
      // absolute coordinates
      Float_t x1R = 1 - gPad->GetRightMargin() - dx; 
      Float_t y1B = 1 - gPad->GetTopMargin()+.007 - dy; // we like the logo to sit a bit above the histo 
     
      Float_t x1L = x1R - d*r;
      Float_t y1T = y1B + d;
      if (y1T > 0.99) {
         cout << "Take " << 0.99 << " for y1T!!!" << endl;
         y1T = 0.99;
      }

      TLine *l[4];
      Int_t lineWidth = 1;

      if ( onlyLogo ){
         x1L = 0.01;
         x1R = 0.99;
         y1B = 0.01;
         y1T = 0.99;
         lineWidth = 2;
      }


      // correct x position (sometihng is still fishy here....)
      //dx += (x1R - x1L)*0.135*scale;
      
      TPad *p1 = new TPad("p1", "p1", x1L, y1B, x1L+(y1T-y1B)*rpad, y1T, color );
      p1->SetRightMargin(0);
      p1->SetBottomMargin(0);
      p1->SetLeftMargin(0);
      p1->SetTopMargin(0);
      p1->Draw();
      
      TPad *p2 = new TPad("p2", "p2", x1L+(y1T-y1B)*rpad, y1B, x1L+12.2/3.7*(y1T-y1B)*rpad, y1T, 
                          TColor::GetColor( "#E0EEEE" ) );
      p2->SetRightMargin(0);
      p2->SetBottomMargin(0);
      p2->SetLeftMargin(0);
      p2->SetTopMargin(0);
      p2->Draw();
      
      TPad *p3 = new TPad("p3", "p3", x1L+12.2/3.7*(y1T-y1B)*rpad, y1B, x1R, y1T, 0 );
      if( theGPackage != IsCombination ){
         p3->SetRightMargin(0);
         p3->SetBottomMargin(0);
         p3->SetLeftMargin(0);
         p3->SetTopMargin(0);
         p3->Draw();
      }

      if( date != "" ){
         TPad *p4 = new TPad("p4", "p4", x1R, y1B, x1R+1/8.*(x1R-x1L), y1T, 0 );
         p4->SetRightMargin(0);
         p4->SetBottomMargin(0);
         p4->SetLeftMargin(0);
         p4->SetTopMargin(0);
         p4->Draw();
         
         p4->cd();
         TLatex *text4 = new TLatex( 0.45, 0.5, date);
         text4->SetTextColor(1);
         text4->SetTextSize(0.6);
         text4->SetTextAlign(22);
         text4->SetTextFont(font);
         text4->SetTextAngle(270);
         text4->Draw();
         TLine *up = new TLine(0, 0, 0, 1 );
         up->SetLineWidth(lineWidth);
         up->Draw();
      } 
      


      p1->cd();
      TLatex *text1 = new TLatex( 0.47, 0.53, "G");
      text1->SetTextColor(0);
      text1->SetTextSize(1);
      text1->SetTextAlign(22);
      text1->SetTextFont(font);
      text1->Draw();
      l[0] = new TLine(0, 0, 0, 1 );
      l[1] = new TLine(0, 1, 1, 1 );
      l[2] = new TLine(1, 1, 1, 0 );
      l[3] = new TLine(1, 0, 0, 0 );
      l[0]->SetLineWidth(lineWidth);
      l[1]->SetLineWidth(lineWidth);
      l[2]->SetLineWidth(lineWidth);
      l[3]->SetLineWidth(lineWidth);
      l[0]->Draw();
      l[1]->Draw();
      l[2]->Draw();
      l[3]->Draw();

      p2->cd();
      TLatex *text2 = new TLatex( 0.50, 0.53, "fitter");
      text2->SetTextColor(1);
      text2->SetTextSize(1);
      text2->SetTextAlign(22);
      text2->SetTextFont(font);
      text2->Draw();
      l[0] = new TLine(0, 0, 0, 1 );
      l[1] = new TLine(0, 1, 1, 1 );
      l[2] = new TLine(1, 1, 1, 0 );
      l[3] = new TLine(1, 0, 0, 0 );
      l[0]->SetLineWidth(lineWidth);
      l[1]->SetLineWidth(lineWidth);
      l[2]->SetLineWidth(lineWidth);
      l[3]->SetLineWidth(lineWidth);
      l[0]->Draw();
      l[1]->Draw();
      l[2]->Draw();
      l[3]->Draw();
      if( theGPackage != IsCombination ){
         p3->cd();
         TLatex *text3 = new TLatex( 0.48, 0.3, package);
         text3->SetTextColor(color);
         text3->SetTextSize(labelSize);
         text3->SetTextAlign(22);
         text3->SetTextFont(font);
         text3->Draw();

         TLatex *text4 = new TLatex( 0.48, 0.75, package2);
         text4->SetTextColor(color);
         text4->SetTextSize(labelSize);
         text4->SetTextAlign(22);
         text4->SetTextFont(font);
         text4->Draw();
         
         l[0] = new TLine(0, 0, 0, 1 );
         l[1] = new TLine(0, 1, 1, 1 );
         l[2] = new TLine(1, 1, 1, 0 );
         l[3] = new TLine(1, 0, 0, 0 );
         l[0]->SetLineWidth(lineWidth);
         l[1]->SetLineWidth(lineWidth);
         l[2]->SetLineWidth(lineWidth);
         l[3]->SetLineWidth(lineWidth);
         l[0]->Draw();
         l[1]->Draw();
         l[2]->Draw();
         l[3]->Draw();      
      } 

   }

   
   void NormalizeHists( TH1* sig, TH1* bkg = 0 ) 
   {
      if (sig->GetSumw2N() == 0) sig->Sumw2();
      if (bkg != 0) if (bkg->GetSumw2N() == 0) bkg->Sumw2();
   
      Float_t dx = (sig->GetXaxis()->GetXmax() - sig->GetXaxis()->GetXmin())/sig->GetNbinsX();
      sig->Scale( 1.0/sig->GetSumOfWeights()/dx );
      if (bkg != 0) bkg->Scale( 1.0/bkg->GetSumOfWeights()/dx );      
   }      

   // the following are tools to help handling different methods and titles
   void GetMethodName( TString & name, TKey * mkey ) {
      if (mkey==0) return;
      name = mkey->GetName();
      name.ReplaceAll("Method_","");
   }

   void GetMethodTitle( TString & name, TKey * ikey ) {
      if (ikey==0) return;
      name = ikey->GetName();
   }

   void GetMethodName( TString & name, TDirectory * mdir ) {
      if (mdir==0) return;
      name = mdir->GetName();
      name.ReplaceAll("Method_","");
   }

   void GetMethodTitle( TString & name, TDirectory * idir ) {
      if (idir==0) return;
      name = idir->GetName();
   }

   TKey *NextKey( TIter & keyIter, TString className) {
      TKey *key=(TKey *)keyIter.Next();
      TKey *rkey=0;
      Bool_t loop=(key!=0);
      //
      while (loop) {
         TClass *cl = gROOT->GetClass(key->GetClassName());
         if (cl->InheritsFrom(className.Data())) {
            loop = kFALSE;
            rkey = key;
         } else {
            key = (TKey *)keyIter.Next();
            if (key==0) loop = kFALSE;
         }
      }
      return rkey;
   }

   UInt_t GetListOfKeys( TList & keys, TString inherits, TDirectory *dir=0 )
   {
      // get a list of keys with a given inheritance
      // the list contains TKey objects
      if (dir==0) dir = gDirectory;
      TIter mnext(dir->GetListOfKeys());
      TKey *mkey;
      keys.Clear();
      keys.SetOwner(kFALSE);
      UInt_t ni=0;
      while ((mkey = (TKey*)mnext())) {
         // make sure, that we only look at TDirectory with name Method_<xxx>
         TClass *cl = gROOT->GetClass(mkey->GetClassName());
         if (cl->InheritsFrom(inherits)) {
            keys.Add(mkey);
            ni++;
         }
      }
      return ni;
   }

   TKey *FindMethod( TString name, TDirectory *dir=0 )
   {
      // find the key for a method
      if (dir==0) dir = gDirectory;
      TIter mnext(dir->GetListOfKeys());
      TKey *mkey;
      TKey *retkey=0;
      Bool_t loop=kTRUE;
      while (loop) {
         mkey = (TKey*)mnext();
         if (mkey==0) {
            loop = kFALSE;
         } else {
            TString clname = mkey->GetClassName();
            TClass *cl = gROOT->GetClass(clname);
            if (cl->InheritsFrom("TDirectory")) {
               TString mname = mkey->GetName(); // method name
               TString tname = "Method_"+name;  // target name
               if (mname==tname) { // target found!
                  loop = kFALSE;
                  retkey = mkey;
               }
            }
         }
      }
      return retkey;
   }

   UInt_t GetListOfMethods( TList & methods, TDirectory *dir=0 )
   {
      // get a list of methods
      // the list contains TKey objects
      if (dir==0) dir = gDirectory;
      TIter mnext(dir->GetListOfKeys());
      TKey *mkey;
      methods.Clear();
      methods.SetOwner(kFALSE);
      UInt_t ni=0;
      while ((mkey = (TKey*)mnext())) {
         // make sure, that we only look at TDirectory with name Method_<xxx>
         TString name = mkey->GetClassName();
         TClass *cl = gROOT->GetClass(name);
         if (cl->InheritsFrom("TDirectory")) {
            if (TString(mkey->GetName()).BeginsWith("Method_")) {
               methods.Add(mkey);
               ni++;
            }
         }
      }
      cout << "--- Found " << ni << " methods(s)" << endl;
      return ni;
   }


   UInt_t GetListOfTitles( TDirectory *rfdir, TList &titles )
   {
      // get a list of titles (i.e TDirectory) given a method dir
      UInt_t ni=0;
      if (rfdir==0) return 0;
      TList *keys = rfdir->GetListOfKeys();
      if (keys==0) {
         cout << "Directory '" << rfdir->GetName() << "' contains no keys" << endl;
         return 0;
      }
      //
      TIter rfnext(rfdir->GetListOfKeys());
      TKey *rfkey;
      titles.Clear();
      titles.SetOwner(kFALSE);
      while ((rfkey = (TKey*)rfnext())) {
         // make sure, that we only look at histograms
         TClass *cl = gROOT->GetClass(rfkey->GetClassName());
         if (cl->InheritsFrom("TDirectory")) {
            titles.Add(rfkey);
            ni++;
         }
      }
      cout << "--- Found " << ni << " instance(s) of the method " << rfdir->GetName() << endl;
      return ni;
   }

   UInt_t GetListOfTitles( TString& methodName, TList& titles, TDirectory* dir=0 )
   {
      // get the list of all titles for a given method
      // if the input dir is 0, gDirectory is used
      // returns a list of keys
      UInt_t ni=0;
      if (dir==0) dir = gDirectory;
      TDirectory* rfdir = (TDirectory*)dir->Get( methodName );
      if (rfdir==0) {
         cout << "Could not locate directory '" << methodName << endl;
         return 0;
      }

      return GetListOfTitles( rfdir, titles );

      TList *keys = rfdir->GetListOfKeys();
      if (keys==0) {
         cout << "Directory '" << methodName << "' contains no keys" << endl;
         return 0;
      }
      //
      TIter rfnext(rfdir->GetListOfKeys());
      TKey *rfkey;
      titles.Clear();
      titles.SetOwner(kFALSE);
      while ((rfkey = (TKey*)rfnext())) {
         // make sure, that we only look at histograms
         TClass *cl = gROOT->GetClass(rfkey->GetClassName());
         if (cl->InheritsFrom("TDirectory")) {
            titles.Add(rfkey);
            ni++;
         }
      }
      cout << "--- Found " << ni << " instance(s) of the method " << methodName << endl;
      return ni;
   }

   void SetBorders( TH2 &hist, Double_t val=0 )
   {
      int num = hist.GetNbinsX();
      for(int i=1; i <=num ; i++){
         hist.SetBinContent(1,i, val);
         hist.SetBinContent(i,1,val);
         hist.SetBinContent(num,i,val);
         hist.SetBinContent(i,num,val);
      } 
   }
}

#endif

/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Namespace: ValidationUtils                                                     *
 *                                                                                *
 * Description:                                                                   *
 *      Implementation (see header for description)                               *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva, Switzerland                               *
 *                                                                                *
 * See corresponding .h file for author and license information                   *
 **********************************************************************************/

#include "ValidationUtils.h"
#include "Significance.h"
#include <TFile.h>


//________________________________________________________________________________________________
void ValidationUtils::Horizontal( TH1 *h, Int_t nbin, Bool_t kLINE, Int_t color, float yWidthScaleUp, float yWidthScaleDown)
{
   // Draw histogram h horizontaly with bars
   TAxis *axis   = h->GetXaxis();
   Double_t dy;
   Double_t x1,y1,x2,y2;
   
   Int_t i = nbin;
   dy = axis->GetBinWidth(i);
   x1 = 0;
   y1 = axis->GetBinCenter(i)-yWidthScaleDown*dy+1;
   x2 = h->GetBinContent(i);
   y2 = axis->GetBinCenter(i)+yWidthScaleUp*dy+1;

   Double_t x[5] = { x1, x1, x2, x2, x1 };
   Double_t y[5] = { y1, y2, y2, y1, y1 };
   TGraph *box = new TGraph(5, x, y);
   box->SetFillColor( color );
   box->SetLineColor( color );
   if ( kLINE ) box->Draw(); 
   else         box->Draw("F");   
}


//________________________________________________________________________________________________
void ValidationUtils::HorizontalElMu( TH1 *h, Int_t nbin, Bool_t /*kLINE*/, Int_t color, Int_t /*color2*/, float yWidthScale )
{
   // Draw histogram h horizontaly with bars
   TAxis *axis   = h->GetXaxis();
   Double_t dy;
   Double_t x1,y1,x2,y2;
   
   Int_t i = nbin;
   dy = axis->GetBinWidth(i);
   x1 = 0;
   y1 = axis->GetBinCenter(i)-yWidthScale*dy+1;
   x2 = h->GetBinContent(i);
   y2 = axis->GetBinCenter(i)+yWidthScale*dy+1;

   Double_t x[5] = { x1, x1, x2, x2, x1 };
   Double_t y[5] = { y1, y2, y2, y1, y1 };
   TGraph *box = new TGraph(5, x, y);
   box->SetFillColor( color );
   box->SetLineColor( color );
   box->Draw("F"); 

}


//________________________________________________________________________________________________
void ValidationUtils::SetCombinationStyle() 
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
  
  CombinationStyle->SetTitleFillColor(TColor::GetColorBright(33));
  
  // set the paper & margin sizes
  CombinationStyle->SetPaperSize(20,26);
  CombinationStyle->SetPadTopMargin(0.10);
  CombinationStyle->SetPadRightMargin(0.05);
  CombinationStyle->SetPadBottomMargin(0.11);
  CombinationStyle->SetPadLeftMargin(0.12);
  
  // use bold lines and markers
  CombinationStyle->SetMarkerStyle(21);
  CombinationStyle->SetMarkerSize(0.3);
  CombinationStyle->SetHistLineWidth( static_cast<Width_t>(1.85) );
  CombinationStyle->SetLineStyleString(2,"[12 12]"); // postscript dashes
  
  // do not display any of the standard histogram decorations
  CombinationStyle->SetOptTitle(0);
  CombinationStyle->SetOptStat(0);
  CombinationStyle->SetOptFit(0);
  
  // put tick marks on top and RHS of plots
  CombinationStyle->SetPadTickX(1);
  CombinationStyle->SetPadTickY(1);

  CombinationStyle->SetHatchesLineWidth(2);

  return;
}


//________________________________________________________________________________________________
/// set style and remove existing canvas'
void ValidationUtils::Initialize( Bool_t useCombinationStyle )
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


//________________________________________________________________________________________________
/// set frame styles
void ValidationUtils::SetFrameStyle2D( TH1* frame, Float_t scale )
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


//________________________________________________________________________________________________
void ValidationUtils::PullPlot3(XtraValues* inValsEl, XtraValues* inValsMu, const TString& outFileNamePrefix)
{
  // set style and remove existing canvas'
   ValidationUtils::Initialize();

   const Int_t Npar = inValsEl->size();
   

   static Int_t c_DarkGreen     = TColor::GetColor( "#115000" );
   static Int_t c_VDarkGreen    = TColor::GetColor( "#114400" );
   static Int_t c_LightBlue     = TColor::GetColor( "#66aaff" );
   static Int_t c_DarkBlue      = TColor::GetColor( "#0000bb" );

   //static Int_t c_LightRed      = TColor::GetColor( "#ff3333" );
   //static Int_t c_DarkRed       = TColor::GetColor( "#800000" );
   static Int_t c_LightYellow   = TColor::GetColor( "#ffff00" );
   //static Int_t c_VLightYellow  = TColor::GetColor( "#ffffe0" );
   //static Int_t c_DarkYellow    = TColor::GetColor( "#ffd700" );
   static Int_t c_VDarkYellow   = TColor::GetColor( "#ffa500" );


   Int_t    colEl = c_VDarkGreen;
   Int_t    colElL = c_DarkGreen;
   Int_t    colMu = c_DarkBlue;
   Int_t    colMuL = c_LightBlue;
   Int_t    colEMu = c_VDarkYellow;
   Int_t    colEMuL = c_LightYellow;
   

   // ----------- now we can start the plotting -----------------------------

   // define canvas
   TCanvas* c = new TCanvas( "c"+outFileNamePrefix, "Pull plot", 0, 0, 400, 700 );   

   // Draw frame
   Double_t offset = 0.5;
   TH2F *frame = new TH2F( "frame"+outFileNamePrefix, "Pull plot", 
                           1, -3.0, 3.0, Npar+1, -offset, Float_t(Npar)+offset );

   ValidationUtils::SetFrameStyle2D( frame, 1.0 ); // the size (scale) is 1.0
   frame->SetLabelFont(42,"X");
   frame->SetTitleFont(42,"X");
   frame->SetLabelFont(42,"Y");
   frame->SetTitleFont(42,"Y");

   // new margins
   TString XTitleSpaces="";
   if(outFileNamePrefix.Contains("_MEff") or outFileNamePrefix.Contains("_bTag")){ 
     c->SetLeftMargin  ( 0.38 ); 
     XTitleSpaces="            ";
   }
   else{ 
     c->SetLeftMargin  ( 0.26 ); 
     XTitleSpaces="                  ";
   }
   c->SetTopMargin   ( 0.12 );
   c->SetRightMargin ( 0.05 );
   c->SetBottomMargin( 0.08 );
   c->SetGridx();
     
   // reduce size of title box
   gStyle->SetTitleW(0.60);          

   frame->SetLineColor(0);
   frame->SetTickLength(0,"Y");
   frame->SetLabelSize(0.034, "X");
   frame->SetXTitle( "(n_{obs} - n_{pred}) / #sigma_{tot}"+XTitleSpaces );
   frame->SetLabelOffset( 0.001, "X" );
   frame->SetTitleOffset( 0.85 , "X");
   frame->SetTitleSize( 0.046, "X" );
   frame->GetYaxis()->CenterLabels( 1 );
   frame->GetYaxis()->SetNdivisions( frame->GetNbinsY()+10, 1 );

   //Double_t y[Npar];   
   frame->GetYaxis()->SetBinLabel( 1, "" ); // no labels
   //for (Int_t i=0; i<Npar; i++) y[i] = i + offset; 

   frame->Draw();   

   Float_t xLeft=0.4;
   TLatex *atlasLabel = new TLatex();
   atlasLabel->SetNDC();
   atlasLabel->SetTextFont( 72 );
   atlasLabel->SetTextColor( 1 );
   atlasLabel->SetTextSize( 0.05 );
   atlasLabel->DrawLatex(xLeft,0.97, "ATLAS");
   atlasLabel->AppendPad();
   
   TLatex *prel = new TLatex();
   prel->SetNDC();
   prel->SetTextFont( 42 );
   prel->SetTextColor( 1 );
   prel->SetTextSize( 0.05 );
   //prel->DrawLatex(xLeft+0.17, 0.97, "Preliminary");
   prel->DrawLatex(xLeft+0.17, 0.97, "internal");
   prel->AppendPad();

   TLine* line = new TLine;
   line->DrawLine( 0, frame->GetYaxis()->GetXmin(), 0, frame->GetYaxis()->GetXmax() );

   // axis labels (parameters)
   TLatex* text = new TLatex;
   text->SetTextFont(42);
   text->SetTextSize( frame->GetLabelSize( "Y" )*0.55 );
   Float_t yy = frame->GetYaxis()->GetXmin();
   Float_t dy = (frame->GetYaxis()->GetXmax() - frame->GetYaxis()->GetXmin())/Float_t(Npar+1);
   //Float_t dx = frame->GetXaxis()->GetXmax() - frame->GetXaxis()->GetXmin();
   Float_t x  = frame->GetXaxis()->GetXmin() - 5.4 + (5-3.5);
   
   // inputs   
   x += 1.5;

   for (Int_t i=Npar-1; i>=0; i--) {
      text->SetTextAlign( 32 );
      text->SetTextSize( 0.035 );
      text->DrawLatex( x+2.2, yy - (i-Npar)*dy, inValsEl->m_reg_names.at(i) );
   }


   //The boxes
   TH1F *hPullEl = new TH1F( "hPullEl"+outFileNamePrefix, "hPullEl", Npar, -1, Npar-1 );
   hPullEl->SetLineColor(colEl);
   hPullEl->SetFillColor(colElL);
   TH1F *hPullMu = new TH1F( "hPullMu"+outFileNamePrefix, "hPullMu", Npar, -1, Npar-1 );
   hPullMu->SetLineColor(colMu);
   hPullMu->SetFillColor(colMuL);
   TH1F *hPullElMu = new TH1F( "hPullElMu"+outFileNamePrefix, "hPullElMu", Npar, -1, Npar-1 );
   hPullElMu->SetLineColor(colEMu);
   hPullElMu->SetFillColor(colEMuL);
   //Fill values - electron channel
   for (Int_t i=0; i<Npar; i++) {
      Float_t delta = inValsEl->m_nObs.at(i) - inValsEl->m_nPred.at(i);
      Float_t err=inValsEl->m_Delta_eTot.at(i);
      Float_t pull = 0;
      if(fabs(err)>0){ pull=delta/err; }
      hPullEl->SetBinContent( Npar-i, pull );
   }
   //Fill values -- muon channel
   for (Int_t i=0; i<Npar; i++) {
      Float_t delta = inValsMu->m_nObs.at(i) - inValsMu->m_nPred.at(i);
      Float_t err=inValsMu->m_Delta_eTot.at(i);
      Float_t pull = 0;
      if(fabs(err)>0){ pull=delta/err; }
      hPullMu->SetBinContent( Npar-i, pull );
   }
   //Draw boxes
   for (Int_t i=0; i<Npar; i++) {
     if(inValsEl->m_reg_names.at(i).Contains("EM")){
       Horizontal( hPullEl, Npar-i, kFALSE, colEMuL, 0.14, 0.14);
       Horizontal( hPullEl, Npar-i, kTRUE, colEMu, 0.14, 0.14);
     }
     else{
       Horizontal( hPullEl, Npar-i, kFALSE, hPullEl->GetFillColor(), 0.28, 0.0);
       Horizontal( hPullEl, Npar-i, kTRUE, hPullEl->GetLineColor(), 0.28, 0.0);
       Horizontal( hPullMu, Npar-i, kFALSE, hPullMu->GetFillColor(), 0.0, 0.28);
       Horizontal( hPullMu, Npar-i, kTRUE, hPullMu->GetLineColor(), 0.0, 0.28);
     }
   }

   cout << " hPullElMu->GetNEntries() = " << hPullElMu->GetEntries() << endl;
   cout << " hPullEl->GetNEntries() = " << hPullEl->GetEntries() << endl;
   cout << " hPullMu->GetNEntries() = " << hPullMu->GetEntries() << endl;

   TLegend* leg = new TLegend(xLeft-0.07,0.885,xLeft+0.43,0.96,"");
   leg->SetFillStyle(0);
   leg->SetBorderSize(0);
   leg->SetTextFont( 42 );
   leg->SetTextSize( 0.04 );

   leg->AddEntry(hPullEl, "Electron Channel", "f");
   leg->AddEntry(hPullMu, "Muon Channel", "f");
   leg->AddEntry(hPullElMu, "Electron-Muon Channel", "f");
   leg->Draw();
   
   // final update of canvas
   c->Update();

   c->Print(outFileNamePrefix+".pdf");
   c->Print(outFileNamePrefix+".eps");
   cout<<"mv "<<outFileNamePrefix<<".pdf ~/www/data/."<<endl;
   return;
}


//________________________________________________________________________________________________
void ValidationUtils::PullPlot5(XtraValues* inValsEl, XtraValues* inValsMu, XtraValues* inValsEM, const TString& outFileNamePrefix)
{
  // set style and remove existing canvas'
   ValidationUtils::Initialize();

   const Int_t Npar = inValsEM->size();
   // if (Npar==0) Npar = inValsEM->size();

   static Int_t c_DarkGreen     = TColor::GetColor( "#115000" );
   static Int_t c_VDarkGreen    = TColor::GetColor( "#114400" );
   static Int_t c_LightBlue     = TColor::GetColor( "#66aaff" );
   static Int_t c_DarkBlue      = TColor::GetColor( "#0000bb" );

   //static Int_t c_LightRed      = TColor::GetColor( "#ff3333" );
   //static Int_t c_DarkRed       = TColor::GetColor( "#800000" );
   //static Int_t c_LightYellow   = TColor::GetColor( "#ffff00" );
   //static Int_t c_VLightYellow  = TColor::GetColor( "#ffffe0" );
   //static Int_t c_DarkYellow    = TColor::GetColor( "#ffd700" );
   static Int_t c_VDarkYellow   = TColor::GetColor( "#ffa500" );


   Int_t    colEl = c_VDarkGreen;
   Int_t    colElL = c_DarkGreen;
   Int_t    colMu = c_DarkBlue;
   Int_t    colMuL = c_LightBlue;
   Int_t    colEMu = c_VDarkYellow;
   //Int_t    colEMuL = c_LightYellow;
   

   // ----------- now we can start the plotting -----------------------------

   // define canvas
   TCanvas* c = new TCanvas( "c"+outFileNamePrefix, "Pull plot", 0, 0, 400, 700 );   

   // Draw frame
   Double_t offset = 0.5;
   TH2F *frame = new TH2F( "frame"+outFileNamePrefix, "Pull plot", 
                           1, -3.0, 3.0, Npar+1, -offset, Float_t(Npar)+offset );

   ValidationUtils::SetFrameStyle2D( frame, 1.0 ); // the size (scale) is 1.0
   frame->SetLabelFont(42,"X");
   frame->SetTitleFont(42,"X");
   frame->SetLabelFont(42,"Y");
   frame->SetTitleFont(42,"Y");

   // new margins
   TString XTitleSpaces="";
   if(outFileNamePrefix.Contains("_MEff") or outFileNamePrefix.Contains("_bTag")){ 
     c->SetLeftMargin  ( 0.38 ); 
     XTitleSpaces="            ";
   }
   else{ 
     c->SetLeftMargin  ( 0.26 ); 
     XTitleSpaces="                  ";
   }
   c->SetTopMargin   ( 0.12 );
   c->SetRightMargin ( 0.05 );
   c->SetBottomMargin( 0.08 );
   c->SetGridx();
     
   // reduce size of title box
   gStyle->SetTitleW(0.60);          

   frame->SetLineColor(0);
   frame->SetTickLength(0,"Y");
   frame->SetLabelSize(0.034, "X");
   frame->SetXTitle( "(n_{obs} - n_{pred}) / #sigma_{tot}"+XTitleSpaces );
   frame->SetLabelOffset( 0.001, "X" );
   frame->SetTitleOffset( 0.85 , "X");
   frame->SetTitleSize( 0.046, "X" );
   frame->GetYaxis()->CenterLabels( 1 );
   frame->GetYaxis()->SetNdivisions( frame->GetNbinsY()+10, 1 );

   //Double_t y[Npar];   
   frame->GetYaxis()->SetBinLabel( 1, "" ); // no labels
   //for (Int_t i=0; i<Npar; i++) y[i] = i + offset; 

   frame->Draw();   

   Float_t xLeft=0.4;
   TLatex *atlasLabel = new TLatex();
   atlasLabel->SetNDC();
   atlasLabel->SetTextFont( 72 );
   atlasLabel->SetTextColor( 1 );
   atlasLabel->SetTextSize( 0.05 );
   atlasLabel->DrawLatex(xLeft,0.97, "ATLAS");
   atlasLabel->AppendPad();
   
   TLatex *prel = new TLatex();
   prel->SetNDC();
   prel->SetTextFont( 42 );
   prel->SetTextColor( 1 );
   prel->SetTextSize( 0.05 );
   //prel->DrawLatex(xLeft+0.17, 0.97, "Preliminary");
   prel->DrawLatex(xLeft+0.17, 0.97, "internal");
   prel->AppendPad();

   TLine* line = new TLine;
   line->DrawLine( 0, frame->GetYaxis()->GetXmin(), 0, frame->GetYaxis()->GetXmax() );

   // axis labels (parameters)
   TLatex* text = new TLatex;
   text->SetTextFont(42);
   text->SetTextSize( frame->GetLabelSize( "Y" )*0.55 );
   Float_t yy = frame->GetYaxis()->GetXmin();
   Float_t dy = (frame->GetYaxis()->GetXmax() - frame->GetYaxis()->GetXmin())/Float_t(Npar+1);
   //Float_t dx = frame->GetXaxis()->GetXmax() - frame->GetXaxis()->GetXmin();
   Float_t x  = frame->GetXaxis()->GetXmin() - 5.4 + (5-3.5);
   
   // inputs   
   x += 1.5;

   for (Int_t i=Npar-1; i>=0; i--) {
      text->SetTextAlign( 32 );
      text->SetTextSize( 0.035 );
      text->DrawLatex( x+2.2, yy - (i-Npar)*dy, inValsEM->m_reg_names.at(i) );
   }


   //The boxes
   TH1F *hPullEl = new TH1F( "hPullEl"+outFileNamePrefix, "hPullEl", Npar, -1, Npar-1 );
   hPullEl->SetLineColor(colEl);
   hPullEl->SetFillColor(colElL);
   TH1F *hPullMu = new TH1F( "hPullMu"+outFileNamePrefix, "hPullMu", Npar, -1, Npar-1 );
   hPullMu->SetLineColor(colMu);
   hPullMu->SetFillColor(colMuL);
   TH1F *hPullElMu = new TH1F( "hPullElMu"+outFileNamePrefix, "hPullElMu", Npar, -1, Npar-1 );
   hPullElMu->SetLineColor(colEMu);
   hPullElMu->SetFillColor(colEMu);

   //Fill values - electron channel
   for (Int_t i=0; i<inValsEl->size(); i++) {
      Float_t delta = inValsEl->m_nObs.at(i) - inValsEl->m_nPred.at(i);
      Float_t err=inValsEl->m_Delta_eTot.at(i);
      Float_t pull = 0;
      if(fabs(err)>0){ pull=delta/err; }
      hPullEl->SetBinContent( Npar-i, pull );
   }
   //Fill values -- muon channel
   for (Int_t i=0; i<inValsMu->size(); i++) {
      Float_t delta = inValsMu->m_nObs.at(i) - inValsMu->m_nPred.at(i);
      Float_t err=inValsMu->m_Delta_eTot.at(i);
      Float_t pull = 0;
      if(fabs(err)>0){ pull=delta/err; }
      hPullMu->SetBinContent( Npar-i, pull );
   }
   //Fill values -- electron+muon channel
   for (Int_t i=0; i<Npar; i++) {
      Float_t delta = inValsEM->m_nObs.at(i) - inValsEM->m_nPred.at(i);
      Float_t err=inValsEM->m_Delta_eTot.at(i);
      Float_t pull = 0;
      if(fabs(err)>0){ pull=delta/err; }
      //   cout << endl <<" i = " <<i << " pull = " << pull ;
      hPullElMu->SetBinContent( Npar-i, pull );
   }   

   //Draw boxes   
   for (Int_t i=0; i<Npar; i++) {
     HorizontalElMu( hPullElMu, Npar-i, kFALSE, colEMu, 0.14, 0.14);
   }

   TLegend* leg = new TLegend(xLeft-0.07,0.885,xLeft+0.43,0.96,"");
   leg->SetFillStyle(0);
   leg->SetBorderSize(0);
   leg->SetTextFont( 42 );
   leg->SetTextSize( 0.04 );

   //leg->AddEntry(hPullEl, "Electron Channel", "f");
   //leg->AddEntry(hPullMu, "Muon Channel", "f");
   leg->AddEntry(hPullElMu, "Electron+Muon Channel", "f");
   leg->Draw();
   
   // final update of canvas
   c->Update();

   c->Print(outFileNamePrefix+".pdf");
   c->Print(outFileNamePrefix+".eps");
   cout<<"mv "<<outFileNamePrefix<<".pdf ~/www/data/."<<endl;
   return;
}


//________________________________________________________________________________________________
void ValidationUtils::PullPlot4(XtraValues* inVals,const TString& outFileNamePrefix)
{
  // set style and remove existing canvas'
   ValidationUtils::Initialize();
 
   const Int_t Npar = inVals->size();
   
   static Int_t c_DarkGreen     = TColor::GetColor( "#115000" );
   static Int_t c_VDarkGreen    = TColor::GetColor( "#114400" );

   Int_t    col = c_VDarkGreen;
   Int_t    colL = c_DarkGreen;
  
   // ----------- now we can start the plotting -----------------------------
   // define canvas
   TCanvas* c = new TCanvas( "c"+outFileNamePrefix, "Results of the global electroweak fit", 0, 0, 420, 700 );   

   // Draw frame
   Double_t offset = 0.5;
   TH2F *frame = new TH2F( "frame"+outFileNamePrefix, "Results of the global SM fit", 
                           1, -3.0, 3.0, Npar+1, -offset, Float_t(Npar)+offset );

   ValidationUtils::SetFrameStyle2D( frame, 1.0 ); // the size (scale) is 1.0
   frame->SetLabelFont(42,"X");
   frame->SetTitleFont(42,"X");
   frame->SetLabelFont(42,"Y");
   frame->SetTitleFont(42,"Y");
 
   // new margins
   TString XTitleSpaces="";
   if(outFileNamePrefix.Contains("_after") or outFileNamePrefix.Contains("_before")){ 
     c->SetLeftMargin  ( 0.43 ); 
     XTitleSpaces="            ";
   }
   else{ 
     c->SetLeftMargin  ( 0.26 ); 
     XTitleSpaces="                  ";
   }
   c->SetTopMargin   ( 0.12 );
   c->SetRightMargin ( 0.05 );
   c->SetBottomMargin( 0.08 );
   c->SetGridx();
 
   // reduce size of title box
   gStyle->SetTitleW(0.60);          

   frame->SetLineColor(0);
   frame->SetTickLength(0,"Y");
   frame->SetLabelSize(0.03, "X");
   //frame->SetXTitle( "(n_{obs} - n_{pred}) / #sigma_{tot}"+XTitleSpaces );
   frame->SetXTitle( "discovery significance"+XTitleSpaces );


   if(outFileNamePrefix.Contains("mu")){ 
     frame->SetXTitle( "(#mu_{afterFit} - #mu_{beforeFit}) / #sigma_{#mu_{afterFit}}"+XTitleSpaces );
     //frame->SetXTitle( "(#mu_{afterFit} - #mu_{beforeFit}) / #sigma_{#mu_{beforeFit}}"+XTitleSpaces );
   }
   frame->SetLabelOffset( 0.001, "X" );
   frame->SetTitleOffset( 0.85 , "X");
   frame->SetTitleSize( 0.04, "X" );
   frame->GetYaxis()->CenterLabels( 1 );
   frame->GetYaxis()->SetNdivisions( frame->GetNbinsY()+10, 1 );

   //Double_t y[Npar];   
   frame->GetYaxis()->SetBinLabel( 1, "" ); // no labels
   //for (Int_t i=0; i<Npar; i++) y[i] = i + offset; 

   frame->Draw();   
 
   Float_t xLeft=0.4;
   TLatex *atlasLabel = new TLatex();
   atlasLabel->SetNDC();
   atlasLabel->SetTextFont( 72 );
   atlasLabel->SetTextColor( 1 );
   atlasLabel->SetTextSize( 0.05 );
   atlasLabel->DrawLatex(xLeft,0.97, "ATLAS");
   atlasLabel->AppendPad();
   
   TLatex *prel = new TLatex();
   prel->SetNDC();
   prel->SetTextFont( 42 );
   prel->SetTextColor( 1 );
   prel->SetTextSize( 0.05 );
   //prel->DrawLatex(xLeft+0.17, 0.97, "Preliminary");
   prel->DrawLatex(xLeft+0.17, 0.97, "Internal");
   prel->AppendPad();

   TLine* line = new TLine;
   line->DrawLine( 0, frame->GetYaxis()->GetXmin(), 0, frame->GetYaxis()->GetXmax() );

   // axis labels (parameters)
   TLatex* text = new TLatex;
   text->SetTextFont(42);
   text->SetTextSize( frame->GetLabelSize( "Y" )*0.55 );
   Float_t yy = frame->GetYaxis()->GetXmin();
   Float_t dy = (frame->GetYaxis()->GetXmax() - frame->GetYaxis()->GetXmin())/Float_t(Npar+1);
   //Float_t dx = frame->GetXaxis()->GetXmax() - frame->GetXaxis()->GetXmin();
   Float_t x  = frame->GetXaxis()->GetXmin() - 5.4 + (5-3.5);
   
   // inputs   
   x += 1.5;
  
   for (Int_t i=Npar-1; i>=0; i--) {
      text->SetTextAlign( 32 );
      text->SetTextSize( 0.035 );
      text->DrawLatex( x+2.2, yy - (i-Npar)*dy, inVals->m_reg_names.at(i) );
   }

 
   //The boxes
   TH1F *hPull = new TH1F( "hPull"+outFileNamePrefix, "hPull", Npar, -1, Npar-1 );
   hPull->SetLineColor(col);
   hPull->SetFillColor(colL);

   std::cout<<"Npar="<<Npar<<std::endl;

   //Fill values 
   for (Int_t i=0; i<Npar; i++) {
      Float_t delta = inVals->m_nObs.at(i) - inVals->m_nPred.at(i);
      Float_t err=inVals->m_Delta_eTot.at(i);
      Float_t pull = StatTools::GetNSigma( inVals->m_nObs.at(i), inVals->m_nPred.at(i), inVals->m_nPred_eFit.at(i) );
      std::cout<<"i="<<i<<"  delta="<<delta;
      std::cout<<"  err="<<err;

      //if(fabs(err)>0){ pull=delta/err;      std::cout<<"  pull="<<pull<<std::endl; }

      if ( delta<0 ) { pull *= -1.0; }  

      hPull->SetBinContent( Npar-i, pull );
    
   }

 
   //Draw boxes
   for (Int_t i=0; i<Npar; i++) {
     Int_t ccll = 0;
     if(outFileNamePrefix.Contains("_after") and outFileNamePrefix.Contains("_before")){ 
       
       if(i==0 || i==1) ccll =2;
       if(i==2 || i==3) ccll =3;
       if(i==4 || i==5) ccll =4;
       if(i==6 || i==7) ccll =5;
       if(i==8 || i==9) ccll =6;
       if(i==10 || i==11) ccll =7;
       if(i==12 || i==13) ccll =8;
       if(i==14 || i==15) ccll =9;
       if(i==16 || i==17) ccll =38;
       if(i==18 || i==19) ccll =39;
       if(i==20 || i==21) ccll =12;
       if(i==22 || i==23) ccll =41;
       if(i==24 || i==25) ccll =42;
       if(i==26 || i==27) ccll =36;
       if(i==28 || i==29) ccll =44;
       if(i==30 || i==31) ccll =30;
       if(i==32 || i==33) ccll =46;
       
     }
     else{
       if(i<=7) 
	 { ccll = i+2;} //2-9
       else
	 { ccll = i+30;} //38-46
       
       if (ccll == 40)   ccll = 12;
       if (ccll == 43)   ccll = 36;
       if (ccll == 45)   ccll = 30;
     }
     Horizontal( hPull, Npar-i, kFALSE,ccll , 0.28, 0.0);
     Horizontal( hPull, Npar-i, kTRUE, ccll, 0.28, 0.0);
   
   }

   TLegend* leg = new TLegend(xLeft,0.885,xLeft+0.4,0.96,"");
   leg->SetFillStyle(0);
   leg->SetBorderSize(0);
   leg->SetTextFont( 42 );
   leg->SetTextSize( 0.05 );

   //  leg->AddEntry(hPull, "Soft Lepton Channel", "f");
   // leg->SetHeader("Soft Lepton Channel");   

   if(outFileNamePrefix.Contains("CR") )   leg->SetHeader("Control Region");   
   if(outFileNamePrefix.Contains("VR") )   leg->SetHeader("Validation Region"); 

   if(outFileNamePrefix.Contains("WZ") )   leg->SetHeader("#mu_{WZ}: W(Z)+jets yield");   
   if(outFileNamePrefix.Contains("Top") )   leg->SetHeader("#mu_{Top}: ttbar yield"); 

   leg->Draw();
   
   // final update of canvas
   c->Update();

   c->Print(outFileNamePrefix+".pdf");
   c->Print(outFileNamePrefix+".eps");
   c->Print(outFileNamePrefix+".root");
 

   //  cout<<"mv "<<outFileNamePrefix<<".pdf ~/www/data/."<<endl;
   return;
}



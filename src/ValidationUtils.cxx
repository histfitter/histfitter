#include "ValidationUtils.h"


void ValidationUtils::Horizontal( TH1 *h, Int_t nbin, Bool_t kLINE, Int_t color, float yWidthScale )
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
   if ( kLINE ) box->Draw(); 
   else         box->Draw("F");   
}

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
  return;
}


// set style and remove existing canvas'
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

// set frame styles
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



void ValidationUtils::PullPlot3(XtraValues* inValsEl, XtraValues* inValsMu, const TString& outFileNamePrefix)
{
  // set style and remove existing canvas'
   ValidationUtils::Initialize();

   const Int_t Npar = inValsEl->size();
   

   static Int_t c_DarkGreen     = TColor::GetColor( "#115000" );
   static Int_t c_VDarkGreen    = TColor::GetColor( "#114400" );
   static Int_t c_LightBlue     = TColor::GetColor( "#66aaff" );
   static Int_t c_DarkBlue      = TColor::GetColor( "#0000bb" );

   Int_t    colEl = c_VDarkGreen;
   Int_t    colElL = c_DarkGreen;
   Int_t    colMu = c_DarkBlue;
   Int_t    colMuL = c_LightBlue;

   // ----------- now we can start the plotting -----------------------------

   // define canvas
   TCanvas* c = new TCanvas( "c"+outFileNamePrefix, "Results of the global electroweak fit", 0, 0, 400, 700 );   

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
   if(outFileNamePrefix.Contains("_MEff") or outFileNamePrefix.Contains("_bTag")){ 
     c->SetLeftMargin  ( 0.38 ); 
     XTitleSpaces="            ";
   }
   else{ 
     c->SetLeftMargin  ( 0.26 ); 
     XTitleSpaces="                  ";
   }
   c->SetTopMargin   ( 0.1 );
   c->SetRightMargin ( 0.05 );
   c->SetBottomMargin( 0.1 );
   c->SetGridx();
     
   // reduce size of title box
   gStyle->SetTitleW(0.60);          

   frame->SetLineColor(0);
   frame->SetTickLength(0,"Y");
   frame->SetLabelSize(0.034, "X");
   frame->SetXTitle( "(n_{pred} - n_{obs}) / #sigma_{tot}"+XTitleSpaces );
   frame->SetLabelOffset( 0.001, "X" );
   frame->SetTitleOffset( 0.85 , "X");
   frame->SetTitleSize( 0.046, "X" );
   frame->GetYaxis()->CenterLabels( 1 );
   frame->GetYaxis()->SetNdivisions( frame->GetNbinsY()+10, 1 );

   Double_t y[Npar];   
   frame->GetYaxis()->SetBinLabel( 1, "" ); // no labels
   for (Int_t i=0; i<Npar; i++) y[i] = i + offset; 

   frame->Draw();   

   Float_t xLeft=0.38;
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
      text->DrawLatex( x+2.2, yy - (i-Npar)*dy, inValsEl->m_reg_names.at(i) );
   }


   //The boxes -- electron channel
   TH1F *hPullEl = new TH1F( "hPullEl"+outFileNamePrefix, "hPullEl", Npar, -1, Npar-1 );
   hPullEl->SetLineColor(colEl);
   hPullEl->SetFillColor(colElL);
   for (Int_t i=0; i<Npar; i++) {
      Float_t delta = inValsEl->m_nPred.at(i) - inValsEl->m_nObs.at(i);
      Float_t err=inValsEl->m_Delta_eTot.at(i);
      Float_t pull = 0;
      if(fabs(err)>0){ pull=delta/err; }
      hPullEl->SetBinContent( Npar-i, pull );
   }
   for (Int_t i=0; i<Npar; i++) {
     Horizontal( hPullEl, Npar-i, kFALSE, hPullEl->GetFillColor() );
     Horizontal( hPullEl, Npar-i, kTRUE, hPullEl->GetLineColor() );
   }
   //The boxes -- muon channel
   TH1F *hPullMu = new TH1F( "hPullMu"+outFileNamePrefix, "hPullMu", Npar, -1, Npar-1 );
   hPullMu->SetLineColor(colMu);
   hPullMu->SetFillColor(colMuL);
   for (Int_t i=0; i<Npar; i++) {
      Float_t delta = inValsMu->m_nPred.at(i) - inValsMu->m_nObs.at(i);
      Float_t err=inValsMu->m_Delta_eTot.at(i);
      Float_t pull = 0;
      if(fabs(err)>0){ pull=delta/err; }
      hPullMu->SetBinContent( Npar-i, pull );
   }
   for (Int_t i=0; i<Npar; i++) {
     Horizontal( hPullMu, Npar-i, kFALSE, hPullMu->GetFillColor(), 0.16 );
     Horizontal( hPullMu, Npar-i, kTRUE, hPullMu->GetLineColor(), 0.16 );
   }

   TLegend* leg = new TLegend(xLeft,0.9,xLeft+0.5,0.96,"");
   leg->SetFillStyle(0);
   leg->SetBorderSize(0);
   leg->SetTextFont( 42 );
   leg->SetTextSize( 0.04 );

   leg->AddEntry(hPullEl, "Electron Channel", "f");
   leg->AddEntry(hPullMu, "Muon Channel", "f");
   leg->Draw();
   
   // final update of canvas
   c->Update();

   c->Print(outFileNamePrefix+".pdf");
   c->Print(outFileNamePrefix+".eps");
   cout<<"mv "<<outFileNamePrefix<<".pdf ~/www/data/."<<endl;
   return;
}



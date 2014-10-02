/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Macro  : SUSY_m0_vs_m12_all_withBand_cls.C                                     *
 * Created: 12 June 2012                                                          *
 *                                                                                *
 * Description:                                                                   *
 *      make contour plots - underlying macro for makecontourplots.C              *                   
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/

#include "contourmacros/CombinationGlob.C"
#include "TColor.h"
#include <algorithm>


/**
make contour plots based on the histograms produced by makecontourhists.C
- underlying macro for makecontourplots.C
*/
void SUSY_m0_vs_m12_all_withBand_cls( TString fname0 = "mudat_list.root",// nominal
                                      TString fname1 = "",               // Up
                                      TString fname2 = "",               // Down  
                                      TString fname3 = "", // external expection
                                      const char* prefix="test",
                                      const float& lumi = 20,
                                      bool showsig = true,
                                      int discexcl = 1,
                                      int showtevatron = 0,
                                      int showcms = 0,
                                      int showOneSigmaExpBand = 0,
                                      int showfixSigXSecBand = 0,
                                      int channel = -1,
                                      TString hname0 = "sigp1clsf",
                                      TString hname1 = "sigp1expclsf",
                                      TString hname3 = "sigclsu1s",
                                      TString hname5 = "sigclsd1s",
                                      TString hname6 = "sigp1ref",
                                      TString fnameMass= "")
{
   // set style and remove existing canvas'
   CombinationGlob::Initialize();
   
   cout << "--- Plotting m0 versus m12 " << endl;
   
   // --- prepare
   // open reference files, and retrieve histogram
   cout << "--- Reading root base file: " << fname0 << endl;
   TFile* f0 = TFile::Open( fname0, "READ" );
   if (!f0) {
      cout << "*** Error: could not retrieve histogram: " << hname0 << " in file: " << f0->GetName() 
           << " ==> abort macro execution" << endl;
      return;
   }
   
   TFile* f1;
   TFile* f2;
   if(showfixSigXSecBand){
      cout << "--- Reading root base file: " << fname1 << endl;
      f1 = TFile::Open( fname1, "READ" );
      cout << "--- Reading root base file: " << fname2 << endl;
      f2 = TFile::Open( fname2, "READ" );

      if(!f1 || !f2){
         cout << "*** Error: could not open in files: " << f1->GetName() <<" or "<< f2->GetName() 
              << " ==> abort macro execution" << endl;
         return;
      }
   }
   
   TH2F* histecls = (TH2F*)f0->Get( "sigp1expclsf" ); 
   TH2F* histocls = (TH2F*)f0->Get( "sigp1clsf" ); 
   if (histecls!=0) histecls->SetDirectory(0);
   if (histocls!=0) histocls->SetDirectory(0);
   
   // in case we use external expectation!
   TFile* f3 = TFile::Open( fname3, "READ" );
   TH2F* histe(0);
   if (f3) { histe = (TH2F*)f3->Get( hname0 ); }
   TH2F* histe_u1s(0);
   if (f3) { histe_u1s = (TH2F*)f3->Get( hname3 ); }
   TH2F* histe_d1s(0);
   if (f3) { histe_d1s = (TH2F*)f3->Get( hname5 ); }
   
   if (f3) {
      if (histecls!=0) { delete histecls; histecls=0; }
      histecls = (TH2F*)f3->Get( "sigp1expcls" );
      if (histecls!=0) histecls->SetDirectory(0);
      else {
        histecls = (TH2F*)f3->Get( "sigp1expclsf" );
        if (histecls!=0) histecls->SetDirectory(0);
      }
   }
   
   bool extExpectation = (f3!=0) ;
   
   TH2F* hist0 = (TH2F*)f0->Get( hname0 );
   TH2F* hist1 = (TH2F*)f0->Get( hname1 );
   TH2F* hist3 = (TH2F*)f0->Get( hname3 );
   TH2F* hist5 = (TH2F*)f0->Get( hname5 );
   TH2F* hist6 = (TH2F*)f0->Get( hname6 );
   
   if (hist0!=0) hist0->SetDirectory(0);
   if (hist1!=0) hist1->SetDirectory(0);
   if (hist3!=0) hist3->SetDirectory(0);
   if (hist5!=0) hist5->SetDirectory(0);
   if (hist6!=0) hist6->SetDirectory(0);
   f0->Close();

   TH2F* histe_esigxsp1s = (TH2F*)f1->Get( hname0 ); 
   TH2F* histe_esigxsm1s = (TH2F*)f2->Get( hname0 ); 

   if (histe_esigxsp1s!=0) histe_esigxsp1s->SetDirectory(0);
   if (histe_esigxsm1s!=0) histe_esigxsm1s->SetDirectory(0);

   //calculation of all contours
   TH2F* contour_esigxsp1s
      = ( histe_esigxsp1s!=0 ? FixAndSetBorders( *histe_esigxsp1s, "contour_esigxsp1s", "contour_esigxsp1s", 0 ) : 0);
   TH2F* contour_esigxsm1s
      = ( histe_esigxsm1s!=0 ? FixAndSetBorders( *histe_esigxsm1s, "contour_esigxsm1s", "contour_esigxsm1s", 0 ) : 0);
   
   TH2F* contour         = ( hist1!=0 ? FixAndSetBorders( *hist1, "contour", "contour", 0 ) : 0);
   TH2F* contour_obs     = ( hist0!=0 ? FixAndSetBorders( *hist0, "contour_obs", "contour_obs") : 0 );
   
   TH2F* contour_ep1s    = ( hist3!=0 ? FixAndSetBorders( *hist3, "contour", "contour", 0 ) : 0 );
   TH2F* contour_em1s    = ( hist5!=0 ? FixAndSetBorders( *hist5, "contour", "contour", 0 ) : 0 );

   // For Band
   TGraph* gr_contour_ep1s = ( contour_ep1s!=0 ? ContourGraph( contour_ep1s )->Clone() : 0 ); //ContourGraph( contour_ep1s )->Clone(); 
   TGraph* gr_contour_em1s = ( contour_em1s!=0 ? ContourGraph( contour_em1s )->Clone() : 0 ); //ContourGraph( contour_em1s )->Clone(); 
   
   TH2F* contour_exp(0);
   if (histe!=0)     { contour_exp     = FixAndSetBorders( *histe, "contour_exp", "contour_exp", 0 ); } 
   TH2F* contour_au1s(0);
   if (histe_u1s!=0) {  contour_au1s   = FixAndSetBorders( *histe_u1s, "contour", "contour", 0 ); }
   TH2F* contour_ad1s(0);
   if (histe_d1s!=0) {  contour_ad1s   = FixAndSetBorders( *histe_d1s, "contour", "contour", 0 ); }
   
   
   TH2F* contour_expcls(0);
   if (histecls!=0)     { contour_expcls     = FixAndSetBorders( *histecls, "contour_expcls", "contour_expcls", 0 ); }
   TH2F* contour_obscls(0);
   if (histocls!=0)     { contour_obscls     = FixAndSetBorders( *histocls, "contour_obscls", "contour_obscls", 0 ); }

   if (contour_obs==0) { 
      cout << "contour is zero" << endl;
      return;
   }


   
   // set text style
   gStyle->SetPaintTextFormat(".2g");
   if (hist1!=0) hist1->SetMarkerStyle(21);
   if (hist1!=0) hist1->SetMarkerSize(1.5);
   Float_t nsigmax(0)
      if (hist1!=0) nsigmax = hist1->GetMaximum();
   
   // --- draw
   
   //starting with style settings
   // create canvas
   TCanvas* c = new TCanvas( "c", "A scan of m_{0} versus m_{12}", 0, 0, 
                             CombinationGlob::StandardCanvas[0], CombinationGlob::StandardCanvas[1] );  
  //c->SetGrayscale();
  
  // create and draw the frame
  TH2F *frame = new TH2F("frame", "m_{0} vs m_{12}", 100, 100., 1400., 100, 150., 500. );
  //TH2F *frame = new TH2F("frame", "m_{0} vs m_{12}", 100, 100., 3750., 100, 115., 700. );
  //TH2F *frame = new TH2F("frame", "m_{0} vs m_{12}", 100, 100., 600., 100, 240., 500. );
  
  // set common frame style
  CombinationGlob::SetFrameStyle2D( frame, 1.0 ); // the size (scale) is 1.0
  
  frame->SetXTitle( "m_{0} [GeV]" );
  frame->SetYTitle( "m_{1/2} [GeV]" );
  frame->GetYaxis()->SetTitleOffset(1.35);

  //frame->SetTextFont( 42 );
  frame->GetXaxis()->SetTitleFont( 42 );
  frame->GetYaxis()->SetTitleFont( 42 );
  frame->GetXaxis()->SetLabelFont( 42 );
  frame->GetYaxis()->SetLabelFont( 42 );

  frame->GetXaxis()->SetTitleSize( 0.04 );
  frame->GetYaxis()->SetTitleSize( 0.04 );
  frame->GetXaxis()->SetLabelSize( 0.04 );
  frame->GetYaxis()->SetLabelSize( 0.04 );

  frame->Draw();
  
  const int nsig(3);
  //TH2F *chist[3];
  // draw contours
  //!instead of printing sigma in 68% 95% 98% levels now printing +1 sigma deviations 
  //for (Int_t nsigma=1; nsigma<=nsig; nsigma++)
  //  DrawContourSameColor( contour, nsigma, "blue", kFALSE, (nsigma==1?inverse:0) ) ;

  TString basecolor="yellow";
  Int_t nsigma=2;

    TLegend *leg = new TLegend(0.6,0.77,0.92,0.915);
  //TLegend *leg = new TLegend(0.59,0.47,0.92,0.915);//(0.565,0.47,0.925,0.915);//(0.59,0.47,0.92,0.915);

  leg->SetTextSize( CombinationGlob::DescriptionTextSize );
  leg->SetTextFont( 42 );
  leg->SetFillColor( 0 );
  leg->SetFillStyle(1001);
  
  Int_t c_myYellow   = TColor::GetColor("#ffe938"); 
  TGraph* grshadeExp = ( (gr_contour_ep1s!=0 && gr_contour_em1s!=0) ? DrawExpectedBand( gr_contour_ep1s, gr_contour_em1s, CombinationGlob::c_DarkYellow , 1001   , 0) : 0 ); //DrawExpectedBand( gr_contour_ep1s, gr_contour_em1s, CombinationGlob::c_DarkYellow , 1001   , 0)->Clone();
  
  if (discexcl==1) {
     //if (contour_obs!=0) DrawContourLine95( leg, contour_obs, "Observed PCL 95% CL", 2, 1, 3 );
     if (!extExpectation) { // expectation from toys
        //if (contour!=0) DrawContourLine95( leg, contour, "Expected PCL", CombinationGlob::c_DarkBlueT3, 6 );
        
        if (showfixSigXSecBand) {
           if (contour_esigxsp1s!=0) DrawContourLine95( leg, contour_esigxsp1s, "", CombinationGlob::c_DarkRed, 3, 2 );
        }
        if (contour_obscls!=0) DrawContourLine95( leg, contour_obscls, "Observed limit (#pm1 #sigma^{SUSY}_{theory})", CombinationGlob::c_DarkRed, 1, 4);
        if (showfixSigXSecBand) {
           if (contour_esigxsm1s!=0) DrawContourLine95( leg, contour_esigxsm1s, "", CombinationGlob::c_DarkRed, 3, 2 );
        }

        if (contour_expcls!=0) DrawContourLine95( leg, contour_expcls, "", CombinationGlob::c_DarkBlueT3, 6 ); 
        
        if (showOneSigmaExpBand) {
           if (contour_ep1s!=0) DrawContourLine95( leg, contour_ep1s, "", CombinationGlob::c_DarkYellow, 1 );
           if (contour_em1s!=0) DrawContourLine95( leg, contour_em1s, "", CombinationGlob::c_DarkYellow, 1 );
           DummyLegendExpected(leg, "Expected limit (#pm1 #sigma_{exp})", CombinationGlob::c_DarkYellow, 1001, CombinationGlob::c_DarkBlueT3, 6, 2);
        } else {
           if (contour!=0) DrawContourLine68( leg, contour, "exp. limit 68% CL", CombinationGlob::c_DarkBlueT3, 2 );
           if (contour!=0) DrawContourLine99( leg, contour, "exp. limit 99% CL", CombinationGlob::c_DarkBlueT3, 3 );
        }
        
     } else { // expectation from asimov
        if (contour_exp!=0) DrawContourLine95( leg, contour_exp, "Median expected limit", CombinationGlob::c_DarkBlueT3, 6);
        if (showOneSigmaExpBand) {
           if (contour_au1s!=0) DrawContourLine95( leg, contour_au1s, "Expected limit #pm1#sigma", CombinationGlob::c_DarkBlueT3, 3 );
           if (contour_ad1s!=0) DrawContourLine95( leg, contour_ad1s, "", CombinationGlob::c_DarkBlueT3, 3 );
        }
     }
  }
  
  // legend
  Float_t textSizeOffset = +0.000;
  Double_t xmax = frame->GetXaxis()->GetXmax();
  Double_t xmin = frame->GetXaxis()->GetXmin();
  Double_t ymax = frame->GetYaxis()->GetXmax();
  Double_t ymin = frame->GetYaxis()->GetXmin();
  Double_t dx   = xmax - xmin;
  Double_t dy   = ymax - ymin;
 
  //TString t1a = "99%, 95%, 68% CL fit contour (excluded)" ;
  // TString t1a = "-1#sigma, central, +1#sigma  fit contour (excluded)" ;
  TString t1b = "tan#beta = 3, A_{0}= 0, #mu < 0" ;
  Float_t nbkg(0);
  if( hist5!=0) nbkg = hist5->GetMaximum();
  TString t1c = Form("MC: n_{bkg}= %.1f", nbkg) ;
  
  // TLatex* text1a = new TLatex( 70, 260, t1a );
  TLatex* text1b = new TLatex( 150, ymax + dy*0.025, t1b );
  TLatex* text1c = new TLatex( 70, 280, t1c );
  
  // text1a->SetTextColor( 1 ); //CombinationGlob::c_VDarkGreen );
  text1b->SetTextColor( 1 ); //CombinationGlob::c_VDarkGreen );
  text1c->SetTextColor( 1 );
  
  text1b->SetTextFont( 42 ); //CombinationGlob::c_VDarkGreen );

  // text1a->SetTextAlign( 11 );
  text1b->SetTextAlign( 11 );
  text1c->SetTextAlign( 11 );
  
  //  text1a->SetTextSize( CombinationGlob::DescriptionTextSize + textSizeOffset );
  text1b->SetTextSize( CombinationGlob::DescriptionTextSize  );
  text1c->SetTextSize( CombinationGlob::DescriptionTextSize  );
  
  TLatex *Leg0 = new TLatex( xmin, ymax + dy*0.025, "MSUGRA/CMSSM: tan#beta = 10, A_{0}= 0, #mu>0" );
  Leg0->SetTextAlign( 11 );
  Leg0->SetTextFont( 42 );
  Leg0->SetTextSize( CombinationGlob::DescriptionTextSize);
  Leg0->SetTextColor( 1 );
  Leg0->AppendPad();
  
  TLatex *Leg1 = new TLatex();
  Leg1->SetNDC();
  Leg1->SetTextAlign( 11 );
  Leg1->SetTextFont( 42 );
  Leg1->SetTextSize( CombinationGlob::DescriptionTextSize );
  Leg1->SetTextColor( 1 );
  Leg1->DrawLatex(0.33,0.87, Form("L^{int} = %1.2f fb^{-1},  #sqrt{s}=7 TeV",lumi));  // 0.32,0.87 //0.33,0.87
  Leg1->AppendPad();
  
  TLatex *Leg2 = new TLatex();
  Leg2->SetNDC();
  Leg2->SetTextAlign( 11 );
  Leg2->SetTextSize( CombinationGlob::DescriptionTextSize );
  Leg2->SetTextColor( 1 );
  Leg2->SetTextFont(42);
  if (prefix!=0) { 
    Leg2->DrawLatex(0.33,0.81,prefix); // 0.15,0.81//0.33,0.81//0.305
    Leg2->AppendPad(); 
  }

  //// draw number of signal events
  if (nsigmax>0 && showsig) {  hist1->Draw("textsame"); }
  //else {
  //  // draw grid for clarity
  //  c->SetGrid();
  //}
  //reddraw cahnnel label
  if (prefix!=0) { Leg2->AppendPad(); }

  // redraw axes
  frame->Draw( "sameaxis" );
  
  leg->Draw("same");
  // update the canvas
  c->Update();

  ////////////////////////////////////////////////////////////////////////////////////////////
  
  //gROOT->GetListOfSpecials()->Print();
  
   TObjArray *contours = (TObjArray*)gROOT->GetListOfSpecials()->FindObject("contours");
   if (contours!=0) {
     //contours->Print("v");
     
     TList *lcontour1 = (TList*)contours->At(0);
     //lcontour1->Print();
     if (lcontour1!=0) {
       TGraph *gc1 = (TGraph*)lcontour1->First();
       if (gc1!=0) { 
         //gc1->Print();
         //if (gc1->GetN() < 10) return;
         //gc1->SetMarkerStyle(21);
         //gc1->Draw("alp");
       }
     }
   }

  ////////////////////////////////////////////////////////////////////////////////////////////
  
  // create plots
  // store histograms to output file
  TObjArray* arr = fname0.Tokenize("/");
  TObjString* objstring = (TObjString*)arr->At( arr->GetEntries()-1 );
  TString outfile = TString(Form("wband%d_",showOneSigmaExpBand)) + TString(Form("wfixSigXSecband%d_",showfixSigXSecBand)) + TString(Form("showcms%d_",showcms)) + objstring->GetString().ReplaceAll(".root","");
  delete arr;

  TString prefixsave = TString(prefix).ReplaceAll(" ","_")+ Form("wband%d_",showOneSigmaExpBand);
  CombinationGlob::imgconv( c, Form("plots/atlascls_m0m12_%s",outfile.Data()) );   

  ////delete leg;
  ////if (contour!=0) delete contour;
  ////delete frame;
}


void
MirrorBorders( TH2& hist )
{
  int numx = hist.GetNbinsX();
  int numy = hist.GetNbinsY();
  
  Float_t val;
  // corner points
  hist.SetBinContent(0,0,hist.GetBinContent(1,1));
  hist.SetBinContent(numx+1,numy+1,hist.GetBinContent(numx,numy));
  hist.SetBinContent(numx+1,0,hist.GetBinContent(numx,1));
  hist.SetBinContent(0,numy+1,hist.GetBinContent(1,numy));
  
  for(int i=1; i<=numx; i++){
    hist.SetBinContent(i,0,	   hist.GetBinContent(i,1));
    hist.SetBinContent(i,numy+1, hist.GetBinContent(i,numy));
  }
  for(int i=1; i<=numy; i++) {
    hist.SetBinContent(0,i,      hist.GetBinContent(1,i));
    hist.SetBinContent(numx+1,i, hist.GetBinContent(numx,i));
  }
}


TH2F*
AddBorders( const TH2& hist, const char* name=0, const char* title=0)
{
  int nbinsx = hist.GetNbinsX();
  int nbinsy = hist.GetNbinsY();
  
  double xbinwidth = ( hist.GetXaxis()->GetBinCenter(nbinsx) - hist.GetXaxis()->GetBinCenter(1) ) / double(nbinsx-1);
  double ybinwidth = ( hist.GetYaxis()->GetBinCenter(nbinsy) - hist.GetYaxis()->GetBinCenter(1) ) / double(nbinsy-1);
  
  double xmin = hist.GetXaxis()->GetBinCenter(0) - xbinwidth/2. ;
  double xmax = hist.GetXaxis()->GetBinCenter(nbinsx+1) + xbinwidth/2. ;
  double ymin = hist.GetYaxis()->GetBinCenter(0) - ybinwidth/2. ;
  double ymax = hist.GetYaxis()->GetBinCenter(nbinsy+1) + ybinwidth/2. ;
  
  TH2F* hist2 = new TH2F(name, title, nbinsx+2, xmin, xmax, nbinsy+2, ymin, ymax);
  
  for (Int_t ibin1=0; ibin1 <= hist.GetNbinsX()+1; ibin1++) {
    for (Int_t ibin2=0; ibin2 <= hist.GetNbinsY()+1; ibin2++)
      hist2->SetBinContent( ibin1+1, ibin2+1, hist.GetBinContent(ibin1,ibin2) );
  }
  
  return hist2;
}


void SetBorders( TH2 &hist, Double_t val=0 )
{
  int numx = hist.GetNbinsX();
  int numy = hist.GetNbinsY();
  
  for(int i=0; i <= numx+1 ; i++){
    hist.SetBinContent(i,0,val);
    hist.SetBinContent(i,numy+1,val);
  }
  for(int i=0; i <= numy+1 ; i++) {
    hist.SetBinContent(0,i,val);
    hist.SetBinContent(numx+1,i,val);
  }
}


TH2F* 
FixAndSetBorders( const TH2& hist, const char* name=0, const char* title=0, Double_t val=0 )
{
  TH2F* hist0 = hist.Clone(); // histogram we can modify
  
  MirrorBorders( *hist0 );    // mirror values of border bins into overflow bins
  
  TH2F* hist1 = AddBorders( *hist0, "hist1", "hist1" );   
  // add new border of bins around original histogram,
  // ... so 'overflow' bins become normal bins
  SetBorders( *hist1, val );                              
  // set overflow bins to value 1
  
  TH2F* histX = AddBorders( *hist1, "histX", "histX" );   
  // add new border of bins around original histogram,
  // ... so 'overflow' bins become normal bins
  
  TH2F* hist3 = histX->Clone();
  hist3->SetName( name!=0 ? name : "hist3" );
  hist3->SetTitle( title!=0 ? title : "hist3" );
  
  delete hist0; delete hist1; delete histX;
  return hist3; // this can be used for filled contour histograms
}


void 
DrawContourSameColor( TLegend *leg, TH2F* hist, Int_t nsigma, TString color, Bool_t second=kFALSE, TH2F* inverse=0, Bool_t linesOnly=kFALSE, Bool_t isnobs=kFALSE )
{
  if (nsigma < 1 || nsigma > 3) {
    cout << "*** Error in CombinationGlob::DrawContour: nsigma out of range: " << nsigma 
	 << "==> abort" << endl;
    exit(1);
  }
  nsigma--; // used as array index
  
  Int_t lcol_sigma;
  Int_t fcol_sigma[3];
  Int_t lstyle = 1;
  if( color == "pink" ){
    lcol_sigma    = CombinationGlob::c_VDarkPink;
    fcol_sigma[0] = CombinationGlob::c_LightPink;
    fcol_sigma[1] = CombinationGlob::c_LightPink;
    fcol_sigma[2] = CombinationGlob::c_LightPink;
  }
  else if( color == "green" ){ // HF
    lcol_sigma    = CombinationGlob::c_VDarkGreen;
    fcol_sigma[0] = CombinationGlob::c_DarkGreen;
    fcol_sigma[1] = CombinationGlob::c_LightGreen;
    fcol_sigma[2] = CombinationGlob::c_VLightGreen;
  } 
  else if( color == "yellow" ){
    lcol_sigma    = CombinationGlob::c_VDarkYellow;
    fcol_sigma[0] = CombinationGlob::c_DarkYellow;
    fcol_sigma[1] = CombinationGlob::c_DarkYellow;
    fcol_sigma[2] = CombinationGlob::c_White; //c_DarkYellow;
    lstyle = 2;
  }
  else if( color == "orange" ){
    lcol_sigma    = CombinationGlob::c_VDarkOrange;
    fcol_sigma[0] = CombinationGlob::c_DarkOrange;
    fcol_sigma[1] = CombinationGlob::c_LightOrange; // c_DarkOrange
    fcol_sigma[2] = CombinationGlob::c_VLightOrange;
  }
  else if( color == "gray" ){
    lcol_sigma    = CombinationGlob::c_VDarkGray;
    fcol_sigma[0] = CombinationGlob::c_LightGray;
    fcol_sigma[1] = CombinationGlob::c_LightGray;
    fcol_sigma[2] = CombinationGlob::c_LightGray;
  }
  else if( color == "blue" ){
    lcol_sigma    = CombinationGlob::c_DarkBlueT1;
    fcol_sigma[0] = CombinationGlob::c_BlueT5;
    fcol_sigma[1] = CombinationGlob::c_BlueT3;
    fcol_sigma[2] = CombinationGlob::c_White;  //CombinationGlob::c_BlueT2;

  }
  
  // contour plot
  TH2F* h = new TH2F( *hist );
  h->SetContour( 1 );
  double pval = CombinationGlob::cl_percent[1];
  double signif = TMath::NormQuantile(1-pval);
  double dnsigma = double(nsigma)-1.;
  double dsignif = signif + dnsigma;
  h->SetContourLevel( 0, dsignif );

  if( !second ){
    h->SetFillColor( fcol_sigma[nsigma] );
    
    if (!linesOnly) h->Draw( "samecont0" );
  }

  h->SetLineColor( nsigma==1? 1 : lcol_sigma );
   if (isnobs)h->SetLineColor( nsigma==1? 2 : lcol_sigma );
  //h->SetLineStyle( 4 );
  h->SetLineWidth( 2 );
  h->SetLineStyle( lstyle );
  h->Draw( "samecont3" );
  
  if (linesOnly&&!isnobs)
    if(nsigma==1){ leg->AddEntry(h,"exp. 95% CL limit","l");}
  if (isnobs)
    if(nsigma==1){ leg->AddEntry(h,"obs. 95% CL limit","l");}  
  if (!linesOnly) {
  if(nsigma==0){ leg->AddEntry(h,"- 1 #sigma expectation","l"); }
  if(nsigma==2){ leg->AddEntry(h,"+ 1 #sigma expectation","l");}
  } 
}


void 
DrawContourSameColorDisc( TLegend *leg, TH2F* hist, Double_t nsigma, TString color, Bool_t second=kFALSE, TH2F* inverse=0, Bool_t linesOnly=kFALSE )
{
  if (nsigma < 0.5 || nsigma > 10.5 ) {
    cout << "*** Error in CombinationGlob::DrawContour: nsigma out of range: " << nsigma 
	 << "==> abort" << endl;
    exit(1);
  }
  
  Int_t lcol_sigma;
  Int_t fcol_sigma[3];

  if( color == "pink" ){
    lcol_sigma    = CombinationGlob::c_VDarkPink;
    fcol_sigma[0] = CombinationGlob::c_LightPink;
    fcol_sigma[1] = CombinationGlob::c_LightPink;
    fcol_sigma[2] = CombinationGlob::c_LightPink;
  }
  else if( color == "green" ){ // HF
    lcol_sigma    = CombinationGlob::c_VDarkGreen;
    fcol_sigma[0] = CombinationGlob::c_DarkGreen;
    fcol_sigma[1] = CombinationGlob::c_LightGreen;
    fcol_sigma[2] = CombinationGlob::c_VLightGreen;
  } 
  else if( color == "yellow" ){
    lcol_sigma    = CombinationGlob::c_VDarkYellow;
    fcol_sigma[0] = CombinationGlob::c_DarkYellow;
    fcol_sigma[1] = CombinationGlob::c_DarkYellow;
    fcol_sigma[2] = CombinationGlob::c_White; //c_DarkYellow;
  }
  else if( color == "orange" ){
    lcol_sigma    = CombinationGlob::c_VDarkOrange;
    fcol_sigma[0] = CombinationGlob::c_DarkOrange;
    fcol_sigma[1] = CombinationGlob::c_LightOrange; // c_DarkOrange
    fcol_sigma[2] = CombinationGlob::c_VLightOrange;
  }
  else if( color == "gray" ){
    lcol_sigma    = CombinationGlob::c_VDarkGray;
    fcol_sigma[0] = CombinationGlob::c_LightGray;
    fcol_sigma[1] = CombinationGlob::c_LightGray;
    fcol_sigma[2] = CombinationGlob::c_LightGray;
  }
  else if( color == "blue" ){
    lcol_sigma    = CombinationGlob::c_DarkBlueT1;
    fcol_sigma[0] = CombinationGlob::c_BlueT5;
    fcol_sigma[1] = CombinationGlob::c_BlueT3;
    fcol_sigma[2] = CombinationGlob::c_BlueT2;
  }

  // contour plot
  TH2F* h = new TH2F( *hist );
  h->SetContour( 1 );
  double dsignif = double (nsigma);
  h->SetContourLevel( 0, dsignif );

  Int_t mycolor = (nsigma==5   ? 0 : 2);
  Int_t mycolor = (nsigma==2.5 ? 1 : 2);

  if( !second ){
    h->SetFillColor( fcol_sigma[mycolor] );
    if (!linesOnly) h->Draw( "samecont0" );
  }

  h->SetLineColor( (nsigma==2.5) ? 2 : lcol_sigma );

  h->SetLineStyle( nsigma==5 || nsigma==2.5 ? 1 : 2 );
  h->SetLineWidth( nsigma==5 || nsigma==2.5 ? 2 : 1 );

  h->Draw( "samecont3" );

  if(nsigma==5)   { leg->AddEntry(h,"5 #sigma discovery","l"); }
  if(nsigma==6)   { leg->AddEntry(h,"N (int) #sigma discovery","l"); }
  if(nsigma==2.5) { leg->AddEntry(h,"2.5 #sigma discovery","l"); }
}




void
DrawContourMassLine(TH2F* hist, Double_t mass, int color=14 ) //color=TColor::GetColor("#dddddd") ) // 204^= TColor::GetColor("#dddddd"); original was int color=14 
{

  // contour plot
  TH2F* h = new TH2F( *hist );

  //  Double_t contours[5] = {500, 1000, 1500, 2000, 2500}
  h->SetContour( 1 );
  //h->SetContour( 5, contours )
  //  h->SetContourLevel( 0, contours );
  h->SetContourLevel( 0, mass );

  h->SetLineColor( color );
  h->SetLineStyle( 7 );
  h->SetLineWidth( 1 );
  h->Draw( "samecont3" );

}





void 
DrawContourLine95( TLegend *leg, TH2F* hist, const TString& text="", Int_t linecolor=CombinationGlob::c_VDarkGray, Int_t linestyle=2, Int_t linewidth=2 )
{
  // contour plot
  TH2F* h = new TH2F( *hist );
  h->SetContour( 1 );
  double pval = CombinationGlob::cl_percent[1];
  double signif = TMath::NormQuantile(1-pval);
  //cout << "signif: " <<signif << endl;
  h->SetContourLevel( 0, signif );

  h->SetLineColor( linecolor );
  h->SetLineWidth( linewidth );
  h->SetLineStyle( linestyle );
  h->Draw( "samecont3" );
  
  if (!text.IsNull()) leg->AddEntry(h,text.Data(),"l"); 
}


void
DrawContourLine99( TLegend *leg, TH2F* hist, const TString& text="", Int_t linecolor=CombinationGlob::c_VDarkGray, Int_t linestyle=2 )
{
  // contour plot
  TH2F* h = new TH2F( *hist );
  h->SetContour( 1 );
  double pval = CombinationGlob::cl_percent[2];
  double signif = TMath::NormQuantile(1-pval);

  h->SetContourLevel( 0, signif );

  h->SetLineColor( linecolor );
  h->SetLineWidth( 2 );
  h->SetLineStyle( linestyle );
  h->Draw( "samecont3" );

  if (!text.IsNull()) leg->AddEntry(h,text.Data(),"l");
}


void
DrawContourLine68( TLegend *leg, TH2F* hist, const TString& text="", Int_t linecolor=CombinationGlob::c_VDarkGray, Int_t linestyle=2 )
{
  // contour plot
  TH2F* h = new TH2F( *hist );
  h->SetContour( 1 );
  double pval = CombinationGlob::cl_percent[0];
  double signif = TMath::NormQuantile(1-pval);

  h->SetContourLevel( 0, signif );

  h->SetLineColor( linecolor );
  h->SetLineWidth( 2 );
  h->SetLineStyle( linestyle );
  h->Draw( "samecont3" );

  if (!text.IsNull()) leg->AddEntry(h,text.Data(),"l");
}


TGraph*
ContourGraph( TH2F* hist)
{
   TGraph* gr0 = new TGraph();
   TH2F* h = (TH2F*)hist->Clone();
   h->GetYaxis()->SetRangeUser(0,700);
   h->GetXaxis()->SetRangeUser(50,4000);
   gr = (TGraph*)gr0->Clone(h->GetName());
   //  cout << "==> Will dumb histogram: " << h->GetName() << " into a graph" <<endl;
   h->SetContour( 1 );
   double pval = CombinationGlob::cl_percent[1];
   double signif = TMath::NormQuantile(1-pval);
   h->SetContourLevel( 0, signif );
   h->Draw("CONT LIST");
   h->SetDirectory(0);
   gPad->Update();
   TObjArray *contours = gROOT->GetListOfSpecials()->FindObject("contours");
   Int_t ncontours     = contours->GetSize();
   TList *list = (TList*)contours->At(0);
   Int_t number_of_lists = list->GetSize();
   gr = (TGraph*)list->At(0);
   TGraph* grTmp = new TGraph();
   for (int k = 0 ; k<number_of_lists ; k++){
      grTmp = (TGraph*)list->At(k);
      Int_t N = gr->GetN();
      Int_t N_tmp = grTmp->GetN();
      if(N < N_tmp) gr = grTmp;
      //    mg->Add((TGraph*)list->At(k));
   }

   gr->SetName(hist->GetName());
   int N = gr->GetN();
   double x0, y0;

   //for(int j=0; j<N; j++) {
   //    gr->GetPoint(j,x0,y0);
   //    cout << j << " : " << x0 << " : "<<y0 << endl;
   // }
     
   //  //  gr->SetMarkerSize(2.0);
   //  gr->SetMarkerSize(2.0);
   //  gr->SetMarkerStyle(21);
   //  gr->Draw("LP");
   //  cout << "Generated graph " << gr << " with name " << gr->GetName() << endl;
   return gr;
}


TGraph*
DrawExpectedBand( TGraph* gr1,  TGraph* gr2, Int_t fillColor, Int_t fillStyle, Int_t cut = 0)
{
   //  TGraph* gr1 = new TGraph( *graph1 );
   //  TGraph* gr2 = new TGraph( *graph2 );
   
   int number_of_bins = max(gr1->GetN(),gr2->GetN());
   
   const Int_t gr1N = gr1->GetN();
   const Int_t gr2N = gr2->GetN();

   const Int_t N = number_of_bins;
   Double_t x1[N], y1[N], x2[N], y2[N];
   
   Double_t xx0, yy0;
    
   for(int j=0; j<gr1N; j++) {
      gr1->GetPoint(j,xx0,yy0);
      x1[j] = xx0;
      y1[j] = yy0;
   }
   if (gr1N < N) {
      for(int i=gr1N; i<N; i++) {
         x1[i] = x1[gr1N-1];
         y1[i] = y1[gr1N-1];
      }
   }   
   Double_t xx1, yy1;
   
   for(int j=0; j<gr2N; j++) {
      gr2->GetPoint(j,xx1,yy1);
      x2[j] = xx1;
      y2[j] = yy1;
   }
   if (gr2N < N) {
      for(int i=gr2N; i<N; i++) {
         x2[i] = x2[gr2N-1];
         y2[i] = y2[gr2N-1];
      }
   }
 

   TGraph *grshade = new TGraphAsymmErrors(2*N);
   for (int i=0;i<N;i++) {
      if (x1[i] > cut){
         grshade->SetPoint(i,x1[i],y1[i]);
         }
      if (x2[N-i-1] > cut){
         grshade->SetPoint(N+i,x2[N-i-1],y2[N-i-1]);
         }
   }
   
   // Apply the cut in the shade plot if there is something that doesn't look good...
   int Nshade = grshade->GetN();
   double x0, y0;
   double x00, y00;
   
   for(int j=0; j<Nshade; j++) {
      grshade->GetPoint(j,x0,y0);
      if ((x0 != 0) && (y0 != 0)) {
         x00 = x0;
         y00 = y0;
         break;
      }
   } 

   for(int j=0; j<Nshade; j++) {
      grshade->GetPoint(j,x0,y0);
      if ((x0 == 0) && (y0 == 0))
         grshade->SetPoint(j,x00,y00);
   }
   
   // Now draw the plot...
   grshade->SetFillStyle(fillStyle);
   grshade->SetFillColor(fillColor);
   grshade->SetMarkerStyle(21);
   grshade->Draw("F");

   return grshade;
}


void
DummyLegendExpected(TLegend* leg, TString what,  Int_t fillColor, Int_t fillStyle, Int_t lineColor, Int_t lineStyle, Int_t lineWidth)
{

   TGraph* gr = new TGraph();
   gr->SetFillColor(fillColor);
   gr->SetFillStyle(fillStyle);
   gr->SetLineColor(lineColor);
   gr->SetLineStyle(lineStyle);
   gr->SetLineWidth(lineWidth);
   leg->AddEntry(gr,what,"LF");
}


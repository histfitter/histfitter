#include "contourmacros/CombinationGlob.C"
#include "TColor.h"
#include <algorithm>

#include "contourmacros/cdftanb5.C"
#include "contourmacros/d0tanb3muneg.C"
#include "contourmacros/ATLAS10_1lepton.C"
#include "../../../HistFitterUser/common/ATLAS_EPS_contours.C"

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
                                      TString fnameMass= "../../../HistFitterUser/common/mSugraGridtanbeta10_gluinoSquarkMasses.root")
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

   TH2F* contour_esigxsp1s
      = ( histe_esigxsp1s!=0 ? FixAndSetBorders( *histe_esigxsp1s, "contour_esigxsp1s", "contour_esigxsp1s", 0 ) : 0);
   TH2F* contour_esigxsm1s
      = ( histe_esigxsm1s!=0 ? FixAndSetBorders( *histe_esigxsm1s, "contour_esigxsm1s", "contour_esigxsm1s", 0 ) : 0);
   
   TH2F* contour         = ( hist1!=0 ? FixAndSetBorders( *hist1, "contour", "contour", 0 ) : 0);
   TH2F* contour_obs     = ( hist0!=0 ? FixAndSetBorders( *hist0, "contour_obs", "contour_obs") : 0 );
   
   TH2F* contour_ep1s    = ( hist3!=0 ? FixAndSetBorders( *hist3, "contour", "contour", 0 ) : 0 );
   TH2F* contour_em1s    = ( hist5!=0 ? FixAndSetBorders( *hist5, "contour", "contour", 0 ) : 0 );

   // For Band
   TGraph* gr_contour_ep1s = ( contour_ep1s!=0 ? ContourGraph( contour_ep1s ) : 0 ); //ContourGraph( contour_ep1s )->Clone(); 
   TGraph* gr_contour_em1s = ( contour_em1s!=0 ? ContourGraph( contour_em1s ) : 0 ); //ContourGraph( contour_em1s )->Clone(); 
   
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
   
   // create canvas
   TCanvas* c = new TCanvas( "c", "A scan of m_{0} versus m_{12}", 0, 0, 
                             CombinationGlob::StandardCanvas[0], CombinationGlob::StandardCanvas[1] );  
  //c->SetGrayscale();
  
  // create and draw the frame
  //TH2F *frame = new TH2F("frame", "m_{0} vs m_{12} - ATLAS work in progress", 100, 100., 1400., 100, 115., 500. );
  TH2F *frame = new TH2F("frame", "m_{0} vs m_{12} - ATLAS work in progress", 100, 100., 3750., 100, 115., 700. );
  //TH2F *frame = new TH2F("frame", "m_{0} vs m_{12} - ATLAS work in progress", 100, 100., 600., 100, 240., 500. );
  
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

  //  TLegend *leg = new TLegend(0.7,0.77,0.95,0.915);
  TLegend *leg = new TLegend(0.57,0.52,0.85,0.915);//(0.565,0.47,0.925,0.915);//(0.59,0.47,0.92,0.915);

  leg->SetTextSize( CombinationGlob::DescriptionTextSize );
  leg->SetTextSize( 0.03 );
  leg->SetTextFont( 42 );
  leg->SetFillColor( 0 );
  leg->SetFillStyle(1001);
  
  // add squark, gluino mass contour lines HERE (TILL)
  TFile* f4 = TFile::Open( fnameMass, "READ" );
  TH2F* histSq = (TH2F*)f4->Get( "mSugraGrid_squarkMasses" );
  TH2F* histGl = (TH2F*)f4->Get( "mSugraGrid_gluinoMasses" );
  histSq->SetDirectory(0);
  histGl->SetDirectory(0);
  f4->Close();

  TH2F* histSquarkMass   = FixAndSetBorders( *histSq, "SquarkMass", "SquarkMass", 10000 );
  TH2F* histGluinoMass   = FixAndSetBorders( *histGl, "GluinoMass", "GluinoMass", 10000 );
  
//  DrawContourMassLine( histSquarkMass, 400.0 );
//  DrawContourMassLine( histSquarkMass, 500.0 );
  DrawContourMassLine( histSquarkMass, 600.0 );
//  DrawContourMassLine( histSquarkMass, 700.0 );
  DrawContourMassLine( histSquarkMass, 800.0 , 17);
//  DrawContourMassLine( histSquarkMass, 900.0 );
  DrawContourMassLine( histSquarkMass, 1000.0 );  
//  DrawContourMassLine( histSquarkMass, 1100.0 ); 
  DrawContourMassLine( histSquarkMass, 1200.0 , 17);
//  DrawContourMassLine( histSquarkMass, 1300.0 );    
  DrawContourMassLine( histSquarkMass, 1400.0 );
//  DrawContourMassLine( histSquarkMass, 1500.0 );
  DrawContourMassLine( histSquarkMass, 1600.0 , 17);
//  DrawContourMassLine( histSquarkMass, 1700.0 );
  DrawContourMassLine( histSquarkMass, 1800.0 );
//  DrawContourMassLine( histSquarkMass, 1900.0 );
  DrawContourMassLine( histSquarkMass, 2000.0 , 17);  
//  DrawContourMassLine( histSquarkMass, 2100.0 ); 
  DrawContourMassLine( histSquarkMass, 2200.0 );  
//  DrawContourMassLine( histSquarkMass, 2300.0 );     
  DrawContourMassLine( histSquarkMass, 2400.0 , 17);
//  DrawContourMassLine( histSquarkMass, 2500.0 );
  DrawContourMassLine( histSquarkMass, 2600.0 );
//  DrawContourMassLine( histSquarkMass, 2700.0 );
  DrawContourMassLine( histSquarkMass, 2800.0 , 17);
//  DrawContourMassLine( histSquarkMass, 2900.0 );
  DrawContourMassLine( histSquarkMass, 3000.0 );   
//  DrawContourMassLine( histSquarkMass, 3100.0 ); 
  DrawContourMassLine( histSquarkMass, 3200.0 , 17);  
//  DrawContourMassLine( histSquarkMass, 2300.0 );     
  DrawContourMassLine( histSquarkMass, 3400.0 );
//  DrawContourMassLine( histSquarkMass, 3500.0 );
//  DrawContourMassLine( histSquarkMass, 3600.0 , 17);
//  DrawContourMassLine( histSquarkMass, 3700.0 );
//  DrawContourMassLine( histSquarkMass, 3800.0 );
//  DrawContourMassLine( histSquarkMass, 3900.0 );
//  DrawContourMassLine( histSquarkMass, 4000.0 );        

  DrawContourMassLine( histGluinoMass, 400.0 );
  DrawContourMassLine( histGluinoMass, 500.0 , 17);
  DrawContourMassLine( histGluinoMass, 600.0 );
  DrawContourMassLine( histGluinoMass, 700.0 , 17);
  DrawContourMassLine( histGluinoMass, 800.0 );
  DrawContourMassLine( histGluinoMass, 900.0 , 17);
  DrawContourMassLine( histGluinoMass, 1000.0 );  
  DrawContourMassLine( histGluinoMass, 1100.0 , 17);  
  DrawContourMassLine( histGluinoMass, 1200.0 );  
  DrawContourMassLine( histGluinoMass, 1300.0 , 17);      
  DrawContourMassLine( histGluinoMass, 1400.0 );
  DrawContourMassLine( histGluinoMass, 1500.0 , 17);
  DrawContourMassLine( histGluinoMass, 1600.0 );
//  DrawContourMassLine( histGluinoMass, 1700.0 );
//  DrawContourMassLine( histGluinoMass, 1800.0 );
//  DrawContourMassLine( histGluinoMass, 1900.0 );
//  DrawContourMassLine( histGluinoMass, 2000.0 );  
//  DrawContourMassLine( histGluinoMass, 2100.0 ); 

  // find gluino ~ squark mass exclusion limit
  //DrawContourMassLine( histSquarkMass, 820.0 );
  //DrawContourMassLine( histGluinoMass, 820.0 );

/*  TLatex * s400 = new TLatex( 140, 167 , "#tilde{q} (400 GeV)" );
  s400->SetTextAlign( 11 );
  s400->SetTextSize( 0.025 );
  s400->SetTextColor( TColor::GetColor("#dddddd") );
  s400->Draw();*/
/*  TLatex * s500 = new TLatex( 150, 220, "#tilde{q} (500 GeV)" );
  s500->SetTextAlign( 11 );
  s500->SetTextSize( 0.025 );
  s500->SetTextColor( TColor::GetColor("#dddddd") );
  s500->Draw();*/
  TLatex * s600 = new TLatex( 340, 230, "#tilde{q} (600 GeV)" );
  s600->SetTextAlign( 11 );
  s600->SetTextAngle(-60);
  s600->SetTextSize( 0.025 );
  s600->SetTextColor( 16 ); //12
  s600->Draw();
  /*TLatex * s700 = new TLatex( 545, 315, "#tilde{q} (700 GeV)" );
  s700->SetTextAlign( 11 );
  s700->SetTextSize( 0.025 );
  s700->SetTextColor( TColor::GetColor("#dddddd") );
  s700->Draw();*/
  /*TLatex * s800 = new TLatex( 250, 270, "#tilde{q} (800 GeV)" );
  s800->SetTextAlign( 11 );
  s800->SetTextSize( 0.025 );
  s800->SetTextColor( 203 );
  s800->Draw();*/
  /*
  TLatex * s900 = new TLatex( 330, 400, "#tilde{q} (900 GeV)" );
  s900->SetTextAlign( 11 );
  s900->SetTextSize( 0.025 );
  s900->SetTextColor( TColor::GetColor("#dddddd") );
  s900->Draw();*/
   TLatex * s1000 = new TLatex( 550, 408, "#tilde{q} (1000 GeV)" );
  s1000->SetTextAlign( 11 );
  s1000->SetTextAngle(-60);
  s1000->SetTextSize( 0.025 );
  s1000->SetTextColor( 16 );
  s1000->Draw(); 
   TLatex * s1400 = new TLatex( 790, 580, "#tilde{q} (1400 GeV)" );
  s1400->SetTextAlign( 11 );
  s1400->SetTextAngle(-60);
  s1400->SetTextSize( 0.025 );
  s1400->SetTextColor( 16 );
  s1400->Draw();   

  /*TLatex * g400 = new TLatex( 1100, 140, "#tilde{g} (400 GeV)" );
  g400->SetTextAlign( 11 );
  g400->SetTextSize( 0.025 );
  g400->SetTextColor( 203 );
  g400->Draw();*/
  /*TLatex * g500 = new TLatex( 1000, 185, "#tilde{g} (500 GeV)" );
  g500->SetTextAlign( 11 );
  g500->SetTextSize( 0.025 );
  g500->SetTextColor( TColor::GetColor("#dddddd") );
  g500->Draw();*/
  TLatex * g600 = new TLatex( 1100, 225, "#tilde{g} (600 GeV)" );
  g600->SetTextAlign( 11 );
  g600->SetTextAngle(-4);
  g600->SetTextSize( 0.025 );
  g600->SetTextColor( 16 );
  g600->Draw();
  /*TLatex * g900 = new TLatex( 550, 380, "#tilde{g} (900 GeV)" );
  g900->SetTextAlign( 11 );
  g900->SetTextSize( 0.025 );
  g900->SetTextColor( TColor::GetColor("#dddddd") );
  g900->Draw();*/
  TLatex * g800 = new TLatex( 690, 330, "#tilde{g} (800 GeV)" );
  g800->SetTextAlign( 11 );
  g800->SetTextSize( 0.025 );
  g800->SetTextColor( 16 );
  //g800->Draw();
  TLatex * g1000 = new TLatex( 1400, 399, "#tilde{g} (1000 GeV)" );
  g1000->SetTextAlign( 11 );
  g1000->SetTextAngle(-5); 
  g1000->SetTextSize( 0.025 );
  g1000->SetTextColor( 16 );
  g1000->Draw();
  TLatex * g1200 = new TLatex( 1550, 489, "#tilde{g} (1200 GeV)" );
  g1200->SetTextAlign( 11 );
  g1200->SetTextAngle(-6); 
  g1200->SetTextSize( 0.025 );
  g1200->SetTextColor( 16 );
  //g1200->Draw();  
  TLatex * g1400 = new TLatex( 1650, 582, "#tilde{g} (1400 GeV)" );
  g1400->SetTextAlign( 11 );
  g1400->SetTextAngle(-6); 
  g1400->SetTextSize( 0.025 );
  g1400->SetTextColor( 16 );
  g1400->Draw();
  
  // island hacks
  if (true && channel==4) { // muon fixes 
    cout << "removing islands in muon channel ..." << endl;
    // contour line is drawn for values at 1.64485
    TAxis* ax = contour_obs->GetXaxis();
    TAxis* ay = contour_obs->GetYaxis();

    TH2F* contour_fix = contour_em1s;

    for (int xbin = 1; xbin <= contour_fix->GetNbinsX(); xbin++) {
      for (int ybin = 1; ybin <= contour_fix->GetNbinsY(); ybin++) {
	// island 1
	if ( ax->GetBinCenter( xbin) > 1350.  && ax->GetBinCenter( xbin) < 1500. && ay->GetBinCenter( ybin) < 130. && ay->GetBinCenter( ybin) > 89. ) {
	  cout << "Found spot here: " << xbin << " (" << ax->GetBinCenter( xbin)  << "), "
	       << ybin << " (" << ay->GetBinCenter( ybin) << "), "
	       << " value: " << contour_fix->GetBinContent(xbin,ybin) <<   endl;
	  cout << "   HACK : Setting above point by hand to 1.65 (!)" << endl;
	  if (contour_fix->GetBinContent(xbin,ybin)<1.65) contour_fix->SetBinContent(xbin, ybin, 1.66);
	}

      }
    }

  } 
  if (false && channel==1) { // electron

    cout << "removing islands in electron channel ..." << endl;
    // contour line is drawn for values at 1.64485
    TAxis* ax = contour_obs->GetXaxis();
    TAxis* ay = contour_obs->GetYaxis();

    contour_em1s

    for (int xbin = 1; xbin <= contour_obs->GetNbinsX(); xbin++) {
      for (int ybin = 1; ybin <= contour_obs->GetNbinsY(); ybin++) {
	// island 2
	if ( ax->GetBinCenter( xbin) > 420. && ax->GetBinCenter( xbin) < 480. &&
	     ay->GetBinCenter( ybin) > 140. && ay->GetBinCenter( ybin) < 160. ) {
	  cout << "Found spot here: " << xbin << " (" << ax->GetBinCenter( xbin)  << "), "
	       << ybin << " (" << ay->GetBinCenter( ybin) << "), "
	       << " value: " << contour->GetBinContent(xbin,ybin) <<   endl;
	  cout << "   HACK : Setting above point by hand to 1.50 (!)" << endl;
	  contour->SetBinContent(xbin, ybin, 1.50);
	}
      }
    }

  }

  if (false && channel==2) { // combined
    cout << "removing islands in combined channel ..." << endl;
  }


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
  

  // plot tevatron limits
  TGraph* lep2slep(0);
  TGraph* lep2char(0);
  TGraph* d0o(0);
  TGraph* d0graph(0);
  TGraph* cdfgraph(0);
  TGraph* atlas(0);
  TGraph* atlasexp(0);
  
  TGraph * staulsp = new TGraph();
  TGraph * noRGE = new TGraph();  
  TGraph * noEWSB = new TGraph(); 
  TGraph * tachyon = new TGraph();   
  TGraph * negmasssq = new TGraph(); 


  if (showtevatron==1 && discexcl==1) {
    //lep2char = ol1();
    lep2char = msugra_lepchrg("../../../HistFitterUser/common/mSugraGridtanbeta10_charginoMasses.root"); //ol1();
    //lep2char->Print();
    c->cd();  
    lep2char->SetFillColor(CombinationGlob::c_BlueT3);  
    lep2char->Draw("FSAME");
    lep2char->Draw("LSAME");
    //d0graph = d0tanb3muneg();
    //cdfgraph = cdftanb5();
    //atlas = ATLAS10_1lepton();
    //atlasexp = ATLAS10_1leptonexp();
  }
  
  msugraThExcl("../../../HistFitterUser/common/msugra_status.txt", staulsp, negmasssq, noRGE, noEWSB, tachyon, "../../../HistFitterUser/common/mSugraGridtanbeta10_charginoMasses.root");  
  
/*
  TGraph* cmscurve(0);
  if (showcms==1) { 
    //cmscurve = cmsoff();
    cmscurve = cms();
  }

  TGraph* msugra_noEWSB_curve(0);
  msugra_noEWSB_curve = msugra_noEWSB("../../../HistFitterUser/common/noEWSB.txt");
  c->cd();
  //msugra_noEWSB_curve->Print();
  msugra_noEWSB_curve->Draw("FSAME");
  msugra_noEWSB_curve->Draw("LSAME");
  
  TGraph* msugra_stauLSP_curve(0);
  msugra_stauLSP_curve = msugra_stauLSP();
  //msugra_stauLSP_curve->Print();
  msugra_stauLSP_curve->Draw("FSAME");
  msugra_stauLSP_curve->Draw("LSAME");

  //:w(void) stautanb3();*/
  
  c->cd();  
  
  
   
  staulsp->SetFillColor(CombinationGlob::c_LightGreen);
  staulsp->Draw("FSAME");
  staulsp->Draw("LSAME"); 
  
  //negmasssq->SetFillColor(kAzure+2);
  negmasssq->Draw("FSAME");
  negmasssq->Draw("LSAME");  
  
  noRGE->SetFillColor(CombinationGlob::c_DarkBlueT5);
  noRGE->Draw("FSAME");
  noRGE->Draw("LSAME"); 
  
  //noEWSB->SetFillColor(CombinationGlob::c_DarkGreen)
  noEWSB->Draw("FSAME");
  noEWSB->Draw("LSAME");   
  
  tachyon->Draw("FSAME");
  tachyon->Draw("LSAME");     
  
  c->cd();      
  c->Update();  
    
    
  if (showcms==1 && discexcl==1) {
     leg->AddEntry(cmscurve,"CMS jets (#alpha_{T}), 35 pb^{-1}","l");
  }
  
  // re-draw TLegend for old exclusions
  if (showtevatron==1 && discexcl==1) {
     leg->AddEntry( lep2char, "LEP2 #tilde{#chi}^{#pm}_{1}","F");
     //leg->AddEntry( d0graph,  "D0 #tilde{g}, #tilde{q}, tan#beta=3, #mu<0, 2.1 fb^{-1}","F" );
     //leg->AddEntry( cdfgraph, "CDF #tilde{g}, #tilde{q}, tan#beta=5, #mu<0, 2 fb^{-1}","F" );
  }
  
  leg->AddEntry( staulsp, "Stau LSP","F" );
  leg->AddEntry( noEWSB, "No EW SB","F" );
  leg->AddEntry( noRGE, "Non-convergent RGE","F" );  
  leg->AddEntry( negmasssq, "negmasssq","F" ); 
  
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
  Leg1->DrawLatex(0.33,0.87, Form("L^{int} = %1.2f fb^{-1},  #sqrt{s}=8 TeV",lumi));  // 0.32,0.87
  Leg1->AppendPad();
  
  TLatex *Leg2 = new TLatex();
  Leg2->SetNDC();
  Leg2->SetTextAlign( 11 );
  Leg2->SetTextSize( CombinationGlob::DescriptionTextSize );
  Leg2->SetTextColor( 1 );
  Leg2->SetTextFont(42);
  if (prefix!=0) { 
    Leg2->DrawLatex(0.33,0.81,prefix); // 0.15,0.81
    Leg2->AppendPad(); 
  }

  TLatex *atlasLabel = new TLatex();
  atlasLabel->SetNDC();
  atlasLabel->SetTextFont( 72 );
  atlasLabel->SetTextColor( 1 );
  atlasLabel->SetTextSize( 0.05 );
  atlasLabel->DrawLatex(0.15,0.87, "ATLAS"); // 0.15,0.87
  atlasLabel->AppendPad();

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

  TLatex *prel = new TLatex();
  prel->SetNDC();
  prel->SetTextFont( 42 );
  prel->SetTextColor( 1 );
  prel->SetTextSize( 0.04 );  
  prel->DrawLatex(0.15, 0.81, "Internal");   // 0.27,0.87
  prel->AppendPad();

  TString prefixsave = TString(prefix).ReplaceAll(" ","_") + Form("%dinvfb_",lumi) + Form("wband%d_",showOneSigmaExpBand);
  CombinationGlob::imgconv( c, Form("plots/m0m12cls_%s",outfile.Data()) );   

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
DrawContourMassLine(TH2F* hist, Double_t mass, int color=14 )
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
   h->GetYaxis()->SetRangeUser(250,700);
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

   // for(int j=0; j<N; j++) {
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
         x2[i] = x2[gr1N-1];
         y2[i] = y2[gr1N-1];
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


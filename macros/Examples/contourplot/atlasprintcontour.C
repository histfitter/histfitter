#include "contourmacros/CombinationGlob.C"
#include "TColor.h"

//#include "../Tevatron/msugra_oldlim.C"
#include "contourmacros/ol1.C"
#include "contourmacros/ol2.C"
#include "contourmacros/ol3.C"

//#include "cmsoff.C" // cms alpha-T prl official contour (not yet used)
#include "contourmacros/cms.C"      // cms alpha-T prelim contour
#include "contourmacros/cdftanb5.C"
#include "contourmacros/d0tanb3muneg.C"
#include "contourmacros/stautanb3.C"



void atlasprintcontour(const TString& combo = "all") 
{
  bool showsignal(false);
  int  discexcl; // 0=discovery, 1=exclusion
  bool showtevatron(true);
  bool showcms(true);
  bool doOneSigmaBand(true);
  int applyfix(0);

//   // sm3OR_list.root

  //
  SUSY_m0_vs_m12_all_withBand("MySoftOneLeptonKtScaleFitMetMeffR17_Output_hypotest__1_harvest_list.root", ""/*"1lexp_list.root"*/, "1 lepton, 3+ jets",   35, showsignal, discexcl=1, showtevatron, showcms,       doOneSigmaBand, channel=2 );


}



void SUSY_m0_vs_m12_all_withBand( TString fname1 = "mudat_list.root",  // this is the expected limit
                                  TString fname2 = "",
				const char* prefix="test",
				const int& lumi = 20,
				bool showsig = true,
				int discexcl = 1,
				int showtevatron = 0,
                                int showcms = 0,
				int showOneSigmaExpBand = 0,
                                int channel = -1,
				TString hname0 = "sigp1clsf",
				TString hname1 = "sigp1expclsf",
				TString hname3 = "sigclsu1s",
				TString hname5 = "sigclsd1s",
				TString fnameMass= "contourmacros/mSugraGrid_gluinoSquarkMasses.root",
                   )
{
  // set style and remove existing canvas'
  CombinationGlob::Initialize();
  
  // open reference files, and retrieve histogram
  cout << "--- Reading root base file: " << fname1 << endl;
  TFile* f0 = TFile::Open( fname1, "READ" );

  if (!f0) {
    cout << "*** Error: could not retrieve histogram: " << hname0 << " in file: " << f0->GetName() 
	 << " ==> abort macro execution" << endl;
    return;
  }


  TH2F* hist0 = (TH2F*)f0->Get( hname0 );
  hist0->SetDirectory(0);

  TH2F* hist1 = (TH2F*)f0->Get( hname1 );
  TH2F* hist3 = (TH2F*)f0->Get( hname3 );
  TH2F* hist5 = (TH2F*)f0->Get( hname5 );

  if (hist0!=0) hist0->SetDirectory(0);
  if (hist1!=0) hist1->SetDirectory(0);
  if (hist3!=0) hist3->SetDirectory(0);
  if (hist5!=0) hist5->SetDirectory(0);


  f0->Close();
  
  TH2F* contour_au1s(0);
  if (hist3!=0) {  contour_au1s   = FixAndSetBorders( *hist3, "contour_expcls_u1s", "contour_expcls_u1s", 0 ); }
  TH2F* contour_ad1s(0);
  if (hist5!=0) {  contour_ad1s   = FixAndSetBorders( *hist5, "contour_expcls_d1s", "contour_expcls_d1s", 0 ); }
  
  TH2F* contour_expcls(0);
  if (hist1!=0)     { contour_expcls     = FixAndSetBorders( *hist1, "contour_expcls", "contour_expcls", 0 ); }
  TH2F* contour_obscls(0);
  if (hist0!=0)     { contour_obscls     = FixAndSetBorders( *hist0, "contour_obscls", "contour_obscls", 0 ); }
    
  if (contour_obscls==0) {
    cout << "contour is zero" << endl;
    return;
  }

  // set text style
  gStyle->SetPaintTextFormat(".2g");
  hist0->SetMarkerStyle(21);
  hist0->SetMarkerSize(1.5);
  Float_t nsigmax = hist0->GetMaximum();
  
  // --- draw
  
  // create canvas
  TCanvas* c = new TCanvas( "c", "A scan of m_{0} versus m_{12}", 0, 0, 
			    CombinationGlob::StandardCanvas[0], CombinationGlob::StandardCanvas[1] );  
  //c->SetGrayscale();
  
  // create and draw the frame
  TH2F *frame = new TH2F("frame", "m_{0} vs m_{12} - ATLAS work in progress", 100, 40., 900., 100, 100., 400. );
  
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
  TLegend *leg = new TLegend(0.65,0.45,0.93,0.915);

  leg->SetTextSize( CombinationGlob::DescriptionTextSize );
  leg->SetTextFont( 42 );
  leg->SetFillColor( 0 );
  leg->SetFillStyle(1001);

  if (discexcl==1) {

    if (contour_obscls!=0) DrawContourLine95( leg, contour_obscls, "Observed limit", 2, 1 );

    frame->Draw( "sameaxis" );
    c->Update();
    if (contour_obscls!=0) writegraph(contour_obscls->GetName(),fname1,true);


    //TGraph* atlas = atlas();
    //c->Update();
    if (contour_expcls!=0) DrawContourLine95( leg, contour_expcls, "Observed limit", 2, 1 );

  
    frame->Draw( "sameaxis" );
    c->Update();
    if (contour_expcls!=0) writegraph(contour_expcls->GetName(),fname1);

    if (contour_au1s!=0) DrawContourLine95( leg, contour_au1s, "Observed limit", 2, 1 );

  
    frame->Draw( "sameaxis" );
    c->Update();
    if (contour_au1s!=0) writegraph(contour_au1s->GetName(),fname1);

    if (contour_ad1s!=0) DrawContourLine95( leg, contour_ad1s, "Observed limit", 2, 1 );

  
    frame->Draw( "sameaxis" );
    c->Update();
    if (contour_ad1s!=0) writegraph(contour_ad1s->GetName(),fname1);

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
  Float_t nbkg = hist0->GetMaximum();
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
  
  // redraw axes
  frame->Draw( "sameaxis" );
  
  leg->Draw("same");
  // update the canvas
  c->Update();

  
  // create plots
  // store histograms to output file
  TObjArray* arr = fname1.Tokenize("/");
  TObjString* objstring = (TObjString*)arr->At( arr->GetEntries()-1 );
  TString outfile = TString(Form("%dinvpb_",lumi)) + TString(Form("wband%d_",showOneSigmaExpBand)) + TString(Form("showcms%d_",showcms)) + objstring->GetString().ReplaceAll(".root","");
  delete arr;

  TString prefixsave = TString(prefix).ReplaceAll(" ","_") + Form("%dinvpb_",lumi) + Form("wband%d_",showOneSigmaExpBand);
  //CombinationGlob::imgconv( c, Form("plots/m0m12_%s",outfile.Data()) );   

  delete leg;
  delete contour_obscls;
  delete frame;
}


void writegraph(TString gname, TString fname1, bool recreate=false)
{
  ////////////////////////////////////////////////////////////////////////////////////////////
  TString fnameout = fname1;
  fnameout.ReplaceAll(".root","_graphs.root");

  TString fnameout2 = fname1;
  fnameout2.ReplaceAll(".root","_");
  fnameout2 += gname + ".C" ;
  

  TFile* fileout(0);
  if (recreate) fileout = TFile::Open(fnameout,"RECREATE");
  else fileout = TFile::Open(fnameout,"UPDATE");
  fileout->cd(); 
  
  gROOT->GetListOfSpecials()->Print();
  
   TObjArray *contours = (TObjArray*)gROOT->GetListOfSpecials()->FindObject("contours");
   if (contours!=0) {
     //contours->Print("v");
     int lsize = contours->GetSize();
     
     TList *lcontour1 = (TList*)contours->At(0);
     //lcontour1->Print("v");
     if (lcontour1!=0) {
       TGraph *gc1 = (TGraph*)lcontour1->First();
       if (gc1!=0) {
         gc1->SetName(gname);
         gc1->Write();
         //gc1->Print();
         //if (gc1->GetN() < 10) return;
         //gc1->SetMarkerStyle(21);
         //gc1->Draw("alp");

	 gc1->SaveAs(fnameout2);

       }
     }
   }

   fileout->Close();



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

  /*  
  // inverse contours plot, needed in case of contours within contours
  if (inverse!=0) {
    TH2F* g = new TH2F( *inverse );
    g->SetContour( 1 );
    g->SetContourLevel( 0, CombinationGlob::cl_percent[nsigma] );
    if( !second ){
      g->SetFillColor( 0 );
      if (!linesOnly) g->Draw( "samecont0" );
    }
  }
  */

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
DrawContourLine95( TLegend *leg, TH2F* hist, const TString& text="", Int_t linecolor=CombinationGlob::c_VDarkGray, Int_t linestyle=2 )
{
  // contour plot
  TH2F* h = new TH2F( *hist );
  h->SetContour( 1 );
  double pval = CombinationGlob::cl_percent[1];
  double signif = TMath::NormQuantile(1-pval);
  //cout << "signif: " <<signif << endl;
  h->SetContourLevel( 0, signif );

  h->SetLineColor( linecolor );
  h->SetLineWidth( 2 );
  h->SetLineStyle( linestyle );
  //h->Draw( "samecont3" );

  h->Draw( "CONT Z LIST" );  

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


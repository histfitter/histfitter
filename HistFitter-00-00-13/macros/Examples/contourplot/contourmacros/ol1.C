#include "TGraph.h"
#include "contourmacros/CombinationGlob.C"


TGraph* lep_chargino2(double xmin=40, double xmax=1500., double ymin=100, double ymax=500., TString xlabel = TString("m_{0} / GeV"), TString ylabel = TString("m_{1/2} / GeV")){

  TGraph *g_exp_leps = new TGraph(48);
  g_exp_leps->SetName("g_exp_leps");
  g_exp_leps->SetTitle("g_exp_leps");
  g_exp_leps->SetFillColor(84);
  g_exp_leps->SetLineWidth(2);
  g_exp_leps->SetMarkerStyle(20);
  g_exp_leps->SetMarkerSize(1.2);
  g_exp_leps->SetPoint(0,2963,169.6426);
  g_exp_leps->SetPoint(1,2939.087,165.375);
  g_exp_leps->SetPoint(2,2889,155.8165);
  g_exp_leps->SetPoint(3,2847.386,151.125);
  g_exp_leps->SetPoint(4,2815,149.4554);
  g_exp_leps->SetPoint(5,2741,147.0251);
  g_exp_leps->SetPoint(6,2667,144.9081);
  g_exp_leps->SetPoint(7,2593,142.8597);
  g_exp_leps->SetPoint(8,2519,138.9168);
  g_exp_leps->SetPoint(9,2445,137.3717);
  g_exp_leps->SetPoint(10,2412.414,136.875);
  g_exp_leps->SetPoint(11,2371,136.2432);
  g_exp_leps->SetPoint(12,2297,135.1538);
  g_exp_leps->SetPoint(13,2223,134.1516);
  g_exp_leps->SetPoint(14,2149,133.4349);
  g_exp_leps->SetPoint(15,2075,132.8093);
  g_exp_leps->SetPoint(16,2001,132.2798);
  g_exp_leps->SetPoint(17,1927,131.9858);
  g_exp_leps->SetPoint(18,1853,131.9393);
  g_exp_leps->SetPoint(19,1779,131.8927);
  g_exp_leps->SetPoint(20,1705,131.8833);
  g_exp_leps->SetPoint(21,1631,131.9131);
  g_exp_leps->SetPoint(22,1557,131.9433);
  g_exp_leps->SetPoint(23,1483,131.9857);
  g_exp_leps->SetPoint(24,1409,132.2631);
  g_exp_leps->SetPoint(25,1335,132.735);
  g_exp_leps->SetPoint(26,1261,133.2518);
  g_exp_leps->SetPoint(27,1187,133.8975);
  g_exp_leps->SetPoint(28,1113,134.7551);
  g_exp_leps->SetPoint(29,1039,135.7017);
  g_exp_leps->SetPoint(30,965,136.6621);
  g_exp_leps->SetPoint(31,950.7605,136.875);
  g_exp_leps->SetPoint(32,891,137.7686);
  g_exp_leps->SetPoint(33,817,139.0351);
  g_exp_leps->SetPoint(34,743,140.4101);
  g_exp_leps->SetPoint(35,669,141.8645);
  g_exp_leps->SetPoint(36,595,143.3901);
  g_exp_leps->SetPoint(37,521,145.0812);
  g_exp_leps->SetPoint(38,447,146.6467);
  g_exp_leps->SetPoint(39,373,148.0813);
  g_exp_leps->SetPoint(40,299,149.3225);
  g_exp_leps->SetPoint(41,225,150.3804);
  g_exp_leps->SetPoint(42,160.6882,151.125);
  g_exp_leps->SetPoint(43,151,151.237);
  g_exp_leps->SetPoint(44,77,151.9807);

  g_exp_leps->SetPoint(45,0,150);
  g_exp_leps->SetPoint(46,0,-10);
  g_exp_leps->SetPoint(47,3000,-10);
  //g_exp_leps->SetPoint(48,3000,130);

  g_exp_leps->SetLineColor(CombinationGlob::c_DarkGray);
  g_exp_leps->SetLineWidth(1);
  g_exp_leps->SetFillColor(CombinationGlob::c_BlueT3); //c_LightGray);
  //g_exp_leps->SetFillColor(kPink+6);
  g_exp_leps->GetXaxis()->SetRangeUser(xmin,xmax);
  g_exp_leps->GetXaxis()->SetTitle(xlabel.Data());
  g_exp_leps->GetYaxis()->SetRangeUser(ymin,ymax);
  g_exp_leps->GetYaxis()->SetTitle(ylabel.Data());
  g_exp_leps->GetYaxis()->SetTitleOffset(1.35);

  g_exp_leps->Draw("FSAME");
  g_exp_leps->Draw("LSAME");

  gPad->RedrawAxis();

  return g_exp_leps;


  // Draw exclusion regions for previous experiments (mainly Tevatron)
/*
  TGraph* g_exp_leps = new TGraph(74);
  g_exp_leps->SetPoint(0,0,243);
  g_exp_leps->SetPoint(1,6,242);
  g_exp_leps->SetPoint(2,10,241);
  g_exp_leps->SetPoint(3,13,240);
  g_exp_leps->SetPoint(4,24,235);
  g_exp_leps->SetPoint(5,36,224);
  g_exp_leps->SetPoint(6,37,222);
  g_exp_leps->SetPoint(7,40,219);
  g_exp_leps->SetPoint(8,41,217);
  g_exp_leps->SetPoint(9,43,215);
  g_exp_leps->SetPoint(10,44,213);
  g_exp_leps->SetPoint(11,45,212);
  g_exp_leps->SetPoint(12,46,210);
  g_exp_leps->SetPoint(13,47,209);
  g_exp_leps->SetPoint(14,48,207);
  g_exp_leps->SetPoint(15,49,206);
  g_exp_leps->SetPoint(16,53,198);
  g_exp_leps->SetPoint(17,54,197);
  g_exp_leps->SetPoint(18,57,191);
  g_exp_leps->SetPoint(19,58,188);
  g_exp_leps->SetPoint(20,61,182);
  g_exp_leps->SetPoint(21,62,179);
  g_exp_leps->SetPoint(22,63,177);
  g_exp_leps->SetPoint(23,64,174);
  g_exp_leps->SetPoint(24,65,172);
  g_exp_leps->SetPoint(25,66,169);
  g_exp_leps->SetPoint(26,68,163);
  g_exp_leps->SetPoint(27,69,161);
  g_exp_leps->SetPoint(28,70,157);
  g_exp_leps->SetPoint(29,71,154);
  g_exp_leps->SetPoint(30,72,151);
  g_exp_leps->SetPoint(31,73,148);
  g_exp_leps->SetPoint(32,74,144);
  g_exp_leps->SetPoint(33,75,141);

  g_exp_leps->SetLineColor(CombinationGlob::c_DarkGray);
  g_exp_leps->SetLineWidth(1);
  g_exp_leps->SetFillColor(CombinationGlob::c_BlueT1); //c_LightGray);
  //g_exp_leps->SetFillColor(kPink+6);
  g_exp_leps->GetXaxis()->SetRangeUser(xmin,xmax);
  g_exp_leps->GetXaxis()->SetTitle(xlabel.Data());
  g_exp_leps->GetYaxis()->SetRangeUser(ymin,ymax);
  g_exp_leps->GetYaxis()->SetTitle(ylabel.Data());
  g_exp_leps->GetYaxis()->SetTitleOffset(1.35);

  g_exp_leps->Draw("FSAME");
  g_exp_leps->Draw("LSAME");

  gPad->RedrawAxis();

  return g_exp_leps;
*/
}


TGraph* ol1(double xmin=40, double xmax=840., double ymin=100, double ymax=340., TCanvas* c = 0, TString xlabel = TString("m_{0} [GeV]"), TString ylabel = TString("m_{1/2} [GeV]")){
  
  // Draw exclusion regions for previous experiments (mainly Tevatron)
  
  return lep_chargino2();
  
/*
  TGraph* lepc_curv = lep_chargino();
  int npts = lepc_curv->GetN();
  TGraph* g_exc_lepc = new TGraph(npts+4);
  double x,y,y0;
  for(int i=0; i<npts; i++) {
    lepc_curv->GetPoint(i,x,y);
    g_exc_lepc->SetPoint(i,x,y);
    if(i==0) y0=y;
  }
  g_exc_lepc->SetPoint(npts,0,130);
  g_exc_lepc->SetPoint(npts+1,0,-10);
  g_exc_lepc->SetPoint(npts+2,3000,-10);
  g_exc_lepc->SetPoint(npts+3,3000,130);
  g_exc_lepc->SetLineColor(CombinationGlob::c_DarkGray);
  g_exc_lepc->SetLineWidth(1);
  g_exc_lepc->SetFillColor(CombinationGlob::c_BlueT3);
  g_exc_lepc->GetXaxis()->SetRangeUser(xmin,xmax);
  g_exc_lepc->GetXaxis()->SetTitle(xlabel.Data());
  g_exc_lepc->GetYaxis()->SetRangeUser(ymin,ymax);
  g_exc_lepc->GetYaxis()->SetTitle(ylabel.Data());
  g_exc_lepc->GetYaxis()->SetTitleOffset(1.35);
  return g_exc_lepc ; 
*/
  
} 


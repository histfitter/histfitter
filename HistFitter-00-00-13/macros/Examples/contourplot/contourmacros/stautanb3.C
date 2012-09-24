#include "TGraph.h"
#include "contourmacros/CombinationGlob.C"

TGraph* stautanb3(){

  // Draw exclusion regions for previous experiments (mainly Tevatron)

  TGraph* g_exc_leps = new TGraph(4);
  g_exc_leps->SetPoint(0,-10.,500.);
  g_exc_leps->SetPoint(1,88.,500.);
  g_exc_leps->SetPoint(2,29.,240.);
  g_exc_leps->SetPoint(3,-10.,220.);

  g_exc_leps->SetLineColor(CombinationGlob::c_DarkGray);
  g_exc_leps->SetLineWidth(1);
  g_exc_leps->SetFillColor(CombinationGlob::c_LightGray);
  //g_exc_leps->SetFillColor(kPink+6);

  g_exc_leps->Draw("FSAME");
  g_exc_leps->Draw("LSAME");

  gPad->RedrawAxis();

  return g_exc_leps;
}


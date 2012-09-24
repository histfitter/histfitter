#include "TGraph.h"

TGraph* cms() {
/*
TStyle *plotStyle= new TStyle("PLOT","prettier plots");

// use black on white
gStyle->SetFrameBorderMode(0);
gStyle->SetCanvasBorderMode(0);
gStyle->SetPadBorderMode(0);
gStyle->SetPadColor(0);
gStyle->SetCanvasColor(0);
gStyle->SetStatColor(0);
gStyle->SetFillColor(0);

//=========Macro generated from canvas: c1/c1
//=========  (Tue Jan 11 15:03:55 2011) by ROOT version5.27/06
   TCanvas *c1 = new TCanvas("c1", "c1",10,32,700,500);
   c1->Range(-1.625,-0.375,4.625,3.375);
   c1->SetBorderSize(2);
   c1->SetFrameFillColor(0);
   c1->SetFillColor(0);
   //c1->SetAxisColor(1);

   
   TH1D *frame_9816460__1 = new TH1D("frame_9816460__1","CMS Exclusion Curve",10,0,500);
   frame_9816460__1->SetMinimum(100);
   frame_9816460__1->SetMaximum(500);
   frame_9816460__1->SetDirectory(0);
   frame_9816460__1->SetStats(0);
   frame_9816460__1->GetXaxis()->SetTitle("signal events");
   frame_9816460__1->GetYaxis()->SetTitle("profile log likelihood");
   frame_9816460__1->SetLineColor(1);
   frame_9816460__1->Draw("");
   
*/

   TGraph *graph = new TGraph(29);
   graph->SetName("cmsnlo");
   graph->SetTitle("Projection of nllWithCons");
   graph->SetFillColor(0);

   Int_t ci;   // for color index setting
   ci = TColor::GetColor("#ff0000");
   graph->SetLineColor(1);
   graph->SetLineWidth(2);
   graph->SetPoint( 0, -5,274.5);
   graph->SetPoint( 1, 40,273);
   graph->SetPoint( 2, 60,272);
   graph->SetPoint( 3, 80,271);
   graph->SetPoint( 4,100,270);
   graph->SetPoint( 5,140,269);
   graph->SetPoint( 6,160,268);
   graph->SetPoint( 7,180,266);
   graph->SetPoint( 8,200,265);
   graph->SetPoint( 9,220,262);
   graph->SetPoint(10,230,260);
   graph->SetPoint(11,240,258);
   graph->SetPoint(12,260,252);
   graph->SetPoint(13,280,246);
   graph->SetPoint(14,300,235);
   graph->SetPoint(15,320,222);
   graph->SetPoint(16,340,207);
   graph->SetPoint(17,360,193);
   graph->SetPoint(18,380,182);
   graph->SetPoint(19,400,173);
   graph->SetPoint(20,420,165);
   graph->SetPoint(21,440,160);
   graph->SetPoint(22,460,155);
   graph->SetPoint(23,470,152);
   graph->SetPoint(24,480,148);
   graph->SetPoint(25,490,142);
   graph->SetPoint(26,500,132);
   graph->SetPoint(27,510,120);
   graph->SetPoint(28,523,100);

   TH1F *nll_full_model_1m3j_data_set_1m3j_with_constr_Normmu1__2 = new TH1F("nll_full_model_1m3j_data_set_1m3j_with_constr_Normmu1__2","Projection of nllWithCons",100,-10,510);
   nll_full_model_1m3j_data_set_1m3j_with_constr_Normmu1__2->SetMinimum(90);
   nll_full_model_1m3j_data_set_1m3j_with_constr_Normmu1__2->SetMaximum(510);
   nll_full_model_1m3j_data_set_1m3j_with_constr_Normmu1__2->SetDirectory(0);
   nll_full_model_1m3j_data_set_1m3j_with_constr_Normmu1__2->SetStats(0);
   graph->SetHistogram(nll_full_model_1m3j_data_set_1m3j_with_constr_Normmu1__2);
   
   graph->Draw("l");

   
/*   
   TH1D *frame_9816460__4 = new TH1D("frame_9816460__4","Muon channel: profile log likelihood",10,-1,4);
   frame_9816460__4->SetMinimum(0);
   frame_9816460__4->SetMaximum(3);
   frame_9816460__4->SetDirectory(0);
   frame_9816460__4->SetStats(0);
   frame_9816460__4->GetXaxis()->SetTitle("mu");
   frame_9816460__4->GetYaxis()->SetTitle("Projection of nllWithCons");
   frame_9816460__4->Draw("AXISSAME");
*/   

/*
   TPaveText *pt = new TPaveText(0.01,0.9390678,0.3374713,0.995,"blNDC");
   pt->SetName("title");
   pt->SetBorderSize(2);
   pt->SetFillColor(0);
   TText *text = pt->AddText("CMS: Exclusion curve");
   pt->Draw();
   c1->Modified();
   c1->cd();
   c1->SetSelected(c1);
*/

  gPad->RedrawAxis();

  return graph;
}

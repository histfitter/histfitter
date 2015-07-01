#include "TGraph.h"

TGraph* cdftanb5(){

  Float_t x[20];
  Float_t y[20];
  x[0]=1850;
  x[1]=1815;
  x[2]=x[1]-222;
  x[3]=x[2]-273;
  x[4]=x[3]-6; 
  x[5]=x[4]-116;
  x[6]=x[5]-104;
  x[7]=x[6]-12;
  x[8]=x[7]-140;
  x[9]=x[8]-25;
  x[10]=x[9]-155;
  x[11]=x[10]-67 ;
  x[12]=x[11]-44 ;
  x[13]=x[12]-20 ;
  x[14]=x[13]-60 ;
  x[15]=x[14]-79 ;
  x[16]=x[15]-265;
  x[17]=x[16]-151;
  x[18]=x[17]-76 ;
  x[19]=-30 ;

  y[0]=-40;
  y[1]=443;
  y[2]=y[1]-0;
  y[3]=y[2]+23;
  y[4]=y[3]+2;
  y[5]=y[4]+33;
  y[6]=y[5]+10; 
  y[7]=y[6]+4 ;
  y[8]=y[7]+47;
  y[9]=y[8]+6 ;
  y[10]=y[9]+25;
  y[11]=y[10]+15;
  y[12]=y[11]+35;
  y[13]=y[12]+12;
  y[14]=y[13]+47;
  y[15]=y[14]+32;
  y[16]=y[15]+60;
  y[17]=y[16]-12;
  y[18]=y[17]-24;
  y[19]=-40;
  Float_t scaleX = 600./1815;
  Float_t scaleY = 300./1404;

  for (int i=0;i<20;i++) x[i]=x[i]*scaleX;
  for (int i=0;i<20;i++) y[i]=y[i]*scaleY;
  TGraph* graph = new TGraph(20,x,y);
   // gr->Draw("a*");

  graph->SetLineColor(CombinationGlob::c_DarkGray);
  graph->SetLineWidth(1);

  graph->SetFillColor(CombinationGlob::c_DarkOrange);

/*
   TH1F *nll_full_model_1m3j_data_set_1m3j_with_constr_Normmu1__3 = new TH1F("nll_full_model_1m3j_data_set_1m3j_with_constr_Normmu1__3","Projection of nllWithCons",100,-10,610);
   nll_full_model_1m3j_data_set_1m3j_with_constr_Normmu1__3->SetMinimum(0);
   nll_full_model_1m3j_data_set_1m3j_with_constr_Normmu1__3->SetMaximum(250);
   nll_full_model_1m3j_data_set_1m3j_with_constr_Normmu1__3->SetDirectory(0);
   nll_full_model_1m3j_data_set_1m3j_with_constr_Normmu1__3->SetStats(0);
   graph->SetHistogram(nll_full_model_1m3j_data_set_1m3j_with_constr_Normmu1__3);
*/
   
//   graph->Draw("l");
  graph->Draw("FSAME");
  graph->Draw("LSAME");

  gPad->RedrawAxis();

  return graph;

}


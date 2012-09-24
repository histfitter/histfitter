#include "TGraph.h"

TGraph* d0tanb3muneg() 
{
/*
  // central observed

  Double_t exclu1x[16] = {-10.,-10.,0., 20., 25.,100.,150.,201.5,250.,300.,350.,400.,450.,500.,600.,600.};
  Double_t exclu1y[16] = {-10.,174.,174.,174.,174.,169.,165.,156.,146.,137.5,128.,119.,115.5,113.,113.,-10.};
  TGraph* grex1 = new TGraph(16,exclu1x,exclu1y);
  //grex1->SetLineColor(2);
  //grex1->SetLineWidth(3);

  grex1->SetLineColor(CombinationGlob::c_DarkGray);
  grex1->SetLineWidth(1);
  grex1->SetFillColor(CombinationGlob::c_VLightOrange);
*/

  // down observed (-1 "sigma" theo. signal xsec)

  Double_t exclu4x[16] = {-10., -10., 0., 20., 25.,100.,150.,192.,250.,300.,350.,400.,450.,500.,600., 600.};
  Double_t exclu4y[16] = {-10., 167., 167.,167.,167.,162.,157.,149.,136.,125.5,116.,109.,106.5,105.,105., -10.};
  TGraph* grex1 = new TGraph(16,exclu4x,exclu4y);

  grex1->SetLineColor(CombinationGlob::c_DarkGray);
  grex1->SetLineWidth(1);
  grex1->SetFillColor(CombinationGlob::c_VLightOrange);


/*
  // central expected

  Double_t exclu2x[13] = {0., 20., 25.,100.,150.,200.5,250.,300.,350.,400.,450.,500.,600.};
  Double_t exclu2y[13] = {173.,173.,173.,168.,164.5,155.,147.5,140.,130.,121.,117.,115.,115.};
  TGraph* grex2 = new TGraph(13,exclu2x,exclu2y);
  grex2->SetLineColor(8);
  grex2->SetLineStyle(2);
  grex2->SetLineWidth(3);

  // up observed (+1 "sigma" theo. signal xsec)

  Double_t exclu3x[13] = {0., 20., 25.,  100.,150.,211.5,250.,300.,350.,400.,450.,500.,600.};
  Double_t exclu3y[13] = {181.5,181.5,181.5,177.,174.,165., 157.,150.,140.5,129.,125.5,122.,122.};
  TGraph* grex3 = new TGraph(13,exclu3x,exclu3y);
  grex3->SetLineColor(1);
  grex3->SetLineWidth(2);
  grex3->SetLineStyle(3);

  // down observed (-1 "sigma" theo. signal xsec)

  Double_t exclu4x[13] = {0., 20., 25.,100.,150.,192.,250.,300.,350.,400.,450.,500.,600.};
  Double_t exclu4y[13] = {167.,167.,167.,162.,157.,149.,136.,125.5,116.,109.,106.5,105.,105.};
  TGraph* grex4 = new TGraph(13,exclu4x,exclu4y);
  grex4->SetLineColor(1);
  grex4->SetLineWidth(2);
  grex4->SetLineStyle(3);
*/
 
  //grex1->Draw("l"); //("ALP");

  grex1->Draw("FSAME");
  grex1->Draw("LSAME");

//  grex1->GetHistogram()->GetXaxis()->SetTitle("m_{0} (GeV)");
//  grex1->GetHistogram()->GetYaxis()->SetTitle("m_{1/2} (GeV)");
//  grex1->GetHistogram()->SetAxisRange(100.,200.,"Y");
//  grex1->SetTitle();
/*
  grex2->Draw("LP");
  grex3->Draw("LP");
  grex4->Draw("LP");
*/
  return grex1;
  
}


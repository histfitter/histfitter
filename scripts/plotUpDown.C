/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Macro  : plotUpDown.C                                                          *
 * Created: 24 March 2015                                                         *
 *                                                                                *
 * Description:                                                                   *
 *      Simple macro to plot up and down variations with respect to nominal       *
 *      for specific systematic uncertainty. To be used together with             *
 *      plotSyst.C                                                                *                         
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/


void plotUpDown(TString sam="BG", TString region = "WREl", TString syst="JES", TString var="meffInc", Bool_t norm=kFALSE){
 
  gStyle->SetOptStat(0000000);

  // TFile* f = new TFile("../data/OneLeptonSUSY12_JEShistoSys.root");
  //  TFile* f = new TFile("../data/OneLeptonSUSY12.root");
  //  TFile* f = new TFile("../data/OneLeptonMoriond2013_PowhegAlpgen.root");
  //   plotUpDown("AlpgenW_Np3","TR3JEl","JLow","nJet30");
  
  TFile* f = new TFile("data/MyConfigExample.root");
  
  cout << " file = " < <  f << endl;

  TString nomName = "hBGNom_WREl_obs_meffInc";
  TString upName = "hBGJESHigh_WREl_obs_meffInc";
  TString downName = "hBGJESLow_WREl_obs_meffInc";
  
  if(sam != "BG"){
    nomName.ReplaceAll("BG",sam);
    upName.ReplaceAll("BG",sam);
    downName.ReplaceAll("BG",sam);
  }
  if(region != "WREl"){
    nomName.ReplaceAll("WREl",region);
    upName.ReplaceAll("WREl",region);
    downName.ReplaceAll("WREl",region);
  }
  if(syst != "JES"){
    upName.ReplaceAll("JES",syst);
    downName.ReplaceAll("JES",syst);
  }
  if(var != "meffInc"){
    nomName.ReplaceAll("meffInc",var);
    upName.ReplaceAll("meffInc",var);
    downName.ReplaceAll("meffInc",var);
  }
  
  if(sam == "WZAlpgen" && region == "WREl" && syst=="JMedium"){
    upName.ReplaceAll("meffInc","meffIncNorm");
  }
  if(sam == "WZAlpgen" && region == "WRMu" && syst=="JLow"){
    downName.ReplaceAll("meffInc","meffIncNorm");
  }

  if (norm){
    upName = upName + "Norm";
    downName = downName + "Norm";
  }

  cout << " upName = " << upName <<  "    downName = " << downName << endl;
  

  TH1F* hnom  = (TH1F*)f->Get(nomName);
  TH1F* hup  = (TH1F*)f->Get(upName);
  TH1F* hdown  = (TH1F*)f->Get(downName);

  
  if (!hnom || !hup || !hdown){
    std::cout << endl << " WARNING: one of the histograms does not exist: hnom(" << nomName << ") = " << hnom
	      << "   hup(" << upName << ") = " << hup
      	      << "   hdown(" << downName << ") = " << hdown 
	      << endl << " WILL NOT PLOT THIS " 



	      << "  PLEASE CHECK THE FILENAME AT THE TOP OF plotUpDown.C" << endl;
    return;
  }
  
  hnom->SetName(Form("%s %s %s",hnom->GetName(),syst.Data(),var.Data()));
  hnom->SetTitle(hnom->GetName());
  TCanvas* c  = new TCanvas(Form("c_%s_%s_%s",upName.Data(),syst.Data(),var.Data()),Form("c_%s_%s_%s",upName.Data(),syst.Data(),var.Data()),600,400);
  hnom->SetMarkerColor(kBlack);
  hnom->SetMarkerStyle(20);
  hnom->SetLineWidth(2.);
  hnom->Draw("e");
  hup->SetLineColor(kCyan-3);
  hup->SetLineStyle(kDashed);
  hup->SetMarkerColor(kCyan-3);
  hup->SetMarkerStyle(25);
  hup->SetLineWidth(2.);
  hup->Draw("esame");
  hdown->SetLineColor(kMagenta-3);
  hdown->SetLineStyle(kDotted);
  hdown->SetMarkerColor(kMagenta-3);
  hdown->SetMarkerStyle(26);
  hdown->SetLineWidth(2.);
  hdown->Draw("esame");

  //  Double_t upRange = hnom->GetBinContent(hnom->GetMaximumBin()) * 3.; // hnom->GetYaxis()->GetBinUpEdge(hnom->GetMaximumBin()) * 2.;
  Double_t upRange = hnom->GetBinContent(hnom->GetMaximumBin()) * 1.5; // hnom->GetYaxis()->GetBinUpEdge(hnom->GetMaximumBin()) * 2.;
  Double_t downtmp = hnom->GetBinContent(hnom->GetMinimumBin()); //hnom->GetYaxis()->GetBinLowEdge(hnom->GetMinimumBin());
  Double_t downRange = downtmp;
  if(downtmp != 0.) downRange  /= 2.;
  else downRange = -0.5;

  //  cout << " YAxis xupRange = " << upRange << "  downRange = " << downRange << endl;

  hnom->GetYaxis()->SetRangeUser(downRange,upRange);

  TLegend* leg = new TLegend(0.7,0.75,0.9,0.9,"");
  leg->SetFillStyle(0);
  leg->SetFillColor(0);
  leg->SetBorderSize(0);
  TLegendEntry* entry=leg->AddEntry(hnom,"nominal","lp") ;
  entry=leg->AddEntry(hup,Form("%s up",syst.Data()),"lp") ;
  entry=leg->AddEntry(hdown,Form("%s down",syst.Data()),"lp") ;
  leg->Draw();

  TString canName = c->GetName() ;
  c->SaveAs(canName + ".eps");


  cout << endl <<" Region: " << region << " sample: " << sam << endl ; //<< " syst: " << syst << " var: " << var << endl;

  //  cout << " nbins  " <<hnom->GetNbinsX() << endl;
  for (Int_t i=1; i<hnom->GetNbinsX()+1; i++){
    //  cout << " hnom->GetBinContent(i) = " << hnom->GetBinContent(i) << endl;
    if( (fabs(hnom->GetBinContent(i)) - 0.0001) > 0.){
      cout << " bin:" << i << " MC stat error:  +/- " << hnom->GetBinError(i)
	   << "    bin-value: " << hnom->GetBinContent(i) 
	   << "   MC stat error in %: " << (hnom->GetBinError(i)/hnom->GetBinContent(i)) * 100.
	//<< endl << "         MC stat error:  - " << hnom->GetBinError(i)/hnom->GetBinContent(i)
	   << endl;
    }
  }
  
}

/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/

#include "TFile.h"
#include "TH1.h"
#include "TSystem.h"


void 
makeCountingExperiment(float nsig, float nbg, int obs)
{
  TFile *tf = new TFile("data/counting_exp_data.root","recreate");

  TH1F *h = new TH1F("signal","signal histogram",1,0,1);
  h->Fill(0.5,nsig);
  h->Write("signal");

  TH1F *hb = new TH1F("background","background histogram",1,0,1);
  hb->Fill(0.5,nbg);
  hb->Write("background");

  TH1F *hd = new TH1F("data","data histrogram",1,0,1);
  hd->Fill(0.5,obs);
  hd->Write("data");

  tf->Close();

  //////////////////////////////////////////////////////////////////

  gSystem->Exec("hist2workspace config/example.xml");

  //OneSidedFrequentistUpperLimitWithBands("counting_exp_ratesys_combined_example_model.root","combined","ModelConfig","obsData");  
}


void 
makeCountingExperiment()
{
  makeCountingExperiment(1.0,5,10);
}



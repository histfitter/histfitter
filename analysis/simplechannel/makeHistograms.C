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

void 
makeHistograms()
{
  TFile* example = new TFile("data/example.root","RECREATE");

  TH1F* data = new TH1F("data","data", 1,0,1);
  TH1F* signal = new TH1F("signal","signal histogram (pb)", 1,0,1);
  TH1F* background = new TH1F("background","background histogram (pb)", 1,0,1);

  // run with 1 pb
  data->SetBinContent(1,13);

  signal->SetBinContent(1,5);

  background->SetBinContent(1,10);

  example->Write();
  example->Close();
}


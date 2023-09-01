/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Macro  : fittest.C                                                             *
 * Created: 12 June 2012                                                          *
 *                                                                                *
 * Description:                                                                   *
 *      To fit the "simple channel" counting experiment created at :              *
 *      analysis/simplechannel/                                                   *
 *      To run:                                                                   *
 *      root -b -q fittest.C                                                      *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/

using namespace RooFit;
using namespace RooStats;

/**
To fit the "simple channel" counting experiment created at analysis/simplechannel.
Extracts workspace, fits the datasets in the workspace and plots the dataset and pdf.
Run with root -b -q fittest.C
*/
void
fittest()
{
  // Load the HistFitter library 
  gSystem->Load("libHistFitter.so");

  //Open file containing workspace and retrieve workspace
  TFile *file = TFile::Open("example_channel1_GaussExample_model.root");
  file->ls();
  RooWorkspace* w = (RooWorkspace *)file->Get("channel1"); 

  // 0. Print the contents of the workspace
  w->Print();

  // 1. Useful trick: make all objects in the workspace directly accessible in CINT
  w->exportToCint();
  //  using namespace channel1;

  // --- CUT ---

  // some printout on interesting objects in the workspace - rpplace false by true to see
  //  if (false) {
  //    SigXsecOverSM.Print();
  //    asimovData.Print("v");
  //    channel1_model.printCompactTree();
  //  }

  // 2. Fit the datasets in the workspace
  // first fit the asimov dataset. Are the fit results as expected?
  TString dataName ="obsData";
  RooAbsData * data = w->data(dataName);
  TString asimovName ="asimovData";
  RooAbsData * asimov = w->data(asimovName);

  // retrieve the model
  TString modelSBName = "ModelConfig";
  ModelConfig* sbModel = (ModelConfig*) w->obj(modelSBName);

  //allow a floating luminosity and systematic uncertainty
  //  alpha_syst1.setConstant(false);
  //  Lumi.setConstant(false);

  // fit to data
  RooFitResult* result_data = sbModel->GetPdf()->fitTo(*data);
  // fit to the asimov dataset
  RooFitResult* result = sbModel->GetPdf()->fitTo(*asimov,Save());

  // you can check the status of the fit
  //result->Print();
  cout <<  "Fit status = " << result->status() << " and covariance quality = " << result->covQual() << endl;

  // 3. plot the dataset and pdf
  RooPlot* frame = w->var("obs_x_channel1")->frame();
  asimov->plotOn(frame);
  sbModel->GetPdf()->plotOn(frame);
  frame->Draw();
}



using namespace RooFit;
using namespace RooStats;

void
fittest()
{
  // Load the HistFitter library 
  gSystem->Load("libSusyFitter.so");

  TFile *file = TFile::Open("example_channel1_GaussExample_model.root");
  file->ls();
  RooWorkspace* w = (RooWorkspace *)file->Get("channel1"); 

  // 0. Print the contents of the workspace
  w->Print();

  // 1. Useful trick: make all objects in the workspace directly accessible in CINT
  w->exportToCint();
  using namespace channel1;

  // --- CUT ---

  // some printout on interesting objects in the workspace
  if (false) {
    SigXsecOverSM.Print();
    asimovData.Print("v");
    channel1_model.printCompactTree();
  }

  // 2. Fit the datasets in the workspace
  // first fit the asimov dataset. Are the fit results as expected?
  model_channel1.fitTo(obsData);

  alpha_syst1.setConstant(false);
  Lumi.setConstant(false);

  // then fit the observed dataset
  RooFitResult* result = model_channel1.fitTo(asimovData,Save());

  //result->Print();

  cout <<  "Fit status = " << result->status() << " and covariance quality = " << result->covQual() << endl;

  // 3. plot the dataset and pdf
  RooPlot* frame = obs_x_channel1.frame();
  asimovData.plotOn(frame);
  model_channel1.plotOn(frame);
  frame->Draw();
}



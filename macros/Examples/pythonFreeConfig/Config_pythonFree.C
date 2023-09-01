/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Macro  : Config_pythonFree.C                                                   *
 * Created: 14 November 2012                                                      *
 *                                                                                *
 * Description:                                                                   *
 *      Fits a workspace without requiring a user defined python configuration    *
 *      file. Various plots as before and after fit plots,                        *
 *      likelihood curves and correlation matrices can be produced.               *                            
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/


using namespace std;
using namespace RooFit;
using namespace RooStats;

/**
This macro gives an example on how a workspace can be fitted within HistFitter without relying on a user python configuration file.
Certain information need to be set for this, including the luminosity, the channels constraining the background and the signal regions, if used.
Various style option can also be set.
The macro can plot before and after fit plots, correlation matrices and likelihood curves.
Note that the user will need to modify the name of the file containing the workspace, as well as the names of control and signal regions and other channels,
and the value for the luminosity.
*/
void Config_pythonFree(){

  //Loading HistFitter library
  gSystem->Load("libHistFitter.so");

  //create configMgr instance
  ConfigMgr* mgr = ConfigMgr::getInstance();
  mgr->initialize();

  // set some configMgr options
  mgr->setNToys(1000);   //not used for anything is this example macro
  //mgr->setSeed(1000);   // unless you turn this on, then the rest is done with a toy dataset

  // create FitConfig
  FitConfig* fc = mgr->addFitConfig("testFitConfig");

  //Name of workspace to be opened
  TString wsFileName = "Sig_SU_400_500_0_10_P_combined_NormalMeasurement_model.root";

  // set FitConfig parameters
  fc->m_inputWorkspaceFileName = wsFileName;
  fc->m_lumi = 5.83521; //modify luminosity to correct value
  
  // set background constrain regions - change names to the ones in your workspace
  fc->m_bkgConstrainChannels.push_back("WREl_meffInc");
  fc->m_bkgConstrainChannels.push_back("TREl_meffInc");
  fc->m_bkgConstrainChannels.push_back("WRMu_meffInc");
  fc->m_bkgConstrainChannels.push_back("TRMu_meffInc");
  // SRs taken into account in the fit - modify the names to the names of the signal regions in your workspace
  fc->m_signalChannels.push_back("SR4jTEl_meffInc");
  fc->m_signalChannels.push_back("SR4jTMu_meffInc");
  //  // VRs could be added
  //   fc->m_validationChannels.push_back("SR4jTEl_meffInc");
  //   fc->m_validationChannels.push_back("SR4jTMu_meffInc");

  //specify which plots should be created
  // fit, create _afterFit.root workspace and make plots
  Bool_t drawBeforeFit = kFALSE;
  Bool_t drawAfterFit = kTRUE; 
  Bool_t plotCorrelationMatrix = kFALSE;
  Bool_t plotSeparateComponents = kFALSE; 
  Bool_t plotNLL = kFALSE;
  Util::GenerateFitAndPlot(fc->m_name,  drawBeforeFit,  drawAfterFit,  plotCorrelationMatrix,  plotSeparateComponents,  plotNLL );
  
  // starting with style settings
  // new ChannelStyle
  ChannelStyle* style = new ChannelStyle("WREl_meffInc");
  
  // set data color  (many more per channeloptions available)
  style->setDataColor(kGreen);

  // set samples and respective plot color
  style->addSample( "BG",kYellow-3);
  style->addSample( "TopMcAtNlo",kGreen-9);
  style->addSample( "WZAlpgen",kAzure+1);
  style->addSample( "QCD",kGray+1);
  style->addSample( "Data",kBlack);
  style->addSample( "SU_400_500_0_10_P",kMagenta);

  // add new channelStyle to fitConfig - finished style settings
  fc->m_channelsStyle.push_back(*style);
  
  // draw again, but now with new style for channel WREl_meffInc and also plot correlation matrix of fit
  plotCorrelationMatrix = kTRUE; 
  Util::GenerateFitAndPlot(fc->m_name,  drawBeforeFit,  drawAfterFit,  plotCorrelationMatrix,  plotSeparateComponents,  plotNLL );

}

using namespace std;
using namespace RooFit;
using namespace RooStats;

void Config_pythonFree(){

  gSystem->Load("libSusyFitter.so");

  //create configMgr instance
  ConfigMgr* mgr = ConfigMgr::getInstance();
  mgr->initialize();

  // set some configMgr options
  mgr->setNToys(1000);   //not used for anything is this example macro
  //mgr->setSeed(1000);   // unless you turn this on, then the rest is done with a toy dataset

  // create FitConfig
  FitConfig* fc = mgr->addFitConfig("testFitConfig");

  TString wsFileName = "~koutsman/public/SUSY/Sig_SU_400_500_0_10_P_combined_NormalMeasurement_model.root";  //on lxplus

  // set FitConfig parameters
  fc->m_inputWorkspaceFileName = wsFileName;
  fc->m_lumi = 5.83521;
  
  // set background constrain regions
  fc->m_bkgConstrainChannels.push_back("WREl_meffInc");
  fc->m_bkgConstrainChannels.push_back("TREl_meffInc");
  fc->m_bkgConstrainChannels.push_back("WRMu_meffInc");
  fc->m_bkgConstrainChannels.push_back("TRMu_meffInc");
  // SRs taken into account in the fit
  fc->m_signalChannels.push_back("SR4jTEl_meffInc");
  fc->m_signalChannels.push_back("SR4jTMu_meffInc");
  //  // SRs NOT taken into account in the fit
  //   fc->m_validationChannels.push_back("SR4jTEl_meffInc");
  //   fc->m_validationChannels.push_back("SR4jTMu_meffInc");

  // fit, create _afterFit.root workspace and make plots
  Bool_t drawBeforeFit = kFALSE;
  Bool_t drawAfterFit = kTRUE; 
  Bool_t plotCorrelationMatrix = kFALSE;
  Bool_t plotSeparateComponents = kFALSE; 
  Bool_t plotNLL = kFALSE;
  Util::GenerateFitAndPlot(fc->m_name,  drawBeforeFit,  drawAfterFit,  plotCorrelationMatrix,  plotSeparateComponents,  plotNLL );
  
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

  // add new channelStyle to fitConfig
  fc->m_channelsStyle.push_back(*style);
  
  // draw again, but now with new style for channel WREl_meffInc and also plot correlation matrix of fit
  plotCorrelationMatrix = kTRUE; 
  Util::GenerateFitAndPlot(fc->m_name,  drawBeforeFit,  drawAfterFit,  plotCorrelationMatrix,  plotSeparateComponents,  plotNLL );

}

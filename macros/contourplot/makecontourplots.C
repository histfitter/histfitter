#include "contourmacros/SUSY_m0_vs_m12_all_withBand_cls.C"

void makecontourplots(const TString& combo = "all") 
{
  bool showsignal(false);
  int  discexcl; // 0=discovery, 1=exclusion
  bool showtevatron(true);
  bool showcms(false);
  bool doOneSigmaBand(true);
  bool showfixSigXSecBand(true);
  int applyfix(0);

  TString infile;

  // simple channel contour plot

  infile = "SoftLeptonMoriond2013_SR1a_StopBCharDeg_20gev_fixSigXSecNominal_hypotest__1_harvest_list.root";
  (void) SUSY_m0_vs_m12_all_withBand_cls(infile.Data(),infile.Data(),infile.Data(), "", "SR1a, 20 GeV", 14.1, showsignal, discexcl=1, showtevatron, showcms, doOneSigmaBand, showfixSigXSecBand, channel=2 );

  infile = "SoftLeptonMoriond2013_SR1b_StopBCharDeg_20gev_fixSigXSecNominal_hypotest__1_harvest_list.root";
  (void) SUSY_m0_vs_m12_all_withBand_cls(infile.Data(),infile.Data(),infile.Data(), "", "SR1b, 20 GeV", 14.1, showsignal, discexcl=1, showtevatron, showcms, doOneSigmaBand, showfixSigXSecBand, channel=2 );

  infile = "SoftLeptonMoriond2013_SR2a_StopBCharDeg_20gev_fixSigXSecNominal_hypotest__1_harvest_list.root";
  (void) SUSY_m0_vs_m12_all_withBand_cls(infile.Data(),infile.Data(),infile.Data(), "", "SR2a, 20 GeV", 14.1, showsignal, discexcl=1, showtevatron, showcms, doOneSigmaBand, showfixSigXSecBand, channel=2 );

  infile = "SoftLeptonMoriond2013_SR2b_StopBCharDeg_20gev_fixSigXSecNominal_hypotest__1_harvest_list.root";
  (void) SUSY_m0_vs_m12_all_withBand_cls(infile.Data(),infile.Data(),infile.Data(), "", "SR2b, 20 GeV", 14.1, showsignal, discexcl=1, showtevatron, showcms, doOneSigmaBand, showfixSigXSecBand, channel=2 );


  infile = "SoftLeptonMoriond2013_SR1a_StopBCharDeg_5gev_fixSigXSecNominal_hypotest__1_harvest_list.root";
  (void) SUSY_m0_vs_m12_all_withBand_cls(infile.Data(),infile.Data(),infile.Data(), "", "SR1a, 5 GeV", 14.1, showsignal, discexcl=1, showtevatron, showcms, doOneSigmaBand, showfixSigXSecBand, channel=2 );

  infile = "SoftLeptonMoriond2013_SR1b_StopBCharDeg_5gev_fixSigXSecNominal_hypotest__1_harvest_list.root";
  (void) SUSY_m0_vs_m12_all_withBand_cls(infile.Data(),infile.Data(),infile.Data(), "", "SR1b, 5 GeV", 14.1, showsignal, discexcl=1, showtevatron, showcms, doOneSigmaBand, showfixSigXSecBand, channel=2 );

  infile = "SoftLeptonMoriond2013_SR2a_StopBCharDeg_5gev_fixSigXSecNominal_hypotest__1_harvest_list.root";
  (void) SUSY_m0_vs_m12_all_withBand_cls(infile.Data(),infile.Data(),infile.Data(), "", "SR2a, 5 GeV", 14.1, showsignal, discexcl=1, showtevatron, showcms, doOneSigmaBand, showfixSigXSecBand, channel=2 );

  infile = "SoftLeptonMoriond2013_SR2b_StopBCharDeg_5gev_fixSigXSecNominal_hypotest__1_harvest_list.root";
  (void) SUSY_m0_vs_m12_all_withBand_cls(infile.Data(),infile.Data(),infile.Data(), "", "SR2b, 5 GeV", 14.1, showsignal, discexcl=1, showtevatron, showcms, doOneSigmaBand, showfixSigXSecBand, channel=2 );

}


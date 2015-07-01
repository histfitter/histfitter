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

  // simple channel contour plot
  (void) SUSY_m0_vs_m12_all_withBand_cls("MySimpleChannelAnalysisOutput_fixSigXSecNominal_hypotest__1_harvest_list.root","MySimpleChannelAnalysisOutput_fixSigXSecUp_hypotest__1_harvest_list.root", "MySimpleChannelAnalysisOutput_fixSigXSecDown_hypotest__1_harvest_list.root","","Simple channel example", 0.001, showsignal, discexcl=1, showtevatron, showcms, doOneSigmaBand, showfixSigXSecBand, channel=2 );

}




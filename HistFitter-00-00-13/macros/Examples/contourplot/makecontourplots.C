#include "contourmacros/SUSY_m0_vs_m12_all_withBand_cls.C"

void makecontourplots(const TString& combo = "all") 
{
  bool showsignal(false);
  int  discexcl; // 0=discovery, 1=exclusion
  bool showtevatron(true);
  bool showcms(false);
  bool doOneSigmaBand(true);

  // simple channel contour plot
  (void) SUSY_m0_vs_m12_all_withBand_cls("MySimpleChannelAnalysisOutput_hypotest__1_harvest_list.root", "", "Tutorial contour", 4.7, showsignal, discexcl=1, showtevatron, showcms, doOneSigmaBand );
}



#include "contourmacros/SUSY_m0_vs_m12_all_withBand_clsSM.C"

void makecontourplots_SM(const TString& combo = "all") 
{
  bool showsignal(true);
  int  discexcl; // 0=discovery, 1=exclusion
  bool showtevatron(false);
  bool showcms(false);
  bool doOneSigmaBand(true);
  int applyfix(0);

  // simple channel contour plot
  (void) SUSY_m0_vs_m12_all_withBand_cls("MySoftOneLeptonKtScaleFitMetMeffR17_Output_hypotest__1_harvest_list.root", "", "Simple channel example", 4.7, showsignal, discexcl=1, showtevatron, showcms, doOneSigmaBand, channel=2 );
  //(void) SUSY_m0_vs_m12_all_withBand_cls("MyOneLeptonKtScaleFitR17_Output_hypotest__1_harvest_list.root", "", "Simple channel example", 4.7, showsignal, discexcl=1, showtevatron, showcms, doOneSigmaBand, channel=2 );
  //(void) SUSY_m0_vs_m12_all_withBand_cls("sm5OR_list.root", ""/*"1lexp_list.root"*/, "1 lepton, combination",   1035, showsignal, discexcl=1, showtevatron, showcms,       doOneSigmaBand, channel=2 );
}       


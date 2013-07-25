#include "contourmacros/m0_vs_m12_nofloat.C"

void makecontourhists(const TString& combo = "all" /*"0lepton"*/ /*"1lepton"*/) 
{
/*
-rw-r--r-- 1 mbaak zp  3600 Jan 18 11:53 SoftLeptonMoriond2013_SR1a_StopBCharDeg_20gev_fixSigXSecNominal_hypotest__1_harvest_list
-rw-r--r-- 1 mbaak zp 14163 Jan 18 11:53 SoftLeptonMoriond2013_SR1b_StopBCharDeg_20gev_fixSigXSecNominal_hypotest__1_harvest_list
-rw-r--r-- 1 mbaak zp 12600 Jan 18 11:53 SoftLeptonMoriond2013_SR2a_StopBCharDeg_20gev_fixSigXSecNominal_hypotest__1_harvest_list
-rw-r--r-- 1 mbaak zp  9894 Jan 18 11:53 SoftLeptonMoriond2013_SR2b_StopBCharDeg_20gev_fixSigXSecNominal_hypotest__1_harvest_list
-rw-r--r-- 1 mbaak zp 15750 Jan 18 11:53 SoftLeptonMoriond2013_SR1a_StopBCharDeg_5gev_fixSigXSecNominal_hypotest__1_harvest_list
-rw-r--r-- 1 mbaak zp 13725 Jan 18 11:53 SoftLeptonMoriond2013_SR1b_StopBCharDeg_5gev_fixSigXSecNominal_hypotest__1_harvest_list
-rw-r--r-- 1 mbaak zp 16875 Jan 18 11:53 SoftLeptonMoriond2013_SR2a_StopBCharDeg_5gev_fixSigXSecNominal_hypotest__1_harvest_list
-rw-r--r-- 1 mbaak zp  8544 Jan 18 11:53 SoftLeptonMoriond2013_SR2b_StopBCharDeg_5gev_fixSigXSecNominal_hypotest__1_harvest_list
*/
  const char* hf = m0_vs_m12_nofloat("SoftLeptonMoriond2013_SRs2LmUED2Lfilter__fixSigXSecNominal_hypotest__1_harvest_list");

  return;

  const char* ehistfile = m0_vs_m12_nofloat("SoftLeptonMoriond2013_SR1a_StopBCharDeg_20gev_fixSigXSecNominal_hypotest__1_harvest_list");
  const char* ehistfile = m0_vs_m12_nofloat("SoftLeptonMoriond2013_SR1b_StopBCharDeg_20gev_fixSigXSecNominal_hypotest__1_harvest_list");
  const char* ehistfile = m0_vs_m12_nofloat("SoftLeptonMoriond2013_SR2a_StopBCharDeg_20gev_fixSigXSecNominal_hypotest__1_harvest_list");
  const char* ehistfile = m0_vs_m12_nofloat("SoftLeptonMoriond2013_SR2b_StopBCharDeg_20gev_fixSigXSecNominal_hypotest__1_harvest_list");

  const char* ehistfile = m0_vs_m12_nofloat("SoftLeptonMoriond2013_SR1a_StopBCharDeg_5gev_fixSigXSecNominal_hypotest__1_harvest_list");
  const char* ehistfile = m0_vs_m12_nofloat("SoftLeptonMoriond2013_SR1b_StopBCharDeg_5gev_fixSigXSecNominal_hypotest__1_harvest_list");
  const char* ehistfile = m0_vs_m12_nofloat("SoftLeptonMoriond2013_SR2a_StopBCharDeg_5gev_fixSigXSecNominal_hypotest__1_harvest_list");
  const char* ehistfile = m0_vs_m12_nofloat("SoftLeptonMoriond2013_SR2b_StopBCharDeg_5gev_fixSigXSecNominal_hypotest__1_harvest_list");

}




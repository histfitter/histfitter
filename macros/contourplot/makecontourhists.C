#include "contourmacros/m0_vs_m12_nofloat.C"

/********************************

REMEMBER that this file uses summary_harvest_tree_description.h 
to determine how to read your list files.  You will need to regenerate
that file in order to read a list file with a different format from
makelistfiles.C

********************************/

void makecontourhists(const TString& combo = "all" ) 
{
  const char* ehistfile;
  ehistfile = m0_vs_m12_nofloat("Merged_Output_1_hypotest__1_harvest_list");
  ehistfile = m0_vs_m12_nofloat("Merged_Output_2_hypotest__1_harvest_list");
}


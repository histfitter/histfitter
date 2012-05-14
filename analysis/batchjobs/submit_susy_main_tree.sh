#!/bin/bash

rm /afs/cern.ch/atlas/project/cern/susy/users/jlorenz/MyOneLeptonKtScaleFitR17_Sig_SU_*_combined_NormalMeasurement_model.root
rm /afs/cern.ch/atlas/project/cern/susy/users/jlorenz/out_tree_SU_*.log

rm -r /afs/cern.ch/atlas/project/cern/susy/users/jlorenz/SU_*_hypotestresult
rm /afs/cern.ch/atlas/project/cern/susy/users/jlorenz/out_SU_*.log


for ds in `cat susy_points4.txt `; do sh ./submit_susy_tree.sh $ds; done

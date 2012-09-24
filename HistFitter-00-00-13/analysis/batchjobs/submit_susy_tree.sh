#!/bin/bash

in_ds=$1

echo $in_ds

out_ds=${in_ds%%,*}

#sh runSusyLimitBatch.sh -p '/afs/cern.ch/user/j/jlorenz/scratch0/SusyFitter_trunkversion' -g $in_ds /afs/cern.ch/user/j/jlorenz/scratch0/SusyFitter_trunkversion/test.log

bsub -q 1nd -e /afs/cern.ch/atlas/project/cern/susy/users/jlorenz/out_tree_${out_ds}.log -o /afs/cern.ch/atlas/project/cern/susy/users/jlorenz/out_tree_${out_ds}.log runSusyLimitBatch2.sh -p '/afs/cern.ch/user/j/jlorenz/scratch0/SusyFitter_trunkversion' -g $in_ds /afs/cern.ch/user/j/jlorenz/scratch0/SusyFitter_trunkversion/test.log 

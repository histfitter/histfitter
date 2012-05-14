#!/bin/bash

in_ds=$1

echo $in_ds

mkdir -p -v /afs/cern.ch/atlas/project/cern/susy/users/jlorenz/${in_ds}_hypotestresult

#sh runSusyLimitBatch.sh -p '/afs/cern.ch/user/j/jlorenz/scratch0/SusyFitter_trunkversion' -g $in_ds /afs/cern.ch/user/j/jlorenz/scratch0/SusyFitter_trunkversion/test.log

bsub -q 1nd -e /afs/cern.ch/atlas/project/cern/susy/users/jlorenz/out_${in_ds}.log -o /afs/cern.ch/atlas/project/cern/susy/users/jlorenz/out_${in_ds}.log runSusyLimitBatch3.sh -p '/afs/cern.ch/user/j/jlorenz/scratch0/SusyFitter_trunkversion' -g $in_ds /afs/cern.ch/user/j/jlorenz/scratch0/SusyFitter_trunkversion/test.log 

# setup ROOT
# check Root environment setup. Allow for external setup script.
if [ ! $ROOTSYS ]; then
  export CWD=$PWD
  #cd /afs/cern.ch/atlas/groups/susy/1lepton/root/root-532-patches
  cd /afs/cern.ch/atlas/offline/external/FullChainTest/tier0/test/mbaak/root/root-v5.32.02
  #cd /afs/cern.ch/atlas/groups/susy/1lepton/root/root-v5-32-02
  source bin/thisroot.sh
  cd $CWD
fi

# check Root environment setup again
if [ ! $ROOTSYS ]; then
  echo "Warning: No valid Root environment (ROOTSYS) defined. Please do so first!"
  return
fi

if [ ! $LD_LIBRARY_PATH ]; then
  echo "Warning: so far you haven't setup your ROOT enviroment properly (no LD_LIBRARY_PATH)"
  return
fi

# setup combination package
export HISTFITTER=$PWD
export SUSYFITTER=$PWD # for backwards compatibility

# put root & python stuff into PATH, LD_LIBRARY_PATH
export PATH=$HISTFITTER/bin:$HISTFITTER/scripts:${PATH}

export LD_LIBRARY_PATH=$HISTFITTER/lib:${LD_LIBRARY_PATH}

# PYTHONPATH contains all directories that are used for 'import bla' commands
export PYTHONPATH=$HISTFITTER/python:$HISTFITTER/scripts:$HISTFITTER/macros:$HISTFITTER/lib:$HISTFITTER/analysis/ZeroLepton/python:$PYTHONPATH

export PATH=$PYTHONPATH/bin:$ROOTSYS/bin:$PATH
export LD_LIBRARY_PATH=$PYTHONPATH/lib:$LD_LIBRARY_PATH
export PYTHONPATH=$ROOTSYS/lib:$PYTHONPATH


# set SVN path to defaults
export SVNOFF="svn+ssh://svn.cern.ch/reps/atlasoff"
export SVNGRP="svn+ssh://svn.cern.ch/reps/atlasgrp"
export SVNUSR="svn+ssh://svn.cern.ch/reps/atlasusr"
export SVNROOT="svn+ssh://svn.cern.ch/reps/atlasoff"

# Hack for mac ?
export LC_ALL=C 

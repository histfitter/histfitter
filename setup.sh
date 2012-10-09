# setup ROOT
# check Root environment setup. Allow for external setup script.

source ~/bin/root-v5-34-patches/bin/thisroot.sh

if [ ! $ROOTSYS ]; then
  export CWD=$PWD
  # first, setup gcc to version 4.3
  source /afs/cern.ch/sw/lcg/external/gcc/4.3.2/x86_64-slc5/setup.sh
  # setup corresponding root
  cd /afs/cern.ch/atlas/offline/external/FullChainTest/tier0-vol3/test/mbaak/root/root-5.32.02b
  source bin/thisroot.sh
  # setup xrootd
  export BUILD=x86_64-slc5-gcc43-opt
  export PATH=/afs/cern.ch/sw/lcg/external/xrootd/3.1.0p2/$BUILD/bin:$PATH
  export LD_LIBRARY_PATH=/afs/cern.ch/sw/lcg/external/xrootd/3.1.0p2/$BUILD/lib64:$LD_LIBRARY_PATH
  # hack: libNetx library from pre=installed root version
  export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/afs/cern.ch/sw/lcg/app/releases/ROOT/5.32.02/$BUILD/root/lib
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
export SVNTEST="svn+ssh://svn.cern.ch/reps/atlastest"
export SVNROOT="svn+ssh://svn.cern.ch/reps/atlasoff"
export SVNPHYS="svn+ssh://svn.cern.ch/reps/atlasphys"

# Hack for mac ?
export LC_ALL=C 

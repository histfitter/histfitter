# setup ROOT
# check Root environment setup. Allow for external setup script.

export BUILD="x86_64-slc5-gcc43-opt"
export ROOTVERSION="5.34.03"

# Must have gcc and python setup outside of ROOTSYS def for batch running!
# This section here is cern specific.
if [[ `hostname -s` = lx*.cern.ch ]]; then 
    #don't check for *.cern.ch - any machine at CERN, incl. your laptop, has that hostname!
    
    # first, setup gcc to version 4.3
    source /afs/cern.ch/sw/lcg/external/gcc/4.3.2/x86_64-slc5/setup.sh
    # second, setup an uptodate python version
    export PATH="/afs/cern.ch/sw/lcg/external/Python/2.6.5/$BUILD/bin:${PATH}"
    export LD_LIBRARY_PATH="/afs/cern.ch/sw/lcg/external/Python/2.6.5/$BUILD/lib:${LD_LIBRARY_PATH}"
fi

# the root-setup section here is cern specific
if [ ! $ROOTSYS ]; then
  export CWD=$PWD
  # setup corresponding root
  cd /afs/cern.ch/atlas/offline/external/FullChainTest/tier0/test/mbaak/root/root-$ROOTVERSION
  source bin/thisroot.sh
  cd $CWD
  # setup xrootd on top of this
  export PATH=/afs/cern.ch/sw/lcg/external/xrootd/3.1.0p2/$BUILD/bin:$PATH
  export LD_LIBRARY_PATH=/afs/cern.ch/sw/lcg/external/xrootd/3.1.0p2/$BUILD/lib64:$LD_LIBRARY_PATH
  # hack: libNetx library from pre-installed root version
  export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/afs/cern.ch/sw/lcg/app/releases/ROOT/$ROOTVERSION/$BUILD/root/lib
fi

# check Root environment setup 
if [ ! $ROOTSYS ]; then
  echo "Warning: No valid Root environment (ROOTSYS) defined. Please do so first!"
  return
fi

if [ ! $LD_LIBRARY_PATH ]; then
  echo "Warning: so far you haven't setup your ROOT enviroment properly (no LD_LIBRARY_PATH)"
  return
fi

# setup HistFitter package
export HISTFITTER=$PWD
export SUSYFITTER=$PWD # for backwards compatibility

# put root & python stuff into PATH, LD_LIBRARY_PATH
export PATH=$HISTFITTER/bin:$HISTFITTER/scripts:${PATH}
export LD_LIBRARY_PATH=$HISTFITTER/lib:${LD_LIBRARY_PATH}
# PYTHONPATH contains all directories that are used for 'import bla' commands
export PYTHONPATH=$HISTFITTER/python:$HISTFITTER/scripts:$HISTFITTER/macros:$HISTFITTER/lib:$PYTHONPATH

# set SVN path to defaults
export SVNTEST="svn+ssh://svn.cern.ch/reps/atlastest"
export SVNROOT="svn+ssh://svn.cern.ch/reps/atlasoff"
export SVNPHYS="svn+ssh://svn.cern.ch/reps/atlasphys"

# Hack for ssh from mac 
export LC_ALL=C 


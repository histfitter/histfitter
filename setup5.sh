# setup ROOT
# check Root environment setup. Allow for external setup script.

export BUILD="x86_64-slc5-gcc46-opt"
export ROOTVERSION="5.34.09"
export CERNPREFIX="/afs/cern.ch/"
export PYTHONVERSION="2.7.3"
export GCCVERSION="4.6"

# Must have gcc and python setup outside of ROOTSYS def for batch running!
# This section here is cern specific.

if [[ `hostname -f` = b*.cern.ch ]] || [[ `hostname -f` = l*.cern.ch ]]; then 
    #don't check for *.cern.ch - any machine at CERN, incl. your laptop, has that hostname!
    echo "INFO: hostname matches l*.cern.ch: setting up gcc and python from afs"
    # first, setup gcc to version 4.3
    echo "Setting up gcc version ${GCCVERSION} ..."
    source $CERNPREFIX/sw/lcg/external/gcc/${GCCVERSION}/x86_64-slc5/setup.sh
    # second, setup an uptodate python version
    echo "Setting up python version ${PYTHONVERSION} ..."
    export PATH="$CERNPREFIX/sw/lcg/external/Python/${PYTHONVERSION}/$BUILD/bin:${PATH}"
    export LD_LIBRARY_PATH="$CERNPREFIX/sw/lcg/external/Python/${PYTHONVERSION}/$BUILD/lib:${LD_LIBRARY_PATH}"
fi

# the root-setup section here is cern specific
if [ ! $ROOTSYS ]; then
  echo "Setting up ROOT ${ROOTVERSION} ..."
  echo "With build ${BUILD} ..."
  export CWD=$PWD
  # setup corresponding root
  cd $CERNPREFIX/atlas/offline/external/FullChainTest/tier0/test/mbaak/root/root-$ROOTVERSION/
  #cd $CERNPREFIX/sw/lcg/app/releases/ROOT/$ROOTVERSION/$BUILD/root/
  source bin/thisroot.sh
  cd $CWD
  # setup xrootd on top of this
  export PATH=$CERNPREFIX/sw/lcg/external/xrootd/3.1.0p2/$BUILD/bin:$PATH
  export LD_LIBRARY_PATH="$CERNPREFIX/sw/lcg/external/xrootd/3.1.0p2/$BUILD/lib64:$LD_LIBRARY_PATH"
  # hack for xrootd: libNetx library from pre-installed root version
  export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$CERNPREFIX/sw/lcg/app/releases/ROOT/$ROOTVERSION/$BUILD/root/lib"
  # missing libraries on lxbatch machines
  export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$CERNPREFIX/atlas/offline/external/FullChainTest/tier0/test/mbaak/root/extlibs64"
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
export HF=$PWD
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


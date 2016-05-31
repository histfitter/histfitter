# setup ROOT
# check Root environment setup. Allow for external setup script.

export BUILD="x86_64-slc6-gcc49-opt"
export PYTHONBUILD="x86_64-slc6-gcc48-opt"
export ROOTVERSION="6.06.04"
export CERNPREFIX="/afs/cern.ch/"
export PYTHONVERSION="2.7.4"
export GCCVERSION="4.9.3"

# Must have gcc and python setup outside of ROOTSYS def for batch running!
# This section here is cern specific.

if [[ `hostname -f` = b*.cern.ch ]] || [[ `hostname -f` = l*.cern.ch ]]; then 
    #don't check for *.cern.ch - any machine at CERN, incl. your laptop, has that hostname!
    echo "INFO: hostname matches l*.cern.ch: setting up gcc and python from afs"
    # first, setup gcc 
    echo "Setting up gcc version ${GCCVERSION} ..."
    source $CERNPREFIX/sw/lcg/external/gcc/${GCCVERSION}/x86_64-slc6/setup.sh
    # second, setup an uptodate python version
    echo "Setting up python version ${PYTHONVERSION} ..."
    export PATH="$CERNPREFIX/sw/lcg/external/Python/${PYTHONVERSION}/$PYTHONBUILD/bin:${PATH}"
    export LD_LIBRARY_PATH="$CERNPREFIX/sw/lcg/external/Python/${PYTHONVERSION}/$PYTHONBUILD/lib:${LD_LIBRARY_PATH}"
fi

# the root-setup section here is cern specific
if [ ! $ROOTSYS ]; then
  echo "Setting up ROOT ${ROOTVERSION} ..."
  echo "With build ${BUILD} ..."
  export CWD=$PWD
  # setup corresponding root
  #cd $CERNPREFIX/atlas/offline/external/FullChainTest/tier0/test/mbaak/root/root_v$ROOTVERSION/
  cd $CERNPREFIX/sw/lcg/app/releases/ROOT/$ROOTVERSION/$BUILD/root/
  ###cd $CERNPREFIX/atlas/offline/external/FullChainTest/tier0/test/mbaak/root/root-v5-34/
  ###cd $CERNPREFIX/work/g/gbesjes/root-v5-34-patches
  #cd $CERNPREFIX/atlas/offline/external/FullChainTest/tier0/test/mbaak/root/root-v5-34-trunk/
  source bin/thisroot.sh
  cd $CWD
  # xrootd setup
  #source /afs/cern.ch/sw/lcg/app/releases/ROOT/$ROOTVERSION/$BUILD/root/bin/setxrd.sh /afs/cern.ch/sw/lcg/external/xrootd/3.2.7/$BUILD
  ## setup xrootd on top of this
  #export PATH=$CERNPREFIX/sw/lcg/external/xrootd/3.2.7/$BUILD/bin:$PATH
  #export LD_LIBRARY_PATH="$CERNPREFIX/sw/lcg/external/xrootd/3.2.7/$BUILD/lib64:$LD_LIBRARY_PATH"
  ## hack for xrootd: libNetx library from pre-installed root version
  #export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$CERNPREFIX/sw/lcg/app/releases/ROOT/$ROOTVERSION/$BUILD/root/lib"
  ## missing libraries on lxbatch machines
  #export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$CERNPREFIX/atlas/offline/external/FullChainTest/tier0/test/mbaak/root/extlibs64"
fi

scriptname=${BASH_SOURCE:-$0}
DIR=$( cd "$( dirname "${scriptname}" )" && pwd )

source $DIR/setup.sh

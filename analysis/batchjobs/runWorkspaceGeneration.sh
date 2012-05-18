 #!/bin/sh

## Check arguments
if [ $# -lt 1 ] ; then
   echo "Usage: runSusyLimitBatch.sh [-d] [-p <setupDir>] [-g <point>] [-c <config>] [-w <workspaceOutDir>]<logfile> " $#
   exit 1
fi

## Intercept dryrun option if given
DRYRUN=0
if [ "$1" = "-d" ] ; then
  DRYRUN=1
  shift
fi

## SusyFitter dir
SUSYDIR="/afs/cern.ch/atlas/groups/susy/1lepton/SusyFitter"
if [ "$1" = "-p" ] ; then
  SUSYDIR=$2
  shift 2
fi

ARGS=""
if [ "$1" = "-g" ]; then
  ARGS=$2
  shift 2
fi

MYCONF=""
if [ "$1" = "-c" ]; then
  MYCONF=$2
  shift 2
fi

WSOUT=""
if [ "$1" = "-w" ]; then
  WSOUT=$2
  shift 2
fi




LOGFILE=$1
#rm -f ${LOGFILE} ${LOGFILE}.gz
shift 1


## setup path
XCWD=$PWD
cd $SUSYDIR
source setup.sh
cd $XCWD

echo "current directory:"
pwd


if [ ! -e "results/" ]
then
        mkdir -v results
fi

if [ ! -e "data/" ]
then
        mkdir -v data
fi

if [ ! -e "config/" ]
then
        mkdir -v config
	cp /afs/cern.ch/user/j/jlorenz/scratch0/SusyFitter_000208/config/HistFactorySchema.dtd config/.
fi

echo "directory contains:"
#ls -lh

#mkdir -p -v /afs/cern.ch/user/j/jlorenz/scratch0/susyresults/$ARGS_hypotestresult 2>&1


RUNCMD="python $SUSYDIR/scripts/HistFitter_onepoint.py -t -w -g ${ARGS} $SUSYDIR/python/${MYCONF}"

echo
echo ">> Now running command:"
echo ">> ===================="
echo "$RUNCMD"
echo 

if [ $DRYRUN -ne 1 ]; then
  $RUNCMD 
  # 2>&1 | tee $LOGFILE
  #gzip $LOGFILE
fi

cp results/*Sig*_combined_BasicMeasurement_model.root ${WSOUT}
#echo '_file0->ls(); gSystem->Exit(0);' | root -b data/MyOneLeptonKtScaleFitR17.root

echo
echo ">> Finished command:"
echo ">> ================="
echo "$RUNCMD"
echo

#if [ $DRYRUN -ne 1 ]; then
#  echo ">> logfile stored as:"
#  echo ">> ===================="
#  echo "${LOGFILE}.gz"
#  echo
#fi

#!/bin/sh

## Check arguments
if [ $# -lt 1 ] ; then
   echo "Usage: runSusyLimitBatch.sh [-d] [-p <setupDir>] [-g <point>] [-r <signal region>] <logfile> " 
   exit 1
fi

## Intercept dryrun option if given
DRYRUN=0
if [ "$1" = "-d" ] ; then
  DRYRUN=1
  shift
fi

## SusyFitter dir
SUSYDIR="/afs/cern.ch/user/m/mbaak/Work/private/HistFitterUser"  ###"/afs/cern.ch/atlas/groups/susy/1lepton/SusyFitter"
if [ "$1" = "-p" ] ; then
  SUSYDIR=$2
  shift 2
fi

ARGS="1000_160_60"
if [ "$1" = "-g" ]; then
  ARGS=$2
  shift 2
fi

SR="SRs1L,SM_GG1step"
if [ "$1" = "-r" ]; then
  SR=$2
  shift 2
fi

SRSTR=$SR
SRSTR=`echo $SRSTR | sed 's/,/_/'`
SRSTR=`echo $SRSTR | sed 's/,/_/'`

LOGFILE=$1
rm -f ${LOGFILE} ${LOGFILE}.gz
shift 1

date
hostname

## setup path
echo "Now sourcing setup:"
XCWD=$PWD
cd $SUSYDIR

export HISTFITTERUSER=$PWD
export SUSYFITTERUSER=$PWD # backwards compatibility

cd ../HistFitter # doing a gamble here on HistFitter location
source setup.sh
cd $HISTFITTERUSER

if [ ! $HISTFITTER ]; then
  echo "Warning: No valid HISTFITTER setup detected. Please do so first!"
  return
fi

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
	cp $SUSYDIR/MET_jets_leptons/config/HistFactorySchema.dtd config/
fi

echo "directory contains:"
ls -lh

#mkdir -p -v /afs/cern.ch/work/d/dxu/scratch0/susyresults/$ARGS_hypotestresult 2>&1
#echo "rootsyst = "$ROOTSYS

RUNCMD="HistFitter.py -p -F excl -r ${SR} -g ${ARGS} $SUSYDIR/MET_jets_leptons/python/ZLSoftLepton2_OneBin2012.py "

echo ">> ===================="
echo ">> Now running command:"
echo ">> ===================="
echo "$RUNCMD"
echo 

if [ $DRYRUN -ne 1 ]; then
  $RUNCMD
  #$RUNCMD 2>&1 | tee $LOGFILE
  #gzip $LOGFILE
fi

ls *
ls */*
ls */*/*

pwd

cp -r results/* /afs/cern.ch/user/m/mbaak/scratch0/Work/Susy/output/
cp  results/SoftLeptonMoriond2013_${SRSTR}_${ARGS}/*  /afs/cern.ch/user/m/mbaak/scratch0/Work/Susy/output/ 

echo ">> ================="
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

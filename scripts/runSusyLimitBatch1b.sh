#!/bin/sh

## Check arguments
if [ $# -lt 1 ] ; then
   echo "Usage: runSusyLimitBatch.sh [-d] [-p <setupDir>] [-g <point>] [-r <signal region>] [-c cmd] [-o <outputdir>] <configfile> " 
   exit 1
fi

## Intercept dryrun option if given
DRYRUN=0
if [ "$1" = "-d" ] ; then
  DRYRUN=1
  shift
fi

## SusyFitter dir
SUSYDIR="/afs/cern.ch/user/m/mbaak/Work/private/HistFitter"  
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

CMD="-twp"
if [ "$1" = "-c" ] ; then
  CMD=$2
  shift 2
fi

OUTDIR="/afs/cern.ch/user/m/mbaak/scratch0/Work/Susy/output/"
if [ "$1" = "-o" ] ; then
  OUTDIR=$2
  shift 2
fi

CONFFILE=$1
shift 1

date
hostname

## setup path
echo "Now sourcing setup:"
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
	cp $SUSYDIR/config/HistFactorySchema.dtd config/
fi

echo "directory contains:"
ls -lh

RUNCMD="HistFitter.py ${CMD} -F excl -r ${SR} -g ${ARGS} ${CONFFILE}"

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

cp -rf results/SoftLeptonMoriond2013_${SRSTR}_${ARGS}* $OUTDIR

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


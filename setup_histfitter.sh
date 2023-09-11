#!/bin/bash

#This script takes up three flags; -p to specify path to work dir and -t to get tests.
#and -h for help
#You can have many working directories, but then this script must be activated with 
#the correct path when you change directory.

#Check if the bash or zsh shells are being used
if [ ! -z "${BASH_VERSION}" ]; then
  #Find location of script
  SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
elif [ ! -z "${ZSH_VERSION}" ]; then 
  #Find location of script
  SCRIPT_DIR="${0:A:h}"
else
  echo "Please source this script using a bash or zsh shell.";
  return;
fi

HISTFITTER_WORKDIR=""
test=false
examples=false

while getopts "hp:te" flag; do
  case "$flag" in
    h) echo "Use the flag -p to specify path to work dir, -t to copy pytest directory to your working directory, -e to copy example analysis and macros to your working directory.";;
    p) HISTFITTER_WORKDIR="${OPTARG}" ;;
    t) test=true  ;;
    e) examples=true ;;
  esac
done
#If we do not set this, the script does not work on second run
export OPTIND=1

#Set histfitter environment path
if [ -z $HISTFITTER_WORKDIR ]; then
  echo "Assuming current directory is the working directory"
  HISTFITTER_WORKDIR=$(pwd)
fi
export HISTFITTER_WORKDIR

echo "Setting the HISTFITTER_WORKDIR variable to $HISTFITTER_WORKDIR"

#Set other paths
source "$SCRIPT_DIR/histfitter_env_setup.sh"

#Set up HistFitter environment with folders
if [[ ! -d "$HISTFITTER_WORKDIR/config" || ! -d "$HISTFITTER_WORKDIR/results" || ! -d "$HISTFITTER_WORKDIR/data" ]]; then
    echo "Making directories ./config ./results ./data in $HISTFITTER_WORKDIR"
    mkdir -p "$HISTFITTER_WORKDIR/config"
    mkdir -p "$HISTFITTER_WORKDIR/results"
    mkdir -p "$HISTFITTER_WORKDIR/data"
fi

#Copy necessary files
if [ ! -f $HISTFITTER_WORKDIR/config/HistFactorySchema.dtd ]; then
  echo "Copying HistFactorySchema.dtd to $HISTFITTER_WORKDIR/config.";
  cp "$SCRIPT_DIR/../share/histfitter/config/HistFactorySchema.dtd" "$HISTFITTER_WORKDIR/config/HistFactorySchema.dtd";
fi

if [[ "$examples" == "true" && ! -d $HISTFITTER_WORKDIR/analysis ]]; then
  echo "Copying /analysis example folder to $HISTFITTER_WORKDIR/analysis.";
  cp -r "$SCRIPT_DIR/../share//histfitter/analysis" "$HISTFITTER_WORKDIR/analysis";
fi

if [[ "$examples" == "true" && ! -d $HISTFITTER_WORKDIR/macros ]]; then
  echo "Copying /macros example folders to $HISTFITTER_WORKDIR/macros.";
  cp -r "$SCRIPT_DIR/../share/histfitter/macros" "$HISTFITTER_WORKDIR/macros";
fi

#Copy test files if specified
if [ $test = true ]; then
  echo "Copying /test folder to $HISTFITTER_WORKDIR/test.";
  cp -r "$SCRIPT_DIR/../share/histfitter/test" "$HISTFITTER_WORKDIR";
fi

#Removing module.modulemap
if [ -f $HISTFITTER_WORKDIR/module.modulemap ]; then
  echo "Removing module.modulemap so ROOT is not confused.";
  rm "$HISTFITTER_WORKDIR/module.modulemap"
fi

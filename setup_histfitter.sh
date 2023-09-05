#!/bin/bash

#This script takes up three flags; -p to specify path to work dir and -t to get tests.
#and -h for help
#You can have many working directories, but then this script must be activated with 
#the correct path when you change directory.

#Check if the bash shell is used
if [ -z "${BASH_VERSION}" ]; then 
  echo "Please source this script using a bash shell.";
  return;
fi

path=""
test=false

while getopts "hp:t" flag; do
  case "$flag" in
    h) echo "Use the flag -p to specify path to work dir and -t to copy pytest directory to your working directory.";;
    p) path="${OPTARG}" ;;
    t) test=true  ;;
  esac
done
#If we do not set this, the script does not work on second run
export OPTIND=1

#Find location of script
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

#Set histfitter environment path
if [ -z $path ];
then
  echo "Assuming current directory is the working directory"
  export HISTFITTER_WORKDIR=$(pwd)
else
  export HISTFITTER_WORKDIR=$path
fi

echo "Setting the HISTFITTER_WORKDIR variable to $HISTFITTER_WORKDIR"

#Set other paths
source "$SCRIPT_DIR/histfitter_env_setup.sh"

#Set up HistFitter environment with folders
echo "Making directories /config /results /data in folder $HISTFITTER_WORKDIR if they do not already exist."
mkdir -p "$HISTFITTER_WORKDIR/config"
mkdir -p "$HISTFITTER_WORKDIR/results"
mkdir -p "$HISTFITTER_WORKDIR/data"

#Copy necessary files
if [ ! -f $HISTFITTER_WORKDIR/config/HistFactorySchema.dtd ]; then
  echo "Copying HistFactorySchema.dtd to $HISTFITTER_WORKDIR/config.";
  cp "$SCRIPT_DIR/../share/histfitter/config/HistFactorySchema.dtd" "$HISTFITTER_WORKDIR/config/HistFactorySchema.dtd";
fi

if [ ! -d $HISTFITTER_WORKDIR/analysis ]; then
  echo "Copying /analysis example folder to $HISTFITTER_WORKDIR/analysis.";
  cp -r "$SCRIPT_DIR/../share//histfitter/analysis" "$HISTFITTER_WORKDIR/analysis";
fi

if [ ! -d $HISTFITTER_WORKDIR/macros ]; then
  echo "Copying /macros folders to $HISTFITTER_WORKDIR/macros.";
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
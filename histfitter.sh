#!/bin/bash

#This script takes up three flags; -p to specify path to work dir and -t to get tests.
#and -h for help
#You can have many working directories, but then this script must be activated with 
#the correct path when you change directory.

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
  export HISTFITTER=$(pwd)
else
  export HISTFITTER=$path
fi

echo "Setting the HISTFITTER variable to $HISTFITTER"

#Set other paths
source "$SCRIPT_DIR/histfitter_env_setup.sh"

#Set up HistFitter environment with folders
echo "Making directories /config /results /data in folder $HISTFITTER if they do not already exist."
mkdir -p "$HISTFITTER/config"
mkdir -p "$HISTFITTER/results"
mkdir -p "$HISTFITTER/data"

#Copy necessary files
if [ ! -f $HISTFITTER/config/HistFactorySchema.dtd ]; then
  echo "Copying HistFactorySchema.dtd to $HISTFITTER/config.";
  cp "$SCRIPT_DIR/../share/histfitter/config/HistFactorySchema.dtd" "$HISTFITTER/config/HistFactorySchema.dtd";
fi

if [ ! -d $HISTFITTER/analysis ]; then
  echo "Copying /analysis example folder to $HISTFITTER/analysis.";
  cp -r "$SCRIPT_DIR/../share//histfitter/analysis" "$HISTFITTER/analysis";
fi

if [ ! -d $HISTFITTER/macros ]; then
  echo "Copying /macros folders to $HISTFITTER/macros.";
  cp -r "$SCRIPT_DIR/../share/histfitter/macros" "$HISTFITTER/macros";
fi

#Copy test files if specified
if [ $test = true ]; then
  echo "Copying /test folder to $HISTFITTER/test.";
  cp -r "$SCRIPT_DIR/../share/histfitter/test" "$HISTFITTER";
fi
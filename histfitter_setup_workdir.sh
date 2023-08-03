#!/bin/bash

#This script takes up to two variables; $1 which should be the name of the working directory
#$2 which is w
#You can have many working directories, but then this script must be activated with the correct path.

while getopts "hpt" flag; do
  case "$flag" in
    h) echo "Use the flag -p to specify path to work dir and -t to get tests.";;
    p) path="${OPTARG}" ;;
    t) test='true'  ;;
  esac
done


#Set histfitter environment path
if [ -z $path ];
then
  echo "Assuming current directory is the working directory"
  export HISTFITTER=$(pwd)
else
  export HISTFITTER=$path
fi

echo "Setting the HISTFITTER variable to $HISTFITTER"

#Set up HistFitter environment with folders
echo "Making directories /config /results /data in folder $HISTFITTER."
mkdir -p "$HISTFITTER/config"
mkdir -p "$HISTFITTER/results"
mkdir -p "$HISTFITTER/data"

#Find location of script
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

#Copy necessary files
if [ ! -f $HISTFITTER/config/HistFactorySchema.dtd ]; then
  echo "Copying HistFactorySchema.dtd to $HISTFITTER/config.";
  cp "$SCRIPT_DIR/histfitter/config/HistFactorySchema.dtd" "$HISTFITTER/config/HistFactorySchema.dtd";
fi

if [ ! -d $HISTFITTER/analysis ]; then
  echo "Copying /analysis example folder to $HISTFITTER/analysis.";
  cp -r "$SCRIPT_DIR/histfitter/analysis" "$HISTFITTER/analysis";
fi

if [ ! -d $HISTFITTER/macros ]; then
  echo "Copying /macros folders to $HISTFITTER/macros.";
  cp -r "$SCRIPT_DIR/histfitter/macros" "$HISTFITTER/macros";
fi

#Copy test files if specified
if [$test]; then
  echo "Copying /test folder to $HISTFITTER/test.";
  cp -r "$SCRIPT_DIR/histfitter/test" "$HISTFITTER/test";
fi
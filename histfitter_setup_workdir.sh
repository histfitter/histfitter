#!/bin/bash

#This script takes one variable $1 which should be the name of the working directory
#You can have many working directories, but then this script must be activated with the correct path.

#Set histfitter environment path
if [ -z $1 ];
then
  echo "Assuming current directory is the working directory"
  export HISTFITTER=$(pwd)
else
  export HISTFITTER=$1
fi

echo "Setting the HISTFITTER variable to $HISTFITTER"

#Set up HistFitter environment with folders and copy necessary files
echo "Making directories /config /results /data in folder $HISTFITTER."
mkdir -p "$HISTFITTER/config"
mkdir -p "$HISTFITTER/results"
mkdir -p "$HISTFITTER/data"

#Find location of script
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

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
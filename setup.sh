#!/bin/bash
# setup ROOT
# check Root environment setup. Allow for external setup script.

# Update here when tagged
VERSION="trunk"

# check Root environment setup 
if [ -z "$(root-config --libs)" ] && [ -z "$(root-config --libs)"] && [ ! $ROOTSYS ]; then
  echo "Warning: No valid Root environment  defined. Please do so first!"
  return
fi

if [[ "$(root-config --version | cut -d "." -f 1)" == "5" ]]; then
  echo "NOTE: ROOT5 installation detected - be aware that this version of HistFitter is developed against ROOT6."
  echo "We cannot guarantee you will not run into issues."
fi

if [ ! $LD_LIBRARY_PATH ]; then
  echo "Warning: so far you haven't setup your ROOT enviroment properly (no LD_LIBRARY_PATH)"
  return
fi


# setup HistFitter package
#if [ "x${BASH_ARGV[0]}" == "x" ]; then
if [ -z ${ZSH_NAME} ] && [ "$(dirname ${BASH_ARGV[0]})" == "." ]; then
  if [ ! -f setup.sh ]; then
    echo ERROR: must "cd where/HistFitter/is" before calling "source setup.sh" for this version of bash!
    HF=; export HF
    return 1
  fi
  HF=$(pwd); export HF
else
  # get param to "."
  scriptname=${BASH_SOURCE:-$0}
  DIR=$( cd "$( dirname "${scriptname}" )" && pwd )
  #thishistfitter=$(dirname ${BASH_ARGV[0]})
  HF=${DIR}; export HF
fi
HISTFITTER=$HF; export HISTFITTER

HISTFITTER_VERSION=$VERSION
export HISTFITTER_VERSION

echo "Setting \$HISTFITTER to ${HISTFITTER}"

# put root & python stuff into PATH, LD_LIBRARY_PATH
export ROOT_INCLUDE_PATH=$HISTFITTER/src:${ROOT_INCLUDE_PATH}
export PATH=$HISTFITTER/bin:$HISTFITTER/scripts:${PATH}
export LD_LIBRARY_PATH=$HISTFITTER/lib:${LD_LIBRARY_PATH}
# PYTHONPATH contains all directories that are used for 'import bla' commands
export PYTHONPATH=$HISTFITTER/python:$HISTFITTER/scripts:$HISTFITTER/macros:$HISTFITTER/lib:$PYTHONPATH
export ROOT_INCLUDE_PATH=$HISTFITTER/include:${ROOT_INCLUDE_PATH}


# Hack for ssh from mac 
export LC_ALL=C 

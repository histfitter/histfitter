#!/bin/bash
# check Root environment setup. Allow for external setup script.
# Update here when tagged
VERSION=1.3.1

# check Root environment setup
if [ -z "$(root-config --libs)" ] && [ -z "$(root-config --libs)"] && [ ! "$ROOTSYS" ]; then
  echo "Warning: No valid Root environment (ROOTSYS) defined. Please do so first!"
  return
fi

function validate_ROOT_release {
  # Ensure valid version of ROOT accessible
  # Can't assume that bc is installed
  # SC2155: Declare and assign separately to avoid masking return values.
  local ROOT_version_minimum
  local ROOT_version_minimum_major
  local ROOT_version_minimum_minor
  local ROOT_version_minimum_rev
  local ROOT_version
  local ROOT_version_major
  local ROOT_version_minor
  local ROOT_version_rev
  local compatible_ROOT_version

  ROOT_version_minimum="6.28/00"
  ROOT_version_minimum_major="$(echo $ROOT_version_minimum | cut -d "." -f 1)"
  ROOT_version_minimum_minor="$(echo $ROOT_version_minimum | cut -d "." -f 2 | cut -d "/" -f 1)"
  ROOT_version_minimum_rev="$(echo $ROOT_version_minimum | cut -d "/" -f 2)"
  ROOT_version="$(root-config --version)"
  ROOT_version_major="$(echo "$ROOT_version" | cut -d "." -f 1)"
  ROOT_version_minor="$(echo "$ROOT_version" | cut -d "." -f 2 | cut -d "/" -f 1)"
  ROOT_version_rev="$(echo "$ROOT_version" | cut -d "/" -f 2)"
  compatible_ROOT_version=true

  if [[ "$ROOT_version_major" -lt "$ROOT_version_minimum_major" ]]; then
    compatible_ROOT_version=false
  elif [ "$ROOT_version_major" -eq "$ROOT_version_minimum_major" ] && [ "$ROOT_version_minor" -lt "$ROOT_version_minimum_minor" ]; then
    compatible_ROOT_version=false
  elif [ "$ROOT_version_major" -eq "$ROOT_version_minimum_major" ] && [ "$ROOT_version_minor" -eq "$ROOT_version_minimum_minor" ] && [ "$ROOT_version_rev" -lt "$ROOT_version_minimum_rev" ]; then
    compatible_ROOT_version=false
  fi
  if [[ "$compatible_ROOT_version" = false ]]; then
      echo "ERROR: Version of ROOT detected: v$ROOT_version"
      echo "       ROOT v$ROOT_version_minimum+ is required to use HistFitter."
      return 1
  fi
}

# Ensure valid version of ROOT accessible
validate_ROOT_release

#Check if LD_LIBRARY_PATH is empty
if [ ! "$LD_LIBRARY_PATH" ]; then
  echo "Warning: so far you haven't setup your ROOT enviroment properly (no LD_LIBRARY_PATH)"
  return
fi

#Export version number
export HISTFITTER_VERSION=$VERSION

#Find location of script
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
echo "Adding HistFitter paths: ROOT_INCLUDE_PATH, PATH, LD_LIBRARY_PATH, PYTHONPATH"

#Update paths
export ROOT_INCLUDE_PATH="$ROOT_INCLUDE_PATH:$SCRIPT_DIR/../include/histfitter"
export PATH="$PATH:$SCRIPT_DIR/histfitter"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$SCRIPT_DIR/../lib"

# PYTHONPATH contains all directories that are used for 'import bla' commands
# Must prepend so as to catch python/cmdLineUtils.py before ROOT installation's
export PYTHONPATH="$SCRIPT_DIR/../python/histfitter:$PYTHONPATH"
export PYTHONPATH="$SCRIPT_DIR/histfitter:$PYTHONPATH"

# Hack for ssh from mac
export LC_ALL=C

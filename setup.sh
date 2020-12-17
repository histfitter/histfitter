#!/bin/bash
# setup ROOT
# check Root environment setup. Allow for external setup script.

# Update here when tagged
VERSION="v0.66.0"

# check Root environment setup
if [ -z "$(root-config --libs)" ] && [ -z "$(root-config --libs)"] && [ ! "${ROOTSYS}" ]; then
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
  local ROOT_version
  local ROOT_version_major
  local ROOT_version_minor
  local compatible_ROOT_version

  ROOT_version_minimum="6.20"
  ROOT_version_minimum_major="$(echo ${ROOT_version_minimum} | cut -d "." -f 1)"
  ROOT_version_minimum_minor="$(echo ${ROOT_version_minimum} | cut -d "." -f 2)"
  ROOT_version="$(root-config --version)"
  ROOT_version_major="$(echo "${ROOT_version}" | cut -d "." -f 1)"
  ROOT_version_minor="$(echo "${ROOT_version}" | cut -d "." -f 2 | cut -d "/" -f 1)"
  compatible_ROOT_version=true

  if [[ "${ROOT_version_major}" -lt "${ROOT_version_minimum_major}" ]]; then
    compatible_ROOT_version=false
  elif [[ "${ROOT_version_minor}" -lt "${ROOT_version_minimum_minor}" ]]; then
    compatible_ROOT_version=false
  fi
  if [[ "${compatible_ROOT_version}" = false ]]; then
      echo "ERROR: Version of ROOT detected: v${ROOT_version}"
      echo "       ROOT v${ROOT_version_minimum}+ is required to use HistFitter."
      return 1
  fi
}

validate_ROOT_release


if [ ! "${LD_LIBRARY_PATH}" ]; then
  echo "Warning: so far you haven't setup your ROOT enviroment properly (no LD_LIBRARY_PATH)"
  return
fi


# setup HistFitter package
if [ -z "${ZSH_NAME}" ] && [ "$(dirname "${BASH_ARGV[0]}")" == "." ]; then
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
export ROOT_INCLUDE_PATH="${ROOT_INCLUDE_PATH}:$HISTFITTER/src"
export PATH="${PATH}:$HISTFITTER/bin:$HISTFITTER/scripts"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:$HISTFITTER/lib"
# PYTHONPATH contains all directories that are used for 'import bla' commands
# Must prepend so as to catch python/cmdLineUtils.py before ROOT installation's
export PYTHONPATH="$HISTFITTER/python:$HISTFITTER/scripts:${PYTHONPATH}"
export ROOT_INCLUDE_PATH=$HISTFITTER/include:${ROOT_INCLUDE_PATH}

# Hack for ssh from mac
export LC_ALL=C

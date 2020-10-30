# Source this script to set up HistFitter
#
# This script is for the fish shell.
#
# Author: Federico Meloni, 2020-10-30

# Update here when tagged
set VERSION "master"

# check Root environment setup
if not set -q ROOTSYS
  echo "Warning: No valid Root environment (ROOTSYS) defined. Please do so first!"
end

if not set -q LD_LIBRARY_PATH
  echo "Warning: so far you haven't setup your ROOT enviroment properly (no LD_LIBRARY_PATH)"
end

# setup HistFitter package
#if [ "x${BASH_ARGV[0]}" == "x" ]; then
#if [ -z ${ZSH_NAME} ] && [ "$(dirname ${BASH_ARGV[0]})" == "." ]; then
#  if [ ! -f setup.sh ]; then
#    echo ERROR: must "cd where/HistFitter/is" before calling "source setup.sh" for this version of bash!
#    HF=; export HF
#    return 1
#  fi
#  HF=$(pwd); export HF
#else
#  # get param to "."
#  scriptname=${BASH_SOURCE:-$0}
#  DIR=$( cd "$( dirname "${scriptname}" )" && pwd )
#  #thishistfitter=$(dirname ${BASH_ARGV[0]})
#  HF=${DIR}; export HF
#fi

set -x HISTFITTER (pwd)
set -x SUSYFITTER (pwd) # for backwards compatibility
set -x HISTFITTER_VERSION $VERSION

echo "Setting \$HISTFITTER to $HISTFITTER"

# put root & python stuff into PATH, LD_LIBRARY_PATH
set -x ROOT_INCLUDE_PATH $HISTFITTER/src $ROOT_INCLUDE_PATH
set -x PATH $HISTFITTER/bin $HISTFITTER/scripts $PATH
set -x LD_LIBRARY_PATH $HISTFITTER/lib $LD_LIBRARY_PATH
set -x DYLD_LIBRARY_PATH $HISTFITTER/lib $DYLD_LIBRARY_PATH
# PYTHONPATH contains all directories that are used for 'import bla' commands
set -x PYTHONPATH $HISTFITTER/python $HISTFITTER/scripts $HISTFITTER/macros $HISTFITTER/lib $PYTHONPATH
set -x ROOT_INCLUDE_PATH $HISTFITTER/include $ROOT_INCLUDE_PATH

#!/bin/bash

RECOMMENDED_LCG="LCG_104"
RECOMMENDED_LCG_PLATFORM_CC7="x86_64-centos7-gcc12-opt"
RECOMMENDED_LCG_PLATFORM_EL9="x86_64-el9-gcc12-opt"

RECOMMENDED_SA="StatAnalysis,0.2.3"

help_fn ()
{
    echo "usage: setup_lcg.sh [-h] [-s]"
    echo ""
    echo "HistFitter base environment configuration script, when the host system has access to /cvmfs/atlas.cern.ch."
    echo "Used to setup a standalone LCG release (default), or StatAnalysis"
    echo "The current recommended LCG release is: '${RECOMMENDED_LCG}'"
    echo "The current recommended StatAnalysis release is: '${RECOMMENDED_SA}'"
    echo ""
    echo "options:"
    echo "  -h                    show this help message and exit"
    echo "  -s                    setup StatAnalysis release instead of a standalone LCG release"
}

do_SA=false

main()
{
    local OPTIND OPTARG flag
    while getopts ":hs" flag; do
        case "$flag" in
            h) help_fn; return 0 ;;
            s) do_SA=true ;;
            *) help_fn; return 1 ;;
        esac
    done
    # Check that no random options were delivered
    shift $((OPTIND-1))
    if [[ $# -ne 0 ]]; then
        help_fn
        return 1
    fi

    # Check that CVMFS is mounted
    if [ ! -d /cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase ]; then
        echo "The ATLAS CVMFS repository /cvmfs/atlas.cern.ch is not available; cannot complete the setup"
        return 1
    fi

    # Setup the common ATLAS environment if "lsetup is not there already"
    if ! command -v lsetup &> /dev/null; then
        export ALRB_localConfigDir="/etc/hepix/sh/GROUP/zp/alrb"
        export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
        source $ATLAS_LOCAL_ROOT_BASE/user/atlasLocalSetup.sh
    fi

    . /etc/os-release
    if [[ $ID == "centos" && $VERSION_ID == 7* ]]; then
        if [ "$do_SA" = true ]; then
            asetup $RECOMMENDED_SA
        else
            lsetup "views ${RECOMMENDED_LCG} ${RECOMMENDED_LCG_PLATFORM_CC7}"
        fi
    elif [[ ($ID == "rhel" || $ID == "almalinux") && $VERSION_ID == 9* ]]; then
        if [ "$do_SA" = true ]; then
            asetup $RECOMMENDED_SA
        else
            lsetup "views ${RECOMMENDED_LCG} ${RECOMMENDED_LCG_PLATFORM_EL9}"
        fi
    fi
}

main "$@"

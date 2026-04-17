cmake_minimum_required(VERSION 3.21)
# Declare the package name:
project(HistFitter VERSION 1.3.1)
set(VERSION "1.3.1")

#Set CXX requirement
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
#SET(CMAKE_CXX_FLAGS_DEBUG "-g")

#Set CMAKE paths and create folders
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
  set(CMAKE_INSTALL_PREFIX "${PROJECT_SOURCE_DIR}/install" CACHE PATH "..." FORCE)
endif()

#Define equired root components
set(root_components Core;Net;Hist;Graf;Graf3d;Gpad;Tree;Rint;
        Postscript;Matrix;Physics;Gui;RooFitCore;RooFit;RooStats;
        HistFactory;XMLParser;Foam;Minuit)

include(GNUInstallDirs)
find_package(Python3 COMPONENTS Interpreter REQUIRED)

set(HISTFITTER_PYTHON_INSTALL_DIR "${CMAKE_INSTALL_PREFIX}/python/histfitter")
configure_file(histfitter_env_setup.sh.in "${CMAKE_CURRENT_BINARY_DIR}/histfitter_env_setup.sh" @ONLY)

#Require root
find_package(ROOT 6 REQUIRED ${root_components})
list(TRANSFORM root_components PREPEND ROOT::)

# Loop over source code and add files to list of source and headers
set(HistFitter_sources "") #The paths to the source files
set(HistFitter_headers "") #The paths to the header files
set(HistFitter_filename_headers "") #These are just the header file names
file(GLOB filePaths src/*)

#Since headers and source files are in the same folder, separate them
foreach (_filePath ${filePaths})
    get_filename_component(_fileDir ${_filePath} DIRECTORY)
	get_filename_component(_fileName ${_filePath} NAME_WE)
    	if(NOT ${_fileName} MATCHES "LinkDef" AND NOT ${_fileName} MATCHES "Makefile")
            list(APPEND HistFitter_sources "${_fileDir}/${_fileName}.cxx")
            list(APPEND HistFitter_headers "${_fileDir}/${_fileName}.h")
            list(APPEND HistFitter_filename_headers "${_fileName}.h")
	endif()
endforeach()

#Remove duplicates
list(REMOVE_DUPLICATES HistFitter_sources)
list(REMOVE_DUPLICATES HistFitter_headers)

#Copy setup scripts
install(PROGRAMS setup_histfitter.sh DESTINATION "${CMAKE_INSTALL_PREFIX}/bin")
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/histfitter_env_setup.sh" DESTINATION "${CMAKE_INSTALL_PREFIX}/bin")

#Copy files needed for working directories
install(FILES ./config/HistFactorySchema.dtd DESTINATION "${CMAKE_INSTALL_DATADIR}/histfitter/config")
install(DIRECTORY ./analysis DESTINATION ${CMAKE_INSTALL_DATADIR}/histfitter
    PATTERN "__pycache__" EXCLUDE
    PATTERN "*.pyc" EXCLUDE
)
install(DIRECTORY ./macros DESTINATION ${CMAKE_INSTALL_DATADIR}/histfitter
    PATTERN "__pycache__" EXCLUDE
    PATTERN "*.pyc" EXCLUDE
)

#Copy test files for testing build
option(HISTFITTER_INSTALL_TESTS "Install test files for use with setup_histfitter.sh -t" OFF)
if(HISTFITTER_INSTALL_TESTS)
  install(DIRECTORY ./test DESTINATION "${CMAKE_INSTALL_DATADIR}/histfitter"
    PATTERN "__pycache__" EXCLUDE
    PATTERN "*.pyc" EXCLUDE
  )
endif()

#Copy python files to install location
install(DIRECTORY ./python/ DESTINATION "${HISTFITTER_PYTHON_INSTALL_DIR}")
install(PROGRAMS scripts/HistFitter.py
        DESTINATION ${CMAKE_INSTALL_BINDIR}
        RENAME histfitter)
install(PROGRAMS
  scripts/GenerateJSONOutput.py
  scripts/GenerateTreeDescriptionFromJSON.py
  scripts/HypoTest.py
  scripts/PrintFitResult.py
  scripts/PrintFitResultTex.py
  scripts/SysTable.py
  scripts/SysTableTex.py
  scripts/SystRankingPlot.py
  scripts/SystRankingPlotMP.py
  scripts/UpperLimitTable.py
  scripts/UpperLimitTableTex.py
  scripts/YieldsTable.py
  scripts/YieldsTableTex.py
  scripts/contourPlotter.py
  scripts/getFinalFullJER.py
  scripts/harvestHepdataToContours.py
  scripts/harvestToContours.py
  scripts/mergeSysTableBreakdown.py
  scripts/multiplexContours.py
  scripts/multiplexJSON.py
  scripts/plotUpDown.py
  scripts/pull_maker.py
  DESTINATION ${CMAKE_INSTALL_BINDIR}
)

#Copy C++ headers before generating root dictionary
install(FILES ${HistFitter_headers} DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/histfitter")

#Add libraries
add_library(HistFitter SHARED ${HistFitter_sources})

#Change .dylib extension to .so on macOS; not pretty, but simpler than changing the
#library file extension in all inports/loads dynamically
if(${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
    set(CMAKE_SHARED_LIBRARY_SUFFIX .so)
endif()

#To make ROOT_GENERATE_DICTIONARY find the header files we are including
target_include_directories(HistFitter PRIVATE ${PROJECT_SOURCE_DIR}/src)

# generate the dictionary source code
ROOT_GENERATE_DICTIONARY(HistFitter_dict ${HistFitter_filename_headers} MODULE HistFitter LINKDEF src/LinkDef.h)

install(TARGETS HistFitter LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})


#Require threads
set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)
target_link_libraries(HistFitter PRIVATE ${root_components} Threads::Threads  m dl)

#IPO
include(CheckIPOSupported)
check_ipo_supported(RESULT supported OUTPUT error)

if(CMAKE_BUILD_TYPE STREQUAL Release)
    if(supported)
        message(STATUS "LTO/IPO enabled")
        set_property(TARGET HistFitter PROPERTY INTERPROCEDURAL_OPTIMIZATION TRUE)
    else()
        message(STATUS "LTO/IPO not supported: <${error}>")
    endif()
endif()

#OpenMP
find_package(OpenMP)
if(OpenMP::OpenMP_CXX)
    target_link_libraries(HistFitter PRIVATE OpenMP::OpenMP_CXX)
endif()

#MPI
find_package(MPI)
if(MPI::MPI_CXX)
    target_link_libraries(HistFitter PRIVATE MPI::MPI_CXX)
endif()
set_property(TARGET HistFitter PROPERTY POSITION_INDEPENDENT_CODE ON)

if(MSVC)
    target_compile_options(HistFitter PRIVATE /W4 /WX)
else()
    target_compile_options(HistFitter PRIVATE -Wall -Wextra -Wpedantic)
endif()

install(CODE "execute_process(COMMAND rm -f
    \"\${CMAKE_INSTALL_PREFIX}/lib/gdk-pixbuf-2.0/2.10.0/loaders.cache\"
    \"\${CMAKE_INSTALL_PREFIX}/lib/graphviz/config8\"
    \"\${CMAKE_INSTALL_PREFIX}/lib/gtk-3.0/3.0.0/immodules.cache\"
    \"\${CMAKE_INSTALL_PREFIX}/share/glib-2.0/schemas/gschemas.compiled\"
    \"\${CMAKE_INSTALL_PREFIX}/share/icons/hicolor/icon-theme.cache\")")

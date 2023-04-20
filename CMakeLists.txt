cmake_minimum_required(VERSION 3.21)
# Declare the package name:
project(HistFitter VERSION 1.3.1)
set(VERSION "1.3.1")

#Set CXX requirement
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

#Set CMAKE paths and create folders
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
  file(MAKE_DIRECTORY "${PROJECT_SOURCE_DIR}/lib")
  set(CMAKE_INSTALL_PREFIX ${PROJECT_SOURCE_DIR} CACHE PATH "..." FORCE)
endif()
set(CMAKE_INSTALL_LIBDIR "${CMAKE_INSTALL_PREFIX}/lib")
set(CMAKE_INSTALL_PYTHON "${CMAKE_INSTALL_PREFIX}/python")
file(MAKE_DIRECTORY "${CMAKE_INSTALL_PREFIX}/python")

#Define equired root components
set(root_components Core;Net;Hist;Graf;Graf3d;Gpad;Tree;Rint;
        Postscript;Matrix;Physics;Gui;RooFitCore;RooFit;RooStats;
        HistFactory;XMLParser;Foam;Html;Minuit)

#Require root
find_package(ROOT 6 REQUIRED ${root_components})
list(TRANSFORM root_components PREPEND ROOT::)

# Loop over source code and add files to list of source and headers
set(SusyFitter_headers "")
set(SusyFitter_sources "")
file(GLOB filePaths src/*/*)

foreach (_filePath ${filePaths})
    get_filename_component(_fileDir ${_filePath} DIRECTORY)
	get_filename_component(_fileName ${_filePath} NAME_WE)
    	if(NOT ${_fileName} MATCHES "LinkDef" AND NOT ${_fileName} MATCHES "Makefile")
            list(APPEND SusyFitter_sources "${_fileDir}/${_fileName}.cxx")
            list(APPEND SusyFitter_headers "${_fileDir}/${_fileName}.h")
	endif()
endforeach()

#Remove duplicates
list(REMOVE_DUPLICATES SusyFitter_sources)
list(REMOVE_DUPLICATES SusyFitter_headers)

#Add libraries
add_library(SusyFitter SHARED ${SusyFitter_sources})

#required to make ROOT_GENERATE_DICTIONARY work
target_include_directories(SusyFitter PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# generate the dictionary source code
ROOT_GENERATE_DICTIONARY(SusyFitter_dict ${SusyFitter_headers} MODULE SusyFitter LINKDEF src/root/LinkDef.h)

#Require threads
set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)
target_link_libraries(SusyFitter PRIVATE ${root_components} Threads::Threads  m dl)

#IPO
include(CheckIPOSupported)
check_ipo_supported(RESULT supported OUTPUT error)

if(CMAKE_BUILD_TYPE STREQUAL Release)
    if(supported)
        message(STATUS "LTO/IPO enabled")
        set_property(TARGET SusyFitter PROPERTY INTERPROCEDURAL_OPTIMIZATION TRUE)
    else()
        message(STATUS "LTO/IPO not supported: <${error}>")
    endif()
endif()

#OpenMP
find_package(OpenMP)
if(OpenMP::OpenMP_CXX)
    target_link_libraries(SusyFitter PRIVATE OpenMP::OpenMP_CXX)
endif()

#MPI
find_package(MPI)
if(MPI::MPI_CXX)
    target_link_libraries(SusyFitter PRIVATE MPI::MPI_CXX)
endif()
set_property(TARGET SusyFitter PROPERTY POSITION_INDEPENDENT_CODE ON)

if(MSVC)
    target_compile_options(SusyFitter PRIVATE /W4 /WX)
else()
    target_compile_options(SusyFitter PRIVATE -Wall -Wextra -Wpedantic)
endif()

#Make setup script
configure_file(setup.sh.in "${CMAKE_INSTALL_PREFIX}/setup.sh")

#Copy python files to install location
file(COPY ./python/hf DESTINATION ${CMAKE_INSTALL_PYTHON})

#Install C++ libraries
install(TARGETS SusyFitter LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})
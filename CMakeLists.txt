cmake_minimum_required(VERSION 3.21)
# Declare the package name:
project(HistFitter VERSION 1.0.2)

#Set CXX requirement
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)


set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
  set(CMAKE_INSTALL_PREFIX ${PROJECT_SOURCE_DIR} CACHE PATH "..." FORCE)
endif()
set(CMAKE_INSTALL_LIBDIR ${CMAKE_INSTALL_PREFIX}/lib)

file(MAKE_DIRECTORY ${PROJECT_SOURCE_DIR}/lib)
file(MAKE_DIRECTORY ${PROJECT_SOURCE_DIR}/bin)


#Define equired root components
set(root_components Core;Net;Hist;Graf;Graf3d;Gpad;Tree;Rint;
        Postscript;Matrix;Physics;Gui;RooFitCore;RooFit;RooStats;
        HistFactory;XMLParser;Foam;Html;Minuit)

#Require root
find_package(ROOT 6 REQUIRED ${root_components})
list(TRANSFORM root_components PREPEND ROOT::)

# Loop over source code
file(GLOB srcPaths src/*)

foreach (_srcPath ${srcPaths})
	get_filename_component(_srcName ${_srcPath} NAME)
    	if(NOT ${_srcName} MATCHES "LinkDef.h" AND NOT ${_srcName} MATCHES "Makefile*")
    	       list(APPEND local_lib_sources "src/${_srcName}")
	endif()
endforeach()

#Add libraries

add_library(SusyFitter SHARED ${local_lib_sources})

#Require threads
set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)


#required to make ROOT_GENERATE_DICTIONARY work
target_include_directories(SusyFitter PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

ROOT_GENERATE_DICTIONARY(SusyFitter_dict ${headers} MODULE SusyFitter LINKDEF src/LinkDef.h)

find_package(OpenMP)
find_package(MPI)

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
target_link_libraries(SusyFitter PRIVATE ${root_components} Threads::Threads  m dl)
if(OpenMP::OpenMP_CXX)
    target_link_libraries(SusyFitter PRIVATE OpenMP::OpenMP_CXX)
endif()
if(MPI::MPI_CXX)
    target_link_libraries(SusyFitter PRIVATE MPI::MPI_CXX)
endif()
set_property(TARGET SusyFitter PROPERTY POSITION_INDEPENDENT_CODE ON)

if(MSVC)
    target_compile_options(SusyFitter PRIVATE /W4 /WX)
else()
    target_compile_options(SusyFitter PRIVATE -Wall -Wextra -Wpedantic)
endif()
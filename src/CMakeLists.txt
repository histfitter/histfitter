cmake_minimum_required(VERSION 3.21)

project(HistFitter VERSION 1.0.2)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(root_components Core;Net;Hist;Graf;Graf3d;Gpad;Tree;Rint;
        Postscript;Matrix;Physics;Gui;RooFitCore;RooFit;RooStats;
        HistFactory;XMLParser;Foam;Html;Minuit)

find_package(ROOT 6 REQUIRED ${root_components})
find_package(nlohmann_json REQUIRED)
list(TRANSFORM root_components PREPEND ROOT::)

set(local_libs ChannelStyle;CombinationUtils;CombineWorkSpaces;ConfigMgr;
        DrawUtils;FitConfig;HistogramPlotter;HypoTestTool;LimitResult;
        RooExpandedFitResult;RooHist;RooPlot;Significance;StatTools;
        TEasyFormula;TMsgLogger;toy_utils;Utils;ValidationUtils;XtraValues)
list(TRANSFORM local_libs APPEND .h OUTPUT_VARIABLE headers)
list(TRANSFORM local_libs APPEND .cxx OUTPUT_VARIABLE local_lib_sources)

add_library(SusyFitter SHARED ${local_lib_sources})
set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)
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

#required to make ROOT_GENERATE_DICTIONARY work
target_include_directories(SusyFitter PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
ROOT_GENERATE_DICTIONARY(SusyFitter_dict ${headers} MODULE SusyFitter LINKDEF LinkDef.h)

// vim: ts=4:sw=4
/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Class  : TMsgLogger                                                            *
 *                                                                                *
 * Description:                                                                   *
 *      Implementation (see header for description)                               *
 *                                                                                *
 *      Authors: the HistFitter team                                              *
 *                                                                                *
 *      Adapted from TMVA:MsgLogger, modified by us. Original authors:            *
 *                                                                                *
 *      Attila Krasznahorkay  <Attila.Krasznahorkay@cern.ch> - CERN, Switzerland  *
 *      Andreas Hoecker       <Andreas.Hocker@cern.ch> - CERN, Switzerland        *
 *      Joerg Stelzer         <stelzer@cern.ch>        - DESY, Germany            *
 *      Eckhard v. Toerne     <evt@uni-bonn.de>        - U of Bonn, Germany       *
 *                                                                                *
 * Copyright (c) 2005-2014:                                                       *
 *      CERN, Switzerland                                                         *
 *      U. of Victoria, Canada                                                    *
 *      MPI-K Heidelberg, Germany                                                 *
 *      U. of Bonn, Germany                                                       *
 *                                                                                *
 *   http://root.cern.ch/root/htmldoc/src/TMVA__MsgLogger.h.html                  *
 *                                                                                *
 * (http://tmva.sourceforge.net/LICENSE)                                          *
 **********************************************************************************/

// STL include(s):
#include <iomanip>
#include <iostream>
#include <stdlib.h>
#include <ctime>

// ROOT include(s):
#include "TObject.h"
#include "TString.h"

// HistFitter include(s)
#include "TMsgLogger.h"

ClassImp(hf::TMsgLogger);

using namespace std;

// uncomment this line to inhibit colored output
#define USE_COLORED_CONSOLE

// this is the hard-coded maximum length of the source names
static const string::size_type MAXIMUM_SOURCE_NAME_LENGTH = 20;

#ifndef __APPLE__
// this is the hardcoded prefix
static const char* PREFIX = ""; //"--- ";
// this is the hardcoded suffix
static const char* SUFFIX = ": ";
#else
#define PREFIX "" //"--- "
#define SUFFIX ": "
#endif

hf::TMsgLevel hf::TMsgLogger::m_minLevel = kINFO;
bool hf::TMsgLogger::m_levelLock = false;

//_____________________________________________________________________________
hf::TMsgLogger::TMsgLogger( const TObject* source, TMsgLevel /*minLevel*/ )
   : m_objSource( source ), 
     m_strSource( "" ), 
     m_prefix( PREFIX ), 
     m_suffix( SUFFIX ), 
     m_activeLevel( kINFO ), 
     m_maxSourceSize( MAXIMUM_SOURCE_NAME_LENGTH ) {
    // constructor
    InitMaps();
}

//_____________________________________________________________________________
hf::TMsgLogger::TMsgLogger( const string& source, TMsgLevel /*minLevel*/ )
   : m_objSource( 0 ),
     m_strSource( source ), 
     m_prefix( PREFIX ), 
     m_suffix( SUFFIX ), 
     m_activeLevel( kINFO ), 
     m_maxSourceSize( MAXIMUM_SOURCE_NAME_LENGTH ) {
    // constructor
    InitMaps();
}

//_____________________________________________________________________________
hf::TMsgLogger::TMsgLogger( TMsgLevel /*minLevel*/ )
   : m_objSource( 0 ), 
     m_strSource( "Unknown" ), 
     m_prefix( PREFIX ), 
     m_suffix( SUFFIX ), 
     m_activeLevel( kINFO ), 
     m_maxSourceSize( MAXIMUM_SOURCE_NAME_LENGTH ) {
    // constructor
    InitMaps();
}

//_____________________________________________________________________________
hf::TMsgLogger::TMsgLogger( const TMsgLogger& parent )
   //: basic_ios< hf::TMsgLogger::char_type, hf::TMsgLogger::traits_type >( new hf::TMsgLogger::__stringbuf_type() ),
   : basic_ios< hf::TMsgLogger::char_type, hf::TMsgLogger::traits_type >( new std::basic_stringbuf< hf::TMsgLogger::char_type >() ),
     ostringstream(),
     TObject(),
     m_prefix( PREFIX ), 
     m_suffix( SUFFIX ),
     m_maxSourceSize( MAXIMUM_SOURCE_NAME_LENGTH ) {
    InitMaps();
    *this = parent;
}

//_____________________________________________________________________________
hf::TMsgLogger::~TMsgLogger() {
}

//_____________________________________________________________________________
hf::TMsgLogger& hf::TMsgLogger::operator= ( const TMsgLogger& parent )  {
    m_objSource   = parent.m_objSource;
    m_strSource   = parent.m_strSource;
    m_activeLevel = parent.m_activeLevel;

    return *this;
}

//_____________________________________________________________________________
string hf::TMsgLogger::GetFormattedSource() const {
    // make sure the source name is no longer than m_maxSourceSize:
    string source_name;
    if (m_objSource) source_name = m_objSource->GetName();
    else             source_name = m_strSource;

    if (source_name.size() > m_maxSourceSize) {
        source_name = source_name.substr( 0, m_maxSourceSize - 3 );
        source_name += "...";
    }
   
    return source_name;
}

//_____________________________________________________________________________
string hf::TMsgLogger::GetPrintedSource() const { 
    // the full logger prefix
    string source_name = GetFormattedSource();

    return m_prefix + source_name + m_suffix; 
}

//_____________________________________________________________________________
void hf::TMsgLogger::Send() {
    // activates the logger writer

    // make sure the source name is no longer than m_maxSourceSize:
    string source_name = GetFormattedSource();

    string message = this->str();
    string::size_type previous_pos = 0, current_pos = 0;

    // slice the message into lines:
    for (;;) {
        current_pos = message.find( '\n', previous_pos );
        string line = message.substr( previous_pos, current_pos - previous_pos );

        ostringstream message_to_send;
        // must call the modifiers like this, otherwise g++ get's confused with the operators...
        message_to_send.setf( ios::adjustfield, ios::left );
        message_to_send.width( source_name.size() );
        message_to_send << source_name << m_suffix << line;
        this->WriteMsg( m_activeLevel, message_to_send.str() );

        if (current_pos == message.npos) 
            break;
        previous_pos = current_pos + 1;
    }

    // reset the stream buffer:
    this->str( "" );
    return;
}

//_____________________________________________________________________________
void hf::TMsgLogger::WriteMsg( TMsgLevel mlevel, const std::string& line ) const  {
    if (mlevel < GetMinLevel()) 
        return;
    
    map<TMsgLevel, std::string>::const_iterator slevel;
    if ((slevel = m_levelMap.find( mlevel )) == m_levelMap.end()) 
        return;

    //we do print names for kINFO - gbesjes 17/10/12
#ifdef USE_COLORED_CONSOLE
    std::cout << m_colorMap.find( mlevel )->second << m_prefix << "<" << slevel->second << "> " << line;  // << "\033[0m" << std::endl;
    if (mlevel == kINFO) { 
      std::cout << std::endl;
    } else {
      std::cout << "\033[0m" << std::endl;
    }
#else
    std::cout << m_prefix << "<" << slevel->second << "> " << line << std::endl;
#endif // USE_COLORED_CONSOLE

    // take decision to stop if fatal error
    if (mlevel == kFATAL) { 
        std::cout << "***> abort program execution" << std::endl; 
        exit(1); 
    }
}

//_____________________________________________________________________________
hf::TMsgLogger& hf::TMsgLogger::endmsg( TMsgLogger& logger ) {
    // end line
    logger.Send();
    return logger;
}

//_____________________________________________________________________________
hf::TMsgLevel hf::TMsgLogger::MapLevel( const TString& instr ) const {
    TString ins = instr; // need to copy
    ins.ToUpper();

   // find the corresponding key
    std::map<TMsgLevel, std::string>::const_iterator it = m_levelMap.begin();
    for (; it != m_levelMap.end(); it++) {
        if (ins == it->second) 
            return it->first;
    }

    // not found --> fatal error
    TString line( Form( "fatal error in <hf::TMsgLogger::MapLevel> unknown output level: %s ==> abort", ins.Data() ) );
    std::cout << m_colorMap.find( kFATAL )->second << m_prefix << line << "\033[0m" << std::endl;
    abort();

    return kFATAL;
}

//_____________________________________________________________________________
void hf::TMsgLogger::InitMaps() {
    m_levelMap[kVERBOSE] = "VERBOSE";
    m_levelMap[kDEBUG]   = "DEBUG";
    m_levelMap[kINFO]    = "INFO";
    m_levelMap[kWARNING] = "WARNING";
    m_levelMap[kERROR]   = "ERROR";
    m_levelMap[kFATAL]   = "FATAL";
    m_levelMap[kALWAYS]  = "ALWAYS";

    //m_colorMap[kVERBOSE] = "\033[1;34m";
    m_colorMap[kVERBOSE] = "\033[96m";
    m_colorMap[kDEBUG]   = "\033[94m";
    m_colorMap[kINFO]    = "";
    m_colorMap[kWARNING] = "\033[0;31m";
    m_colorMap[kERROR]   = "\033[1;31m";
    m_colorMap[kFATAL]   = "\033[37;41;1m";
    m_colorMap[kALWAYS]  = "\033[30m";   
}

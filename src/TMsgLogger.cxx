// vim: ts=4:sw=4
/**********************************************************************************
 * Class  : TMsgLogger                                                            *
 *                                                                                *
 * Authors (alphabetical):                                                        *
 *      Attila Krasznahorkay <Attila.Krasznahorkay@cern.ch> - CERN, Switzerland   *
 **********************************************************************************/

// STL include(s):
#include <iomanip>
#include <iostream>
#include <stdlib.h>

// ROOT include(s):
#include "TObject.h"
#include "TString.h"

// Local include(s):
#include "TMsgLogger.h"

ClassImp(TMsgLogger);

using namespace std;

// uncomment this line to inhibit colored output
#define USE_COLORED_CONSOLE

// this is the hard-coded maximum length of the source names
static const string::size_type MAXIMUM_SOURCE_NAME_LENGTH = 20;
#ifndef __APPLE__
// this is the hardcoded prefix
static const char* PREFIX = "--- ";
// this is the hardcoded suffix
static const char* SUFFIX = ": ";
#else
#define PREFIX "--- "
#define SUFFIX ": "
#endif

TMsgLogger::TMsgLevel TMsgLogger::m_minLevel = TMsgLogger::kINFO;

TMsgLogger::TMsgLogger( const TObject* source, TMsgLevel minLevel )
   : m_objSource( source ), 
     m_strSource( "" ), 
     m_prefix( PREFIX ), 
     m_suffix( SUFFIX ), 
     m_activeLevel( kINFO ), 
     m_maxSourceSize( MAXIMUM_SOURCE_NAME_LENGTH ) {
    // constructor
    InitMaps();
}

TMsgLogger::TMsgLogger( const string& source, TMsgLevel minLevel )
   : m_objSource( 0 ),
     m_strSource( source ), 
     m_prefix( PREFIX ), 
     m_suffix( SUFFIX ), 
     m_activeLevel( kINFO ), 
     m_maxSourceSize( MAXIMUM_SOURCE_NAME_LENGTH ) {
    // constructor
    InitMaps();
}

TMsgLogger::TMsgLogger( TMsgLevel minLevel )
   : m_objSource( 0 ), 
     m_strSource( "Unknown" ), 
     m_prefix( PREFIX ), 
     m_suffix( SUFFIX ), 
     m_activeLevel( kINFO ), 
     m_maxSourceSize( MAXIMUM_SOURCE_NAME_LENGTH ) {
    // constructor
    InitMaps();
}

TMsgLogger::TMsgLogger( const TMsgLogger& parent )
   : basic_ios< TMsgLogger::char_type, TMsgLogger::traits_type >( new TMsgLogger::__stringbuf_type() ),
     ostringstream(),
     TObject(),
     m_prefix( PREFIX ), 
     m_suffix( SUFFIX ),
     m_maxSourceSize( MAXIMUM_SOURCE_NAME_LENGTH ) {
    InitMaps();
    *this = parent;
}

TMsgLogger::~TMsgLogger() {
    if(m_singleton)
        delete m_singleton;
}

TMsgLogger& TMsgLogger::operator= ( const TMsgLogger& parent )  {
    m_objSource   = parent.m_objSource;
    m_strSource   = parent.m_strSource;
    m_activeLevel = parent.m_activeLevel;

    return *this;
}

string TMsgLogger::GetFormattedSource() const {
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

string TMsgLogger::GetPrintedSource() const { 
    // the full logger prefix
    string source_name = GetFormattedSource();
    if (source_name.size() < m_maxSourceSize) { 
        for (string::size_type i=source_name.size(); i<m_maxSourceSize; i++) 
            source_name.push_back( ' ' );
    }

    return m_prefix + source_name + m_suffix; 
}

void TMsgLogger::Send() {
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
        message_to_send.width( m_maxSourceSize );
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

void TMsgLogger::WriteMsg( TMsgLevel mlevel, const std::string& line ) const  {
    if (mlevel < GetMinLevel()) 
        return;
    
    map<TMsgLevel, std::string>::const_iterator slevel;
    if ((slevel = m_levelMap.find( mlevel )) == m_levelMap.end()) 
        return;

#ifdef USE_COLORED_CONSOLE
    //// no text for INFO
    //if (mlevel == kINFO) 
        //cout << m_colorMap.find( mlevel )->second << m_prefix << line << "\033[0m" << endl;
    //else
        cout << m_colorMap.find( mlevel )->second << m_prefix 
             << "<" << slevel->second << "> " << line  << "\033[0m" << endl;
#else
    //if (mlevel == kINFO) 
        //cout << m_prefix << line << endl;
    //else
        cout << m_prefix << "<" << slevel->second << "> " << line << endl;
#endif // USE_COLORED_CONSOLE

    // take decision to stop if fatal error
    if (mlevel == kFATAL) { 
        cout << "***> abort program execution" << endl; 
        exit(1); 
    }
}

TMsgLogger& TMsgLogger::endmsg( TMsgLogger& logger ) {
    // end line
    logger.Send();
    return logger;
}

TMsgLogger::TMsgLevel TMsgLogger::MapLevel( const TString& instr ) const {
    TString ins = instr; // need to copy
    ins.ToUpper();

   // find the corresponding key
    std::map<TMsgLevel, std::string>::const_iterator it = m_levelMap.begin();
    for (; it != m_levelMap.end(); it++) {
        if (ins == it->second) 
            return it->first;
    }

    // not found --> fatal error
    TString line( Form( "fatal error in <TMsgLogger::MapLevel> unknown output level: %s ==> abort", ins.Data() ) );
    cout << m_colorMap.find( kFATAL )->second << m_prefix << line << "\033[0m" << endl;
    abort();

    return kFATAL;
}

void TMsgLogger::InitMaps() {
    m_levelMap[kVERBOSE] = "VERBOSE";
    m_levelMap[kDEBUG]   = "DEBUG";
    m_levelMap[kINFO]    = "INFO";
    m_levelMap[kWARNING] = "WARNING";
    m_levelMap[kERROR]   = "ERROR";
    m_levelMap[kFATAL]   = "FATAL";
    m_levelMap[kALWAYS]  = "ALWAYS";

    m_colorMap[kVERBOSE] = "\033[1;34m";
    m_colorMap[kDEBUG]   = "\033[34m";
    m_colorMap[kINFO]    = "";
    m_colorMap[kWARNING] = "\033[1;31m";
    m_colorMap[kERROR]   = "\033[1;31m";
    m_colorMap[kFATAL]   = "\033[37;41;1m";
    m_colorMap[kALWAYS]  = "\033[30m";   
}

TMsgLogger* TMsgLogger::m_singleton = NULL; 

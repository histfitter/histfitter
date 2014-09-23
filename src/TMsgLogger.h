// vim: ts=4:sw=4
/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *  
 * Package: HistFitter                                                            *
 * Class  : TMsgLogger                                                            *
 *                                                                                *
 * Description:                                                                   *
 *      output logger class producing nicely formatted log messages               *
 *                                                                                *
 *      Authors: the HistFitter team                                              *
 *                                                                                *
 *      Adapted from TMVA:MsgLogger. Original authors:                            *
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

#ifndef ROOT_TMsgLogger
#define ROOT_TMsgLogger

//////////////////////////////////////////////////////////////////////////
//                                                                      //
// TMsgLogger                                                           //
//                                                                      //
// ostreamstream derivative to redirect and format output               //
//                                                                      //
//////////////////////////////////////////////////////////////////////////

// STL include(s):
#include <iostream>
#include <string>
#include <sstream>
#include <map>

// ROOT include(s)
#include "TObject.h"
#include "TString.h"
#include "RooGlobalFunc.h"

enum TMsgLevel { 
    kVERBOSE = 1, 
    kDEBUG   = 2,
    kINFO    = 3,
    kWARNING = 4,
    kERROR   = 5,
    kFATAL   = 6,
    kALWAYS  = 7
};

class TMsgLogger : public std::ostringstream, public TObject {
    public:
        TMsgLogger( const TObject* source, TMsgLevel minLevel = kINFO );
        TMsgLogger( const std::string& source, TMsgLevel minLevel = kINFO );
        TMsgLogger( TMsgLevel minLevel = kINFO );
        TMsgLogger( const TMsgLogger& parent );
        virtual ~TMsgLogger();

        // Accessors
        void               SetSource( const char*        source ) { m_strSource = source; }
        void               SetSource( const std::string& source ) { m_strSource = source; }
        void               SetSource( const TString&     source ) { m_strSource = source.Data(); }
        const std::string& GetSource() const { return m_strSource; }

        UInt_t      GetMaxSourceSize() const       { return (UInt_t)m_maxSourceSize; }
        std::string GetPrintedSource() const;
        std::string GetFormattedSource() const;

        TMsgLevel          GetMinLevel() const     { return m_minLevel; }
        const std::string& GetMinLevelStr() const  { return m_levelMap.find( m_minLevel )->second; }

        RooFit::MsgLevel GetRooFitMsgLevel() const {
            if(m_minLevel == kVERBOSE)
                return RooFit::DEBUG;

            if(m_minLevel == kDEBUG)
                return RooFit::DEBUG;

            if(m_minLevel == kINFO)
                return RooFit::INFO;

            if(m_minLevel == kWARNING)
                return RooFit::WARNING;

            if(m_minLevel == kERROR)
                return RooFit::ERROR;

            if(m_minLevel == kFATAL)
                return RooFit::FATAL;

            return RooFit::INFO;
        }

        TMsgLevel   MapLevel( const TString& instr ) const;

        // Needed for copying
        TMsgLogger& operator= ( const TMsgLogger& parent );

        // Stream modifier(s)
        static TMsgLogger& endmsg( TMsgLogger& logger );

        // Accept stream modifiers
        TMsgLogger& operator<< ( TMsgLogger& ( *_f )( TMsgLogger& ) );
        TMsgLogger& operator<< ( std::ostream& ( *_f )( std::ostream& ) );
        TMsgLogger& operator<< ( std::ios& ( *_f )( std::ios& ) );

        // Accept message level specification
        TMsgLogger& operator<< ( TMsgLevel level );

        // For all the "conventional" inputs
        template <class T> TMsgLogger& operator<< ( T arg ) {
            *(std::ostringstream*)this << arg; return *this;
        }

        static void SetMinLevel( TMsgLevel minLevel, bool lock=false ) {
            if(m_levelLock) 
                return;

            m_minLevel = minLevel;
            if(lock)
                m_levelLock = true;
        }

        static bool GetLevelLock() {
            return m_levelLock;
        }

        std::map<TMsgLevel, std::string> GetLevelMap() const { return m_levelMap; }

        // for python
        void writeLogMessage( TMsgLevel level, std::string message) { 
            *(TMsgLogger*) this << level << message << TMsgLogger::endmsg; 
        }

    private:
        //can the level setting be changed?
        static bool m_levelLock;

        // the current minimum level is global for the whole Combination
        // it can only be changed by the central storage singleton object
        static TMsgLevel                 m_minLevel;       // minimum level for logging output

        // private utility routines
        void Send();
        void InitMaps();
        void WriteMsg( TMsgLevel level, const std::string& line ) const;

        const TObject*                   m_objSource;      // the source TObject (used for name)
        std::string                      m_strSource;      // alternative string source
        const std::string                m_prefix;         // the prefix of the source name
        const std::string                m_suffix;         // suffix following source name
        TMsgLevel            m_activeLevel;    // active level
        const std::string::size_type     m_maxSourceSize;  // maximum length of source name

        std::map<TMsgLevel, std::string> m_levelMap;       // matches output levels with strings
        std::map<TMsgLevel, std::string> m_colorMap;       // matches output levels with terminal colors

        ClassDef(TMsgLogger,0)

}; // class TMsgLogger

inline TMsgLogger& TMsgLogger::operator<< ( TMsgLogger& (*_f)( TMsgLogger& ) ) {
    return (_f)(*this);
}

inline TMsgLogger& TMsgLogger::operator<< ( std::ostream& (*_f)( std::ostream& ) ) {
    (_f)(*this);
    return *this;
}

inline TMsgLogger& TMsgLogger::operator<< ( std::ios& ( *_f )( std::ios& ) ) {
    (_f)(*this);
    return *this;
}

inline TMsgLogger& TMsgLogger::operator<< ( TMsgLevel level ) {
    m_activeLevel = level;
    return *this;
}

// Although the proper definition of "Endl" as a function pointer
// would be nicer C++-wise, it introduces some "unused variable"
// warnings so let's use the #define definition after all...
// [ static TMsgLogger& ( *Endl )( TMsgLogger& ) = &TMsgLogger::endmsg; ]
#define GEndl TMsgLogger::endmsg

#endif // Combination_TMsgLogger

// vim: ts=4:sw=4
/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Class  : SRootFinder                                                           *
 *                                                                                *
 * Description:                                                                   *
 *      RootFinder using Brents algorithm, taken from TMVA implementation         *
 *                                                                                *
 *      Adapted from TMVA:RootFinder. Original author(s):                         *
 *                                                                                *
 *      Andreas Hoecker <Andreas.Hocker@cern.ch> - CERN, Switzerland              *
 *      Helge Voss      <Helge.Voss@cern.ch>     - MPI-K Heidelberg, Germany      *
 *      Kai Voss        <Kai.Voss@cern.ch>       - U. of Victoria, Canada         *
 *                                                                                *
 * Copyright (c) 2005:                                                            *
 *      CERN, Switzerland                                                         * 
 *      U. of Victoria, Canada                                                    * 
 *      MPI-K Heidelberg, Germany                                                 *
 *                                                                                *
 *     http://root.cern.ch/root/html/src/TMVA__RootFinder.h.html                  * 
 *                                                                                *
 * (http://tmva.sourceforge.net/LICENSE)                                          *
 **********************************************************************************/

#ifndef StatTools_SRootFinder
#define StatTools_SRootFinder

#include "TMsgLogger.h"
#include "TObject.h"

namespace StatTools {

    class SRootFinder : public TObject {

        public:

            SRootFinder( Double_t (*rootVal)( Double_t ),
                    Double_t rootMin, Double_t rootMax,
                    Int_t    maxIterations = 100, 
                    Double_t absTolerance  = 0.0 );
            virtual ~SRootFinder( void );

            // returns the root of the function
            Double_t Root( Double_t refValue );

        private:
            Double_t fRootMin;  // minimum root value
            Double_t fRootMax;  // maximum root value
            Int_t    fMaxIter;  // maximum number of iterations
            Double_t fAbsTol;   // absolute tolerance deviation

            // function pointer
            Double_t (*fGetRootVal)( Double_t );
            
            TMsgLogger m_logger;

            ClassDef(SRootFinder,0) // Root finding using Brents algorithm
    };

} // namespace StatTools

#endif


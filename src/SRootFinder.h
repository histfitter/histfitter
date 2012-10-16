/**********************************************************************************
 * Package: StatTools                                                             *
 * Class  : SRootFinder                                                           *
 * Creation: 27 Jan 2007                                                          *
 *                                                                                *
 * Author : Andreas Hoecker <Andreas.Hoecker@cern.ch> - CERN, Switzerland         *
 *                                                                                *
 * File and Version Information:                                                  *
 * $Id$    
 **********************************************************************************/

#ifndef StatTools_SRootFinder
#define StatTools_SRootFinder

//////////////////////////////////////////////////////////////////////////
//                                                                      //
// SRootFinder                                                          //
//                                                                      //
// Root finding using Brents algorithm                                  //
// (translated from CERNLIB function RZERO)                             //
//                                                                      //
//////////////////////////////////////////////////////////////////////////

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

      ClassDef(SRootFinder,0) // Root finding using Brents algorithm
   };

} // namespace StatTools

#endif


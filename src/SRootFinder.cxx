/**********************************************************************************
 * Package : StatTools                                                            *
 * Class   : SRootFinder                                                          *
 * Creation: 27 Jan 2007                                                          *
 *                                                                                *
 * Author : Andreas Hoecker <Andreas.Hoecker@cern.ch> - CERN, Switzerland         *
 *                                                                                *
 * File and Version Information:                                                  *
 * $Id$    
 **********************************************************************************/

#include "SRootFinder.h"
#include "Riostream.h"
#include "TMath.h"

using namespace Combination;

ClassImp(StatTools::SRootFinder)

//_______________________________________________________________________
StatTools::SRootFinder::SRootFinder( Double_t (*rootVal)( Double_t ),
                                     Double_t rootMin, 
                                     Double_t rootMax,
                                     Int_t maxIterations, 
                                     Double_t absTolerance )
   : TObject(),
     fRootMin( rootMin ),
     fRootMax( rootMax ),
     fMaxIter( maxIterations ),
     fAbsTol ( absTolerance  ),
     m_logger( kINFO )
{
   // constructor
   fGetRootVal = rootVal;

   m_logger.SetSource( "SRootFinder" );
}

//_______________________________________________________________________
StatTools::SRootFinder::~SRootFinder( void )
{
   // destructor
}

//_______________________________________________________________________
Double_t StatTools::SRootFinder::Root( Double_t refValue  )
{
   // Root finding using Brents algorithm; taken from CERNLIB function RZERO
   Double_t a  = fRootMin, b = fRootMax;
   Double_t fa = (*fGetRootVal)( a ) - refValue;
   Double_t fb = (*fGetRootVal)( b ) - refValue;
   if (fb*fa > 0) {
      m_logger << kWARNING << "<Root> initial interval w/o root: "
               << "(a=" << a << ", b=" << b << "),"
               << " (F(a) = " << (*fGetRootVal)( a ) 
               << ", F(b) = " << (*fGetRootVal)( b ) << "), "
               << "(fa=" << fa << ", fb=" << fb << "), "
               << "refValue = " << refValue << GEndl;
      return 1;
   }

   Bool_t   ac_equal(kFALSE);
   Double_t fc = fb;
   Double_t c  = 0, d = 0, e = 0;
   for (Int_t iter= 0; iter <= fMaxIter; iter++) {
      if ((fb < 0 && fc < 0) || (fb > 0 && fc > 0)) {

         // Rename a,b,c and adjust bounding interval d
         ac_equal = kTRUE;
         c  = a; fc = fa;
         d  = b - a; e  = b - a;
      }
  
      if (TMath::Abs(fc) < TMath::Abs(fb)) {
         ac_equal = kTRUE;
         a  = b;  b  = c;  c  = a;
         fa = fb; fb = fc; fc = fa;
      }

      Double_t tol = 0.5 * 2.2204460492503131e-16 * TMath::Abs(b);
      Double_t m   = 0.5 * (c - b);
      if (fb == 0 || TMath::Abs(m) <= tol || TMath::Abs(fb) < fAbsTol) return b;
  
      // Bounds decreasing too slowly: use bisection
      if (TMath::Abs (e) < tol || TMath::Abs (fa) <= TMath::Abs (fb)) { d = m; e = m; }      
      else {
         // Attempt inverse cubic interpolation
         Double_t p, q, r;
         Double_t s = fb / fa;
      
         if (ac_equal) { p = 2 * m * s; q = 1 - s; }
         else {
            q = fa / fc; r = fb / fc;
            p = s * (2 * m * q * (q - r) - (b - a) * (r - 1));
            q = (q - 1) * (r - 1) * (s - 1);
         }
         // Check whether we are in bounds
         if (p > 0) q = -q;
         else       p = -p;
      
         Double_t min1 = 3 * m * q - TMath::Abs (tol * q);
         Double_t min2 = TMath::Abs (e * q);
         if (2 * p < (min1 < min2 ? min1 : min2)) {
            // Accept the interpolation
            e = d;        d = p / q;
         }
         else { d = m; e = m; } // Interpolation failed: use bisection.
      }
      // Move last best guess to a
      a  = b; fa = fb;
      // Evaluate new trial root
      if (TMath::Abs(d) > tol) b += d;
      else                     b += (m > 0 ? +tol : -tol);

      fb = (*fGetRootVal)( b ) - refValue;

   }

   // Return our best guess if we run out of iterations
   m_logger << kWARNING << "<Root> maximum iterations (" << fMaxIter 
            << ") reached before convergence" << GEndl;

   return b;
}


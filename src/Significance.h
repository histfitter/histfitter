// vim: ts=4:sw=4
/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Namespace: StatTools                                                           *
 *                                                                                *
 * Description:                                                                   *
 *      Namespace for global statistics utility functions                         *
 *      E.g. get correct p-value from significance and inverse                    *
 *                                                                                *
 * Authors:                                                                       *
 *      Andreas Hoecker <Andreas.Hocker@cern.ch> - CERN, Switzerland              *
 *      Till Eifert <Till.Eifert@cern.ch> - CERN, Switzerland                     *
 *      HistFitter group, CERN, Geneva, Switzerland                               *
 *                                                                                *
 * See corresponding .h file for author and license information                   *
 **********************************************************************************/

#ifndef __Significance__
#define __Significance__ 

#include "TString.h"
#include <vector>

class RooWorkspace;
class RooDataSet;

namespace StatTools
{
    Double_t GetProbFromSigma( Double_t );     // get p-value from significance [sigma]
    Double_t GetSigma( Double_t pValue );      // inverse of above: get significance [sigma] from p-value

    Double_t DmLogL_PA( Double_t nObs, Double_t nb, Double_t sig ) ;

    Double_t GetSimpleP1( Double_t nObs, Double_t nEvtExp, Double_t sumErr ) ;

    Double_t FindSignal( Double_t nObs, Double_t nEvtExp, Double_t sumErr, Double_t signald=0, Double_t signalu=50, Double_t pValue=0.05, Double_t tol=0.001 );

    Double_t GetDLL( Double_t nObs, Double_t nb, Double_t sig );
    Double_t GetNSigma( Double_t nObs, Double_t nb, Double_t sig );

    Double_t FindS95( Double_t nObs, Double_t nEvtExp, Double_t sumErr, Double_t signald=0, Double_t signalu=50, Double_t dll95=1.35277172704770687, Double_t tol=0.001 );
    Double_t FindXS95( Double_t nObs, Double_t nBkgExp, Double_t nBkgErr, Double_t signalEff, Double_t lumi, Double_t pValue=0.05 );

    Double_t FindSNSigma( Double_t nEvtExp, Double_t sumErr, Double_t nsigma3=3.0, Double_t signald=0, Double_t signalu=100, Double_t tol=0.001 ) ;
    Double_t FindXSNSigma( Double_t nBkgExp, Double_t nBkgErr, Double_t signalEff, Double_t lumi, Double_t nsigma3=3.0, 
            Double_t signalu=100 ) ;
}

#endif


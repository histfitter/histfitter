// vim: ts=4:sw=4
/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Namespace: StatTools                                                           *
 *                                                                                *
 * Description:                                                                   *
 *      Implementation (see header for description)                               *
 *                                                                                *
 * Authors:                                                                       *
 *      Andreas Hoecker <Andreas.Hocker@cern.ch> - CERN, Switzerland              *
 *      Till Eifert <Till.Eifert@cern.ch> - CERN, Switzerland                     *
 *      HistFitter group, CERN, Geneva, Switzerland                               *
 *                                                                                *
 * See corresponding .h file for author and license information                   *
 **********************************************************************************/

#include "Significance.h"
#include "TMath.h"
#include "RooWorkspace.h"
#include "CombineWorkSpaces.h"
#include "RooRealVar.h"
#include "RooDataSet.h"
#include "RooArgSet.h"
#include "RooAbsReal.h"
#include "toy_utils.h"


//________________________________________________________________________________________________
Double_t StatTools::GetNSigma( Double_t nObs, Double_t nb, Double_t sig ) {
    Double_t dll = StatTools::GetDLL( nObs, nb, sig );
    Double_t nsigma = TMath::Sqrt( 2.*dll );
    return nsigma;
}


//________________________________________________________________________________________________
Double_t StatTools::GetSimpleP1( Double_t nObs, Double_t nEvtExp, Double_t sumErr ) {
    double nsigma = StatTools::GetNSigma( nObs, nEvtExp, sumErr );
    return StatTools::GetProbFromSigma(nsigma) ;
}


//________________________________________________________________________________________________
Double_t StatTools::FindS95( Double_t nObs, Double_t nEvtExp, Double_t sumErr, Double_t signald, Double_t signalu, Double_t dll95, Double_t tol ) {
    Double_t dlld = StatTools::GetDLL( nObs, nEvtExp+signald, sumErr );
    Double_t dllu = StatTools::GetDLL( nObs, nEvtExp+signalu, sumErr );

    if ( dlld<dll95 && dllu>dll95 ) {
        if (signalu-signald<tol) { return (signald+signalu)/2. ; }

        Double_t dllm = StatTools::GetDLL( nObs, nEvtExp+(signald+signalu)/2., sumErr );
        if ( dllm>dll95 ) {
            return StatTools::FindS95( nObs, nEvtExp, sumErr, signald, (signald+signalu)/2., dll95 ) ;
        } else {
            return StatTools::FindS95( nObs, nEvtExp, sumErr, (signald+signalu)/2., signalu, dll95 ) ;
        }
    }

    // no initial solution 
    return -1.;
}


//________________________________________________________________________________________________
Double_t StatTools::FindSNSigma( Double_t nEvtExp, Double_t sumErr, Double_t nsigma3, Double_t signald, Double_t signalu, Double_t tol ) {
    Double_t nsigmad = StatTools::GetNSigma( nEvtExp+signald, nEvtExp, sumErr );
    Double_t nsigmau = StatTools::GetNSigma( nEvtExp+signalu, nEvtExp, sumErr );

    if ( nsigmad<nsigma3 && nsigmau>nsigma3 ) {
        if (nsigmau-nsigmad<tol) { 
            return (signald+signalu)/2. ; 
        }

        Double_t nsigmam = StatTools::GetNSigma( nEvtExp+(signald+signalu)/2, nEvtExp, sumErr );
        if ( nsigmam>nsigma3 ) {
            return StatTools::FindSNSigma( nEvtExp, sumErr, nsigma3, signald, (signald+signalu)/2 ) ;
        } else {
            return StatTools::FindSNSigma( nEvtExp, sumErr, nsigma3, (signald+signalu)/2, signalu ) ;
        }
    }

    // no initial solution 
    return -1.;
}


//________________________________________________________________________________________________
Double_t StatTools::FindSignal( Double_t nObs, Double_t nEvtExp, Double_t sumErr, Double_t signald, Double_t signalu, Double_t pValue, Double_t tol ) {
    Double_t pd = StatTools::GetSimpleP1( nObs, nEvtExp+signald, sumErr );
    Double_t pu = StatTools::GetSimpleP1( nObs, nEvtExp+signalu, sumErr );

    if (pd>pValue && pu<pValue) {
        if (signalu-signald<tol) 
            return (signald+signalu)/2. ;

        Double_t pm = StatTools::GetSimpleP1( nObs, nEvtExp+(signald+signalu)/2., sumErr );
        if (pm < pValue) {
            return StatTools::FindSignal( nObs, nEvtExp, sumErr, signald, (signald+signalu)/2., pValue ) ;
        } else {
            return StatTools::FindSignal( nObs, nEvtExp, sumErr, (signald+signalu)/2., signalu, pValue ) ;
        }
    } 

    // no solution
    return -1.;
}


//________________________________________________________________________________________________
Double_t  StatTools::FindXS95( Double_t nObs, Double_t nBkgExp, Double_t nBkgErr, Double_t signalEff, Double_t lumi, Double_t pValue ) {
    if ( signalEff<=0 || lumi<=0 ) 
        return -1;
    
    if ( pValue<0 || pValue>1 ) 
        return -1; 

    double nsigma = StatTools::GetSigma(pValue) ;
    double dll95 = nsigma*nsigma / 2. ;

    double s95 = StatTools::FindS95( nObs, nBkgExp, nBkgErr, 0, 100, dll95 );
    if (s95<0) 
        return -1;

    return s95 / (signalEff*lumi) ;
}


//________________________________________________________________________________________________
Double_t StatTools::FindXSNSigma( Double_t nBkgExp, Double_t nBkgErr, Double_t signalEff, Double_t lumi, Double_t nsigma3, Double_t signalu ) {
    if ( signalEff<=0 || lumi<=0 ) 
        return -1;
    
    if ( nsigma3<0 ) 
        return -1;

    double snsigma3 = StatTools::FindSNSigma( nBkgExp, nBkgErr, nsigma3, 0.0, signalu );
    if (snsigma3<0) 
        return -1;

    return snsigma3 / (signalEff*lumi) ;  
}


//________________________________________________________________________________________________
Double_t StatTools::FindXSNSigma( Double_t nBkgExp1, Double_t nBkgErr1, Double_t signalEff1, Double_t nBkgExp2, Double_t nBkgErr2, Double_t signalEff2, Double_t lumi, Double_t nsigma3, Double_t xsectiond, Double_t xsectionu, Double_t tol ) {
    double signal1d = signalEff1 * lumi * xsectiond;
    double signal1u = signalEff1 * lumi * xsectionu;
    double signal2d = signalEff2 * lumi * xsectiond;
    double signal2u = signalEff2 * lumi * xsectionu;

    double dlld = StatTools::GetDLL( nBkgExp1+signal1d, nBkgExp1, nBkgErr1 ) + StatTools::GetDLL( nBkgExp2+signal2d, nBkgExp2, nBkgErr2 );
    double dllu = StatTools::GetDLL( nBkgExp1+signal1u, nBkgExp1, nBkgErr1 ) + StatTools::GetDLL( nBkgExp2+signal2u, nBkgExp2, nBkgErr2 );

    double nsigmad = TMath::Sqrt(2.0*dlld) ;
    double nsigmau = TMath::Sqrt(2.0*dllu) ;

    if ( nsigmad<nsigma3 && nsigmau>nsigma3 ) {
        if (nsigmau-nsigmad < tol) { 
            return (xsectiond+xsectionu)/2. ; 
        }

        double signal1m = (signal1d+signal1u)/2.0;
        double signal2m = (signal2d+signal2u)/2.0;
        double dllm = StatTools::GetDLL( nBkgExp1+signal1m, nBkgExp1, nBkgErr1 ) + StatTools::GetDLL( nBkgExp2+signal2m, nBkgExp2, nBkgErr2 );
        double nsigmam = TMath::Sqrt(2.0*dllm) ;

        if ( nsigmam>nsigma3 ) {
            return StatTools::FindXSNSigma( nBkgExp1, nBkgErr1, signalEff1, nBkgExp2, nBkgErr2, signalEff2, lumi, nsigma3, xsectiond, (xsectiond+xsectionu)/2., tol );
        } else {
            return StatTools::FindXSNSigma( nBkgExp1, nBkgErr1, signalEff1, nBkgExp2, nBkgErr2, signalEff2, lumi, nsigma3, (xsectiond+xsectionu)/2., xsectionu, tol );
        }
    }

    // no initial solution 
    return -1.;
}


//________________________________________________________________________________________________
Double_t StatTools::FindXS95( Double_t nObs1, Double_t nBkgExp1, Double_t nBkgErr1, Double_t signalEff1, 
        Double_t nObs2, Double_t nBkgExp2, Double_t nBkgErr2, Double_t signalEff2,
        Double_t lumi, Double_t dll95, Double_t xsectiond, Double_t xsectionu, Double_t tol ) {
    double signal1d = signalEff1 * lumi * xsectiond;
    double signal1u = signalEff1 * lumi * xsectionu;
    double signal2d = signalEff2 * lumi * xsectiond;
    double signal2u = signalEff2 * lumi * xsectionu;

    double dlld = StatTools::GetDLL( nObs1, nBkgExp1+signal1d, nBkgErr1 ) + StatTools::GetDLL( nObs2, nBkgExp2+signal2d, nBkgErr2 );
    double dllu = StatTools::GetDLL( nObs1, nBkgExp1+signal1u, nBkgErr1 ) + StatTools::GetDLL( nObs2, nBkgExp2+signal2u, nBkgErr2 );

    if ( dlld<dll95 && dllu>dll95 ) {
        if (xsectionu-xsectiond<tol) { 
            return (xsectionu+xsectiond)/2. ; 
        }

        double xsectionm = (xsectionu+xsectiond)/2. ;

        double signal1m = signalEff1 * lumi * xsectionm;
        double signal2m = signalEff2 * lumi * xsectionm;

        Double_t dllm = StatTools::GetDLL( nObs1, nBkgExp1+signal1m, nBkgErr1 ) + StatTools::GetDLL( nObs2, nBkgExp2+signal2m, nBkgErr2 );
        if ( dllm>dll95 ) {
            return StatTools::FindXS95( nObs1, nBkgExp1, nBkgErr1, signalEff1, nObs2, nBkgExp2, nBkgErr2, signalEff2, lumi, dll95, xsectiond, xsectionm, tol) ;
        } else {
            return StatTools::FindXS95( nObs1, nBkgExp1, nBkgErr1, signalEff1, nObs2, nBkgExp2, nBkgErr2, signalEff2, lumi, dll95, xsectionm, xsectionu, tol) ;
        }
    }

    // no initial solution 
    return -1.;
}

// The following methods are based on: hep 0312059 J. Linnemann and references therein
// definitions:
//   1)  null hypothesis (H0), p-value : p = P( s >= observed | assume only background )
//   2)  std deviation [sigma]         : Z = ErrInv( 1 - p )
//       with:  Err(z) = 1/sqrt(2 pi) * int_{-inf}^{z} { exp(-t^2 / 2) dt }
//                     = normal distribution from -inf to z
//
//   Note: this allows for negative Z numbers ! e.g. p=0 corresponds to Z=-inf;
//         p=0.5 corr. Z=0.0;
//
// The two methods below implement the defitions from above in a consistent way, ie
// 2e-6 = GetProbFromSigma( GetSigmafromProb( 2e-6 ) ).
//
// Conversion overview table:
//   Sigma  <=>  p-value
//   0.0         0.5
//   1.0         1.587e-01  ~ (1 - 84.1%)
//   2.0         2.275e-02  ~ (1 - 97.7%)
//   3.0         1.350e-03
//   4.0         3.167e-05
//   5.0         2.867e-07

//________________________________________________________________________________________________
Double_t StatTools::GetProbFromSigma( Double_t nsigma ) {
    Double_t p = -1.0;

    if (nsigma>0){
        p = 0.5*TMath::Prob(nsigma*nsigma,1);
    } else{
        p = 1-0.5*TMath::Prob(nsigma*nsigma,1);
    }
    
    if (nsigma < 7.4 && nsigma > -7.4) {
        p =  1. - (0.5 + 0.5 * TMath::Erf( nsigma / TMath::Sqrt(2.) ) );
    } else{
        bool sigsign=nsigma>0;
        p=1.0;
        if (sigsign){
            p=0;
        }
    }
    return p;
}


//________________________________________________________________________________________________
Double_t StatTools::GetSigma( Double_t p ) {
    // Equiv: S = TMath::NormQuantile(1-p)

    // double pres limit:
    if (p > (1.0-1e-16)){
        return -7.4;
    }   
    // double pres limit:
    if (p < 1e-16){
        return 7.4;
    }   
    // convert p-value in standard deviations ("nsigma")
    Double_t nsigma = 0;
    if (p > 1.0e-16) { 
        nsigma = TMath::ErfInverse( 1.0 - 2.0 * p )*TMath::Sqrt(2.0);
    } else if (p > 0) {
        // use approximation, ok for sigma > 1.5
        Double_t u = -2.0 * TMath::Log( p*TMath::Sqrt( 2.*TMath::Pi() ) );
        nsigma = TMath::Sqrt( u - TMath::Log(u) );
    } else {
        nsigma = -1;
    }

    return nsigma;
}


//________________________________________________________________________________________________
Double_t StatTools::DmLogL_PA( Double_t nObs, Double_t nb, Double_t sig ) {
    Double_t sig2 = sig*sig;
    Double_t sig4 = sig2*sig2;
    Double_t nb2  = nb*nb;
    Double_t retval = 0;

    Double_t A = TMath::Sqrt(nb2 + 4*nObs*sig2 - 2*nb*sig2 + sig4);
    retval = ( (nb - sig2 + A + TMath::Power(nb + sig2 - A, 2)/(4.0*sig2))/2.0 +
            nObs*(TMath::Log(nObs) - 1.0 - TMath::Log(nb - sig2 + A) + TMath::Log(2.0)) );

    return retval;
}


//________________________________________________________________________________________________
Double_t StatTools::GetDLL( Double_t nObs, Double_t nb, Double_t sig ) {
    Double_t sig2 = sig*sig;
    Double_t sig4 = sig2*sig2;
    Double_t nb2  = nb*nb;
    Double_t retval = 0;

    Double_t A = TMath::Sqrt(nb2 + 4*nObs*sig2 - 2*nb*sig2 + sig4);
    retval = ( (nb - sig2 + A + TMath::Power(nb + sig2 - A, 2)/(4.0*sig2))/2.0 +
            nObs*(TMath::Log(nObs) - 1.0 - TMath::Log(nb - sig2 + A) + TMath::Log(2.0)) );

    if (retval < 0) retval = 0;

    return retval;
}


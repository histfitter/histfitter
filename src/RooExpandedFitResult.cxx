// vim: ts=4:sw=4 
/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Class  : RooExpandedFitResult                                                  *
 * Created: March 2012
 *                                                                                *
 * Description:                                                                   *
 *      Implementation (see header for description)                               *
 *                                                                                *
 * See corresponding .h file for author and license information                   *         
 *                                                                                *
 **********************************************************************************/

#include "RooExpandedFitResult.h"

#include "RooRealVar.h"
#include <iostream>
using namespace std;

ClassImp(RooExpandedFitResult);

//_______________________________________________________________________________________
RooExpandedFitResult::RooExpandedFitResult(RooFitResult* origResult, RooArgList extraPars){

    TString name,title ;
    name = Form("Expanded%s", origResult->GetName()) ;
    title = Form("Expanded%s", origResult->GetTitle()) ;

    SetName(name);
    SetTitle(title);

    // Get all parameters from 
    RooArgList saveConstList;
    RooArgList saveFloatInitList =  origResult->floatParsInit();
    RooArgList origFloatInitList =  origResult->floatParsInit();
    RooArgList saveFloatFinalList = origResult->floatParsFinal();
    RooArgList origFloatFinalList =  origResult->floatParsFinal();
    // add all the floating parameters from original result and the extra Pars, that are not in RooFitResult already)
    for( Int_t j=0; j<extraPars.getSize(); j++){
        RooAbsArg* par = extraPars.at(j) ;
        if(! saveFloatInitList.contains(*par))  saveFloatInitList.add(*par); 
        if(! saveFloatFinalList.contains(*par))  saveFloatFinalList.add(*par);
    }

    // Move eventual fixed paramaters in floatList to constList
    // a copy is needed, otherwise looping and removing from the same list in for-loop
    RooArgList allPars = saveFloatFinalList;
    for (Int_t i = 0 ; i < allPars.getSize() ; i++) {
        RooAbsArg* par = allPars.at(i) ;
        if (par->isConstant()) {
            saveFloatInitList.remove(*saveFloatInitList.find(par->GetName()),kTRUE) ;
            saveFloatFinalList.remove(*saveFloatFinalList.find(par->GetName()),kTRUE) ;
            if(! saveConstList.contains(*par))  saveConstList.add(*par) ;
        }
    }
    saveConstList.sort() ;

    // Save all (original+extra) floating/const parameters to new RooExpandedFitResult
    setConstParList(saveConstList) ;
    setInitParList(saveFloatInitList) ;
    setFinalParList(saveFloatFinalList) ;

    setStatus(origResult->status()) ;
    std::vector<std::pair<std::string,int> > statusHistory(origResult->numStatusHistory());
    for(unsigned int k= 0; k<origResult->numStatusHistory(); k++){
        std::pair<std::string,int> sh(origResult->statusLabelHistory(k), origResult->statusCodeHistory(k));
        statusHistory[k] = sh;
    }
    setStatusHistory(statusHistory) ;

    setCovQual(origResult->covQual()) ;
    setMinNLL(origResult->minNll()) ;
    setNumInvalidNLL(origResult->numInvalidNLL()) ;
    setEDM(origResult->edm()) ;

    // store global Correlation Coefficients
    std::vector<double> globalCC;
    for (Int_t ic=0; ic<saveFloatFinalList.getSize(); ic++) {
        RooAbsArg* par = saveFloatFinalList.at(ic) ;
        if( origFloatFinalList.contains(*par)) globalCC.push_back(origResult->globalCorr(*par));
        else globalCC.push_back(0.0);
    }

    // create and store new correlation/covariance matrices
    TMatrixDSym corrs(saveFloatFinalList.getSize()) ;
    TMatrixDSym covs(saveFloatFinalList.getSize()) ;
    for (Int_t ic=0; ic<saveFloatFinalList.getSize(); ic++) {
        RooAbsArg* par1 = saveFloatFinalList.at(ic) ;
        for (Int_t ii=0; ii<saveFloatFinalList.getSize(); ii++) {
            RooAbsArg* par2 = saveFloatFinalList.at(ii) ;
            // check whether the parameters were in the original RooFitResult
            if( origFloatFinalList.contains(*par1) && origFloatFinalList.contains(*par2)){
                corrs(ic,ii) = origResult->correlation(*par1,*par2);
                covs(ic,ii) = origResult->covarianceMatrix()[ic][ii];
            }
            else{
                // covariance matrix[ic][ii] = sigma_ic * sigma_ii * corr(par1,par2)
                //  hence only applicable to the diagonal of cov.matrix, where corr=1 (everywhere else corr=0)
                if(ic==ii ){
                    corrs(ic,ii) = 1.;
                    if(par1->InheritsFrom("RooRealVar") &&  par2->InheritsFrom("RooRealVar")){
                        covs(ic,ii) = ((RooRealVar*) par1)->getError() * ((RooRealVar*) par2)->getError() ;
                    }
                    else  covs(ic,ii) = 1e-300; 
                }
                else{
                    corrs(ic,ii) = 1e-300; 
                    covs(ic,ii) = 1e-300; 
                }
            }
        }
    }

    fillCorrMatrix(globalCC,corrs,covs) ;

}


//______________________________________________________________________________________
RooExpandedFitResult::RooExpandedFitResult(RooArgList extraPars){

    TString name,title ;
    name = "RooExpandedFitResult";
    title = "RooExpandedFitResult";

    SetName(name);
    SetTitle(title);

    // Get all parameters from 
    RooArgList saveConstList;
    RooArgList saveFloatInitList = extraPars;
    RooArgList origFloatInitList = extraPars;
    RooArgList saveFloatFinalList = extraPars; 
    RooArgList origFloatFinalList =  extraPars; 

    // Move eventual fixed paramaters in floatList to constList
    // a copy is needed, otherwise looping and removing from the same list in ne for-loop
    RooArgList allPars = saveFloatFinalList;
    for (Int_t i = 0 ; i < allPars.getSize() ; i++) {
        RooAbsArg* par = allPars.at(i) ;
        if (par->isConstant()) {
            saveFloatInitList.remove(*saveFloatInitList.find(par->GetName()),kTRUE) ;
            saveFloatFinalList.remove(*saveFloatFinalList.find(par->GetName()),kTRUE) ;
            if(! saveConstList.contains(*par))  saveConstList.add(*par) ;
        }
    }
    saveConstList.sort() ;

    // Save all (original+extra) floating/const parameters to new RooExpandedFitResult
    setConstParList(saveConstList) ;
    setInitParList(saveFloatInitList) ;
    setFinalParList(saveFloatFinalList) ;

    setStatus(1) ;
    std::vector<std::pair<std::string,int> > statusHistory(1);
    std::pair<std::string,int> sh("dummy",0);
    statusHistory[0] = sh;
    setStatusHistory(statusHistory) ;

    setCovQual(0) ;
    setMinNLL(0.);
    setNumInvalidNLL(0);
    setEDM(0.);

    // store global Correlation Coefficients
    std::vector<double> globalCC;
    for (Int_t ic=0; ic<saveFloatFinalList.getSize(); ic++) {
        globalCC.push_back(0.);
    }

    // create new matrix
    TMatrixDSym corrs(saveFloatFinalList.getSize()) ;
    TMatrixDSym covs(saveFloatFinalList.getSize()) ;
    for (Int_t ic=0; ic<saveFloatFinalList.getSize(); ic++) {
        RooAbsArg* par1 = saveFloatFinalList.at(ic) ;
        for (Int_t ii=0; ii<saveFloatFinalList.getSize(); ii++) {
            RooAbsArg* par2 = saveFloatFinalList.at(ii) ;
            // covariance matrix[ic][ii] = sigma_ic * sigma_ii * corr(par1,par2)
            //  hence only applicable to the diagonal of cov.matrix, where corr=1 (everywhere else corr=0)
            if(ic==ii ){
                corrs(ic,ii) = 1.;
                if(par1->InheritsFrom("RooRealVar") &&  par2->InheritsFrom("RooRealVar")){
                    covs(ic,ii) = ((RooRealVar*) par1)->getError() * ((RooRealVar*) par2)->getError() ;
                }
                else{
                    covs(ic,ii) = 1e-300; 
                }
            }
            else{
                corrs(ic,ii) = 1e-300; 
                covs(ic,ii) = 1e-300; 
            }
        }
    }

    fillCorrMatrix(globalCC,corrs,covs) ;
}

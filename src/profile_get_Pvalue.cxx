// vim: ts=4:sw=4
#include "profile_get_Pvalue.h"
#include "toy_utils.h"
#include "CombinationUtils.h"
#include "TObjString.h"
#include "TTree.h"
#include <sstream>
#include <math.h>
#include <iostream>
#include <fstream>
#include "RooMsgService.h"
#include "RooRandom.h"
#include "RooWorkspace.h"
#include "TMath.h"
#include "RooStats/ModelConfig.h"
#include "RooFitResult.h"
#include "RooAbsData.h"
#include "RooDataSet.h"
#include "RooProdPdf.h"
#include "RooRealVar.h"
#include "Significance.h"

using namespace RooFit;
using namespace RooStats;


//________________________________________________________________________________________________
void doFreeFit( const RooWorkspace* fullwspace, RooDataSet* inputdata, bool verbose ) {
    RooFitResult* result = doFreeFitSave( fullwspace, inputdata, verbose );
    delete result;

    return;
}


//________________________________________________________________________________________________
RooFitResult* doFreeFitSave( const RooWorkspace* fullwspace, RooDataSet* inputdata, bool verbose ) {
    // fit to reset the workspace

    if(!fullwspace){
        std::cerr << "ERROR: Input workspace is null!" << std::endl;
        return 0;
    }

    if(!fullwspace->obj("text_suffix")){
        std::cerr << "ERROR: No suffix found, this workspace can not be automatically combined using this function. If possible recreate your single workspaces with newer code" << std::endl;
        return 0;
    }

    TString suffix("");
    if(strcmp("",fullwspace->obj("text_suffix")->GetTitle()))
        suffix=TString("_")+fullwspace->obj("text_suffix")->GetTitle();

    RooDataSet* data_set(0);
    if (inputdata!=0) data_set = inputdata;
    else              data_set = dynamic_cast<RooDataSet*>(fullwspace->data("data_set"+suffix));
    RooAbsPdf* full_model_thispdf =dynamic_cast<RooAbsPdf*>( fullwspace->pdf("full_model"+suffix));

    if (verbose) data_set->Print();

    if((!data_set)||(!full_model_thispdf)){
        std::cerr << "ERROR: data set or pdf not found" <<std::endl;
        std::cerr << "     :   pdfname    =" <<"full_model"+suffix<<std::endl;
        std::cerr << "     :   datasetname=" <<"data_set"+suffix<<std::endl;
        return 0;
    }

    //////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // Free fit:
    RooRealVar* mu = fullwspace->var("mu");
    mu->setRange(0,10000);
    mu->setVal(0.5); // start value. 
    mu->setConstant(0);
    RooFitResult* result = full_model_thispdf->fitTo(*data_set,PrintLevel(verbose?1:-1),Verbose(verbose?1:0),Save());
    mu->setRange(-100,10000);

    return result;
}

// vim: ts=4:sw=4
/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Namespace: Util                                                                *
 *                                                                                *
 * Description:                                                                   *
 *      Implementation (see header for description)                               *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva, Switzerland                               *
 *                                                                                *
 * See corresponding .h file for author and license information                   *
 **********************************************************************************/

#include "CombinationUtils.h"

#include "TMath.h"
#include "RooArgList.h"
#include "RooRealVar.h"
#include "RooFitResult.h"
#include "RooWorkspace.h"
#include "TTree.h"
#include "TMsgLogger.h"
#include "TFile.h"

using namespace std;


//________________________________________________________________________________________________
void resetFloatPars( const RooWorkspace* w, const RooFitResult* result ) {
    const RooArgList& floatParsInit = result->floatParsInit() ;

    for (int i=0; i<floatParsInit.getSize(); ++i) {
        RooRealVar* cvar = (RooRealVar *)floatParsInit.at(i);
        RooRealVar* var = (RooRealVar *)w->var(cvar->GetName());
        var->setVal(cvar->getVal());
    }
}


//_____________________________________________________________________________
namespace Util {
    static TMsgLogger CombinationUtilsLogger("CombinationUtils");
}


//_____________________________________________________________________________
float Util::getValueFromTree( TTree* tree, const std::string& searchpar,
        const std::string& pn0, const float& v0, const std::string& pn1, const float& v1,
        const std::string& pn2, const float& v2, const std::string& pn3, const float& v3,
        const std::string& pn4, const float& v4, const std::string& pn5, const float& v5,
        const std::string& pn6, const float& v6, const std::string& pn7, const float& v7,
        const std::string& pn8, const float& v8, const std::string& pn9, const float& v9 ) {
    std::vector<std::string> pnVec;
    std::vector<float> vVec;

    if ( !pn0.empty() ) { pnVec.push_back(pn0); vVec.push_back(v0); }
    if ( !pn1.empty() ) { pnVec.push_back(pn1); vVec.push_back(v1); }
    if ( !pn2.empty() ) { pnVec.push_back(pn2); vVec.push_back(v2); }
    if ( !pn3.empty() ) { pnVec.push_back(pn3); vVec.push_back(v3); }
    if ( !pn4.empty() ) { pnVec.push_back(pn4); vVec.push_back(v4); }
    if ( !pn5.empty() ) { pnVec.push_back(pn5); vVec.push_back(v5); }
    if ( !pn6.empty() ) { pnVec.push_back(pn6); vVec.push_back(v6); }
    if ( !pn7.empty() ) { pnVec.push_back(pn7); vVec.push_back(v7); }
    if ( !pn8.empty() ) { pnVec.push_back(pn8); vVec.push_back(v8); }
    if ( !pn9.empty() ) { pnVec.push_back(pn9); vVec.push_back(v9); }

    return Util::getValueFromTree( tree, searchpar, pnVec, vVec );
}


//_____________________________________________________________________________
float Util::getValueFromTree( TTree* tree, const std::string& searchpar, const std::vector<std::string>& pnVec, const std::vector<float>& vVec ) {
    float searchval(-1);
    bool matchfound = Util::findValueFromTree( tree,searchpar,searchval,pnVec,vVec );

    if (!matchfound) 
        CombinationUtilsLogger << kERROR << "no value found for search parameter : " << searchpar << GEndl;

    return searchval;
}


//_____________________________________________________________________________
bool Util::findValueFromTree( TTree* tree, const std::string& searchpar, float& searchval,
        const std::string& pn0, const float& v0, const std::string& pn1, const float& v1,
        const std::string& pn2, const float& v2, const std::string& pn3, const float& v3,
        const std::string& pn4, const float& v4, const std::string& pn5, const float& v5,
        const std::string& pn6, const float& v6, const std::string& pn7, const float& v7,
        const std::string& pn8, const float& v8, const std::string& pn9, const float& v9 ) {
    std::vector<std::string> pnVec;
    std::vector<float> vVec;

    if ( !pn0.empty() ) { pnVec.push_back(pn0); vVec.push_back(v0); }
    if ( !pn1.empty() ) { pnVec.push_back(pn1); vVec.push_back(v1); }
    if ( !pn2.empty() ) { pnVec.push_back(pn2); vVec.push_back(v2); }
    if ( !pn3.empty() ) { pnVec.push_back(pn3); vVec.push_back(v3); }
    if ( !pn4.empty() ) { pnVec.push_back(pn4); vVec.push_back(v4); }
    if ( !pn5.empty() ) { pnVec.push_back(pn5); vVec.push_back(v5); }
    if ( !pn6.empty() ) { pnVec.push_back(pn6); vVec.push_back(v6); }
    if ( !pn7.empty() ) { pnVec.push_back(pn7); vVec.push_back(v7); }
    if ( !pn8.empty() ) { pnVec.push_back(pn8); vVec.push_back(v8); }
    if ( !pn9.empty() ) { pnVec.push_back(pn9); vVec.push_back(v9); }

    return Util::findValueFromTree( tree, searchpar, searchval, pnVec, vVec );
}


//_____________________________________________________________________________
bool Util::findValueFromTree( TTree* tree, const std::string& searchpar, float& searchval, const std::vector<std::string>& pnVec, const std::vector<float>& vVec, const float& defaultVal ) {
    if (tree==0) return false;
    if (pnVec.size()!=vVec.size()) return false;
    if (pnVec.size()==0) return false;
    if (searchpar.empty()) return false;

    const int nidpar = static_cast<int>( pnVec.size() ); 

    float val[nidpar], sval(defaultVal);
    TBranch* branch[nidpar], *sbranch(0);

    // set branches
    for (Int_t i=0; i<nidpar; ++i) { 
        tree->SetBranchAddress( pnVec[i].c_str(), &val[i], &branch[i] );
        if (branch[i]==0) { 
            CombinationUtilsLogger << kERROR << "no branch found with name : " << pnVec[i] << ". Return false." << GEndl;
            return false;
        }
    }  

    // search par
    tree->SetBranchAddress( searchpar.c_str(), &sval, &sbranch );
    if (sbranch==0) {
        CombinationUtilsLogger << kERROR << "no branch found with name : " << searchpar << ". Return false." << GEndl;
        return false;
    }

    bool match(true);
    for( Int_t i=0; i<tree->GetEntries(); i++ ){
        tree->GetEntry( i );
        match = true;
        for (Int_t j=0; j<nidpar && match; ++j) { if (vVec[j]!=val[j]) match=false; }
        if (match) break;
    }

    if (match) { searchval=sval; }
    else { searchval=defaultVal; }

    return match;
}




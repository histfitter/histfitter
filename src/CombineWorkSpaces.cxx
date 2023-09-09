// vim: ts=4:sw=4
/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Namespace: CombineWorkspaces                                                   *
 *                                                                                *
 * Description:                                                                   *
 *      Implementation (see header for description)                               *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva, Switzerland                               *
 *                                                                                *
 * See corresponding .h file for author and license information                   *
 **********************************************************************************/
// STL include(s):
#include <stdio.h>

// ROOT include(s)
#include "RooArgSet.h"
#include "RooAbsPdf.h"
#include "RooRealVar.h"
#include "RooConstVar.h"
#include "RooAbsData.h"
#include "RooDataSet.h"
#include "RooProduct.h"
#include "RooAddition.h"
#include "RooCustomizer.h"
#include "RooProdPdf.h"
#include "RooWorkspace.h"
#include "RooStats/RooStatsUtils.h"
#include "RooStats/HypoTestInverterResult.h"
#include "RooCategory.h"
#include "RooWorkspace.h"
#include "RooSimultaneous.h"
#include "RooProdPdf.h"
#include "RooStats/ModelConfig.h"
#include "TFile.h"
#include "TKey.h"
#include "TObject.h"
#include "TObjArray.h"
#include "TObjString.h"
#include "TEasyFormula.h"
#include "RooMCStudy.h"
#include "RooFitResult.h"
#include "Roo1DTable.h"

// HistFitter include(s)
#include "CombineWorkSpaces.h"
#include "CombinationUtils.h"
#include "Utils.h"
#include "TMsgLogger.h"

using namespace std;
using namespace RooFit;
using namespace RooStats;

using hf::kDEBUG;
using hf::kINFO;
using hf::kERROR;
using hf::kFATAL;


static hf::TMsgLogger CombineWorkSpacesLogger("CombineWorkSpaces");


//________________________________________________________________________________________________
void hf::clearVec( std::vector<RooWorkspace*>& wsVec ) {
    //std::vector<RooWorkspace*>::iterator wItr=wsVec.begin(), wEnd=wsVec.end();
    //for (; wItr!=wEnd; ++wItr) {
    for(auto *wItr: wsVec) {
        if ( wItr !=0) {
            delete (wItr);
        }
    }
    wsVec.clear();
}


//________________________________________________________________________________________________
/* This function retrieves workspaces from files as specified in fwnameMap, where
 * the key is the filename, and map[key] gives the identifyer of the workspace.
 * wid is the new names of the retrieved workspaces
 */
std::vector<RooWorkspace*> hf::CollectWorkspaces( const std::map< TString,TString >& fwnameMap, const TString& wid ) {
    std::vector<RooWorkspace*> wsVec;
    //std::map< TString,TString >::const_iterator wfItr=fwnameMap.begin(), wfEnd=fwnameMap.end();

    unsigned int i = 0;
    for(auto const &wfItr : fwnameMap) {
        //for (int i=0; wfItr!=wfEnd; ++wfItr, ++i) {
        ++i;
        RooWorkspace* w = hf::Util::GetWorkspaceFromFile( wfItr.first.Data(), wfItr.second );
        if ( w==0 ) {
            CombineWorkSpacesLogger << kFATAL << "Cannot open workspace <" << wfItr.second << "> in file <" << wfItr.second << ">" << GEndl;
        }

        CombineWorkSpacesLogger << kINFO << "Now collecting <" << wfItr.first << "> <" << wfItr.second << ">" << GEndl;

        w->SetName( Form("%s%d",wid.Data(),i) );
        wsVec.push_back(w);
    }

return wsVec;
}


//________________________________________________________________________________________________
/* this function categorizes all workspaces found in infile, whose names match the format
 * string, eg. "muSUSY10_3j_20pb_SU_%f_%f_0_3", where %f and %f are mapped onto the parameters "m0:m12"
 */
std::map< TString,TString > hf::GetMatchingWorkspaces( const TString& infile, const TString& theformat, const TString& interpretation, const TString& cutStr, const Int_t& fID, TTree* ORTree ) {

    CombineWorkSpacesLogger << kDEBUG   << " GetMatchingWorkspaces() : infile = " << infile << GEndl;
    CombineWorkSpacesLogger << kDEBUG   << " GetMatchingWorkspaces() : theformat = " << theformat << GEndl ;
    CombineWorkSpacesLogger << kDEBUG   << " GetMatchingWorkspaces() : interpretation=" << interpretation << GEndl;
    CombineWorkSpacesLogger << kDEBUG   << " GetMatchingWorkspaces() : cutStr=" << cutStr << GEndl;
    CombineWorkSpacesLogger << kDEBUG   << " GetMatchingWorkspaces() : fID = " << fID  << GEndl ;//<< " ORTree = " << ORTree->GetName() << GEndl;

    std::map< TString,TString > wsidMap;

    TFile* file = TFile::Open(infile.Data(), "READ");
    if (file->IsZombie()) {
        CombineWorkSpacesLogger << kFATAL << "Cannot open file: " << infile << GEndl;
    }


    TString format = theformat;
    CombineWorkSpacesLogger << kDEBUG << " 1  format = " << format << GEndl;
    Bool_t searchFileName(kFALSE);
    if (format.BeginsWith("filename+")) {
        format = format.ReplaceAll("filename+","");
        searchFileName = kTRUE;
    }

    CombineWorkSpacesLogger << kDEBUG << " 2  format = " << format << GEndl;

    TString fullWSName;
    if (searchFileName) {
        TObjArray* iArr = format.Tokenize("+");
        int narg = iArr->GetEntries();
        if (narg==2) {
            fullWSName = ((TObjString*)iArr->At(1))->GetString();
        }
        delete iArr;
    }
    CombineWorkSpacesLogger << kDEBUG << " 3  fullWSName = " << fullWSName << GEndl;

    TObjString* objString = NULL;
    std::map<TString,int> keymap;
    int narg1 = format.CountChar('%');
    TString wsid, wsname, wssel, wsnameSearch;
    std::vector<float> wsarg(10);

    TObjArray* iArr = interpretation.Tokenize(":");
    int narg3 = iArr->GetEntries();
    if (narg1!=narg3) {
        delete iArr;
        CombineWorkSpacesLogger << kFATAL << "No valid interpretation string <" << interpretation << "> with format <" << format << ">, for file <" << infile << ">" << GEndl;
        exit(-1);
    }

    std::vector<std::string> wsidvec; //[narg3];
    for (int i=0; i<narg3; ++i) {
        objString = (TObjString*)iArr->At(i);
        wsidvec.push_back( objString->GetString().Data() );
    }

    CombineWorkSpacesLogger << kDEBUG << " 4  wsidvec.size() = " << wsidvec.size() << GEndl;
    for(unsigned int i=0; i<wsidvec.size();i++){
        CombineWorkSpacesLogger << kDEBUG << " wsidvec[" << i << "] = " << wsidvec[i] << GEndl;
    }

    file->cd();

    hf::TEasyFormula formula( cutStr.Data() );

    TList* list = file->GetListOfKeys();
    CombineWorkSpacesLogger << kDEBUG << " 5 list : "  << GEndl;
    if(CombineWorkSpacesLogger.GetMinLevel() < kINFO) {
        list->Print("v");
    }
    for(int j=0; j<list->GetEntries(); j++) {
        TKey* key = (TKey*)list->At(j);
        // get proper index with name
        // NOTE: wsid always connects to highest key-index found in file!
        if ( keymap.find(key->GetName())==keymap.end() ) { keymap[key->GetName()] = key->GetCycle(); }
        else if ( key->GetCycle() > keymap[key->GetName()] ) { keymap[key->GetName()] = key->GetCycle(); }
        wsname = Form("%s;%d",key->GetName(),keymap[key->GetName()]) ;
        wsnameSearch = wsname;
        CombineWorkSpacesLogger << kDEBUG <<" 5.1   j = " << j << " wsnameSearch = " << wsnameSearch << GEndl;

        if (searchFileName && !fullWSName.IsNull()) { // E.g. WS is called combined
            CombineWorkSpacesLogger << kDEBUG << " 5.2   searchFileName && !fullWSName.IsNull() = " << (searchFileName && !fullWSName.IsNull()) << GEndl;
            CombineWorkSpacesLogger << kDEBUG << " 5.3   TString(key->GetName())) = " << TString(key->GetName()) << GEndl;
            if (fullWSName != TString(key->GetName()))  continue;
        }


        //// Turn off, this is slow! Reading the object and checking for non-NULL doesnt make a lot of sense
        //// -> we check for NULL when really reading anyway!
        //// confirm this is a workspace
        //TObject* obj = file->Get( wsname.Data() );
        //if (obj==0) continue;
        ////	if ( obj->ClassName()!=TString("RooWorkspace") ) continue;

        CombineWorkSpacesLogger << kDEBUG << " 5.4  searchFileName = " << searchFileName << GEndl;
        if (searchFileName) {
            wsnameSearch = infile + "_" + wsnameSearch;
        }
        CombineWorkSpacesLogger << kDEBUG << " 5.5  wsnameSearch = " << wsnameSearch << GEndl;

        // accept upto 10 args in ws name
        int narg2 = sscanf( wsnameSearch.Data(), format.Data(), &wsarg[0],&wsarg[1],&wsarg[2],&wsarg[3],&wsarg[4],&wsarg[5],&wsarg[6],&wsarg[7],&wsarg[8],&wsarg[9] );
        if ( !(narg1==narg2 && narg1==narg3 && narg2>0) ) { continue; }

        wsarg.resize(narg2);
        wsid.Clear();  // form unique ws id
        for (int i=0; i<narg2; ++i) {
            objString = (TObjString*)iArr->At(i);
            // wsid  += Form("%s_%.2f_", objString->GetString().Data(), wsarg[i]);
            wsid  += Form("%s=%.2f_", objString->GetString().Data(), wsarg[i]);
            formula.SetValue(objString->GetString(),wsarg[i]);
        }
        //wsid += Form( "%d_",keymap[key->GetName()] );
        if (!formula.GetBoolValue()) continue;

        if ((ORTree!=0) && fID>=0) { // logical orring
            float searchVal(-1);
            bool found = hf::Util::findValueFromTree(ORTree,"fID",searchVal,wsidvec,wsarg);
            if (!found)
                continue;
            if ( fID!=static_cast<int>(searchVal) )
                continue;
        }

        // NOTE: wsid always connects to highest key-index found in file!
        wsidMap[wsid] = wsname;
        CombineWorkSpacesLogger << kDEBUG  << " 5.6  wsidMap[ " << wsid << "] = " << wsname << GEndl;
    }

    CombineWorkSpacesLogger << kINFO << "Found : " << wsidMap.size() << " matching workspaces in file : " << infile << GEndl;

    file->Close();
    delete iArr;

    return wsidMap;
}

//________________________________________________________________________________________________
RooStats::HypoTestInverterResult* hf::GetHypoTestResultFromFile( TFile* file, const TString& wsname ) {

    if (!file || file->IsZombie()) {
        CombineWorkSpacesLogger << kERROR << "Invalid file. Pointer: " << file << GEndl;
        return nullptr;
    }

    TObject* obj = file->Get( wsname.Data() ) ;
    if (obj==0) {
        CombineWorkSpacesLogger << kERROR << "Cannot open HypoTestInverterResult <" << wsname << "> in file <" << file->GetName() << ">" << GEndl;
        return nullptr;
    }

    if ( obj->ClassName()!=TString("RooStats::HypoTestInverterResult") ) {
        CombineWorkSpacesLogger << kERROR << "Cannot open HypoTestInverterResult <" << wsname << "> in file <" << file->GetName() << ">" << GEndl;
        return nullptr;
    }

    RooStats::HypoTestInverterResult* w = (RooStats::HypoTestInverterResult*)( obj );
    if ( w==0 ) {
        CombineWorkSpacesLogger << kERROR << "Cannot open HypoTestInverterResult <" << wsname << "> in file <" << file->GetName() << ">" << GEndl;
        return nullptr;
    }

    RooStats::HypoTestInverterResult* v = (RooStats::HypoTestInverterResult*) w->Clone();

    // We don't own the file, so we don't close or delete anything

    return v;
}


//________________________________________________________________________________________________
RooFitResult* hf::GetFitResultFromFile( TFile* file, const TString& fitname ) {

    if (!file || file->IsZombie()) {
        CombineWorkSpacesLogger << kERROR << "Invalid file. Pointer: " << file << GEndl;
        return nullptr;
    }

    TObject* obj = file->Get( fitname.Data() ) ;
    if (obj==0) {
        CombineWorkSpacesLogger << kERROR << "Cannot open RooFitResult <" << fitname << "> in file <" << file->GetName() << ">" << GEndl;
        return nullptr;
    }

    if ( obj->ClassName()!=TString("RooFitResult") ) {
        CombineWorkSpacesLogger << kERROR << "Cannot open RooFitResult <" << fitname << "> in file <" << file->GetName() << ">" << GEndl;
        return nullptr;
    }

    RooFitResult* w = (RooFitResult*)( obj );
    if ( w==0 ) {
        CombineWorkSpacesLogger << kERROR << "Cannot open RooFitResult <" << fitname << "> in file <" << file->GetName() << ">" << GEndl;
        return nullptr;
    }

    RooFitResult* v = (RooFitResult*) w->Clone();

    // We don't own the file, so we don't close or delete anything

    return v;
}


//________________________________________________________________________________________________
RooMCStudy* hf::GetMCStudy( const RooWorkspace* w ) {
    if (w==0) {
        CombineWorkSpacesLogger << kERROR << "Input workspace is null. Return." << GEndl;
        return 0;
    }

    // suffix for workspace
    if( !w->obj("text_suffix") ) {
        CombineWorkSpacesLogger << kERROR << "No suffix found, this workspace can not be automatically combined using this function.\n"
            << "If possible recreate your single workspaces with newer code."
            << GEndl;
        return 0; //theresult;
    }
    TString suffix = w->obj("text_suffix")->GetTitle();
    if (!suffix.IsNull()) { suffix = "_" + suffix; }

    RooAbsData* data_set = w->data("data_set"+suffix) ;
    RooAbsPdf* full_model_thispdf = w->pdf("full_model"+suffix);

    if((!data_set)||(!full_model_thispdf)){
        CombineWorkSpacesLogger << kERROR << "data set or pdf not found" << GEndl;
        CombineWorkSpacesLogger << kERROR << "     pdfname    =" << "full_model"+suffix << GEndl;
        CombineWorkSpacesLogger << kERROR << "     datasetname=" << "data_set"+suffix << GEndl;
        return 0;
    }

    // get observables
    const RooArgSet* obsset = data_set->get();

    // caller owns mcstudy
    return ( new RooMCStudy(*full_model_thispdf,*obsset) ) ;
}


//________________________________________________________________________________________________
std::map<std::string, float> hf::ParseWorkspaceID( const TString& wid ) {
    // workspace id has form "m0=300.00_m12=700_"
    std::map<std::string, float> wconf;

    // basic checks
    if ( wid.Length()<3 ) return wconf;
    if ( wid.CountChar('=')==0 ) return wconf;

    TObjArray* iArr = wid.Tokenize("_");
    int narg = iArr->GetEntries();
    TString sub, par;
    float parVal;

    for (int i=0; i<narg; ++i) {
        sub = ((TObjString*)iArr->At(i))->GetString();
        if (sub.CountChar('=')!=1) continue;

        TObjArray* jArr = sub.Tokenize("=");
        if (jArr->GetEntries()!=2) { delete jArr; continue; }
        par = ((TObjString*)jArr->At(0))->GetString();
        parVal = ((TObjString*)jArr->At(1))->GetString().Atof();
        wconf[par.Data()] = parVal;
        delete jArr;
    }

    delete iArr;
    return wconf;
}

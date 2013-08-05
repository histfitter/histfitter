// vim: ts=4:sw=4
#include "CombineWorkSpaces.h"
#include "CombinationUtils.h"
#include "Utils.h"
#include <stdio.h>

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
#include "TMsgLogger.h"

#include "Roo1DTable.h"

using namespace std;
using namespace RooFit ;
using namespace RooStats ;

// -------------------------------
// read the header for information
// -------------------------------

static TMsgLogger CombineWorkSpacesLogger("CombineWorkSpaces");

//________________________________________________________________________________________________
void clearVec( std::vector<RooWorkspace*>& wsVec ) {
    std::vector<RooWorkspace*>::iterator wItr=wsVec.begin(), wEnd=wsVec.end();
    for (; wItr!=wEnd; ++wItr) { 
        if ((*wItr)!=0) { 
            delete (*wItr); 
        } 
    }
    wsVec.clear();
}


//________________________________________________________________________________________________
// This function retrieves workspaces from files as specified in fwnameMap, where
// the key is the filename, and map[key] gives the identifyer of the workspace.
// wid is the new names of the retrieved workspaces
//
std::vector<RooWorkspace*> CollectWorkspaces( const std::map< TString,TString >& fwnameMap, const TString& wid ) {
    std::vector<RooWorkspace*> wsVec;
    std::map< TString,TString >::const_iterator wfItr=fwnameMap.begin(), wfEnd=fwnameMap.end();

    for (int i=0; wfItr!=wfEnd; ++wfItr, ++i) {
      //cout << "  wfItr->first.Data() = " << wfItr->first.Data() << "  wfItr->second = " << wfItr->second << endl;
        RooWorkspace* w = GetWorkspaceFromFile( wfItr->first.Data(), wfItr->second );
        if ( w==0 ) {
            CombineWorkSpacesLogger << kFATAL << "Cannot open workspace <" << wfItr->second << "> in file <" << wfItr->second << ">" << GEndl;
        }

        CombineWorkSpacesLogger << kINFO << "Now collecting <" << wfItr->first << "> <" << wfItr->second << ">" << GEndl;

        //// Dataset names not properly copied!
        //RooWorkspace* ws = new RooWorkspace( *w );
        //ws->SetName( Form("%s%d",wid.Data(),i) );
        //wsVec.push_back(ws);

        w->SetName( Form("%s%d",wid.Data(),i) );
        wsVec.push_back(w);
    }

    return wsVec;
}


//________________________________________________________________________________________________
// this function categorizes all workspaces found in infile, whose names match the format 
// string, eg. "muSUSY10_3j_20pb_SU_%f_%f_0_3", where %f and %f are mapped onto the parameters "m0:m12"
//
std::map< TString,TString > GetMatchingWorkspaces( const TString& infile, const TString& theformat, const TString& interpretation, const TString& cutStr, const Int_t& fID, TTree* ORTree ) {

    CombineWorkSpacesLogger << kDEBUG   << " GetMatchingWorkspaces() : infile = " << infile << GEndl;
    CombineWorkSpacesLogger << kDEBUG   << " GetMatchingWorkspaces() : theformat = " << theformat << GEndl ;
    CombineWorkSpacesLogger << kDEBUG   << " GetMatchingWorkspaces() : interpretation=" << interpretation << GEndl;
    CombineWorkSpacesLogger << kDEBUG   << " GetMatchingWorkspaces() : cutStr=" << cutStr << GEndl;
    CombineWorkSpacesLogger << kDEBUG   << " GetMatchingWorkspaces() : fID = " << fID  << GEndl ;//<< " ORTree = " << ORTree->GetName() << endl;
  
    
    std::map< TString,TString > wsidMap;

    TFile* file = TFile::Open(infile.Data(), "READ");
    if (file->IsZombie()) {
        CombineWorkSpacesLogger << kFATAL << "Cannot open file: " << infile << GEndl;
    }

    TString format = theformat;
    Bool_t searchFileName(kFALSE);
    if (format.BeginsWith("filename+")) { 
      format = format.ReplaceAll("filename+","");
      searchFileName = kTRUE;
    }

    TString fullWSName;
    if (searchFileName) {
        TObjArray* iArr = format.Tokenize("+");
        int narg = iArr->GetEntries();
        if (narg==2) {
          fullWSName = ((TObjString*)iArr->At(1))->GetString();
        }
        delete iArr;
    }

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
        //wsidvec[i] = objString->GetString().Data();
        wsidvec.push_back( objString->GetString().Data() );
    }

    file->cd();

    TEasyFormula formula( cutStr.Data() );

    TList* list = file->GetListOfKeys();
    for(int j=0; j<list->GetEntries(); j++) {
        TKey* key = (TKey*)list->At(j);
        // get proper index with name
        // NOTE: wsid always connects to highest key-index found in file!
        if ( keymap.find(key->GetName())==keymap.end() ) { keymap[key->GetName()] = key->GetCycle(); }
        else if ( key->GetCycle()>keymap[key->GetName()] ) { keymap[key->GetName()] = key->GetCycle(); }
        wsname = Form("%s;%d",key->GetName(),keymap[key->GetName()]) ;
	    wsnameSearch = wsname;

        if (searchFileName && !fullWSName.IsNull()) { // E.g. WS is called combined 
          if (fullWSName != TString(key->GetName())) continue;
        }

	
        // Turn off, this is slow!
        // confirm this is a workspace
        TObject* obj = file->Get( wsname.Data() );
        if (obj==0) continue; 
        if ( obj->ClassName()!=TString("RooWorkspace") ) continue;


	if (searchFileName) {
	  wsnameSearch = infile + "_" + wsnameSearch;
	}

        // accept upto 10 args in ws name
        int narg2 = sscanf( wsnameSearch.Data(), format.Data(), &wsarg[0],&wsarg[1],&wsarg[2],&wsarg[3],&wsarg[4],&wsarg[5],&wsarg[6],&wsarg[7],&wsarg[8],&wsarg[9] ); 
        if ( !(narg1==narg2 && narg1==narg3 && narg2>0) ) { continue; }

        wsarg.resize(narg2);
        wsid.Clear();  // form unique ws id
        for (int i=0; i<narg2; ++i) { 
            objString = (TObjString*)iArr->At(i);
            wsid  += Form("%s_%.0f_", objString->GetString().Data(), wsarg[i]); 
	    //            wsid  += Form("%s=%f_", objString->GetString().Data(), wsarg[i]); 
            formula.SetValue(objString->GetString(),wsarg[i]);
        }        
        //wsid += Form( "%d_",keymap[key->GetName()] );
        if (!formula.GetBoolValue()) continue;

        if ((ORTree!=0) && fID>=0) { // logical orring
            float searchVal(-1);
            bool found = Util::findValueFromTree(ORTree,"fID",searchVal,wsidvec,wsarg);
            if (!found) 
                continue;
            if ( fID!=static_cast<int>(searchVal) ) 
                continue; 
        }

        // NOTE: wsid always connects to highest key-index found in file!
        wsidMap[wsid] = wsname;    
    }

    CombineWorkSpacesLogger << kINFO << "Found : " << wsidMap.size() << " matching workspaces in file : " << infile << GEndl;

    file->Close();
    delete iArr;

    return wsidMap;
}

//________________________________________________________________________________________________
RooWorkspace* GetWorkspaceFromFile( const TString& infile, const TString& wsname ) {
    TFile* file = TFile::Open(infile.Data(), "READ");
    if (file->IsZombie()) {
        CombineWorkSpacesLogger << kERROR << "Cannot open file: " << infile << GEndl;
        return NULL;
    }
    file->cd();

    TObject* obj = file->Get( wsname.Data() ) ;
    if (obj==0) {
        CombineWorkSpacesLogger << kERROR << "Cannot open workspace <" << wsname << "> in file <" << infile << ">" << GEndl;
        file->Close();
        return NULL;
    }

    if (obj->ClassName()!=TString("RooWorkspace")) {
        CombineWorkSpacesLogger << kERROR << "Cannot open workspace <" << wsname << "> in file <" << infile << ">" << GEndl;
        file->Close();
        return NULL;
    }

    RooWorkspace* w = (RooWorkspace*)( obj );
    if ( w==0 ) {
        CombineWorkSpacesLogger << kERROR << "Cannot open workspace <" << wsname << "> in file <" << infile << ">" << GEndl;
        file->Close();
        return NULL;
    }

    //file->Close();
    return w;
}

//________________________________________________________________________________________________
RooStats::HypoTestInverterResult* GetHypoTestResultFromFile( const TString& infile, const TString& wsname ) {
    TFile* file = TFile::Open(infile.Data(), "READ");
    if (file->IsZombie()) {
        CombineWorkSpacesLogger << kERROR << "Cannot open file: " << infile << GEndl;
        return NULL;
    }
    file->cd();

    TObject* obj = file->Get( wsname.Data() ) ;
    if (obj==0) {
        CombineWorkSpacesLogger << kERROR << "Cannot open HypoTestInverterResult <" << wsname << "> in file <" << infile << ">" << GEndl;
        file->Close();
        return NULL;
    }

    if ( obj->ClassName()!=TString("RooStats::HypoTestInverterResult") ) {
        CombineWorkSpacesLogger << kERROR << "Cannot open HypoTestInverterResult <" << wsname << "> in file <" << infile << ">" << GEndl;
        file->Close();
        return NULL;
    }

    RooStats::HypoTestInverterResult* w = (RooStats::HypoTestInverterResult*)( obj );
    if ( w==0 ) {
        CombineWorkSpacesLogger << kERROR << "Cannot open HypoTestInverterResult <" << wsname << "> in file <" << infile << ">" << GEndl;
        file->Close();
        return NULL;
    }

    RooStats::HypoTestInverterResult* v = (RooStats::HypoTestInverterResult*) w->Clone();

    file->Close(); // this invalidates w
    delete obj;
    w = NULL; obj = NULL;

    return v;
}


//________________________________________________________________________________________________
RooFitResult* GetFitResultFromFile( const TString& infile, const TString& fitname ) {
    TFile* file = TFile::Open(infile.Data(), "READ");
    if (file->IsZombie()) {
        CombineWorkSpacesLogger << kERROR << "Cannot open file: " << infile << GEndl;
        return NULL;
    }
    file->cd();

    TObject* obj = file->Get( fitname.Data() ) ;
    if (obj==0) {
        CombineWorkSpacesLogger << kERROR << "Cannot open RooFitResult <" << fitname << "> in file <" << infile << ">" << GEndl;
        file->Close();
        return NULL;
    }

    if ( obj->ClassName()!=TString("RooFitResult") ) {
        CombineWorkSpacesLogger << kERROR << "Cannot open RooFitResult <" << fitname << "> in file <" << infile << ">" << GEndl;
        file->Close();
        return NULL;
    }

    RooFitResult* w = (RooFitResult*)( obj );
    if ( w==0 ) {
        CombineWorkSpacesLogger << kERROR << "Cannot open RooFitResult <" << fitname << "> in file <" << infile << ">" << GEndl;
        file->Close();
        return NULL;
    }

    RooFitResult* v = (RooFitResult*) w->Clone();

    file->Close(); // this invalidates w
    delete obj;
    w = NULL; obj = NULL;

    return v;
}

//________________________________________________________________________________________________
RooMCStudy* GetMCStudy( const RooWorkspace* w ) {
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
std::map<TString,float> ParseWorkspaceID( const TString& wid ) {
    // workspace id has form "m0=300.00_m12=700_"
    std::map<TString,float> wconf;

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
        wconf[par] = parVal;
        delete jArr;
    }

    delete iArr;

    return wconf;
}



//________________________________________________________________________________________________
// See MatchingCountingExperimentsVec
//
bool 
MatchingCountingExperiments ( const TString& of,  const TString& opref,
			      const TString& if1, const TString& f1, const TString& i1, 
			      const TString& if2, const TString& f2, const TString& i2,
			      const TString& if3, const TString& f3, const TString& i3,
			      const TString& if4, const TString& f4, const TString& i4,
			      const TString& cutStr, const Int_t& combinationMode, TTree* ORTree )
{
  std::vector<TString> infile, format, interpretation;

  infile.push_back(if1);  format.push_back(f1);  interpretation.push_back(i1);
  infile.push_back(if2);  format.push_back(f2);  interpretation.push_back(i2);
  infile.push_back(if3);  format.push_back(f3);  interpretation.push_back(i3);
  infile.push_back(if4);  format.push_back(f4);  interpretation.push_back(i4);

  return MatchingCountingExperimentsVec( of, opref, infile, format, interpretation, cutStr, combinationMode, ORTree ) ; 
}


//________________________________________________________________________________________________
// See MatchingCountingExperimentsVec
//
bool
MatchingCountingExperiments ( const TString& of,  const TString& opref,
			      const TString& if1, const TString& f1, const TString& i1,
			      const TString& if2, const TString& f2, const TString& i2,
			      const TString& if3, const TString& f3, const TString& i3,
			      const TString& cutStr, const Int_t& combinationMode, TTree* ORTree )
{
  std::vector<TString> infile, format, interpretation;

  infile.push_back(if1);  format.push_back(f1);  interpretation.push_back(i1);
  infile.push_back(if2);  format.push_back(f2);  interpretation.push_back(i2);
  infile.push_back(if3);  format.push_back(f3);  interpretation.push_back(i3);

  return MatchingCountingExperimentsVec( of, opref, infile, format, interpretation, cutStr, combinationMode, ORTree ) ;
}


//________________________________________________________________________________________________
// See MatchingCountingExperimentsVec
//
bool 
MatchingCountingExperiments ( const TString& of,     const TString& opref,
			      const TString& if1,    const TString& f1,    const TString& i1,
			      const TString& if2,    const TString& f2,    const TString& i2,  
			      const TString& cutStr, const Int_t& combinationMode, TTree* ORTree )
{
  std::vector<TString> infile, format, interpretation;
  infile.push_back(if1);  format.push_back(f1);  interpretation.push_back(i1);
  infile.push_back(if2);  format.push_back(f2);  interpretation.push_back(i2);

  return MatchingCountingExperimentsVec( of, opref, infile, format, interpretation, cutStr, combinationMode, ORTree ) ;
}


//________________________________________________________________________________________________
// Select workspaces from single input file and store them in outputfile
//
bool 
MatchingCountingExperiments( const TString& of,  const TString& opref, const TString& if1, const TString& f1, const TString& i1, const TString& cutStr )
{
  std::vector<TString> infile, format, interpretation;
  infile.push_back(if1);  format.push_back(f1);  interpretation.push_back(i1);
  return MatchingCountingExperimentsVec( of, opref, infile, format, interpretation, cutStr ) ;
}


bool
MatchingCountingExperiments( const TString& outfile,  const TString& outws_prefix, 
                             const std::vector<TString>& infile1, const TString& f1, 
                             const std::vector<TString>& infile2, const TString& f2, 
                             const TString& interp, const TString& cutStr, const TString& combineVars )
{
  std::vector<TString> format, interpretation, infile(infile1); 

  for (unsigned int i=0; i<infile2.size(); ++i) { infile.push_back(infile2[i]); }
  interpretation.resize(infile.size(),interp);

  format.resize(infile.size(),f1);
  for (unsigned int i=0; i<infile2.size(); ++i) { format[infile1.size()+i] = f2; }

  return MatchingCountingExperimentsVec( outfile, outws_prefix, infile, format, interpretation, cutStr, 0, 0, combineVars );
}


bool
MatchingCountingExperiments( const TString& of,  const TString& opref, 
                             const std::vector<TString>& infile1, const TString& f1, 
                             const std::vector<TString>& infile2, const TString& f2,
                             const std::vector<TString>& infile3, const TString& f3,
                             const TString& interp, const TString& cutStr, const TString& combineVars )
{
  std::vector<TString> format, interpretation, infile(infile1);

  for (unsigned int i=0; i<infile2.size(); ++i) { infile.push_back(infile2[i]); }
  for (unsigned int i=0; i<infile3.size(); ++i) { infile.push_back(infile3[i]); }
  interpretation.resize(infile.size(),interp);
  
  format.resize(infile.size(),f1);
  for (unsigned int i=0; i<infile2.size(); ++i) { 
    format[infile1.size()+i] = f2; 
  }
  for (unsigned int i=0; i<infile2.size()+infile3.size(); ++i) { 
    format[infile1.size()+i] = f3; 
  }

  return MatchingCountingExperimentsVec( of, opref, infile, format, interpretation, cutStr, 0, 0, combineVars );
}


//________________________________________________________________________________________________
// This function searches for matching workspaces in the list of inputfiles, combines them,
// and stores them in a new output file
//
bool 
MatchingCountingExperimentsVec ( const TString& outfile, const TString& outws_prefix,
				 const std::vector<TString>& infile, const std::vector<TString>& format, const std::vector<TString>& interpretation, 
				 const TString& cutStr, const Int_t& combinationMode, TTree* ORTree, const TString& combineVars )
{
  if (infile.empty() || format.empty() || interpretation.empty() ) return false;
  if ( (infile.size()!=format.size()) || (infile.size()!=interpretation.size()) ) return false;

  // classify all workspaces in input files
  std::map< TString, std::map<TString,TString> > wsnameMap, wfwMap;
  for (unsigned int i=0; i<infile.size(); ++i) {
    wsnameMap[ infile[i] ] = GetMatchingWorkspaces( infile[i], format[i], interpretation[i], cutStr, i, ORTree );
    //if ( wsnameMap[ infile[i] ].empty() ) return false; // no matching workspaces 
  }

  // match to-be-combined workspaces 
  std::map< TString, std::map<TString,TString> >::iterator nItr=wsnameMap.begin(), nEnd=wsnameMap.end();
  std::map< TString, TString >::iterator widItr, widEnd;

  for ( ; nItr!=nEnd; ++nItr ) {
    widItr=nItr->second.begin();
    widEnd=nItr->second.end();

    for (; widItr!=widEnd; ++widItr) {
      TString wid = widItr->first;
      if ( wfwMap.find(wid)==wfwMap.end() ) { wfwMap[wid] = std::map<TString,TString>(); }
      // collect matching workspaces
      std::map<TString,TString>& fwnameMap = wfwMap[wid];
      fwnameMap[nItr->first] = widItr->second;
    }
  }

  // do ws combination
  nItr=wfwMap.begin();
  for (int idx=0; nItr!=wfwMap.end(); ++nItr, ++idx ) {

    // get wid and file/ws map
    TString wid = nItr->first;
    std::map<TString,TString>& fwnameMap = nItr->second;

    // get workspace pointers
    std::vector<RooWorkspace*> wsVec = CollectWorkspaces( fwnameMap, wid );

    // combine workspaces
    TString combinedName = outws_prefix + "_" + wid + Form("nws%d",static_cast<int>(wsVec.size()));
    RooWorkspace* combined = ConstructCombinedModel( wsVec, combineVars ); //CombineWorkspaces( wsVec, combinedName, combinationMode );
    combined->SetName( combinedName.Data() );

    // store
    if (combined!=0) { 
      TString outfilename = outfile;
      outfilename = outfilename.ReplaceAll(".root","");

      bool recreate = (idx!=0?kFALSE:kTRUE) ;

      if (outfile.EndsWith("+wsid")) {
	    outfilename = outfilename.ReplaceAll("+wsid","_"+wid);
	    recreate = kTRUE; // create unique output file
      }

      TString outprefix = outws_prefix;
      if (!outprefix.IsNull() && !outprefix.BeginsWith("_")) { outprefix = "_"+outws_prefix; }
      outfilename += ".root"; 

      combined->writeToFile(outfilename.Data(), recreate ); // do not recreate file, but update instead
        
      CombineWorkSpacesLogger << kINFO << " Written combination workspace to file: " << outfilename << GEndl;

    }

    // clear 
    if (combined!=0) { delete combined; combined=0; }
    clearVec(wsVec);
  }

  return true;
}



RooWorkspace* 
ConstructCombinedModel(RooWorkspace* ws1, const TString& correlateVarsStr) 
{
  std::vector<RooWorkspace*> wsvec;
  wsvec.push_back(ws1);
  return ConstructCombinedModel(wsvec,correlateVarsStr);
}


RooWorkspace* 
ConstructCombinedModel(RooWorkspace* ws1, RooWorkspace* ws2, const TString& correlateVarsStr) 
{
  std::vector<RooWorkspace*> wsvec;
  wsvec.push_back(ws1);
  wsvec.push_back(ws2);
  return ConstructCombinedModel(wsvec,correlateVarsStr);
}


RooWorkspace* 
ConstructCombinedModel(std::vector<RooWorkspace*> chs, const TString& correlateVarsStr) 
{  
  //
  /// These things were used for debugging. Maybe useful in the future
  //

  std::map<std::string, RooAbsPdf*> pdfMap;
  std::vector<RooAbsPdf*> models;
  std::vector<std::string> ch_names;
  stringstream ss;
  
  RooArgList obsList;
  RooArgSet  globalObs;
  RooArgSet  poiSet;

  RooWorkspace* combined = new RooWorkspace("combined");
  RooWorkspace* tempws   = new RooWorkspace("tempws");
  TString exceptionList = "Lumi,nominalLumi,channelCat,weightVar";

  if (!correlateVarsStr.IsNull()) { exceptionList += "," + correlateVarsStr; }

  /////////////////////////////////////////////////////////////////////////////////////////////////////

  cout << "\n\n------------------\n Administration\n" << endl;

  for(unsigned int i = 0; i< chs.size(); ++i) {
    RooWorkspace * ch=chs[i];
    TString suffix = Form("a%d",i);

    //ch->Print();

    ModelConfig* config = (ModelConfig *) chs[i]->obj("ModelConfig");
    RooAbsPdf* pdf = config->GetPdf();

    poiSet.add( *config->GetParametersOfInterest() );
    globalObs.add(*ch->set("globalObservables")); // note: this can give duplicates. fine.

    TString className = pdf->ClassName();

    if (className == "RooProdPdf") {
      TString channel_name = pdf->GetName();
      channel_name = channel_name.ReplaceAll("model_","");

      ch_names.push_back(channel_name.Data());
      if (ss.str().empty()) ss << channel_name ;
      else ss << ',' << channel_name ;

    } else if (className == "RooSimultaneous") {
      RooCategory* cCat = (RooCategory*)chs[i]->obj("channelCat");
      for(int j=0; j<cCat->numBins(0); ++j) {
	cCat->setIndex(j);
	TString channel_name = cCat->getLabel();

	ch_names.push_back(channel_name.Data());
	if (ss.str().empty()) ss << channel_name.Data() ;
	else ss << ',' << channel_name.Data() ;
      }      
    }
  }


  // don't rename global observables
  RooAbsArg* var(0);
  TString globObsStr;
  TIterator* varItr = globalObs.createIterator() ;
  for (Int_t i=0; (var = (RooAbsArg*)varItr->Next()); ++i) {
    if (i!=0) { globObsStr += ","; }
    TString varname = var->GetName();
    globObsStr += varname ;
  }
  delete varItr;

  //exceptionList += "," + globObsStr;

  TString poiStr;
  varItr = globalObs.createIterator() ;
  for (Int_t i=0; (var = (RooAbsArg*)varItr->Next()); ++i) {
    if (i!=0) { poiStr += ","; }
    TString varname = var->GetName();
    poiStr += varname ;
  }
  delete varItr;

  exceptionList += "," + poiStr;


  cout << "\n\n------------------\n Creation of obsList ...\n" << endl;

  RooArgSet oSet;

  for(unsigned int i = 0; i< chs.size(); ++i) {
    TString suffix = Form("a%d",i);
    RooDataSet* myData = (RooDataSet*) chs[i]->data("asimovData");
    TString datasetName = Form("%s_%s",suffix.Data(),myData->GetName());

    TString vIn, vOut;
    RooAbsArg* var ; 
    RooArgSet const * args = myData->get();
    TIterator* varItr = args->createIterator() ;
    for (Int_t j=0; (var = (RooAbsArg*)varItr->Next()); ++j) {
      if (j!=0) { vIn += ","; vOut += ","; }
      TString vName = var->GetName();
      if (vName=="weightVar" || vName=="channelCat") continue;
      vIn  += var->GetName(); 
      vOut += ( !suffix.IsNull() ? Form("%s_%s",var->GetName(),suffix.Data()) : var->GetName() ) ;
    }
    delete varItr;

    tempws->import( *myData, Rename(datasetName.Data()), RenameVariable(vIn,vOut) );
    myData = (RooDataSet*) tempws->data( datasetName.Data() );

    // AK: for some reason remove() does not remove the channelCat,weightVar from the obsSet
    // Solution: starting from an empty argset, we only add the variables
    //     RooArgSet obsSet = *myData->get(0) ;
    //     if ( chs[i]->obj("weightVar")!=NULL )  { obsSet.remove( *((RooAbsArg*)chs[i]->obj("weightVar")) ); cout << " removing weightVar " << endl; }
    //     if ( chs[i]->obj("channelCat")!=NULL ) { obsSet.remove( *((RooAbsArg*)chs[i]->obj("channelCat")) ); cout << " removing channelCat " << endl;}

    // starting from an empty argset, we only add the variables
    RooArgSet obsSet;
    TIterator* varItr2 = args->createIterator() ;
    for (Int_t j=0; (var = (RooAbsArg*)varItr2->Next()); ++j) {
      TString vName = var->GetName();
      if (vName=="weightVar" || vName=="channelCat") continue;
      obsSet.add( *((RooAbsArg*)chs[i]->obj(vName)) );
    }
    delete varItr2;

    oSet.add(obsSet); // ignore duplicates    
  }
  
  obsList.add(oSet);
  
  cout <<"full list of pois:" << endl;
  poiSet.Print();
  cout <<"full list of observables:"<<endl;
  obsList.Print();
  cout <<"full list of channels:"<<endl;
  cout << ss.str() << endl;


  ///////////////////////////////////////////////////////////////////////////////////////////////////////////


  cout << "\n\n------------------\n Entering workspace combination\n" << endl;

  for(unsigned int i = 0; i< chs.size(); ++i) {
    TString suffix = Form("a%d",i);

    ModelConfig* config = (ModelConfig *) chs[i]->obj("ModelConfig");
    RooArgSet obsSet = *config->GetObservables();
    RooAbsPdf* pdf = config->GetPdf();

    TString className = pdf->ClassName();

    if (className == "RooProdPdf") {
      TString pdfName = suffix + "_" + pdf->GetName();
      TString channel_name = pdf->GetName();
      channel_name = channel_name.ReplaceAll("model_","");

      pdf->SetName(pdfName.Data());
      tempws->import( *pdf, RenameAllNodes(suffix.Data()), RenameAllVariablesExcept(suffix.Data(),exceptionList.Data()) );
      pdf = tempws->pdf(pdfName.Data());

      models.push_back(pdf);
      pdfMap[channel_name.Data()]=pdf;

    } else if (className == "RooSimultaneous") {
      if ( chs[i]->obj("weightVar")!=NULL )  { obsSet.remove( *((RooAbsArg*)chs[i]->obj("weightVar")) ); }
      if ( chs[i]->obj("channelCat")!=NULL ) { obsSet.remove( *((RooAbsArg*)chs[i]->obj("channelCat")) ); }

      RooCategory* cCat = (RooCategory*)chs[i]->obj("channelCat");
      for(int j=0; j<cCat->numBins(0); ++j) {
	cCat->setIndex(j);
	TString channel_name = cCat->getLabel();

	RooAbsPdf* model = ((RooSimultaneous*)pdf)->getPdf(channel_name.Data());
	TString pdfName = TString(model->GetName()) + "_" + suffix;

	tempws->import( *model, RenameAllNodes(suffix.Data()), RenameAllVariablesExcept(suffix.Data(),exceptionList.Data()) );
	model = tempws->pdf(pdfName.Data());

	models.push_back(model);
	pdfMap[channel_name.Data()]=model;
      }      
    }
  }

  cout << "\n\n------------------\n Done workspace combination\n" << endl;

  combined->factory("weightVar[0,-1e10,1e10]");
  obsList.add( *combined->var("weightVar") );

  RooCategory* channelCat = (RooCategory*) combined->factory(("channelCat["+ss.str()+"]").c_str());
  obsList.add(*channelCat);

  RooSimultaneous *simPdf= new RooSimultaneous("simPdf","",pdfMap, *channelCat);
  cout << "\n\n----------------\n Importing combined model" << endl;
  combined->import(*simPdf,RecycleConflictNodes());

  ///////////////////////////////////////////////////////////////////////////////////////////////////////////

  cout << "\n\n----------------------------------------- Creation of combined datasets ...\n" << endl;

  // Make toy simultaneous dataset
  cout <<"-----------------------------------------"<<endl;
  cout << endl << "create toy data for " << ss.str() << endl;
    
  // now with weighted datasets
  // First Asimov
  RooDataSet * simData=NULL;
  Int_t lastCatIdx=0;
  
  for(unsigned int i = 0; i< chs.size(); ++i) {

    TString suffix = Form("a%d",i);
    TString datasetName = suffix + "_asimovData";
    RooDataSet* myData = (RooDataSet*) tempws->data( datasetName.Data() );

    ModelConfig* config = (ModelConfig *) chs[i]->obj("ModelConfig");
    RooAbsPdf* pdf = config->GetPdf();
    TString className = pdf->ClassName();

    if (className == "RooProdPdf") {
      TString channel_name = pdf->GetName();
      channel_name = channel_name.ReplaceAll("model_","");

      RooDataSet* tempData = new RooDataSet(channel_name.Data(), "", obsList, Index(*channelCat),
					    WeightVar("weightVar"),
					    Import( channel_name.Data(), *myData ) 
					   );
      if (simData) {
	simData->append(*tempData);
	delete tempData;
      } else {
	simData = tempData;
      }
    } else if (className == "RooSimultaneous") {
      RooCategory* cCat = (RooCategory*)chs[i]->obj("channelCat");

      for(int j=0; j<cCat->numBins(0); ++j) {
	cCat->setIndex(j);
	TString channel_name = cCat->getLabel();
	RooAbsPdf* regionPdf = ((RooSimultaneous*)pdf)->getPdf(channel_name.Data());

	RooArgSet* obsSet = regionPdf->getObservables( myData->get(0) );
	TString dataCatLabel = Form("channelCat==channelCat::%s", channel_name.Data() ); 

	RooDataSet* regionData = (RooDataSet*) myData->reduce( *obsSet, dataCatLabel.Data() );

	RooDataSet* tempData = new RooDataSet(channel_name.Data(), "", obsList, Index(*channelCat),
					      WeightVar("weightVar"),
					      Import( channel_name.Data(), *regionData ) 
					      );
	delete regionData;

	if (simData) {
	  simData->append(*tempData);
	  delete tempData;
	} else {
	  simData = tempData;
	}
      }      

    }
  } // and import
  if (simData) combined->import(*simData,Rename("asimovData"));


  // observed dataset
  cout << endl << "merging observed data for workspace " << ss.str() << endl;

  simData=NULL;
 
  for(unsigned int i = 0; i< chs.size(); ++i) {

    TString suffix = Form("a%d",i);
    RooDataSet* myData = (RooDataSet*) chs[i]->data("obsData");
    TString datasetName = Form("%s_%s",suffix.Data(),myData->GetName());

    TString vIn, vOut;
    RooAbsArg* var ; 
    RooArgSet const * args = myData->get();
    TIterator* varItr = args->createIterator() ;
    for (Int_t j=0; (var = (RooAbsArg*)varItr->Next()); ++j) {
      if (j!=0) { vIn += ","; vOut += ","; }
      TString vName = var->GetName();
      if (vName=="weightVar" || vName=="channelCat") continue;
      vIn  += var->GetName(); 
      vOut += ( !suffix.IsNull() ? Form("%s_%s",var->GetName(),suffix.Data()) : var->GetName() ) ;
    }
    delete varItr;

    tempws->import( *myData, Rename(datasetName.Data()), RenameVariable(vIn,vOut) );
    myData = (RooDataSet*) tempws->data( datasetName.Data() );

    ModelConfig* config = (ModelConfig *) chs[i]->obj("ModelConfig");
    RooAbsPdf* pdf = config->GetPdf();
    TString className = pdf->ClassName();

    if (className == "RooProdPdf") {
      TString channel_name = pdf->GetName();
      channel_name = channel_name.ReplaceAll("model_","");

      RooDataSet* tempData = new RooDataSet(channel_name.Data(), "", obsList, Index(*channelCat),
					    WeightVar("weightVar"),
					    Import( channel_name.Data(), *myData ) 
					   );
      if (simData) {
	simData->append(*tempData);
	delete tempData;
      } else {
	simData = tempData;
      }
    } else if (className == "RooSimultaneous") {
      RooCategory* cCat = (RooCategory*)chs[i]->obj("channelCat");
     
      for(int j=0; j<cCat->numBins(0); ++j) {
	cCat->setIndex(j);
	channelCat->setIndex(lastCatIdx+j);
	TString channel_name = cCat->getLabel();
	RooAbsPdf* regionPdf = ((RooSimultaneous*)pdf)->getPdf(channel_name.Data());

	RooArgSet* obsSet = regionPdf->getObservables( myData->get(0) );
	TString dataCatLabel = Form("channelCat==channelCat::%s", channel_name.Data() ); 

	RooDataSet* regionData = (RooDataSet*) myData->reduce( *obsSet, dataCatLabel.Data() );

	RooDataSet* tempData = new RooDataSet(Form("obsData_%s",channel_name.Data()), "", obsList, Index(*channelCat),
					      WeightVar("weightVar"),
					      Import( channel_name.Data(), *regionData ) 
					      );
	delete regionData;
	
	if(simData) {
	  simData->append(*tempData);
	  delete tempData;
	} else { 
	  simData = tempData;
	}
      }      
      lastCatIdx += cCat->numBins(0);
    }  
  } 
  // and import
  if (simData) combined->import(*simData,Rename("obsData"));



  ModelConfig *combined_config = new ModelConfig("ModelConfig", combined);
  combined_config->SetWorkspace(*combined);
  //    combined_config->SetNuisanceParameters(*constrainedParams);


  combined->import(globalObs);
  combined->defineSet("globalObservables",globalObs);
  combined_config->SetGlobalObservables(*combined->set("globalObservables"));  

  //////////////////////////////////////////////////////////////////////////////////////

  // conclusion
  combined->defineSet("observables",obsList);
  combined_config->SetObservables(*combined->set("observables"));
    
  combined->Print();
  
  combined_config->SetPdf(*simPdf);
  combined_config->SetParametersOfInterest(poiSet);

  //    combined_config->GuessObsAndNuisance(*simData);
  //    customized->graphVizTree(("results/"+fResultsPrefixStr.str()+"_simul.dot").c_str());
  combined->import(*combined_config,combined_config->GetName());
  combined->importClassCode();
  //    combined->writeToFile("results/model_combined.root");
  
  return combined;
}



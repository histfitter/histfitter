
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
#include "TFile.h"
#include "TKey.h"
#include "TObject.h"
#include "TObjArray.h"
#include "TObjString.h"
#include "TEasyFormula.h"
#include "RooMCStudy.h"
#include "RooFitResult.h"

using namespace RooFit ;
using namespace RooStats ;

// -------------------------------
// read the header for information
// -------------------------------


//________________________________________________________________________________________________
void 
Combination::clearVec( std::vector<RooWorkspace*>& wsVec )
{
  std::vector<RooWorkspace*>::iterator wItr=wsVec.begin(), wEnd=wsVec.end();
  for (; wItr!=wEnd; ++wItr) { if ((*wItr)!=0) { delete (*wItr); } }
  wsVec.clear();
}

  
//________________________________________________________________________________________________
// This function retrieves workspaces from files as specified in fwnameMap, where
// the key is the filename, and map[key] gives the identifyer of the workspace.
// wid is the new names of the retrieved workspaces
//
std::vector<RooWorkspace*>
Combination::CollectWorkspaces( const std::map< TString,TString >& fwnameMap, const TString& wid ) 
{
  std::vector<RooWorkspace*> wsVec;
  std::map< TString,TString >::const_iterator wfItr=fwnameMap.begin(), wfEnd=fwnameMap.end();

  for (int i=0; wfItr!=wfEnd; ++wfItr, ++i) {

    RooWorkspace* w = Combination::GetWorkspaceFromFile( wfItr->first.Data(), wfItr->second );
    if ( w==0 ) {
      cout << "ERROR : Cannot open workspace <" << wfItr->second << "> in file <" << wfItr->second << ">" << endl;
      exit(-1);
    }

    cout << "INFO: Now collecting <" << wfItr->first << "> <" << wfItr->second << ">" << endl;

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
std::map< TString,TString > 
Combination::GetMatchingWorkspaces( const TString& infile, const TString& format, const TString& interpretation, const TString& cutStr, const Int_t& fID, TTree* ORTree )
{
  std::map< TString,TString > wsidMap;

  TFile* file = TFile::Open(infile.Data(), "READ");
  if (file->IsZombie()) {
    cout << "ERROR : Cannot open file: " << infile << endl;
    exit(-1);
  }

  TObjString* objString = NULL;
  std::map<TString,int> keymap;
  int narg1 = format.CountChar('%');
  TString wsid, wsname, wssel;
  std::vector<float> wsarg(10);
  
  TObjArray* iArr = interpretation.Tokenize(":");
  int narg3 = iArr->GetEntries();
  if (narg1!=narg3) {
    cout << "ERROR : No valid interpretation string <" << interpretation << "> with format <" << format << ">, for file <" << infile << ">" << endl;
    delete iArr;
    exit(-1);
  }

  std::vector<std::string> wsidvec; //[narg3];
  for (int i=0; i<narg3; ++i) {
    objString = (TObjString*)iArr->At(i);
    //wsidvec[i] = objString->GetString().Data();
    wsidvec.push_back( objString->GetString().Data() );
  }

  file->cd();

  Combination::TEasyFormula formula( cutStr.Data() );

  TList* list = file->GetListOfKeys();
  for(int j=0; j<list->GetEntries(); j++) {
    TKey* key = (TKey*)list->At(j);
    // get proper index with name
    // NOTE: wsid always connects to highest key-index found in file!
    if ( keymap.find(key->GetName())==keymap.end() ) { keymap[key->GetName()] = key->GetCycle(); }
    else if ( key->GetCycle()>keymap[key->GetName()] ) { keymap[key->GetName()] = key->GetCycle(); }
    wsname = Form("%s;%d",key->GetName(),keymap[key->GetName()]) ;

    //// Turn off, this is slow!
    //// confirm this is a workspace
    //TObject* obj = file->Get( wsname.Data() );
    //if (obj==0) continue; 
    //if ( obj->ClassName() != TString("RooWorkspace") ) continue;

    // accept upto 10 args in ws name
    int narg2 = sscanf( wsname.Data(), format.Data(), &wsarg[0],&wsarg[1],&wsarg[2],&wsarg[3],&wsarg[4],&wsarg[5],&wsarg[6],&wsarg[7],&wsarg[8],&wsarg[9] ); 
    if ( !(narg1==narg2 && narg1==narg3 && narg2>0) ) { continue; }

    wsarg.resize(narg2);
    wsid.Clear();  // form unique ws id
    for (int i=0; i<narg2; ++i) { 
      objString = (TObjString*)iArr->At(i);
      wsid  += Form("%s=%f_", objString->GetString().Data(), wsarg[i]); 
      formula.SetValue(objString->GetString(),wsarg[i]);
    }        
    //wsid += Form( "%d_",keymap[key->GetName()] );
    if (!formula.GetBoolValue()) continue;

    if ((ORTree!=0) && fID>=0) { // logical orring
      float searchVal(-1);
      bool found = Util::findValueFromTree(ORTree,"fID",searchVal,wsidvec,wsarg);
      if (!found) continue;
      if ( fID!=static_cast<int>(searchVal) ) continue; 
    }

    // NOTE: wsid always connects to highest key-index found in file!
    wsidMap[wsid] = wsname;
  }
  
  cout << "INFO: Found : " << wsidMap.size() << " matching workspaces in file : " << infile << endl;

  file->Close();
  delete iArr;

  return wsidMap;
}



//________________________________________________________________________________________________
RooWorkspace*
Combination::GetWorkspaceFromFile( const TString& infile, const TString& wsname )
{
  TFile* file = TFile::Open(infile.Data(), "READ");
  if (file->IsZombie()) {
    cout << "ERROR : Cannot open file: " << infile << endl;
    return NULL;
  }
  file->cd();

  TObject* obj = file->Get( wsname.Data() ) ;
  if (obj==0) {
    cout << "ERROR : Cannot open workspace <" << wsname << "> in file <" << infile << ">" << endl;
    file->Close();
    return NULL;
  }

  if (obj->ClassName()!=TString("RooWorkspace")) {
    cout << "ERROR : Cannot open workspace <" << wsname << "> in file <" << infile << ">" << endl;
    file->Close();
    return NULL;
  }

  RooWorkspace* w = (RooWorkspace*)( obj );
  if ( w==0 ) {
    cout << "ERROR : Cannot open workspace <" << wsname << "> in file <" << infile << ">" << endl;
    file->Close();
    return NULL;
  }

  file->Close();
  return w;
}



//________________________________________________________________________________________________
RooStats::HypoTestInverterResult*
Combination::GetHypoTestResultFromFile( const TString& infile, const TString& wsname )
{
  TFile* file = TFile::Open(infile.Data(), "READ");
  if (file->IsZombie()) {
    cout << "ERROR : Cannot open file: " << infile << endl;
    return NULL;
  }
  file->cd();

  TObject* obj = file->Get( wsname.Data() ) ;
  if (obj==0) {
    cout << "ERROR : Cannot open HypoTestInverterResult <" << wsname << "> in file <" << infile << ">" << endl;
    file->Close();
    return NULL;
  }

  if ( obj->ClassName()!=TString("RooStats::HypoTestInverterResult") ) {
    cout << "ERROR : Cannot open HypoTestInverterResult <" << wsname << "> in file <" << infile << ">" << endl;
    file->Close();
    return NULL;
  }

  RooStats::HypoTestInverterResult* w = (RooStats::HypoTestInverterResult*)( obj );
  if ( w==0 ) {
    cout << "ERROR : Cannot open HypoTestInverterResult <" << wsname << "> in file <" << infile << ">" << endl;
    file->Close();
    return NULL;
  }

  RooStats::HypoTestInverterResult* v = (RooStats::HypoTestInverterResult*) w->Clone();

  file->Close(); // this invalidates w

  return v;
}


//________________________________________________________________________________________________
RooFitResult*
Combination::GetFitResultFromFile( const TString& infile, const TString& fitname )
{

  TFile* file = TFile::Open(infile.Data(), "READ");
  if (file->IsZombie()) {
    cout << "ERROR : Cannot open file: " << infile << endl;
    return NULL;
  }
  file->cd();

  TObject* obj = file->Get( fitname.Data() ) ;
  if (obj==0) {
    cout << "ERROR : Cannot open RooFitResult<" << fitname << "> in file <" << infile << ">" << endl;
    file->Close();
    
    return NULL;
  }

  if ( obj->ClassName()!=TString("RooFitResult") ) {
    cout << "ERROR : Cannot open RooFitResult <" << fitname << "> in file <" << infile << ">" << endl;
    file->Close();
    return NULL;
  }

  RooFitResult* w = (RooFitResult*)( obj );
  if ( w==0 ) {
    cout << "ERROR : Cannot open RooFitResult <" << fitname << "> in file <" << infile << ">" << endl;
    file->Close();
    return NULL;
  }

  RooFitResult* v = (RooFitResult*) w->Clone();

  file->Close(); // this invalidates w

  return v;
}


//________________________________________________________________________________________________
RooMCStudy* 
Combination::GetMCStudy( const RooWorkspace* w )
{
  if (w==0) {
    std::cerr << "Input workspace is null. Return." << std::endl;
    return 0;
  }

  // suffix for workspace
  if( !w->obj("text_suffix") ) {
     std::cerr << "No suffix found, this workspace can not be automatically combined using this function.\n"
               << "If possible recreate your single workspaces with newer code."
               << std::endl;
     return 0; //theresult;
  }
  TString suffix = w->obj("text_suffix")->GetTitle();
  if (!suffix.IsNull()) { suffix = "_" + suffix; }

  RooAbsData* data_set = w->data("data_set"+suffix) ;
  RooAbsPdf* full_model_thispdf = w->pdf("full_model"+suffix);

  if((!data_set)||(!full_model_thispdf)){
     std::cerr << "Error: data set or pdf not found" <<std::endl;
     std::cerr << "     :   pdfname    =" <<"full_model"+suffix<<std::endl;
     std::cerr << "     :   datasetname=" <<"data_set"+suffix<<std::endl;
     return 0;
  }

  // get observables
  const RooArgSet* obsset = data_set->get();

  // caller owns mcstudy
  return ( new RooMCStudy(*full_model_thispdf,*obsset) ) ;
}


//________________________________________________________________________________________________
std::map<TString,float> 
Combination::ParseWorkspaceID( const TString& wid )
{
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



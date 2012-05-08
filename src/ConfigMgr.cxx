////////////////////////////////////////////////////////////////////////
// Creation: December 2011, David Cote (CERN)                         //
// Simple C++ mirror of the python configManager.                     //
// Note that ConfigMgr is a singleton (like its python counter-part). //
// Currently assumes uniform fit configuration for all TopLevelXMLs . //
////////////////////////////////////////////////////////////////////////

//SusyFitter includes
#include "ConfigMgr.h"
#include "Utils.h"
#include "StatTools.h"

//Root/RooFit/RooStats includes
#include "TFile.h"
#include "TTree.h"
#include "RooMCStudy.h"
#include "RooFitResult.h"
#include "RooStats/HypoTestInverterResult.h"
#include "RooRandom.h"


using namespace std;

ConfigMgr::ConfigMgr()
{
  m_nToys = 1000;
  m_calcType = 0;
  m_testStatType = 3;
  m_status = "Unkwn";
  m_saveTree=false;
  m_doHypoTest=false;
  m_useCLs=true;
  m_doUL=true;
  m_seed=0;
  m_nPoints=10;
  m_muValGen=0.0;
}

FitConfig* ConfigMgr::addFitConfig(const TString& name){
  FitConfig* fc = new FitConfig(name);
  m_fitConfigs.push_back(fc);
  return m_fitConfigs.at(m_fitConfigs.size()-1);
}

FitConfig* ConfigMgr::getFitConfig(const TString& name){
  for(unsigned int i=0; i<m_fitConfigs.size(); i++) {
    if(m_fitConfigs.at(i)->m_Name==name){
      return m_fitConfigs.at(i);
    }
  }
  cout<<"WARNING unkown FitConfig object named '"<<name<<"'"<<endl;
  return 0;
}


Bool_t ConfigMgr::checkConsistency(){
  if(m_fitConfigs.size()==0){
    m_status = "empty";
    return false;
  }
  //to-do: add check for duplicated fit regions
  m_status = "OK";
  return true;
}





void ConfigMgr::initialize(){  
  if(m_saveTree || m_doHypoTest){
    if(m_outputFileName.Length()>0){
      TFile fileOut(m_outputFileName,"RECREATE");
      fileOut.Close();
    }
    else{
      cout<<"ERROR in ConfigMgr: no outputFileName specified."<<endl;
    }
  }
  return;
}


void 
ConfigMgr::fitAll()
{
  for(unsigned int i=0; i<m_fitConfigs.size(); i++) {
    fit ( m_fitConfigs.at(i) );
  }

  return;
}

void 
ConfigMgr::fit(int i)
{
  return fit(m_fitConfigs.at(i));
}

void 
ConfigMgr::fit(FitConfig* fc)
{
  TString outfileName = m_outputFileName;
  outfileName.ReplaceAll(".root","_fitresult.root");
  TFile* outfile = TFile::Open(outfileName,"UPDATE");
  if(!outfile){ cerr<<"ERROR TFile <" << outfileName << "> could not be opened"<<endl; return; }

  TFile* inFile = TFile::Open(fc->m_inputWorkspaceFileName);
  if(!inFile) { cout << "ERROR TFile could not be opened" << endl; return; }
  
  RooWorkspace* w = (RooWorkspace*)inFile->Get("combined");
  if(w==NULL) { cout << "workspace 'combined' does not exist in file" << endl; return; }
  
  RooFitResult* fitresult = Util::doFreeFit( w );
  
  if(fitresult) {	
    outfile->cd();
    TString hypName="fitTo_"+fc->m_signalSampleName;
    fitresult->SetName(hypName);
    fitresult->Write();
    cout << ">>> Now storing RooFitResult <" << hypName << ">" << endl;
  }
  
  inFile->Close();
  
  outfile->Close();
  
  cout << ">>> Done. Stored fit result in file <" << outfileName << ">" << endl;
  
  return;
}


void 
ConfigMgr::doHypoTestAll(TString outdir)
{
  for(unsigned int i=0; i<m_fitConfigs.size(); i++) {
    doHypoTest( m_fitConfigs.at(i) , outdir);
  }
  return;
}

void 
ConfigMgr::doHypoTest(int i , TString outdir)
{
  return doHypoTest( m_fitConfigs.at(i), outdir );
}

void 
ConfigMgr::doHypoTest(FitConfig* fc, TString outdir)
{
  TString outfileName = m_outputFileName;
  outfileName.ReplaceAll(".root","_hypotest.root");
  outfileName.ReplaceAll("results/",outdir);
  TFile* outfile = TFile::Open(outfileName,"UPDATE");
  if(!outfile){ cerr<<"ERROR TFile <" << outfileName << "> could not be opened"<<endl; return; }

  TFile* inFile = TFile::Open(fc->m_inputWorkspaceFileName);
  if(!inFile){ cout<<"ERROR TFile could not be opened"<<endl; return; }
  
  RooWorkspace* w = (RooWorkspace*)inFile->Get("combined");
  if(w==NULL){ cout<<"workspace 'combined' does not exist in file"<<endl; return; }
  
  cout << "Processing analysis " << fc->m_signalSampleName << endl;
  
  if ((fc->m_signalSampleName).Contains("Bkg") || (fc->m_signalSampleName) == "") {
    cout << "No hypothesis test performed for background fits." << endl;
    inFile->Close();  
    outfile->Close(); 
    return;
  }
  
  //Do first fit and save fit result in order to control fit quality
  
  RooFitResult* fitresult = Util::doFreeFit( w, 0, false, true ); // reset fit paremeters after the fit ...
  
  if(fitresult) {	
    outfile->cd();
    TString hypName="fitTo_"+fc->m_signalSampleName;
    fitresult->SetName(hypName);
    fitresult->Print();
    fitresult->Write();
    cout << ">>> Now storing RooFitResult <" << hypName << ">" << endl;
  }
  
  RooStats::HypoTestInverterResult* hypo = RooStats::DoHypoTestInversion(w,m_nToys,m_calcType,m_testStatType); 
  
  if(hypo){	
    outfile->cd();
    TString hypName="hypo_"+fc->m_signalSampleName;
    hypo->SetName(hypName);
    hypo->Write();
    cout << ">>> Now storing HypoTestInverterResult <" << hypName << ">" << endl;
    delete hypo;
  }

  cout << ">>> Done. Stored HypoTestInverterResult and fit result in file <" << outfileName << ">" << endl;
  
  inFile->Close();  
  outfile->Close();

  return;
}


void 
ConfigMgr::doUpperLimitAll()
{
  for(unsigned int i=0; i<m_fitConfigs.size(); i++) {
    doUpperLimit( m_fitConfigs.at(i) );
  }
  return;
}

void 
ConfigMgr::doUpperLimit(int i)
{
  return doUpperLimit(m_fitConfigs.at(i));
}

void 
ConfigMgr::doUpperLimit(FitConfig* fc)
{
  TString outfileName = m_outputFileName;
  outfileName.ReplaceAll(".root","_upperlimit.root");
  TFile* outfile = TFile::Open(outfileName,"UPDATE");
  if(outfile->IsZombie()) { cerr<<"ERROR TFile <" << outfileName << "> could not be opened"<<endl; return; }

  TFile* inFile = TFile::Open(fc->m_inputWorkspaceFileName);
  if(!inFile){ cout<<"ERROR doUL : TFile could not be opened"<<endl; return; }
  
  RooWorkspace* w = (RooWorkspace*)inFile->Get("combined");
  if(w==NULL){ cout<<"workspace 'combined' does not exist in file"<<endl; return; }
  
  /// here we go ...
  
  /// first asumptotic limit, to get a quick but reliable estimate for the upper limit
  /// dynamic evaluation of ranges
  RooStats::HypoTestInverterResult* hypo = RooStats::DoHypoTestInversion(w,1,2,m_testStatType,m_useCLs,20,0,-1);  
  
  /// then reevaluate with proper settings
  if ( hypo!=0 ) { 
    double eul2 = 1.10 * hypo->GetExpectedUpperLimit(2);
    delete hypo; hypo=0;
    //cout << "INFO grepme : " << m_nToys << " " << m_calcType << " " << m_testStatType << " " << m_useCLs << " " << m_nPoints << endl;
    hypo = RooStats::DoHypoTestInversion(w,m_nToys,m_calcType,m_testStatType,m_useCLs,m_nPoints,0,eul2); 
  }
  
  /// store ul as nice plot ..
  if ( hypo!=0 ) { 
    RooStats::AnalyzeHypoTestInverterResult( hypo,m_calcType,m_testStatType,m_useCLs,m_nPoints, fc->m_signalSampleName.Data(), ".eps") ;
  }
  
  //cout << "h1" << endl;
  
  // save complete hypotestinverterresult to file
  if(hypo!=0){	
    outfile->cd();
    TString hypName="hypo_"+fc->m_signalSampleName;
    hypo->SetName(hypName);
    cout << ">>> Now storing HypoTestInverterResult <" << hypName << ">" << endl;
    hypo->Write();
  }
  
  if (hypo!=0) { delete hypo; }
  
  inFile->Close();
  
  outfile->Close();

  cout << ">>> Done. Stored upper limit in file <" << outfileName << ">" << endl;

  return;
}


void 
ConfigMgr::runToysAll() 
{
  for(unsigned int i=1; i<m_fitConfigs.size(); i++) {
    runToys ( m_fitConfigs.at(i) );
  }
  return;
}

void 
ConfigMgr::runToys(int i)
{
  return runToys(m_fitConfigs.at(i));
}

void 
ConfigMgr::runToys(FitConfig* fc)
{
  TFile* inFile = TFile::Open(fc->m_inputWorkspaceFileName);
  if(!inFile){ cout<<"ERROR TFile could not be opened"<<endl; return; }
  
  RooWorkspace* w = (RooWorkspace*)inFile->Get("combined");
  if(w==NULL){ cout<<"workspace 'combined' does not exist in file"<<endl; return; }
  
  /// here we go ...
  m_seed = RooRandom::randomGenerator()->GetSeed(); // m_seed );
  bool doDataFitFirst = true;
  bool storeToyResults = true;
  TString toyoutfile =  fc->m_inputWorkspaceFileName;
  toyoutfile.ReplaceAll(".root","");  
  toyoutfile =  TString::Format("%s_toyResults_seed=%d_ntoys=%d.root",toyoutfile.Data(),m_seed,m_nToys);  
  
  /// storage performed inside function
  TTree* dummy = RooStats::toyMC_gen_fit( w, m_nToys, m_muValGen, doDataFitFirst, storeToyResults, toyoutfile );
  delete dummy;
  
  return;
}


void ConfigMgr::finalize(){
  return;
}


// Initialization of singleton
ConfigMgr *ConfigMgr::_singleton = NULL;

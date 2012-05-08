#include "Utils.h"
#include "ConfigMgr.h"

#include "TMap.h"
#include "TString.h"
#include "TObjString.h"
#include "TObjArray.h"

#include "RooArgSet.h"
#include "TIterator.h"
#include "RooAbsReal.h"
#include "RooAbsPdf.h"
#include "RooAbsArg.h"
#include "RooFitResult.h"
#include "RooRealVar.h"
#include "SigmaLR.h"
#include "RooWorkspace.h"
#include "RooSimultaneous.h"
#include "RooProdPdf.h"
#include "RooDataSet.h"
#include "RooPlot.h"
#include "RooProduct.h"
#include "RooMCStudy.h"
#include "Roo1DTable.h"
#include "RooCategory.h"
#include "RooRealSumPdf.h"
#include "RooGaussian.h"
#include "RooCurve.h"
#include "RooHist.h"

#include "RooStats/ModelConfig.h"
#include "RooStats/ProfileLikelihoodTestStat.h"
#include "RooStats/ProfileLikelihoodCalculator.h"
#include "RooStats/LikelihoodInterval.h"
#include "RooStats/ToyMCSampler.h"
#include "RooStats/SamplingDistPlot.h"
#include "RooStats/HypoTestInverterResult.h"
#include "RooStats/HypoTestResult.h"

#include "TF1.h"
#include "TH2D.h"
#include "TTree.h"
#include "TBranch.h"
#include "TGraph2D.h"
#include "TGraphAsymmErrors.h"
#include "TPad.h"
#include "TStyle.h"

#include "TVectorD.h"
#include "TFile.h"
#include "TLine.h"
#include "TLatex.h"
#include "TCanvas.h"
#include "TLegend.h"
#include "TLegendEntry.h"

#include <iostream>
#include <fstream>

using namespace std;
using namespace RooFit;
using namespace RooStats;




//_____________________________________________________________________________
double Util::looseToTightVal(const TString& reg, TMap* map){
  double nLMT=((TObjString*)map->GetValue("DATA_DATA_"+reg+"lmt"))->GetString().Atof();
  double nTopTight=((TObjString*)map->GetValue("MC_tt_"+reg))->GetString().Atof();
  double nWTight=((TObjString*)map->GetValue("MC_WZ_"+reg))->GetString().Atof();
  double LtoTeffFake=((TObjString*)map->GetValue("LtoTeffFake_QCD"+reg+"_"+reg+"lmt"))->GetString().Atof();
  double LtoTeffReal_tt=((TObjString*)map->GetValue("LtoTeffReal_tt_"+reg+"lmt"))->GetString().Atof();
  double LtoTeffReal_W=((TObjString*)map->GetValue("LtoTeffReal_WZ_"+reg+"lmt"))->GetString().Atof();
  double fBTagTop=((TObjString*)map->GetValue("btag_sep_tt"))->GetString().Atof();
  double fBTagWZ=((TObjString*)map->GetValue("btag_sep_WZ"))->GetString().Atof();
  
  double nTop=nTopTight * (LtoTeffReal_tt-1.0);
  double nWZ=nWTight * (LtoTeffReal_W-1.0);
  if(reg=="TR"){ 
    nTop=nTop*fBTagTop; 
    nWZ=nWZ*fBTagWZ; 
  }
  else if(reg=="WR"){ 
    nTop=nTop*(1.0-fBTagTop); 
    nWZ=nWZ*(1.0-fBTagWZ); 
  }
  
  double val=(nLMT-nTop-nWZ)/LtoTeffFake;
  //cout<<reg<<" "<<nLMT<<" "<<nTop<<" "<<nWZ<<" "<<LtoTeffFake<<" "<<val<<endl;
  return val;
}

//_____________________________________________________________________________
double Util::looseToTightErr(const TString& reg, TMap* map){
  double nLMT=((TObjString*)map->GetValue("DATA_DATA_"+reg+"lmt"))->GetString().Atof();
  double LtoTeffFake=((TObjString*)map->GetValue("LtoTeffFake_QCD"+reg+"_"+reg+"lmt"))->GetString().Atof();
  double err=sqrt(nLMT)/LtoTeffFake; //incomplete and temporary
  return err;
}

//_____________________________________________________________________________
double Util::getNonQcdVal(const TString& proc, const TString& reg, TMap* map,const TString& opt){
  TString prefix="MC_";
  if(proc=="DATA"){ prefix="DATA_"; }

  double val=((TObjString*)map->GetValue(prefix+proc+opt+"_"+reg))->GetString().Atof();
  
  //exception #1: WTR, overwrite val
  if((reg=="WR" || reg=="TR") && proc!="DATA"){
    double mcVal=val;
    double fBTag=((TObjString*)map->GetValue("btag_sep_"+proc))->GetString().Atof();
    if(reg=="TR"){ val=mcVal*fBTag; }
    else if(reg=="WR"){ val=mcVal*(1.0-fBTag); }
  }
  return val;
}



//_____________________________________________________________________________
void Util::SaveInitialSnapshot(RooWorkspace* w){

  if(w==NULL){
    cout << "Util::SaveInitialSnapshot():   workspace does not exist" << endl;
    return;
  }

  w->SetName("w");
  w->SetTitle("w");
  
  // save snapshot before any fit has been done
  RooSimultaneous* pdf = (RooSimultaneous*) w->pdf("simPdf");
  RooAbsData* data = (RooAbsData*) w->data("obsData");
  RooArgSet* params = (RooArgSet*) pdf->getParameters(*data) ;
  if(!w->loadSnapshot("snapshot_paramsVals_initial"))  w->saveSnapshot("snapshot_paramsVals_initial",*params);
  else cout << endl << " Snapshot 'snapshot_paramsVals_initial' already exists in  workspace, will not overwrite it" << endl;

  // Put workspace in the global directory
  gDirectory->Add(w);

}


//_____________________________________________________________________________
void Util::LoadSnapshotInWorkspace(RooWorkspace* w,TString snapshot){
  
  Bool_t loaded =  w->loadSnapshot(snapshot);
  
  if (loaded){ cout << endl << " LOADED" << endl; return; }
  else cout << endl << endl << " WARNING:   Util.LoadSnapshotInWorkspace() did not find snapshot named "  << snapshot << ", check your workspace file" << endl;
  
  return;  

}


//_____________________________________________________________________________
void Util::WriteWorkspace(RooWorkspace* w, TString outFileName, TString suffix){

  if(w==NULL){ cout << endl << " Workspace not found, not writing workspace to file" << endl << endl; return; }
  
  outFileName.ReplaceAll(".root","_afterFit.root");

  if (suffix != "") {
    TString suff =  "_" + suffix + ".root";
    outFileName.ReplaceAll(".root",suff);
  }

  w->SetName("w");
  w->SetTitle("w");
  
  w->writeToFile(outFileName.Data());
  
  cout << endl << " Util::WriteWorkspace():   have written workspace to file " <<  outFileName << endl;

  return;
}


//_____________________________________________________________________________
RooFitResult* Util::FitPdf( RooWorkspace* w, TString fitRegions, bool lumiConst, RooAbsData* inputData, TString suffix)
{
  //ConfigMgr* mgr = ConfigMgr::getInstance();
  //int nToys = mgr->getNToys();
  //bool doToys = (nToys > 0); //nToys < 0 means to fit real data

  cout << endl << endl << " ------ Starting FitPdf with parameters:    fitRegions = " <<  fitRegions 
       <<  "  inputData = " << inputData << "  suffix = " << suffix  << endl << endl;

  RooMsgService::instance().getStream(1).removeTopic(NumIntegration);

  //RooWorkspace* w = (RooWorkspace*) gDirectory->Get("w");
  if(w==NULL){ cout << endl << " Workspace not found, no fitting performed" << endl << endl; return NULL; }
  RooSimultaneous* pdf = (RooSimultaneous*) w->pdf("simPdf");
  // pdf->Print("t");

  RooAbsData* data = ( inputData!=0 ? inputData : (RooAbsData*)w->data("obsData") ); 
  RooCategory* regionCat = (RooCategory*) w->cat("channelCat");  
  data->table(*((RooAbsCategory*)regionCat))->Print("v");

  RooRealVar* lumi = (RooRealVar*) w->var("Lumi");
  lumi->setConstant(lumiConst); 
  //HACK DC
  //   w->var("alpha_NormQCDTR_nJet_1")->setConstant();

  // Construct an empty simultaneous pdf using category regionCat as index
  RooSimultaneous* simPdfFitRegions = pdf;
  RooDataSet* dataFitRegions = (RooDataSet*) data;
  
  std::vector<TString> fitRegionsVec = GetRegionsVec(fitRegions, regionCat);

  unsigned int numFitRegions = fitRegionsVec.size();
  std::vector<RooDataSet*> dataVec;
  std::vector<RooAbsPdf*> pdfVec;
  
  for(unsigned int iVec=0; iVec<numFitRegions; iVec++){
    TString regionCatLabel = fitRegionsVec[iVec];
    if( regionCat->setLabel(regionCatLabel,kTRUE)){  cout << endl << " Label '" << regionCatLabel << "' is not a state of channelCat (see Table) " << endl << endl << endl ; }
    else{
      // dataset for each channel/region/category
      TString dataCatLabel = Form("channelCat==channelCat::%s",regionCatLabel.Data());
      RooDataSet* regionData = (RooDataSet*) data->reduce(dataCatLabel.Data());
      dataVec.push_back(regionData);
      // pdf for each channel/region/category
      RooAbsPdf* regionPdf = (RooAbsPdf*) pdf->getPdf(regionCatLabel.Data());
      pdfVec.push_back(regionPdf);
    }
  }
  
  
  if(dataVec.empty()){ 
    cout << endl << endl  << "   NONE OF THE REGIONS ARE SPECIFIED IN DATASET, NO FIT WILL BE PERFORMED" << endl; 
    return 0;
  }
  else if(pdfVec.empty()){ 
    cout << endl << endl  << "   NONE OF THE REGIONS ARE SPECIFIED IN SIMULTANEOUS PDF, NO FIT WILL BE PERFORMED" << endl; 
    return 0;
  }
  else{
    // Construct a simultaneous dataset for all fit regions
    dataFitRegions = (RooDataSet*) dataVec[0]->Clone("dataFitRegions");
    for(unsigned int jVec=1; jVec<dataVec.size(); jVec++){
      dataFitRegions->append(*dataVec[jVec]);
    }
    // Construct a simultaneous pdf using category regionCat as index
    simPdfFitRegions = new RooSimultaneous("simPdfFitRegions","simultaneous pdf only for fit regions",*regionCat) ;
    for(unsigned int kVec=0; kVec<pdfVec.size(); kVec++){
      simPdfFitRegions->addPdf(*pdfVec[kVec],fitRegionsVec[kVec].Data());
    }
  }
  
  w->import(*simPdfFitRegions,kTRUE);
  gDirectory->Add(simPdfFitRegions);
  
  // fit pdf to data
  RooFitResult* r = 0;

  TString datasetname = data->GetName();
  cout << endl << endl << " datasetname = " << datasetname << endl;
  if( datasetname.Contains("asimov")){
    r = simPdfFitRegions->fitTo(*dataFitRegions,Save(),SumW2Error(kFALSE)); //MB no verbose :) ,Verbose(kTRUE));
  }
  else{
    r = simPdfFitRegions->fitTo(*dataFitRegions,Save(),SumW2Error(kFALSE));
  }
  r->Print("v");
  
  TString fitName = data->GetName();
  for(unsigned int iVec=0; iVec<fitRegionsVec.size(); iVec++){
    if(iVec ==0)  fitName += "_fitRegions";
    fitName += "_" + fitRegionsVec[iVec];
  }
    
  TString resultname = Form("RooFitResult_%s",fitName.Data());
  if(suffix!= "") resultname += "_" + suffix;
  r->SetName(resultname.Data());
  w->import(*r,kTRUE) ;
  gDirectory->Add(r);
 
  // save snapshot after fit has been done
  RooArgSet* params = (RooArgSet*) pdf->getParameters(*data) ;
  w->saveSnapshot(Form("snapshot_paramsVals_%s",resultname.Data()),*params);

  return r;
}
 

//_____________________________________________________________________________
RooAbsData* 
Util::GetAsimovSet( RooWorkspace* inputws  )
{
  RooWorkspace* w(0);
  if (inputws!=NULL) { w = inputws; }
  else { w = (RooWorkspace*) gDirectory->Get("w"); }

  if(w==NULL){ cout << "Workspace not found, no Asimov set found. Return." << endl; return 0; }

  RooAbsData* data = w->data("asimovData");
  if (data==NULL) { cout << "No Asimov set found. Return." << endl; return 0; }

  return data;
}
 

//_____________________________________________________________________________
RooAbsData* 
Util::GetToyMC( RooWorkspace* inputws  )
{
  RooWorkspace* w(0);
  if (inputws!=NULL) { w = inputws; }
  else { w = (RooWorkspace*) gDirectory->Get("w"); }
  if(w==NULL){ cout << "Workspace not found, no toy dataset generated." << endl; return 0; }

  RooStats::ModelConfig* mc = Util::GetModelConfig( w );
  if (mc==NULL) { cout << "No model config found. Return." << endl; return 0; }

  RooAbsPdf* pdf = mc->GetPdf();
  if (pdf==NULL) { cout << "No pdf found. Return." << endl; return 0; }

  RooAbsData* data = w->data("obsData");
  if (data==NULL) { cout << "No dataset found. Return." << endl; return 0; }

  const RooArgSet* obsSet = mc->GetObservables();
  if (obsSet==NULL) { cout << "No observables found. Return." << endl; return 0; }

  cout << "Util::GetToyMC() : now generating toy MC set with # events : " << data->sumEntries() << endl;

  RooAbsData* toymc = pdf->generate( *obsSet, RooFit::NumEvents(int(data->sumEntries())), RooFit::AutoBinned(false) );

  return toymc;
}
 
//_____________________________________________________________________________________________________________________________________
vector<TString> Util::GetRegionsVec(TString regions, RooCategory* regionCat){
  
  std::vector<TString> regionsVec;
  std::vector<TString> regionsAllVec = TokensALL(regionCat);
  std::vector<TString> regionsRequestedVec = Tokens(regions,",");
  
  if(regions=="ALL"){ regionsVec = regionsAllVec; 
  } else {
    for(unsigned int iReg=0; iReg<regionsAllVec.size(); iReg++){
      for(unsigned int jReg=0; jReg<regionsRequestedVec.size(); jReg++){
	if( regionsAllVec[iReg].EqualTo(regionsRequestedVec[jReg]) ) {
	  regionsVec.push_back(regionsAllVec[iReg]);
	}
      }    
    }
  }
  
  return regionsVec;
}

//__________________________________________________________________________________________________________________________________________________________
void Util::PlotPdfWithComponents(RooWorkspace* w, TString fcName, TString plotRegions, TString outputPrefix, RooFitResult* rFit, RooAbsData* inputData, Bool_t plotRatio)
{
 
  Bool_t plotComponents=true;
  ConfigMgr* mgr = ConfigMgr::getInstance();
  FitConfig* fc = mgr->getFitConfig(fcName);
  Float_t lumi =  fc->getLumi(); 
 
  cout << endl << endl << " ------ Starting Plot with parameters:   analysisName = " << fcName 
       << "    plotRegions = " <<  plotRegions <<  "  plotComponents = " << plotComponents << "  outputPrefix = " << outputPrefix  << endl << endl;

  RooMsgService::instance().getStream(1).removeTopic(NumIntegration);
  RooMsgService::instance().getStream(1).removeTopic(Plotting);


  if(w==NULL){ cout << endl << " Workspace not found, no plotting performed" << endl << endl; return; }
  RooSimultaneous* pdf = (RooSimultaneous*) w->pdf("simPdf");
  //pdf->Print("t");
  
  RooAbsData* data = ( inputData!=0 ? inputData : (RooAbsData*)w->data("obsData") ); 

  RooCategory* regionCat = (RooCategory*) w->cat("channelCat");
  data->table(*((RooAbsCategory*)regionCat))->Print("v");
  
  if(plotRegions =="") plotRegions = "ALL";
  std::vector<TString> regionsVec = GetRegionsVec(plotRegions, regionCat);

  unsigned  int numPlots = regionsVec.size();  
  TCanvas* canVec[numPlots];
  RooPlot* frameVec[numPlots];

  // iterate over all the regions 
  for(unsigned int iVec=0; iVec<numPlots; iVec++){
    TString regionCatLabel = regionsVec[iVec];
    //   cout << " regionCatLabel =  " << regionCatLabel << endl;
    if( regionCat->setLabel(regionCatLabel,kTRUE)){  cout << endl << " Label '" << regionCatLabel << "' is not a state of channelCat (see Table) " << endl << endl << endl; }
    else{
      RooAbsPdf* regionPdf = (RooAbsPdf*) pdf->getPdf(regionCatLabel.Data());
      TString dataCatLabel = Form("channelCat==channelCat::%s",regionCatLabel.Data());
      RooAbsData* regionData = (RooAbsData*) data->reduce(dataCatLabel.Data());
      //  cout << " regionPdf = " << regionPdf << "   regionData = " << regionData << endl;
      if(regionPdf==NULL || regionData==NULL){ 
	cout << " Either the Pdf or the Dataset do not have an appropriate state for the region = " << regionCatLabel << ", check the Workspace file" << endl;
	cout << " regionPdf = " << regionPdf << "   regionData = " << regionData << endl;  
	continue; 
      }
      RooRealVar* regionVar =(RooRealVar*) ((RooArgSet*) regionPdf->getObservables(*regionData))->find(Form("obs_x_%s",regionCatLabel.Data()));
      // regionVar->Print();
      RooPlot* frame =  regionVar->frame(); 
      frame->SetName(Form("frame_%s_%s",regionCatLabel.Data(),outputPrefix.Data()));
      data->plotOn(frame,Cut(dataCatLabel),RooFit::DataError(RooAbsData::Poisson));
      // normalize pdf to number of expected events, not to number of events in dataset
      double normCount = regionPdf->expectedEvents(*regionVar);
      regionPdf->plotOn(frame,Normalization(normCount,RooAbsReal::NumEvent),Precision(1e-5));
      // plot components
      if(plotComponents)  AddComponentsToPlot(w, fc, frame, regionPdf, regionData, regionVar, regionCatLabel.Data());
      // visualize error of fit
      if(rFit != NULL) 	regionPdf->plotOn(frame,Normalization(normCount,RooAbsReal::NumEvent),Precision(1e-5),FillColor(kBlue-5),FillStyle(3004),VisualizeError(*rFit));
      // re-plot data and pdf, so they are on top
      regionPdf->plotOn(frame,Normalization(normCount,RooAbsReal::NumEvent),Precision(1e-5));
      regionData->plotOn(frame,RooFit::DataError(RooAbsData::Poisson));
      //   pdf->plotOn(frame, Slice(*regionCat,regionCatLabel.Data()),ProjWData(*regionCat,*data),LineStyle(kDashed),LineColor(kMagenta));
      //      data->plotOn(frame,Cut(dataCatLabel),RooFit::DataError(RooAbsData::Poisson));

      TString canName=Form("can_%s_%s",regionCatLabel.Data(),outputPrefix.Data());

      canVec[iVec] = new TCanvas(canName,canName, 700, 600);// 200,10,920,800); //720, 790); ////600,400); // .c_str())
      TPad *pad1 = new TPad(Form("%s_pad1",canName.Data()),Form("%s_pad1",canName.Data()),0.,0.305,.99,1);
      pad1->SetBottomMargin(0.005);
      pad1->SetFillColor(kWhite);
      TPad *pad2 = new TPad(Form("%s_pad2",canName.Data()),Form("%s_pad2",canName.Data()),0.,0.01,.99,0.295);
      pad2->SetTopMargin(0.005);
      pad2->SetBottomMargin(0.3);
      pad2->SetFillColor(kWhite);
      
      canVec[iVec]->cd();
      pad1->Draw();
      pad2->Draw();

      pad1->cd();
      frame->SetMinimum(0.); 
      //frame->SetMaximum(frame->GetMaximum()*10.);
      
      frame->Draw();
      
      ATLASLabel(0.25,0.875,"for approval");
      //AddText(0.25,0.85,Form("#int Ldt = %.3f fb^{-1}",lumi));
      AddText(0.175,0.775,Form("#int Ldt = %.1f fb^{-1}",lumi));
      
      TLegend* leg = new TLegend(0.6,0.475,0.9,0.925,"");
      leg->SetFillStyle(0);
      leg->SetFillColor(0);
      leg->SetBorderSize(0);
      TLegendEntry* entry=leg->AddEntry("","Data 2011 (#sqrt{s}=7 TeV)","p") ;
      entry->SetMarkerColor(kBlack);
      entry->SetMarkerStyle(20);
      entry=leg->AddEntry("","Total pdf","lf") ;
      entry->SetLineColor(kBlue);
      entry->SetFillColor(kBlue-5);
      entry->SetFillStyle(3004);
 
      // add components to legend
      TString RRSPdfName = Form("%s_model",regionCatLabel.Data()); 
      RooRealSumPdf* RRSPdf = (RooRealSumPdf*) regionPdf->getComponents()->find(RRSPdfName);
      RooArgList RRSComponentsList =  RRSPdf->funcList();
      RooLinkedListIter iter = RRSComponentsList.iterator() ;
      RooProduct* component;
      vector<TString> compNameVec;
      compNameVec.clear();
      while( (component = (RooProduct*) iter.Next())) { 
	TString  componentName = component->GetName();
	cout << "componentName = " << componentName << endl;
	compNameVec.push_back(componentName);
      }
     
      for( int iComp = (compNameVec.size()-1) ; iComp>-1; iComp--){
	Int_t  compPlotColor    = ( (fc!=0) ? fc->getSampleColor(compNameVec[iComp]) : iComp );
	TString  compShortName  = ( (fc!=0) ? fc->getSampleName(compNameVec[iComp])  : "" );
	
	TString legName = "";
	/*if(compShortName.Contains("BG")) legName = "single top & diboson";
	if(compShortName.Contains("WZ")) legName = "W+jets & Z+jets";
	if(compShortName.Contains("Top")) legName = "t#bar{t}";
	if(compShortName.Contains("QCD")) legName = "multijets (data estimate)";
    
	//
	if(compShortName.Contains("WZpT0GeV"))   legName = "W/Z (p_{T}^{V,Truth}=0-50GeV)";
	if(compShortName.Contains("WZpT50GeV"))  legName = "W/Z (p_{T}^{V,Truth}=50-100GeV)";
	if(compShortName.Contains("WZpT100GeV")) legName = "W/Z (p_{T}^{V,Truth}=100-150GeV)";
	if(compShortName.Contains("WZpT150GeV")) legName = "W/Z (p_{T}^{V,Truth}=150-200GeV)";
	if(compShortName.Contains("WZpT200GeV")) legName = "W/Z (p_{T}^{V,Truth}=200-250GeV)";
	if(compShortName.Contains("WZpT250GeV")) legName = "W/Z (p_{T}^{V,Truth}=250GeV-)";
	
	else legName = compShortName;
	*/
	legName = compShortName;
	entry=leg->AddEntry("",legName.Data(),"f") ;
	//	if(compShortName.Contains("QCD") && hasQCDentry) continue;
	//	else if(compShortName.Contains("QCD") && !hasQCDentry) hasQCDentry = true;
	//	entry=leg->AddEntry("",compShortName.Data(),"f") ;
	entry->SetLineColor(compPlotColor);
	entry->SetFillColor(compPlotColor);
	entry->SetFillStyle(1001);
      }
      leg->Draw();
      
      frameVec[iVec]=frame;

      // now make/draw the ratio histogram
      pad2->cd();

      // data/pdf ratio histograms is plotted by RooPlot.ratioHist()
      RooPlot* frame_dummy =  regionVar->frame(); 
      data->plotOn(frame_dummy,Cut(dataCatLabel),RooFit::DataError(RooAbsData::Poisson));
      // normalize pdf to number of expected events, not to number of events in dataset
      regionPdf->plotOn(frame_dummy,Normalization(normCount,RooAbsReal::NumEvent),Precision(1e-5));      
      // Construct a histogram with the ratio of the data w.r.t the pdf curve
      RooHist* hratio = NULL;
      if(plotRatio)  hratio = (RooHist*) frame_dummy->ratioHist() ;
      else hratio = (RooHist*) frame_dummy->pullHist() ;

      // Construct a histogram with the ratio of the pdf curve w.r.t the pdf curve +/- 1 sigma
      RooCurve* hratioPdfError = new RooCurve;
      if (rFit != NULL)  hratioPdfError = MakePdfErrorRatioHist(w, regionData, regionPdf, regionVar, rFit);
      
      //  pad2->cd();

      // Create a new frame to draw the residual distribution and add the distribution to the frame
      RooPlot* frame2 = regionVar->frame() ;
      if(plotRatio)  hratio->SetTitle("Ratio Distribution");
      else hratio->SetTitle("Pull Distribution");
      frame2->addPlotable(hratio,"P");
      // only add PdfErrorsPlot when the plot shows ratio, not with pull
      if (rFit != NULL && plotRatio)   frame2->addPlotable(hratioPdfError,"F");
      
      int firstbin = frame_dummy->GetXaxis()->GetFirst();
      int lastbin = frame_dummy->GetXaxis()->GetLast();
      double xmax = frame_dummy->GetXaxis()->GetBinUpEdge(lastbin) ;
      double xmin = frame_dummy->GetXaxis()->GetBinLowEdge(firstbin) ;

      TLine* l = new TLine(xmin,1.,xmax,1.);
      TLine* l2 = new TLine(xmin,0.5,xmax,0.5);
      TLine* l3 = new TLine(xmin,1.5,xmax,1.5);
      TLine* l4 = new TLine(xmin,2.,xmax,2.);
      TLine* l5 = new TLine(xmin,2.5,xmax,2.5);
      l->SetLineWidth(1);
      l->SetLineStyle(2);
      l2->SetLineStyle(3);
      l3->SetLineStyle(3);
      l4->SetLineStyle(3);
      l5->SetLineStyle(3);
     
     
      TLine* lp1 = new TLine(xmin,1.,xmax,1.);	
      TLine* lp2 = new TLine(xmin,2.,xmax,2.);	
      TLine* lp3 = new TLine(xmin,3.,xmax,3.);
      TLine* lp4 = new TLine(xmin,4.,xmax,4.);
      TLine* lp5 = new TLine(xmin,5.,xmax,5.);
      TLine* lp6 = new TLine(xmin,-1.,xmax,-1.);	
      TLine* lp7 = new TLine(xmin,-2.,xmax,-2.);	
      TLine* lp8 = new TLine(xmin,-3.,xmax,-3.);
      TLine* lp9 = new TLine(xmin,-4.,xmax,-4.);
      TLine* lp10 = new TLine(xmin,-5.,xmax,-5.);
      
      lp1->SetLineStyle(3);
      lp2->SetLineStyle(3);
      lp3->SetLineStyle(3);
      lp4->SetLineStyle(3);
      lp5->SetLineStyle(3);
      lp6->SetLineStyle(3);
      lp7->SetLineStyle(3);
      lp8->SetLineStyle(3);
      lp9->SetLineStyle(3);
      lp10->SetLineStyle(3);
      
      if(plotRatio){	
	frame2->addObject(l);
	frame2->addObject(l2);
	frame2->addObject(l3);
	frame2->addObject(l4);
	frame2->addObject(l5);
      } else {
	frame2->addObject(lp1);
	frame2->addObject(lp2);
	frame2->addObject(lp3);
    	frame2->addObject(lp4);
	frame2->addObject(lp5);
	frame2->addObject(lp6);
    	frame2->addObject(lp7);
	frame2->addObject(lp8);
	frame2->addObject(lp9);
	frame2->addObject(lp10);
      }

      Double_t lowerlimit = 0.; 
      Double_t upperlimit = 2.2; 
      if (!plotRatio){ lowerlimit = -5.7; upperlimit = 5.7;}

      frame2->SetMinimum(lowerlimit);
      frame2->SetMaximum(upperlimit);

      if(plotRatio) frame2->GetYaxis()->SetTitle("Data / SM");
      else frame2->GetYaxis()->SetTitle("Pull");
      
      frame2->GetXaxis()->SetTitle(GetXTitle(regionVar)); //Name());

      frame2->GetYaxis()->SetLabelSize(0.13);
      frame2->GetYaxis()->SetNdivisions(504);                                                                                                   
      frame2->GetXaxis()->SetLabelSize(0.13);
      frame2->GetYaxis()->SetTitleSize(0.14);
      frame2->GetXaxis()->SetTitleSize(0.14);
      frame2->GetYaxis()->SetTitleOffset(0.35);
      frame2->GetXaxis()->SetTitleOffset(1.);
      frame2->GetYaxis()->SetLabelOffset(0.01);
      frame2->GetXaxis()->SetLabelOffset(0.03);
      frame2->GetXaxis()->SetTickLength(0.06);
      
      frame2->Draw();

      canVec[iVec]->SaveAs("results/"+canName+".pdf");
      canVec[iVec]->SaveAs("results/"+canName+".eps");

    }
  }

  cout << endl << endl;

}



//_____________________________________________________________________________
void Util::AddComponentsToPlot(RooWorkspace* w, FitConfig* fc, RooPlot* frame, RooAbsPdf* regionPdf, RooAbsData* regionData, RooRealVar* obsRegion, TString regionCatLabel)
{

  // regionPdf->Print("t");
  TString RRSPdfName = Form("%s_model",regionCatLabel.Data()); 
  RooRealSumPdf* RRSPdf = (RooRealSumPdf*) regionPdf->getComponents()->find(RRSPdfName);
  cout << endl << "Adding Components of Region-Model = " << RRSPdfName << " to plot" << endl;

  RooArgList RRSComponentsList =  RRSPdf->funcList();
  //RRSComponentsList.Print("v");

  //  if (regionData!=0) regionData->Print();

  RooLinkedListIter iter = RRSComponentsList.iterator() ;
  RooProduct* component;
  vector<TString> compNameVec;
  vector <double> compFracVec;
  vector<TString> compStackNameVec;
  vector <double> compStackFracVec;
  compNameVec.clear();
  compStackNameVec.clear();
  compFracVec.clear();
  compStackFracVec.clear();

  TString binWidthName =  Form("binWidth_obs_x_%s_0",regionCatLabel.Data());
  RooRealVar* regionBinWidth = ((RooRealVar*) RRSPdf->getVariables()->find(Form("binWidth_obs_x_%s_0",regionCatLabel.Data()))) ;

  if(regionBinWidth==NULL){
    cout << " bindWidth variable not found for region(" << regionCatLabel << "),   PLOTTING COMPONENTS WILL BE WRONG " << endl ;
  }
  
  while( (component = (RooProduct*) iter.Next())) { 
    TString  componentName = component->GetName();
    TString stackComponentName = componentName; 
    if(!compStackNameVec.empty()){  stackComponentName  = Form("%s,%s",compStackNameVec.back().Data() ,componentName.Data()); }
    compNameVec.push_back(componentName);
    compStackNameVec.push_back(stackComponentName);
    
    double componentFrac = GetComponentFrac(w,componentName,RRSPdfName,obsRegion,regionBinWidth) ;
    double stackComponentFrac = componentFrac; 
    if(!compStackFracVec.empty()){  stackComponentFrac  = compStackFracVec.back() + componentFrac; } 
    compFracVec.push_back(componentFrac);
    compStackFracVec.push_back(stackComponentFrac);
    
  }

  // normalize data to expected number of events 
  double normCount = regionPdf->expectedEvents(*obsRegion);
   
  for( int iVec = (compFracVec.size()-1) ; iVec>-1; iVec--){
    Int_t  compPlotColor = ( (fc!=0) ? fc->getSampleColor(compNameVec[iVec]) : iVec );
        
    if(compPlotColor == 0) compPlotColor = kMagenta;
    regionPdf->plotOn(frame,Components(compStackNameVec[iVec].Data()),FillColor(compPlotColor),FillStyle(1001),DrawOption("F"),Normalization(compStackFracVec[iVec]*normCount,RooAbsReal::NumEvent),Precision(1e-5));
        
  }
}



//_____________________________________________________________________________________________________________________________________
void Util::PlotSeparateComponents(RooWorkspace* w,TString fcName, TString plotRegions,TString outputPrefix, RooFitResult* rFit, RooAbsData* inputData)
{
  if(rFit==NULL){ cout << " Running PlotSeparateComponents() without a RooFitResult is pointless, I'm done" << endl ; return; }

  Bool_t plotComponents=true;
  ConfigMgr* mgr = ConfigMgr::getInstance();
  FitConfig* fc = mgr->getFitConfig(fcName);

  cout << endl << endl << " ------ Starting Plot with parameters:   analysisName = " << fcName 
       << "    fitRegions = " <<  plotRegions <<  "  plotComponents = " << plotComponents << "  outputPrefix = " << outputPrefix  << endl << endl;

  if(w==NULL){ cout << endl << " Workspace not found, no plotting performed" << endl << endl; return; }
  RooSimultaneous* pdf = (RooSimultaneous*) w->pdf("simPdf");

  RooAbsData* data = ( inputData!=0 ? inputData : (RooAbsData*)w->data("obsData") ); 
  RooCategory* regionCat = (RooCategory*) w->cat("channelCat");
  data->table(*((RooAbsCategory*)regionCat))->Print("v");

  if(plotRegions =="") plotRegions = "ALL";
  std::vector<TString> regionsVec = GetRegionsVec(plotRegions, regionCat);
  
  unsigned  int numRegions = regionsVec.size();
  TCanvas* canVec[numRegions];

  vector<TString> samplesVec = fc->m_sampleNames;
 
  for(unsigned int iVec=0; iVec<numRegions; iVec++){   
    
    TString regionCatLabel = regionsVec[iVec];
    if( regionCat->setLabel(regionCatLabel,kTRUE)){  cout << endl << " Label '" << regionCatLabel << "' is not a state of channelCat (see Table) " << endl << endl << endl; }
    else{
      RooAbsPdf* regionPdf = (RooAbsPdf*) pdf->getPdf(regionCatLabel.Data());
      TString dataCatLabel = Form("channelCat==channelCat::%s",regionCatLabel.Data());
      RooAbsData* regionData = (RooAbsData*) data->reduce(dataCatLabel.Data());
      if(regionPdf==NULL || regionData==NULL){ 
	cout << " Either the Pdf or the Dataset do not have an appropriate state for the region = " << regionCatLabel << ", check the Workspace file" << endl;
	cout << " regionPdf = " << regionPdf << "   regionData = " << regionData << endl;  
	continue; 
      }
      RooRealVar* regionVar =(RooRealVar*) ((RooArgSet*) regionPdf->getObservables(*regionData))->find(Form("obs_x_%s",regionCatLabel.Data()));
      // get all components/samples in this region
      TString RRSPdfName = Form("%s_model",regionCatLabel.Data()); 
      RooRealSumPdf* RRSPdf = (RooRealSumPdf*) regionPdf->getComponents()->find(RRSPdfName);
      TString binWidthName =  Form("binWidth_obs_x_%s_0",regionCatLabel.Data());
      RooRealVar* regionBinWidth = ((RooRealVar*) RRSPdf->getVariables()->find(Form("binWidth_obs_x_%s_0",regionCatLabel.Data()))) ;
      if(regionBinWidth==NULL){
	cout << " bindWidth variable not found for region(" << regionCatLabel << "),   PLOTTING COMPONENTS WILL BE WRONG " << endl ;
      }
      
      vector<double> regionCompFracVec = GetAllComponentFracInRegion(w, regionCatLabel, regionPdf, regionVar,regionBinWidth);
      vector<TString> regionCompNameVec = GetAllComponentNamesInRegion(regionCatLabel, regionPdf);
      Int_t numComps = regionCompNameVec.size();
   
      // divide the canvas
      Int_t canVecDivX = 1;
      Int_t canVecDivY = 1;
      if(numComps>0){
	canVecDivX = ((Int_t) (sqrt(numComps)));
	canVecDivY = ((Int_t) (sqrt(numComps)+0.5));
	// cout << " canVecDivX = " << canVecDivX << " canVecDivY = " << canVecDivY << endl;
	if(canVecDivX<1) canVecDivX = 1;
	if(canVecDivY<1) canVecDivY = 1;
      }  

      RooPlot* frameVec[numRegions][numComps];
  

      TString canName=Form("can_%s_%s_separateComponents",regionCatLabel.Data(),outputPrefix.Data());
      canVec[iVec] = new TCanvas(canName,canName,600,600); // .c_str()) 
      canVec[iVec]->Divide(canVecDivX , canVecDivY);

      //iterate over all samples and plot
      for( unsigned int iComp=0; iComp<regionCompFracVec.size(); iComp++){
	//	cout << endl << " component = " << regionCompNameVec[iComp] << endl;
	TString component =  regionCompNameVec[iComp];
	RooPlot* frame =  regionVar->frame(); 
	frame->SetName(Form("frame_%s_%s_%s",regionCatLabel.Data(),regionCompNameVec[iComp].Data(),outputPrefix.Data()));
	Int_t  compPlotColor = ( (fc!=0) ? fc->getSampleColor(regionCompNameVec[iComp]) : static_cast<int>(iComp) );
	TString  compShortName  = ( (fc!=0) ? fc->getSampleName(regionCompNameVec[iComp])  : "" );
	// normalize pdf to number of expected events, not to number of events in dataset
	double normCount = regionPdf->expectedEvents(*regionVar);

	if (rFit != NULL) regionPdf->plotOn(frame,Components(regionCompNameVec[iComp].Data()),VisualizeError(*rFit),FillColor(kCyan),Precision(1e-5),Normalization(regionCompFracVec[iComp]*normCount,RooAbsReal::NumEvent));
	regionPdf->plotOn(frame,Components(regionCompNameVec[iComp].Data()),LineColor(compPlotColor),Normalization(regionCompFracVec[iComp]*normCount,RooAbsReal::NumEvent),Precision(1e-5));
	
	canVec[iVec]->cd(iComp+1);
	//  canVec[iVec] ->SetLogy();
	frame->SetMinimum(0.);
	frame->Draw();
	frameVec[iVec][iComp]=frame;

	TLegend* leg = new TLegend(0.55,0.65,0.85,0.9,"");
	leg->SetFillStyle(0);
	leg->SetFillColor(0);
	leg->SetBorderSize(0);
	TLegendEntry* entry=leg->AddEntry("","Prop. Fit Error","f") ;
	entry->SetMarkerColor(kCyan);
	entry->SetMarkerStyle();	
	entry->SetFillColor(kCyan);
	entry->SetFillStyle(1001);
	//	entry->SetFillStyle(3004);
	entry=leg->AddEntry("",compShortName.Data(),"l") ;
	entry->SetLineColor(compPlotColor);
	//	entry->SetFillStyle(1001);
	leg->Draw();
      }
       
      canVec[iVec]->SaveAs("results/"+canName+".pdf");
      canVec[iVec]->SaveAs("results/"+canName+".eps");
    }
  }
  
  
}





//_____________________________________________________________________________________________________________________________________
void Util::PlotNLL(RooWorkspace* w, RooFitResult* rFit, Bool_t plotPLL, TString outputPrefix, RooAbsData* inputData)
{
  if(rFit==NULL){ cout << " Running PlotSeparateComponents() without a RooFitResult is pointless, I'm done" << endl ; return; }
  
  cout << endl << endl << " ------ Starting PlotNLL with parameters:  "
       << "  outputPrefix = " << outputPrefix  << endl << endl;

  if(w==NULL){ cout << endl << " Workspace not found, no plotting performed" << endl << endl; return; }
  RooSimultaneous* pdf = (RooSimultaneous*) w->pdf("simPdf");

  RooAbsData* data = ( inputData!=0 ? inputData : (RooAbsData*)w->data("obsData") ); 
  RooCategory* regionCat = (RooCategory*) w->cat("channelCat");
  data->table(*((RooAbsCategory*)regionCat))->Print("v");

  // Get all parameters of result
  RooArgList  fpf =  rFit->floatParsFinal();
 
  // Create Log Likelihood    
  RooAbsReal* nll = pdf->createNLL(*data,NumCPU(2)) ;
  // Create the profile likelihood  
  RooStats::ModelConfig* modelConfig = (RooStats::ModelConfig*) w->obj("ModelConfig");
  const RooArgSet* poi = modelConfig->GetParametersOfInterest();
  RooAbsReal* pll = nll->createProfile(*poi) ;
  
  unsigned  int numPars = fpf.getSize();
  if(numPars<1){
    cout << " WARNING: Util::PlotNLL rFit contains no floating parameters" << endl;
    return;
  }
  
  TString canName=Form("can_NLL_%s_%s",outputPrefix.Data(),rFit->GetName());
  TCanvas* can = new TCanvas(canName,canName,600,600); 

  // divide the canvas
  Int_t canVecDivX = 1;
  Int_t canVecDivY = 1;
  if(numPars>0){
    canVecDivX = ((Int_t) (sqrt(numPars)+0.5));
    canVecDivY = ((Int_t) (sqrt(numPars)+0.5));
    //    cout << endl << " canVecDivX = " << canVecDivX << " canVecDivY = " << canVecDivY << endl;
    if(canVecDivX<1) canVecDivX = 1;
    if(canVecDivY<1) canVecDivY = 1;
  }  
  can->Divide(canVecDivX , canVecDivY);

  // loop over all floating pars
  for(unsigned int iPar=0; iPar<numPars ; iPar++){
    RooAbsArg* arg = fpf.at(iPar);
    if(arg->InheritsFrom("RooRealVar")){
      RooRealVar* par = (RooRealVar*) arg;
      TString parName = par->GetName();
      cout << endl << "Plotting NLL for par = " << parName << endl;
      RooPlot* frame = par->frame();
      nll->plotOn(frame, ShiftToZero());
      frame->SetMinimum(0.);
      frame->SetMaximum(10000.);

      if(plotPLL)   pll->plotOn(frame,LineColor(kRed),LineStyle(kDashed),NumCPU(4)) ;
      
      can->cd(iPar+1);
      frame->Draw();  

      TLegend* leg = new TLegend(0.55,0.65,0.85,0.9,"");
      leg->SetFillStyle(0);
      leg->SetFillColor(0);
      leg->SetBorderSize(0);
      TLegendEntry* entry=leg->AddEntry("","NLL","l") ;
      entry->SetLineColor(kBlue);
      entry=leg->AddEntry("","PLL","l") ;
      entry->SetLineColor(kRed);
      entry->SetLineStyle(kDashed);
      leg->Draw();

    }
  }
         
  can->SaveAs("results/"+canName+".pdf");
  can->SaveAs("results/"+canName+".eps");

  delete nll ;
  delete pll;
  //  delete fpf;
    
}




//_____________________________________________________________________________
TH2D* Util::PlotCorrelationMatrix(RooFitResult* rFit){
 
  if(rFit==NULL){ cout << " Running PlotCorrelationMatrix() without a RooFitResult is pointless, I'm done" << endl ; throw 1 ; }
   
  Int_t numPars = rFit->floatParsFinal().getSize();

  TString canName = Form("c_corrMatrix_%s",rFit->GetName());
  TCanvas* c_corr = new TCanvas(canName.Data(),canName.Data(),600,400); // .c_str()) 
  
  Double_t orig_MarkerSize =  gStyle->GetMarkerSize();
  Int_t orig_MarkerColor =  gStyle->GetMarkerColor();
  const char* orig_PaintTextFormat = gStyle->GetPaintTextFormat() ;
  Double_t orig_LabelSize = gStyle->GetLabelSize();

  gStyle->SetPalette(51) ;
  gStyle->SetMarkerSize(1.45);
  gStyle->SetMarkerColor(kWhite);
  gStyle->SetPaintTextFormat("4.2f") ;
  
  if(numPars<5)    gStyle->SetMarkerSize(1.4);
  else if(numPars<10)    gStyle->SetMarkerSize(1.1);
  else if(numPars<20)    gStyle->SetMarkerSize(0.85);
  else     gStyle->SetMarkerSize(0.5);

 
  TH2D* h_corr = (TH2D*) rFit->correlationHist(Form("h_corr_%s",rFit->GetName())); 

  Double_t labelSize = orig_LabelSize;
  if(numPars<5) labelSize = 0.05;
  else if(numPars<10)   labelSize = 0.04;
  else if(numPars<20)   labelSize = 0.025;
  else labelSize = 0.02;

  h_corr->GetXaxis()->SetLabelSize(labelSize);
  h_corr->GetYaxis()->SetLabelSize(labelSize);
 
  gPad->SetLeftMargin(0.18);
  gPad->SetRightMargin(0.13);
  
  h_corr->Draw("colz");
  h_corr->Draw("textsame");
  
  c_corr->SaveAs("results/"+canName+".pdf");
  c_corr->SaveAs("results/"+canName+".eps");
  
  gStyle->SetMarkerSize(orig_MarkerSize);
  gStyle->SetMarkerColor(orig_MarkerColor);
  gStyle->SetPaintTextFormat(orig_PaintTextFormat) ;
  gStyle->SetLabelSize(orig_LabelSize);

  return h_corr;

}

//_____________________________________________________________________________
TH2D* Util::GetCorrelations(RooFitResult* rFit, double threshold) {
  TH2D* h_corr = Util::PlotCorrelationMatrix(rFit);
  
  unsigned int nBinsX = h_corr->GetNbinsX();
  unsigned int nBinsY = h_corr->GetNbinsY();
  
  for(unsigned int iBinY = 1; iBinY <= nBinsY; iBinY++){
    for(unsigned int iBinX = 1; iBinX <= nBinsX && iBinX <= (nBinsX-iBinY); iBinX++){
      if(fabs(h_corr->GetBinContent(iBinX,iBinY)) > threshold){
	cout << endl << " High correlation coefficient between:   par1 = " << h_corr->GetXaxis()->GetBinLabel(iBinX) << "  and par2 = "
	     << h_corr->GetYaxis()->GetBinLabel(iBinY) << " " 
	     << " val = " << h_corr->GetBinContent(iBinX,iBinY) << endl;
      }
    }
  }

  return h_corr;
} 


//_____________________________________________________________________________
TString Util::GetShortCompName(TString compName) {
  
  TString shortCompName = "empty";
  if(compName.Contains("WZ")) shortCompName = "WZ";
  else if(compName.Contains("Top"))   shortCompName = "Top";
  else if(compName.Contains("SU")) shortCompName = "SUSY"; 
  
  if(shortCompName == "empty"){ cout << endl << " component(" << compName << ")  in GetCompName not recognized " << endl << endl; }
      
  return shortCompName;
}


//_____________________________________________________________________________
vector<TString> Util::Tokens(TString aline,TString aDelim)
{
  Int_t i;
  TObjArray* InObjArray;
  TObjString* os;
  TString s;
  vector<TString> OutStringVec;
  OutStringVec.clear();
  
  InObjArray=aline.Tokenize(aDelim);
  for ( i=0; i<InObjArray->GetEntriesFast(); i++ )
    {
      os=(TObjString*)InObjArray->At(i);
      s=os->GetString();
      //     cout << " string[" << i << "] = " << s << endl;
      OutStringVec.push_back(s);
    }
  return OutStringVec;
}


//_____________________________________________________________________________
vector<TString> Util::TokensALL(RooCategory* cat)
{
  
  vector<TString> OutStringVec;
  OutStringVec.clear();
  TIterator* iter = cat->typeIterator() ;
  RooCatType* catType ;
  while( (catType = (RooCatType*) iter->Next())) {
    TString regionCatLabel = catType->GetName();
    //    cout << " TOKENSALL :  regionCatLabel = " << regionCatLabel << endl;
    OutStringVec.push_back(regionCatLabel);
  }
    
  return OutStringVec;
    
}



//__________________________________________________________________________________________________________________________________________________________
Double_t Util::GetComponentFrac(RooWorkspace* w, const char* Component, const char* RRSPdfName, RooRealVar* observable, RooRealVar* binWidth){
  
  RooAbsReal*  i_RRSPdf = ((RooAbsPdf*)w->pdf(RRSPdfName))->createIntegral(RooArgSet(*observable));
  RooAbsReal*  i_component =   ((RooProduct*)w->obj(Component))->createIntegral(RooArgSet(*observable));
  
  Double_t Int_RRSPdf = i_RRSPdf->getVal();
  Double_t Int_component = i_component->getVal();
  
  Double_t componentFrac = 0.;
  if(Int_RRSPdf != 0.) componentFrac =  Int_component * binWidth->getVal() / Int_RRSPdf;
  
  delete  i_RRSPdf;
  delete  i_component;
  
  return componentFrac;
}



//________________________________________________________________________________________________
RooWorkspace*
Util::GetWorkspaceFromFile( const TString& infile, const TString& wsname )
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

  if (obj->ClassName()!=TString("RooWorkspace")) { // much faster than dynamic cast
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

  //file->Close(); // this invalidates w;
  return w;
}


//________________________________________________________________________________________________
RooStats::ModelConfig* 
Util::GetModelConfig( const RooWorkspace* w, const TString& mcName )
{
  if (w==0) {
    cout << "ERROR : Workspace is a null pointer." << endl;
    return NULL;
  }

  TObject* obj = w->obj( mcName.Data() ) ;
  if (obj==0) {
    cout << "ERROR : Cannot open ModelConfig <" << mcName << "> from workspace." << endl;
    return NULL;
  }
  
  RooStats::ModelConfig* mc = (RooStats::ModelConfig *)(obj);
  if ( mc==0 ) {
    cout << "ERROR : Cannot open ModelConfig <" << mcName << "> from workspace" << endl;
    return NULL;
  }

  return mc;
}


//________________________________________________________________________________________________
RooRealVar* 
Util::GetPOI( const RooWorkspace* w  )
{
  if(w==0){
     std::cerr << "ERROR : Input workspace is null!" << std::endl;
     return NULL;
  }

  RooStats::ModelConfig* mc = Util::GetModelConfig(w);
  if(mc==0){
     std::cerr << "ERROR : ModelConfig is null!" << std::endl;
     return NULL;
  }

  const RooArgSet* poiSet = mc->GetParametersOfInterest();
  RooRealVar* firstPOI = ( poiSet!=0 ? (RooRealVar*) poiSet->first() : 0 );

  return firstPOI;
}


//________________________________________________________________________________________________
RooFitResult*
Util::doFreeFit( RooWorkspace* w, RooDataSet* inputdata, const bool& verbose, const bool& resetAfterFit )
{
  // fit to reset the workspace

  if(w==0){
     std::cerr << "ERROR : Input workspace is null!" << std::endl;
     return NULL;
  }

  RooStats::ModelConfig* mc = Util::GetModelConfig(w);

  if(mc==0){
     std::cerr << "ERROR : ModelConfig is null!" << std::endl;
     return NULL;
  }

  /// get pdf and dataset 
  RooDataSet* data(0);
  if (inputdata!=0) { 
     data = inputdata;
  }
  else              
     data = dynamic_cast<RooDataSet*>(w->data("obsData")); // default: fit to data
  if (verbose) data->Print();

  RooAbsPdf* pdf = mc->GetPdf();

  if((data==0)||(pdf==0)){
     std::cerr << "Error: data set or pdf not found" <<std::endl;
     return NULL;
  }

  if (resetAfterFit) {
    // save snapshot before any fit has been done
    RooArgSet* params = (RooArgSet*) pdf->getParameters(*data) ;
    if(!w->loadSnapshot("snapshot_paramsVals_initial"))  w->saveSnapshot("snapshot_paramsVals_initial",*params);
    else cout << endl << " Snapshot 'snapshot_paramsVals_initial' already exists in  workspace, will not overwrite it" << endl;
  }

  /// do the fit
  RooFitResult* result = pdf->fitTo(*data,Save()); //PrintLevel(verbose?1:-1),Verbose(verbose?1:0),Save());

  if (resetAfterFit) {
    w->loadSnapshot("snapshot_paramsVals_initial");
  }

  return result;
}


//________________________________________________________________________________________________
RooMCStudy* 
Util::GetMCStudy( const RooWorkspace* w )
{
  if (w==0) {
    std::cerr << "ERROR : Input workspace is null. Return." << std::endl;
    return NULL;
  }

  RooStats::ModelConfig* mc = Util::GetModelConfig(w);

  if(mc==0){
     std::cerr << "ERROR : ModelConfig is null!" << std::endl;
     return NULL;
  }

  RooAbsPdf* pdf = mc->GetPdf();
  const RooArgSet* obsset = mc->GetObservables();

  if((pdf==0)||(obsset==0)){
     std::cerr << "ERROR : pdf or observables not found" <<std::endl;
     return NULL;
  }

  // caller owns mcstudy
  return ( new RooMCStudy( *pdf, *obsset, RooFit::FitOptions("r") ) ) ;
}





//________________________________________________________________________________________________
void Util::ATLASLabel(Double_t x,Double_t y,const char* text,Color_t color) 
{

  TLatex l; //l.SetTextAlign(12); l.SetTextSize(tsize); 
  l.SetNDC();
  l.SetTextFont(72);
  l.SetTextColor(color);

  double delx = 0.115*696*gPad->GetWh()/(472*gPad->GetWw());

  l.DrawLatex(x,y,"ATLAS");
  if (text) {
    TLatex p; 
    p.SetNDC();
    p.SetTextFont(42);
    p.SetTextColor(color);
    p.DrawLatex(x+delx,y,text);
    //    p.DrawLatex(x,y,"#sqrt{s}=900GeV");
  }
}


//________________________________________________________________________________________________
void Util::AddText(Double_t x,Double_t y,char* text,Color_t color) 
{

  TLatex l; //l.SetTextAlign(12); l.SetTextSize(tsize); 
  l.SetNDC();
  l.SetTextFont(72);
  l.SetTextColor(color);

  double delx = 0.115*696*gPad->GetWh()/(472*gPad->GetWw());

  if (text) {
    TLatex p; 
    p.SetNDC();
    p.SetTextFont(42);
    p.SetTextColor(color);
    p.DrawLatex(x+delx,y,text);
    //    p.DrawLatex(x,y,"#sqrt{s}=900GeV");
  }
}



//_____________________________________________________________________________
RooAbsReal* Util::GetComponent(RooWorkspace* w, TString component, TString region){  //, unsigned int bin){
 
  //   ConfigMgr* mgr = ConfigMgr::getInstance();
  //   FitConfig* fc = mgr->getFitConfig(fcName);
      
  std::vector<TString> componentVec = Tokens(component,",");
  if(componentVec.size() <1) { cout << " componentVec.size() < 1, for components = " << component << endl; }

  // RooWorkspace* w = (RooWorkspace*) gDirectory->Get("w");
  if(w==NULL){ cout << endl << " Workspace not found, no GetComponent performed" << endl << endl; return NULL; }
  
  RooCategory* regionCat = (RooCategory*) w->cat("channelCat");
  TString regionFullName = GetFullRegionName(regionCat, region);
  
  RooSimultaneous* pdf = (RooSimultaneous*) w->pdf("simPdf");
  RooAbsPdf* regionPdf = (RooAbsPdf*) pdf->getPdf(regionFullName.Data());
  
  RooAbsData* data = (RooAbsData*)w->data("obsData"); 
  TString dataCatLabel = Form("channelCat==channelCat::%s",regionFullName.Data());
  RooAbsData* regionData = (RooAbsData*) data->reduce(dataCatLabel.Data());
  
  if(regionPdf==NULL || regionData==NULL){ 
    cout << " Either the Pdf or the Dataset do not have an appropriate state for the region = " << region << ", check the Workspace file" << endl;
    cout << " regionPdf = " << regionPdf << "   regionData = " << regionData << endl;  
    return NULL; 
  }
  RooRealVar* regionVar =(RooRealVar*) ((RooArgSet*) regionPdf->getObservables(*regionData))->find(Form("obs_x_%s",regionFullName.Data()));

  // get the binWidth variable, to be multiplied with component RooProduct, for a complete component RooFormulaVar, as used in RooRealSumPdf
  TString binWidthName =  Form("binWidth_obs_x_%s_0",regionFullName.Data());
  RooRealVar* regionBinWidth = ((RooRealVar*) regionPdf->getVariables()->find(Form("binWidth_obs_x_%s_0",regionFullName.Data()))) ;
  
  if(regionBinWidth==NULL){
    cout << " bindWidth variable not found for region(" << regionFullName << "),   RETURNING COMPONENTS WILL BE WRONG " << endl ;
    return NULL;
  }
  
  // find the correct RooProduct
  vector<TString> regionCompNameVec = GetAllComponentNamesInRegion(regionFullName, regionPdf);
  RooArgList compFuncList;
  RooArgList compCoefList;
  for(unsigned int iReg=0; iReg<regionCompNameVec.size(); iReg++){
    for(unsigned int iComp=0; iComp< componentVec.size(); iComp++){
      if(  regionCompNameVec[iReg].Contains(componentVec[iComp])) {
       	compFuncList.add(*(RooProduct*)w->obj(regionCompNameVec[iReg]));
       	compCoefList.add(*regionBinWidth);
      }
    }  
  } 

  //   compFuncList.Print("v");
  //   compCoefList.Print("v");
  if (compFuncList.getSize()==0 || compCoefList.getSize()==0 || compCoefList.getSize()!=compFuncList.getSize()){
    cout << " Something wrong with compFuncList or compCoefList in Util::GetComponent() "<< endl;
    return NULL;
  }

  TString compName = "comps";
  for(unsigned int iVec=0; iVec<componentVec.size(); iVec++){
    compName += "_" + componentVec[iVec];
  }

  RooRealSumPdf* compRRS = new RooRealSumPdf(Form("RRS_region_%s_%s",region.Data(),compName.Data()),Form("RRS_region_%s_%s",region.Data(),compName.Data()),compFuncList,compCoefList);
  if(!compRRS){
    cout << " Cannot creat a RooRealSumPdf in Util::GetComponent() "<< endl;
    return NULL;
  }
  RooAbsReal* compFunc = compRRS->createIntegral(RooArgSet(*regionVar));
  
  if(compFunc == NULL){
    cout << " compRooProduct not found for region(" << regionFullName << "), component(" << component << ")   RETURNING COMPONENTS WILL BE WRONG " << endl ;
    return NULL;
  }
  
  RooFormulaVar* form_frac = new RooFormulaVar("form_fracError","@0",RooArgList(*compFunc));
  //RooFormulaVar* form_frac = new RooFormulaVar("form_fracError","@0 * @1",RooArgList(*regionBinWidth,*compFunc));
  //RooFormulaVar* form_frac = new RooFormulaVar("form_fracError","@0 * @1",RooArgList(*compFunc,*regionBinWidth));
  form_frac->SetName(Form("form_frac_region_%s_%s",region.Data(),compName.Data()));
  form_frac->SetTitle(Form("form_frac_region_%s_%s",region.Data(),compName.Data()));
  
  //  form_frac->SetName(Form("form_frac_%s_%s",regionFullName.Data(),compName.Data()));
  cout << " Adding " << form_frac->GetName() << " to workspace" << endl;
  w->import( *form_frac,kTRUE);
  gDirectory->Add(form_frac);

  return form_frac;
  //return compRRS;
    
}





//_____________________________________________________________________________
Double_t Util::GetComponentFracInRegion(RooWorkspace* w, TString component, TString region){
 
  //   ConfigMgr* mgr = ConfigMgr::getInstance();
  //   FitConfig* fc = mgr->getFitConfig(fcName);

  //  cout << " w = " << w   << "  component = " << component << " region = " << region << endl;

  std::vector<TString> componentVec = Tokens(component,",");
  if(componentVec.size() <1) { cout << " componentVec.size() < 1, for components = " << component << endl; }

  //RooWorkspace* w = (RooWorkspace*) gDirectory->Get("w");
  if(w==NULL){ cout << endl << " Workspace not found, no GetComponent performed" << endl << endl; return 0; }
  
  RooCategory* regionCat = (RooCategory*) w->cat("channelCat");
  TString regionFullName = GetFullRegionName(regionCat, region);

  RooSimultaneous* pdf = (RooSimultaneous*) w->pdf("simPdf");
  RooAbsPdf* regionPdf = (RooAbsPdf*) pdf->getPdf(regionFullName.Data());

  RooAbsData* data = (RooAbsData*)w->data("obsData"); 
  TString dataCatLabel = Form("channelCat==channelCat::%s",regionFullName.Data());
  RooAbsData* regionData = (RooAbsData*) data->reduce(dataCatLabel.Data());

  if(regionPdf==NULL || regionData==NULL){ 
    cout << " Either the Pdf or the Dataset do not have an appropriate state for the region = " << region << ", check the Workspace file" << endl;
    cout << " regionPdf = " << regionPdf << "   regionData = " << regionData << endl;  
    return 0; 
  }

  RooRealVar* regionVar =(RooRealVar*) ((RooArgSet*) regionPdf->getObservables(*regionData))->find(Form("obs_x_%s",regionFullName.Data()));

  // get the binWidth variable, to be multiplied with component RooProduct, for a complete component RooFormulaVar, as used in RooRealSumPdf
  TString binWidthName =  Form("binWidth_obs_x_%s_0",regionFullName.Data());
  RooRealVar* regionBinWidth = ((RooRealVar*) regionPdf->getVariables()->find(Form("binWidth_obs_x_%s_0",regionFullName.Data()))) ;
  
  if(regionBinWidth==NULL){
    cout << " bindWidth variable not found for region(" << regionFullName << "),   RETURNING COMPONENTS WILL BE WRONG " << endl ;
    return 0;
  }
  
  // find the correct RooProduct
  vector<TString> regionCompNameVec = GetAllComponentNamesInRegion(regionFullName, regionPdf);
  RooArgList compFuncList;
  RooArgList compCoefList;
  for(unsigned int iReg=0; iReg<regionCompNameVec.size(); iReg++){
    for(unsigned int iComp=0; iComp< componentVec.size(); iComp++){
      if(  regionCompNameVec[iReg].Contains(componentVec[iComp])) {
       	compFuncList.add(*(RooProduct*)w->obj(regionCompNameVec[iReg]));
       	compCoefList.add(*regionBinWidth);
      }
    }  
  } 
  
  //   compFuncList.Print("v");
  //   compCoefList.Print("v");
  if (compFuncList.getSize()==0 || compCoefList.getSize()==0 || compCoefList.getSize()!=compFuncList.getSize()){
    cout << " Something wrong with compFuncList or compCoefList in Util::GetComponent() "<< endl;
    return 0.;
  }

  TString compName = "comps";
  for(unsigned int iVec=0; iVec<componentVec.size(); iVec++){
    compName += "_" + componentVec[iVec];
  }
      
  // get the full RRSPdf of this region
  TString RRSPdfName = Form("%s_model",regionFullName.Data()); 
    
  double componentFrac = 0.;
  for(unsigned int iReg=0; iReg<regionCompNameVec.size(); iReg++){
     for(unsigned int iComp=0; iComp< componentVec.size(); iComp++){
       if(  regionCompNameVec[iReg].Contains(componentVec[iComp])) {
	 //	 cout <<  endl << " regionCompNameVec[iReg] = " << regionCompNameVec[iReg] << "   componentVec[iComp] = " << componentVec[iComp] << endl;
	 componentFrac += GetComponentFrac(w,regionCompNameVec[iReg],RRSPdfName,regionVar,regionBinWidth) ;
       }
     }
  }

  return componentFrac;
    
}




//_____________________________________________________________________________
RooAbsPdf* Util::GetRegionPdf(RooWorkspace* w, TString region){  //, unsigned int bin){
 
  //   ConfigMgr* mgr = ConfigMgr::getInstance();
  //   FitConfig* fc = mgr->getFitConfig(fcName);
  
  // RooWorkspace* w = (RooWorkspace*) gDirectory->Get("w");
  if(w==NULL){ cout << endl << " Workspace not found, no GetRegionPdf performed" << endl << endl; return NULL; }
  
  RooCategory* regionCat = (RooCategory*) w->cat("channelCat");
  TString regionFullName = GetFullRegionName(regionCat, region);
  
  RooSimultaneous* pdf = (RooSimultaneous*) w->pdf("simPdf");
  RooAbsPdf* regionPdf = (RooAbsPdf*) pdf->getPdf(regionFullName.Data());
  
//   //  pdf->Print("t");
//   cout << endl <<  " region = " << region  << " regionFullName =" << regionFullName << endl;
//   regionPdf->Print("t");

  
  if(regionPdf==NULL){ 
    cout << " The Simultaneous Pdf  does not have an appropriate state for the region = " << region << ", check the Workspace file" << endl;
    cout << " regionPdf = " << regionPdf << endl;  
    return NULL; 
  }
  
  return regionPdf;
  
}



//_____________________________________________________________________________
RooRealVar* Util::GetRegionVar(RooWorkspace* w, TString region){ 
  
  //  RooWorkspace* w = (RooWorkspace*) gDirectory->Get("w");
  if(w==NULL){ cout << endl << " Workspace not found, no GetComponent performed" << endl << endl; return NULL; }
  
  RooCategory* regionCat = (RooCategory*) w->cat("channelCat");
  TString regionFullName = GetFullRegionName(regionCat, region);
  
  RooSimultaneous* pdf = (RooSimultaneous*) w->pdf("simPdf");
  RooAbsPdf* regionPdf = (RooAbsPdf*) pdf->getPdf(regionFullName.Data());
  
  RooAbsData* data = (RooAbsData*)w->data("obsData"); 
  TString dataCatLabel = Form("channelCat==channelCat::%s",regionFullName.Data());
  RooAbsData* regionData = (RooAbsData*) data->reduce(dataCatLabel.Data());
  
  if(regionPdf==NULL || regionData==NULL){ 
    cout << " Either the Pdf or the Dataset do not have an appropriate state for the region = " << region << ", check the Workspace file" << endl;
    cout << " regionPdf = " << regionPdf << "   regionData = " << regionData << endl;  
    return NULL; 
  }
  RooRealVar* regionVar =(RooRealVar*) ((RooArgSet*) regionPdf->getObservables(*regionData))->find(Form("obs_x_%s",regionFullName.Data()));
  
  return regionVar;
  
}


//__________________________________________________________________________________________
TString Util::GetFullRegionName(RooCategory* regionCat,  TString regionShortName){

  std::vector<TString> regionsAllVec = TokensALL(regionCat);
  
  TString regionFullName;
  Int_t foundReg = 0;
  for(unsigned int iReg=0; iReg<regionsAllVec.size(); iReg++){
    // cout << " regionsAllVec[iReg] = " << regionsAllVec[iReg] << " regionShortName = " << regionShortName << endl;
    if( regionsAllVec[iReg].Contains(regionShortName) && foundReg==0) {
      regionFullName = regionsAllVec[iReg];
      foundReg++;
    } 
    if( regionsAllVec[iReg].Contains(regionShortName) && foundReg>1){
      foundReg++;
    }
  }
  //  cout << "  regionFullName = " << regionFullName << endl;
  
  if(foundReg>1)   cout << "   WARNING: Util.GetFullRegionName() found more then one region in workspace with shortname = " << regionShortName << endl;
  
  return regionFullName;
}



//__________________________________________________________________________________________
vector<TString> Util::GetAllComponentNamesInRegion(TString region, RooAbsPdf* regionPdf){
 
  TString RRSPdfName = Form("%s_model",region.Data()); 
  RooRealSumPdf* RRSPdf = (RooRealSumPdf*) regionPdf->getComponents()->find(RRSPdfName);

  if(RRSPdf==NULL){
    cout << " Util::GetAllComponentNamesInRegion() cannot find a RooRealSumPdf named " <<  RRSPdfName << endl ;
    vector<TString> vec;
    return vec; 
  }

  RooArgList RRSComponentsList =  RRSPdf->funcList();
  //RRSComponentsList.Print("v");

  RooLinkedListIter iter = RRSComponentsList.iterator() ;
  RooProduct* component;
  vector<TString> compNameVec;
  compNameVec.clear();

  while( (component = (RooProduct*) iter.Next())) { 
    TString  componentName = component->GetName();
    compNameVec.push_back(componentName);
  }
  
return compNameVec;
}




//__________________________________________________________________________________________
vector<double> Util::GetAllComponentFracInRegion(RooWorkspace* w, TString region, RooAbsPdf* regionPdf, RooRealVar* obsRegion,RooRealVar* regionBinWidth){
 
  TString RRSPdfName = Form("%s_model",region.Data()); 
  RooRealSumPdf* RRSPdf = (RooRealSumPdf*) regionPdf->getComponents()->find(RRSPdfName);

  RooArgList RRSComponentsList =  RRSPdf->funcList();
  //RRSComponentsList.Print("v");

  RooLinkedListIter iter = RRSComponentsList.iterator() ;
  RooProduct* component;
  vector<double> compFracVec;
  // vector<TString> compNameVec;
  //compNameVec.clear();
  compFracVec.clear();

  while( (component = (RooProduct*) iter.Next())) { 
    TString  componentName = component->GetName();
    double componentFrac = GetComponentFrac(w,componentName,RRSPdfName,obsRegion,regionBinWidth) ;
    compFracVec.push_back(componentFrac);
  }
  
return compFracVec;
}


//_____________________________________________________________________________
//double Util::GetPropagatedError(RooAbsReal* var, const RooFitResult& fr, const RooFitResult& frCR )
double Util::GetPropagatedError(RooAbsReal* var, const RooFitResult& fr) //, RooArgList varlist)
{
	
  // copied from RooAbsReal : fixed bug in reducedCovarianceMatrix (!)
  // add more text (sometimes) ;)
	 
  // Calculate error on self by propagated errors on parameters with correlations as given by fit result
  // The linearly propagated error is calculated as follows
  //                                    T           
  // error(x) = F_a(x) * Corr(a,a') F_a'(x)
  //
  // where     F_a(x) = [ f(x,a+da) - f(x,a-da) ] / 2, with f(x) this function and 'da' taken from the fit result
  //       Corr(a,a') = the correlation matrix from the fit result
  //

  // Clone self for internal use
  RooAbsReal* cloneFunc = var; //(RooAbsReal*) var->cloneTree();  // var;
  RooArgSet* errorParams = cloneFunc->getObservables(fr.floatParsFinal()) ;
  RooArgSet* nset = cloneFunc->getParameters(*errorParams) ;
  
// cout << endl << endl << " GPA: cloneFunc = "  << endl;
// cloneFunc->Print();
// cout << " GPA: errorParams = "  << endl;
// errorParams->Print("v");
// cout << " GPA: nset = "  << endl;
// nset->Print("v");
  

  // Make list of parameter instances of cloneFunc in order of error matrix
  RooArgList paramList ;
  const RooArgList& fpf = fr.floatParsFinal() ;
  vector<int> fpf_idx ;
  for (Int_t i=0 ; i<fpf.getSize() ; i++) {
    RooAbsArg* par = errorParams->find(fpf[i].GetName()) ;
    if (par ) {
      if (! par->isConstant() ) {
	paramList.add(*par) ;
	fpf_idx.push_back(i) ;
      }
    }
  }


  
  // cout << " GPA: paramList:" << endl;
//   paramList.Print("v");
  
  vector<Double_t> plusVar, minusVar ;   
	 
  TMatrixDSym V( fr.covarianceMatrix() ) ;

//   TMatrixDSym COR( fr.correlationMatrix() ) ;
//   V.Print();
//   COR.Print();

  for (Int_t ivar=0 ; ivar<paramList.getSize() ; ivar++) {
	   
    RooRealVar& rrv = (RooRealVar&)fpf[fpf_idx[ivar]] ;
	
    int newI = fpf_idx[ivar];
	
    Double_t cenVal = rrv.getVal() ;
    Double_t errVal = sqrt(V(newI,newI)) ;
	
    //    //rrv.Print();
    //     Double_t errMe = rrv.getError();
    //     Double_t errLo = rrv.getErrorLo();
    //     Double_t errHi = rrv.getErrorHi();
    
    // Make Plus variation
    ((RooRealVar*)paramList.at(ivar))->setVal(cenVal+errVal) ;
//     cout << endl << " GPA:  PLUS parName = " << ((RooRealVar*)paramList.at(ivar))->GetName()
// 	 << "  parVal = " << ((RooRealVar*)paramList.at(ivar))->getVal() << " cloneFunc(nset) = " << cloneFunc->getVal(nset) 
// 	  << " cloneFunc() = " <<    cloneFunc->getVal() << endl;
//    cloneFunc->Print("t");
    plusVar.push_back(cloneFunc->getVal(nset)) ;
	
    // Make Minus variation
    ((RooRealVar*)paramList.at(ivar))->setVal(cenVal-errVal) ;
//     cout << endl << " GPA:  MINUS parName = " << ((RooRealVar*)paramList.at(ivar))->GetName()
// 	 << "  parVal = " << ((RooRealVar*)paramList.at(ivar))->getVal() << " cloneFunc(nset) = " << cloneFunc->getVal(nset) 
// 	  << " cloneFunc() = " <<    cloneFunc->getVal() << endl;
    //    cloneFunc->Print("t");
    minusVar.push_back(cloneFunc->getVal(nset)) ;
	   
    ((RooRealVar*)paramList.at(ivar))->setVal(cenVal) ;

    //  cout << " GPA: for-loop"  << " ivar = " << ivar 
    //	 << " cenVal = " << cenVal << "   errVal = " << errVal << endl;
  }
	 
  TMatrixDSym C(paramList.getSize()) ;     
  vector<double> errVec(paramList.getSize()) ;
  for (int i=0 ; i<paramList.getSize() ; i++) {
   int newII = fpf_idx[i];
   errVec[i] = sqrt(V(newII,newII)) ;
   for (int j=i ; j<paramList.getSize() ; j++) {
     int newJ = fpf_idx[j];
     C(i,j) = V(newII,newJ)/sqrt(V(newII,newII)*V(newJ,newJ)) ;
     C(j,i) = C(i,j) ;
   }
  }
	  
  // Make vector of variations
  TVectorD F(plusVar.size()) ;
	
  for (unsigned int j=0 ; j<plusVar.size() ; j++) {
    //    cout << endl << " GPA:  plusVar = " << plusVar[j] << "   minusVar = " << minusVar[j] << endl;
    F[j] = (plusVar[j]-minusVar[j])/2 ;
  }
	
  // Calculate error in linear approximation from variations and correlation coefficient
  Double_t sum = F*(C*F) ;
  
//  F.Print();
//  C.Print();
//  cout << " sum = " << sum << endl;
  
  //  delete cloneFunc ;
  //  delete errorParams ;
  // delete nset ;
	
  return sqrt(sum) ;
}


//_____________________________________________________________________________
void
Util::resetAllErrors( RooWorkspace* wspace )
{
  RooStats::ModelConfig* mc  = Util::GetModelConfig(wspace);
  if (mc==0) return;

  const RooArgSet* obsSet = mc->GetObservables();
  if (obsSet==0) return;

  RooAbsPdf* pdf = mc->GetPdf();
  if (pdf==0) return;

  RooArgList floatParList = Util::getFloatParList( *pdf, *obsSet );

  //const RooArgSet* pars = pdf->getParameters(*obsSet);
  //if (pars==0) return;

  Util::resetError(wspace,floatParList);
}



//_____________________________________________________________________________
RooArgList 
Util::getFloatParList( const RooAbsPdf& pdf, const RooArgSet& obsSet )
{
  RooArgList floatParList;

  const RooArgSet* pars = pdf.getParameters( obsSet );
  if (pars==0) { return floatParList; }

  TIterator* iter = pars->createIterator() ;
  RooAbsArg* arg ;
  while( (arg=(RooAbsArg*)iter->Next()) ) {
    if(arg->InheritsFrom("RooRealVar") && !arg->isConstant()){
      floatParList.add( *arg );
    }
  }
  delete iter;

  return floatParList;
}



//_____________________________________________________________________________
void 
Util::resetError( RooWorkspace* wspace, const RooArgList& parList, const RooArgList& vetoList ) 

{

  // For the given workspace,
  // find the input systematic with
  // the given name and shift that
  // systematic by 1-sigma

  TIterator* iter = parList.createIterator() ;
  RooAbsArg* arg ;
  while( (arg=(RooAbsArg*)iter->Next()) ) {

    std::string UncertaintyName;
    if(arg->InheritsFrom("RooRealVar") && !arg->isConstant()){
      UncertaintyName = arg->GetName();
    } else { continue; }
   
    if ( vetoList.FindObject( UncertaintyName.c_str() )!=0 ) { continue; }

    RooRealVar* var = wspace->var( UncertaintyName.c_str() );
    if( ! var ) {
      std::cout << "Error: Could not find variable: " << UncertaintyName
		<< " in workspace: " << wspace->GetName() << ": " << wspace
		<< std::endl;
    }
    
    // Initialize
    double val_hi  = FLT_MAX;
    double val_low = FLT_MIN;
    double sigma = 0.;
    
    if( UncertaintyName == "" ) {
      std::cout << "Error: No Uncertainty Name provided" << std::endl;
      throw -1;
    }
    // If it is a standard (gaussian) uncertainty
    else if( string(UncertaintyName).find("alpha")!=string::npos ){ 
      // Assume the values are +1, -1
      val_hi  =  1.0;
      val_low = -1.0;      
      sigma = 1.0;
    }
    // If it is Lumi:
    else if( UncertaintyName == "Lumi" ) {
      // Get the Lumi's constraint term:
      RooGaussian* lumiConstr = (RooGaussian*) wspace->pdf("lumiConstraint");
      // Get the uncertainty on the Lumi:
      RooRealVar* lumiSigma = (RooRealVar*) lumiConstr->findServer(0);
      sigma = lumiSigma->getVal();
      
      RooRealVar* nominalLumi = wspace->var("nominalLumi");
      double val_nom = nominalLumi->getVal();
      
      val_hi  = val_nom + sigma;
      val_low = val_nom - sigma; 
    }
    // If it is a stat uncertainty (gamma)
    else if( string(UncertaintyName).find("gamma")!=string::npos ){
      
      // Get the constraint and check its type:
      RooAbsReal* constraint = (RooAbsReal*) wspace->obj( (UncertaintyName+"_constraint").c_str() );
      std::string ConstraintType ="";
      if(constraint != 0){ ConstraintType=constraint->IsA()->GetName(); }
      /*
      cout << string(UncertaintyName) << endl;
      cout << "here1" << endl;
      cout << "constraint " << constraint << endl;
      cout << "constraint->IsA() " << constraint->IsA() << endl;
      cout << constraint->IsA()->GetName() << endl;
      cout << "here2" << endl;
      */
      if( ConstraintType == "" ) {
	//std::cout << "Error: Strange constraint type for Stat Uncertainties " << ConstraintType << std::endl;
	std::cout << "Assuming parameter is a ShapeFactor and so unconstrained" << endl;
	continue;
      }
      else if( ConstraintType == "RooGaussian" ){
	RooAbsReal* sigmaVar = (RooAbsReal*) wspace->obj( (UncertaintyName+"_sigma").c_str() );
	sigma = sigmaVar->getVal();
	
	// Symmetrize shifts
	val_hi = 1 + sigma;
	val_low = 1 - sigma;
      }
      else if( ConstraintType == "RooPoisson" ){
	RooAbsReal* nom_gamma = (RooAbsReal*) wspace->obj( ("nom_" + UncertaintyName).c_str() );
	double nom_gamma_val = nom_gamma->getVal();
	
	sigma = 1/TMath::Sqrt( nom_gamma_val );
	
	val_hi = 1 + sigma;
	val_low = 1 - sigma;
      } 
      else {
	std::cout << "Error: Strange constraint type for Stat Uncertainties: " << ConstraintType << std::endl;
	throw -1;
      }
      
    } // End Stat Error
    else {
      // Some unknown uncertainty
      std::cout << "Warning: Couldn't identify type of uncertainty for parameter: " << UncertaintyName << ". Skip."   
		<< std::endl;
      continue;
    }
    
    std::cout << "Uncertainties on parameter: " << UncertaintyName 
	      << " low: "  << val_low
	      << " high: " << val_hi
              << " sigma: " << sigma
	      << std::endl;
    
    var->setError(abs(sigma));
    //var->setErrorHi(abs(sigma));
    //var->setErrorLo(-abs(sigma));
    //if( ShiftUp ) var->setVal( val_hi );
    //else          var->setVal( val_low );
    
    // Done
  } // end loop

  delete iter ;
}





//______________________________________________________________________________________________
void Util::ImportInWorkspace( RooWorkspace* wspace, TObject* obj, TString name) {
  
  if(obj){
    
    if(name && obj->InheritsFrom("TNamed") ) {
      ((TNamed*) obj)->SetName(name.Data());
      ((TNamed*) obj)->SetTitle(name.Data());
    }
    
    wspace->import(*obj,kTRUE) ;
  }
  else{
    cout << " WARNING: Util::Import called with a NULL pointer, nothing will be imported" << endl;
  }

  // save snapshot
  RooSimultaneous* pdf = (RooSimultaneous*) wspace->pdf("simPdf");
  RooAbsData* data = (RooAbsData*)wspace->data("obsData"); 
  RooArgSet* params = (RooArgSet*) pdf->getParameters(*data) ;

  wspace->saveSnapshot(Form("snapshot_paramsVals_%s",name.Data()),*params);

}



//________________________________________________________________________________________________________________________________________
RooCurve* Util::MakePdfErrorRatioHist(RooWorkspace* w, RooAbsData* regionData, RooAbsPdf* regionPdf, RooRealVar* regionVar, RooFitResult* rFit, Double_t Nsigma){

  // curvename=0 means that the last RooCurve is taken from the RooPlot
  const char* curvename = 0;
  
  RooPlot* frame =  regionVar->frame(); 
  regionData->plotOn(frame, RooFit::DataError(RooAbsData::Poisson));
  // RooHist* curveData = (RooHist*) frame->findObject(curvename,RooHist::Class()) ;
  // cout << "Util::makePdfErrorRatioHist(" << frame->GetName() << ") curveData = " << curveData->GetName() << endl ;

 //  for(Int_t i=1; i<curveData->GetN()-1; i++){
//     Double_t x,y;
//     curveData->GetPoint(i,x,y) ;
//     cout << "  data    i = " << i << "  x = " << x << " y = " << y << endl;
//   }


  // normalize pdf to number of expected events, not to number of events in dataset
  double normCount = regionPdf->expectedEvents(*regionVar);
  regionPdf->plotOn(frame,Normalization(normCount,RooAbsReal::NumEvent),Precision(1e-5));
  RooCurve* curveNom = (RooCurve*) frame->findObject(curvename,RooCurve::Class()) ;
  if (!curveNom) {
    cout << "Util::MakePdfErrorRatioHist(" << frame->GetName() << ") cannot find curveNom" << curveNom->GetName() << endl ;
    return 0 ;
  }
  //  cout << "Util::makePdfErrorRatioHist(" << frame->GetName() << ") curveNom = " << curveNom->GetName() << endl ;
  // cout << " curveNom->GetN() = " << curveNom->GetN() << endl;

//   Int_t curveNomN = curveNom->GetN() ;
//   for(Int_t i=1; i<curveNom->GetN(); i++){
//     Double_t x,y;
//     curveNom->GetPoint(i,x,y) ;
//     cout << "  Nom    i = " << i << "  x = " << x << " y = " << y << endl;
//   }
  
  if(rFit != NULL) regionPdf->plotOn(frame,Normalization(normCount,RooAbsReal::NumEvent),Precision(1e-5),FillColor(kBlue-5),FillStyle(3004),VisualizeError(*rFit,Nsigma));
  
  
  // Find curve object
  RooCurve* curveError = (RooCurve*) frame->findObject(curvename,RooCurve::Class()) ;
  //  cout << "Util::makePdfErrorRatioHist(" << frame->GetName() << ") curveError = " << curveError->GetName() << endl ;
  if (!curveError) {
    cout << "Util::makePdfErrorRatioHist(" << frame->GetName() << ") cannot find curve" << endl ;
    return 0 ;
  }

  // cout << " curveError->GetN() = " << curveError->GetN() << endl;

  RooCurve* ratioBand = new RooCurve ;
  ratioBand->SetName(Form("%s_ratio_errorband",curveNom->GetName())) ;
  ratioBand->SetLineWidth(1) ;
  ratioBand->SetLineColor(kBlue-5);
  ratioBand->SetFillColor(kBlue-5);
  ratioBand->SetFillStyle(3004);
  
  Int_t j = 0;
  Bool_t bottomCurve = kFALSE;
  for(Int_t i=1; i<curveError->GetN()-1; i++){
    Double_t x,y;
    curveError->GetPoint(i,x,y) ;
    //  cout << "  Error   i = " << i << "  x = " << x << " y = " << y << endl;
    
    // errorBand curve has twice as many points as does a normal (pdf) curve
    // first it walk through all +1 sigma points (topCurve), then the -1 sigma points (bottomCurve)
    // so to divide the errorCurve by the pdfCurve, we need to count back for the pdfCurve once we're in the middle of errorCurve
    if( i >= (curveNom->GetN()-1) ) bottomCurve = kTRUE;
    
    Double_t xNom = x;
    Double_t yNom = y;
    
    // each errorCurve has two more points just outside the plot, so we need to treat them separately
    if( i == (curveNom->GetN() - 1) ||  i == curveNom->GetN() ){
      xNom = x;
      yNom = 1.;
      //   cout << "   Special Error Nom j = " << j << " xNom = " << xNom << " yNom = " << yNom << endl;
      ratioBand->addPoint(x, (y - yNom) / y + 1.);
      continue;
    }


    if( bottomCurve){
      curveNom->GetPoint(j,xNom,yNom);
      //  cout << "     Error Nom j = " << j << " xNom = " << xNom << " yNom = " << yNom << endl;
      j--;
    } else {
      j++;
      curveNom->GetPoint(j,xNom,yNom);
      //  cout << "     Error Nom j = " << j << " xNom = " << xNom << " yNom = " << yNom << endl;
    }
    
    // only divide by yNom if it is non-zero
     if(  fabs(yNom) > 0.00001 ){ 
      ratioBand->addPoint(x, (y - yNom) / yNom + 1.);  
      //     cout << endl << " RATIOBAND:   regionvar = " << regionVar->GetName() << " x = " << x << " y = " << y << " ynom = " << yNom 
      // 	   << "   y-yNom = " << (y-yNom) << "  (y-yNom)/yNom = " <<  (y-yNom)/yNom << " (+1) =  " << ( (y-yNom)/yNom +1.)<< endl;
    }
    else { 
      ratioBand->addPoint(x, (y - yNom));       
      // cout << endl << endl << "   XXX   else  y =  " << y <<  " xNom = " << xNom << " yNom = " << yNom << "   y-yNom = " << (y-yNom) << endl; 
    }
  }
    
  return ratioBand;
}



//_____________________________________________________________________________
void Util::SetPdfParError(RooWorkspace* w, RooAbsPdf* regionPdf, double Nsigma){

  RooStats::ModelConfig* mc  = Util::GetModelConfig(w);
  if (mc==0) return;

  const RooArgSet* obsSet = mc->GetObservables();
  if (obsSet==0) return;

  RooAbsPdf* pdf = mc->GetPdf();
  if (pdf==0) return;

  RooArgList floatParList = Util::getFloatParList( *pdf, *obsSet );
 
  TIterator* iter = floatParList.createIterator() ;
  RooAbsArg* arg ;
  while( (arg=(RooAbsArg*)iter->Next()) ) {
    
    TString parName;
    if(arg->InheritsFrom("RooRealVar") && !arg->isConstant()){
      parName = arg->GetName();
    } else { continue; }
   
    RooRealVar* par = (RooRealVar*) w->var(parName.Data());
    
    Double_t cenVal = par->getVal();
    Double_t errVal = par->getError();
    // cout << " par = " << parName << " val(before) = " << cenVal << endl;
    par->setVal(cenVal + Nsigma * errVal);
    // cout << " par = " << parName << " val(after) = " << par->getVal() << endl;
    
  }
}





//_____________________________________________________________________________
TString Util::GetXTitle(RooRealVar* regionVar){

  TString varName = regionVar->GetName();
  TString outName = varName;
  
  if( varName.Contains("met")) outName = "E_{T}^{miss} [GeV]"; 
  else if(  varName.Contains("mt")) outName = "m_{T} [GeV]"; 
  else if(  varName.Contains("meff")) outName = "m_{eff} [GeV]"; 
  else if(  varName.Contains("nJet")) outName = "N jets"; 
  else if( varName.Contains("met/meff")) outName = "E_{T}^{miss}/m_{eff}"; 
  
  return outName;
}


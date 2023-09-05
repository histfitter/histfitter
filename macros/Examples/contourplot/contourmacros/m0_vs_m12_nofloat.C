/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Macro  : m0_vs_m12_nofloat.C                                                   *
 * Created: 12 June 2012                                                          *
 *                                                                                *
 * Description:                                                                   *
 *      make contour histograms based on the list text files produced by          *
 *      makelistfiles - underlying macro                                          *                              
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/

#include "CombinationGlob.C"
#include "TROOT.h"
#include "TColor.h"
#include "DrawUtils.h"
#include "StatTools.h"
#include "../summary_harvest_tree_description.h"
#include "TFile.h"

/**
Initialzing the macro: loading the description of the list text file from summary_harvest_tree_description.h
*/
void initialize() {
  //gROOT->ProcessLine(".L summary_harvest_tree_description.h+");
  gSystem->Load("libHistFitter.so");
}

/**
Convert the text lists into ROOT histograms by interpolating between the discrete points 
*/
const char*
m0_vs_m12_nofloat(const char* textfile = 0, TH2D* inputHist = 0, const char* rootfile = "m0m12_nofloat.root", TString id1="m0",TString id2="m12", int   nbinsX=21,int nbinsY=17, float minX=20,float maxX=860, float minY=92.5, float maxY=347.5)
{
   // set combination style and remove existing canvas'
   CombinationGlob::Initialize();

   initialize();

   // get the harvested tree
   TTree* tree = harvesttree( textfile!=0 ? textfile : 0 );
   if (tree==0) { 
     cout << "Cannot open list file. Exit." << endl;
     return "ERROR";
   }

   // store histograms to output file
   const char* outfile(0);
   if (textfile!=0) {
     TObjArray* arr = TString(textfile).Tokenize("/");
     TObjString* objstring = (TObjString*)arr->At( arr->GetEntries()-1 );
     outfile = Form("%s%s",objstring->GetString().Data(),".root");
     delete arr;
   } else {
     outfile = rootfile;
   }

   cout << "Histograms being written to : " << outfile << endl;
   TFile* output = TFile::Open(outfile,"RECREATE");
   output->cd();

   TH2D* hist;
   
   if (inputHist!=NULL){
     TH2D *clonehclPmin2=(TH2D*)inputHist->Clone();
     hist = DrawUtil::triwsmooth( tree, "p1:m12:m0", "hclPmin2" , "Observed CLsplusb", "p1>=0 && p1<=1", clonehclPmin2 );}
   else{
     hist = DrawUtil::triwsmooth( tree, "p1:m12:m0", "hclPmin2" , "Observed CLsplusb", "p1>=0 && p1<=1", inputHist);}


   if (hist!=0) {
     hist->Write();
     delete hist; hist=0;
   } else {
     cout << "Cannot make smoothed significance histogram. Exit." << endl;
   }


   TH2D* sigp1;

   if (inputHist!=NULL){
     TH2D *clonesigp1=(TH2D*)inputHist->Clone();
     sigp1 = DrawUtil::triwsmooth( tree, "StatTools::GetSigma(p1):m12:m0", "sigp1" , "One-sided significance of CLsplusb", "(p1>0 && p1<=1)", clonesigp1 );}
   else{
     sigp1 = DrawUtil::triwsmooth( tree, "StatTools::GetSigma(p1):m12:m0", "sigp1" , "One-sided significance of CLsplusb", "(p1>0 && p1<=1)", inputHist );}

   if (sigp1!=0) {
     sigp1->Write();
     delete sigp1; sigp1=0;
   } else {
     cout << "Cannot make smoothed significance histogram. Exit." << endl;
   }

   ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

   // cls:clsexp:clsu1s:clsd1s

   TH2D* p1clsf;

   if (inputHist!=NULL){
     TH2D *clonep1clsf=(TH2D*)inputHist->Clone();
     p1clsf = DrawUtil::triwsmooth( tree, "CLs:m12:m0", "sigp1clsf" , "Observed CLs", "p1>0 && p1<=1", clonep1clsf );}
   else{
     p1clsf = DrawUtil::triwsmooth( tree, "CLs:m12:m0", "sigp1clsf" , "Observed CLs", "p1>0 && p1<=1", inputHist );
   }


   if (p1clsf!=0) {
     p1clsf->Write();
     delete p1clsf; p1clsf=0;
   } else {
     cout << "Cannot make smoothed significance histogram. Exit." << endl;
   }

   TH2D* sigp1clsf;

   if (inputHist!=NULL){
     TH2D *clonesigp1clsf=(TH2D*)inputHist->Clone();
     sigp1clsf = DrawUtil::triwsmooth( tree, "StatTools::GetSigma( CLs ):m12:m0", "sigp1clsf" , "One-sided significalce of observed CLs", "p1>0 && p1<=1",clonesigp1clsf );}
   else{
     sigp1clsf = DrawUtil::triwsmooth( tree, "StatTools::GetSigma( CLs ):m12:m0", "sigp1clsf" , "One-sided significalce of observed CLs", "p1>0 && p1<=1", inputHist );}


   if (sigp1clsf!=0) {
     sigp1clsf->Write();
     delete sigp1clsf; sigp1clsf=0;
   } else {
     cout << "Cannot make smoothed significance histogram. Exit." << endl;
   }

   TH2D* sigp1expclsf;

   if (inputHist!=NULL){
     TH2D *clonesigp1expclsf=(TH2D*)inputHist->Clone();
     sigp1expclsf = DrawUtil::triwsmooth( tree, "StatTools::GetSigma( CLsexp ):m12:m0", "sigp1expclsf" , "One-sided significalce of expected CLs", "p1>0 && p1<=1", clonesigp1expclsf );}
   else{
     sigp1expclsf = DrawUtil::triwsmooth( tree, "StatTools::GetSigma( CLsexp ):m12:m0", "sigp1expclsf" , "One-sided significalce of expected CLs", "p1>0 && p1<=1", inputHist );}
   

   if (sigp1expclsf!=0) {
     sigp1expclsf->Write();
     delete sigp1expclsf; sigp1expclsf=0;
   } else {
     cout << "Cannot make smoothed significance histogram. Exit." << endl;
   }

   TH2D* sigclsu1s;

   if (inputHist!=NULL){
     TH2D *clonesigclsu1s=(TH2D*)inputHist->Clone();
     sigclsu1s = DrawUtil::triwsmooth( tree, "StatTools::GetSigma(clsu1s):m12:m0", "sigclsu1s" , "One-sided significalce of expected CLs (+1 sigma)", "clsu1s>0", clonesigclsu1s );}
   else{
     sigclsu1s = DrawUtil::triwsmooth( tree, "StatTools::GetSigma(clsu1s):m12:m0", "sigclsu1s" , "One-sided significalce of expected CLs (+1 sigma)", "clsu1s>0", inputHist );}

   if (sigclsu1s!=0) {
     sigclsu1s->Write();
     delete sigclsu1s; sigclsu1s=0;
   } else {
     cout << "Cannot make smoothed significance histogram. Exit." << endl;
   }

  TH2D* sigclsd1s;

  if (inputHist!=NULL){
     TH2D *clonesigclsd1s=(TH2D*)inputHist->Clone();
     sigclsd1s = DrawUtil::triwsmooth( tree , "StatTools::GetSigma(clsd1s):m12:m0", "sigclsd1s" , "One-sided significalce of expected CLs (-1 sigma)", "clsd1s>0",clonesigclsd1s );}
   else{
     sigclsd1s = DrawUtil::triwsmooth( tree, "StatTools::GetSigma(clsd1s):m12:m0", "sigclsd1s" , "One-sided significalce of expected CLs (-1 sigma)", "clsd1s>0", inputHist );}
   if (sigclsd1s!=0) {
     sigclsd1s->Write();
     delete sigclsd1s; sigclsd1s=0;
   } else {
     cout << "Cannot make smoothed significance histogram. Exit." << endl;
   }


   ///////////////////////////////////////////////////// upper limit * cross section plots

  TH2D* UpperLimit;

  if (inputHist!=NULL){
     TH2D *cloneupperlimit=(TH2D*)inputHist->Clone();
     UpperLimit = DrawUtil::triwsmooth( tree, "upperLimit:m12:m0", "upperLimit" , "upperlimit","1", cloneupperlimit);}
   else{
     UpperLimit = DrawUtil::triwsmooth( tree, "upperLimit:m12:m0", "upperLimit" , "upperlimit","1", inputHist);}


   if (UpperLimit!=0) {
     UpperLimit->Write();
     delete UpperLimit; UpperLimit=0;
   } else {
     cout << "Cannot make smoothed significance histogram. Exit." << endl;
   }


  TH2D* xsec;

  if (inputHist!=NULL){
     TH2D *clonexsec=(TH2D*)inputHist->Clone();
     xsec = DrawUtil::triwsmooth( tree, "xsec:m12:m0", "xsec" , "xsec","1", clonexsec);}   
   else{
     xsec = DrawUtil::triwsmooth( tree, "xsec:m12:m0", "xsec" , "xsec","1", inputHist);}


   if (xsec!=0) {
     xsec->Write();
     delete xsec; xsec=0;
   } else {
     cout << "Cannot make smoothed significance histogram. Exit." << endl;
   }

  TH2D* excludedXsec;
   
  if (inputHist!=NULL){
     TH2D *cloneexcludedXsec=(TH2D*)inputHist->Clone();
     excludedXsec = DrawUtil::triwsmooth( tree, "excludedXsec:m12:m0", "excludedXsec" , "excludedXsec","1", cloneexcludedXsec);}
   else{
     excludedXsec = DrawUtil::triwsmooth( tree, "excludedXsec:m12:m0", "excludedXsec" , "excludedXsec","1", inputHist);}


   if (excludedXsec!=0) {
     excludedXsec->Write();
     delete excludedXsec; excludedXsec=0;
   } else {
     cout << "Cannot make smoothed significance histogram. Exit." << endl;
   }


   ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

   output->Close();
   //if (output!=0) { delete output; output=0; }
   cout << "Done." << endl;

   return outfile;
}


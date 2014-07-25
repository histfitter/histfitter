// vim: ts=4:sw=4
/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Namespace: DrawUtil                                                            *
 *                                                                                *
 * Description:                                                                   *
 *      Implementation (see header for description)                               *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva, Switzerland                               *
 *                                                                                *
 * See corresponding .h file for author and license information                   *
 **********************************************************************************/

#include "DrawUtils.h"
#include "TMsgLogger.h"

#include <iostream>
#include "TH2D.h"
#include "TTree.h"
#include "TBranch.h"
#include "TGraph2D.h"
#include "TString.h"

using namespace std;


namespace DrawUtil {
    static TMsgLogger DrawUtilLogger("DrawUtil");
}


//________________________________________________________________________________________________
TH2D* DrawUtil::triwsmooth( TTree* tree, const char* varstr, const char* name, const char* title, const char* cutstr, TH2D* inputHist){
    if (tree==NULL) 
        return 0;

    int ntotal = tree->GetEntries("1");
    int nselect = tree->GetEntries(cutstr);

    DrawUtilLogger << kINFO << "Plotting " << varstr << " with selection " << cutstr << "." << GEndl; 
    DrawUtilLogger << kINFO << "Selected " << nselect << " out of " << ntotal << " entries. Fraction = " << double(nselect)/ntotal << GEndl;

    // Wacky workaround to prevent segfault in tree->Draw() below.
    TString buh("");
    bool goff = buh.Contains("goff");
    // prevent compiler warning about goff not used:
    goff=goff*goff;

    tree->Draw(varstr,cutstr,"goff");
    Long64_t  nrows = tree->GetSelectedRows();
    Double_t *v1 =  tree->GetV1();
    Double_t *v2 = tree->GetV2();
    Double_t *v3 = tree->GetV3();

    if (nselect == 0) 
        return 0;

    TGraph2D* gr = new TGraph2D( nrows, v3, v2, v1 );

    gr->SetName(name!=0 ? TString(name)+"gr" : "graph2d");
    gr->SetTitle(title!=0 ? TString(title)+"gr" : TString(varstr) + " drawn TRIW");
    gr->Draw("TRIW");

    if (inputHist!=NULL){
        gr->SetHistogram(inputHist);
    }

    TH2D* foo = gr->GetHistogram();
    TH2D* hist = (TH2D*)foo->Clone();

    /// for some reason this doesn't work in cint?
    hist->SetName(  name!=0 ? name : "hist" );
    hist->SetTitle( title!=0 ? title : "hist title" );
    delete gr; gr=0;

    return hist; // note: caller owns histogram
}


//________________________________________________________________________________________________
TH2F* DrawUtil::makesignificancehistos( TTree* tree, int mode,TString id1,TString id2,int   nbinsX,int nbinsY, float minX,float maxX, float minY, float maxY) {
    if (tree == NULL) 
        return 0;
    
    if (mode<0 || mode>2) 
        return 0;

    Float_t         m0;
    Float_t         m12;
    Float_t         p1;
    Float_t         p0;
    Float_t         sig;
    Float_t         bkg;

    TBranch         *b_m0;   //!
    TBranch         *b_m12;  //!
    TBranch         *b_p1;   //!
    TBranch         *b_p0;   //!
    TBranch         *b_sig;  //!
    TBranch         *b_bkg;  //!

    tree->SetBranchAddress(id1,  &m0,  &b_m0);
    tree->SetBranchAddress(id2, &m12, &b_m12);
    tree->SetBranchAddress("p1",  &p1,  &b_p1);
    tree->SetBranchAddress("p0",  &p0,  &b_p0);
    tree->SetBranchAddress("sig", &sig, &b_sig);
    tree->SetBranchAddress("bkg", &bkg, &b_bkg);

    TString bulkName = "SUSY_"+id1+"_vs_"+id2+"_Scan";

    TH2F* hclPmin(0);
    if (mode==0)   hclPmin   = new TH2F("hclPmin"     , bulkName + TString(" (1 - CL)"),    nbinsX, minX, maxX, nbinsY, minY, maxY );
    TH2F* hsigPmin(0);
    if (mode==1)   hsigPmin  = new TH2F("hsigPmin"    , bulkName + TString("sig"), nbinsX, minX, maxX, nbinsY, minY, maxY );
    TH2F* hbkgPmin(0);
    if (mode==2)   hbkgPmin  = new TH2F("hbkgPmin"    , bulkName + TString("bkg"), nbinsX, minX, maxX, nbinsY, minY, maxY );

    // then: fill histograms
    for( Int_t i = 0; i < tree->GetEntries(); i++ ){
        tree->GetEntry( i );
        //cout << " m0=" << m0 << " m12=" << m12 << " p1=" << p1 << GEndl;
        if (mode==0) { hclPmin->Fill( m0, m12, p1 ); }
        if (mode==1) { hsigPmin->Fill( m0, m12, sig ); }
        if (mode==2) { hbkgPmin->Fill( m0, m12, bkg ); }
    }

    DrawUtilLogger << kINFO << "done filling bkg" << GEndl;

    if (mode==0)  return hclPmin;
    if (mode==1)  return hsigPmin;
    if (mode==2)  return hbkgPmin;
    else return 0;
}


//________________________________________________________________________________________________
TH2F* DrawUtil::linearsmooth(const TH2& hist, const char* name, const char* title) {
    int nbinsx = hist.GetNbinsX();
    int nbinsy = hist.GetNbinsY();

    double xbinwidth = ( hist.GetXaxis()->GetBinCenter(nbinsx) - hist.GetXaxis()->GetBinCenter(1) ) / double(nbinsx-1);
    double ybinwidth = ( hist.GetYaxis()->GetBinCenter(nbinsy) - hist.GetYaxis()->GetBinCenter(1) ) / double(nbinsy-1);

    int nbinsxsm = 2*nbinsx - 1 ;
    int nbinsysm = 2*nbinsy - 1 ;

    double xmin = hist.GetXaxis()->GetBinCenter(1) - xbinwidth/4. ;
    double xmax = hist.GetXaxis()->GetBinCenter(nbinsx) + xbinwidth/4. ;
    double ymin = hist.GetYaxis()->GetBinCenter(1) - ybinwidth/4. ;
    double ymax = hist.GetYaxis()->GetBinCenter(nbinsy) + ybinwidth/4. ;

    TH2F* hist2 = new TH2F(name, title, nbinsxsm, xmin, xmax, nbinsysm, ymin, ymax);

    for (Int_t ibin1=1; ibin1 < hist.GetNbinsX(); ibin1++) {
        for (Int_t ibin2=1; ibin2 < hist.GetNbinsY(); ibin2++) {
            float f00 = hist.GetBinContent(ibin1,ibin2);
            float f10 = hist.GetBinContent(ibin1+1,ibin2);
            float f01 = hist.GetBinContent(ibin1,ibin2+1);
            float f11 = hist.GetBinContent(ibin1+1,ibin2+1);

            for (Int_t i=0; i<=2; ++i)
                for (Int_t j=0; j<=2; ++j) {
                    float x = i*0.5; float y = j*0.5;
                    float val = (1-x)*(1-y)*f00 + x*(1-y)*f10 + (1-x)*y*f01 + x*y*f11 ;
                    Int_t jbin1 = 2*ibin1 - 1 + i;
                    Int_t jbin2 = 2*ibin2 - 1 + j;
                    hist2->SetBinContent(jbin1,jbin2,val);
                }
        }
    }

    return hist2; // caller owns histogram
}


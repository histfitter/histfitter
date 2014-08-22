// vim: ts=4:sw=4
/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Namespace: -                                                                   *
 *                                                                                *
 * Description:                                                                   *
 *      Implementation (see header for description)                               *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva, Switzerland                               *
 *                                                                                *
 * See corresponding .h file for author and license information                   *
 **********************************************************************************/

#include "toy_utils.h"
#include "CombineWorkSpaces.h"
#include "Significance.h"
#include "Utils.h"
#include "StatTools.h"
#include "TMsgLogger.h"
#include "RooStats/HypoTestInverterResult.h"

#include "TTree.h"
#include "TFile.h"
#include "TMath.h"
#include "TSystem.h"
#include "TObjString.h"
#include "RooRandom.h"
#include <sstream>
#include <math.h>
#include <iostream>
#include <fstream>
#include "RooStats/ModelConfig.h"
#include "RooMsgService.h"
#include "RooRandom.h"
#include "RooFitResult.h"
#include "RooAbsData.h"
#include "RooDataSet.h"
#include "RooProdPdf.h"
#include "RooRealVar.h"
#include "RooMCStudy.h"

#include <stdlib.h>

#include "RooAddition.h"

#include <stdexcept>

using namespace std;
using namespace RooFit;
using namespace RooStats;

/////////////////////////////////////////////////////////////////////////////////////////////////////////
/// Code to collect hypotest results and write to text files
/////////////////////////////////////////////////////////////////////////////////////////////////////////
static TMsgLogger ToyUtilsLogger("toy_utils");


//________________________________________________________________________________________________
const char* CollectAndWriteHypoTestResults( const TString& infile, const TString& format, const TString& interpretation, const TString& cutStr, const bool rejectFailedPrefit, const TString& outDir, const TString& fileprefix  ){
    // outdir
    TString outdir = gSystem->pwd();
    if ( !gSystem->cd( outDir.Data() ) ) {
        ToyUtilsLogger << kERROR << "output dir <" << outDir << "> does not exist. Return." << GEndl;
        return 0;
    } else {
        TString fulloutdir = gSystem->pwd();
        gSystem->cd( outdir.Data() ); // back to original dir
        outdir = fulloutdir;
    }
    outdir = ( outdir.EndsWith("/") ? outdir : outdir+"/" );

    // construct workspace and output file names
    TString cutstr = "_" + cutStr;
    cutstr = cutstr.ReplaceAll(" ","_");
    cutstr = cutstr.ReplaceAll(">","G");
    cutstr = cutstr.ReplaceAll("<","L");
    cutstr = cutstr.ReplaceAll("=","E");
    cutstr = cutstr.ReplaceAll("&","A");
    cutstr = cutstr.ReplaceAll("|","O");
    cutstr = cutstr.ReplaceAll("!","N");

    //int seed = RooRandom::randomGenerator()->GetSeed();
    TString confStr; // = Form("_mode%d_nexp%d_2par%d_doUL%d_seed%d",mode,n_toys,in_doFreeFitFirst,do_ul,seed);

    TObjArray* jArr = infile.Tokenize("/");
    TString listname = ((TObjString*)jArr->At(jArr->GetEntries()-1))->GetString();
    delete jArr;
    listname = listname.ReplaceAll(".root","");

    TString prefix = fileprefix;
    if (!prefix.BeginsWith("_")) prefix = "_" + prefix;

    // list file name
    listname = listname + confStr + prefix + cutstr;
    TString rootoutfilestub = outdir + listname;

    // collect p-values, store rootfile if needed
    std::list<LimitResult> summary = CollectHypoTestResults( infile, format, interpretation, cutStr, rejectFailedPrefit ); 

    // store harvest in text file
    return WriteResultSet( summary, listname, outdir );
}


//________________________________________________________________________________________________
std::list<LimitResult> CollectHypoTestResults( const TString& infile, const TString& format, const TString& interpretation, 
        const TString& cutStr, const bool& rejectFailedPrefit ) 
{
    std::list<LimitResult> limres;
    if ( infile.IsNull() || format.IsNull() || interpretation.IsNull() ) 
        return limres;

    // collect all hypotest results in input file
    std::map<TString,TString> wsnameMap = GetMatchingWorkspaces( infile, format, interpretation, cutStr );
    if ( wsnameMap.empty() ) 
        return limres;

    // loop over hypotestresults and save results
    std::list<LimitResult> limitres;
    std::map<TString,TString>::iterator itr=wsnameMap.begin(), end=wsnameMap.end();

    int counter_failed_fits = 0;
    int counter_failed_status = 0;
    int counter_not_great_fits = 0;
    int counter_badcovquality = 0;
    int counter_probably_bad_fit = 0;

    RooStats::HypoTestInverterResult *ht = NULL; 
    RooFitResult *fitresult = NULL;

    for (; itr!=end; ++itr) {
        ht = GetHypoTestResultFromFile( infile, itr->second );

        if(!ht) { continue; }
        if(ht->ArraySize()==0) {
            ToyUtilsLogger << kWARNING << "Fit result " << ht->GetName()
                << " has failed HypoTestInverterResult - cannot use result. Skip." << GEndl;
            delete ht; ht=NULL;
            continue;
        } 

        //Check fit result
        TString fitresultname = TString(ht->GetName());
        fitresultname.ReplaceAll("hypo_discovery_","fitTo_");
        fitresultname.ReplaceAll("hypo_","fitTo_");
        //fitresultname.ReplaceAll("hypo_","hypo_");
        //cout << "Check fit result " << fitresultname << GEndl;
        fitresult = GetFitResultFromFile(infile, fitresultname);

        ToyUtilsLogger << kINFO << "At fit point " << fitresultname.Data() << GEndl;

        bool nofit = false;
        if (fitresult == NULL) { nofit = true; }

        bool failed_status = false;
        if (fitresult && fitresult->status()!=0) {
            ToyUtilsLogger << kWARNING << "Fit failed for point " << fitresultname.Data() << ". Result has been flagged as failed fit." << GEndl;
            counter_failed_status++;
            failed_status = true;   
        }

        int fitstatus = -1;
        if (fitresult) {
            fitstatus = fitresult->status() ;
        }

        bool failed_cov = false;
        bool dodgy_cov = false;
        if (fitresult && fitresult->covQual() < 1.1) {
            ToyUtilsLogger << kWARNING << "Fit result " << fitresultname.Data() 
                << " has bad covariance matrix quality! Result has been flagged as failed fit." << GEndl;
            counter_badcovquality++;
            //failed_fit = true;
            failed_cov = true;
        } else if (fitresult && fitresult->covQual() < 2.1) {
            ToyUtilsLogger << kWARNING << "Fit result " << fitresultname.Data() 
                << " has mediocre covariance matrix quality. Result has been flagged as failed cov matrix." << GEndl;
            counter_not_great_fits++;
            //failed_cov = true;
            dodgy_cov = true;
        }
        int covqual = ( fitresult!=0 ? fitresult->covQual() : -1 );

        bool failed_fit = ( failed_status || failed_cov || dodgy_cov );
        if(failed_fit) counter_failed_fits++;

        // don't store points with failed fits, if configured so.
        if (rejectFailedPrefit && failed_fit) {
            if(ht) { delete ht; ht=NULL; }
            if(fitresult) { delete fitresult; fitresult=NULL; }
            continue;
        }

        bool failed_p0half = false;
        LimitResult result = RooStats::get_Pvalue( ht );
        // MB Keeping points for now, this also rejects bad fits.
        if (fabs(result.GetP0()-0.5) < 0.0001 && result.GetSigma0() < 0.0001){
            //counter_probably_bad_fit++;
            ToyUtilsLogger << kINFO << "One of the base fits _may_ have failed for point (or may not): " 
                << fitresultname.Data() << " : " << result.GetP0() << " " << result.GetSigma0() << " Flagged as p0=0.5." << GEndl;
            //failed_fit = true;
            failed_p0half = true;
        }

        std::map<TString,float> failMap;
        failMap["nofit"]        = float(nofit);
        failMap["failedstatus"] = float(failed_status);
        failMap["fitstatus"]    = float(fitstatus);
        failMap["failedcov"]    = float(failed_cov);
        failMap["dodgycov"]     = float(dodgy_cov);
        failMap["covqual"]      = float(covqual);
        failMap["failedfit"]    = float(failed_fit);

        failMap["failedp0"]     = float(failed_p0half);

        result.AddMetaData ( ParseWorkspaceID(itr->first) );
        result.AddMetaData ( failMap );

        // store info from interpretation string (eg m0 and m12 value) 
        limres.push_back(result); 

        if(ht){ delete ht; ht=NULL; }
        if(fitresult) { delete fitresult; fitresult=NULL; }
    }

    ToyUtilsLogger << kINFO << counter_failed_status << " failed fit status and " << counter_badcovquality 
        << " fit(s) with bad covariance matrix quality were counted" << GEndl;
    ToyUtilsLogger << kINFO << counter_probably_bad_fit << " fit(s) with a bad p-value and " << counter_not_great_fits 
        << " fit(s) with mediocre covariance matrix quality were counted" << GEndl;
    ToyUtilsLogger << kINFO << "All but the ones with mediocre covariance matrix quality were rejected from the final results list." << GEndl;
    ToyUtilsLogger << kINFO << counter_failed_fits << " failed fit(s)" << GEndl;

    return limres;
}


//________________________________________________________________________________________________
const char* WriteResultSet( const std::list<LimitResult>& summary, const TString& listname, const TString& outDir ){
    if (summary.empty()) 
        return 0;

    ToyUtilsLogger << kINFO << "Storing results of " << summary.size() << " scan points." << GEndl;

    TString outdir = gSystem->pwd(); 
    if ( !gSystem->cd( outDir.Data() ) ) {
        ToyUtilsLogger << kERROR << "output dir <" << outDir << "> does not exist. Return." << GEndl;
        return 0;
    } else {
        TString fulloutdir = gSystem->pwd();
        gSystem->cd( outdir.Data() ); // back to original dir
        outdir = fulloutdir;
    }
    outdir = ( outdir.EndsWith("/") ? outdir : outdir+"/" );

    std::list<LimitResult>::const_iterator itr=summary.begin(), end=summary.end();

    TString outfile = outdir + listname + "_harvest_list" ;
    TString outdesc = outdir + "summary_harvest_tree_description.h" ;
    TString outdescp= outdir + "summary_harvest_tree_description.py" ;

    TString includes, harvesttree, writetree, mymain, pythonstr;

    /// generate c-macro code
    includes     = "\n#include \"TTree.h\"\n";
    includes    += "#include \"TFile.h\"\n";
    includes    += "#include <iostream>\n";
    includes    += "using namespace std;\n";

    harvesttree  = "\nTTree* harvesttree(const char* textfile=0) {\n";
    harvesttree += "  const char* filename    = \"" + outfile + "\";\n";
    harvesttree += "  const char* description = \"" + itr->GetDescriptionString() + "\";\n";
    harvesttree += "  TTree* tree = new TTree(\"tree\",\"data from ascii file\");\n";
    harvesttree += "  Long64_t nlines(0);\n";
    harvesttree += "  if (textfile!=0) {\n";
    harvesttree += "    nlines = tree->ReadFile(textfile,description);\n";
    harvesttree += "  } else if (filename!=0) {\n";
    harvesttree += "    nlines = tree->ReadFile(filename,description);\n";
    harvesttree += "  } else {\n";
    harvesttree += "    cout << \"WARNING: file name is empty. No tree is read.\" << endl;\n";
    harvesttree += "  }\n";
    harvesttree += "  tree->SetMarkerStyle(8);\n";
    harvesttree += "  tree->SetMarkerSize(0.5);\n";
    harvesttree += "  return tree;\n";
    harvesttree += "}\n";

    writetree    = "\nvoid writetree() {\n";
    writetree   += "  TTree* tree = (TTree *)gDirectory->Get(\"tree\");\n";
    writetree   += "  if (tree==0) {\n";
    writetree   += "    tree = harvesttree();\n";
    writetree   += "    if (tree==0) return;\n";
    writetree   += "  }\n";
    writetree   += "  TFile* file = TFile::Open(\"" + outfile + ".root" + "\",\"RECREATE\");\n";
    writetree   += "  file->cd();\n";
    writetree   += "  tree->Write();\n";
    writetree   += "  file->Close();\n";
    writetree   += "}\n";

    mymain  = "\nvoid summary_harvest_tree_description() {\n"; 
    mymain += "  TTree* tree = harvesttree();\n";
    mymain += "  gDirectory->Add(tree);\n";
    mymain += "}\n";

    /// generate python code
    pythonstr  = "#!/usr/bin/env python\n\n";
    pythonstr += "import os, sys, ROOT\n";
    pythonstr += "from ROOT import TTree, TString\n\n";
    pythonstr += "def treedescription():\n";
    pythonstr += "  filename = '" + outfile + "'\n";
    pythonstr += "  description = \"" + itr->GetDescriptionString() + "\"\n";
    pythonstr += "  return filename, description\n\n";
    pythonstr += "def harvesttree(textfile=''):\n";
    pythonstr += "  filename, description=treedescription()\n";
    pythonstr += "  tree = TTree('tree','data from ascii file')\n";
    pythonstr += "  if len(textfile)>0:\n";
    pythonstr += "    nlines = tree.ReadFile(textfile,description)\n";
    pythonstr += "  elif len(filename)>0:\n";
    pythonstr += "    nlines = tree.ReadFile(filename,description)\n";
    pythonstr += "  else:\n";
    pythonstr += "    print 'WARNING: file name is empty. No tree is read.'\n\n";
    pythonstr += "  tree.SetMarkerStyle(8)\n";
    pythonstr += "  tree.SetMarkerSize(0.5)\n\n";
    pythonstr += "  return tree\n\n";

    // write out files
    ofstream fout;

    // tree description
    fout.open(outdesc);
    if (!fout.is_open()) {
        ToyUtilsLogger << kERROR << "Error opening file <" << outdesc <<">" << GEndl;
        return 0;
    }
    fout << includes << "\n";
    fout << harvesttree << "\n";
    fout << writetree << "\n";
    fout << mymain << "\n";
    fout.close();

    // tree description python
    fout.open(outdescp);
    if (!fout.is_open()) {
        ToyUtilsLogger << kERROR << "Error opening file <" << outdescp <<">" << GEndl;
        return 0;
    }
    fout << pythonstr << "\n";
    fout.close();

    // data for tree
    fout.open(outfile.Data());
    if (!fout.is_open()) {
        ToyUtilsLogger << kERROR << "Error opening file <" << outfile <<">" << GEndl;
        return 0;
    }
    for(; itr!=end; ++itr) { fout << itr->GetSummaryString() << "\n"; }
    fout.close();

    ToyUtilsLogger << kINFO << "list file stored as <" << outfile << ">" << GEndl;

    return outfile.Data();
}


/// Same code, but takes workspaces as input from which p-values are evaluated, then stored
//________________________________________________________________________________________________
const char* CollectAndWriteResultSet( const TString& infile, const TString& format, const TString& interpretation, const TString& cutStr, const int& mode, const int& n_toys, const int& in_doFreeFitFirst, const int& do_ul, const TString& outDir, const TString& fileprefix ) {
    // outdir
    TString outdir = gSystem->pwd();
    if ( !gSystem->cd( outDir.Data() ) ) {
        ToyUtilsLogger << kERROR << "output dir <" << outDir << "> does not exist. Return." << GEndl;
        return 0;
    } else {
        TString fulloutdir = gSystem->pwd();
        gSystem->cd( outdir.Data() ); // back to original dir
        outdir = fulloutdir;
    }
    outdir = ( outdir.EndsWith("/") ? outdir : outdir+"/" );

    // construct workspace and output file names
    TString cutstr = "_" + cutStr;
    cutstr = cutstr.ReplaceAll(" ","_");
    cutstr = cutstr.ReplaceAll(">","G");
    cutstr = cutstr.ReplaceAll("<","L");
    cutstr = cutstr.ReplaceAll("=","E");
    cutstr = cutstr.ReplaceAll("&","A");
    cutstr = cutstr.ReplaceAll("|","O");
    cutstr = cutstr.ReplaceAll("!","N");

    int seed = RooRandom::randomGenerator()->GetSeed();
    TString confStr = Form("_mode%d_nexp%d_2par%d_doUL%d_seed%d",mode,n_toys,in_doFreeFitFirst,do_ul,seed);

    TObjArray* jArr = infile.Tokenize("/");
    TString listname = ((TObjString*)jArr->At(jArr->GetEntries()-1))->GetString();
    delete jArr;
    listname = listname.ReplaceAll(".root","");

    TString prefix = fileprefix;
    if (!prefix.BeginsWith("_")) prefix = "_" + prefix;

    // list file name
    listname = listname + confStr + prefix + cutstr;
    TString rootoutfilestub = outdir + listname;

    // collect p-values, store rootfile if needed
    std::list<LimitResult> summary = CollectLimitResults( infile, format, interpretation, cutStr, mode, n_toys, do_ul ); 

    // store harvest in text file
    return WriteResultSet( summary, listname, outdir );
}


//________________________________________________________________________________________________
std::list<LimitResult> CollectLimitResults( const TString& infile, const TString& format, const TString& interpretation, const TString& cutStr, const int& mode, const int& n_toys, const int& do_ul) {
    std::list<LimitResult> limres;
    if ( infile.IsNull() || format.IsNull() || interpretation.IsNull() ) 
        return limres;

    // classify all workspaces in input files
    std::map<TString,TString> wsnameMap = GetMatchingWorkspaces( infile, format, interpretation, cutStr );
    if ( wsnameMap.empty() ) 
        return limres;

    // loop over workspaces and print results
    std::list<LimitResult> limitres;
    std::map<TString,TString>::iterator itr=wsnameMap.begin(), end=wsnameMap.end();

    for (; itr!=end; ++itr) {
        RooWorkspace* w = GetWorkspaceFromFile( infile, itr->second );
        LimitResult result = get_Pvalue( w, mode, n_toys, do_ul, itr->first );
        limres.push_back(result);
        delete w;
    }

    return limres;
}


//________________________________________________________________________________________________
LimitResult get_Pvalue( RooWorkspace* w, const int& mode, const int& n_toys, const int& do_ul, const TString& wid ) {
    LimitResult result;

    bool doUL = bool(do_ul);

    TString wsname = w->GetName();

    switch ( mode ) {
        case 0: case 2:  // take dataset from workspace
            result = RooStats::get_Pvalue( w, doUL, n_toys, mode );
            break;
        default: // use dataset in workspace
            break;
    }

    result.SetMode(mode);
    result.AddMetaData ( ParseWorkspaceID(wid) );

    return result;
}

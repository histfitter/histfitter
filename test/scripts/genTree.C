#include "TFile.h"
#include "TTree.h"
#include "TRandom3.h"

/*
Generate TTree for testing
*/

void genTree(){

    // open file
    std::string outfileName = "test_tree.root";

    TFile *f = TFile::Open(outfileName.c_str(),"RECREATE");

    TRandom3 rnd(1000);

    double m = 0; //{50,100,150,200}
    double weight = 1;
    double sys_weight1 = 1;
    double sys_weight2 = 1;
    double sys_weight3 = 1;
    double sys_weight4 = 1;
    double sys_weight5 = 1;
    double sys_weight6 = 1;

    // Data tree
    TTree *data_tree = new TTree("data","data");
    data_tree->Branch("m", &m, "m/D");
    data_tree->Branch("weight", &weight, "weight/D");

    // Signal tree
    TTree *signal_tree = new TTree("signal","signal");
    signal_tree->Branch("m", &m, "m/D");
    signal_tree->Branch("weight", &weight, "weight/D");

    // Bkg1 tree (flat)
    TTree *bkg1_tree = new TTree("bkg1_nom","bkg1_nom");
    bkg1_tree->Branch("m", &m, "m/D");
    bkg1_tree->Branch("weight", &weight, "weight/D");
    bkg1_tree->Branch("sys_weight1", &sys_weight1, "sys_weight1/D");
    bkg1_tree->Branch("sys_weight2", &sys_weight2, "sys_weight2/D");
    bkg1_tree->Branch("sys_weight3", &sys_weight3, "sys_weight3/D");
    bkg1_tree->Branch("sys_weight4", &sys_weight4, "sys_weight4/D");
    bkg1_tree->Branch("sys_weight5", &sys_weight5, "sys_weight5/D");
    bkg1_tree->Branch("sys_weight6", &sys_weight6, "sys_weight6/D");

    // Bkg2 tree (falling)
    TTree *bkg2_nom_tree = new TTree("bkg2_nom","bkg2_nom");
    bkg2_nom_tree->Branch("m", &m, "m/D");
    bkg2_nom_tree->Branch("weight", &weight, "weight/D");
    bkg2_nom_tree->Branch("sys_weight1", &sys_weight1, "sys_weight1/D");
    bkg2_nom_tree->Branch("sys_weight2", &sys_weight2, "sys_weight2/D");
    bkg2_nom_tree->Branch("sys_weight3", &sys_weight3, "sys_weight3/D");
    bkg2_nom_tree->Branch("sys_weight4", &sys_weight4, "sys_weight4/D");
    bkg2_nom_tree->Branch("sys_weight5", &sys_weight5, "sys_weight5/D");
    bkg2_nom_tree->Branch("sys_weight6", &sys_weight6, "sys_weight6/D");

    TTree *bkg2_sys_tree = new TTree("bkg2_sys","bkg2_sys");
    bkg2_sys_tree->Branch("m", &m, "m/D");
    bkg2_sys_tree->Branch("weight", &weight, "weight/D");


    /////////////////////// Fill Trees //////////////
    // data
    weight = 1.;
    m = 75.;
    for (int i=0; i<105; i++){ data_tree->Fill(); }
    m = 125.;
    for (int i=0; i<15; i++){ data_tree->Fill(); }
    m = 175.;
    for (int i=0; i<6; i++){ data_tree->Fill(); }


    // signal
    m = 125.;
    weight = 1/5.;
    for (int i=0; i<5*2; i++)
    { 
        signal_tree->Fill(); 
    }
    m = 175.;
    for (int i=0; i<5*7; i++)
    { 
        signal_tree->Fill(); 
    }

    // bkg1
    double norm = 9./1000.;
    for (int i=0; i<1000.; i++)
    {
        weight = norm;
        m = rnd.Uniform(150)+50.;
        sys_weight1 = 1.03 + .05*(m-50.)/150.;
        sys_weight2 = 1.02 + .01*(m-50.)/150.;
        sys_weight3 = 1.01 + .02*(m-50.)/150.;
        sys_weight4 = 1.02 + .03*(m-50.)/150.;
        sys_weight5 = 1.03 + .04*(m-50.)/150.;
        sys_weight6 = 1.01 + .06*(m-50.)/150.;
        bkg1_tree->Fill();
    }

    // bkg2
    for (int i=0; i<3*(100-9); i++)
    { 
        weight = 1/3.;
        m = 75.;
        float r = rnd.Uniform(30) + 75.;
        sys_weight1 = 1.03 + .05*(m-75.)/30.;
        sys_weight2 = 1.02 + .01*(m-75.)/30.;
        sys_weight3 = 1.01 + .02*(m-75.)/30.;
        sys_weight4 = 1.02 + .03*(m-75.)/30.;
        sys_weight5 = 1.03 + .04*(m-75.)/30.;
        sys_weight6 = 1.01 + .06*(m-75.)/30.;
        bkg2_nom_tree->Fill(); 
        bkg2_sys_tree->Fill(); 
    }
    for (int i=0; i<3*(20-9); i++)
    { 
        weight = 1/3.;
        m = 125.;
        float r = rnd.Uniform(30) + 125.;
        sys_weight1 = 1.03 + .05*(m-125.)/30.;
        sys_weight2 = 1.02 + .01*(m-125.)/30.;
        sys_weight3 = 1.01 + .02*(m-125.)/30.;
        sys_weight4 = 1.02 + .03*(m-125.)/30.;
        sys_weight5 = 1.03 + .04*(m-125.)/30.;
        sys_weight6 = 1.01 + .06*(m-125.)/30.;
        bkg2_nom_tree->Fill(); 
        bkg2_sys_tree->Fill(); 
    }
    for (int i=0; i<3*(10-9); i++)
    { 
        weight = 1/3.;
        m = 175.;
        float r = rnd.Uniform(30) + 175.;
        sys_weight1 = 1.03 + .05*(m-175.)/30.;
        sys_weight2 = 1.02 + .01*(m-175.)/30.;
        sys_weight3 = 1.01 + .02*(m-175.)/30.;
        sys_weight4 = 1.02 + .03*(m-175.)/30.;
        sys_weight5 = 1.03 + .04*(m-175.)/30.;
        sys_weight6 = 1.01 + .06*(m-175.)/30.;
        bkg2_nom_tree->Fill(); 
        bkg2_sys_tree->Fill(); 
    }

    signal_tree->Write();
    data_tree->Write();
    bkg1_tree->Write();
    bkg2_nom_tree->Write();
    bkg2_sys_tree->Write();

    f->Close();
}
// vim: ts=4:sw=4
/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Class: HistogramPlotter                                                        *
 *                                                                                *
 * Description:                                                                   *
 *      Implementation (see header for description)                               *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva, Switzerland                               *
 *                                                                                *
 * See corresponding .h file for author and license information                   *
 **********************************************************************************/

#include <memory>

#include "HistogramPlotter.h"
#include "Utils.h"
#include "ConfigMgr.h"
#include "TMsgLogger.h"
#include "ChannelStyle.h"

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
#include "RooWorkspace.h"
#include "RooSimultaneous.h"
#include "RooProdPdf.h"
#include "RooAddPdf.h"
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
#include "RooMinimizer.h"
#include "RooConstVar.h"
#include "RooNumIntConfig.h"
#include "RooBinningCategory.h"

#include "TLegendEntry.h"
#include "TLegend.h"
#include "TCanvas.h"
#include "TPad.h"
#include "TLine.h"

static TMsgLogger Logger("HistogramPlotter");

HistogramPlotter::HistogramPlotter(RooWorkspace *w, const TString& fitConfigName) {
    ConfigMgr* mgr = ConfigMgr::getInstance();
    FitConfig* fc = mgr->getFitConfig(fitConfigName);
    if(!w) {
        throw std::invalid_argument( "No workspace passed" );
    }

    if(!fc) {
        throw std::invalid_argument( "No such fit configuration" );
    }

    m_workspace = w;
    m_fitConfig = fc;

    m_plotRatio = mgr->m_plotRatio;

    m_plotRegions = "ALL";
    m_plotComponents = true;
    m_plotSeparateComponents = false;
    m_storeSingleFiles = true;
    m_storeMergedFile = false;
    m_doStackPlots = true;

    m_fitResult = nullptr;
    m_inputData = nullptr;
}

HistogramPlotter::HistogramPlotter(RooWorkspace* w, FitConfig* fc) {
    if(!w) {
        throw std::invalid_argument( "No workspace passed" );
    }

    if(!fc) {
        throw std::invalid_argument( "No such fit configuration" );
    }

    m_workspace = w;
    m_fitConfig = fc;

    ConfigMgr* mgr = ConfigMgr::getInstance();
    m_plotRatio = mgr->m_plotRatio;
    m_plotRegions = "ALL";

    m_storeSingleFiles = true;
    m_storeMergedFile = false;
    m_doStackPlots = true;
}

HistogramPlotter::~HistogramPlotter() {
    // we do NOT own the pointers. leave them be.
}

void HistogramPlotter::setPlotSeparateComponents(bool b) {
    m_plotSeparateComponents = b;
}

void HistogramPlotter::setPlotComponents(bool b) {
    m_plotComponents = b;
}

void HistogramPlotter::setStoreSingleFiles(bool b) {
    m_storeSingleFiles = b;
}

void HistogramPlotter::setStoreMergedFile(bool b) {
    m_storeMergedFile = b;
}

void HistogramPlotter::setDoStackPlots(bool b) {
    m_doStackPlots = b;
}

void HistogramPlotter::setPlotRegions(const TString &s) {
    m_plotRegions = s;
}

void HistogramPlotter::setAnalysisName(const TString& anaName) {
    m_anaName = anaName;
}

void HistogramPlotter::setOutputPrefix(const TString& outputPrefix) {
    m_outputPrefix = outputPrefix;
}

void HistogramPlotter::setFitResult(RooFitResult *r) {
    m_fitResult = r;
}

void HistogramPlotter::setInputData(RooAbsData* data) {
    m_inputData = data;
}

void HistogramPlotter::Initialize() {
    RooMsgService::instance().getStream(1).removeTopic(RooFit::NumIntegration);
    RooMsgService::instance().getStream(1).removeTopic(RooFit::Plotting);

    Logger << kINFO << "HistogramPlotter::Initialize()" << GEndl;
    Logger << kINFO << " ------ Starting Plot with parameters:   analysisName = " << m_fitConfig->m_name << " and " << m_anaName << GEndl;
    Logger << kINFO << "    plotRegions = '" <<  m_plotRegions <<  "'  plotComponents = " << m_plotComponents << "  outputPrefix = " << m_outputPrefix  << GEndl;
    Logger << kINFO << "    storeSingleFiles = '" <<  m_storeSingleFiles <<  "'  storeMergedFiles = " << m_storeMergedFile << "  doStackPlot = " << m_doStackPlots  << GEndl;

    m_pdf = static_cast<RooSimultaneous*>(m_workspace->pdf("simPdf"));
    if(!m_inputData) {
        Logger << kDEBUG << "No data provided; loading from PDF" << GEndl;
        m_inputData = static_cast<RooAbsData*>(m_workspace->data("obsData"));
    }

    Logger << kDEBUG << "Loading RooCategory 'channelCat'" << GEndl;
    m_regionCategory = static_cast<RooCategory*>(m_workspace->cat("channelCat"));

    Logger << kINFO << "Datasets found:" << GEndl;
    m_inputData->table(*(static_cast<RooAbsCategory*>(m_regionCategory)))->Print("v");

    Logger << kDEBUG << "Finding regions to use for plot" << GEndl;
    m_regions = Util::GetRegionsVec(m_plotRegions, m_regionCategory);
}

void HistogramPlotter::PlotRegions() {
    Logger << kINFO << "Plotting all known regions in PDF" << GEndl;

    if(m_storeMergedFile) {
        m_mergedFile = ("results/" + m_anaName + "/histograms_" + m_outputPrefix + ".root");
        Logger << kINFO << "Will store " << m_outputPrefix << " histograms in " << m_mergedFile << GEndl;
        TFile *f = TFile::Open(m_mergedFile.Data(), "RECREATE");
        f->Close();
    }

    // loop loop loop
    for(const auto &categoryLabel : m_regions)  {
        // Does the region actually exist?
        if( m_regionCategory->setLabel(categoryLabel, kTRUE)) {
            Logger << kINFO << " Label '" << categoryLabel << "' is not a state of channelCat (see table) " << GEndl;
            continue;
        }

        PlotRegion(categoryLabel);
    }
}

void HistogramPlotter::PlotRegion(const TString &regionCategoryLabel) {
    Logger << kINFO << "Plotting for region label '" << regionCategoryLabel << "'" << GEndl;

    // find the PDF in this region
    RooAbsPdf* regionPdf = static_cast<RooAbsPdf*>(m_pdf->getPdf(regionCategoryLabel.Data()));

    // select the data here
    TString dataCatLabel("channelCat==channelCat::" + regionCategoryLabel);
    Logger << kDEBUG << "Selecting data with '" << dataCatLabel << "'" << GEndl;
    RooDataSet* regionData = static_cast<RooDataSet*>(m_inputData->reduce(dataCatLabel.Data()));

    // style for this channel
    ChannelStyle style = m_fitConfig->getChannelStyle(regionCategoryLabel);

    // does this make sense?
    if(!regionPdf || !regionData){
        Logger << kWARNING << "Either the PDF or the dataset does not have an appropriate state for the region = " << regionCategoryLabel << ", check the workspace file" << GEndl;
        Logger << kWARNING << "regionPdf = " << regionPdf << "   regionData = " << regionData << GEndl;
        return;
    }

    HistogramPlot plot(m_workspace, regionCategoryLabel, regionPdf, regionData, style);
    plot.setAnalysisName(m_anaName);
    plot.setFitResult(m_fitResult);
    plot.setPlotComponents(m_plotComponents);
    plot.setOutputPrefix(m_outputPrefix);
    plot.setStoreSingleFiles(m_storeSingleFiles);

    TFile *file = nullptr;
    TDirectory *directory = nullptr;
    if(m_storeMergedFile) {
        //std::string filename("results/" + m_anaName + "/histograms_" + m_outputPrefix + ".root");
        file = TFile::Open(m_mergedFile.Data(), "UPDATE");
        directory = file->mkdir(regionCategoryLabel);
    }

    // This will write single files if m_storeSingleFiles was set, and write to the directory if it was set too
    if(m_doStackPlots) plot.plot(directory);

    if(m_storeSingleFiles) {
        //TString canvasName(Form("%s_%s", regionCategoryLabel.Data(), m_outputPrefix.Data()));
        std::string filename("results/" + m_anaName + "/" + regionCategoryLabel + ".root");
        TFile *f = TFile::Open(filename.c_str(), "update");
        plot.saveHistograms(f);
        f->Close();
    }

    if(directory) {
        plot.saveHistograms(directory);
    }

    //if(m_plotSeparateComponents) {
    //plot.plotSeparateComponents();
    //}

    if(file) file->Close();

}

////////////////

HistogramPlot::HistogramPlot(RooWorkspace *w,
        const TString& regionCategoryLabel, RooAbsPdf *regionPdf,
        RooDataSet *regionData, const ChannelStyle &style) : m_workspace(w),
    m_regionPdf(regionPdf),
    m_regionData(regionData),
    m_style(style),
    m_regionCategoryLabel(regionCategoryLabel),
    m_regionVariableName("obs_x_"+regionCategoryLabel),
    m_binEdges({})
{
    m_regionVariable = static_cast<RooRealVar*>( static_cast<RooArgSet*>(m_regionPdf->getObservables(*regionData))->find(m_regionVariableName));

    ConfigMgr* mgr = ConfigMgr::getInstance();
    m_plotRatio = mgr->m_plotRatio;

    if (mgr->getRebinMap().find(std::string(m_regionCategoryLabel)) != mgr->getRebinMap().end())
        m_binEdges = mgr->getRebinMap()[std::string(m_regionCategoryLabel)];

    m_fitResult = nullptr;
    m_plotComponents = false;
    m_storeSingleFiles = false;
}

void HistogramPlot::setPlotComponents(bool b) {
    m_plotComponents = b;
}

void HistogramPlot::setStoreSingleFiles(bool b) {
    m_storeSingleFiles = b;
}

void HistogramPlot::setOutputPrefix(const TString& outputPrefix) {
    m_outputPrefix = outputPrefix;
}

void HistogramPlot::setAnalysisName(const TString& anaName) {
    m_anaName = anaName;
}

void HistogramPlot::setFitResult(RooFitResult *r) {
    m_fitResult = r;
}

void HistogramPlot::buildFrame() {
    Logger << kINFO << "Building frame for " << m_regionCategoryLabel << GEndl;

    // create RooFit frame
    m_frame =  m_regionVariable->frame();
    m_frame->SetName(Form("frame_%s_%s", m_regionCategoryLabel.Data(), m_outputPrefix.Data()));

    // plot the data
    if(m_style.getXErrorSize()>= 0.){
            Logger << kDEBUG << "setting X error " << GEndl;
            m_regionData->plotOn(m_frame, RooFit::DataError(RooAbsData::Poisson),
            RooFit::MarkerColor(m_style.getDataColor()),
            RooFit::LineColor(m_style.getDataColor()),
            RooFit::XErrorSize(m_style.getXErrorSize()));

    }else m_regionData->plotOn(m_frame, RooFit::DataError(RooAbsData::Poisson),
            RooFit::MarkerColor(m_style.getDataColor()),
            RooFit::LineColor(m_style.getDataColor()));

    if(m_style.getRemoveEmptyBins()){
        Logger << kINFO << "RemoveEmptyDataBins() removing empty bin points from data histogram on plot " << m_frame->GetName() << GEndl;
        Util::RemoveEmptyDataBins(m_frame);
    }

    // normalize pdf to number of expected events, not to number of events in dataset
    Logger << kDEBUG << "Drawing PDF" << GEndl;
    m_regionPdf->plotOn(m_frame, RooFit::Normalization(1, RooAbsReal::RelativeExpected),
            RooFit::Precision(1e-5),
            RooFit::LineColor(m_style.getTotalPdfColor()));

    // plot components
    if(m_plotComponents) {
        //AddComponentsToPlot(w, fc, frame, regionPdf, regionVar, regionCatLabel.Data(),style);
        addComponents();
    }

    // visualize error of fit
    if(m_fitResult) {
        Logger << kDEBUG << "Drawing fit errors" << GEndl;
        m_regionPdf->plotOn(m_frame, RooFit::Normalization(1, RooAbsReal::RelativeExpected),
                RooFit::Precision(1e-5),
                RooFit::FillColor(m_style.getErrorFillColor()),
                RooFit::FillStyle(m_style.getErrorFillStyle()),
                RooFit::LineColor(m_style.getErrorLineColor()),
                RooFit::LineStyle(m_style.getErrorLineStyle()),
                RooFit::DrawOption("F"),
                RooFit::VisualizeError(*m_fitResult),
                RooFit::Name("total_error_band"));

    }

    // re-plot data and pdf, so they are on top of error and components
    Logger << kDEBUG << "Redrawing PDF" << GEndl;
    m_regionPdf->plotOn(m_frame, RooFit::Normalization(1, RooAbsReal::RelativeExpected),
            RooFit::Precision(1e-5),
            RooFit::LineColor(m_style.getTotalPdfColor()));

    Logger << kDEBUG << "Redrawing data" << GEndl;
    if(m_style.getXErrorSize()>= 0.){
            Logger << kDEBUG << "setting X error " << GEndl;
            m_regionData->plotOn(m_frame, RooFit::DataError(RooAbsData::Poisson),
            RooFit::MarkerColor(m_style.getDataColor()),
            RooFit::LineColor(m_style.getDataColor()),
            RooFit::XErrorSize(m_style.getXErrorSize()));

    } else  m_regionData->plotOn(m_frame, RooFit::DataError(RooAbsData::Poisson),
            RooFit::MarkerColor(m_style.getDataColor()),
            RooFit::LineColor(m_style.getDataColor()));

    // remove any empty bins
    if(m_style.getRemoveEmptyBins()) {
        Logger << kDEBUG << "Removing empty bins" << GEndl;
        Util::RemoveEmptyDataBins(m_frame);
    }
        
    // Set NaN/infinite numbers to 0
    Logger << kDEBUG << "Setting NaN/infinite entries to 0 in graphs" << GEndl;
    for (Int_t i = 0; i < m_frame->numItems(); ++i) {
        RooHist *h = (RooHist*) m_frame->getObject(i);
        TString hname = h->GetName();

        if (hname.BeginsWith(TString("model"))) {
            Logger << kDEBUG << " Fixing up graph " << hname << GEndl;
            
            for (Int_t i = 0; i < h->GetN(); ++i) {
                Double_t x, y;
                h->GetPoint(i, x, y);

                if (!isfinite(y)) {
                    Logger << kWARNING << "  Zeroing non-finite bin: " << x << " " << y << " of graph " << hname << GEndl;
                    h->SetPoint(i, x, 0.);
                }
            }
        }
    }

}

void HistogramPlot::addRatioPanelCosmetics(RooPlot* frame_dummy, RooPlot* frame) {
    // ratio plot cosmetics
    int firstbin = frame_dummy->GetXaxis()->GetFirst();
    int lastbin = frame_dummy->GetXaxis()->GetLast();
    double xmax = frame_dummy->GetXaxis()->GetBinUpEdge(lastbin) ;
    double xmin = frame_dummy->GetXaxis()->GetBinLowEdge(firstbin) ;

    TLine* l = new TLine(xmin, 1., xmax, 1.);
    TLine* l2 = new TLine(xmin, 0.5, xmax, 0.5);
    TLine* l3 = new TLine(xmin, 1.5, xmax, 1.5);
    TLine* l4 = new TLine(xmin, 2., xmax, 2.);
    TLine* l5 = new TLine(xmin, 2.5, xmax, 2.5);
    l->SetLineWidth(1);
    l->SetLineStyle(2);
    l2->SetLineStyle(3);
    l3->SetLineStyle(3);
    l4->SetLineStyle(3);
    l5->SetLineStyle(3);

    TLine* lp1 = new TLine(xmin, 1., xmax, 1.);
    TLine* lp2 = new TLine(xmin, 2., xmax, 2.);
    TLine* lp3 = new TLine(xmin, 3., xmax, 3.);
    TLine* lp4 = new TLine(xmin, 4., xmax, 4.);
    TLine* lp5 = new TLine(xmin, 5., xmax, 5.);
    TLine* lp6 = new TLine(xmin, -1., xmax, -1.);
    TLine* lp7 = new TLine(xmin, -2., xmax, -2.);
    TLine* lp8 = new TLine(xmin, -3., xmax, -3.);
    TLine* lp9 = new TLine(xmin, -4., xmax, -4.);
    TLine* lp10 = new TLine(xmin, -5., xmax, -5.);

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

    if(m_plotRatio == "ratio"){
        frame->addObject(l);
        frame->addObject(l2);
        frame->addObject(l3);
        frame->addObject(l4);
        frame->addObject(l5);
    } else if(m_plotRatio == "pull"){
        frame->addObject(lp1);
        frame->addObject(lp2);
        frame->addObject(lp3);
        frame->addObject(lp4);
        frame->addObject(lp5);
        frame->addObject(lp6);
        frame->addObject(lp7);
        frame->addObject(lp8);
        frame->addObject(lp9);
        frame->addObject(lp10);
    }

    Double_t lowerlimit = 0.;
    Double_t upperlimit = 2.2;
    if (m_plotRatio == "pull"){
        lowerlimit = -5.7;
        upperlimit = 5.7;
    }

    frame->SetMinimum(lowerlimit);
    frame->SetMaximum(upperlimit);

}

void HistogramPlot::addRatioPanel() {
    Logger << kDEBUG << "Adding ratio panel to plot" << GEndl;

    //TFile f("/tmp/test.root", "recreate");

    //std::cout << "pdf = " << m_regionData << std::endl;
    //std::cout << "data = " << m_regionPdf << std::endl;
    //std::cout << "variable = " << m_regionVariable << std::endl;

    // Data/model ratio
    auto hratio = Util::MakeRatioOrPullHist(m_regionData, m_regionPdf, m_regionVariable);
    hratio->SetMarkerColor(m_style.getDataColor());
    hratio->SetLineColor(m_style.getDataColor());

    // Data/bkg ratio -- check if we have a POI, if so, calculate the ratio with it set to 0
    RooStats::ModelConfig* mc = Util::GetModelConfig( m_workspace );
    const RooArgSet * poiSet = mc->GetParametersOfInterest();
    RooRealVar *poi = NULL;
    if (poiSet->getSize()>0) { poi = (RooRealVar*) poiSet->first();}
    RooHist* hratio_excl_sig = nullptr;
    if(poi) {
        //exit(0);
        Logger << kWARNING << "Found a signal model; calculating ratio with mu_sig=0 as well" << GEndl;

        const auto poi_val_old = poi->getVal();
        poi->setVal(0);

        hratio_excl_sig = Util::MakeRatioOrPullHist(m_regionData, m_regionPdf, m_regionVariable );
        hratio_excl_sig->SetMarkerColor(m_style.getDataColor());
        //hratio_excl_sig->SetLineColor(m_style.getDataColor());
        hratio_excl_sig->SetMarkerStyle(21);
        hratio_excl_sig->SetMarkerColor(kRed);
        hratio_excl_sig->SetLineWidth(0);

        poi->setVal(poi_val_old);
    }

    //// data/pdf ratio histograms are plotted by RooPlot through a dummy frame
    RooPlot* frame_dummy = m_regionVariable->frame();

    // Construct a histogram with the ratio of the pdf curve w.r.t the pdf curve +/- 1 sigma
    RooCurve* hratioPdfError = new RooCurve;
    if (m_fitResult) {
        hratioPdfError = Util::MakePdfErrorRatioHist(m_regionData, m_regionPdf, m_regionVariable, m_fitResult);
    }
    hratioPdfError->SetFillColor(m_style.getErrorFillColor());
    hratioPdfError->SetFillStyle(m_style.getErrorFillStyle());
    hratioPdfError->SetLineColor(m_style.getErrorLineColor());
    hratioPdfError->SetLineStyle(m_style.getErrorLineStyle());

    // Create a new frame to draw the residual distribution and add the distribution to the frame
    RooPlot* frame2 = m_regionVariable->frame() ;
    if(m_plotRatio == "ratio") {
        hratio->SetTitle("Ratio Distribution");
    } else if(m_plotRatio == "pull") {
        hratio->SetTitle("Pull Distribution");
    }

    // only add PdfErrorsPlot when the plot shows ratio, not with pull
    if (m_fitResult && m_plotRatio == "ratio") {
        frame2->addPlotable(hratioPdfError, "F");
    }

    // add the data/model ratio
    frame2->addPlotable(hratio, "P");

    // add the data/bkg ratio, if there was a POI to be set to 0
    if(hratio_excl_sig) {
        Logger << kWARNING << "Plotting second ratio" << GEndl;
        frame2->addPlotable(hratio_excl_sig, "P");
    }

    addRatioPanelCosmetics(frame_dummy, frame2);

    if(m_plotRatio == "ratio") {
        frame2->GetYaxis()->SetTitle("Data / Model");
    } else if(m_plotRatio == "pull") {
        frame2->GetYaxis()->SetTitle("Pull");
    }

    if(m_style.getTitleX() != "") {
        frame2->GetXaxis()->SetTitle(m_style.getTitleX());
    }

    //if(m_style.getTitleY() != "") {
    //m_frame->GetYaxis()->SetTitle(m_style.getTitleY());
    //}

    if(m_style.getArrowRatio()){
            Logger << kDEBUG << "add arrow(s) showing out of scale data in the ratio plot " << GEndl;
            double maxFrame=frame2->GetMaximum();
            double dy=(maxFrame-1.)/4.;
            for (Int_t i =0;i<hratio->GetN();i++){
               Double_t x,y;
               hratio->GetPoint(i,x,y);
               if(y > maxFrame){
                 TArrow* arrow = new TArrow(x,1+dy,x,maxFrame-dy,0.02,"|>") ;
                 arrow->SetAngle(m_style.getArrowAngle()) ;
                 arrow->SetLineColor(m_style.getArrowColor()) ;
                 arrow->SetFillColor(m_style.getArrowColor()) ;
                 arrow->SetLineWidth(m_style.getArrowWidth()) ;
                 frame2->addObject(arrow) ;
               }
            }
    }

    frame2->GetYaxis()->SetLabelSize(0.13);
    frame2->GetYaxis()->SetNdivisions(504);
    frame2->GetXaxis()->SetLabelSize(0.13);
    frame2->GetYaxis()->SetTitleSize(0.13);
    frame2->GetXaxis()->SetTitleSize(0.13);
    frame2->GetYaxis()->SetTitleOffset(0.35);
    frame2->GetXaxis()->SetTitleOffset(1.);
    frame2->GetYaxis()->SetLabelOffset(0.01);
    frame2->GetXaxis()->SetLabelOffset(0.03);
    frame2->GetXaxis()->SetTickLength(0.06);

    frame2->SetTitle("");
    frame2->GetYaxis()->CenterTitle();
    frame2->Draw();

}

void HistogramPlot::addComponents() {
    Logger << kDEBUG << "Adding components to plot" << GEndl;

    if(m_componentNames.empty()) {
        loadComponentInformation();
    }

    const double normalisation = m_regionPdf->expectedEvents(*m_regionVariable);
    for(int i = (m_componentNames.size()-1); i >- 1; --i){
        // loop backwards, otherwise it doesn't make sense: then the biggest contribution hides the others

        // We really plot various _stacks_, starting from the biggest one. Otherwise, the normalisations
        // are wrong; individual components unfortunately cannot get stacked.

        //Logger << kDEBUG << "At component " << m_componentNames[i] << GEndl;
        //Logger << kDEBUG << "Stacked name: " << m_componentStackedNames[i] << GEndl;

        auto color = m_style.getSampleColor(m_componentNames[i]);

        m_regionPdf->plotOn(m_frame, //RooFit::Normalization(1, RooAbsReal::RelativeExpected),
                RooFit::Components(m_componentStackedNames[i].Data()),
                RooFit::Normalization(m_componentStackedFractions[i]*normalisation, RooAbsReal::NumEvent),
                RooFit::FillColor(color),
                RooFit::FillStyle(1001),
                RooFit::DrawOption("F"),
                RooFit::Precision(1e-5));
    }

}

void HistogramPlot::loadComponentInformation() {
    // Finds all components, their fractions, and their stacked fractions.
    // Used for the legend and the component addition.

    // Find the RooRealSumPdf
    TString RSSPdfName = m_regionCategoryLabel + "_model";
    RooRealSumPdf* RRSPdf = static_cast<RooRealSumPdf*>(m_regionPdf->getComponents()->find(RSSPdfName));
    Logger << kINFO << "Identifying components of region model " << RSSPdfName << GEndl;

    // Build the components list to iterate over
    RooArgList RRSComponentsList =  RRSPdf->funcList();
    RooLinkedListIter iter = RRSComponentsList.iterator() ;
    RooProduct* component = nullptr;

    // Now load the names and calculate the fractions to be able to build the plot
    while( (component = dynamic_cast<RooProduct*>(iter.Next()))) {
        TString componentName(component->GetName());

        Logger << kDEBUG << "Identified component " << componentName << GEndl;

        // Build the stacked component names
        TString stackedComponentName(componentName);
        if(!m_componentStackedNames.empty()){
            stackedComponentName = Form("%s,%s", m_componentStackedNames.back().Data(), componentName.Data());
        }

        m_componentNames.push_back(componentName);
        m_componentStackedNames.push_back(stackedComponentName);

        // Find the fraction and the stacked fraction for these backgrounds
        // RooFit can't stack via PlotOn() when normalising, so keep track of this ourselves
        double componentFraction = Util::GetComponentFrac(m_workspace, componentName, RSSPdfName, m_regionVariable) ;
        double stackComponentFraction = componentFraction;
        if(!m_componentStackedFractions.empty()){
            stackComponentFraction  = m_componentStackedFractions.back() + componentFraction;
        }

        Logger << kVERBOSE << "Fraction = " << componentFraction << GEndl;
        Logger << kVERBOSE << "Stacked fraction = " << stackComponentFraction << GEndl;

        m_componentFractions.push_back(componentFraction);
        m_componentStackedFractions.push_back(stackComponentFraction);

        // Find the PDF associated to the component
        TString componentPdf_name = Form("RooRealSumPdf_region_%s_%s", m_regionCategoryLabel.Data(), componentName.Data());
        RooArgList compFuncList;
        RooArgList compCoefList;
        compFuncList.add(*(RooProduct*) m_workspace->obj(componentName));
        TString coefName = TString(componentName).ReplaceAll("_shapes", "_scaleFactors");
        compCoefList.add(*(RooRealVar*) m_workspace->obj(coefName));
        RooRealSumPdf* componentPdf = new RooRealSumPdf(componentPdf_name, componentPdf_name, compFuncList, compCoefList);

        m_componentPdfs[componentName] = componentPdf;

    }
}

TLegend* HistogramPlot::buildLegend() {
    Logger << kDEBUG << "Building legend for plot" << GEndl;

    TLegend *leg = new TLegend(0.5, 0.44, 0.895, 0.895, "");
    leg->SetFillStyle(0);
    leg->SetFillColor(0);
    leg->SetBorderSize(0);

    // Add data
    TLegendEntry* entry=leg->AddEntry("", "Data", "p") ;
    entry->SetMarkerColor(m_style.getDataColor());
    entry->SetMarkerStyle(20);

    // Add total as SM
    entry=leg->AddEntry("", "Standard Model", "lf") ;
    entry->SetLineColor(m_style.getTotalPdfColor());
    entry->SetFillColor(m_style.getErrorFillColor());
    entry->SetFillStyle(m_style.getErrorFillStyle());

    // Load component info
    if(m_componentNames.empty()) {
        loadComponentInformation();
    }

    // add components to legend
    for(int i = (m_componentNames.size()-1); i >- 1; --i){
        Int_t  compPlotColor    = m_style.getSampleColor(m_componentNames[i]);
        TString compShortName   = m_style.getSampleName(m_componentNames[i]);

        TString legName = compShortName;
        entry = leg->AddEntry("", legName.Data() ,"f");
        entry->SetLineColor(compPlotColor);
        entry->SetFillColor(compPlotColor);
        entry->SetFillStyle(1001);
    }

    return leg;
}

void HistogramPlot::plot(TDirectory *directory) {
    if(!m_storeSingleFiles && !directory){
        Logger << kWARNING << "HistogramPlot::plot called with m_storeSingleFiles == false and directory == nullptr - nothing to do here!" << GEndl;
        return;
    }

    buildFrame();

    // Now build the canvas
    TString canvasName(Form("%s_%s", m_regionCategoryLabel.Data(), m_outputPrefix.Data()));
    auto canvas = new TCanvas(canvasName, canvasName,  700,  600);

    // two pads, one for 'standard' plot, one for data/MC ratio
    float yMinP1 = 0.305;
    float bottomMarginP1 = 0.005;
    if(m_plotRatio == "none"){
        yMinP1 = 0.01;
        bottomMarginP1 = 0.09;
    }

    // pad for standard plot
    TPad *pad1 = new TPad(Form("%s_pad1", canvasName.Data()), Form("%s_pad1", canvasName.Data()), 0., yMinP1, .99, 1);
    pad1->SetBottomMargin(bottomMarginP1);
    pad1->SetFillColor(kWhite);
    pad1->SetTickx();
    pad1->SetTicky();

    // pad for ratio
    TPad *pad2 = new TPad(Form("%s_pad2", canvasName.Data()), Form("%s_pad2", canvasName.Data()), 0., 0.01, .99, 0.295);
    pad2->SetTopMargin(0.005);
    pad2->SetBottomMargin(0.3);
    pad2->SetFillColor(kWhite);

    // Do we have a log plot?
    if(m_style.getLogY()) {
        pad1->SetLogy();
    }

    // Is there a title for the x-axis?
    if(m_style.getTitleX() != "") {
        m_frame->GetXaxis()->SetTitle(m_style.getTitleX());
    }

    // Draw the pads
    pad1->Draw();
    if(m_plotRatio != "none"){
        pad2->Draw();
        m_frame->GetXaxis()->SetLabelSize(0.);
    }

    // Go to the main pad and set ranges for the frame
    pad1->cd();

    m_frame->SetMinimum(m_style.getMinY());
    if( fabs(m_style.getMaxY() + 999.) > 0.000001) {
        m_frame->SetMaximum(m_style.getMaxY());
    }

    // now draw frame
    m_frame->SetTitle("");
    m_frame->Draw();

    // ATLAS string - FIXME: remove for public release
    if( (fabs(m_style.getATLASLabelX() + 1.) > 0.000001) and (fabs(m_style.getATLASLabelY() + 1.) > 0.000001) ) {
        Util::ATLASLabel(m_style.getATLASLabelX(), m_style.getATLASLabelY(), m_style.getATLASLabelText()) ;
    }

    // Lumi
    if(m_style.getShowLumi()){
        Util::AddText(m_style.getLumiX(), m_style.getLumiY(), Form("#sqrt{s} = %s, %.1f fb^{-1}", m_style.getEnergy().Data(), m_style.getLumi() ));
    }

    // Legend
    TLegend *legend = m_style.getTLegend();
    if(!legend) { legend = buildLegend(); }
    legend->Draw();

    // Add ratio?
    if(m_plotRatio != "none") {
        pad2->cd();
        addRatioPanel();
    }

    // Write output
    if(m_storeSingleFiles) {
        canvas->SaveAs("results/" + m_anaName + "/" + canvasName + ".pdf");
        canvas->SaveAs("results/" + m_anaName + "/" + canvasName + ".eps");
        canvas->SaveAs("results/" + m_anaName + "/" + canvasName + ".root");
    }

    // If required (i.e. if directory is set), store a copy
    if(directory) {
        TDirectory* currentDir = gDirectory->CurrentDirectory();
        directory->cd();
        canvas->Write();
        currentDir->cd();
    }
}

void HistogramPlot::plotSeparateComponents() {
    if(m_componentNames.empty()) {
        loadComponentInformation();
    }

    int nComponents = m_componentNames.size();
    if(nComponents == 0) {
        // this doesn't make any sense, so stop
        Logger << kWARNING << "No components found for '" << m_regionCategoryLabel << "' - returning." << GEndl;
        return;
    }

    Logger << kDEBUG << "Will plot " << nComponents << " single components for " << m_regionCategoryLabel << GEndl;

    // divide the canvas
    int nPlotsX = static_cast<int>(std::sqrt(nComponents));
    int nPlotsY = static_cast<int>(std::sqrt(nComponents)+0.5);

    if(nPlotsX < 1) nPlotsX = 1;
    if(nPlotsY < 1) nPlotsY = 1;

    TString canvasName(Form("%s_%s_separateComponents", m_regionCategoryLabel.Data(), m_outputPrefix.Data()));
    auto canvas = new TCanvas(canvasName, canvasName, 600, 600);
    canvas->Divide(nPlotsX, nPlotsY);

    // normalize pdf to number of expected events, not to number of events in dataset
    const double normalisation = m_regionPdf->expectedEvents(*m_regionVariable);

    //iterate over all samples and plot
    for( unsigned int i=0; i < m_componentNames.size(); i++){
        canvas->cd(i+1);
        plotSingleComponent(i, normalisation);
    }

    canvas->SaveAs("results/" + m_anaName + "/" + canvasName + ".pdf");
    canvas->SaveAs("results/" + m_anaName + "/" + canvasName + ".eps");
    canvas->SaveAs("results/" + m_anaName + "/" + canvasName + ".root");
}

void HistogramPlot::plotSingleComponent(unsigned int i, double normalisation) {
    if(m_componentNames.empty()) {
        loadComponentInformation();
    }

    if(normalisation == 0.0) {
        normalisation = m_regionPdf->expectedEvents(*m_regionVariable);
    }

    RooPlot* frame = m_regionVariable->frame();
    frame->SetName(Form("frame_%s_%s_%s", m_regionCategoryLabel.Data(), m_componentNames[i].Data(), m_outputPrefix.Data()));
    auto color = m_style.getSampleColor(m_componentNames[i]);
    auto sampleName = m_style.getSampleName(m_componentNames[i]);

    Logger << kDEBUG << "Plotting single component " << sampleName << " for " << m_regionCategoryLabel << GEndl;

    if (m_fitResult) {
        m_regionPdf->plotOn(frame, RooFit::Components(m_componentNames[i].Data()),
                RooFit::VisualizeError(*m_fitResult),
                RooFit::FillColor(kCyan),
                RooFit::DrawOption("F"),
                RooFit::Precision(1e-5),
                RooFit::Normalization(m_componentFractions[i]*normalisation, RooAbsReal::NumEvent));
    }

    m_regionPdf->plotOn(frame, RooFit::Components(m_componentNames[i].Data()),
            RooFit::LineColor(color),
            RooFit::Normalization(m_componentFractions[i]*normalisation, RooAbsReal::NumEvent),
            RooFit::Precision(1e-5));

    frame->SetMinimum(0.0);
    m_frame->GetYaxis()->SetTitle(m_style.getTitleY());
    frame->Draw();

    TLegend* leg = new TLegend(0.55, 0.65, 0.85, 0.9, "");
    leg->SetFillStyle(0);
    leg->SetFillColor(0);
    leg->SetBorderSize(0);

    TLegendEntry* entry = nullptr;
    if(m_fitResult) {
        entry = leg->AddEntry("", "Propagated fit error", "f") ;
        entry->SetMarkerColor(kCyan);
        entry->SetMarkerStyle();
        entry->SetFillColor(kCyan);
        entry->SetFillStyle(1001);
    }

    entry = leg->AddEntry("", sampleName.Data(), "l") ;
    entry->SetLineColor(color);
    leg->Draw();
}

void HistogramPlot::saveHistograms(TDirectory *directory) {
    if(m_componentNames.empty()) {
        loadComponentInformation();
    }

    // Save the current directory to resume it after this function call
    TDirectory* currentDir = gDirectory->CurrentDirectory();
    directory->cd();

    // Data hist
    RooPlot* frame_dummy = m_regionVariable->frame();
    m_regionData->plotOn(frame_dummy, RooFit::DataError(RooAbsData::Poisson));
    auto data_hist = frame_dummy->findObject(nullptr, RooHist::Class());
    if (m_binEdges.size()) {
        TGraphAsymmErrors* data_hist_g = remapGraph(static_cast<TGraphAsymmErrors*>(data_hist));
        data_hist = static_cast<RooHist*>(data_hist_g);
    }
    data_hist->Write();

    // Get the total MC
    TString RSSPdfName = m_regionCategoryLabel + "_model";
    RooRealSumPdf* RRSPdf = static_cast<RooRealSumPdf*>(m_regionPdf->getComponents()->find(RSSPdfName));
    auto mc_hist = Util::ComponentToHistogram(RRSPdf, m_regionVariable, m_fitResult);
    mc_hist->SetLineColor(m_style.getTotalPdfColor());
    if (m_binEdges.size())
        mc_hist = remapHistogram(mc_hist);
    mc_hist->Write("SM_total");

    // Data/model ratio
    auto hratio = Util::MakeRatioOrPullHist(m_regionData, m_regionPdf, m_regionVariable);
    hratio->SetMarkerColor(m_style.getDataColor());
    hratio->SetLineColor(m_style.getDataColor());
    if (m_binEdges.size()) {
        TGraphAsymmErrors* g_hratio = remapGraph(static_cast<TGraphAsymmErrors*>(hratio), static_cast<TGraphAsymmErrors*>(data_hist));
        hratio = static_cast<RooHist*>(g_hratio);
    }
    hratio->Write("h_ratio"); // "ratio" is a reserved keyword in root

    // Data/bkg ratio -- check if we have a POI, if so, calculate the ratio with it set to 0
    RooStats::ModelConfig* mc = Util::GetModelConfig( m_workspace );
    const RooArgSet * poiSet = mc->GetParametersOfInterest();

    RooRealVar *poi = NULL;
    if (poiSet->getSize()>0) {poi = (RooRealVar*) poiSet->first();}

    if(poi) {
        //exit(0);
        Logger << kINFO << "Found a signal model; calculating ratio with mu_sig=0 as well" << GEndl;

        const auto poi_val_old = poi->getVal();
        poi->setVal(0);

        auto hratio2 = Util::MakeRatioOrPullHist(m_regionData, m_regionPdf, m_regionVariable );
        hratio2->SetMarkerColor(m_style.getDataColor());
        hratio2->SetLineColor(m_style.getDataColor());

        if (m_binEdges.size()) {
            TGraphAsymmErrors* g_hratio2 = remapGraph(static_cast<TGraphAsymmErrors*>(hratio2), static_cast<TGraphAsymmErrors*>(data_hist));
            hratio2 = static_cast<RooHist*>(g_hratio2);
        }
        hratio2->Write("h_ratio_excl_sig");

        poi->setVal(poi_val_old);
    }

    // Fit error for ratio, and the total fit error
    if (m_fitResult) {
        auto hratioPdfError = Util::MakePdfErrorRatioHist(m_regionData, m_regionPdf, m_regionVariable, m_fitResult);
        hratioPdfError->SetFillColor(m_style.getErrorFillColor());
        hratioPdfError->SetFillStyle(m_style.getErrorFillStyle());
        hratioPdfError->SetLineColor(m_style.getErrorLineColor());
        hratioPdfError->SetLineStyle(m_style.getErrorLineStyle());
        hratioPdfError->SetLineWidth(0);
        if (m_binEdges.size()) {
            remapCurve(hratioPdfError);
        }
        hratioPdfError->Write("h_rel_error_band");

        // We get the total error directly from RooFit
        // Needs to be drawn again for some reason; we cannot just get it from above and using m_frame
        m_regionPdf->plotOn(frame_dummy, RooFit::Normalization(1, RooAbsReal::RelativeExpected),
                RooFit::Precision(1e-5),
                RooFit::FillColor(m_style.getErrorFillColor()),
                RooFit::FillStyle(m_style.getErrorFillStyle()),
                RooFit::LineColor(m_style.getErrorLineColor()),
                RooFit::LineStyle(m_style.getErrorLineStyle()),
                RooFit::DrawOption("F"),
                RooFit::VisualizeError(*m_fitResult),
                RooFit::Name("total_error_band"));
        auto total_err = static_cast<RooCurve*>(frame_dummy->findObject("total_error_band"));
        total_err->SetLineWidth(0);
        if (m_binEdges.size()) {
            remapCurve(total_err);
        }
        total_err->Write("h_total_error_band");
    }

    // Every seperate component
    for(const auto& component: m_componentNames) {
        auto h = Util::ComponentToHistogram(m_componentPdfs[component], m_regionVariable, m_fitResult);

        h->SetFillColor(m_style.getSampleColor(component));

        h->SetName(m_style.getSampleName(component));
        Logger << kINFO << component << GEndl;
        Logger << kINFO << "Rebinning histogram " << h->GetName() << GEndl;
        if (m_binEdges.size())
            h = remapHistogram(h);
        h->Write();
    }

    Logger << kINFO << "Wrote histogram information to: " << directory->GetPath() << GEndl;

    // Resume the previous directory
    currentDir->cd();
}

TH1D* HistogramPlot::remapHistogram(TH1* h) {
    std::string name(h->GetName());
    for (auto &d: m_binEdges)
        std::cout << d << " ";
    std::cout << std::endl;
    TH1D* temph = new TH1D((name+"TempName").c_str(),(name+"TempName").c_str(),
                            m_binEdges.size()-1, &(m_binEdges[0]));
    for (int i = 0; i <= h->GetNbinsX()+1; i++) {
        temph->SetBinContent(i,h->GetBinContent(i));
        temph->SetBinError(i,h->GetBinError(i));
    }
    temph->SetMarkerStyle(h->GetMarkerStyle());
    temph->SetMarkerSize(h->GetMarkerSize());
    temph->SetMarkerColor(h->GetMarkerColor());
    temph->SetLineStyle(h->GetLineStyle());
    temph->SetLineWidth(h->GetLineWidth());
    temph->SetLineColor(h->GetLineColor());
    temph->SetFillStyle(h->GetFillStyle());
    temph->SetFillColor(h->GetFillColor());
    temph->GetXaxis()->SetTitle(h->GetXaxis()->GetTitle());
    temph->GetYaxis()->SetTitle(h->GetYaxis()->GetTitle());
    delete h;
    temph->SetName(name.c_str());
    temph->SetTitle(name.c_str());
    return temph;
}

TGraphAsymmErrors* HistogramPlot::remapGraph(TGraphAsymmErrors* g, TGraphAsymmErrors* gref) {
    TGraphAsymmErrors* tempg = new TGraphAsymmErrors();
    unsigned int i_adjusted = 0;
    for (unsigned int i = 0; i < m_binEdges.size()-1; i++) {
        int N = tempg->GetN();
        if (gref and gref->GetY()[i]==0) {
            continue;
        }
        double xl = m_binEdges[i];
        double xh = m_binEdges[i+1];
        tempg->SetPoint(N, xl+(xh-xl)/2., g->GetY()[i_adjusted]);
        tempg->SetPointError(N, (xh-xl)/2., (xh-xl)/2., g->GetEYlow()[i_adjusted],  g->GetEYhigh()[i_adjusted]);
        i_adjusted++;
    }
    tempg->SetMarkerStyle(g->GetMarkerStyle());
    tempg->SetMarkerSize(g->GetMarkerSize());
    tempg->SetMarkerColor(g->GetMarkerColor());
    tempg->SetLineStyle(g->GetLineStyle());
    tempg->SetLineWidth(g->GetLineWidth());
    tempg->SetLineColor(g->GetLineColor());
    tempg->SetFillStyle(g->GetFillStyle());
    tempg->SetFillColor(g->GetFillColor());
    tempg->SetName(g->GetName());
    return tempg;
}

void HistogramPlot::remapCurve(RooCurve* c) {
    double extra = (m_binEdges[1]-m_binEdges[0])/2.;
    for (int i = 0; i < c->GetN(); i++) {
        int x = c->GetX()[i] + 0.99;
        if (x >= 0 and x <= (int)(m_binEdges.size()-1)) {
            c->GetX()[i] = m_binEdges[x];
        }
        else if (x >= 0) {
            c->GetX()[i] = m_binEdges[m_binEdges.size()-1] + extra;
        }
        else{
            c->GetX()[i] = m_binEdges[0] - extra;
        }
    }
}

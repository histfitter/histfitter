// vim: ts=4 sw=4
#ifndef HISTOGRAMPLOTTER_H
#define HISTOGRAMPLOTTER_H

#include <iostream>
#include <map>
#include <vector>
#include <string>
#include "TString.h"
#include "TGraphAsymmErrors.h"
#include "TArrow.h"

#include <stdexcept>

#include "RooFitResult.h"
#include "RooArgSet.h"
#include "RooArgList.h"
#include "RooExpandedFitResult.h"
#include "ChannelStyle.h"
#include "RooBinning.h"

class TH1D;
class TMap;
class TTree;

class RooAbsReal;
class RooDataSet;
class RooWorkspace;
class RooRealVar;
class RooAbsPdf;
class RooAbsData;
class RooSimultaneous;
class RooCategory;
class RooPlot;
class RooMCStudy;
class FitConfig;
class RooProdPdf;
class RooHist;
class RooCurve;
class RooRealSumPdf;

namespace RooStats {
    class HypoTestResult;
    class ModelConfig;
}

// A class to write a lot of PDFs
class HistogramPlotter {
    public:

        HistogramPlotter(RooWorkspace *w, const TString& fitConfigName = "Example3b");
        HistogramPlotter(RooWorkspace* w, FitConfig* fc);
        ~HistogramPlotter();

        void setAnalysisName(const TString& anaName);
        void setOutputPrefix(const TString& outputPrefix);
        void setFitResult(RooFitResult *r);
        void setInputData(RooAbsData* data);
        void setPlotRegions(const TString& s);
        void setPlotComponents(bool b);
        void setPlotSeparateComponents(bool b);
        void setStoreSingleFiles(bool b);
        void setStoreMergedFile(bool b);
        void setDoStackPlots(bool b);

        void Initialize();
        void PlotRegions();
        void PlotRegion(const TString& r);

    private:
        RooWorkspace* m_workspace;

        FitConfig* m_fitConfig;
        TString m_anaName;

        bool m_plotSeparateComponents;
        bool m_plotComponents;
        bool m_storeSingleFiles;
        bool m_storeMergedFile;
        TString m_mergedFile;
        bool m_doStackPlots;
        TString m_plotRegions;
        TString m_outputPrefix;

        RooFitResult* m_fitResult;
        RooAbsData* m_inputData;

        std::string m_plotRatio;

        // internals
        RooSimultaneous *m_pdf;
        RooCategory *m_regionCategory;
        std::vector<TString> m_regions; // regions actually used for plotting

        std::vector< std::vector<TH1*> > m_histograms; // histograms
};

class HistogramPlot {
    public:
        HistogramPlot(RooWorkspace *w, const TString& r, RooAbsPdf *regionPdf, RooDataSet *regionData, const ChannelStyle &style);
        void plot(TDirectory *directory = nullptr);

        void saveHistograms(TDirectory *directory);
        void plotSeparateComponents();

        void setAnalysisName(const TString& anaName);
        void setOutputPrefix(const TString& outputPrefix);
        void setFitResult(RooFitResult *r);
        void setPlotComponents(bool b);
        void setStoreSingleFiles(bool b);

    private:
        HistogramPlot();

        // for the 'normal' plot
        void buildFrame();
        void addRatioPanelCosmetics(RooPlot*, RooPlot*);
        void addRatioPanel();
        void addComponents();

        // plot a single component
        void plotSingleComponent(unsigned int i, double normalisation=0.0);

        TLegend* buildLegend();
        void loadComponentInformation();

        // remap histograms
        TH1D* remapHistogram(TH1* h);
        TGraphAsymmErrors* remapGraph(TGraphAsymmErrors* g, TGraphAsymmErrors* gref = nullptr);
        void remapCurve(RooCurve* c);

        RooWorkspace* m_workspace;
        RooAbsPdf* m_regionPdf;
        RooDataSet* m_regionData;
        ChannelStyle m_style;

        RooFitResult* m_fitResult;

        TString m_regionCategoryLabel;
        TString m_regionVariableName;
        TString m_anaName;

        bool m_plotComponents;
        bool m_storeSingleFiles;
        TString m_outputPrefix;
        TString m_plotRatio;

        RooRealVar *m_regionVariable;
        RooPlot *m_frame;

        // for component plots
        std::vector<TString> m_componentNames;
        std::vector<TString> m_componentStackedNames;
        std::map<TString, RooRealSumPdf*> m_componentPdfs;

        std::vector<double> m_componentFractions;
        std::vector<double> m_componentStackedFractions;

        // component histograms
        std::vector<TH1*> m_componentHistograms;

        // bin edges for rebinning
        std::vector<double> m_binEdges;


};

#endif

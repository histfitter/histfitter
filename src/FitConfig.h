// vim: ts=4:sw=4
////////////////////////////////////////////////////////////////////////
// Creation: January 2011, David Cote (CERN)                          //
// Simple C++ mirror of python TopLevelXML objects.                   //
////////////////////////////////////////////////////////////////////////

#ifndef FITCONFIG_H
#define FITCONFIG_H

#include <iostream>
#include <vector>
#include "TString.h"
#include "TLegend.h"
#include "TMsgLogger.h"

class FitConfig {
    public:
        FitConfig();
        FitConfig(const TString& name);
        ~FitConfig(){}

        // per FitConfig options (in python equivalent to TopLevelXML)
        TString m_Name;
        TString m_inputWorkspaceFileName;
        Float_t m_Lumi;
        TString m_signalSampleName;

        std::vector<TString> m_signalChannels;
        std::vector<TString> m_validationChannels;
        std::vector<TString> m_bkgConstrainChannels;

        Int_t m_dataColor;
        Int_t m_totalPdfColor;
        Int_t m_errorLineColor;
        Int_t m_errorLineStyle;
        Int_t m_errorFillColor;
        Int_t m_errorFillStyle;      
        TLegend* m_legend;
        Bool_t m_removeEmptyBins;    

        // per channel options
        std::vector<TString> m_channels;
        std::vector<Double_t> m_channelsMinY;
        std::vector<Double_t> m_channelsMaxY;
        std::vector<Int_t> m_channelsNBins;
        std::vector<TString> m_channelsTitleX;
        std::vector<TString> m_channelsTitleY;
        std::vector<Bool_t> m_channelsLogY;
        std::vector<Double_t> m_channelsATLASLabelX;
        std::vector<Double_t> m_channelsATLASLabelY;
        std::vector<TString> m_channelsATLASLabelText;
        std::vector<Bool_t> m_channelsShowLumi;

        // per sample options
        std::vector<Int_t> m_sampleColors;
        std::vector<TString> m_sampleNames;

        // get/set functions
        Int_t getSampleColor(const TString& sample);
        void setSampleColor(Int_t color){ m_sampleColors.push_back(color);}

        TString getSampleName(const TString& sample);
        void setSampleName(const TString& sample){ m_sampleNames.push_back(sample);}

        Float_t getLumi();
        void setLumi(Double_t lumi){ m_Lumi = lumi; }

        Int_t getDataColor() { return m_dataColor; }
        void setDataColor(const Int_t& color) { m_dataColor = color; }

        Int_t getTotalPdfColor() { return m_totalPdfColor; }
        void setTotalPdfColor(const Int_t& color) { m_totalPdfColor = color; }

        Int_t getErrorLineColor() { return m_errorLineColor; }
        void setErrorLineColor(const Int_t& color) { m_errorLineColor = color; }

        Int_t getErrorLineStyle() { return m_errorLineStyle; }
        void setErrorLineStyle(const Int_t& style) { m_errorLineStyle = style; }

        Int_t getErrorFillColor() { return m_errorFillColor; }
        void setErrorFillColor(const Int_t& color) { m_errorFillColor = color; }

        Int_t getErrorFillStyle() { return m_errorFillStyle; }
        void setErrorFillStyle(const Int_t& style) { m_errorFillStyle = style; }

        Double_t getChannelMinY(const TString& channel);
        void setChannelMinY(Double_t miny) { m_channelsMinY.push_back(miny); }

        Double_t getChannelMaxY(const TString& channel);
        void setChannelMaxY(Double_t maxy) { m_channelsMaxY.push_back(maxy); }

        Int_t getChannelNBins(const TString& channel);
        void setChannelNBins(Int_t nbins) { m_channelsNBins.push_back(nbins); }

        TString getChannelTitleX(const TString& channel);
        void setChannelTitleX(const TString& title) { m_channelsTitleX.push_back(title); }

        TString getChannelTitleY(const TString& channel);
        void setChannelTitleY(const TString& title) { m_channelsTitleY.push_back(title); }

        Bool_t getChannelLogY(const TString& channel);
        void setChannelLogY(Bool_t doLogy = kFALSE) { m_channelsLogY.push_back(doLogy); }

        TLegend* getTLegend(){ return m_legend;}
        void setTLegend(TLegend* leg) { m_legend = leg; }

        Double_t getChannelATLASLabelX(const TString& channel);
        void setChannelATLASLabelX(Double_t x) { m_channelsATLASLabelX.push_back(x); }

        Double_t getChannelATLASLabelY(const TString& channel);
        void setChannelATLASLabelY(Double_t y) { m_channelsATLASLabelY.push_back(y); }

        TString getChannelATLASLabelText(const TString& channel);
        void setChannelATLASLabelText(const TString& text) { m_channelsATLASLabelText.push_back(text); }

        Bool_t getChannelShowLumi(const TString& channel);
        void setChannelShowLumi(Bool_t showLumi = kFALSE) { m_channelsShowLumi.push_back(showLumi); }

        void findChannel(const TString& channel, Int_t& idx, Bool_t& channelFound);
        void Print();
private:
        TMsgLogger m_logger;
};

#endif

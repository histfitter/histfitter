// vim: ts=4:sw=4
#ifndef XTRAVALUES_H
#define XTRAVALUES_H

#include "TString.h"
#include <vector>

class XtraValues {
    public:
        XtraValues(){}
        virtual ~XtraValues(){}

        int size();

        std::vector<double> m_nObs;
        std::vector<double> m_nObs_eStat;
        std::vector<double> m_nPred;
        std::vector<double> m_nPred_eFit;
        std::vector<double> m_Delta;
        std::vector<double> m_Delta_eTot;
        std::vector<TString> m_reg_names;

        ClassDef(XtraValues,1) // Container class
};

#endif

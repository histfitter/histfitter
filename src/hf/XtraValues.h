// vim: ts=4:sw=4
/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Class  : XtraValues                                                            *
 *                                                                                *
 * Description:                                                                   *
 *      Simple storage container class.                                           *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/

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

// vim: ts=4:sw=4
/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Class  : TEasyFormula                                                          *
 *                                                                                *
 * Description:                                                                   *
 *      Implementation (see header for description)                               *
 *                                                                                *
 * See corresponding .h file for author and license information                   *         
 *                                                                                *
 **********************************************************************************/

#include "TEasyFormula.h"
#include "TMsgLogger.h"

#include "TString.h"
#include <stdio.h>
#include <iostream>
#include <stdlib.h>
#include <algorithm>

ClassImp(TEasyFormula)

//_____________________________________________________________________________
TEasyFormula::TEasyFormula()
: TFormula(), m_logger("TEasyFormula") {
}


//_____________________________________________________________________________
TEasyFormula::TEasyFormula(const char* expression)
    : TFormula(), m_logger("TEasyFormula") {
    (void) this->SetFormula(expression);
}


//_____________________________________________________________________________
TEasyFormula::TEasyFormula(const char* name,const char* expression) 
    : TFormula(name,"1"), m_logger("TEasyFormula")  {
    (void) this->SetFormula(expression);
}


//_____________________________________________________________________________
TEasyFormula::~TEasyFormula() {
}


//_____________________________________________________________________________
TEasyFormula::TEasyFormula(const TEasyFormula& other)
    : TFormula(other)
    , m_expr(other.m_expr)
    , m_par(other.m_par)
    , m_stod(other.m_stod)
    , m_itos(other.m_itos)
      , m_stoi(other.m_stoi), m_logger("TEasyFormula") {
}


//_____________________________________________________________________________
TEasyFormula& TEasyFormula::operator=(const TEasyFormula& other) {
    if (&other == this) {
        return *this;
    }

    TFormula::operator=(other) ;
    m_expr = other.m_expr;
    m_par  = other.m_par;
    m_stod = other.m_stod;
    m_itos = other.m_itos;
    m_stoi = other.m_stoi;

    return *this ;
}

//_____________________________________________________________________________
Int_t TEasyFormula::SetFormula(const char *expression) {
    m_par.clear();
    m_stod.clear();
    m_itos.clear();
    m_stoi.clear();
    m_expr = expression;

    return this->Compile(m_expr.Data());
}


//_____________________________________________________________________________
void TEasyFormula::SetValue(const TString& name, const double& value) {
    if ( m_stod.find(name)==m_stod.end() ) {
        TString newname(name);
        (void) this->DefinedVariable(newname); // define new variable
    }
    m_stod[name] = value; 
}


//_____________________________________________________________________________
Double_t TEasyFormula::DefinedValue(Int_t code) {
  /* Interface to TFormula, return value defined by object with id 'code'
   * Object ids are mapped from object names by method DefinedVariable()
   * Return current value for variable indicated by internal reference code
   */

    if ( m_itos.find(code)==m_itos.end() ) { return 0.; }
    TString name = m_itos[code];
    if ( m_stod.find(name)!=m_stod.end() ) { return m_stod[name]; }

    return 0.;
}


//_____________________________________________________________________________
Int_t TEasyFormula::DefinedVariable(TString &name, int& action) {
  /* Interface to TFormula. If name passed by TFormula is recognized
   * as one of our RooAbsArg servers, return a unique id integer
   * that represent this variable.
   */

    Int_t ret = DefinedVariable(name) ;
    if (ret>=0) { action = kDefinedVariable; }
    return ret ;
}


//_____________________________________________________________________________
Int_t TEasyFormula::DefinedVariable(TString &name) {
  /* Interface to TFormula. If name passed by TFormula is recognized
   * as one of our RooAbsArg servers, return a unique id integer
   * that represent this variable.
   */

    if ( m_stod.find(name)==m_stod.end() ) {
        // variable not known, add it
        m_stod[name] = 0.;
        m_par.push_back(name);
        int uid = static_cast<int>(m_stod.size())-1 ; 
        m_itos[uid]  = name;
        m_stoi[name] = uid;
        return uid ;
    } else {
        // variable known, return code
        return m_stoi[name];
    }

    // variable does not exist
    return -1 ;
}


//_____________________________________________________________________________
void TEasyFormula::Summary() {
    m_logger << kINFO << "Formula : " << m_expr << GEndl;
}


//_____________________________________________________________________________
Bool_t TEasyFormula::Contains(const TString& parname) const {
    return (m_stod.find(parname)!=m_stod.end());
}


//_____________________________________________________________________________
Bool_t TEasyFormula::Contains(const std::vector<TString>& parList) const {
    if (parList.empty()) { return kTRUE; }

    Bool_t found(kFALSE);
    std::vector<TString>::const_iterator itr = parList.begin();
    for (; itr!=parList.end(); ++itr) {
        found = this->Contains(*itr);
        if (found) break;
    }
    return found;
}


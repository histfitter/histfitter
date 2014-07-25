/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Namespace: Util                                                                *
 *                                                                                *
 * Description:                                                                   *
 *      Util functions, e.g. for help with combinations and pdf constructions     *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/

#ifndef CombinationUtils_H
#define CombinationUtils_H

#include <string>
#include "TString.h"


class RooFitResult;
class RooWorkspace;

class TTree;

//________________________________________________________________________________________________
void resetFloatPars( const RooWorkspace* w, const RooFitResult* result );

//________________________________________________________________________________________________
namespace Util 
{
  /// From combination package

  float getValueFromTree( TTree* tree, const std::string& searchpar, 
                          const std::string& pn0="", const float& v0=-1, const std::string& pn1="", const float& v1=-1, 
                          const std::string& pn2="", const float& v2=-1, const std::string& pn3="", const float& v3=-1, 
                          const std::string& pn4="", const float& v4=-1, const std::string& pn5="", const float& v5=-1, 
                          const std::string& pn6="", const float& v6=-1, const std::string& pn7="", const float& v7=-1, 
                          const std::string& pn8="", const float& v8=-1, const std::string& pn9="", const float& v9=-1 );

  float getValueFromTree( TTree* tree, const std::string& searchpar, const std::vector<std::string>& pnVec, const std::vector<float>& vVec );

  bool findValueFromTree( TTree* tree, const std::string& searchpar, float& searchval,
                          const std::string& pn0="", const float& v0=-1, const std::string& pn1="", const float& v1=-1,
                          const std::string& pn2="", const float& v2=-1, const std::string& pn3="", const float& v3=-1,
                          const std::string& pn4="", const float& v4=-1, const std::string& pn5="", const float& v5=-1,
                          const std::string& pn6="", const float& v6=-1, const std::string& pn7="", const float& v7=-1,
                          const std::string& pn8="", const float& v8=-1, const std::string& pn9="", const float& v9=-1 );

  bool findValueFromTree( TTree* tree, const std::string& searchpar, float& searchval, const std::vector<std::string>& pnVec, const std::vector<float>& vVec, const float& defaultVal=-999. );

}


#endif

/**********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Macro  : plotSyst.C                                                            *
 * Created: 24 March 2015                                                         *
 *                                                                                *
 * Description:                                                                   *
 *      Macro to call plotUpDown.C with user defined systematics                  *                         
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************/

#include "plotUpDown.C"

void plotSyst(){

  plotUpDown("Top","SS","JES","metmeff2Jet");
  plotUpDown("Top","SS","JES","metmeff2Jet",true);

}

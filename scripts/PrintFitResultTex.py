"""
 * Project : HistFitter - A ROOT-based package for statistical data analysis      *
 * Package : HistFitter                                                           *
 * Script  : PrintFitResultTex.py                                                 *
 *                                                                                *
 * Description:                                                                   *
 *      Script for producing LaTeX-files derived from fit result numbers          *
 *      produced by PrintFitResult.py script                                      *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group                                                          *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
"""

def tablefragment(m,sr):
  """ 
  main function to transfer the set of numbers/names (=m provided by PrintFitResult) into a LaTeX table

  @param m Set of numbers/names provided by PrintFitResult
  @param sr Name of region, used in caption and label of table
  """

  tableline = ''

  tableline += '''
\\begin{table}
\\begin{center}
\\setlength{\\tabcolsep}{0.0pc}
\\begin{tabular*}{\\textwidth}{@{\\extracolsep{\\fill}}lcc'''
  tableline += '''}
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
Parameter                                  ''' 

  tableline += ''' &    initial value and error & fitted value and error      '''   

  tableline += ''' \\\\
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
%%'''

  m_listofkeys = m.keys()

  """
  print the initial (before fit) and fitted (after fit) parameter values and errors
  """   
  for name in m_listofkeys:
      printname = name
      printname = printname.replace('syserr_','')
      printname = printname.replace('_','\_')

      phantom = ""
      if m[name][4]>=0: phantom = "\phantom{-}"
      if str(("%.2f" %m[name][4]))=="0.00": phantom = "\phantom{-}"

      tableline += "\n" + printname + " & $" + str(("%.2f" %m[name][0])) + "\\pm " + str(("%.2f" %m[name][1])) + "$  & $ " + phantom + str(("%.2f" %m[name][4])) + "\\pm " + str(("%.2f" %m[name][5])) + "$  \\\\"
      tableline += '''
%%'''
      pass


  tableline += '''
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
\\end{tabular*}
\\end{center}
\\caption[Fit results]{
Floating fit parameters for the analysis involving signal region %s, before (left) and after (right) the background-only fit. The quoted fit errors come from HESSE.
\\label{fitparameters.%s}}
\\end{table}
%%''' % (sr,sr) 
    
  return tableline


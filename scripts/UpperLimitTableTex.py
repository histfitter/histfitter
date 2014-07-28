"""
 * Project : HistFitter - A ROOT-based package for statistical data analysis      *
 * Package : HistFitter                                                           *
 * Script  : UpperLimitTableTex.py                                                *
 *                                                                                *
 * Description:                                                                   *
 *      Script for producing LaTeX-files derived from upper limit tables          *
 *       produced by UpperLimitTable.py script                                    *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group                                                          *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
"""

def tablefragment(m,tabname):
  """ 
  main function to transfer the set of numbers/names (=m provided by UpperLimitTable) into a LaTeX table

  @param m Set of names/numbers provided by UpperLimitTable.py
  @param tabname Table name used as label in LaTeX
  """
  
  tableline = ''

  tableline += '''
\\begin{table}
\\begin{center}
\\setlength{\\tabcolsep}{0.0pc}
\\begin{tabular*}{\\textwidth}{@{\\extracolsep{\\fill}}lccccc}
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
{\\bf Signal channel}                        & $\\langle\\epsilon{\\rm \\sigma}\\rangle_{\\rm obs}^{95}$[fb]  &  $S_{\\rm obs}^{95}$  & $S_{\\rm exp}^{95}$ & $CL_{B}$ & $p(s=0)$  \\\\
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
%%'''

  m_listofkeys = m.keys()
  m_listofkeys.sort()
  for name in m_listofkeys:
    tableline = addlinetosystable(tableline,m,name)

  tableline += '''
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
\\end{tabular*}
\\end{center}
\\caption[Breakdown of upper limits.]{
Left to right: 95\\%% CL upper limits on the visible cross section
($\\langle\\epsilon\\sigma\\rangle_{\\rm obs}^{95}$) and on the number of
signal events ($S_{\\rm obs}^{95}$ ).  The third column
($S_{\\rm exp}^{95}$) shows the 95\\%% CL upper limit on the number of
signal events, given the expected number (and $\\pm 1\\sigma$
excursions on the expectation) of background events.
The last two columns
indicate the $CL_B$ value, i.e. the confidence level observed for
the background-only hypothesis, and the discovery $p$-value ($p(s = 0)$). 
\\label{table.results.exclxsec.pval.%s}}
\\end{table}
%%''' %(tabname)

  return tableline


  
def givetuplesym(m,name):
  ntuple = ( m[name][0], m[name][1], m[name][2], m[name][3] , m[name][4], m[name][5], m[name][6])
  return ntuple

def addlinetosystable(tableline,m,name):
  try:
    m.has_key(name)
  except:
    print " \n", name, "  not inside the upper limit table"
    return tableline

  printname = name
  printname = printname.replace('_','\_')
  tableline += '\n'+ printname + '''   & $%.2f$ &  $%.1f$  & ${%.1f}^{+%.1f}_{-%.1f}$ & $%.2f$ &  $%.2f$  \\\\ 
  %%''' % givetuplesym(m,name)

  
  return tableline
 

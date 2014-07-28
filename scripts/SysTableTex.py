"""
 * Project : HistFitter - A ROOT-based package for statistical data analysis      *
 * Package : HistFitter                                                           *
 * Script  : SysTableTex.py                                                       *
 *                                                                                *
 * Description:                                                                   *
 *      Script for producing LaTeX-files derived from systematics tables          *
 *      produced  by SysTable.py script                                           *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group                                                          *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
"""

def tablefragment(m,signalRegions,skiplist,chanStr,showPercent):
  """ 
  main function to transfer the set of numbers/names (=m provided by SysTable) into a LaTeX table

  @param m Set of numbers/names provided by SysTable
  @param signalRegions List of channels/regions used
  @param skiplist List of parameters/members of 'm' to be skipped (such as 'sqrtnobsa') when showing per-systematic errors
  @param chanStr String of all channels used, to be used in label of table
  @param showPercent Boolean deciding whether to show percentage for each systematic
  """
  
  tableline = ''

  tableline += '''
\\begin{table}
\\begin{center}
\\setlength{\\tabcolsep}{0.0pc}
\\begin{tabular*}{\\textwidth}{@{\\extracolsep{\\fill}}l'''

  """
  print the region names
  """ 
  for region in signalRegions:
    tableline += "c"   
  tableline += '''}
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
{\\bf Uncertainty of channel}                                   ''' 


  """
  print the total fitted (after fit) number of events
  """   
  for region in signalRegions:
    tableline += " & " + region.replace('_','\_') + "           "   

  tableline += ''' \\\\
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
%%'''

  tableline += '''
Total background expectation            '''
  for region in signalRegions:
    tableline += " &  $" + str(("%.2f" %m[region]['nfitted'])) + "$       "
  tableline += '''\\\\
%%'''


  tableline += ''' \\\\
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
%%'''


  """
  print sqrt(N_obs) - for comparison with total systematic
  """   
  tableline += '''
Total statistical $(\\sqrt{N_{\\rm exp}})$             '''
  for region in signalRegions:
    tableline += " & $\\pm " + str(("%.2f" %m[region]['sqrtnfitted'])) + "$       "
  tableline += '''\\\\
%%'''

  """
  print total systematic uncertainty
  """   
  tableline += '''
Total background systematic              '''

  for region in signalRegions:
    percentage = m[region]['totsyserr']/m[region]['nfitted'] * 100.0    
    tableline += " & $\\pm " + str(("%.2f" %m[region]['totsyserr'])) + "\ [" + str(("%.2f" %percentage)) + "\\%] $       "

  tableline += '''      \\\\
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
%%''' 


  """
  print systematic uncertainty per floated parameter (or set of parameters, if requested)
  """   
  d = m[signalRegions[0]] 
  m_listofkeys = sorted(d.iterkeys(), key=lambda k: d[k], reverse=True)

  for name in m_listofkeys:
    if name not in skiplist:
      printname = name
      printname = printname.replace('syserr_','')
      printname = printname.replace('_','\_')
      for index,region in enumerate(signalRegions):
        if index == 0:
          tableline += "\n" + printname + "      "
          
        if not showPercent:
          tableline += "   & $\\pm " + str(("%.2f" %m[region][name])) + "$       "
        else:
          percentage = m[region][name]/m[region]['nfitted'] * 100.0
          if percentage <1:
            tableline += "   & $\\pm " + str(("%.2f" %m[region][name])) + "\ [" + str(("%.2f" %percentage)) + "\\%] $       "
          else:
            tableline += "   & $\\pm " + str(("%.2f" %m[region][name])) + "\ [" + str(("%.1f" %percentage)) + "\\%] $       "
                    
          
        if index == len(signalRegions)-1:
          tableline += '''\\\\
%%'''

  """
  print table end with default Caption and Label
  """   

  tableline += '''
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
\\end{tabular*}
\\end{center}
\\caption[Breakdown of uncertainty on background estimates]{
Breakdown of the dominant systematic uncertainties on background estimates in the various signal regions.
Note that the individual uncertainties can be correlated, and do not necessarily add up quadratically to 
the total background uncertainty. The percentages show the size of the uncertainty relative to the total expected background.
\\label{table.results.bkgestimate.uncertainties.%s}}
\\end{table}
%%''' % (chanStr) 
    
  return tableline


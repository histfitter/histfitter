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

def colorShade(percent, useColorShade):

  if not useColorShade:
    return 'black'

  if percent < 1.:
    return 'lightgray'
  elif percent <10.:
    return 'gray'
  elif percent<50.:
    return 'darkgray'
  else:
    return 'black'


def tablefragment(m,signalRegions,skiplist,chanStr,showPercent,label="",caption="",useColorShade=False):
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
\\centering
\\begin{adjustbox}{width=\\textwidth}
\\scriptsize
\\begin{tabular}{l'''

  """
  print the region names
  """
  for region in signalRegions:
    tableline += "c"
  tableline += '''}
\\toprule
\\textbf{Uncertainty of channel}                                   '''


  """
  print the total fitted (after fit) number of events
  """
  for region in signalRegions:
    tableline += " & " + region.replace('_',r'\_') + "           "

  tableline += ''' \\\\
\\midrule
%%'''

  tableline += '''
Total background expectation            '''
  for region in signalRegions:
    tableline += " &  $" + str("%.2f" %m[region]['nfitted']) + "$       "
  tableline += '''\\\\
%%'''


  tableline += ''' \\\\
\\midrule
%%'''


  """
  print sqrt(N_obs) - for comparison with total systematic
  """
  tableline += '''
Total statistical $(\\sqrt{N_{\\mathrm{exp}}})$             '''
  for region in signalRegions:
    tableline += " & $\\pm " + str("%.2f" %m[region]['sqrtnfitted']) + "$       "
  tableline += '''\\\\
%%'''

  """
  print total systematic uncertainty
  """
  tableline += '''
Total background systematic              '''

  for region in signalRegions:
      percentage = (
          m[region]["totsyserr"] / m[region]["nfitted"] * 100.0
          if m[region]["nfitted"] > 0
          else 0
      )
      tableline += (
          " & $\\pm "
          + str("%.2f" % m[region]["totsyserr"])
      )
      if showPercent: tableline += fr"\ [{percentage:0.2f}\%] "
      tableline += "$       "

  tableline += '''      \\\\
\\midrule
%%'''


  """
  print systematic uncertainty per floated parameter (or set of parameters, if requested)
  """
  d = m[signalRegions[0]]
  m_listofkeys = sorted(iter(d.keys()), key=lambda k: d[k], reverse=True)

  for name in m_listofkeys:
    if name not in skiplist:
      printname = name
      printname = printname.replace('syserr_','')
      printname = printname.replace('_',r'\_')
      for index,region in enumerate(signalRegions):
        if index == 0:
          tableline += "\n" + printname + "      "

        percentage = m[region][name]/m[region]['nfitted'] * 100.0 if m[region]['nfitted']>0. else 0.

        if not showPercent:
          #tableline += "   & $\\pm " + str("%.2f" %m[region][name]) + "$       "
          tableline += f"   & \\textcolor{{{colorShade(percentage,useColorShade)}}}{{$\\pm " + str("%.2f" %m[region][name]) + "$}       "
        else:
          if percentage <1:
            #tableline += "   & $\\pm " + str("%.2f" %m[region][name]) + r"\ [" + str("%.2f" %percentage) + "\\%] $       "
            tableline += f"   & \\textcolor{{{colorShade(percentage,useColorShade)}}}{{$\\pm " + str("%.2f" %m[region][name]) + r"\ [" + str("%.2f" %percentage) + "\\%] $}       "
          else:
            tableline += f"   & \\textcolor{{{colorShade(percentage,useColorShade)}}}{{$\\pm " + str("%.2f" %m[region][name]) + r"\ [" + str("%.1f" %percentage) + "\\%] $}       "


        if index == len(signalRegions)-1:
          tableline += '''\\\\
%%'''

  """
  print table end with default Caption and Label
  """

  if caption =="":
    caption="""Breakdown of the dominant systematic uncertainties on background estimates in the various signal regions.
Note that the individual uncertainties can be correlated, and do not necessarily add up quadratically to
the total background uncertainty. The percentages show the size of the uncertainty relative to the total expected background."""

  if label =="":
    label="table.results.bkgestimate.uncertainties.%s"%(chanStr)

  tableline += """

\\bottomrule
\\end{tabular}
\\end{adjustbox}
\\caption{"""+caption+"""}
\\label{"""+label+r"""}
\end{table}"""

  return tableline


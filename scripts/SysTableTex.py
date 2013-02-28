
def tablefragment(m,table,signalRegions,skiplist,chanStr,showPercent):
  tableline = ''

  tableline += '''
\\begin{table}
\\begin{center}
\\setlength{\\tabcolsep}{0.0pc}
\\begin{tabular*}{\\textwidth}{@{\\extracolsep{\\fill}}l'''

  for region in signalRegions:
    tableline += "c"   
  tableline += '''}
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
{\\bf Uncertainty of channel}                                   ''' 

  for region in signalRegions:
    tableline += " & " + region + "           "   

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



  tableline += '''
Total statistical $(\\sqrt{N_{\\rm exp}})$             '''
  for region in signalRegions:
    tableline += " & $\\pm " + str(("%.2f" %m[region]['sqrtnfitted'])) + "$       "
  tableline += '''\\\\
%%'''

  tableline += '''
Total background systematic              '''

  for region in signalRegions:
    percentage = m[region]['totsyserr']/m[region]['nfitted'] * 100.0    
    tableline += " & $\\pm " + str(("%.2f" %m[region]['totsyserr'])) + "\ [" + str(("%.2f" %percentage)) + "\\%] $       "

  tableline += '''      \\\\
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
%%''' 


  doAsym=False
  m_listofkeys = m[signalRegions[0]].keys()
  m_listofkeys.sort()
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
#          percentage = m[region][name]/m[region]['totsyserr'] * 100.0
          percentage = m[region][name]/m[region]['nfitted'] * 100.0
          if percentage <1:
            tableline += "   & $\\pm " + str(("%.2f" %m[region][name])) + "\ [" + str(("%.2f" %percentage)) + "\\%] $       "
          else:
            tableline += "   & $\\pm " + str(("%.2f" %m[region][name])) + "\ [" + str(("%.1f" %percentage)) + "\\%] $       "
                    
          
        if index == len(signalRegions)-1:
          tableline += '''\\\\
%%'''


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


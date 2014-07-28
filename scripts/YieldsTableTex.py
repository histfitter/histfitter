"""
 * Project : HistFitter - A ROOT-based package for statistical data analysis      *
 * Package : HistFitter                                                           *
 * Script  : YieldsTableTex.py                                                    *
 *                                                                                *
 * Description:                                                                   *
 *      Script for producing LaTeX-files derived from yields tables produced      *
 *      by YieldsTable.py script                                                  *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group                                                          *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
"""

import sys
import pprint


"""
Outdated example of table -- FIXME
"""
def exampletable():

  m = {
  'names' :		( 'SR',		'TR',		'WR',		'TR + WR',	'SR (LnT)' ),
  'nobs' : 		( 1, 		80, 		202, 		282, 		1464 ),
  'Fitted_bkg_events' : ( 1.81, 0.75, 	80, 9, 		202, 14, 	282, 17, 	1464, 38 ),

  'Fitted_top_events' : ( 1.34, 0.52, 	65.0, 12.3, 	31.8, 15.8, 	96.7, 25.9, 	40.1, 11.3 ), 
  'Fitted_WZ_events' : ( 0.47, 0.40, 	11.2, 4.6, 	160.9, 27.4, 	172.1, 31.2, 	169.7, 34.1 ),
  'Fitted_top_WZ_events' : ( 1.81, 0.69, 	76.2, 11.8, 	192.6, 24.3, 	268.8, 32.1, 	209.8, 33.8 ),
  'Fitted_QCD_events' : ( 0.0, 0.3, 0.0, 	3.7, 7.6, 	9.4, 19.6, 	13.0, 27.2, 	1254.2, 51.3 ),
  'MC_exp_SM_events' : ( 1.75, 		77.76,  	189.15, 	266.91, 	1848.38 ),
  'MC_exp_top_events' : ( 1.29, 		62.9,		31.0,		93.93,		38.94 ),
  'MC_exp_WZ_events' : ( 0.46,		10.2,		146,		156.29,		154.10 ), 
  'MC_exp_QCD_events' : ( 0.00, 		4.67,		12.02,		16.69,		1655.34 ),
  }

  return m



def tablefragment(m, tabname, signalregionslist,sampleList,showBeforeFitError):
  """ 
  main function to transfer the set of numbers/names (=m provided by YieldsTable) into a LaTeX table

  @param m Set of names/numbers provided by YieldsTable.py
  @param tabname Table name
  @param signalregionslist List of channels/regions used
  @param sampleList List of sample used
  @param showBeforeFitError Boolean deciding whether to show before-fit errors
  """
  
  tableline = ''
  
  tableline += '''
\\begin{tabular*}{\\textwidth}{@{\\extracolsep{\\fill}}l'''

  for region in m['names']:
    tableline += "r"   
  
  tableline += '''}
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
{\\bf %s channel}          ''' %tabname

  """
  print the region names
  """ 
  for region in m['names']:
    regionName = region.replace("_cuts", "").replace("_meffInc", "").replace('_','\_')
    tableline += " & " + regionName + "           "   
    
  tableline += '''   \\\\[-0.05cm]
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
%%''' 

  """
  print the number of observed events
  """ 
  tableline += '''
Observed events         '''
  for n in m['nobs']:
    tableline += " & $" + ("%d" %n) + "$             "

  tableline +='''       \\\\
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
%%'''


  """
  print the total fitted (after fit) number of events
  if the N_fit - N_error extends below 0, make the error physical , meaning extend to 0
  """   
  tableline += '''
Fitted bkg events        '''
  for index, n in enumerate(m['TOTAL_FITTED_bkg_events']):
    """
    possible separation of regions with 1 or 2 digits - currently turned off in YieldsTable.py
    """   
    if m['names'][index] in signalregionslist:
      if (n - m['TOTAL_FITTED_bkg_events_err'][index]) > 0. :
        tableline += " & $" + str(("%.2f" %n)) + " \\pm " + str(("%.2f" %m['TOTAL_FITTED_bkg_events_err'][index])) +  "$         "
      else:
        print "\n YieldsTableTex.py WARNING:   negative symmetric error after fit extends below 0. for total bkg pdf:  will print asymmetric error w/ truncated negative error reaching to 0."
        tableline += " & $" + str(("%.2f" %n)) + "_{-" + str(("%.2f"%n)) + "}^{+" + str(("%.2f" %m['TOTAL_FITTED_bkg_events_err'][index])) +  "}$         "
    else:
      if (n - m['TOTAL_FITTED_bkg_events_err'][index]) > 0. :
        tableline += " & $" + str(("%.1f" %n)) + " \\pm " + str(("%.1f" %m['TOTAL_FITTED_bkg_events_err'][index])) +  "$         "
      else:
        print "\n YieldsTableTex.py WARNING:   negative symmetric error extends below 0. for total bkg pdf:  will print asymmetric error w/ truncated negative error reaching to 0."
        tableline += " & $" + str(("%.1f" %n)) + "_{-" + str(("%.1f"%n)) + "}^{+" + str(("%.1f" %m['TOTAL_FITTED_bkg_events_err'][index])) +  "}$         "
  tableline +='''     \\\\
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
%%'''


  map_listofkeys = m.keys()

  """
  print fitted number of events per sample
  if the N_fit - N_error extends below 0, make the error physical , meaning extend to 0
  """   
  for sample in sampleList:
    for name in map_listofkeys:
      if "Fitted_events_" in name: 
        sampleName = name.replace("Fitted_events_","")
        if sampleName != sample:
          continue
        
        sample = name.replace("Fitted_events_","")
        tableline += '''
        Fitted '''
        sampleName = sample
        sampleName = sampleName.replace("_","\_")
        tableline += sampleName
        tableline += ''' events        '''
        for index, n in enumerate(m[name]):
          """
          possible separation of regions with 1 or 2 digits - currently turned off in YieldsTable.py
          """   
          if m['names'][index] in signalregionslist:
            if ((n - m['Fitted_err_'+sample][index]) > 0.) or not abs(n) > 0.00001:
              tableline += " & $" + str(("%.2f" %n)) + " \\pm " + str(("%.2f" %m['Fitted_err_'+sample][index])) +  "$         "
            else:
              print "\n YieldsTableTex.py WARNING:   negative symmetric error after fit extends below 0. for sample", sample, "    will print asymmetric error w/ truncated negative error reaching to 0."
              tableline += " & $" + str(("%.2f" %n)) + "_{-" + str(("%.2f"%n)) + "}^{+" + str(("%.2f" %m['Fitted_err_'+sample][index])) +  "}$         "
          else:
            if ((n - m['Fitted_err_'+sample][index]) > 0.) or not abs(n) > 0.00001:
              tableline += " & $" + str(("%.1f" %n)) + " \\pm " + str(("%.1f" %m['Fitted_err_'+sample][index])) +  "$         "
            else:
              print "\n YieldsTableTex.py WARNING:   negative symmetric error after fit extends below 0. for sample", sample, "    will print asymmetric error w/ truncated negative error reaching to 0."
              tableline += " & $" + str(("%.1f" %n)) + "_{-" + str(("%.1f"%n)) + "}^{+" + str(("%.1f" %m['Fitted_err_'+sample][index])) +  "}$         "
        tableline +='''     \\\\
%%'''


  tableline +='''     
 \\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
%%'''

  """
  print the total expected (before fit) number of events
  if the N_fit - N_error extends below 0, make the error physical , meaning extend to 0
  """   
  
  tableline += '''
MC exp. SM events             '''
  for index, n in enumerate(m['TOTAL_MC_EXP_BKG_events']):
    if showBeforeFitError:
      if ((n - m['TOTAL_MC_EXP_BKG_err'][index]) > 0.) or not abs(n) > 0.00001:
        tableline += " & $" + str(("%.2f" %n)) + " \\pm " + str(("%.2f" %m['TOTAL_MC_EXP_BKG_err'][index])) +  "$         "
      else:
        print "\n YieldsTableTex.py WARNING:   negative error before fit extends below 0. for total bkg pdf:   will print asymmetric error w/ truncated negative error reaching to 0."
        tableline += " & $" + str(("%.2f" %n)) + "_{-" + str(("%.2f"%n)) + "}^{+" + str(("%.2f" %m['TOTAL_MC_EXP_BKG_err'][index])) +  "}$         "
    else:
      tableline += " & $" + str(("%.2f" %n)) +  "$         "
  tableline +='''     \\\\
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
%%''' 

  map_listofkeys = m.keys()

  """
  print expected number of events per sample
  if the N_fit - N_error extends below 0, make the error physical , meaning extend to 0
  """   
  for sample in sampleList:
    for name in map_listofkeys:
      if "MC_exp_events_" in name and sample in name:
        sampleName = name.replace("MC_exp_events_","")
        if sampleName != sample:
          continue
        sample = name.replace("MC_exp_events_","")
        if sample!="QCD":
            tableline += '''
        MC exp. '''
        else: 
            tableline += '''
        data-driven exp. '''

        sampleName = sample
        sampleName = sampleName.replace("_","\_")
        tableline += sampleName
        tableline += ''' events        '''
        for index, n in enumerate(m[name]):
          if m['names'][index] in signalregionslist:
            if showBeforeFitError:
              if ((n - m['MC_exp_err_'+sample][index]) > 0.) or not abs(n) > 0.00001:
                tableline += " & $" + str(("%.2f" %n)) + " \\pm " + str(("%.2f" %m['MC_exp_err_'+sample][index])) +  "$         "
              else:
                print "\n YieldsTableTex.py WARNING:   negative error before fit extends below 0. for sample", sample, "    will print asymmetric error w/ truncated negative error reaching to 0."
                tableline += " & $" + str(("%.2f" %n)) + "_{-" + str(("%.2f"%n)) + "}^{+" + str(("%.2f" %m['MC_exp_err_'+sample][index])) +  "}$         "
            else:
              tableline += " & $" + str(("%.2f" %n)) +  "$         "
          else:
            if showBeforeFitError:
              if ((n - m['MC_exp_err_'+sample][index]) > 0.) or not abs(n) > 0.00001:
                tableline += " & $" + str(("%.2f" %n)) + " \\pm " + str(("%.2f" %m['MC_exp_err_'+sample][index])) +  "$         "
              else:
                print "\n YieldsTableTex.py WARNING:   negative error before fit extends below 0. for sample", sample, "    will print asymmetric error w/ truncated negative error reaching to 0."
                tableline += " & $" + str(("%.2f" %n)) + "_{-" + str(("%.2f"%n)) + "}^{+" + str(("%.2f" %m['MC_exp_err_'+sample][index])) +  "}$         "
            else:
              tableline += " & $" + str(("%.2f" %n)) +  "$         "##           else:
        tableline +='''     \\\\
%%'''


  tableline +='''     \\\\
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
\\end{tabular*}
%%''' 

  return tableline




def tablestart():
  """
  print tabel start for LaTeX table
  """   
 
  start = '''

\\begin{table}
\\begin{center}
\\setlength{\\tabcolsep}{0.0pc}
{\\small
%%'''

  return start

def tableEndWithCaptionAndLabel(tableCaption, tableLabel):
  """
  print table end with Caption and Label given by user
  """   
 
  end = '''%%
}
\\end{center}
\\caption{%s}
\\label{%s}
\\end{table}
%%''' % (tableCaption, tableLabel)

  return end

def tableend(signalregion='3+ jets, loose',suffix='sr3jl'):
  """
  print table end with Caption and Label used by default
  """   

  end = '''%%
}
\\end{center}
\\caption{Signal region: %s. Fit results for the electron (top part) and muon (bottom part) channels, for an integrated luminosity of $1035$\,\ipb.
The results are obtained from the control regions using the discovery fit (see text for details). The fit results of the loose-not-tight regions are not shown.
Nominal MC expectations (normalised to MC cross-sections) are given for comparison. 
The Monte Carlo QCD estimates are provided for illustrational purposes only, and are not used in the fit.
The errors shown are the statistical plus systematic uncertainties, except for the error on the background estimate in the signal region, which is the systematic uncertainty only.
Uncertainties on the fitted yields are symmetric by construction, 
where the negative error is truncated when reaching to zero event yield.
}
\\label{table.results.systematics.in.logL.fit.%s}
\\end{table}
%%''' % (signalregion,suffix)

  return end



def tableend2(signalregion='3+ jets, loose',suffix='sr3jl'):
  """
  print table end with Caption and Label used by default-2
  """   
 

  end = '''%%
}
\\end{center}
\\caption{Signal region: %s. Fit results for an integrated luminosity of $1035$\,\ipb.
The results are obtained from the control regions using the discovery fit (see text for details). 
Nominal MC expectations (normalised to MC cross-sections) are given for comparison. 
The Monte Carlo QCD estimates are provided for illustrational purposes only, and are not used in the fit.
The errors shown are the statistical plus systematic uncertainties, except for the error on the background estimate in the signal region, which is the systematic uncertainty only.
%%All presented errors have been derived using MINOS.
Uncertainties on the fitted yields are symmetric by construction, 
where the negative error is truncated when reaching to zero event yield.
}
\\label{table.results.systematics.in.logL.fit.%s}
\\end{table}
%%''' % (signalregion,suffix)

  return end




def tableend3(suffix='sr3jl'):
  """
  print table end with Caption and Label used by default-3
  """   
 

  end = '''%%
}
\\end{center}
\caption{ Background fit results for the S3 (top part) and S4 (bottom part) signal regions, for an integrated luminosity of $20.5$~\\ifb.
%%The results are obtained from the control regions using the discovery fit (see text for details). The fit results of the loose-not-tight regions are not shown.
Nominal MC expectations (normalised to MC cross-sections) are given for comparison. 
%%The Monte Carlo QCD estimates are provided for illustrational purposes only, and are not used in the fit.
The errors shown are the statistical plus systematic uncertainties for control regions, while only the statistical errors are shown for signal and validation regions, in the case of a background only fit.
Uncertainties on the fitted yields are symmetric by construction, 
where the negative error is truncated when reaching to zero event yield.
%%, except for the error on the background estimate in the signal region, which is the systematic uncertainty only.
}
\\label{table.results.systematics.in.logL.fit.%s}
\\end{table}
%%''' %(suffix)

  return end


def tableend4(rList, suffix='sr3jl', mentionCh=''):
  """
  print table end with Caption and Label used by default-4
  """   
 

  regionsList = []
  for r in rList:
      regionsList.append(r.replace('_','\_'))

  mentionCh = mentionCh.replace('_','\_')

  tomention = ''
  if len(mentionCh)>0:
      tomention = 'related to the analysis containing region %s, ' % mentionCh

  end = '''%%
}
\\end{center}
\caption{ Background fit results for the '''

  nRegions = len(regionsList)
  for index, region in enumerate(regionsList):
    if index == 0 :
      end +=  region
    elif index < nRegions-1:
      end += ", " + region 
    else:
      end += " and " + region
      
  end += ''' region(s), %s for an integrated luminosity of $20.5$~\\ifb.
%%The results are obtained from the control regions using the discovery fit (see text for details). The fit results of the loose-not-tight regions are not shown.
Nominal MC expectations (normalised to MC cross-sections) are given for comparison. 
%%The Monte Carlo QCD estimates are provided for illustrational purposes only, and are not used in the fit.
The errors shown are the statistical plus systematic uncertainties.
%%, except for the error on the background estimate in the signal region, which is the systematic uncertainty only.
Uncertainties on the fitted yields are symmetric by construction, 
where the negative error is truncated when reaching to zero event yield.
}
\\label{table.results.yields.fit.%s}
\\end{table}
%%''' %(tomention,suffix)

  return end




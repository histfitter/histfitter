import sys

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



def tablefragment(m, channel, signalregionslist):

  tableline = ''
  
  tableline += '''
\\begin{tabular*}{\\textwidth}{@{\\extracolsep{\\fill}}l'''

  for region in m['names']:
    tableline += "r"   
  
  tableline += '''}
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
{\\bf %s channel}          ''' %channel
  for region in m['names']:
    tableline += " & " + region + "           "   

  tableline += '''   \\\\[-0.05cm]
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
%%''' 

  tableline += '''
Observed events         '''
  for n in m['nobs']:
    tableline += " & $" + str(int(n)) + "$             "

  tableline +='''       \\\\
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
%%'''
  
  tableline += '''
Fitted bkg events        '''
  for index, n in enumerate(m['Fitted_bkg_events']):
    if m['names'][index] in signalregionslist:
      tableline += " & $" + str(("%.2f" %n)) + " \\pm " + str(("%.2f" %m['Fitted_bkg_events_err'][index])) +  "$         "
    else:
      tableline += " & $" + str(("%.1f" %n)) + " \\pm " + str(("%.1f" %m['Fitted_bkg_events_err'][index])) +  "$         "
  tableline +='''     \\\\
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
%%'''

  tableline += '''
Fitted top events        '''
  for index, n in enumerate(m['Fitted_top_events']):
    if m['names'][index] in signalregionslist:
      tableline += " & $" + str(("%.2f" %n)) + " \\pm " + str(("%.2f" %m['Fitted_top_events_err'][index])) +  "$         "
    else:
      tableline += " & $" + str(("%.1f" %n)) + " \\pm " + str(("%.1f" %m['Fitted_top_events_err'][index])) +  "$         "
  tableline +='''     \\\\
%%'''

  tableline += '''
Fitted WZ events        '''
  for index, n in enumerate(m['Fitted_WZ_events']):
    if m['names'][index] in signalregionslist:
      tableline += " & $" + str(("%.2f" %n)) + " \\pm " + str(("%.2f" %m['Fitted_WZ_events_err'][index])) +  "$         "
    else:
      tableline += " & $" + str(("%.1f" %n)) + " \\pm " + str(("%.1f" %m['Fitted_WZ_events_err'][index])) +  "$         "
  tableline +='''     \\\\
%%'''

##   tableline += '''
## Fitted top+WZ events        '''
##   for index, n in enumerate(m['Fitted_top_WZ_events']):
##     if m['names'][index] in signalregionslist:
##       tableline += " & $" + str(("%.2f" %n)) + " \\pm " + str(("%.2f" %m['Fitted_top_WZ_events_err'][index])) +  "$         "
##     else:
##       tableline += " & $" + str(("%.1f" %n)) + " \\pm " + str(("%.1f" %m['Fitted_top_WZ_events_err'][index])) +  "$         "
##   tableline +='''     \\\\
## %%'''


##   tableline += '''
## Fitted other BGs events        '''
##   for index, n in enumerate(m['Fitted_BG_events']):
##     if m['names'][index] in signalregionslist:
##       tableline += " & $" + str(("%.2f" %n)) + " \\pm " + str(("%.2f" %m['Fitted_BG_events_err'][index])) +  "$         "
##     else:
##       tableline += " & $" + str(("%.1f" %n)) + " \\pm " + str(("%.1f" %m['Fitted_BG_events_err'][index])) +  "$         "
##   tableline +='''     \\\\
## %%'''

##   tableline += '''
## Fitted QCD \\& fake lepton events       '''
##   for index, n in enumerate(m['Fitted_QCD_events']):
##     if m['names'][index] in signalregionslist:
##       tableline += " & $" + str(("%.2f" %n)) + " \\pm " + str(("%.2f" %m['Fitted_QCD_events_err'][index])) +  "$         "
##     else:
##       tableline += " & $" + str(("%.1f" %n)) + " \\pm " + str(("%.1f" %m['Fitted_QCD_events_err'][index])) +  "$         "
##   tableline +='''     \\\\    '''

  tableline +='''
  \\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
 %%'''
  
#########  #########
########## expected
######### #########

  tableline += '''
MC exp. SM events             '''
  for n in m['MC_exp_SM_events']:
       tableline += " & $" + str(("%.2f" %n)) +  "$         "
  tableline +='''     \\\\
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
%%''' 

  tableline += '''
MC exp. top events             '''
  for n in m['MC_exp_top_events']:
       tableline += " & $" + str(("%.2f" %n)) +  "$         "
  tableline +='''     \\\\
%%''' 

  tableline += '''
MC exp. WZ events             '''
  for n in m['MC_exp_WZ_events']:
       tableline += " & $" + str(("%.2f" %n)) +  "$         "
  tableline +='''     \\\\
%%''' 

##   tableline += '''
## MC exp. top+WZ events             '''
##   for n in m['MC_exp_top_WZ_events']:
##        tableline += " & $" + str(("%.2f" %n))  +  "$         "
##   tableline +='''     \\\\
## %%''' 

##   tableline += '''
## MC exp. other BGs events             '''
##   for n in m['MC_exp_BG_events']:
##        tableline += " & $" + str(("%.2f" %n))  +  "$         "
##   tableline +='''     \\\\
## %%''' 

  
##   tableline += '''
## Data-driven QCD \\& fake lepton events             '''
##   for n in m['MC_exp_QCD_events']:
##        tableline += " & $" + str(("%.2f" %n))  +  "$         "
##   tableline +='''     \\\\ '''

  tableline +='''
\\noalign{\\smallskip}\\hline\\noalign{\\smallskip}
\\end{tabular*}
%%''' 

  return tableline


################


def tablestart():

  start = '''

\\begin{table}
\\begin{center}
\\setlength{\\tabcolsep}{0.0pc}
{\\small
%%'''

  return start


def tableend(signalregion='3+ jets, loose',suffix='sr3jl'):

  end = '''%%
}
\\end{center}
\\caption{Signal region: %s. Fit results for the electron (top part) and muon (bottom part) channels, for an integrated luminosity of $1035$\,\ipb.
The results are obtained from the control regions using the discovery fit (see text for details). The fit results of the loose-not-tight regions are not shown.
Nominal MC expectations (normalised to MC cross-sections) are given for comparison. 
The Monte Carlo QCD estimates are provided for illustrational purposes only, and are not used in the fit.
The errors shown are the statistical plus systematic uncertainties, except for the error on the background estimate in the signal region, which is the systematic uncertainty only.}
\\label{table.results.systematics.in.logL.fit.%s}
\\end{table}
%%''' % (signalregion,suffix)

  return end



def tableend2(signalregion='3+ jets, loose',suffix='sr3jl'):

  end = '''%%
}
\\end{center}
\\caption{Signal region: %s. Fit results for an integrated luminosity of $1035$\,\ipb.
The results are obtained from the control regions using the discovery fit (see text for details). 
Nominal MC expectations (normalised to MC cross-sections) are given for comparison. 
The Monte Carlo QCD estimates are provided for illustrational purposes only, and are not used in the fit.
The errors shown are the statistical plus systematic uncertainties, except for the error on the background estimate in the signal region, which is the systematic uncertainty only.
All presented errors have been derived using MINOS.}
\\label{table.results.systematics.in.logL.fit.%s}
\\end{table}
%%''' % (signalregion,suffix)

  return end




def tableend3(suffix='sr3jl'):

  end = '''%%
}
\\end{center}
\caption{ Background fit results for the S3 (top part) and S4 (bottom part) signal regions, for an integrated luminosity of $4.7$~\\ifb.
%%The results are obtained from the control regions using the discovery fit (see text for details). The fit results of the loose-not-tight regions are not shown.
Nominal MC expectations (normalised to MC cross-sections) are given for comparison. 
%%The Monte Carlo QCD estimates are provided for illustrational purposes only, and are not used in the fit.
The errors shown are the statistical plus systematic uncertainties.}
%%, except for the error on the background estimate in the signal region, which is the systematic uncertainty only.}
\\label{table.results.systematics.in.logL.fit.%s}
\\end{table}
%%''' %(suffix)

  return end


def tableend4(regionsList, suffix='sr3jl'):

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
      
  end += ''' regions, for an integrated luminosity of $4.7$~\\ifb.
%%The results are obtained from the control regions using the discovery fit (see text for details). The fit results of the loose-not-tight regions are not shown.
Nominal MC expectations (normalised to MC cross-sections) are given for comparison. 
%%The Monte Carlo QCD estimates are provided for illustrational purposes only, and are not used in the fit.
The errors shown are the statistical plus systematic uncertainties.}
%%, except for the error on the background estimate in the signal region, which is the systematic uncertainty only.}
\\label{table.results.systematics.in.logL.fit.%s}
\\end{table}
%%''' %(suffix)

  return end

#print tablestart(), tableframent(m), tableend()



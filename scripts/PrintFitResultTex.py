
def tablefragment(m,sr):
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
  #m_listofkeys.sort()
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


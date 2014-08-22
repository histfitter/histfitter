# David Cote, October 2013
# Examples of optional] user-specific code to fill map of sytematics with the YieldsTable.py script
# Namemap can be used to merged systematics 
# namemap can be used to re-name the systematics arbitrarily in the output latex Table
namemap={}

namemap['fake lepton background']=[]
namemap['charge mis-identification background']=[]
namemap['theory unc. on ttbar+W/Z/H, top+Z']=[]
namemap['theory unc. on dibosons']=[]
namemap['jet and met']=[]
namemap['b-jet tagging']=[]
namemap['lepton reconstruction']=[]
namemap['trigger, luminosity and pile-up']=[]
namemap['MC statistics']=[]

w = Util.GetWorkspaceFromFile(wsFileName,'w')
result = w.obj("RooExpandedFitResult_afterFit")
fpf = result.floatParsFinal() 
for idx in range(fpf.getSize()):
    parname = fpf[idx].GetName()
    if parname.startswith("gamma_shape_mcstat_fakes") or parname=="alpha_Fakes_El" or parname=="alpha_Fakes_Mu" or parname=="alpha_fakes1bto3b":
        namemap['fake lepton background'].append(parname)

    elif parname.startswith("gamma_shape_mcstat_misId_") or parname=="alpha_FlipWgt":
        namemap['charge mis-identification background'].append(parname)

    elif parname.startswith("gamma_shape_mcstat_"): 
        namemap['MC statistics'].append(parname)

    elif parname=="alpha_theoryUncertSingleTopZ" or parname=="alpha_ttVAlpgen" or parname=="alpha_ttVjetMatching" or parname=="alpha_xSecTTW" or parname=="alpha_xSecTTZ":
        namemap['theory unc. on ttbar+W/Z/H, top+Z'].append(parname)

    elif parname=="alpha_theoryUncertWV" or parname=="alpha_theoryUncertZZ" or  parname=="alpha_pdfWgt":
        namemap['theory unc. on dibosons'].append(parname)

    elif parname=="alpha_JES" or parname=="alpha_JER" or parname=="alpha_RESOST" or parname=="alpha_SCALEST":
        namemap['jet and met'].append(parname)

    elif parname=="alpha_bTag":
        namemap['b-jet tagging'].append(parname)

    elif parname=="alpha_elReco" or parname=="alpha_muReco":
        namemap['lepton reconstruction'].append(parname)

    elif parname=="Lumi" or parname=="alpha_pileup" or parname=="alpha_triggerWgt":
        namemap['trigger, luminosity and pile-up'].append(parname)

    elif parname!="mu_SRall_disc":
        print "WARNING: don't know what to do with nuisance parameter: %s. It will be ignored."%parname


##### Note: it's also fine to simply hard-code namemap as e.g. below:

#namemap = { 'jet energy scale' : ['alpha_normJES', 'alpha_JES'],
#            'combined theory' : ['alpha_normgen_tt', 'alpha_normps_tt', 'alpha_normrad_tt', 'alpha_normfac_tt', 'alpha_normren_tt', 'alpha_normscales_wjets', 'alpha_normfac_wjets', 'alpha_normmatch_wjets', 'alpha_normrad_wjets', 'alpha_gen_sts', 'alpha_rad_st', 'alpha_gen_stwt', 'alpha_ps_stwt', 'alpha_drds_stwt', 'alpha_theory_diboson', 'alpha_theory_ttv', 'alpha_theory_wh', 'alpha_theory_zh', 'alpha_theory_zjets' ],
#            'single top' : ['alpha_gen_sts', 'alpha_rad_st', 'alpha_gen_stwt', 'alpha_ps_stwt', 'alpha_drds_stwt'],
#            'b-tagging' : ['alpha_normbTag', 'alpha_bTag']
#            }




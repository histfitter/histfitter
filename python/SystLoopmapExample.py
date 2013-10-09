# David Cote, October 2013
# Example of user-specific code to fill map of sytematics to be merged
loopmap={}

loopmap['fake lepton background']=[]
loopmap['charge mis-identification background']=[]
loopmap['theory unc. on ttbar+W/Z/H, top+Z']=[]
loopmap['theory unc. on dibosons']=[]
loopmap['jet and met']=[]
loopmap['b-jet tagging']=[]
loopmap['lepton reconstruction']=[]
loopmap['trigger, luminosity and pile-up']=[]
loopmap['MC statistics']=[]
loopmap['PDF']=[]

w = Util.GetWorkspaceFromFile(wsFileName,'w')
result = w.obj("RooExpandedFitResult_afterFit")
fpf = result.floatParsFinal() 
for idx in range(fpf.getSize()):
    parname = fpf[idx].GetName()
    if parname.startswith("gamma_shape_mcstat_fakes") or parname=="alpha_Fakes_El" or parname=="alpha_Fakes_Mu" or parname=="alpha_fakes1bto3b":
        loopmap['fake lepton background'].append(parname)

    elif parname.startswith("gamma_shape_mcstat_misId_") or parname=="alpha_FlipWgt":
        loopmap['charge mis-identification background'].append(parname)

    elif parname.startswith("gamma_shape_mcstat_"): 
        loopmap['MC statistics'].append(parname)

    elif parname=="alpha_theoryUncertSingleTopZ" or parname=="alpha_ttVAlpgen" or parname=="alpha_ttVjetMatching" or parname=="alpha_xSecTTW" or parname=="alpha_xSecTTZ":
        loopmap['theory unc. on ttbar+W/Z/H, top+Z'].append(parname)

    elif parname=="alpha_theoryUncertWV" or parname=="alpha_theoryUncertZZ":
        loopmap['theory unc. on dibosons'].append(parname)

    elif parname=="alpha_pdfWgt":
        loopmap['PDF'].append(parname)

    elif parname=="alpha_JES" or parname=="alpha_JER" or parname=="alpha_RESOST" or parname=="alpha_SCALEST":
        loopmap['jet and met'].append(parname)

    elif parname=="alpha_bTag":
        loopmap['b-jet tagging'].append(parname)

    elif parname=="alpha_elReco" or parname=="alpha_muReco":
        loopmap['lepton reconstruction'].append(parname)

    elif parname=="Lumi" or parname=="alpha_pileup" or parname=="alpha_triggerWgt":
        loopmap['trigger, luminosity and pile-up'].append(parname)

    elif parname!="mu_SRall_disc":
        print "WARNING: don't know what to do with nuisance parameter: %s. It will be ignored."%parname




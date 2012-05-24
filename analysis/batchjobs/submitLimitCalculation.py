import os

####### CONFIGURATION #######

configFile = 'CombinedKFactorFit_5Channel_SoftHard.py'

dryRun =True
calculatorType = 2 # 2 for asymptotic calculator / 0 for toys
nToys = -1
nJobsPerPoint = 1 
seed = 5 #for parallelized toys set seed in submission loop
runLfromPws = True
#for later
sample = "SM_GG_onestepCC"
#############################



mode = 'l'
if '_p_' in configFile:
    mode = 'p'
elif '_l_' in configFile:
    mode = 'l'

points = ['SM_GG_onestepCC_205_125_45', 'SM_GG_onestepCC_225_185_145', 'SM_GG_onestepCC_227_215_202', 'SM_GG_onestepCC_235_155_75', 'SM_GG_onestepCC_245_125_5', 'SM_GG_onestepCC_255_215_175', 'SM_GG_onestepCC_257_245_232', 'SM_GG_onestepCC_265_185_105', 'SM_GG_onestepCC_275_155_35', 'SM_GG_onestepCC_285_245_205', 'SM_GG_onestepCC_287_275_262', 'SM_GG_onestepCC_295_215_135', 'SM_GG_onestepCC_305_185_65', 'SM_GG_onestepCC_315_275_235', 'SM_GG_onestepCC_317_305_292', 'SM_GG_onestepCC_325_245_165', 'SM_GG_onestepCC_335_215_95', 'SM_GG_onestepCC_345_185_25', 'SM_GG_onestepCC_345_305_265', 'SM_GG_onestepCC_355_275_195', 'SM_GG_onestepCC_365_245_125', 'SM_GG_onestepCC_375_215_55', 'SM_GG_onestepCC_385_305_225', 'SM_GG_onestepCC_395_275_155', 'SM_GG_onestepCC_397_385_372', 'SM_GG_onestepCC_405_245_85', 'SM_GG_onestepCC_415_215_15', 'SM_GG_onestepCC_425_305_185', 'SM_GG_onestepCC_425_385_345', 'SM_GG_onestepCC_435_275_115', 'SM_GG_onestepCC_445_245_45', 'SM_GG_onestepCC_465_305_145', 'SM_GG_onestepCC_465_385_305', 'SM_GG_onestepCC_475_275_75', 'SM_GG_onestepCC_477_465_452', 'SM_GG_onestepCC_485_245_5', 'SM_GG_onestepCC_505_305_105', 'SM_GG_onestepCC_505_385_265', 'SM_GG_onestepCC_505_465_425', 'SM_GG_onestepCC_515_275_35', 'SM_GG_onestepCC_545_305_65', 'SM_GG_onestepCC_545_385_225', 'SM_GG_onestepCC_545_465_385', 'SM_GG_onestepCC_557_545_532', 'SM_GG_onestepCC_585_305_25', 'SM_GG_onestepCC_585_385_185', 'SM_GG_onestepCC_585_465_345', 'SM_GG_onestepCC_585_545_505', 'SM_GG_onestepCC_625_385_145', 'SM_GG_onestepCC_625_465_305', 'SM_GG_onestepCC_625_545_465', 'SM_GG_onestepCC_637_625_612', 'SM_GG_onestepCC_665_385_105', 'SM_GG_onestepCC_665_465_265', 'SM_GG_onestepCC_665_545_425', 'SM_GG_onestepCC_665_625_585', 'SM_GG_onestepCC_705_385_65', 'SM_GG_onestepCC_705_465_225', 'SM_GG_onestepCC_705_545_385', 'SM_GG_onestepCC_705_625_545', 'SM_GG_onestepCC_717_705_692', 'SM_GG_onestepCC_745_385_25', 'SM_GG_onestepCC_745_465_185', 'SM_GG_onestepCC_745_545_345', 'SM_GG_onestepCC_745_625_505', 'SM_GG_onestepCC_745_705_665', 'SM_GG_onestepCC_785_465_145', 'SM_GG_onestepCC_785_545_305', 'SM_GG_onestepCC_785_625_465', 'SM_GG_onestepCC_785_705_625', 'SM_GG_onestepCC_797_785_772', 'SM_GG_onestepCC_825_465_105', 'SM_GG_onestepCC_825_545_265', 'SM_GG_onestepCC_825_625_425', 'SM_GG_onestepCC_825_705_585', 'SM_GG_onestepCC_825_785_745', 'SM_GG_onestepCC_865_465_65', 'SM_GG_onestepCC_865_545_225', 'SM_GG_onestepCC_865_625_385', 'SM_GG_onestepCC_865_705_545', 'SM_GG_onestepCC_865_785_705', 'SM_GG_onestepCC_877_865_852', 'SM_GG_onestepCC_905_465_25', 'SM_GG_onestepCC_905_545_185', 'SM_GG_onestepCC_905_625_345', 'SM_GG_onestepCC_905_705_505', 'SM_GG_onestepCC_905_785_665', 'SM_GG_onestepCC_905_865_825', 'SM_GG_onestepCC_945_545_145', 'SM_GG_onestepCC_945_625_305', 'SM_GG_onestepCC_945_705_465', 'SM_GG_onestepCC_945_785_625', 'SM_GG_onestepCC_945_865_785', 'SM_GG_onestepCC_957_945_932', 'SM_GG_onestepCC_985_545_105', 'SM_GG_onestepCC_985_625_265', 'SM_GG_onestepCC_985_705_425', 'SM_GG_onestepCC_985_785_585', 'SM_GG_onestepCC_985_865_745', 'SM_GG_onestepCC_985_945_905', 'SM_GG_onestepCC_1025_545_65', 'SM_GG_onestepCC_1025_625_225', 'SM_GG_onestepCC_1025_705_385', 'SM_GG_onestepCC_1025_785_545', 'SM_GG_onestepCC_1025_865_705', 'SM_GG_onestepCC_1025_945_865', 'SM_GG_onestepCC_1037_1025_1012', 'SM_GG_onestepCC_1065_545_25', 'SM_GG_onestepCC_1065_625_185', 'SM_GG_onestepCC_1065_705_345', 'SM_GG_onestepCC_1065_785_505', 'SM_GG_onestepCC_1065_865_665', 'SM_GG_onestepCC_1065_945_825', 'SM_GG_onestepCC_1065_1025_985', 'SM_GG_onestepCC_1105_625_145', 'SM_GG_onestepCC_1105_705_305', 'SM_GG_onestepCC_1105_785_465', 'SM_GG_onestepCC_1105_865_625', 'SM_GG_onestepCC_1105_945_785', 'SM_GG_onestepCC_1105_1025_945', 'SM_GG_onestepCC_1117_1105_1092', 'SM_GG_onestepCC_1145_625_105', 'SM_GG_onestepCC_1145_705_265', 'SM_GG_onestepCC_1145_785_425', 'SM_GG_onestepCC_1145_865_585', 'SM_GG_onestepCC_1145_945_745', 'SM_GG_onestepCC_1145_1025_905', 'SM_GG_onestepCC_1145_1105_1065', 'SM_GG_onestepCC_1185_625_65', 'SM_GG_onestepCC_1185_705_225', 'SM_GG_onestepCC_1185_785_385', 'SM_GG_onestepCC_1185_865_545', 'SM_GG_onestepCC_1185_945_705', 'SM_GG_onestepCC_1185_1025_865', 'SM_GG_onestepCC_1185_1105_1025']



# remove stuff in the dirs above...?
## if len(points)>=130:
##     print "Deleting results/data/config %s*"%(configFile)
##     os.system('rm results/%s*'%(configFile))
##     os.system('rm data/%s*'%(configFile))
##     os.system('rm config/%s*'%(configFile))

SusyFitterDir = os.getenv("SUSYFITTER")

logDir       = "%s/submit/logs/limitCalcuation/%s_%s"       % (SusyFitterDir,mode,configFile.strip(".py"))
if runLfromPws:
    workspaceDir = "%s/submit/workspaces/%s_%s" % (SusyFitterDir,"p",configFile.strip(".py"))
else:
    workspaceDir = "%s/submit/workspaces/%s_%s" % (SusyFitterDir,mode,configFile.strip(".py"))
resultsDir = "%s/submit/results/%s_%s" % (SusyFitterDir,mode,configFile.strip(".py"))


os.system("mkdir -p %s " % (logDir))
os.system("mkdir -p %s " % (resultsDir))


for point in points:
    for job in range(0,nJobsPerPoint):
        cmd = "bsub -q 1nd -R 'hname!=lxbsq2311 && hname!=lxbsp20b26 && hname!=lxbsp20b14 && hname!=lxbsq2015 && hname!=lxbsp1543 && hname!=lxbsp2130 && hname!=lxbsp2209 && hname!=lxbsp20b06 && hname!=lxbrf18b01 && hname!=lxbsp2409 && hname!=lxbsp21b34' -e "+logDir+"/out_"+str(point)+"_"+str(job)+".log.e -o "+logDir+"/out_"+str(point)+"_"+str(job)+".log.o runLimitCalculation.sh -m '"+mode+"' -p '"+SusyFitterDir+"' -g "+point+" -w "+workspaceDir+" -r "+resultsDir+" -n "+str(nToys)+" -c "+str(calculatorType)+" -j "+str(job)+" "+SusyFitterDir+"/test.log"

        if dryRun:
            print cmd
            print ""
        else:
            print cmd
            os.system(cmd)
            print ""



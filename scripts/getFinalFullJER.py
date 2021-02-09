#scripts to handle FullJER trees:                                                            #
# myTree_JER_NP1_up = (myTree_JER_NP1_MC_up - myTree_JER_NP1_PD_up) + myTree_nominal         #
# myTree_JER_NP1_down = (myTree_JER_NP1_MC_down - myTree_JER_NP1_PD_down) + myTree_nominal   #
#                                                                                            #
# for problems contact luigi.longo@cern.ch                                                                        #
##############################################################################################
import ROOT 
import logging
from ROOT import gROOT, TChain, TFile, SetOwnership,TDirectory
import os,sys,subprocess
from copy import deepcopy
import json,argparse,time

class handleFullJERSyst(object):


      def __init__(self,name = "FullJERHandler"):

          self.name = name
          self.path = ""
          self.leaf = "weight"
          self.cut = "true"
          self.samples = ""
          self.nomName = "_NONE"
          self.mc16aTag = "mc16a"
          self.mc16dTag = "mc16d"
          self.mc16eTag = "mc16e"
          self.tcInMaps = {}
          self.mapTreeName = {}


      def getTChainInMaps(self):


          if os.path.isdir(self.path): self.path += "/*.root"
          if not self.path[-5:]==".root": self.path += "/*.root" 
         
          ls = subprocess.Popen("ls "+self.path, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE) 
          stdout, stderr = ls.communicate()
    

          files = []
          for  f in stdout.split('\n'):
               if not f=="": files.append(f)
 
          if len(files) == 0 or not stderr == "": 
             logging.error("Error reading %s" % (self.path))
             logging.error(stderr) 
             sys.exit(-1)

          for fName in files:
              logging.info("reading %s" % (fName))
              nameTrees = []
              f = TFile(fName)
              for el in f.GetListOfKeys():
                  if el.GetClassName()=="TTree" or el.GetClassName()=="TChain" or el.GetClassName()=="TNtuple": 
                     toBeUsed = False
                     for sample in self.samples.split(","):
                         #if sample in el.GetName():
                         if sample in fName+el.GetName(): 
                            toBeUsed = True
                            break
                     if toBeUsed and not el.GetName() in nameTrees: 
                        nameTrees.append(el.GetName())
              f.Close() 

              for name in nameTrees:
                  tc = TChain(name)
                  tc.Add(fName)
                  SetOwnership(tc, False)
                  self.tcInMaps[name+";"+fName] = tc


      def getFullJERTree(self):

          self.getTChainInMaps()

          if self.samples == "":
             logging.error("MC Sample not specified")
             sys.exit(-1)


          Samples = self.samples.split(",")
          mapDict = {}

          logging.info("FullJER uncertainties will be built following these expressions")
          logging.info("  - myTree_JET_syst_up = (myTree_JET_syst_up - myTree_JET_PDSmear_syst_up) + myTree%s" %(self.nomName))
          logging.info("  - myTree_JET_syst_down = (myTree_JET_syst_down - myTree_JET_PDSmear_syst_down) + myTree%s" %(self.nomName))
          logging.info("for the following samples: ")

          for sample in Samples:
          
              logging.info("  * %s" %(sample))

              nominalMC16a= "" 
              nominalMC16d= "" 
              nominalMC16e= "" 

              mapDict[sample] = {}
              #print self.tcInMaps.keys() 
              for kName in self.tcInMaps.keys():
                  if sample in kName:
                     if self.nomName in kName: 
                       if nominalMC16a=="" or nominalMC16d=="" or nominalMC16e=="":
                         if self.mc16aTag in kName: nominalMC16a = kName
                         elif self.mc16dTag in kName: nominalMC16d = kName
                         elif self.mc16eTag in kName: nominalMC16e = kName
                         else: 
                          logging.warning("not found any splitting in MC campaigns using the following tag: %s, %s, %s" % (self.mc16aTag,self.mc16dTag,self.mc16eTag))
                       else:
                         break
    
              if not nominalMC16a=="": mapDict[sample][self.mc16aTag] = {}
              if not nominalMC16d=="": mapDict[sample][self.mc16dTag] = {}
              if not nominalMC16e=="": mapDict[sample][self.mc16eTag] = {}
              #print mapDict
              if len(mapDict[sample].keys()) == 0: 
                 logging.warning("%s nominal not found for any of the MC tags: %s, %s, %s " % (sample,self.mc16aTag,self.mc16dTag,self.mc16eTag))
                 logging.warning("skipping sample %s" %(sample))
                 continue
    
              for k in mapDict[sample].keys(): mapDict[sample][k] = {}
    
              for kName in self.tcInMaps.keys():
                  if sample in kName:
                     if "JET_JER" in kName and "__2" in kName: 
                         nameNoPDS = kName.replace("__2","__1")
                         if nameNoPDS in self.tcInMaps.keys():
                            #print "Full", nameNoPDS.split(";")[0]
                            #print "Sample", nominalMC16d.split(";")[0].replace(self.nomName,"")+"_"
                            #print "Syst", nameNoPDS.split(";")[0].replace(nominalMC16d.split(";")[0].replace(self.nomName,"")+"_","")
                            if self.mc16aTag in nameNoPDS: mapDict[sample][self.mc16aTag][nameNoPDS.split(";")[0].replace(nominalMC16a.split(";")[0].replace(self.nomName,"")+"_","")] = (nominalMC16a,kName,nameNoPDS) 
                            if self.mc16dTag in nameNoPDS: mapDict[sample][self.mc16dTag][nameNoPDS.split(";")[0].replace(nominalMC16d.split(";")[0].replace(self.nomName,"")+"_","")] = (nominalMC16d,kName,nameNoPDS) 
                            if self.mc16eTag in nameNoPDS: mapDict[sample][self.mc16eTag][nameNoPDS.split(";")[0].replace(nominalMC16e.split(";")[0].replace(self.nomName,"")+"_","")] = (nominalMC16e,kName,nameNoPDS) 
                         else:
                            logging.warning("not found the corresponding  MC syst for %s" % (nameNoPDS))

          logging.info("Full JER Map: ")
          outjson = json.dumps(mapDict, indent=4)
          print outjson




          for sample in mapDict.keys():
              for mcTag in mapDict[sample].keys():
                  for syst in mapDict[sample][mcTag].keys():

                      def writeRDF(sampleName,mcTag,syst,tc,treeOrigName,sign,column):
            
                          RDF = ROOT.ROOT.RDataFrame                          
                          TreeName=sampleName+"_"+syst
                          print TreeName
                          FileName="FullJER_tmp_"+sample+"_"+mcTag+"_"+treeOrigName+".root" 
                          # print column
                          rdframeold = RDF(tc)
                          tmpFileName = "tmp"+str(time.time()).replace(".","_")+".root"
                          tree = rdframeold.Define("oldweight",self.leaf)
                          listNames = ROOT.vector('string')()
                          for c in column: 
                             if c != self.leaf: listNames.push_back(c)
                          listNames.push_back('oldweight')
                          tree.Snapshot(TreeName,tmpFileName,listNames)
                          del tree
                          del rdframeold                         
 
                          tmpTC = TChain(TreeName)
                          tmpTC.Add(tmpFileName) 
                            
                          rdSample = RDF(tmpTC)
                          """
                          #LUIGI
                          colRD =  rdSample.GetColumnNames()
                          for i in range(0,len(colRD)):
                              if colRD[i] == "oldweight":
                                 colRD[i] = self.leaf
                                 break
                          """
            
                          outRDF = rdSample.Filter(self.cut,"User cut - "+sampleName+" - ").Define(self.leaf,'({})*oldweight'.format(sign))
                          cutflow_report = outRDF.Report()
                          cutflow_report.Print()
                          outRDF.Snapshot(TreeName,FileName,column)

                          rm = subprocess.Popen("rm "+tmpFileName, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                          stdout, stderr = rm.communicate()
                          if not stderr == "":
                             logging.warning("not able to remove the temporary root file tmp.root")
                          del outRDF
                          del rdSample
                          del tmpTC

                      def GetBranchesName(nom,systPDS,systMC):

                          listNames = ROOT.vector('string')()
                          nomBranches = []
                          systPDSBranches = []
                          systMCBranches = []
                          for el in nom.GetListOfBranches(): nomBranches.append(el.GetName())
                          for el in systPDS.GetListOfBranches(): systPDSBranches.append(el.GetName())
                          for el in systMC.GetListOfBranches(): systMCBranches.append(el.GetName())

                          for nameBr in nomBranches:
                              if nameBr in systPDSBranches and nameBr in systMCBranches: listNames.push_back(nameBr)
                              else:
                                 if not nameBr in systPDSBranches: logging.warning("%s missing in %s" %(nameBr,systPDS.GetName()))
                                 if not nameBr in systMCBranches: logging.warning("%s missing in %s" %(nameBr,systMC.GetName()))

                          return listNames
                                 
                          

                      logging.info("Defining syst %s" % (syst))
                      nominal = mapDict[sample][mcTag][syst][0]
                      PDSmear = mapDict[sample][mcTag][syst][1]
                      MCSmear = mapDict[sample][mcTag][syst][2]

                      columns = GetBranchesName(self.tcInMaps[nominal],self.tcInMaps[PDSmear],self.tcInMaps[MCSmear])

                      writeRDF(sample,mcTag,syst,self.tcInMaps[nominal],"Nominal_"+syst,"1.",columns)
                      writeRDF(sample,mcTag,syst,self.tcInMaps[PDSmear],"PDSmear_"+syst,"-1.",columns)
                      writeRDF(sample,mcTag,syst,self.tcInMaps[MCSmear],"MCSmear_"+syst,"1.",columns)

                  hadd = subprocess.Popen("hadd -f FullJER_"+sample+"_"+mcTag+".root FullJER_tmp_"+sample+"_"+mcTag+"_*.root", shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                  stdout, stderr = hadd.communicate()
                  if not stderr == "":
                     logging.error("Error doing hadd for %s %s" % (mcTag, sample))
                     logging.error(stderr)
                     sys.exit(-1)
                  logging.info(stdout)
                  rm = subprocess.Popen("rm FullJER_tmp_"+sample+"_"+mcTag+"_*.root", shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                  stdout, stderr = rm.communicate()
                  if not stderr == "":
                     logging.error("Error removinf temporary root files for %s %s" % (mcTag, sample))
                     logging.error(stderr)
                     sys.exit(-1)
                  logging.info(stdout)

if __name__ == "__main__":

     ROOT.gROOT.SetBatch(True)
     ROOT.gStyle.SetOptStat(False)

     ######################################################################################################################################################################
     # python getFinalFullJER.py --pathInput '/eos/atlas/atlascerngroupdisk/phys-susy/stop2L/stop2LFULLJER/LSF_ntuple_*/' --leaf WeightEvents -s ttbar --nomName _WEIGHTS #
     ######################################################################################################################################################################
     parser = argparse.ArgumentParser()
     parser.add_argument('--pathInput','-i', type=str, help='path input files', required=True)
     parser.add_argument('--leaf', type=str, help='leaf name whose sign will be changed to substract PD smeared events', required=True)
     parser.add_argument("--cut", type=str, help="skimming cut", default="true")
     parser.add_argument("--samples","-s", type = str, help="samples names, ex. ttbar,VV", required=True)
     parser.add_argument("--nomName", type = str, help="suffix of the nominal samples", required=True)
     parser.add_argument("--mc16aTag", type = str, help="mc16a tag", default="mc16a")
     parser.add_argument("--mc16dTag", type = str, help="mc16d tag", default="mc16d")
     parser.add_argument("--mc16eTag", type = str, help="mc16e tag", default="mc16e")
     parser.add_argument("--MT",action="store_true", help="enable ROOT MT")
     
     try:
        Args  = parser.parse_args()
     except:
        parser.print_help()
        sys.exit(-1)

     if Args.MT: 
        logging.info("Enabling ROOT MT")
        ROOT.ROOT.EnableImplicitMT()



     fullJER = handleFullJERSyst()
     fullJER.path = Args.pathInput #"/eos/atlas/atlascerngroupdisk/phys-susy/stop2L/stop2LFULLJER/LSF_ntuple_*/"
     fullJER.leaf = Args.leaf
     fullJER.cut = Args.cut
     fullJER.samples=Args.samples
     fullJER.nomName = Args.nomName
     fullJER.mc16aTag = Args.mc16aTag
     fullJER.mc16dTag = Args.mc16dTag
     fullJER.mc16eTag = Args.mc16eTag
     fullJER.getFullJERTree()


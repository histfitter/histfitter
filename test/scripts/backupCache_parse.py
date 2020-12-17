import os.path

class backupCacheParser:

  # list of mu_BKG parameters
  mus = ['mu_DB', 'mu_ZSS']

  def __init__(self, log, ref = None, precision = 1e-4):
    self.log = log
    self.ref = ref
    self.precision = precision

  def getMu(self, mu, log):
    # open file or modify the log file
    if os.path.isfile(log):
      f = open(log)
    else:
      # if self.log is already the log, mimic a file by splitting it with new lines
      f = self.log.split('\n')
    # get the parameter
    for l in f:
      if mu in l and "1.0000" in l and "none" not in l:
        return l
    # close file
    if os.path.isfile(self.log):
      f.close()

  def parse(self):
    # if no reference given, create one
    if self.ref == None:
      outfile = open(self.log.replace(".txt",".ref"), 'w')

    # loop through mu_BKG parameters
    for mu in self.mus:
      l = self.getMu(mu, self.log)
      # if no reference given, save mu_BKG to ref file
      if self.ref == None:
        outfile.write(l)
      # compare reference mu to current mu
      else:
        l_ref = self.getMu(mu, self.ref).strip().split()
        l = l.strip().split()
        central_diff = float(l[2])-float(l_ref[2])
        error_diff = float(l[4])-float(l_ref[4])
        print(f"difference in central value for {mu}: {central_diff}")
        print(f"difference in error for {mu}: {error_diff}")
        # return error if not close enough
        assert abs(central_diff/float(l[2])) < self.precision
        assert abs(error_diff/float(l[4])) < self.precision

    if self.ref == None:
      outfile.close()

if __name__ == '__main__':
  import argparse

  ap = argparse.ArgumentParser(description = 'Process HistFitter log file.')
  ap.add_argument('-l', '--log', required = True,
    help = 'a HistFitter log file')
  ap.add_argument('-r', '--ref', required = False,
    help = 'a reference log file')
  args = vars(ap.parse_args())

  log = args['log']
  ref = args['ref']

  assert '.txt' in log, 'logfile should end with .txt'

  parser = backupCacheParser(log,ref)
  parser.parse()

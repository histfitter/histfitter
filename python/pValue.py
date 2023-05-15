"""
Modified from:

  Code for "Plotting the Differences Between Data and Expectation"
  by Georgios Choudalakis and Diego Casadei
  Eur. Phys. J. Plus 127 (2012) 25 
  http://dx.doi.org/10.1140/epjp/i2012-12025-y
  (http://arxiv.org/abs/1111.2062)
  -----------------------------------------------------------------
  This code is covered by the GNU General Public License:
  http://www.gnu.org/licenses/gpl.html
  -----------------------------------------------------------------

Original code available as:
  Git: (recommended)
     https://github.com/dcasadei/psde

  SVN: (old)
     svn co https://svn.cern.ch/guest/psde 
     svn co svn+ssh://svn.cern.ch/guest/psde

Modifications:
  * only selected functions are avaiable here
  * code ported to python 
"""

import math

def pValuePoissonError(nObs,   E, V):
    print("obs",nObs)
    if E<=0 or V<=0:
        print("ERROR in pValuePoissonError(): expectation and variance must be positive. ")
        print("Returning 0.5")

    B = E/V
    A = E*B

    if A>100:  # need to use logarithms

        stop=nObs
        if nObs>E :
            stop = stop-1

    #/ NB: must work in log-scale otherwise troubles!
        logProb = A*math.log(B/(1+B))
        sum=math.exp(logProb) # P(n=0)
        for u in range(1, stop+1):
            logProb += math.log((A+u-1)/(u*(1+B)))
            sum += math.exp(logProb)

        if nObs>E:  # excess
            return 1-sum
        else:  # deficit
            return sum
        
    else :
        # Recursive formula: P(nA,B) = P(n-1A,B) (A+n-1)/(n*(1+B))
        p0 = pow(B/(1+B),A) # P(0A,B)
        nExp = A/B
        if nObs>nExp :# excess
            pLast = p0
            sum = p0
            for k in range(1, nObs):
                p = pLast * (A+k-1) / (k*(1+B))
	# cout << Form("Excess: P(%d%8.5g) = %8.5g and sum = %8.5g",k-1,nExp,pLast,sum) << " -> "
                sum = sum + p
                pLast = p
	# cout << Form("P(%d%8.5g) = %8.5g and sum = %8.5g",k,nExp,pLast,sum) << endl      
            return 1-sum
        else :# deficit
            pLast = p0
            sum = p0
            for k in range(1, nObs+1):
	# cout << Form("Deficit: P(%d%8.5g) = %8.5g and sum = %8.5g",k-1,nExp,pLast,sum) << " -> "
                p = pLast * (A+k-1) / (k*(1+B))
                sum += p
                pLast = p
            return sum


def pja_normal_quantile( p): 

    a = [ -3.969683028665376e+01,     2.209460984245205e+02,     -2.759285104469687e+02,     1.383577518672690e+02,     -3.066479806614716e+01,    2.506628277459239e+00]

    b = [
        -5.447609879822406e+01, # b(1) -> b[0]
         1.615858368580409e+02, # b(2)
         -1.556989798598866e+02, # b(3)
         6.680131188771972e+01, # b(4)
         -1.328068155288572e+01, # b(5) -> b[4]
         ]

    c = [
        -7.784894002430293e-03, # c(1) -> c[0]
         -3.223964580411365e-01, # c(2)
         -2.400758277161838e+00, # c(3)
         -2.549732539343734e+00, # c(4)
         4.374664141464968e+00, # c(5)
         2.938163982698783e+00, # c(6) -> c[5]
         ]

    d = [
        7.784695709041462e-03, # d(1) -> d[0]
        3.224671290700398e-01, # d(2)
        2.445134137142996e+00, # d(3)
        3.754408661907416e+00, # d(4) -> d[3]
        ]

  # Define break-points.
    
    p_low  = 0.02425
    p_high = 1 - p_low

  # output value
    x=0

  # Rational approximation for lower region.
    
    if 0 < p and p < p_low:
        q = math.sqrt(-2*math.log(p))
        x = (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)

  # Rational approximation for central region.
    elif p_low <= p and p <= p_high:
        q = p - 0.5
        r = q*q
        x = (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
  # Rational approximation for upper region.
    elif p_high < p and p < 1:
        q = math.sqrt(-2*math.log(1-p))
        x = -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)

    return x


def  pValueToSignificance( p, excess): # excess: bool, False if deficit

  if p<0 or p>1:
    print("ERROR: p-value must belong to [0,1] but input value is ", p)
    return 0

  if excess:
    return pja_normal_quantile(1-p)
  else:
    return pja_normal_quantile(p)

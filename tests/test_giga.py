import hilbertcoresets as hc
import numpy as np

n_trials = 50
tol = 1e-16

####################################################
#verifies that 
#-coreset size <= M at iteration M
#-error() vs output y(weights) are close to each other
#-error is decreasing
#-reset() resets the alg properly
#-run(M) with increasing M outputs same weights as 
# one run with large M
#-if input size = 1, error is 0 for any M
#-if input is colinear, error is 0 forall M
#-sqrt_bound()/exp_bound is valid
#-bound is positive, decreasing -> 0 
#-giga outputs expected weights and error for axis_aligned data 
####################################################
def giga_single(N, D, dist="gauss"):
  print 'GIGA single: N = ' +str(N) + ' D = ' +str(D) + ' dist = ' + dist
  for n in range(n_trials):
    if dist == "gauss":
      x = np.random.normal(0., 1., (N, D))
    elif dist == "bin":
      x = (np.random.rand(N, D) > 0.5).astype(int)
    elif dist == "gauss_colinear":
      x = np.random.normal(0., 1., D)
      y = np.random.rand(N)*2.-1.
      x = y[:, np.newaxis]*x
    elif dist == "bin_colinear":
      x = (np.random.rand(D) > 0.5).astype(int)
      y = np.random.rand(N)*2.-1.
      x = y[:, np.newaxis]*x
    else:
      x = np.zeros((N, N))
      for i in range(N):
        x[i, i] = 1./float(N)
    xs = x.sum(axis=0)
    giga = hc.FrankWolfe(x)

    #bound tests
    prev_sqrt_bd = np.inf
    prev_exp_bd = np.inf
    for m in range(1, N+1):
      sqrt_bd = giga.sqrt_bound(m)
      exp_bd = giga.exp_bound(m)
      assert sqrt_bd >= 0., "GIGA failed: sqrt bound < 0"
      assert sqrt_bd - prev_sqrt_bd < tol, "GIGA failed: sqrt bound is not decreasing"
      assert exp_bd >= 0., "GIGA failed: exp bound < 0"
      assert exp_bd - prev_exp_bd < tol, "GIGA failed: exp bound is not decreasing"
      prev_sqrt_bd = sqrt_bd
      prev_exp_bd = exp_bd
    assert giga.sqrt_bound(1e100) < tol, "GIGA failed: sqrt bound doesn't approach 0"
    assert giga.exp_bound(1e100) < tol, "GIGA failed: exp bound doesn't approach 0"

    #incremental M tests
    prev_err = np.sqrt(x**2.sum(axis=1)).sum()*np.sqrt(((x - xs)**2).sum(axis=1)).max()
    for m in range(1, N+1):
      giga.run(m)
      if x.shape[0] == 1:
        assert np.fabs(giga.weights() - np.array([1])) < tol, "GIGA failed: coreset not immediately optimal with N = 1"
      assert (giga.weights() > 0.).sum() <= m, "GIGA failed: coreset size > m"
      xw = (giga.weights()[:, np.newaxis]*x).sum(axis=0)
      assert np.sqrt(((xw-xs)**2).sum()) < prev_err, "GIGA failed: error is not monotone decreasing"
      assert np.fabs(giga.error() - np.sqrt(((xw-xs)**2).sum())) < tol, "GIGA failed: x(w) est is not close to true x(w)"
      assert giga.sqrt_bound() - np.sqrt(((xw-xs)**2).sum()) >= -tol, "GIGA failed: sqrt bound invalid"
      assert giga.exp_bound() - np.sqrt(((xw-xs)**2).sum()) >= -tol, "GIGA failed: exp bound invalid"
      if 'colinear' in dist and m >= 2:
        assert np.sqrt(((xw-xs)**2).sum()) < tol, "GIGA failed: for M>=2, coreset with colinear data not optimal"
      if 'axis' in dist:
        assert np.all( np.fabs(giga.weights()[ giga.weights() > 0. ] - 1./np.sqrt(m) ) < tol ), "GIGA failed: on axis-aligned data, weights are not 1/sqrt(M)"
        assert np.fabs(np.sqrt(((xw-xs)**2).sum()) - np.sqrt(1./float(m) - 1./float(N))) < tol, "GIGA failed: on axis-aligned data, error is not sqrt(1/M - 1_N)"
      prev_err = np.sqrt(((xw-xs)**2).sum())
    #save incremental M result
    w_inc = giga.weights()
    xw_inc = (giga.weights()[:, np.newaxis]*x).sum(axis=0) 
    
    #check reset
    giga.reset()
    assert giga.M == 0 and np.all(np.fabs(giga.weights()) < tol) and np.fabs(giga.error() - np.sqrt((xs**2).sum())) < tol, "GIGA failed: giga.reset() did not properly reset"
    #check reset
    giga.run(N)
    xw = (giga.weights()[:, np.newaxis]*x).sum(axis=0) 
    assert np.all(np.fabs(giga.weights() - w_inc) < tol) and np.sqrt(((xw-xw_inc)**2).sum()) < tol, "GIGA failed: incremental run up to N doesn't produce same result as one run at N"

def test_giga_random():
  tests = [(N, D, dist) for N in [0, 1, 1000] for D in [0, 1, 10] for dist in ['gauss', 'bin']]
  for N, D, dist in tests:
    yield giga_single(N, D, dist)
 
def test_giga_colinear():
  tests = [(N, D, dist) for N in [0, 1, 1000] for D in [0, 1, 10] for dist in ['gauss_colinear', 'bin_colinear']]
  for N, D, dist in tests:
    yield giga_single(N, D, dist)

def test_giga_axis_aligned():
  for N in [0, 1, 10, 1000]:
    yield giga_single(N, 0, 'axis_aligned')


####################################################
#verifies that GIGA correctly responds to bad input
####################################################
   
def test_giga_input_validation():
  #empty
  #non array
  #non number
  #integer vs real
  #m = 0
  pass #TODO
 
  
 


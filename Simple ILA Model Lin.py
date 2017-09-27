#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 16:08:19 2017

@author: klp4
"""

import numpy as np
import matplotlib.pyplot as plt

# import the modules from LinApp
from LinApp_FindSS import LinApp_FindSS
from LinApp_Deriv import LinApp_Deriv
from LinApp_Solve import LinApp_Solve
from LinApp_SSL import LinApp_SSL

def Modeldefs(Xp, X, Y, Z, params):
    '''
    This function takes vectors of endogenous and exogenous state variables
    along with a vector of 'jump' variables and returns explicitly defined
    values for consumption, gdp, wages, real interest rates, and transfers
    
    Inputs are:
        Xp: value of capital in next period
        X: value of capital this period
        Y: value of labor this period
        Z: value of productivity this period
        params: list of parameter values
    
    Output are:
        Y: GDP
        w: wage rate
        r: rental rate on capital
        T: transfer payments
        c: consumption
        i: investment
        u: utiity
    '''
    
    # unpack input vectors
    kp = Xp
    k = X
    ell = Y
    z = Z
    
    # unpack params
    [alpha, beta, gamma, delta, chi, theta, tau, rho_z, sigma_z] = params
    
    # find definintion values
    Y = k**alpha*(np.exp(z)*ell)**(1-alpha)
    w = (1-alpha)*Y/ell
    r = alpha*Y/k
    T = tau*(w*ell + (r - delta)*k)
    c = (1-tau)*(w*ell + (r - delta)*k) + k + T - kp
    i = Y - c
    u = c**(1-gamma)/(1-gamma) - chi*ell**(1+theta)/(1+theta)
    return Y, w, r, T, c, i, u


def Modeldyn(theta0, params):
    '''
    This function takes vectors of endogenous and exogenous state variables
    along with a vector of 'jump' variables and returns values from the
    characterizing Euler equations.
    
    Inputs are:
        theta: a vector containng (Xpp, Xp, X, Yp, Y, Zp, Z) where:
            Xpp: value of capital in two periods
            Xp: value of capital in next period
            X: value of capital this period
            Yp: value of labor in next period
            Y: value of labor this period
            Zp: value of productivity in next period
            Z: value of productivity this period
        params: list of parameter values
    
    Output are:
        Euler: a vector of Euler equations written so that they are zero at the
            steady state values of X, Y & Z.  This is a 2x1 numpy array. 
    '''
    
    # unpack theat0
    (Xpp, Xp, X, Yp, Y, Zp, Z) = theta0
    
    # unpack params
    [alpha, beta, gamma, delta, chi, theta, tau, rho_z, sigma_z] = params
    
    # find definitions for now and next period
    ell = Y
    Y, w, r, T, c, i, u = Modeldefs(Xp, X, Y, Z, params)
    Yp, wp, rp, Tp, cp, ip, up = Modeldefs(Xpp, Xp, Yp, Zp, params)
    
    # Evaluate Euler equations
    E1 = (c**(-gamma)*(1-tau)*w) / (chi*ell**theta) - 1
    E2 = (c**(-gamma)) / (beta*cp**(-gamma)*(1 + (1-tau)*(rp - delta))) - 1
    
    return np.array([E1, E2])


# set parameter values
alpha = .35
beta = .99
gamma = 2.5
delta = .08
chi = 10.
theta = 2.
tau = .05
rho_z = .9
sigma_z = .01

# make parameter list to pass to functions
params = np.array([alpha, beta, gamma, delta, chi, theta, tau, rho_z, sigma_z])

# set LinApp parameters
Zbar = np.array([0.])
nx = 1
ny = 1
nz = 1
logX = 0
Sylv = 0

# take a guess for steady state values of k and ell
guessXY = np.array([.1, .25])

# find the steady state values using LinApp_FindSS
XYbar = LinApp_FindSS(Modeldyn, params, guessXY, Zbar, nx, ny)
(kbar, ellbar) = XYbar

# set up steady state input vector
theta0 = np.array([kbar, kbar, kbar, ellbar, ellbar, 0., 0.])

# check SS solution
check = Modeldyn(theta0, params)
print ('check SS: ', check)
if np.max(np.abs(check)) > 1.E-6:
    print ('Have NOT found steady state')
    
# find the steady state values for the definitions
Ybar, wbar, rbar, Tbar, cbar, ibar, ubar = \
    Modeldefs(kbar, kbar, ellbar, 0., params)

# display all steady state values
print ('kbar:   ', kbar)
print ('ellbar: ', ellbar)
print ('Ybar:   ', Ybar)
print ('wbar:   ', wbar)
print ('rbar:   ', rbar)
print ('Tbar:   ', Tbar)
print ('cbar:   ', cbar)
print ('ibar:   ', ibar)
print ('ubar:   ', ubar)

# find the derivatives matrices
[AA, BB, CC, DD, FF, GG, HH, JJ, KK, LL, MM, WW, TT] = \
    LinApp_Deriv(Modeldyn, params, theta0, nx, ny, nz, logX)

# set value for NN    
NN = rho_z
    
# find the policy and jump function coefficients
PP, QQ, UU, RR, SS, VV = \
    LinApp_Solve(AA,BB,CC,DD,FF,GG,HH,JJ,KK,LL,MM,WW,TT,NN,Zbar,Sylv)
print ('P: ', PP)
print ('Q: ', QQ)
print ('R: ', RR)
print ('S: ', SS)

# generate a history of Z's
nobs = 250
Zhist = np.zeros((nobs,1))
for t in range(1, nobs):
    Zhist[t,0] = rho_z*Zhist[t,0] + sigma_z*np.random.normal(0., 1.)
    
# put SS values and starting values into numpy vectors
XYbar = np.array([kbar, ellbar])
X0 = np.array([kbar])
Y0 = np.array([ellbar])

## simulate the model
#khist, ellhist = \
#    LinApp_SSL(X0, Zhist, XYbar, logX, PP, QQ, UU, Y0, RR, SS, VV)
#    
## plot k and ell
#plt.subplot(2, 1, 1)
#plt.plot(khist)
#plt.title('Capital Stock')
#plt.subplot(2, 1, 2)
#plt.plot(ellhist)
#plt.title('Labor')
#plt.show()
#
## find other variables and plot
## preallocate histories
#Yhist = np.zeros(nobs-1)
#whist = np.zeros(nobs-1)
#rhist = np.zeros(nobs-1)
#Thist = np.zeros(nobs-1)
#chist = np.zeros(nobs-1)
#ihist = np.zeros(nobs-1)
#uhist = np.zeros(nobs-1)
#for t in range(0, nobs-1):
#    Yhist[t], whist[t], rhist[t], Thist[t], chist[t], ihist[t], uhist[t] = \
#        Modeldefs(khist[t+1], khist[t], ellhist[t], Zhist[t], params)
#        
#plt.subplot(3, 3, 1)
#plt.plot(Zhist)
#plt.title('z')
#
#plt.subplot(3, 3, 2)
#plt.plot(Yhist)
#plt.title('Y')
#
#plt.subplot(3, 3, 3)
#plt.plot(whist)
#plt.title('w')
#
#plt.subplot(3, 3, 4)
#plt.plot(rhist)
#plt.title('r')
#
#plt.subplot(3, 3, 5)
#plt.plot(Thist)
#plt.title('T')
#
#plt.subplot(3, 3, 6)
#plt.plot(chist)
#plt.title('c')
#
#plt.subplot(3, 3, 7)
#plt.plot(ihist)
#plt.title('i')
#
#plt.subplot(3, 3, 8)
#plt.plot(uhist)
#plt.title('u')
#
#plt.show()

## CHANGE POLICY

# set new tax rate
tau2 = .055

# make parameter list to pass to functions
params2 = np.array([alpha, beta, gamma, delta, chi, theta, tau2, rho_z, 
                    sigma_z])

# find new steady state
# use the old steady state values of k and ell for our guess
guessXY = XYbar

# find the steady state values using LinApp_FindSS
XYbar2 = LinApp_FindSS(Modeldyn, params2, guessXY, Zbar, nx, ny)
(kbar2, ellbar2) = XYbar2

# set up steady state input vector
theta02 = np.array([kbar2, kbar2, kbar2, ellbar2, ellbar2, 0., 0.])

# check SS solution
check = Modeldyn(theta02, params2)
print ('check SS: ', check)
if np.max(np.abs(check)) > 1.E-6:
    print ('Have NOT found steady state')
    
# find the steady state values for the definitions
Ybar2, wbar2, rbar2, Tbar2, cbar2, ibar2, ubar2 = \
    Modeldefs(kbar2, kbar2, ellbar2, 0., params2)

# display all steady state values
print ('kbar:   ', kbar2)
print ('ellbar: ', ellbar2)
print ('Ybar:   ', Ybar2)
print ('wbar:   ', wbar2)
print ('rbar:   ', rbar2)
print ('Tbar:   ', Tbar2)
print ('cbar:   ', cbar2)
print ('ibar:   ', ibar2)
print ('ubar:   ', ubar2)

# find the new derivatives matrices
[AA2, BB2, CC2, DD2, FF2, GG2, HH2, JJ2, KK2, LL2, MM2, WW2, TT2] = \
    LinApp_Deriv(Modeldyn, params2, theta02, nx, ny, nz, logX)
    
# find the policy and jump function coefficients
PP2, QQ2, UU2, RR2, SS2, VV2 = \
    LinApp_Solve(AA2,BB2,CC2,DD2,FF2,GG2,HH2,JJ2,KK2,LL2,MM2,WW2,TT2,NN,Zbar, \
                 Sylv)
print ('P: ', PP2)
print ('Q: ', QQ2)
print ('R: ', RR2)
print ('S: ', SS2)


def PolSim(initial, nobs, ts, coeffs1, state1, params1, coeffs2, state2, \
           params2):
    from LinApp_Sim import LinApp_Sim
    '''
    Generates a history of k & ell with a switch in regime in period ts.
    
    Inputs
    -----------    
    initial: list of values for k & z (k0, z0) in the first period.
    nobs: number of periods to simulate.
    ts: period in which the shift occurs.
    coeffs1: list of (PP, QQ, UU, RR, SS, VV) under the baseline regime.
    state1: numpy array of XYbar under the baseline regime.
    params1: list of parameters under the baseline regime.
    coeffs2: list of (PP2, QQ2, UU2, RR2, SS2, VV2) under the new regime.
    state2: numpy array of XYbar2 under the new regime.
    params2: list of parameters under the new regime.
    
    Returns
    --------
    khist: 2D-array, dtype=float
        nobs-by-1 matrix containing the values of k
    
    ellhist: 2D-array, dtype=float
        nobs-by-1 matrix vector containing the values of ell 
        
    zhist: 2D-array, dtype=float
        nobs-by-1 matrix vector containing the values of z 
    '''
    
    # preallocate histories
    khist = np.zeros(nobs+1)
    ellhist = np.zeros(nobs)
    zhist = np.zeros(nobs)
    Yhist = np.zeros(nobs)
    whist = np.zeros(nobs)
    rhist = np.zeros(nobs)
    Thist = np.zeros(nobs)
    chist = np.zeros(nobs)
    ihist = np.zeros(nobs)
    uhist = np.zeros(nobs)
    
    # set starting values
    khist[0] = k0
    zhist[0] = z0
    
    # unpack state1 and state2
    (kbar, ellbar) = XYbar
    (kbar2, ellbar2) = XYbar2
    
    # generate history of random shocks
    for t in range(1, nobs):
        zhist[t] = rho_z*zhist[t] + sigma_z*np.random.normal(0., 1.)
        
    # generate histories for k and ell for the first ts-1 periods
    for t in range(0, ts-1):
        # inputs must be 1D numpy arrays and deviation from SS values
        kin = np.array([khist[t] - kbar])
        zin = np.array([zhist[t]])
        k, ell = LinApp_Sim(kin, zin, PP, QQ, UU, RR, SS, VV)
        # k and ell are deviations from SS values, so add these back.
        # they are also 1D numpy arrays, so pull out the values rather than 
        # use the arrays.
        khist[t+1] = k + kbar
        ellhist[t] = ell + ellbar
        Yhist[t], whist[t], rhist[t], Thist[t], chist[t], ihist[t], \
            uhist[t] = \
            Modeldefs(khist[t+1], khist[t], ellhist[t], zhist[t], params)
    
    for t in range(ts-1, nobs):
        kin = np.array([khist[t] - kbar2])
        zin = np.array([zhist[t]])
        k, ell = LinApp_Sim(kin, zin, PP2, QQ2, UU2, RR2, SS2, VV2)
        khist[t+1] = k + kbar2
        ellhist[t] = ell + ellbar2
        Yhist[t], whist[t], rhist[t], Thist[t], chist[t], ihist[t], \
            uhist[t] = \
            Modeldefs(khist[t+1], khist[t], ellhist[t], zhist[t], params2)
    
    return khist, ellhist, zhist, Yhist, whist, rhist, Thist, chist, ihist, \
        uhist


# specify the number of simulations and observations per simulation
nsim = 100
nobs = 120

# specify the period policy shifts
ts = 20

# specify initial values
k0 = kbar
z0 = 0.
initial = (k0, z0)

# set up coefficient lists
coeffs1 = (PP, QQ, UU, RR, SS, VV)
coeffs2 = (PP2, QQ2, UU2, RR2, SS2, VV2)

# begin Monte Carlos

# run first simulation and store in Monte Carlo matrices
kmc, ellmc, zmc, Ymc, wmc, rmc, Tmc, cmc, imc, umc \
    = PolSim(initial, nobs, ts, coeffs1, XYbar, params, coeffs2, XYbar2, \
             params2)

for i in range(1, nsim):
    # run remaining simulations
    khist, ellhist, zhist, Yhist, whist, rhist, Thist, chist, ihist, uhist = \
        PolSim(initial, nobs, ts, coeffs1, XYbar, params, coeffs2, XYbar2, \
               params2)
    # stack results in Monte Carlo matrices
    kmc = np.vstack((kmc, khist))
    ellmc = np.vstack((ellmc, ellhist))
    zmc = np.vstack((zmc, zhist))
    Ymc = np.vstack((Ymc, Yhist))
    wmc = np.vstack((wmc, whist))
    rmc = np.vstack((rmc, rhist))
    Tmc = np.vstack((Tmc, Thist))
    cmc = np.vstack((cmc, chist))
    imc = np.vstack((imc, ihist))
    umc = np.vstack((umc, uhist))
    
# now sort the Monte Carlo matrices over the rows
kmc = np.sort(kmc, axis = 0)
ellmc = np.sort(ellmc, axis = 0)
zmc = np.sort(zmc, axis = 0)
Ymc = np.sort(Ymc, axis = 0)
wmc = np.sort(wmc, axis = 0)
rmc = np.sort(rmc, axis = 0)
Tmc = np.sort(Tmc, axis = 0)
cmc = np.sort(cmc, axis = 0)
imc = np.sort(imc, axis = 0)
umc = np.sort(umc, axis = 0)

# find the average values for each variable in each time period across 
# Monte Carlos
kavg = np.mean(kmc, axis = 0)
ellavg = np.mean(ellmc, axis = 0)
zavg = np.mean(zmc, axis = 0)
Yavg = np.mean(Ymc, axis = 0)
wavg = np.mean(wmc, axis = 0)
ravg = np.mean(rmc, axis = 0)
Tavg = np.mean(Tmc, axis = 0)
cavg = np.mean(cmc, axis = 0)
iavg = np.mean(imc, axis = 0)
uavg = np.mean(umc, axis = 0)

# find the rows for desired confidence bands
conf = .1
low = int(np.floor((conf/2)*nsim))
high = nsim - low

# find the upper and lower confidence bands for each variable
kupp = kmc[high,:]
ellupp = ellmc[high,:]
zupp = zmc[high,:]
Yupp = Ymc[high,:]
wupp = wmc[high,:]
rupp = rmc[high,:]
Tupp = Tmc[high,:]
cupp = cmc[high,:]
iupp = imc[high,:]
uupp = umc[high,:]

klow = kmc[low,:]
elllow = ellmc[low,:]
zlow = zmc[low,:]
Ylow = Ymc[low,:]
wlow = wmc[low,:]
rlow = rmc[low,:]
Tlow = Tmc[low,:]
clow = cmc[low,:]
ilow = imc[low,:]
ulow = umc[low,:]

# plot
plt.subplot(2,2,1)
plt.plot(range(kavg.size), kavg, 'k-',
         range(kupp.size), kupp, 'k:',
         range(klow.size), klow, 'k:')
plt.title('k')

plt.subplot(2,2,2)
plt.plot(range(ellavg.size), ellavg, 'k-',
         range(ellupp.size), ellupp, 'k:',
         range(elllow.size), elllow, 'k:')
plt.title('ell')

plt.subplot(2,2,3)
plt.plot(range(zavg.size), zavg, 'k-',
         range(zupp.size), zupp, 'k:',
         range(zlow.size), zlow, 'k:')
plt.title('z')

plt.subplot(2,2,4)
plt.plot(range(Yavg.size), Yavg, 'k-',
         range(Yupp.size), Yupp, 'k:',
         range(Ylow.size), Ylow, 'k:')
plt.title('Y')

# save high quality version to external file
plt.savefig('ILAfig1.eps', format='eps', dpi=2000)

plt.show()

plt.subplot(3,2,1)
plt.plot(range(wavg.size), wavg, 'k-',
         range(wupp.size), wupp, 'k:',
         range(wlow.size), wlow, 'k:')
plt.title('w')

plt.subplot(3,2,2)
plt.plot(range(ravg.size), ravg, 'k-',
         range(rupp.size), rupp, 'k:',
         range(rlow.size), rlow, 'k:')
plt.title('r')

plt.subplot(3,2,3)
plt.plot(range(Tavg.size), Tavg, 'k-',
         range(Tupp.size), Tupp, 'k:',
         range(Tlow.size), Tlow, 'k:')
plt.title('T')

plt.subplot(3,2,4)
plt.plot(range(cavg.size), cavg, 'k-',
         range(cupp.size), cupp, 'k:',
         range(clow.size), clow, 'k:')
plt.title('c')

plt.subplot(3,2,5)
plt.plot(range(iavg.size), iavg, 'k-',
         range(iupp.size), iupp, 'k:',
         range(ilow.size), ilow, 'k:')
plt.title('iT')

plt.subplot(3,2,6)
plt.plot(range(uavg.size), uavg, 'k-',
         range(uupp.size), uupp, 'k:',
         range(ulow.size), ulow, 'k:')
plt.title('u')

# save high quality version to external file
plt.savefig('ILAfig2.eps', format='eps', dpi=2000)

plt.show()

# plot
plt.subplot(2,2,1)
plt.plot(range(khist.size), khist, 'k-',
         range(kavg.size), kavg, 'r-')
plt.title('k')

plt.subplot(2,2,2)
plt.plot(range(ellhist.size), ellhist, 'k-',
         range(ellavg.size), ellavg, 'r-')
plt.title('ell')

plt.subplot(2,2,3)
plt.plot(range(zhist.size), zhist, 'k-',
         range(zavg.size), zavg, 'r-')
plt.title('z')

plt.subplot(2,2,4)
plt.plot(range(Yhist.size), Yhist, 'k-',
         range(Yavg.size), Yavg, 'r-')
plt.title('Y')

# save high quality version to external file
plt.savefig('ILAfig3.eps', format='eps', dpi=2000)

plt.show()

plt.subplot(3,2,1)
plt.plot(range(whist.size), whist, 'k-',
         range(wavg.size), wavg, 'r-')
plt.title('w')

plt.subplot(3,2,2)
plt.plot(range(rhist.size), rhist, 'k-',
         range(ravg.size), ravg, 'r-')
plt.title('r')

plt.subplot(3,2,3)
plt.plot(range(Thist.size), Thist, 'k-',
         range(Tavg.size), Tavg, 'r-')
plt.title('T')

plt.subplot(3,2,4)
plt.plot(range(chist.size), chist, 'k-',
         range(cavg.size), cavg, 'r-')
plt.title('c')

plt.subplot(3,2,5)
plt.plot(range(ihist.size), ihist, 'k-',
         range(iavg.size), iavg, 'r-')
plt.title('iT')

plt.subplot(3,2,6)
plt.plot(range(uhist.size), uhist, 'k-',
         range(uavg.size), uavg, 'r-')
plt.title('u')

# save high quality version to external file
plt.savefig('ILAfig4.eps', format='eps', dpi=2000)

plt.show()

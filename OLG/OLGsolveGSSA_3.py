#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This program reads in paramter values and steady states from the file, 
ILAfindss.pkl.

It then calculates the linear coefficients for the policy and jump function
approximations using the LinApp toolkit.

The coefficients and time to solve are written to the file, ILAsolveGSSA.pkl.

The baseline values have a 1 at the end of the variable name.
The values after the policy change have a 2 at the end. 
"""

import numpy as np
import timeit
import pickle as pkl

# import the modules from LinApp
from LinApp_Deriv import LinApp_Deriv
from LinApp_Solve import LinApp_Solve
# from LinApp_SSL import LinApp_SSL
from gssa import GSSA
from OLGfuncs import Modeldyn

pord = 3
# -----------------------------------------------------------------------------
# READ IN VALUES FROM STEADY STATE CALCULATIONS

# load steady state values and parameters
infile = open('OLGfindss.pkl', 'rb')
(bar1, bar2, params1, params2, LINparams) = pkl.load(infile)
infile.close()

infile = open('OLGsolveGSSA1.pkl', 'rb')
(coeffs2a, coeffs2b, timesolve) = pkl.load(infile)
infile.close()

A = np.zeros((4,6))
coeffs2a = np.insert(coeffs2a, 9, A)
coeffs2b = np.insert(coeffs2b, 9, A)

try:
    infile = open('OLGsolveGSSA_3.pkl', 'rb')
    (coeffs3a, coeffs3b, timesolve) = pkl.load(infile)
    infile.close()
    old_pord = False
except FileNotFoundError:
    old_pord = True
    pass

# unpack
[k2bar1, k3bar1, k4bar1, l1bar1, l2bar1, l3bar1, Kbar1, \
    Lbar1, GDPbar1, wbar1, rbar1, T4bar1, Bbar1, c1bar1, c2bar1, c3bar1, \
    c4bar1, Cbar1, Ibar1, u1bar1, u2bar1, u3bar1, u4bar1] = bar1
[k2bar2, k3bar2, k4bar2, l1bar2, l2bar2, l3bar2, Kbar2, \
    Lbar2, GDPbar2, wbar2, rbar2, T4bar2, Bbar2, c1bar2, c2bar2, c3bar2, \
    c4bar2, Cbar2, Ibar2, u1bar2, u2bar2, u3bar2, u4bar2] = bar2
[alpha, beta, gamma, delta, chi, theta, tau, rho_z, \
    sigma_z, pi2, pi3, pi4, f1, f2, f3, nx, ny, nz] = params1
tau2 = params2[6]
(zbar, Zbar, NN, nx, ny, nz, logX, Sylv) = LINparams

# set clock for time to calcuate functions
startsolve = timeit.default_timer()

# set name for external files written
name = 'OLGsolveGSSA1'
old = True

# -----------------------------------------------------------------------------
# BASELINE
T = 10000
kbar1 = (k2bar1, k3bar1, k4bar1)
lbar1 = (l1bar1, l2bar1, l3bar1)
GSSAparams = (T, nx, ny, nz, pord, old)
# set up coefficient list
if old_pord == True:
    coeffs1 = GSSA(params1, kbar1, lbar1, GSSAparams, coeffs2a)
elif old_pord == False:
    coeffs1 = GSSA(params1, kbar1, lbar1, GSSAparams, coeffs3a)

# -----------------------------------------------------------------------------
# CHANGE POLICY
kbar2 = (k2bar2, k3bar2, k4bar2)
lbar2 = (l1bar2, l2bar2, l3bar2)

if old_pord == True:
    coeffs2 = GSSA(params2, kbar2, lbar2, GSSAparams, coeffs2b)
elif old_pord == False:
    coeffs2 = GSSA(params2, kbar2, lbar2, GSSAparams, coeffs3b)

# calculate time to solve for functions
stopsolve = timeit.default_timer()
timesolve =  stopsolve - startsolve
print('time to solve: ', timesolve)


# -----------------------------------------------------------------------------
# SAVE RESULTS

output = open(name + '.pkl', 'wb')

# write timing
pkl.dump((coeffs1, coeffs2, timesolve), output)

output.close()
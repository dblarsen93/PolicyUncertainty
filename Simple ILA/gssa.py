# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 16:55:35 2017
@author: Daryl Larsen
"""
'''
This program implements the Generalized Stochastic Simulation Algorthim from 
Judd, Maliar and Mailar (2011) "Numerically stable and accurate stochastic 
simulation approaches for solving dynamic economic models", Quantitative
Economics vol. 2, pp. 173-210.
'''
import numpy as np
import matplotlib.pyplot as plt
from LinApp_FindSS import LinApp_FindSS

'''
We test the algorithm with a simple DSGE model with endogenous labor.
'''

'''
Choose the simulation length
'''
T = 10000

'''
Model's parameters
'''
alpha = .35
beta = .99
gam = 2.5
delta = .08
chi = 10.
theta = 2.
tau = .05 # The first stochastic shock
rho = .9
sigma = .01
mparams = ([alpha, beta, gam, delta, chi, theta, tau, rho, sigma])
nx = 1
ny = 1
nz = 1

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
    if ell > 0.9999:
        ell = 0.9999
    elif ell < 0:
        ell = 0
    z = Z
    
    # unpack params
    [alpha, beta, gamma, delta, chi, theta, tau, rho, sigma] = params
    
    # find definintion values
    GDP = k**alpha*(np.exp(z)*ell)**(1-alpha)
    w = (1-alpha)*GDP/ell
    r = alpha*GDP/k
    T = tau*(w*ell + (r - delta)*k)
    c = (1-tau)*(w*ell + (r - delta)*k) + k + T - kp
    i = GDP - c
    u = c**(1-gamma)/(1-gamma) - chi*ell**(1+theta)/(1+theta)
    return GDP, w, r, T, c, i, u

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
    [alpha, beta, gamma, delta, chi, theta, tau, rho, sigma] = params
    
    # find definitions for now and next period
    ell = Y
    if ell > 1:
        ell = 0.9999
    elif ell < 0:
        ell = 0
    GDP, w, r, T, c, i, u = Modeldefs(Xp, X, Y, Z, params)
    GDPp, wp, rp, Tp, cp, ip, up = Modeldefs(Xpp, Xp, Yp, Zp, params)
    
    # Evaluate Euler equations
    E1 = (c**(-gamma)*(1-tau)*w) / (chi*ell**theta) - 1
    E2 = (c**(-gamma)) / (beta*cp**(-gamma)*(1 + (1-tau)*(rp - delta))) - 1
    
    return np.array([E1, E2])

def poly1(Xin, XYparams):
    '''
    Includes polynomial terms up to order 'pord' for each element and quadratic 
    cross terms  One observation (row) at a time
    '''
    nX = nx + nz
    Xbasis = np.ones((1, 1))
    # generate polynomial terms for each element
    for i in range(1, 3):
        Xbasis = np.append(Xbasis, Xin**i)
    # generate cross terms
    for i in range (0, nX):
        for j in range(i+1, nX):
            temp = Xin[i]*Xin[j]
            Xbasis = np.append(Xbasis, temp)
    return Xbasis

def XYfunc(Xm, Zn, XYparams, coeffs):
    An = np.exp(Zn)
    XZin = np.append(Xm, An)
    XYbasis = np.append(1., XZin)
    for i in range(1, 3):
        XYbasis = poly1(XZin, XYparams)
    XYout = np.dot(XYbasis, coeffs)
    Xn = XYout[0:nx]
    Y = XYout[nx:nx+ny]
    if Xn < 0:
        Xn = np.array([0])
    if Y > 0.9999:
        Y = np.array([0.9999])
    elif Y < 0:
        Y = np.array([0])
    return Xn, Y
    
def MVOLS(Y, X):
    '''
    OLS regression with observations in rows
    '''
    XX = np.dot(np.transpose(X), X)
    XY = np.dot(np.transpose(X), Y)
    coeffs = np.linalg.solve(XX, XY)
    # coeffs = np.dot(np.linalg.inv(XX), XY)
    return coeffs

Zbar = np.zeros(nz)
guessXY = np.array([.1, .25])
XYbar = LinApp_FindSS(Modeldyn, mparams, guessXY, Zbar, nx, ny)
(kbar, ellbar) = XYbar
# set up steady state input vector
theta0 = np.array([kbar, kbar, kbar, ellbar, ellbar, 0., 0.])

# check SS solution
check = Modeldyn(theta0, mparams)
#print ('check SS: ', check)
if np.max(np.abs(check)) > 1.E-6:
    print ('Have NOT found steady state')
 
def GSSA(params, kbar):
    T = 10000
    regtype = 'poly1' # functional form for X & Y functions 
    fittype = 'MVOLS'   # regression fitting method
    pord = 3  # order of polynomial for fitting function
    ccrit = 1.0E-8  # convergence criteria for XY change
    damp = 0.01  # damping paramter for fixed point algorithm
    
    [alpha, beta, gamma, delta, chi, theta, tau, rho, sigma] = params
    XYparams = (regtype, fittype, pord, nx, ny, nz, ccrit, damp)

    Xstart = kbar
    
    #create history of Z's
    Z = np.zeros([T,nz])
    for t in range(1,T):
        Z[t,:] = rho*Z[t-1] + np.random.randn(1)*sigma
    if regtype == 'poly1':
        #coeffs = np.array([[  1.58688185e-01,   2.34967609e+00], \
        #                   [  6.79067876e-01,   4.69017966e-02], \
        #                   [  8.47971976e+00,  -4.14676234e+00], \
        #                   [  3.57665399e-02,  -3.61949992e-03], \
        #                   [  7.56323595e+00,   1.40629271e+00], \
        #                   [ -1.20773866e+00,   6.71621248e-02]])
        coeffs = np.array([[  1.14283341e+03,   2.48767872e+01], \
                           [ -9.97029153e+01,  -3.18909650e+00], \
                           [ -3.13420276e+02,   1.38021793e+01], \
                           [  2.15133629e+00,   1.01468495e-01], \
                           [ -1.89909459e+00,   7.37298161e-01], \
                           [  1.63137901e+01,  -7.87431895e-01]])
    
    dist = 1.
    distold = 2.
    count = 0
    damp = .01
    XYold = np.ones((T-1, nx+ny))

    while dist > 1e-6:
        count = count + 1
        X = np.zeros((T+1, nx))
        Y = np.zeros((T+1, ny))
        Xin = np.zeros((T, nx+nz))
        A = np.exp(Z)
        x = np.zeros((T,(pord*2)))
        X[0], Y[0] = XYfunc(Xstart, Z[0], XYparams, coeffs)
        for t in range(1,T+1):
            X[t], Y[t] = XYfunc(X[t-1], Z[t-1], XYparams, coeffs)
            Xin[t-1,:] = np.concatenate((X[t-1], A[t-1]))
            x[t-1,:] = poly1(Xin[t-1,:], XYparams)
            X1 = X[0:T]
            Y1 = Y[0:T]
            # plot time series
        if count % 10 == 0:
            timeperiods = np.asarray(range(0,T))
            plt.subplot(2,1,1)
            plt.plot(timeperiods, X1, label='X')
            #plt.axhline(y=kbar, color='r')
            plt.subplot(2,1,2)
            plt.plot(timeperiods, Y1, label='Y')
            #plt.axhline(y=ellbar, color='g')
            plt.xlabel('time')
            # plt.legend(loc=9, ncol=(nx+ny))
            plt.show()    
    
        # Generate consumption, lambda, and gamma series
        r = alpha*X[0:T]**(alpha-1)*(A[0:T]*Y[0:T])**(1-alpha)
        w = (1-alpha)*X[0:T]**alpha*(A[0:T]*Y[0:T])**(-alpha)
        c = (1-tau)*(w[0:T]*Y[0:T] + (r[0:T] - delta)*X[0:T]) + X[0:T] \
            + tau*(w[0:T]*Y[0:T] + (r[0:T] - delta)*X[0:T]) - X[1:T+1]
        # T-by-1
        Lam = (c[0:T-1]**(-gam)*(1-tau)*w[0:T-1]) / (chi*Y[0:T-1]**theta)
        # (T-1)-by-1
        Gam = (beta*c[1:T]**(-gam)*(1 + (1-tau)*(r[1:T] - delta))) \
            / (c[0:T-1]**(-gam))
        # (T-1)-by-1
    
        # update values for X and Y
        Xnew = (Gam)*X[1:T]
        Ynew = (Lam)*Y[1:T]
        XY = np.append(Xnew, Ynew, axis = 1)
        x = x[0:T-1,:]
        
        if fittype == 'MVOLS':
            coeffsnew = MVOLS(XY, x)
        
        dist = np.mean(np.abs(1-XY/XYold))
        print('count ', count, 'distance', dist, 'distold', distold, \
              'damp', damp)
        
        if dist < distold:
            damp = damp*1.05
            if damp > 1.:
                damp = 1.
        else:
            damp = damp*.8

        distold = 1.*dist
    
        # update coeffs
        XYold = XY
        coeffs = (1-damp)*coeffs + damp*coeffsnew
        if count % 10 == 0:
            print('coeffs', coeffs)
    return coeffs
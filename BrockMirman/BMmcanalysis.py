'''
Analysis of Monte Carlos for Simple ILA Model
'''
import numpy as np
from BMplots import BMplots
    

def mcanalysis(mcdata, preddata, bardata, histdata, name, nsim):
    '''
    This function finds confidence bands for data from the Monte Carlo
    simulations.  It also plots predictions and with confidence bands, and 
    predictions versus the final simulation as an example.
    
    Inputs:
    -----------  
    mcdata: a list of numpy arrays with simulations in the rows and
        observations in the columns
    preddata: a list of 1-dimensional numpy arrays for the period zero
        predictions from the model
    bardata: a list of steady state values from the baseline
    histdata: a list of 1-dimensional numpy arrays for the final simulation 
    name: a string that is used when saving the plots and other files
    nsim: the number of Monte Carlo simulations that have been run
    
    Outputs:
    -----------  
    avgdata: list of 1-dimensional numpy arrays containing the average values 
        from the simulations for each time period
    uppdata: list of 1-dimensional numpy arrays containing the upper confidence
        bands from the simulations for each time period
    lowdata: list of 1-dimensional numpy arrays containing the lower confidence
        bands from the simulations for each time period
    '''    
    
    #unpack data
    (kmc, zmc, Ymc, wmc, rmc, Tmc, cmc, imc, umc, foremeanmc,\
        zformeanmc, RMsqEerrmc) = mcdata
    # calculate and report statistics and charts from Monte Carlos  
    (kpred, zpred, Ypred, wpred, rpred, Tpred, cpred, ipred, \
        upred) = preddata   
    (kbar, zbar, Ybar, wbar, rbar, Tbar, cbar, ibar, ubar) = bardata
    (khist, zhist, Yhist, whist, rhist, Thist, chist, ihist, \
            uhist) = histdata
          
    # now sort the Monte Carlo matrices over the rows
    kmc = np.sort(kmc, axis = 0)
    zmc = np.sort(zmc, axis = 0)
    Ymc = np.sort(Ymc, axis = 0)
    wmc = np.sort(wmc, axis = 0)
    rmc = np.sort(rmc, axis = 0)
    Tmc = np.sort(Tmc, axis = 0)
    cmc = np.sort(cmc, axis = 0)
    imc = np.sort(imc, axis = 0)
    umc = np.sort(umc, axis = 0)
    foremeanmc = np.sort(foremeanmc, axis = 0)
    zformeanmc = np.sort(zformeanmc, axis = 0)
    
    # find the average values for each variable in each time period across 
    # Monte Carlos
    kavg = np.mean(kmc, axis = 0)
    zavg = np.mean(zmc, axis = 0)
    Yavg = np.mean(Ymc, axis = 0)
    wavg = np.mean(wmc, axis = 0)
    ravg = np.mean(rmc, axis = 0)
    Tavg = np.mean(Tmc, axis = 0)
    cavg = np.mean(cmc, axis = 0)
    iavg = np.mean(imc, axis = 0)
    uavg = np.mean(umc, axis = 0)
    foremeanavg = np.mean(np.abs(foremeanmc), axis = 0)
    zformeanavg = np.mean(np.abs(zformeanmc), axis = 0)
    RMsqEerravg = np.mean(np.abs(RMsqEerrmc), axis = 0)
    
    # find the rows for desired confidence bands
    conf = .1
    low = int(np.floor((conf/2)*nsim))
    high = nsim - low
    
    # find the upper and lower confidence bands for each variable
    kupp = kmc[high,:]
    zupp = zmc[high,:]
    Yupp = Ymc[high,:]
    wupp = wmc[high,:]
    rupp = rmc[high,:]
    Tupp = Tmc[high,:]
    cupp = cmc[high,:]
    iupp = imc[high,:]
    uupp = umc[high,:]
    foremeanupp = foremeanmc[high,:]
    zformeanupp = zformeanmc[high,:]
    
    klow = kmc[low,:]
    zlow = zmc[low,:]
    Ylow = Ymc[low,:]
    wlow = wmc[low,:]
    rlow = rmc[low,:]
    Tlow = Tmc[low,:]
    clow = cmc[low,:]
    ilow = imc[low,:]
    ulow = umc[low,:]
    foremeanlow = foremeanmc[low,:]
    zformeanlow = zformeanmc[low,:]
    
    # create a list of time series to plot
    dataplot = np.array([kpred/kbar, kupp/kbar, klow/kbar, khist/kbar, \
        zpred, zupp, zlow, zhist, \
        Ypred/Ybar, Yupp/Ybar, Ylow/Ybar, Yhist/Ybar, \
        wpred/wbar, wupp/wbar, wlow/wbar, whist/wbar, \
        rpred/rbar, rupp/rbar, rlow/rbar, rhist/rbar, \
        Tpred/Tbar, Tupp/Tbar, Tlow/Tbar, Thist/Tbar, \
        cpred/cbar, cupp/cbar, clow/cbar, chist/cbar, \
        ipred/ibar, iupp/ibar, ilow/ibar, ihist/ibar, \
        upred/ubar, uupp/ubar, ulow/ubar, uhist/ubar])
    
    # plot using Simple ILA Model Plot.py
    BMplots(dataplot, name)
    
    # create lists of data to return
    avgdata = (kavg, zavg, Yavg, wavg, ravg, Tavg, cavg, iavg, uavg, \
               foremeanavg, zformeanavg, RMsqEerravg) 
    uppdata = (kupp, zupp, Yupp, wupp, rupp, Tupp, cupp, iupp, uupp, \
               foremeanupp, zformeanupp) 
    lowdata = (klow, zlow, Ylow, wlow, rlow, Tlow, clow, ilow, ulow, \
               foremeanlow, zformeanlow) 
    
    return avgdata, uppdata, lowdata
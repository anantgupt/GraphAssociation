# -*- coding: utf-8 -*-
"""
Created on Wed May  1 20:54:50 2019
Analyzed effect of FFT, NOMP (NOMP better, see May19 slides or workflowy)
@author: gupta
"""
import GAutils
import GAutils.master_simulator3 as ms3
import GAutils.config as cfg
import numpy as np
from IPython import get_ipython
from datetime import date

def set_it(itrx, xval, idxa, val):
    it_name=['roba','snra','Nsensa','Noba','swidtha']
    it_xlbl = ['Robust level','SNR (dB)','Num. Sensors','Num. Targets','Array width (m)']
    exec("ms3.set_params('"+it_name[itrx]+"',xval)")
    ms3.set_params('Ninst',len(xval))
    ms3.set_params('rng_used',xval)
    ms3.set_params('xlbl',it_xlbl[itrx])
    for i, idx in enumerate(idxa):
        exec("ms3.set_params('"+it_name[idx]+"',np.ones(len(xval), dtype='int')*val[i])")

def run_it(datef, rng, itrx, itry):
    for num, i in enumerate(rng):
        exec("cfg."+itry+"a=i*np.ones(cfg.Ninst, dtype='int')")
        cfg.folder= datef +itrx+'-'+itry+str(i)
        print('Running '+str(num)+'/'+str(len(rng)))
        ms3.main()
        
def main():
    datef =('results'+str(date.today().month)+'_'+str(date.today().day)+'/fig_')
    cfg.Nf = 20 # was 50
    
    rob_rng = [0,1,2]
    sep_th_rng = [0.5,0.9,1.1,1.5]
    snr_rng = [-20,-15,-10,0,10]
    Nsens_rng = [4,5,6,8,10,12]
    Nob_rng = np.linspace(1,28,9, dtype='int') 
    swidth_rng = [0.1,0.2,0.4,0.8,1.6,2.4,3.2,4,5]
    
    rob_std = 1
    sep_th_std = 0.8
    snr_std = -10
    Nsens_std=4
    Nob_std=10
    swidth_std = 2
    
    cfg.sep_th = sep_th_std

    # Rob vS Nob
    set_it(3, Nob_rng, [1,2,4],[snr_std, Nsens_std, swidth_std])
    run_it(datef, np.arange(0,Nsens_std-2),'Nob','rob')
    # Rob vS swidth
    set_it(4, swidth_rng, [1,2,3],[snr_std, Nsens_std, Nob_std])
    run_it(datef, np.arange(0,Nsens_std-2),'swidth','rob')
    
    # Rob vS SNR
    set_it(1, snr_rng, [2,3,4],[Nsens_std, Nob_std, swidth_std])
    run_it(datef, np.arange(0,Nsens_std-2),'snr','rob')

    # Rob vS Nsens
    set_it(2, Nsens_rng, [1,3,4],[snr_std, Nob_std, swidth_std])
    run_it(datef, np.arange(0,np.min(Nsens_rng)-2),'Nsens','rob')


    
if __name__ == "__main__":
    __spec__ = None
    ipython = get_ipython()
    ipython.magic('%load_ext autoreload')
    ipython.magic('%autoreload 2')    
    ipython.magic('%matplotlib')
    
    main()
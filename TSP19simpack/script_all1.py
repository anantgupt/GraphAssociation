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
from datetime import date, datetime
 
def main():
    datef =('results'+str(date.today().month)+'_'+str(date.today().day)
            +'_'+str(datetime.now().hour)+str(datetime.now().minute)+'/fig_')
    cfg.Nf = 50 # was 50
    
    rob_rng = [0,1,2]
    sep_th_rng = [0.5,0.9,1.1,1.5]
    snr_rng = [-15] #[-20,-15,-10,0,10]
    Nsens_rng = [4,5,6,8,10]
    Nob_rng = [1,2] #np.linspace(1,28,9, dtype='int') 
    swidth_rng = [0.1,0.2,0.4,0.8,1.6,2.4,3.2,4,5]
    
    rob_std = 1 #0
    snr_std = -10 #1
    Nsens_std=4 #2
    Nob_std=10 #3
    swidth_std = 4 #4
        
    sep_th_std = 0
    cfg.sep_th = sep_th_std
#    # SNR vS Rob
#    set_it(1, rob_rng, [2,3,4],[Nsens_std, Nob_std, swidth_std])
#    run_it(datef, snr_rng,'rob','snr')
#
#    # SNR vS Nsens
#    set_it(2, Nsens_rng, [0,3,4],[rob_std, Nob_std, swidth_std])
#    run_it(datef, snr_rng,'Nsens','snr')
    # SNR vS Nob
    set_it(3, Nob_rng, [0,2,4],[rob_std, Nsens_std, swidth_std])
    run_it(datef, snr_rng,'Nob','snr')
#    # SNR vS swidth
#    set_it(4, swidth_rng, [0,2,3],[rob_std, Nsens_std, Nob_std])
#    run_it(datef, snr_rng,'swidth','snr')

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

    
if __name__ == "__main__":
    __spec__ = None
    # ipython = get_ipython()
    # ipython.magic('%load_ext autoreload')
    # ipython.magic('%autoreload 2')    
    # ipython.magic('%matplotlib')
    
    main()
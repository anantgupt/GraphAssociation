#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 11:57:27 2019
Use this code to edit figures saved using pickle dump
@author: anantgupta
"""

import matplotlib.pyplot as plt
import pickle as pl
import numpy as np

# Load figure from disk and display

#fig_handle = pl.load(open('results6_14/fig_obj_est2/plot4.pickle','rb'))
#fig_handle1 = pl.load(open('fig_Nsens-Nob1/plot11.pickle','rb'))
fig_handle2 = pl.load(open('DFT/fig_Nob-snr-15/plot4.pickle','rb'))
#fig_handle3 = pl.load(open('fig_Nsens-Nob11/plot11.pickle','rb'))
fig_handle4 = pl.load(open('NOMP/fig_Nob-snr-15/plot4.pickle','rb'))

#fig_handle3 = pl.load(open('fig_snr-Nob21/plot2.pickle','rb'))

ax = fig_handle2.axes
mse1=[0]*4;mse2=[0]*4;mse3=[0]*4;mse4=[0]*4


for i in range(2):
    rng = fig_handle2.axes[i].lines[1].get_data()[0]
#    crb1 = fig_handle1.axes[i].lines[1].get_data()[1]
#    mse1[i] = fig_handle1.axes[1].lines[i].get_data()[1]
    #cnt1 = fig_handle1.axes[3]
#    crb2[i] = fig_handle2.axes[i].lines[1].get_data()[1]
#    mse2[i] = fig_handle2.axes[i].lines[1].get_data()[1]
#    #cnt2 = fig_handle2.axes[3]
#    crb3 = fig_handle3.axes[i].lines[1].get_data()[1]
#    mse3[i] = fig_handle3.axes[1].lines[i].get_data()[1]
    mse4[i] = fig_handle4.axes[i].lines[0].get_data()[1]
    
    #cnt3 = fig_handle3.axes[3]
#for i in range(3):
#    for line in fig_handle2.axes[i].lines[:10]:
#        mser[t]=line.get_data()[1]
#        t+=1
#    ax[i].plot(rng, crb1, 'b--',label='CRB SNR=-10 dB')
#    ax[i].plot(rng, crb2[i], 'k--',label='CRB')
#    ax[i].plot(rng, mse2[i], 'r-.', label='DFT')
    ax[i].plot(rng, mse4[i], 'b-s', label='NOMP')
    
#    ax.plot(rng, mse1[i], 'b-', label='RMSE SNR=-10 dB')
#ax.plot(rng, crb2, 'k--', label='CRB')
#ax.plot(rng, mse2[0], 'r-.', label='DFT')
#ax.plot(rng, mse4[0], 'b-', label='NOMP')
#ax.plot(rng, mse4[0], 'b--s', label='Brute, Rob=1')
#    ax[i].plot(rng, mse3, 'r-', label='RMSE Nob=21')
    ax[i].legend(loc='best'),ax[i].grid(True);ax[i].set_xlabel('Num targets');
#plt.plot(rng, cnt1, 'b:', label='Count SNR=-10 dB')
#plt.plot(rng, cnt2, 'g:', label='Count SNR=0 dB')
#plt.plot(rng, cnt3, 'r:', label='Count SNR=10 dB')
#plt.errorbar(rng, np.sqrt(np.mean(mser**2, axis=0)), np.std(mser, axis=0), label='Range RMSE'),plt.yscale('log')
#ax.set_title('Association Complexity');ax.set_ylabel('Number of tracks visited')
#ax[1].set_title('Localization Error');ax[1].set_ylabel('RMSE (dB)')
#ax[2].set_title('Cardinality Error');ax[2].set_ylabel('Num Targets error')
plt.tight_layout()
#plt.title('Doppler Resolution');plt.xlabel('Doppler Separation (m/s)');plt.ylabel('RMSE (dB), Count')
#ax.set_yscale('log')
pl.dump(fig_handle2, open("plot_/rderror_vs_Nob.pickle", "wb"))

#%%
#plt.figure(2)
#fig_handle = pl.load(open('res_comb/plot_doppler_resolution.pickle','rb'))
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
def cf4(mode = 'Relax', width = 3.45, height = 2.6, font_size = 8):
    #fig_handle = pl.load(open('results6_14/fig_obj_est2/plot4.pickle','rb'))
    #fig_handle1 = pl.load(open('fig_Nsens-Nob1/plot11.pickle','rb'))
    fig_handle2 = pl.load(open('fig_Nsens-Nob10/plot11.pickle','rb'))
    #fig_handle3 = pl.load(open('fig_Nsens-Nob11/plot11.pickle','rb'))
    fig_handle4 = pl.load(open('fig_Nsens-Nob20/plot11.pickle','rb'))
    
    #fig_handle3 = pl.load(open('fig_snr-Nob21/plot2.pickle','rb'))
    
    fig, ax = plt.subplots(1,1)
    mse1=[0]*4;mse2=[0]*4;mse3=[0]*4;mse4=[0]*4
    for i in range(2):
        rng = fig_handle2.axes[1].lines[i].get_data()[0]

        mse2[i] = fig_handle2.axes[1].lines[i+1].get_data()[1]

        mse4[i] = fig_handle4.axes[1].lines[i+1].get_data()[1]
        

    ax.plot(rng, mse2[1], 'g-', label=mode+', Nob=10')
    ax.plot(rng, mse2[0], 'b--', label='Brute, Nob=10')
    ax.plot(rng, mse4[1], 'g-s', label=mode+', Nob=20')
    ax.plot(rng, mse4[0], 'b--s', label='Brute, Nob=20')
    #    ax[i].plot(rng, mse3, 'r-', label='RMSE Nob=21')
    ax.legend(loc='best'),ax.grid(True);ax.set_xlabel('Num Sensors');
    ax.set_title('Association Complexity');ax.set_ylabel('Number of tracks visited')
    #ax[1].set_title('Localization Error');ax[1].set_ylabel('RMSE (dB)')
    #ax[2].set_title('Cardinality Error');ax[2].set_ylabel('Num Targets error')
    plt.tight_layout()
    #plt.title('Doppler Resolution');plt.xlabel('Doppler Separation (m/s)');plt.ylabel('RMSE (dB), Count')
    ax.set_yscale('log')
    fig.set_size_inches(width, height, forward=True)
    # v--- change title and axeslabel font sizes manually
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
                 ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(font_size)
    plt.tight_layout()
    pl.dump(fig, open("Sel_figs/plot_complexity_vs_Nob.pickle", "wb"))
    fig.savefig('Sel_figs/plot_complexity_vs_Nob.pdf')
    #%%
    #plt.figure(2)
    #fig_handle = pl.load(open('res_comb/plot_doppler_resolution.pickle','rb'))
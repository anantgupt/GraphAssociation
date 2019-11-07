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
def cf5(mode = 'Relax', width = 3.45, height = 2.6, font_size = 8):
    #fig_handle = pl.load(open('results6_14/fig_obj_est2/plot4.pickle','rb'))
    #fig_handle1 = pl.load(open('fig_Nsens-Nob1/plot11.pickle','rb'))
    fig_handle2 = pl.load(open('fig_rob-swidth0.4/plot3.pickle','rb'))
    #fig_handle3 = pl.load(open('fig_Nsens-Nob11/plot11.pickle','rb'))
    fig_handle4 = pl.load(open('fig_rob-swidth0.8/plot3.pickle','rb'))
    
    #fig_handle3 = pl.load(open('fig_snr-Nob21/plot2.pickle','rb'))
    
    fig, ax = plt.subplots(1,1)
    mse1=[0]*4;mse2=[0]*4;mse3=[0]*4;mse4=[0]*4
    if 1:
        rng = fig_handle2.axes[2].lines[0].get_data()[0]
        mse2 = fig_handle2.axes[2].lines[0].get_data()[1]
        mse4 = fig_handle4.axes[2].lines[0].get_data()[1]
        
    ax.plot(rng, mse2, 'g-', label=mode+', Rob=0')
    #ax.plot(rng, mse2[0], 'b--', label='Brute, Rob=0')
    ax.plot(rng, mse4, 'b-', label=mode+', Rob=1')
    #ax.plot(rng, mse4[0], 'b--s', label='Brute, Rob=1')
    #    ax[i].plot(rng, mse3, 'r-', label='RMSE Nob=21')
    ax.legend(loc='best'),ax.grid(True);ax.set_xlabel('Robustness level');
    ax.set_title('Cardinality Error');ax.set_ylabel('Error in Num Targets')

    fig.set_size_inches(width, height, forward=True)
    # v--- change title and axeslabel font sizes manually
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
                 ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(font_size)
    plt.tight_layout()
    pl.dump(fig, open("Sel_figs/plot_card_vs_rob.pickle", "wb"))
    fig.savefig('Sel_figs/plot_card_vs_rob.pdf')
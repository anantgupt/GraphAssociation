# -*- coding: utf-8 -*-
"""
Created on Sat Nov  2 22:10:13 2019
# Runs all plotting scripts in Extract_Results directory
@author: gupta
"""
import os, argparse
from colorama import Fore, Style
import matplotlib as mpl
import matplotlib.pyplot as plt
import Extract_Results.create_fig1 as cf1
import Extract_Results.create_fig1b as cf1b 

import Extract_Results.create_fig2 as cf2 
import Extract_Results.create_fig3 as cf3 

import Extract_Results.create_fig4 as cf4 
import Extract_Results.create_fig4b as cf4b 
import Extract_Results.create_fig4c as cf4c
 
import Extract_Results.create_fig5 as cf5
import Extract_Results.create_fig5b as cf5b 

import Extract_Results.create_fig6 as cf6 
import Extract_Results.create_fig6b as cf6b 

import Extract_Results.create_fig7 as cf7 
import Extract_Results.create_fig7b as cf7b 
import Extract_Results.create_fig8 as cf8 
import Extract_Results.create_fig9 as cf9

params = {
    'axes.labelsize': 8, # fontsize for x and y labels (was 10)
    'axes.titlesize': 8,
#    'text.fontsize': 8, # was 10
    'legend.fontsize': 8, # was 10
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'text.usetex': True,
    'font.size': 8,
    'font.family': 'serif',
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'grid.linestyle':':',       # dotted
    'grid.linewidth':0.4,     # in points
    'lines.linewidth':0.8
}
mpl.rcParams.update(params)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--f', default='results11_1_20502_SPEKF-heap',type=str, help='Result Folder')

    args = parser.parse_args()

    folder = args.f # u'results11_1_20502_SPEKF-heap'
    os.chdir(os.path.join(os.path.abspath(os.path.curdir),folder))

    mode = str(folder.split('_')[-1])
    res_list = {'cf1':'7', 'cf1b':'7',
                'cf2':'7', 'cf3':'7',
                'cf4':'', 'cf4b':'', 'cf4c':'',
                'cf5':'','cf5b':'','cf6':'','cf6b':'7',
                'cf7':'7','cf7b':'',
                'cf8':'',
                'cf9':'7'}
    try:
        os.makedirs('Sel_figs')
    except OSError:
        pass


    for res, size in res_list.items():
        print('Running '+res+"('"+mode+"',"+size+'): ', end='')
        try:
            exec(res+'.'+res+"('"+mode+"',"+size+')')
            plt.close('all')
            print(Fore.GREEN,' Done \x1b[0m')
        except Exception as e:
            print(Fore.RED,e,'\x1b[0m')
    # plt.show()

    # try:
    #     cf1.cf1(7)
    #     cf1b.cf1b(7)
    # except Exception as e:
    #     print(e)
    # try:
    #     cf2.cf2()
    #     cf3.cf3(7)
    # except Exception as e:
    #     print(e)
    # try:
    #     cf4.cf4()
    #     cf4b.cf4b()
    #     cf4c.cf4c()
    # except Exception as e:
    #     print(e)
    # try:
    #     cf5.cf5() # Not Found
    #     cf5b.cf5b()
    #     cf6.cf6()
    #     cf6b.cf6b(7)
    # except Exception as e:
    #     print(e)
    # try:
    #     cf7.cf7(7)
    #     cf7b.cf7b()
    # except Exception as e:
    #     print(e)
    # try:
    #     cf8.cf8()
    # except Exception as e:
    #     print(e)
    # try:
    #     cf9.cf9(7)
    # except Exception as e:
    #     print(e)

if __name__ == "__main__":
    main()
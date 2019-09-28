#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 16:11:08 2019
Analyze performance of multi sensor localization algorithms
@author: anantgupta
"""
import numpy as np
import matplotlib.pyplot as plt
import multiprocessing as mp
import pickle
import importlib
from IPython import get_ipython
from functools import partial
import os as os
from tqdm import tqdm
import matplotlib.animation as animation
# Custom libs
import objects as ob
import config as cfg # Sim parameters
import proc_est as pr
importlib.reload(cfg)
import simulate_snapshot2 as sim2
import perf_eval as prfe
import PCRLB as pcrlb

def main():
#if 1: # For spyder     
    Nsensa = cfg.Nsensa
    
    # Naming algorithm names & Plotting
    alg_name = ['Estimation', 'Graph Init.','Association','Refinement']
        
    Nf = cfg.Nf
    Noba=cfg.Noba
    snra=cfg.snra
    
    static_snapshot = cfg.static_snapshot

    runtime = np.zeros([4,cfg.Ninst])

    ospa_error1 = np.zeros([cfg.Ninst,cfg.Nf,5]); ospa_error2 = np.zeros([cfg.Ninst,cfg.Nf,5])
    rd_error = np.zeros([cfg.Ninst,cfg.Nf,2])
    rd_err1 = np.zeros((cfg.Ninst, max(Nsensa), max(Noba),2))
    rd_err2 = np.zeros((cfg.Ninst, max(Nsensa), max(Noba),2))
    crb1 = np.zeros((cfg.Ninst, max(Nsensa), max(Noba),2))
    crbpv = np.zeros((cfg.Ninst, max(Nsensa), max(Noba),2))
    present = np.zeros((cfg.Ninst, max(Nsensa), max(Noba)))
    Nmiss1=np.zeros((cfg.Ninst, max(Nsensa)))
    Nfa1 =np.zeros((cfg.Ninst, max(Nsensa)))
    grca = [[] for _ in range(cfg.Ninst)]
    glena = np.zeros((cfg.Ninst, cfg.hN+1))
    plt.close('all')
    #for plt_n in range(1,6): plt.figure(plt_n), plt.clf()
    
    print('CPU count = ',str(mp.cpu_count()))
    #%%
    # Arrange sensors in worst case to build up a scene
    sensorsa = []
    sx=np.linspace(-max(cfg.swidtha), max(cfg.swidtha), max(cfg.Nsensa))
    for x in sx:
        sensorsa.append(ob.Sensor(x,0))
        
    np.random.seed(28)
    seeda = np.random.randint(1000, size=Nf)
    print('Seeds used:',seeda)
    # TODO NOTE: Min threshold might not be satisfied for all sensors!!
    scenea = [pr.init_random_scene(max(Noba), sensorsa, cfg.sep_th, seeda[f]) for f in range(Nf)]
    # Step 1: Init multiprocessing.Pool()
    pool = mp.Pool(mp.cpu_count())
    # snap = partial(sim2.run_snapshot, )
    for inst in tqdm(range(cfg.Ninst), desc='Instances'):
        Nob = Noba[inst]
        Nsens = Nsensa[inst]
        swidth = cfg.swidtha[inst]
        # Generate sensor each time
        sx=np.linspace(-swidth, swidth,Nsens)
        sensors = [ob.Sensor(x,0) for x in sx]

        Nsel = Nob# Genie info on # targets
#        print('Running {} of {} '.format(inst+1, cfg.Ninst))
        if cfg.parallel:
            # snapshot_results = []
            argarray = [(scenea[f][0:Nob], sensors, snra[inst], Nsel, seeda[f]) for f in range(Nf)]
            def collect_result(result):
                snapshot_results.append(result)
            # Step 2: `pool.apply` the `howmany_within_range()`
            # for f in range(Nf):
                # pool.apply_async(sim2.run_snapshot,
                #  args=(scenea[f][0:Nob], sensors, snra[inst], Nsel, seeda[f]),callback = collect_result) 
            snapshot_results = pool.starmap(sim2.run_snapshot, argarray)
        for f in tqdm(range(Nf),desc='Averaging', leave=False):  # Loop over frames
            if cfg.parallel:
                snapshot_result = snapshot_results[f]
            else:
                snapshot_result = sim2.run_snapshot(scenea[f][0:Nob], sensors, snra[inst], Nsel, seeda[f])
                
            runtime[:,inst] += snapshot_result['runtime']
            ospa_error1[inst,f,:] += snapshot_result['OSPAerror1'] # track based
            rd_error[inst,f,:] += np.mean(snapshot_result['RDerror'],axis =1)
            glen = snapshot_result['glen']
            glena[inst,:len(glen)] += np.array(glen)
            ret, det, Nmisst, Nfat, crbt, presentt = snapshot_result['RDpack']#prfe.compute_rde_targetwise(garda_sel, gardat, sensors)
            grca[inst].append( snapshot_result['loc'] )
            rd_err1[inst,:Nsens,:Nob,0] += np.array(ret)
            rd_err1[inst,:Nsens,:Nob,1] += np.array(det)
            rd_err2[inst,:Nsens,:Nob,0] += np.array(ret)**2
            rd_err2[inst,:Nsens,:Nob,1] += np.array(det)**2
            
            present[inst,:Nsens,:Nob] +=presentt
            crb1[inst,:Nsens,:Nob] += crbt
            Nmiss1[inst,:Nsens] += Nmisst
            Nfa1[inst,:Nsens] += Nfat

            crbpv[inst,:Nob] += snapshot_result['crbpv']/Nf
#            for i in range(3,5):
#                print(grca[inst][0][i-3].x)
#                print(ospa_error1[inst,f,i])
            #Average or update scene
            if not static_snapshot: scene = snapshot_result['next_scene'] # Update scene for next timestep
    # Step 3: Don't forget to close
    pool.close()  
    #%% Mask the arrays for averaging
    mask1 = np.ones((cfg.Ninst, max(Nsensa), max(Noba),2))
    for i in range(cfg.Ninst):
        mask1[i,:Nsensa[i],:Noba[i]]=0
    rd_err1 = np.ma.array(rd_err1, mask=mask1)
    rd_err2 = np.ma.array(rd_err2, mask=mask1)
    crb1 = np.ma.array(crb1, mask=mask1)
    present = np.ma.array(present, mask=mask1[:,:,:,0])
    Nmiss1=np.ma.array(Nmiss1, mask=mask1[:,:,0,0])
    Nfa1 =np.ma.array(Nfa1, mask=mask1[:,:,0,0])
    crbpv = np.ma.array(crbpv, mask=mask1)
    #%% INterference CRB
    

    #%% Final Plotting
    # plt.switch_backend('Qt4Agg')  
    rng_used = cfg.rng_used
    units=['(m)','(m/s)']
    plt.figure(1)
    plt.subplot(1,2,1)
    plt.bar(range(4), np.mean(runtime, axis=1), tick_label=alg_name),plt.grid(True)
    plt.subplot(1,2,2)
    pltn={}
    for i in range(4):
        pltn[i]= plt.plot(rng_used, runtime[i,:], label = alg_name[i]),plt.grid(True)
    plt.legend()
    fig = plt.gcf()
    fig.set_size_inches(8.8,4.8)
    plt.tight_layout()
    
    # Analyze track quality
#    plt.figure(2)
#    plt.plot(St_er)
#    plt.xlabel(cfg.xlbl),plt.ylabel('RMS Error'),plt.title('Error Nearest Phantom(Solid), Auto KF(Dashed)')
#    plt.plot(Auto_er, linestyle='--'),plt.legend(['x','y','v_x','x','y','v_x'])
    # Ananlyze
    capt2 = ['Position error','Velocity error']
    plt.figure(2)
    for i in range(3,5):
        plt.subplot(1,2,i-2)
        plt.errorbar(rng_used, np.mean(ospa_error1[:,:,i], axis=1), np.std(ospa_error1[:,:,i], axis=1), color='r')
        plt.errorbar(rng_used, np.mean(crbpv[:,:,:,i-3], axis=(1,2)), np.std(crbpv[:,:,:,i-3], axis=(1,2)), color='k')
        plt.xlabel(cfg.xlbl),plt.ylabel('RMS Error '+units[i-3]),plt.title(capt2[i-3]),plt.grid(True)
    fig = plt.gcf()
    fig.set_size_inches(8,4.8)
    plt.tight_layout()
    capt3 = ['Overall','Localization error','Cardinality error']
    plt.figure(3)
    for i in range(3):
        plt.subplot(1,3,i+1)
        plt.errorbar(rng_used, np.mean(ospa_error1[:,:,i], axis=1), np.std(ospa_error1[:,:,i], axis=1), color='r')
        plt.errorbar(rng_used, np.mean(ospa_error2[:,:,i], axis=1), np.std(ospa_error2[:,:,i], axis=1), color='g')
        plt.xlabel(cfg.xlbl),plt.ylabel('RMS Error (?)'),plt.title(capt3[i]),plt.grid(True)
        if i==1: plt.yscale('log'), plt.ylabel('RMS Error (?)')
    fig = plt.gcf()
    fig.set_size_inches(9.6,4.8)
    plt.tight_layout()
    capt4 = ['Range Error','Doppler Error']
    plt.figure(4)
    for i in range(2):
        plt.subplot(1,2,i+1)
        plt.errorbar(rng_used, np.mean(rd_error[:,:,i], axis =1), np.std(rd_error[:,:,i], axis =1))
        plt.xlabel(cfg.xlbl),plt.ylabel('RMS Error '+units[i]),plt.title(capt4[i]),plt.grid(True)
    plt.tight_layout()
    fig = plt.gcf()
    fig.set_size_inches(8,4.8)
    capt4 = ['Range Error, ','Doppler Error, ']
    if cfg.sensor_wise:
        plt.figure(5)
        for i in range(2):
            for j in range(Nsens):
                plt.subplot(2,Nsens, i*Nsens+j+1)
                plt.errorbar(rng_used, np.mean(rd_err1[:,j,:,i]/present[:,j,:],axis=1), 
                             np.sqrt(np.mean(rd_err2[:,j,:,i]/present[:,j,:]-(rd_err1[:,j,:,i]/present[:,j,:])**2, axis =1)),label='S{}'.format(j))
                if i==1: plt.xlabel(cfg.xlbl)
                if j==0: plt.ylabel('RMS Error '+units[i])
                plt.title(capt4[i]),plt.legend(),plt.grid(True)
        fig = plt.gcf()
        fig.set_size_inches(12.8,7.2)
        plt.tight_layout()
        plt.figure(6)
        for j in range(Nsens):
            plt.subplot(1,Nsens,j+1)
            for k in range(Nob):
                plt.plot(rng_used, present[:,j,k]/Nf, label='Ob{}'.format(k+1)),plt.title('Pr(detection)')
            if j==0: plt.ylabel(r'$P_D$')
            plt.xlabel(cfg.xlbl),plt.grid(True)
        fig = plt.gcf()
        fig.set_size_inches(12.8,4.8)
        plt.tight_layout()
        plt.figure(9)
        for j in range(Nsens):
            plt.subplot(2,Nsens,j+1)
            prfe.plotg(rd_err1[:,j,:,0].flatten(), np.sqrt(np.sum(crb1[:,j,:,0],
                       axis=(0,1))/sum(Noba*Nsens)),plt,True),plt.title(r'$\Delta R$ Sensor {}'.format(j+1))
            plt.subplot(2,Nsens,Nsens+j+1)
            prfe.plotg(rd_err1[:,j,:,1].flatten(), np.sqrt(np.sum(crb1[:,j,:,1],
                       axis=(0,1))/sum(Noba*Nsens)),plt,True),plt.title(r'$\Delta D$ Sensor {}'.format(j+1))
        fig = plt.gcf()
        fig.set_size_inches(12.8,7.2)
        plt.tight_layout()
        fig = plt.figure(7)
        plt.subplot(1,2,1)
        for j in range(Nsens):
            plt.plot(rng_used, Nmiss1[:,j]/Nf, label='S{}'.format(j+1))
        plt.title('Missed targets'),plt.legend(),plt.grid(True),plt.xlabel(cfg.xlbl),plt.ylabel(r'$E\left[(N_{est}-N_{true})_-\right]$')
        plt.subplot(1,2,2)
        for j in range(Nsens):
            plt.plot(rng_used, Nfa1[:,j]/Nf, label='S{}'.format(j+1))
        plt.title('False Targets'),plt.legend(),plt.grid(True),plt.xlabel(cfg.xlbl),plt.ylabel(r'$E\left[(N_{est}-N_{true})_+\right]$')
        resizefig(plt, 8,4.8)
        plt.figure(8)
        for i in range(2):
            for j in range(Nsens):
                plt.subplot(2,Nsens,Nsens*i+j+1)
                for k in range(Nob):
                    plt.plot(rng_used, np.sqrt((rd_err2[:,j,k,i]/present[:,j,k]-(rd_err1[:,j,k,i]/present[:,j,k])**2)))
                plt.gca().set_prop_cycle(None)# Reset coloring
                for k in range(Nob):
                    plt.plot(rng_used, np.sqrt(crb1[:,j,k,i]/present[:,j,k]), '--')
                if i==1: plt.xlabel(cfg.xlbl)
                if j==0: plt.ylabel('RMS Error '+units[i])
                plt.title(capt4[i]+'Sensor '+str(j+1)),plt.grid(True),plt.yscale('log')
        resizefig(plt, 12.8,7.2)
    else:
        plt.figure(5)
        for i in range(2):
            plt.subplot(1,2, i+1)
            plt.errorbar(rng_used, np.mean(rd_err1[:,:,:,i]/present,axis=(1,2)), 
                         np.sqrt(np.mean(rd_err2[:,:,:,i]/present-(rd_err1[:,:,:,i]/present)**2, axis =(1,2))))
            plt.xlabel(cfg.xlbl),plt.ylabel('RMS Error'),plt.title(capt4[i]),plt.grid(True)
        plt.figure(6)
        plt.errorbar(rng_used, np.mean(present[:,:,:]/Nf, axis=(1,2)), np.std(present/Nf, axis=(1,2))),plt.title('Probability of detection')
        plt.xlabel(cfg.xlbl),plt.ylabel('P_D'),plt.legend(rng_used),plt.grid(True)
        plt.figure(7)
        plt.errorbar(rng_used,np.mean( Nmiss1/Nf, axis=1),np.std( Nmiss1/Nf, axis=1), label= 'Miss')
        plt.errorbar(rng_used,np.mean( Nfa1/Nf, axis=1),np.std( Nfa1/Nf, axis=1),label = 'False Alarm')
        plt.title('Expected Miss, False Alarm'),plt.legend(),plt.grid(True)
        plt.figure(8)
        for i in range(2):
            plt.subplot(1,2,i+1)
            plt.errorbar(rng_used, np.sqrt(np.mean(rd_err2[:,:,:,i]/present-(rd_err1[:,:,:,i]/present)**2, axis=(1,2))),
                             np.sqrt(np.std(rd_err2[:,:,:,i]/present-(rd_err1[:,:,:,i]/present)**2, axis=(1,2))))
            plt.errorbar(rng_used, np.sqrt(np.mean(crb1[:,:,:,i]/present,axis=(1,2))),
                 np.sqrt(np.std(crb1[:,:,:,i]/present,axis=(1,2))), fmt= '--')
            plt.gca().set_prop_cycle(None)# Reset coloring
            plt.xlabel('Sensor'),plt.ylabel('RMS Error'),plt.title(capt4[i]),plt.grid(True),plt.yscale('log')
    plt.figure(10)
    plt.subplot(1,2,1)
    for i in range(cfg.Ninst):
        plt.plot(range(cfg.hN+1), (glena[i,:]/Nf), label = str(rng_used[i]))
    plt.legend(),plt.grid(True),plt.title('Graph nodes v/s relax iterations'),plt.ylabel('Num vertices')
    Ndet = np.array([[len(gr) for gr in grca[i]] for i in range(cfg.Ninst)])
    plt.subplot(1,2,2)
    plt.errorbar(rng_used, np.mean(Ndet, axis=1), np.std(Ndet, axis =1), label = 'Estimated')
    plt.plot(rng_used, cfg.Noba, 'k:', label = 'True')
    plt.legend(),plt.grid(True),plt.title('Number of targets detected'),plt.ylabel('Num vertices'),plt.xlabel(cfg.xlbl)
    resizefig(plt, 8,4.8)
    # Save files
    try:
        # Create target Directory
        os.makedirs(cfg.folder)
        print("Directory " , cfg.folder ,  " Created ") 
    except FileExistsError:
        print("Directory " , cfg.folder ,  " already exists")
    # Setup video files
    FFMpegWriter = animation.writers['ffmpeg']
    metadata = dict(title='Movie Test', artist='Anant',comment='Target motion')
    writer = FFMpegWriter(fps=1, metadata=metadata)
    fig = plt.figure(11)
    with writer.saving(fig, '{}/Scenes.mp4'.format(cfg.folder), dpi=100):
        for i, scene in enumerate(scenea):
            for j in range(cfg.Ninst):
                phlist = grca[j][i]
                plt.clf()
                for gr in phlist: plt.quiver(gr.x, gr.y,gr.vx,gr.vy, color='r', headwidth = 4, headlength=6, headaxislength=5)
                pr.plot_scene(plt, scene[:Noba[j]], sensorsa[:Nsensa[j]], 11, 'Scene {} with {} detections, SNR = {} dB'.format(i, np.round(np.sum(present[j,:,:],axis=1)/Nf/Noba[j],2), round(snra[j])))
                writer.grab_frame()

    for fignum in range(1,11):
        plt.figure(fignum)
        plt.savefig("{}/{}".format(cfg.folder,fignum), Transparent=True)
        pickle.dump(plt.figure(fignum), open("{}/plot{}.pickle".format(cfg.folder,fignum), "wb"))
    plt.show()

def resizefig(plt, x, y):
    fig = plt.gcf()
    fig.set_size_inches(x,y)
    plt.tight_layout()
        
if __name__ == "__main__":
    __spec__ = None
    ipython = get_ipython()
    ipython.magic('%load_ext autoreload')
    ipython.magic('%autoreload 2')    
    ipython.magic('%matplotlib')
    
    main()

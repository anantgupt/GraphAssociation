# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 18:54:50 2019
Contains function for operating on Graph
@author: gupta
"""
import numpy as np

# Custom libs
from GAutils import objects as ob
import copy as cp
from GAutils import proc_est as pr
from GAutils import ml_est as mle
# import config as cfg
from scipy.stats import chi2

def make_graph(garda, sensors, lskp=False, l2p=0):
    Ns=len(sensors)
    tol = 0 # tolerance for range bands
    Lp1, Lp2, Lt1, Lt2, Nnodes =0,0, 1,1,0
    G=[]
    for sid, gard in enumerate(garda):
        L=len(gard.g)
        G.append([ob.obs_node(gard.g[oid],gard.a[oid],abs(gard.r[oid]),gard.d[oid],oid, sid) for oid in range(L)])
        Lp1-=L*(L-1)/2 # Num of self edges to subtract later
        Lt1*=L # Total tracks without prunung
        Nnodes +=L
    Lp1+= Nnodes*(Nnodes-1)/2
    for i in range(1,Ns): 
        sobs_c = G[i] # ranges of current sensor
        j=i-1
        sobs_b = G[j]
        l1 = np.sqrt((sensors[i].x - sensors[j].x)**2+(sensors[i].y - sensors[j].y)**2) # sensor separation
        d = sensors[i].fov * l1 + tol # max range delta
        for sob_c in sobs_c:
            for sob_b in sobs_b:
                if abs(sob_b.r-sob_c.r)<d and abs(sob_b.r+sob_c.r)>d :
                    sob_c.insert_blink(sob_b)
                    sob_b.insert_flink(sob_c)
                    Lp2+=1
                    Lt2+=1+len(sob_b.lkb)
            if 0:
            #Add connection jumping across 1 sensor (more sensors?) 
            # Implement using hashmap which remembers track positions
                if lskp and i-2>=0: 
                    k=i-2
                    l2 = np.sqrt((sensors[i].x - sensors[k].x)**2+(sensors[i].y - sensors[k].y)**2)
                    djk = np.sqrt((sensors[j].x - sensors[k].x)**2+(sensors[j].y - sensors[k].y)**2)
                    dk = sensors[i].fov * l2 + tol # max range delta
                    sobs_k = G[k]
                    for sob_k in sobs_k:
                        if (abs(sob_k.r-sob_c.r)<dk and abs(sob_k.r+sob_c.r)>dk and not 
                            any([similar_paths(sob_c, sob_b, sob_k, sensors) for sob_b in sobs_b])):
                            sob_c.insert_blink(sob_k)
                            sob_k.insert_flink(sob_c)
                            Lp2+=1
                            Lt2+=1+len(sob_k.lkb)
            if 1:
                # Recursive implementation for P-skip connections
                k=i-2 # current index of backtracking
                while i-k<=lskp+1 and k>=0:
                    l2 = np.sqrt((sensors[i].x - sensors[k].x)**2+(sensors[i].y - sensors[k].y)**2)
                    dk = sensors[i].fov * l2 + tol # max range delta
                    sobs_k = G[k]
                    for sob_k in sobs_k:
                        if (abs(sob_k.r-sob_c.r)<dk and abs(sob_k.r+sob_c.r)>dk and not 
                            any([similar_paths(sob_c, sob_prev, sob_k, sensors) for sob_prev in G[k+1]])):
                            sob_c.insert_blink(sob_k)
                            sob_k.insert_flink(sob_c)
                            Lp2+=1
                            Lt2+=1+len(sob_k.lkb)
                    k-=1
    return G, Lt1

def similar_paths(sob_i, sob_j, sob_k, sensors):# Check if 3 nodes should be on same path or not
    pth =0.01# TODO: How to set this automatically
    vth = 0.01
    obij = pr.get_pos_from_rd(sob_i.r, sob_j.r, sob_i.d, sob_j.d, sob_i.sid , sob_j.sid, sensors)
    objk = pr.get_pos_from_rd(sob_k.r, sob_j.r, sob_k.d, sob_j.d, sob_k.sid , sob_j.sid, sensors)
    if obij and objk:
        if ((obij.x-objk.x)**2+(obij.y-objk.y)**2<pth) and ((obij.vx-objk.vx)**2+(obij.vy-objk.vy)**2<vth):
            return True
    return False
    
def enum_graph_sigs(G, sensors):
    # If no signatures observed then they should be intialized inside loop, 
    # here we assume atleast 1 track goes across all sensors
    s=len(sensors)-1
    Final_tracks = []
    while s>0: # s is sensor index of source
        for p, sobc in enumerate(G[s]):
            Nb = len(sobc.lkb)
            Nf = len(sobc.lkf)
            if (Nf == 0) & (Nb>0): # Stop track and store in final tracks
                sg = ob.SignatureTracks(sobc.r, sobc.d, s, sobc.g)# create new signature
                signatures = get_tracks(G, sobc, sg, sensors)
                Final_tracks.extend(signatures)# At sensor 0, Nb=0 for all, so all tracks will be saved
        s=s-1 # Move to previous sensor
#    for tracks in signatures:   
#        for track in tracks:
#            Final_tracks.append(track) 
    return Final_tracks, len(Final_tracks)

def get_tracks(G, nd, sig, sensors): # recursively extract tracks
    if nd.lkb:
        child_sigs = []
        for tnd in nd.lkb:
            new_sig = cp.copy(sig)
            new_sig.add_update3(tnd.r, tnd.d, tnd.g, tnd.sid, sensors)
            sig_pool = get_tracks(G, tnd, new_sig, sensors)
            child_sigs.extend(sig_pool)
        return child_sigs
    else:
        return [sig]

def get_Ntracks(nd): # recursively extract tracks from beginning
    N=0
    if nd.lkf:
        for tnd in nd.lkf:
            N +=1+ get_Ntracks(tnd)#*2
    return N
#        d_c = garda[i].d # Doppler of current
#        r_cp = garda[i-1].r # ranges from prev(below) sensor
#        d_cp = garda[i-1].d # ranges from prev(below) sensor
#        l1 = np.sqrt((sensors[i].x - sensors[i-1].x)**2+(sensors[i].y - sensors[i-1].y)**2) # sensor separation
#        d = sensors[i].fov * l1 + tol # max range delta
#        links = [] # [[] for l in range(len(r_c))] # Initialize List of Ns empty lists
#        for j,r in enumerate(r_c):
#            link_pr = [idx for idx,rcp in enumerate(r_cp) if abs(rcp-r)<d] #prev node indexs
#            
#            # to keep track going across sensors we link trac to atleast one obs
##            if not link_pr: link_pr = [abs(r_cp-r).argmin()] # NOTE: Point to nearest link if no other range is close, 
#            vx_asc = (r*d_c[j] - r_cp[link_pr]*d_cp[link_pr])/l1 # vx estimate bw j AND prev
#            if (l1p) & (i>1):
#                prunedid = [pid for pid, (vxasc, pnodeid) in enumerate(zip(vx_asc, link_pr))
#                if np.min(abs(ordered_links[i-1][pnodeid].vxa - vxasc)) < tol2/l1] # check common vxa with prev nodes childs
##                print(prunedid)
#                link_new = [link_pr[idx] for idx in prunedid]
#                vx_new = [vx_asc[idx] for idx in prunedid]
#                
#            else:
#                link_new = link_pr
#                vx_new = vx_asc
##                links.append(ob.link(link_pr, vx_asc))
#            if l2p:# level 2 pruning
#                link_cur = link_pr # indices of previous nodes associated with r_j
#                link_new = []
#                for bki in range(i-1):# backtrack: check bands with prev sensors
#                    l2 = np.sqrt((sensors[i].x - sensors[i-2-bki].x)**2+(sensors[i].y - sensors[i-2-bki].y)**2) # sensor separation
#                    dbk = sensors[i].fov * l2 + tol # max range delta
#                    for bkid, bknodeid in enumerate(link_cur):
#                        r_cb= garda[i-2-bki].r[ordered_links[i-bki-1][bknodeid]]
#                        d_cb= garda[i-2-bki].d[ordered_links[i-bki-1][bknodeid]]
#                        vx_bk = (r*d_c[j] - r_cb*d_cb)/l2 # vx estimate bw j and backtrack
#                        if l3p:
##                            print('sensor{}: r={},d={}, vx={}, vxj={}'.format(i, r_cb, d_cb,vx_bk,vx_asc[bkid]))
#                            ordered_links[i-bki-1][bknodeid] = [idx for idx,(rcb,vxbk) in enumerate(zip(r_cb,vx_bk))
#                            if (abs(rcb-r)<dbk) & (abs(vxbk-vx_asc[bkid])<tol2/l2)] #replace with valid idx 
#                        else:
#                            ordered_links[i-bki-1][bknodeid] = [idx for idx,rcb in enumerate(r_cb)
#                            if abs(rcb-r)<dbk] #replace with valid idx 
#                        set().union(link_new,ordered_links[i-bki-1][bknodeid]) #ranges in (i-bki-2) linked to r_j
#                    link_cur = link_new
#                    link_new=[]
#            links.append(ob.link(link_new, vx_new))
def get_g_thres(sig, scale, ag_pfa):
    if sig.N<3:
        return -np.inf # only 1 target cant make sense
    else:
        return scale[1]*chi2.isf(ag_pfa, 2*sig.N, loc=0, scale=1)# NOTE: Fudge factor 10
#        return np.sqrt(2*sig.N*2) # Roughly 2 sigma 95%
    
def get_l_thres(sig, scale, al_pfa):
    if sig.N<2:
        return -np.inf # only 1 target cant make sense
    else:
        return scale[0]*chi2.isf(al_pfa, 2*sig.N, loc=0, scale=1)# TODO: Wald statistic is normalized by CRB

def get_order(G, new_nd, target_nds, path, sensors):
    if target_nds:
        child_sigst = []
        g_cost=[]
        for tnd in target_nds:
            new_sig = cp.copy(path)
            try:
                new_sig.add_update3(tnd.r, tnd.d, tnd.g, tnd.sid, sensors)
            except ValueError as err:
                print(err.args)
                continue # Can print error happened                    
            if path.N<2: # Cannot calculate straigtness with 2 nodes
                g_cost.append(np.inf)
            else:
                g_cost.append(sum(new_sig.gc)) # use trace maybe
            child_sigst.append(new_sig)
        srtind = np.argsort(g_cost)
        childs = [target_nds[ind] for ind in srtind]
        child_sigs = [child_sigst[ind] for ind in srtind]
    else:
        childs=[]
        child_sigs=[]
    return childs, child_sigs

def Brute(G, nd, sig, sel_sigs, pid, sensors, cfgp, scale, minP): # recursive implementation
    childs, child_sigs = get_order(G, nd, nd.lkf, cp.copy(sig), sensors)
    ag_pfa, al_pfa, rd_wt = cfgp['ag_pfa'],cfgp['al_pfa'],cfgp['rd_wt']
    L3 = 0
    for (ndc, ndc_sig) in zip(childs, child_sigs):# Compute costs for all neighbors
        if not ndc.visited:
            pnext = cp.copy(pid)
            pnext.append(ndc.oid)
            L3+=Brute(G, ndc, ndc_sig, sel_sigs, pnext, sensors, cfgp, scale, minP)
    if not childs:# check for min cost(if node has no childs)
        if sig.N>=minP:# Only tolerate 1 miss
            l_cost, g_cost = mle.est_pathllr(sig, sensors, minP, rd_wt, False)#+wp*(len(sensors)-sig.N)    
            L3+=1
            # np.set_printoptions(precision=3)
#            print((pid, l_cost, round(get_l_thres(sig)), sig.gc))
            if l_cost < get_l_thres(sig, scale, al_pfa): # Based on CRLB
                sig.llr = l_cost
                sig.pid = pid
                sel_sigs.append(sig)# sig in this list should be updated whenever in nd is updated
        return L3
def Brute_iter(Gfix, sel_sigs, sensors, glen, cfgp): # recursive implementation
    G = cp.copy(Gfix)
    scale = cfgp['hscale']
    hN = cfgp['hN']
    minP = len(sensors)# Start with full length track search
    L3 = 0 # Counting edges visited
    for h in range(hN):
#        print('Graph has {} nodes.'.format(sum(len(g) for g in G)))
        sig_final =[]
        for i, sobs in enumerate(G):
            for pid, sobc in enumerate(sobs):
    #            print(G[ind].val)
                sig_origin = ob.SignatureTracks(sobc.r, sobc.d, i, sobc.g)# create new signature
                L3+=Brute(G, sobc, sig_origin, sig_final, [pid], sensors, cfgp, scale, minP)
        new_sigs = visit_selsigs(G, sig_final)
        sel_sigs.extend(new_sigs)
        G, stopping_cr = remove_scc(G, sensors)# Add skip connection
        glen.append(sum(len(g) for g in G))
        if stopping_cr:# Until path of length minP left in Graph
            break
        scale = scale*cfgp[incr]
        if glen[-1]-glen[-2]==0 and minP>len(sensors)-cfgp['rob']:
            minP-=1
    return glen, L3
        
def remove_scc(G, sensors):# efficient in-place implementation
    flag = 0
    for i, sobs in enumerate(G):# NOTE: Should delete node from G instead of creating new G
        oidn = 0
        del_ind = []
        for pid, sobc in enumerate(sobs):
            if sobc.visited:
                for ndc in sobc.lkb:# TODO: Add skip connection here
                    ndc.lkf.remove(sobc)
                for ndc in sobc.lkf:
                    ndc.lkb.remove(sobc)
                del_ind.append(pid)
            else:
                G[i][pid].oid = oidn # Update observation order
                oidn +=1
        for did in reversed(del_ind):  G[i].pop(did)
        if len(G[i])==0: # Just stop here if need to save time
#            print([sobc.visited for pid, sobc in enumerate(sobs)])
            flag+=1
            if flag>1: return G, True # Empty consecutive sensor
        else: # Reset flag if obs found
            flag = 0
    return G, False

def remove_scc2(G, sensors):# Inefficient implementation
    garda=[]
    flag = 0
    for i, sobs in enumerate(G):# NOTE: Should delete node from G instead of creating new G
        gard_new = ob.gardEst()
        for pid, sobc in enumerate(sobs):
            if not sobc.visited:
                gard_new.add_Est(sobc.g, 0, sobc.r, sobc.d)
        if len(gard_new.r)==0: # Just stop here if need to save time
#            print([sobc.visited for pid, sobc in enumerate(sobs)])
            flag+=1
            if flag>1: return G, True # Empty consecutive sensor
        else: # Reset flag if obs found
            flag = 0
        garda.append(gard_new)
    G = make_graph(garda, sensors, True) # With skip connextion
    return G, False

def Relax(Gfix, sel_sigs, sensors, glen, cfgp): # recursive implementation
    G = cp.copy(Gfix)
    scale = cfgp['hscale']
    hN = cfgp['hN']
    L3 = 0
    minP = len(sensors)
    for h in range(hN):
#        print('Graph has {} nodes.'.format(sum(len(g) for g in G)))
        for i, sobs in enumerate(G):
            for pid, sobc in enumerate(sobs):
    #            print(G[ind].val)
                sig_origin = ob.SignatureTracks(sobc.r, sobc.d, i, sobc.g)# create new signature
                L3+=DFS(G, sobc, sig_origin, sel_sigs, [pid], sensors, cfgp, minP, scale, opt=[False,False,False] )
        G, stopping_cr = remove_scc(G, sensors)# Add skip connection
        glen.append(sum(len(g) for g in G))
        if stopping_cr:# Until path of length minP left in Graph
            break
        scale = scale*cfgp['incr']
        if glen[-1]-glen[-2]==0 and minP>len(sensors)-cfgp['rob']:
            minP-=1
    return glen, L3
    
def DFS(G, nd, sig, sel_sigs, pid, sensors, cfgp, minP, scale=[1e2,1e4], opt=[True,False,False]): # recursive implementation
    
    cand_sig =[]
    llr_min = np.inf
    L3 = 0 # Count edges visited
    ag_pfa, al_pfa, rd_wt = cfgp['ag_pfa'],cfgp['al_pfa'],cfgp['rd_wt']
    if nd.visited:# Check if tracks could be joined
        if opt[0]:# Choose best path acc to min lcost
            sig_used = sel_sigs[nd.used]
            nid = list(sig_used.sindx).index(nd.sid)
            if nid<sig_used.N-1:
                sig.add_sig(sig_used, nid+1, sensors)# create new signature
                llr_new, gc_new = mle.est_pathllr(sig, sensors, minP+2, rd_wt);L3+=1
                if llr_new < sig_used.llr and abs(sum(sig.gc))<abs(sum(sig_used.gc)) and sig.N>=minP:
                    if llr_new<llr_min:
                        sig.llr = llr_new
                        sig.pid = pid+sig_used.pid[nid+1:]
                        cand_sig = sig
                        repl_sigid = nd.used
                        repl_point = nid           
                        llr_min = llr_new
    else:
        childs, child_sigs = get_order(G, nd, nd.lkf, cp.copy(sig), sensors)
        for (ndc, ndc_sig) in zip(childs, child_sigs):# Compute costs for all neighbors
            if not path_check(G, sig, pid): break # Added to stop DFS if parent is visited!
            if not ndc.visited:
                pnext = cp.copy(pid)
                pnext.append(ndc.oid)
                L3+=DFS(G, ndc, ndc_sig, sel_sigs, pnext, sensors, cfgp, minP, scale, opt)
            elif opt[1]:# Skip connection ndc
                sig_used = sel_sigs[ndc.used]
                nid = list(sig_used.sindx).index(ndc.sid)
                if nid<sig_used.N-1:
                    ndc_sig.add_sig(sig_used, nid+1, sensors)# create new signature
                    llr_new, gc_new = mle.est_pathllr(ndc_sig, sensors, minP+2, rd_wt); L3+=1
                    if llr_new < sig_used.llr and abs(sum(ndc_sig.gc))<abs(sum(sig_used.gc)) and ndc_sig.N>=minP:
                        if llr_new<llr_min:
                            ndc_sig.llr = llr_new
                            ndc_sig.pid = pid+sig_used.pid[nid+1:]
                            cand_sig = ndc_sig
                            repl_sigid = ndc.used
                            repl_point = nid           
                            llr_min = llr_new
        if cand_sig: # Check if node got visited by better track
            if nd.visited:
                if llr_min < sel_sigs[nd.used].llr:
                    # Erase existing track without nd
                    sig_temp = sel_sigs[nd.used]
                    sel_sigs[nd.used] = None
                    update_G(G, sig_temp.sindx,sig_temp.pid, False, None)# Mark new ones as visited
                else:
                    cand_sig = []

        if not nd.visited:# check for min cost(if node not used)
            if sig.N>=minP:
                l_cost, g_cost = mle.est_pathllr(sig, sensors, minP+2, rd_wt);L3+=1
#                print(l_cost, get_l_thres(sig), g_cost, get_g_thres(sig), pid )
                if l_cost < get_l_thres(sig, scale, al_pfa) and abs(sum(sig.gc))<get_g_thres(sig, scale, ag_pfa): # Based on CRLB
                    if opt[2]:# Backtrack to find best path using lkb along sig
                        if path_check(G, sig, pid):
                            sig_min = sig
                            pid_min = pid
                            sigb = ob.SignatureTracks(nd.r, nd.d, nd.sid)
                            max_g_cost = sum(sig.gc)
                            bk_l_cost, sig_back, pid_bk = DFSr(G, nd, sigb, max_g_cost, [nd.oid], sensors,wt)
                            # Mark nodes as visited
                            if bk_l_cost < l_cost and path_check(G, sig_back, pid_bk):# If backward path not found, means it was visited by other path
                                sig_min = sig_back
                                pid_min = pid_bk# traversed in rev order
                            update_G(G, sig_min.sindx, pid_min, True, sig)
                            sel_sigs.append(sig_min)# sig in this list should be updated whenever in nd is updated
                    else:# Just check path doesn't have already used nodes
                        if path_check(G, sig, pid):
                            sig.llr = l_cost
                            sig.pid = pid
                            sel_sigs.append(sig)
                            update_G(G, sig.sindx, pid, True, len(sel_sigs)-1)# Stores id of sig in sel_sigs
                            # sig in this list should be updated whenever in nd is updated
    if cand_sig:# Replace with the one which minimizes LLR
        # Add new track at nd
        sig_used = sel_sigs[repl_sigid]
        for iold in range(repl_point):# MArk old as free
            si=sig_used.sindx[iold]
            pi=sig_used.pid[iold]
            G[si][pi].visited = False
            G[si][pi].used = None
        update_G(G, cand_sig.sindx,cand_sig.pid, True, repl_sigid)# Mark new ones as visited
        sel_sigs[repl_sigid]=cand_sig
        print('State changed to x={}'.format(cand_sig.pid))
    return L3

def update_G(G, sindx, pid, vis, used):
    for (si,pi) in zip(sindx,pid):# Mark new ones as visited
        G[si][pi].visited = vis
        G[si][pi].used = used
    return

def path_check(G, sig, pid, allow_breaks=False):# Allows crossing paths
    flag = 0
    for (ob_id, cur_sid) in zip(pid, sig.sindx):
#        print(cur_sid, ob_id)
        if G[cur_sid][ob_id].visited:
            if not allow_breaks:
                return False
            flag+=1# Increment visited node count
        else: 
            flag = 0# Reset to 0 if unvisited node appears
        if flag>1:# IF 2 consecutive nodes in path were visited
            return False
    return True
def DFSr2(G, nd, sigb, max_g_cost, pidb, sensors, wt):# Picks overall min L-cost over unvisited
    wp=5
    g_costs = []
    sig_list = []
    pidn_list = []
    childs, child_sigs = get_order(G, nd, nd.lkb, cp.copy(sigb), sensors)
    
    for (ndc, ndc_sig) in zip(childs, child_sigs):# Compute costs for all neighbors
        if 1: #np.trace(ndc_sig.state_end.cov) <=max_g_cost:
            if not ndc.visited:
                pidb_next = cp.copy(pidb)
                pidb_next.append(ndc.oid)
                g_cost, sig_min, pidn = DFSr2(
                        G, ndc, ndc_sig, max_g_cost, pidb_next, sensors, wt)
                g_costs.append(g_cost)
                sig_list.append(sig_min)
                pidn_list.append(pidn)
    if g_costs:
        ind = np.argmin(g_costs)
        return g_costs[ind], sig_list[ind], pidn_list[ind]
    else:
        l_cost = mle.est_pathllr(sigb, sensors, wt, rd_wt)
        return l_cost+wp*(len(sensors)-sigb.N), sigb, pidb
    
def DFSr(G, nd, sigb, max_g_cost, pidb, sensors, wt):#Use G-cost to search over unvisited
    wp=5
    childs, child_sigs = get_order(G, nd, nd.lkb, cp.copy(sigb), sensors)
    exit_flag=False
    for (ndc, ndc_sig) in zip(childs, child_sigs):# Compute costs for all neighbors
        if exit_flag: #np.trace(ndc_sig.state_end.cov) <=max_g_cost:
            break
        if not ndc.visited:
            pidb_next = cp.copy(pidb)
            pidb_next.append(ndc.oid)
            g_cost, sig_min, pidn = DFSr(
                    G, ndc, ndc_sig, max_g_cost, pidb_next, sensors, wt)
            exit_flag = True
    if exit_flag:
        return g_cost, sig_min, pidn
    else:
        l_cost = mle.est_pathllr(sigb, sensors, wt, rd_wt)
        return l_cost+wp*(len(sensors)-sigb.N), sigb, pidb

def visit_selsigs(G, sel_sigs):# For Brute force method
    sig_final = sorted(sel_sigs, key=lambda x: x.llr )#mle.est_pathllr(x, sensors, wt)
    if 0:# Just pick min
        Nc = min([len(sig_final),max([len(Gs) for Gs in G])])
        sel_sigs = sig_final[0:Nc]
    else:# Mark Graph in ascending order
        sig_new=[]
        for sig in sig_final:
            if path_check(G, sig, sig.pid):
                sig_new.append(sig)
                for (si, pi) in zip(sig.sindx, sig.pid):
                    G[si][pi].visited = True
                    G[si][pi].used = sig
        sel_sigs = sig_new
    return sel_sigs

def get_minpaths(G, sensors, mode, cfgp):
    sel_sigs =[] # Note: wt includes the crb_min for range, doppler
    L3 = 0
    glen = [sum(len(g) for g in G)]
    dispatcher ={'DFS':DFS, 'Brute': Brute, 'Relax': Relax, 'Brute_iter': Brute_iter}
    if mode in ['DFS','Brute']:
        for i, sobs in enumerate(G):
            for pid, sobc in enumerate(sobs):
                if 1:#not sobc.visited:
                    sig_origin = ob.SignatureTracks(sobc.r, sobc.d, i, sobc.g)# create new signature
                    dispatcher[mode](G, sobc, sig_origin, sel_sigs, [pid], sensors, cfgp)
    if mode=='DFS':# Run once again
        for i, sobs in enumerate(G):
            for pid, sobc in enumerate(sobs):
                if 1:#not sobc.visited:
                    sig_origin = ob.SignatureTracks(sobc.r, sobc.d, i, sobc.g)# create new signature
                    dispatcher[mode](G, sobc, sig_origin, sel_sigs, [pid], sensors, cfgp)
        sig_new=[]
        for sig in sel_sigs:
            if sig!=None:
                sig_new.append(sig)
        sel_sigs= sig_new
    if mode=='Relax':#Run with relaxed params
        glen, L3 = dispatcher[mode](G, sel_sigs, sensors, glen, cfgp)
    if mode=='Brute_iter':#Run with relaxed params
        glen, L3 = dispatcher[mode](G, sel_sigs, sensors, glen, cfgp)

    if mode=='Brute':
        sel_sigs = visit_selsigs(G, sel_sigs)
        
    if not sel_sigs: # If no signature could be found, try finding any feasible path
        flag = False
        if False: # Don't try to find feasible paths, doing this will increasing pos-vel error
            for i, sobs in enumerate(G):
                for pid, sobc in enumerate(sobs): 
                    sig_rnd = ob.SignatureTracks(sobc.r, sobc.d, i, sobc.g)
                    if get_rndsig(G, sobc, sig_rnd, sel_sigs, [pid], sensors):
                        flag = True
                        break
                if flag:
                    break
        if not sel_sigs: # If no feasible target found, create fake signature at origin
            for sid, sensor in enumerate(sensors):
                if sid==0:
                    sig_rnd = ob.SignatureTracks(np.sqrt(sensor.x**2+0.01), 0, sid, 1)
                else:
                    sig_rnd.add_update3(np.sqrt(sensor.x**2+0.01), 0, 1, sid, sensors)
            sel_sigs.append(sig_rnd)
            print('No Feasible Targets Found (choosing (0,0.1)). ')
        else:
            print('No Targets Found (choosing random feasible path). ')
            
    return sel_sigs, glen, L3

def get_rndsig(G, nd, sig_rnd, sel_sigs, pid, sensors):
    minP=len(sensors)-1
    out = False
    if nd:
        if sig_rnd.N >= minP:
            l_cost, g_cost = mle.est_pathllr(sig_rnd, sensors, minP)#+wp*(len(sensors)-sig.N)    
            sig_rnd.llr = l_cost
            sig_rnd.pid = pid
            sel_sigs.append(sig_rnd)
            sel_sigs.append(sig_rnd)
            return True
        childs, child_sigs = get_order(G, nd, nd.lkf, cp.copy(sig_rnd), sensors)
        for (ndc, ndc_sig) in zip(childs, child_sigs):
            pnext = cp.copy(pid)
            pnext.append(ndc.oid)
            out = get_rndsig(G, ndc, ndc_sig, sel_sigs, pnext, sensors)
            if out:
                break
    return out
    
# ML estiamtion routines
import numpy as np
from GAutils import proc_est as pr
from GAutils import objects as ob
from scipy import special
from scipy.stats import chi2
from scipy.stats import norm
from GAutils import config as cfg
from GAutils import PCRLB as pcrlb

def create_llrmap(xrg, yrg, vxrg, vyrg, sensors, obs):
    # xrg : [min, max, #gridpoints]
    # obs: garda objects estimated at all sensors (same size)
    xlin = np.linspace(xrg[0],xrg[1], xrg[2])
    ylin = np.linspace(yrg[0],yrg[1], yrg[2])
    [xa, ya] = np.meshgrid(xlin, ylin, indexing ='ij')
    llr = np.zeros([xrg[2], yrg[2]],dtype='float64')
    for i in range(xrg[2]):
        for j in range(yrg[2]):
            template = ob.PointTarget(xa[i,j], ya[i,j], 0, 0)
            llr[i,j] = est_llr(template, sensors, obs, [1,0]) # estimate llr at template NOTE: Weight r,d (w[1]=0 since dopp unknown)
    return xa, ya, llr

def est_pathllr(sig, sensors, minP=[], rd_wt = cfg.rd_wt, modf=False): # Use range if dop. unknown
    # w : weights given to range, doppler errors
    # Compute likelihood of r,d in the path only (NOT all) excluding weakest link
    if sig.N <=2:
        return np.inf, 0.0
    llr = 0.0 
    pre=0.0
    pde=0.0
    
    if not minP: minP=sig.N
    
    if sig.N>minP: # Compute geometric cost ignoring weak node(Didn't work)
        ind_weak = np.argmax(abs(sig.gc))
        sid_weak = sig.sindx[ind_weak] # Sensor obs with mighest fitting error
        strong_id = list(range(sig.N))
        strong_id.remove(ind_weak)
        part_state, g_cost = sig.get_partialest(sensors, strong_id, abs(sum(sig.gc)), modf)# Updates sig if better path found
        if abs(g_cost)<abs(sum(sig.gc)): # ONly consider if removing node makes fitting better
            tpa = part_state.mean
        else:
            tpa = sig.state_end.mean
            sid_weak = -1 # Impossible value
            g_cost = sum(sig.gc)
         
    else:
        tpa = sig.state_end.mean
        sid_weak = -1 # Impossible value
        g_cost = sum(sig.gc)
    template = ob.PointTarget(tpa[0],tpa[1],tpa[2],tpa[3])
    for (rp, dp, gp, sid) in zip(sig.r, sig.d, sig.g, sig.sindx):
        if sid !=sid_weak:
            sensor = sensors[sid]
            crb = sensor.getCRB()/(abs(gp)**2)
            gard = pr.get_gard_true(sensor, template) #gard template
            dR = rp- gard.r # Array of est range delta
            dD = dp - gard.d
            # Using likelihood of r,d
            pre += dR**2/crb[0] #max(w[0],crb[0]) #norm.logpdf(dR,loc=0, scale=np.sqrt(crb[0][0]))
            pde += dD**2/crb[1] #max(w[1],crb[1]) #norm.logpdf(dD,loc=0, scale=np.sqrt(crb[1][1]))
    llr=rd_wt[0]*pre + rd_wt[1]*pde
    
    return llr, g_cost

def est_sensor_llr(sig, sensors, w=[1,1]):
    tpa = sig.state_end.mean
    template = ob.PointTarget(tpa[0],tpa[1],tpa[2],tpa[3])
    llra1=[]
    llra2=[]
    for (rp, dp, gp, sid) in zip(sig.r, sig.d, sig.g, sig.sindx):
        sensor = sensors[sid]
        crb = sensor.getCRB()/(abs(gp)**2)
        gard = pr.get_gard_true(sensor, template) #gard template
        dR = rp- gard.r # Array of est range delta
        dD = dp - gard.d
        # Using likelihood of r,d
        pre = dR**2/crb[0] #max(w[0],crb[0]) #norm.logpdf(dR,loc=0, scale=np.sqrt(crb[0][0]))
        pde = dD**2/crb[1] #max(w[1],crb[1]) #norm.logpdf(dD,loc=0, scale=np.sqrt(crb[1][1]))
        llra1.append(pre)
        llra2.append(pde)
    
    return np.vstack((llra1,llra2))

def est_llr(template, sensors, obs, w=[1,0]): # Use range if dop. unknown
    # w : weights given to range, doppler errors
    llr = 0.0
    agg= 0 # Aggregate over all estimates or not?
    for s, (sensor, gard_obs) in enumerate(zip(sensors, obs)):
        if not len(gard_obs.r): continue # Skip adding llr for this sensor
        Ni = sensor.mcs.Ni
        Nch = sensor.mcs.Nch
        Kr = sensor.mcs.Ts * sensor.mcs.ss * 4 * np.pi / 3e8
        Kd = Ni* sensor.mcs.Ts * sensor.mcs.fc * 4 * np.pi / 3e8
        gard = pr.get_gard_true(sensor, template) #gard template
        dR = gard_obs.r- gard.r # Array of est range delta
        dD = gard_obs.d - gard.d
        ga = gard_obs.g # Array of est gains
        if agg:
#           er = np.sum( ga * dirichlet(Ni, dR*Kr) - 1/2*(abs(ga)**2+1)) /(sensor.meas_std**2) # range error only
#           ed = np.sum( ga * dirichlet(Nch, dD*Kd) - 1/2*(abs(ga)**2+1))/(sensor.meas_std**2)# doppler error
        
            er = np.real(np.sum( np.abs(ga)**2 * dirichlet(Ni, dR*Kr) ) /(sensor.meas_std)) # range error only
            ed = np.real(np.sum( np.abs(ga)**2 * dirichlet(Nch, dD*Kd))/(sensor.meas_std))# doppler error
            erd = np.real(np.sum( np.abs(ga)**2 * dirichlet(Nch, dD*Kd) * dirichlet(Ni, dR*Kr))/(sensor.meas_std))# doppler error
            temp = w[0]*np.abs(er) + w[1]*np.abs(ed)
        else:
#            er = np.abs(( dirichlet(Ni, dR*Kr) )**2 /(sensor.meas_std**2)) # range error only
#            ed = np.abs(( dirichlet(Nch, dD*Kd))**2/(sensor.meas_std**2))# doppler error
            
            ind = np.argmin(dR**2 + dD**2) # Finds closest point
            er = np.abs( dirichlet(Ni, dR[ind]*Kr) )**2/(sensor.meas_std**2) # range error only
            ed = np.abs( dirichlet(Nch, dD[ind]*Kd))**2/(sensor.meas_std**2) # doppler error
            # Using closeset point & gain also!
#            er = np.abs( (ga[ind]) * dirichlet(Ni, dR[ind]*Kr) )**2/(sensor.meas_std**2) # range error only
#            ed = np.abs( (ga[ind]) * dirichlet(Nch, dD[ind]*Kd))**2/(sensor.meas_std**2) # doppler error
#            erd = np.real( np.abs(ga[ind])**2 * dirichlet(Nch, dD[ind]*Kd) * dirichlet(Ni, dR[ind]*Kr))/(sensor.meas_std) # doppler error
            temp = np.max(w[0]*np.abs(er) + w[1]*np.abs(ed))
        llr += temp # w[0]*np.abs(er) + w[1]*np.abs(ed) # sum abs value of correlations, WAS real
    return llr

def compute_llr_thres2(sensors, garda, rd_wt, N=1000):
    llr_joint = np.zeros(N)
    agg =0 # NOTE: Switch this
    for j, (sensor, gard) in enumerate(zip(sensors, garda)):
        Ni = sensor.mcs.Ni
        Nch = sensor.mcs.Nch
        Kr = sensor.mcs.Ts * sensor.mcs.ss * 4 * np.pi / 3e8
        Kd = Ni* sensor.mcs.Ts * sensor.mcs.fc * 4 * np.pi / 3e8
        ga = gard.g # Array of est gains
        dRa = np.random.randn(N) # range error samples, use variance of range
        dDa = np.random.randn(N) # NOTE: USe variance of doppler
        crb0=np.zeros(len(ga))
        crb1=np.zeros(len(ga))
        for i, gi in enumerate(ga):
            crb = crbrd(sensor, abs(gi))
            crb0[i]=5e-2
            crb1[i]=5e-2 #crb[1,1]
        if agg:
            if 0:
                for i, gi in enumerate(ga):
    #                llr_joint += (np.abs( gi * dirichlet(Ni, np.sqrt(crb0[i])*dRa[i]*Kr) * dirichlet(Nch, np.sqrt(crb1[i])*dDa[i]*Kd)) /(sensor.meas_std)) # range error only
                    llr_joint += (np.real( abs(gi)**2 * dirichlet(Ni, np.sqrt(crb0[i])*dRa[i]*Kr) )/(sensor.meas_std)) # range error only
            llr_joint += (np.real( min(abs(ga)**2) * dirichlet(Ni, np.sqrt(max(crb0))*dRa[0]*Kr) )/(sensor.meas_std)) # range error only
        else:
#            ind = np.argmin(abs(ga)) # Finds closest point
#            llr_r =np.abs( (ga[ind]) * dirichlet(Ni, np.sqrt(crb0[i])*dRa*Kr) )**2/(sensor.meas_std**2)
#            llr_d = np.abs( (ga[ind]) * dirichlet(Nch, np.sqrt(crb1[i])*dDa*Kd) )**2/(sensor.meas_std**2)
#            llr_joint += rd_wt[0]*llr_r + rd_wt[1]*llr_d
            llr_r = np.abs(( dirichlet(Ni, np.sqrt(crb0[i])*dRa*Kr) )**2 /(sensor.meas_std**2)) # range error only
            llr_d = np.abs(( dirichlet(Nch, np.sqrt(crb1[i])*dDa*Kd))**2/(sensor.meas_std**2))# doppler error
            llr_joint += (rd_wt[0]*llr_r + rd_wt[1]*llr_d)
    if cfg.debug_plots:# plot cdf of llr_joint and eyeball kappa for 0.95 
        import matplotlib.pyplot as plt
        #    import pickle as pl

        plt.figure(23)
            #    plt.rc('text', usetex=False)
            #    plt.rc('font', family='serif')
#        points = plt.hist(llr_joint, bins = 100, cumulative=True, density= True, histtype='step')
    p95 = np.percentile(llr_joint, 1)
    
#    plt.annotate(str(points[1][4]), xy=(points[1][4], points[0][4]),xytext=(points[1][4], points[0][4]+0.2), arrowprops=dict(facecolor='black', shrink=0.05))
#    plt.title('CDF of likelihood')
#    plt.xlabel('Likelihood, L($\theta$)');plt.ylabel('CDF')
#    # Save figure handle to disk
#    pl.dump(plt.figure(23),open("llr_cdf.pickle",'wb'))

    return p95 # LLR at cdf=0.05 i.e. 95% confidence of LLR's are above

def est_llr_joint(template, sensors, obs, w=[1,0]): # Use range if dop. unknown
    # w : weights given to range, doppler errors
    llr_joint = 0.0
    agg= 0 # Aggregate over all estimates or not?
    for s, (sensor, gard_obs) in enumerate(zip(sensors, obs)):
        Ni = sensor.mcs.Ni
        Nch = sensor.mcs.Nch
        Kr = sensor.mcs.Ts * sensor.mcs.ss * 4 * np.pi / 3e8
        Kd = Ni* sensor.mcs.Ts * sensor.mcs.fc * 4 * np.pi / 3e8
        gard = pr.get_gard_true(sensor, template) #gard template
        dR = gard_obs.r- gard.r # Array of est range delta
        dD = gard_obs.d- gard.d
        ga = gard_obs.g # Array of est gains
        if agg:
#           llr_joint += np.real(np.sum( ga * dirichlet(Ni, dR*Kr) * dirichlet(Nch, dD*Kd) - 1/2*(abs(ga)**2+1)))/(sensor.meas_std**2)
            llr_joint += np.real((np.sum( np.abs(ga)**2 * dirichlet(Ni, dR*Kr) * dirichlet(Nch, dD*Kd) ))/(sensor.meas_std))
        else:
            ind = np.argmin(abs(dR)) # Finds closest point
            llr_joint += np.real(( np.abs(ga[ind])**2 * dirichlet(Ni, dR[ind]*Kr) * dirichlet(Nch, dD[ind]*Kd) )/(sensor.meas_std))
    return llr_joint

def dirichlet(N, d):# Normalized correkation. N scalar, d:array
    return special.diric(d, N-1)* np.exp(1j*d*(N-1)/2) # * np.exp(1j*d*(N-1)/2) 
#        return np.sin((N-1)/2*d) / np.sin(1/2*d) * np.exp(1j*d*(N-1)/2) / N

def create_llrmap_doppler(xrg, yrg, vxrg, vyrg, sensors, obs, trgt, rd_wt):
    # vxrg : [min, max, #gridpoints]
    # obs: garda objects estimated at all sensors (same size)
    # scene: Also needs true positions to evaluate doppler
    vxlin = np.linspace(vxrg[0],vxrg[1], vxrg[2])
    vylin = np.linspace(vyrg[0],vyrg[1], vyrg[2])
    [vxa, vya] = np.meshgrid(vxlin, vylin, indexing ='ij')
    llr = np.zeros([vxrg[2], vyrg[2]])
    for i in range(vxrg[2]):
        for j in range(vyrg[2]):
            template = ob.PointTarget(trgt.x, trgt.y, vxa[i,j], vya[i,j])
            llr[i,j] += est_llr(template, sensors, obs, [1,1]) # estimate llr at template NOTE: Weight r,d (w[1]=0 since dopp unknown)
    return vxa, vya, llr

def create_llrmap_rd(xrg, yrg, vxrg, vyrg, sensors, obs):
    xlin = np.linspace(xrg[0],xrg[1], xrg[2])
    ylin = np.linspace(yrg[0],yrg[1], yrg[2])
    [xa, ya] = np.meshgrid(xlin, ylin, indexing ='ij')
    vxlin = np.linspace(vxrg[0],vxrg[1], vxrg[2])
    vylin = np.linspace(vyrg[0],vyrg[1], vyrg[2])
    [vxa, vya] = np.meshgrid(vxlin, vylin, indexing ='ij')
#    llr_p = np.zeros([xrg[2], yrg[2]])
#    llr_v = np.zeros([vxrg[2], vyrg[2]])
    llr = np.zeros([xrg[2], yrg[2],vxrg[2], vyrg[2]])
    for i in range(xrg[2]):
        for j in range(yrg[2]):
#            template = ob.PointTarget(xa[i,j], ya[i,j], 0, 0)
#            llr_p[i,j] = est_llr(template, sensors, obs, [1,0])
            for k in range(vxrg[2]):
                for l in range(vyrg[2]):
                    template = ob.PointTarget(xa[i,j], ya[i,j], vxa[k,l], vya[k,l])
                    llr[i,j,k,l] += est_llr_joint(template, sensors, obs, [0,1]) # estimate llr at template NOTE: Weight r,d (w[1]=0 since dopp unknown)
#            llr[i,j,:,:] = llr_p[i,j]+llr_v
    return xa, ya, vxa, vya, llr

def compute_llr_thres(sensors, rd_wt, Nmin=2, pfa = 1e-3):
    #Nmin: Number of sensors being associated 
#    for (gard, sensor) in zip(garda, sensors):
#        llr_var += np.sqrt(np.sum([(abs(gard.g)*sensor.meas_std)**2 ]))
    var= (sensors[0].meas_std)**2 # TODO: This assumes equal sensor noise levels
#    out = - np.log(1-(1-pfa)**(1/Nmin)) 
    out = chi2.ppf(pfa, len(sensors), loc=0, scale= sensors[0].meas_std)# TODO: This assumes equal sensor noise levels
    return out*np.sum(rd_wt)

def compute_llr_thres3(pos, ga, sa, sensors, rd_wt=[1,0], N=1000, pfa = 1e-3):
    llr_joint = np.zeros(N)
    dRa = np.random.randn(len(ga),N) # range error samples, variance of range added later
    dDa = np.random.randn(len(ga),N) # variance of doppler added later
    crb0=np.zeros(len(ga))
    crb1=np.zeros(len(ga))
    for i, (gi, si) in enumerate(zip(ga, sa)):
        sensor = sensors[si]
        Ni = sensor.mcs.Ni
        Nch = sensor.mcs.Nch
        Kr = sensor.mcs.Ts * sensor.mcs.ss * 4 * np.pi / 3e8
        Kd = Ni* sensor.mcs.Ts * sensor.mcs.fc * 4 * np.pi / 3e8
        crb = crbrd(sensor, abs(gi))
        crb0[i]=1e-2 # crb[0,0]
        crb1[i]=1e-3 # crb[1,1]
#        llr_rd = np.abs(( (gi) * dirichlet(Ni, np.sqrt(crb0[i])*dRa[i]*Kr) * dirichlet(Nch, np.sqrt(crb1[i])*dDa[i]*Kd)) /(sensor.meas_std)) # range, doppler error
        llr_r = np.abs( (gi) * dirichlet(Ni, np.sqrt(crb0[i])*dRa[i]*Kr) )**2/(sensor.meas_std) # range error only
        llr_d = np.abs( (gi) * dirichlet(Nch, np.sqrt(crb1[i])*dDa[i]*Kd))**2 /(sensor.meas_std) # range, doppler error
        llr_joint += rd_wt[0]*llr_r + rd_wt[1]*llr_d # range error only

    p95 = np.percentile(llr_joint, 5)
#    print(p95)
    if cfg.debug_plots:# plot cdf of llr_joint and eyeball kappa for 0.95 
        import matplotlib.pyplot as plt    
        plt.figure(24)
        plt.quiver(pos.x,pos.y,pos.vx,pos.vy, color='r', label=str(p95))
        plt.text(pos.x,pos.y, int(p95), fontsize=7)
#        points = plt.hist(llr_joint, bins = 100, cumulative=True, density= True, histtype='step')
#    plt.annotate(str(points[1][4]), xy=(points[1][4], points[0][4]),xytext=(points[1][4], points[0][4]+0.2), arrowprops=dict(facecolor='black', shrink=0.05))
#    plt.title('CDF of likelihood')
#    plt.xlabel('Likelihood, L($\theta$)');plt.ylabel('CDF')
#    # Save figure handle to disk
#    pl.dump(plt.figure(23),open("llr_cdf.pickle",'wb'))
    return compute_llr_thres(sensors, rd_wt, 2, 1e-3) #p95 # LLR at cdf=0.05 i.e. 95% confidence of LLR's are above

def crbrd(sensor, alpha=1):
    mcs = sensor.mcs
#    tfa0 = mcs.get_tfa()
#    tna = (np.outer(np.ones([tfa0.shape[0],1]),tfa0[0])).flatten() - mcs.Ts * mcs.Ni/2
#    tfa = tfa0.flatten() - mcs.tf/2
    Ni = mcs.Ni
    Nch = mcs.Nch
    Kr = mcs.Ts * mcs.ss * 4 * np.pi / mcs.c
    Kd = Ni* mcs.Ts * mcs.fc * 4 * np.pi / mcs.c
    FIM = np.array([ [(Kr**2)*Nch*(Ni/6 * (2 * Ni**2 + 1)), 0],
            [0, (Kd**2)*Ni*(Nch/6*(2 * Nch**2 + 1))] ])
#    print(FIM)
    FIM = FIM * 2 * (alpha/sensor.meas_std)**2
    try:
        out = np.linalg.inv(FIM)
    except:
        out = np.diag(1/np.diag(FIM))
    return out
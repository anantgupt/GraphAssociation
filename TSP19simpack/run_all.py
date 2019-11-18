import os, subprocess

# # subprocess.call(['python', 'script_all1.py', '--mode', 'Relax','--N_avg','50'])
# subprocess.call(['python', 'script_all2.py', '--mode', 'mle','--N_avg','50'])

# # subprocess.call(['python', 'script_all1.py', '--mode', 'Relax','--N_avg','50','--sep_th','1'])
# subprocess.call(['python', 'script_all2.py', '--mode', 'mle','--N_avg','50','--sep_th','1'])

subprocess.call(['python', 'script_all3.py', '--mode', 'Relax','--N_avg','40','--sep_th','1','--pmiss','0'])
subprocess.call(['python', 'script_all3.py', '--mode', 'mle','--N_avg','40','--sep_th','1','--pmiss','0'])


# subprocess.call(['python', 'script_all1.py', '--mode', 'SPEKF','--N_avg','50'])
# subprocess.call(['python', 'script_all1.py', '--mode', 'SPEKF-heap','--N_avg','50'])

# subprocess.call(['python', 'script_all1.py', '--mode', 'mcf_all','--N_avg','50'])
# subprocess.call(['python', 'script_all1.py', '--mode', 'mcf','--N_avg','50'])

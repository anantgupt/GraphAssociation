from IPython import get_ipython

if __name__ == "__main__":
    __spec__ = None
    ipython = get_ipython()
    ipython.magic('%load_ext autoreload')
    ipython.magic('%autoreload 2')    
    ipython.magic('%run script_all.py ')
    ipython.magic('%run script_all1.py ')
    ipython.magic('%run script_all2.py ')
    ipython.magic('%run script_all3.py ')
    ipython.magic('%run script_all4.py ')

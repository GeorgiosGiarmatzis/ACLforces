# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 14:28:44 2019

@author: Giorgos Giarmatzis
"""

#from IPython import get_ipython
#get_ipython().magic('reset -sf')
import opensim
#os.chdir('C:\Users\user\Documents\GitHub\ACLforces')
#cwd = os.getcwd()

def lock(model_app,coordinate,LockType):
    model = opensim.Model(model_app)
    dof = model.getCoordinateSet().get(coordinate)
    dof.setDefaultLocked(LockType)
#    ml = model_app.strip('.osim')+ '_unlocked.osim'
    model.printToXML(model_app)
    
    return model_app
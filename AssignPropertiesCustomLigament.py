# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 13:33:02 2019

@author: Giorgos Giarmatzis
"""

# After scaling the model with class Ligament, we update it with the properties
# from the CustomLigament, and rename it 

import os
from xml.dom.minidom import parse

def change_properies(osimfile,swingModel):

    TL = ['aACL_R','pACL_R','aPCL_R','pPCL_R','aMCL_R','iMCL_R','pMCL_R','dMCL_R',\
    'eMCL_R','aLCL_R','aACL_L','pACL_L','aPCL_L','pPCL_L','aMCL_L','iMCL_L',\
    'pMCL_L','dMCL_L','eMCL_L','aLCL_L',]
    
       ###############################################################################
    for i in range(len(TL)):
        if i==0:
            model_Lig = parse(osimfile) #load this model only the first time
        else:
            model_Lig = parse(osimfile.strip('.osim')+'_append.osim')
            
        Lig = model_Lig.getElementsByTagName('Ligament')[0]
        Lig_name = Lig.attributes['name'].value
        if Lig_name != TL[i]:
           raise RuntimeError('something is wrong with '+TL[i])
        damping = model_Lig.createElement('damping')
        stiffness = model_Lig.createElement('stiffness')
        el = model_Lig.createElement('el')
        
        # Load the swing.osim model and the rest of the CustomLigament properties
        
        model_swing = parse(swingModel)
        CLig = model_swing.getElementsByTagName('CustomLigament')[i]
        CLig_name = Lig.attributes['name'].value
        if CLig_name != TL[i]:
           raise RuntimeError('something is wrong with '+TL[i]+' in the second loop')
        damp =  (CLig.getElementsByTagName('damping')[0].childNodes[0].nodeValue)
        stiff =  (CLig.getElementsByTagName('stiffness')[0].childNodes[0].nodeValue)
        cel = (CLig.getElementsByTagName('el')[0].childNodes[0].nodeValue)
        
        # Add the damping, stiffness and el properties to the scaled model
        
        damping.appendChild(model_Lig.createTextNode(damp))
        stiffness.appendChild(model_Lig.createTextNode(stiff))
        el.appendChild(model_Lig.createTextNode(cel))
        
        Lig.appendChild(damping)
        Lig.appendChild(stiffness)
        Lig.appendChild(el)
        
        # Change the name of the Ligament to CustomLigament
        
        Lig.tagName = 'CustomLigament'
            
        ## save the xml file
            
        F= open(osimfile.strip('.osim')+'_append.osim',"w")
        model_Lig.writexml(F)
        F.close()
        
    model_app = os.path.basename(osimfile).strip('.osim')+'_append.osim'

    return model_app

# ----------------------------------------------------------------------- #
# The OpenSim API is a toolkit for musculoskeletal modeling and           #
# simulation. See http://opensim.stanford.edu and the NOTICE file         #
# for more information. OpenSim is developed at Stanford University       #
# and supported by the US National Institutes of Health (U54 GM072970,    #
# R24 HD065690) and by DARPA through the Warrior Web program.             #
#                                                                         #   
# Copyright (c) 2005-2012 Stanford University and the Authors             #
#                                                                         #   
# Licensed under the Apache License, Version 2.0 (the "License");         #
# you may not use this file except in compliance with the License.        #
# You may obtain a copy of the License at                                 #
# http://www.apache.org/licenses/LICENSE-2.0.                             #
#                                                                         # 
# Unless required by applicable law or agreed to in writing, software     #
# distributed under the License is distributed on an "AS IS" BASIS,       #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or         #
# implied. See the License for the specific language governing            #
# permissions and limitations under the License.                          #
# ----------------------------------------------------------------------- #

# This example increases the maxIsometricForce of all the muscles in the currently loaded model.
# A pop-up dialog displays a confirmation with the name of the new model.

# Get handle to current model in GUI


import opensim

def strengthen(osimfile,scalefactor):
    oldModel = opensim.Model(osimfile)
   
    # Create a fresh copy
    newModel = opensim.Model(oldModel)
    
    # Initialize the copy
    newModel.initSystem()
    
    # Name the copy for later showing in GUI
    oldName = oldModel.getName()
    newModel.setName(oldName+str(scalefactor))
    
        
    # Apply scale factor to MaxIsometricForce
    for i in range(newModel.getMuscles().getSize()):
    	currentMuscle = newModel.getMuscles().get(i)
    	currentMuscle.setMaxIsometricForce(currentMuscle.getMaxIsometricForce()*scalefactor)
    
    # Save resulting model
    fullName = oldModel.getInputFileName()
    newName = fullName.strip('Ligament.osim')+str(scalefactor)+'.osim'
    newModel.printToXML(newName)
    
    return newName






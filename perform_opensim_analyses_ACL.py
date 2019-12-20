# This script automates the execution of Inverse Kinematics, Static Optimization
# and Joint Reaction Analysis. Instead of using the OpenSim GUI one can provide
# the required files and generate the files needed for the analysis.
#
# @author Dimitar Stanev (jimstanev@gmail.com)
#
# Tested with OpenSim 3.3
#from IPython import get_ipython
#get_ipython().magic('reset -sf')
import os
from opensim_utils_g import perform_ik, perform_so, perform_jra, plot_sto
import pandas as pd

#from tkinter.filedialog import askdirectory
###############################################################################
# parameters
#path=askdirectory()
#subject_dir = path
def Opensim_Analysis(name,model_file): 
    for i in range(1,2):
        events_file = pd.read_excel(name+'_HDR_'+str(i)+'_Events.xls')
        trc_file = '\HDR_'+str(i)+'\HDR_'+str(i)+'.trc'
        grf_file = '\HDR_'+str(i)+'_GRF.mot'
        grf_xml_file = '\HDR_'+str(i)+'_ExternalLoads.xml'
        reserve_actuators_file = 'Actuators.xml'
        results_dir = 'Results'
        settings_dir = 'Settings'
        opensimtools_dir = 'C:\Opensim3.3\\bin'
        opensimplugin_dir = 'C:\Opensim3.3\plugins'
        
        if not (os.path.isfile(model_file) and
                os.path.isfile(trc_file) and
                os.path.isfile(grf_file) and
                os.path.isfile(grf_xml_file) and
                os.path.isfile(reserve_actuators_file)):
            raise RuntimeError('required files do not exist')
        
        ## Create the necessary directories
        dir1 = os.path.join(results_dir)
        dir2 = os.path.join(settings_dir)
        dir_list = [dir1, dir2]
        
        for _file in dir_list:
                if not os.path.exists(_file):
                    os.mkdir(_file)
        
        
        
        ###############################################################################
        # main
        
        # perform OpenSim inverse kinematics
        ik_file = perform_ik(model_file, trc_file, results_dir,settings_dir,opensimtools_dir,opensimplugin_dir)
    #    plot_sto(ik_file, 3, os.path.join(results_dir, ik_file[0:-4] + '.pdf'))
        
        # perform OpenSim static optimization
        (so_force_file, so_activation_file) = perform_so(dl,events_file,model_file, ik_file, grf_file,
                                                         grf_xml_file,
                                                         reserve_actuators_file,
                                                         results_dir,opensimtools_dir,opensimplugin_dir,settings_dir)
        plot_sto(so_force_file, 3, os.path.join(
            results_dir, so_force_file[0:-4] + '.pdf'))
        plot_sto(so_activation_file, 3, os.path.join(
            results_dir, so_activation_file[0:-4] + '.pdf'))
        
        # perform OpenSim joint reaction analysis
        jra_file = perform_jra(model_file, ik_file, grf_file, grf_xml_file,
                               reserve_actuators_file, so_force_file, results_dir, '',
                               ['All'],
                               ['child'],
                               ['child'])
        plot_sto(jra_file, 3, os.path.join(results_dir, jra_file[0:-4] + '.pdf'),
                 None,
                 lambda x: x.replace('_on_', '\n').replace('_in_', '\n'))
        return
# \brief A variety of useful OpenSim utilities.
#
# @author Dimitar Stanev (stanev@ece.upatras.gr)
import os
import opensim
import numpy as np
import matplotlib    #This line is added because there was a problem with loading tkinter module
matplotlib.use('Agg')#I found this suggestion on line and it worked! (GGiarmatzis)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from xml.dom.minidom import parse
opensimtools_dir = 'C:\Opensim3.3\\bin'
opensimplugin_dir = 'C:\Opensim3.3\plugins'

def readMotionFile(filename):
    """Reads OpenSim .sto files.

    Parameters
    ----------
    filename: str
        absolute path to the .sto file

    Returns
    -------
    header: list of str
        the header of the .sto
    labels: list of str
        the labels of the columns
    data: list of lists
        an array of the data

    """

    if not os.path.exists(filename):
        print('file do not exists')

    file_id = open(filename, 'r')

    # read header
    next_line = file_id.readline()
    header = [next_line]
    nc = 0
    nr = 0
    while 'endheader' not in next_line:
        if 'datacolumns' in next_line:
            nc = int(next_line[next_line.index(' ') + 1:len(next_line)])
        elif 'datarows' in next_line:
            nr = int(next_line[next_line.index(' ') + 1:len(next_line)])
        elif 'nColumns' in next_line:
            nc = int(next_line[next_line.index('=') + 1:len(next_line)])
        elif 'nRows' in next_line:
            nr = int(next_line[next_line.index('=') + 1:len(next_line)])

        next_line = file_id.readline()
        header.append(next_line)

    # process column labels
    next_line = file_id.readline()
    if next_line.isspace() is True:
        next_line = file_id.readline()

    labels = next_line.split()

    # get data
    data = []
    for i in range(1, nr + 1):
        d = [float(x) for x in file_id.readline().split()]
        data.append(d)

    file_id.close()

    return header, labels, data


def index_containing_substring(list_str, pattern):
    """For a given list of strings finds the index of the element that contains the
    substring.

    Parameters
    ----------
    list_str: list of str

    pattern: str
         pattern


    Returns
    -------
    indices: list of int
         the indices where the pattern matches

    """
    indices = []
    for i, s in enumerate(list_str):
        if pattern in s:
            indices.append(i)

    return indices


def plot_sto(sto_file, plots_per_row, plot_file, pattern=None,
             title_function=lambda x: x):
    """Plots the .sto file (OpenSim) by constructing a grid of subplots.

    Parameters
    ----------
    sto_file: str
        path to file
    plots_per_row: int
        subplot columns
    plot_file: str
        path to store results
    pattern: str, optional, default=None
        plot based on pattern (e.g. only pelvis coordinates)
    title_function: lambda
        callable function f(str) -> str
    """
    assert('pdf' in plot_file)

    header, labels, data = readMotionFile(sto_file)
    data = np.array(data)
    indices = []
    if pattern is not None:
        indices = index_containing_substring(labels, pattern)
    else:
        indices = range(1, len(labels))

    n = len(indices)
    ncols = int(plots_per_row)
    nrows = int(np.ceil(float(n) / plots_per_row))
    pages = int(np.ceil(float(nrows) / ncols))
    if ncols > n:
        ncols = n

    with PdfPages(plot_file) as pdf:
        for page in range(0, pages):
            fig, ax = plt.subplots(nrows=ncols, ncols=ncols,
                                   figsize=(8, 8))
            ax = ax.flatten()
            for pl, col in enumerate(indices[page * ncols ** 2:page * ncols ** 2 + ncols ** 2]):
                ax[pl].plot(data[:, 0], data[:, col])
                ax[pl].set_title(title_function(labels[col]))

            fig.tight_layout()
            pdf.savefig(fig)
            plt.close()


def construct_ik_task_set(model, marker_data, task_set):
    """Construct OpenSim Inverse Kinematics task set.

    In older versions of OpenSim (e.g. 3.3) IK will not execute when there are
    virtual markers that do not exist in the marker data.

    """
    virtual_markers = model.getMarkerSet()
    marker_names = marker_data.getMarkerNames()
    for i in range(0, marker_names.getSize()):
        marker_name = marker_names.get(i)
        exists = False
        for j in range(0, virtual_markers.getSize()):
            if virtual_markers.get(j).getName() == marker_name:
                task = opensim.IKMarkerTask()
                task.setName(marker_name)
                task.setApply(True)
                task.setWeight(1)
                task_set.adoptAndAppend(task)
                exists = True
                break

        if not exists:
            task = opensim.IKMarkerTask()
            task.setName(marker_name)
            task.setApply(False)
            task.setWeight(1)
            task_set.adoptAndAppend(task)


def perform_ik(model_file, trc_file, results_dir,settings_dir,opensimtools_dir,opensimplugin_dir):
    """Performs Inverse Kinematics using OpenSim.

    Parameters
    ----------
    model_file: str
        OpenSim model (.osim)
    trc_file: str
        the experimentally measured marker trajectories (.trc)
    results_dir: str
        directory to store the results

    """
    model = opensim.Model(model_file)
    # model.set_assembly_accuracy(1e-3)
    
    #model.initSystem()
    marker_data = opensim.MarkerData(trc_file)
    trial = os.path.basename(trc_file)[:-4]
    ik_tool = opensim.InverseKinematicsTool()
    task_set = ik_tool.getIKTaskSet()
    construct_ik_task_set(model, marker_data, task_set)
    ik_tool.setName(trial)
    ik_tool.setModel(model)
    ik_tool.setStartTime(marker_data.getStartFrameTime())
    ik_tool.setEndTime(marker_data.getLastFrameTime())
    ik_tool.setMarkerDataFileName(trc_file)
    ik_tool.setResultsDir(results_dir)
    ik_file = results_dir + trial + '_IK.mot'
    ik_xml = settings_dir + trial+'_Setup_IK.xml'
    ik_tool.setOutputMotionFileName(ik_file)
    ik_tool.printToXML(ik_xml)
    
    ##parsing the previously created setup file and change the model_file item
    ik_set_file = parse(ik_xml)
    ik_set_file.getElementsByTagName("model_file")[0].childNodes[0].nodeValue = model_file

    ## save the xml file
    F= open(ik_xml,"w")
    ik_set_file.writexml(F)
    F.close()
    
    # run the IK tool through cmd
    
    ik_cmd = opensimtools_dir + '\ik -S ' + ik_xml
    print(os.system(ik_cmd))    
    return ik_file


def perform_id(events_file,model_file, ik_file, grf_file,
    grf_xml_file,results_dir,opensimtools_dir,opensimplugin_dir,settings_dir):  
    """Performs Inverse dynamics using Opensim."""
    
     # model
    
    model = opensim.Model(model_file)
    
    trial = os.path.basename(grf_file).strip('_GRF.mot')
#    external_loads = opensim.ExternalLoads(model, grf_xml_file)
#    external_loads.setExternalLoadsModelKinematicsFileName(ik_file)
#    external_loads.setDataFileName(grf_file)
#    external_loads.setLowpassCutoffFrequencyForLoadKinematics(6)
#    external_loads.printToXML(settings_dir + name + 'ExternalLoads.xml')
    
    # create the setuo file
    model.initSystem()
    id_tool = opensim.InverseDynamicsTool()
    id_tool.setName(trial)
    id_tool.setModel(model)
    id_tool.setExternalLoadsFileName(grf_xml_file)
    id_tool.setResultsDir(results_dir)
    id_tool.setStartTime(events_file.InitialContactTime.iloc[0])
    id_tool.setEndTime(events_file.TimeLowestCOMX.iloc[1])
    id_tool.setCoordinatesFileName(ik_file)
    id_tool.setOutputGenForceFileName(trial+ '_ID.sto')
    id_tool.setLowpassCutoffFrequency(6)
    id_xml = settings_dir+trial+'_Setup_ID.xml'
    id_tool.printToXML(id_xml)
    id_tool.run()
    id_file = results_dir+trial+ '_ID.sto' 
    return id_file
    
     ## parsing the generic setup file and change accordingly 
    
#    subj_dir = os.path.dirname(model_file)
#    data_dir = os.path.dirname(subj_dir)
#    id_set_file = parse(data_dir+'/ID_Setup.xml')
#    id_set_file.getElementsByTagName('results_directory')[0].childNodes[0].nodeValue = results_dir
#    id_set_file.getElementsByTagName('model_file')[0].childNodes[0].nodeValue = model_file
#    id_set_file.getElementsByTagName('external_loads_file')[0].childNodes[0].nodeValue\
#    = settings_dir + name + 'ExternalLoads.xml'
#    id_set_file.getElementsByTagName('coordinates_file')[0].childNodes[0].nodeValue = ik_file
#    id_set_file.getElementsByTagName('output_gen_force_file')[0].childNodes[0].nodeValue = results_dir+name+ '_ID.mot'
#    id_set_file.getElementsByTagName('time_range')[0].childNodes[0].nodeValue = ik_file
    
    


def perform_so(events_file,model_file, ik_file, grf_file, grf_xml, 
               results_dir,opensimtools_dir,opensimplugin_dir,settings_dir):
    """Performs Static Optimization using OpenSim.

    Parameters
    ----------
    model_file: str
        OpenSim model (.osim)
    ik_file: str
        kinematics calculated from Inverse Kinematics
    grf_file: str
        the ground reaction forces
    grf_xml: str
        xml description containing how to apply the GRF forces
    reserve_actuators: str
        path to the reserve actuator .xml file
    results_dir: str
        directory to store the results
    """
    # model
    model = opensim.Model(model_file)
    
    # prepare external forces xml file
    trial = os.path.basename(grf_file).strip('_GRF.mot')
#    external_loads = opensim.ExternalLoads(model, grf_xml)
#    external_loads.setExternalLoadsModelKinematicsFileName(ik_file)
#    external_loads.setDataFileName(grf_file)
#    external_loads.setLowpassCutoffFrequencyForLoadKinematics(6)
#    external_loads.printToXML(settings_dir + trial + 'ExternalLoads.xml')
    
    """ Create the Actuators file"""
    subj_dir = os.path.dirname(model_file)
    data_dir = os.path.dirname(subj_dir)
    name = os.path.basename(model_file).strip('.osim')
    actuators_file = parse(data_dir+'\Actuators.xml')
    
    """Get the mass center of the pelvis"""
    model=parse(model_file)
    massCenter = model.getElementsByTagName('BodySet')[0].getElementsByTagName('objects')[0].\
    getElementsByTagName('Body')[1].getElementsByTagName('mass_center')[0]\
    .childNodes[0].nodeValue
    
    """Assign the mass center from the model to the Actuators file and save"""
    for i in range(0,3):    
        actuators_file.getElementsByTagName('ForceSet')[0].getElementsByTagName('objects')[0].\
        getElementsByTagName('PointActuator')[i].getElementsByTagName('point')[0].childNodes[0].nodeValue = massCenter
    
    F= open(settings_dir + 'Actuators.xml',"w")
    actuators_file.writexml(F)
    F.close()

    ## parsing the generic setup file and change accordingly
    
    trial = os.path.basename(grf_file).strip('_GRF.mot')
    so_set_file = parse(data_dir+'/SO.xml')
    so_set_file.getElementsByTagName('AnalyzeTool')[0].attributes['name'].value = name+'_'+trial
    so_set_file.getElementsByTagName('model_file')[0].childNodes[0].nodeValue = model_file
    so_set_file.getElementsByTagName('force_set_files')[0].childNodes[0].nodeValue = settings_dir + 'Actuators.xml'
    so_set_file.getElementsByTagName('results_directory')[0].childNodes[0].nodeValue = results_dir
    #motion = opensim.Storage(ik_file)
#    initial_time = motion.getFirstTime()
    #final_time = motion.getLastTime()
    so_set_file.getElementsByTagName('initial_time')[0].childNodes[0].nodeValue = events_file.InitialContactTime.iloc[0]
    so_set_file.getElementsByTagName('final_time')[0].childNodes[0].nodeValue = events_file.TimeLowestCOMX.iloc[1]
    so_set_file.getElementsByTagName('AnalysisSet')[0].getElementsByTagName('objects')[0].\
    getElementsByTagName('StaticOptimization')[0].getElementsByTagName('start_time')[0].\
    childNodes[0].nodeValue = events_file.InitialContactTime.iloc[0]
    so_set_file.getElementsByTagName('AnalysisSet')[0].getElementsByTagName('objects')[0].\
    getElementsByTagName('StaticOptimization')[0].getElementsByTagName('end_time')[0].childNodes[0].nodeValue = events_file.TimeLowestCOMX.iloc[1]
    so_set_file.getElementsByTagName('external_loads_file')[0].childNodes[0].nodeValue\
    = grf_xml
    so_set_file.getElementsByTagName('coordinates_file')[0].childNodes[0].nodeValue = ik_file
    
    ## save the xml file
    so_xml = settings_dir + name + '_'+trial + '_Setup_SO.xml'
    F= open(so_xml,"w")
    so_set_file.writexml(F)
    F.close()
    
    so_force_file = results_dir + name + '_'+trial + '_StaticOptimization_force.sto'
    so_activations_file = results_dir +name +'_'+ trial + \
        '_StaticOptimization_activation.sto'
    
    #run the so tool through system cmd
    so_cmd = opensimtools_dir + '\\analyze -S ' + so_xml+' -L ' \
     + opensimplugin_dir + '\CustomLigament.dll'
    print(os.system(so_cmd))
    
    return (so_force_file, so_activations_file)


def perform_jra(model_file, ik_file, grf_file, grf_xml, reserve_actuators,
                muscle_forces_file, results_dir, prefix,
                joint_names,
                apply_on_bodies,
                express_in_frame):
    """Performs Static Optimization using OpenSim.

    Parameters
    ----------
    model_file: str
        OpenSim model (.osim)
    ik_file: str
        kinematics calculated from Inverse Kinematics
    grf_file: str
        the ground reaction forces
    grf_xml: str
        xml description containing how to apply the GRF forces
    reserve_actuators: str
        path to the reserve actuator .xml file
    muscle_forces_file: str
        path to the file containing the muscle forces from SO
    results_dir: str
        directory to store the results
    prefix: str
        prefix of the resultant joint reaction loads
    joint_names: list
        joint names of interest
    apply_on_bodies: list
        apply on child or parent
    express_in_frame: list
        frame to express results
    """
    assert(len(joint_names) == len(apply_on_bodies) == len(express_in_frame))

    # model
    model = opensim.Model(model_file)

    # prepare external forces xml file
    name = os.path.basename(grf_file)[:-8]
#    external_loads = opensim.ExternalLoads(model, grf_xml)
#    external_loads.setExternalLoadsModelKinematicsFileName(ik_file)
#    external_loads.setDataFileName(grf_file)
#    external_loads.setLowpassCutoffFrequencyForLoadKinematics(6)
#    external_loads.printToXML(results_dir + name + '.xml')

   
    # construct joint reaction analysis
    motion = opensim.Storage(ik_file)
    joint_reaction = opensim.JointReaction(model)
    joint_reaction.setName('JointReaction')
    joint_reaction.setStartTime(motion.getFirstTime())
    joint_reaction.setEndTime(motion.getLastTime())
    joint_reaction.setForcesFileName(muscle_forces_file)
    joint_names_arr = opensim.ArrayStr()
    apply_on_bodies_arr = opensim.ArrayStr()
    express_in_frame_arr = opensim.ArrayStr()
    for j, b, f in zip(joint_names, apply_on_bodies, express_in_frame):
        joint_names_arr.append(j)
        print(j)
        apply_on_bodies_arr.append(b)
        express_in_frame_arr.append(f)

    joint_reaction.setJointNames(joint_names_arr)
    joint_reaction.setOnBody(apply_on_bodies_arr)
    joint_reaction.setInFrame(express_in_frame_arr)
    model.addAnalysis(joint_reaction)
    model.initSystem()

    # analysis
    analysis = opensim.AnalyzeTool(model)
    analysis.setName(prefix + name)
    analysis.setModel(model)
    analysis.setModelFilename(model_file)
    analysis.setInitialTime(motion.getFirstTime())
    analysis.setFinalTime(motion.getLastTime())
    analysis.setLowpassCutoffFrequency(6)
    analysis.setCoordinatesFileName(ik_file)
    analysis.setExternalLoadsFileName(results_dir + name + '.xml')
    analysis.setLoadModelAndInput(True)
    analysis.setResultsDir(results_dir)
    analysis.run()
    jra_file = results_dir + name + '_JointReaction_ReactionLoads.sto'
    return jra_file

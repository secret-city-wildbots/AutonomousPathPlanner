# Date: 2020-06-09
# Description: a path planner for FRC 2020
#-----------------------------------------------------------------------------

# Versioning information
versionNumber = '0.0.1' # breaking.major-feature-add.minor-feature-or-bug-fix
versionType = 'release' # options are "beta" or "release"
print('Loading v%s...' %(versionNumber))

# Ignore future and depreciation warnings when not in development
import warnings 
if(versionType=='release'):
    warnings.simplefilter(action='ignore', category=FutureWarning)
    warnings.simplefilter(action='ignore', category=DeprecationWarning)
    warnings.filterwarnings('ignore', category=UserWarning)
    
# Hardcoded directory paths
dirPvars = '../vars/' # persistent variables directory
    
# Check the specified operating system
import numpy as np # Numpy toolbox
try: ostype = str(np.load(dirPvars+'ostype.npy'))
except: ostype = None
    
# Get system configuration  
import os # operating system interactions
cpus = os.cpu_count() # number of logical cores
import psutil # needed to query system memory
ram = int(psutil.virtual_memory().free//1e9)
from win32api import GetSystemMetrics # system configuration and details
scrnW = GetSystemMetrics(0) # [pixels] width of the computer monitor
scrnH = GetSystemMetrics(1) # [pixels] height of the computer monitor

# Report system configuration
print('\nOperating System: %s' %(ostype))
print('Monitor resolution: %ip x %ip' %(scrnW,scrnH))
print('CPUs detected: %i' %(cpus))
print('RAM available: %i GB \n' %(ram))

#-----------------------------------------------------------------------------

# Perform initial installation if necessary
import VersioningControl as version # functions to handle software updates
if(versionType=='release'):
    
    # Automatic installation
    version.install()

    # Update the readme file
    flag_upgraded = version.upgrade(versionNumber)
    
    # Restart the software if the software has been upgraded
    if(flag_upgraded): raise Exception('restart required')
    
else: flag_upgraded = False

#-----------------------------------------------------------------------------

# Load remaining external modules
import cv2 # OpenCV
import matplotlib # Matplotlib module
import matplotlib.pyplot as plt # Matplotlib plotting functionality
import tkinter as tk # TkInter UI backbone
from tkinter import filedialog # TkInter file browsers
from tkinter import messagebox # TkInter popup windows

# Load remaining user modules
import GeneralSupportFunctions as gensup # general support functions
import PathPlanning as plan # pathe planner

# Load persistent variables
h_npz_settings = np.load(dirPvars+'settings.npz',allow_pickle=True)
softwareName = str(h_npz_settings['softwareName'])
recognizedImageExtensions = np.ndarray.tolist(h_npz_settings['recognizedImageExtensions'])
guiColor_black = h_npz_settings['guiColor_black']
guiColor_white = h_npz_settings['guiColor_white']
guiColor_offwhite = h_npz_settings['guiColor_offwhite']
guiColor_hotpink = h_npz_settings['guiColor_hotpink']
guiFontSize_large = h_npz_settings['guiFontSize_large']
guiFontSize_small = h_npz_settings['guiFontSize_small']
guiFontType_normal = h_npz_settings['guiFontType_normal']
guiFontType_uniform = h_npz_settings['guiFontType_uniform']

#-----------------------------------------------------------------------------

# Close previous windows
cv2.destroyAllWindows()
plt.close('all')

# Change Environment settings (some are only applicable if running in an iPython console)
try:
    from IPython import get_ipython # needed to run magic commands
    ipython = get_ipython() # needed to run magic commands
    ipython.magic('matplotlib qt') # display figures in a separate window
except: pass
plt.rcParams.update({'font.size': 24}) # change the default font size for plots
plt.rcParams.update({'figure.max_open_warning': False}) # disable warning about too opening too many figures - don't need that kind of negativity 
plt.rcParams['keymap.quit'] = '' # disable matplotlib hotkeys
plt.rcParams['keymap.save'] = '' # disable matplotlib hotkeys
if(ostype=='Linux'): matplotlib.use('TkAgg') # call the correct backend when installed on Linux

# Adjust dpi and font settings based on screen resolution
minScrnDim = min(scrnW,scrnH) # smallest screen dimension
guiScaling = min(1.0,minScrnDim/1080) # scaling factor for the user interface
if(scrnW*scrnH<(1.1*1920*1080)): plt.rcParams.update({'figure.dpi': 50})
else: plt.rcParams.update({'figure.dpi': 100})
guiFontSize_large = int(np.ceil(guiFontSize_large*(guiScaling**1)))
guiFontSize_small = int(np.ceil(guiFontSize_small*(guiScaling**1)))

#-----------------------------------------------------------------------------

class Path(): 
    """
    Data object for the current path
    """
    
    def __init__(self):
        
        self.x_real = 12*52.4375 # (in) length of the field
        self.y_real = 12*26.9375 # (in) width of the field
        self.v_max = 12*15.0 # (in/s) maximum robot velocity
        self.step_size = 1.0 # (in) path step size
        self.radius_min = 12.0 # (in) minimum robot turn radius
        self.radius_max = 100.0 # (in) maximum robot turn radius
        
# Instantiate the robot path
path = Path()
    
#-----------------------------------------------------------------------------

# Initialize global variables

#-----------------------------------------------------------------------------

def easyPlace(h,x,y):
    """
    Simplifies placing GUI elements in the main window
    """
    
    if((x>=0)&(y>=0)): h.place(x=abs(x)*windW,y=abs(y)*windH,anchor=tk.NW)
    elif((x<0)&(y>=0)): h.place(x=windW-abs(x)*windW,y=abs(y)*windH,anchor=tk.NE)
    elif((x>=0)&(y<0)): h.place(x=abs(x)*windW,y=windH-abs(y)*windH,anchor=tk.SW)
    elif((x<0)&(y<0)): h.place(x=windW-abs(x)*windW,y=windH-abs(y)*windH,anchor=tk.SE)
    
def lockMenus(topMenus,flag_lock): 
    """
    Simplifies the locking and un-locking process for the top menus
    """           
            
    # Set flags for locking an unlocking the menus
    if(flag_lock==True): lock = tk.DISABLED
    else: lock = tk.NORMAL 
    
    # Lock or unlock specific sets of menus
    for menu in topMenus:
        if(menu=='File'):
            menuFile.entryconfig('Load Field Map',state=lock) 

#-----------------------------------------------------------------------------

def actionNope(*args):
    """
    Default error message for un-implimented operations
    """
    
    # Report that the current operation is unavailable
    messagebox.showinfo(softwareName,'Error: This operation is\nnot yet available.')
    
#-----------------------------------------------------------------------------

def actionQuit(*args):
    """
    Closes the main GUI and exits the code
    """
    
    # Close the main GUI window 
    try:
        guiwindow.quit()
        guiwindow.destroy()
    except: pass

#-----------------------------------------------------------------------------

def actionApplySettings(*args):
    """
    Check the settings for errors and save them
    """
    
    # Check entries for errors
    flags = True
    [x_real,flags] = gensup.safeTextEntry(flags,textFields[0]['field'],'float',vmin=0.0,vmax=100.0)
    [y_real,flags] = gensup.safeTextEntry(flags,textFields[1]['field'],'float',vmin=0.0,vmax=100.0)
    [v_max,flags] = gensup.safeTextEntry(flags,textFields[2]['field'],'float',vmin=1.0,vmax=30.0)
    [step_size,flags] = gensup.safeTextEntry(flags,textFields[3]['field'],'float',vmin=1.0,vmax=100.0)
    [radius_min,flags] = gensup.safeTextEntry(flags,textFields[4]['field'],'float',vmin=1.0,vmax=1000.0)
    [radius_max,flags] = gensup.safeTextEntry(flags,textFields[5]['field'],'float',vmin=1.1*radius_min,vmax=1000.0)
    
    # Save the error-free entries in the correct units
    if(flags):
        path.x_real = 12.0*x_real
        path.y_real = 12.0*y_real
        path.v_max = 12.0*v_max
        path.step_size =step_size
        path.radius_min = radius_min
        path.radius_max = radius_max
    
#-----------------------------------------------------------------------------

def actionLoadField(*args):
    """
    ***
    """
    
    # Ask the user to load a field map
    path_I = filedialog.askopenfilename(initialdir='../field drawings/',title = 'Select a Field Drawing',filetypes=recognizedImageExtensions)
    
    # Ask the user to load a previous path
    #***
    
    print('yolo')
    
#-----------------------------------------------------------------------------

# Open the GUI window
guiwindow = tk.Tk()
guiwindow.title(softwareName)
windW = int(0.3*min(1080,minScrnDim)) # window width
windH = int(0.65*min(1080,minScrnDim)) # window height 
guiwindow.geometry(str(windW)+'x'+str(windH))
guiwindow.configure(background=guiColor_offwhite)
guiwindow.resizable(width=False, height=False)

# Set the initial window location
guiwindow.geometry("+{}+{}".format(int(0.5*(guiwindow.winfo_screenwidth()-windW)),int(0.5*(guiwindow.winfo_screenheight()-windH))))

# Configure to handle use of the Windows close button
guiwindow.protocol('WM_DELETE_WINDOW',actionQuit)

# Set up the logos
logo = tk.Canvas(guiwindow,width=int(466*guiScaling),height=int(232*guiScaling),highlightthickness=0,background=guiColor_offwhite)  
I_logo = gensup.convertColorSpace(cv2.imread(dirPvars+'graphic_4265.png')) # load the default image
gensup.easyTkImageDisplay(guiwindow,logo,I_logo,forceSize=[int(466*guiScaling),int(232*guiScaling)])

# Define the settings fields
fieldNames = ['Field Length (ft)',
              'Field Width (ft)',
              'Maximum Robot Velocity (ft/s)',
              'Step Size (in)',
              'Minimum Turn Radius (in)',
              'Maximum Turn Radius (in)']
defaults = [path.x_real/12.0,
            path.y_real/12.0,
            path.v_max/12.0,
            path.step_size,
            path.radius_min,
            path.radius_max]

# Set up the settings elements
textFields = []
for i in range(0,len(fieldNames),1):
    [title,field] = gensup.easyTextField(guiwindow,windW,fieldNames[i],str(defaults[i]))
    textFields.append({'title': title, 'field': field})
buttonApply = tk.Button(guiwindow,text='Apply',fg=guiColor_black,bg=guiColor_hotpink,font=(guiFontType_normal,guiFontSize_large),height=1,width=int(0.02*windW),command=actionApplySettings)

# Set up the menu bar
menubar = tk.Menu(guiwindow)
menuFile = tk.Menu(menubar, tearoff=0)
menuFile.add_command(label='Load Field Map',command=actionLoadField)
menuFile.add_command(label='Quit',command=actionQuit)
menubar.add_cascade(label='File',menu=menuFile)
guiwindow.config(menu=menubar)

# Place all elements
for i in range(0,len(textFields),1):
    textFields[i]['title'].pack(fill='both')
    textFields[i]['field'].pack()
buttonApply.pack(pady=20)
logo.pack(pady=20)

# Final GUI initializations

# Run the GUI window
if((__name__ == '__main__') and not flag_upgraded):
    plt.ion()
    gensup.flushMatplotlib()
    guiwindow.mainloop()
else: plt.pause(10.0) # allow the users to read any error messages
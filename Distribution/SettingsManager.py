# Date: 2020-06-09
# Description: handles configuration of embedded settings
#-----------------------------------------------------------------------------

# Load external modules
import datetime # formatting timestamps
import numpy as np # Numpy toolbox
import time # time toolbox

#-----------------------------------------------------------------------------

# Hardcoded directory paths
dirHome = '../code/' # return location of the home (code) directory
dirPvars = '../vars/' # persistent variables directory

# Hidden settings
softwareName = '4265 Path Planner'
recognizedImageExtensions = [('Images','*.jpg *.jpeg *.png *.tif *.tiff')] 
figSize = [25,25] # [inches, inches]
dispRes = 10 # controls the resolution of the displayed image
guiColor_black = '#%02x%02x%02x' % ((0,0,0))
guiColor_white = '#%02x%02x%02x' % ((150,150,150))
guiColor_offwhite = '#%02x%02x%02x' % ((58,58,58))
guiColor_darkgreen = '#%02x%02x%02x' % ((0,121,52))
guiColor_lightgreen = '#%02x%02x%02x' % ((132,182,65))
guiColor_red = '#%02x%02x%02x' % ((136,51,46)) 
guiColor_cherryred = '#%02x%02x%02x' % ((200,0,0)) 
guiColor_hotpink = '#%02x%02x%02x' % ((255,0,153)) 
guiColor_hotgreen = '#%02x%02x%02x' % ((118,255,3)) 
guiColor_hotyellow = '#%02x%02x%02x' % ((247,236,18)) 
guiFontSize_large = 14
guiFontSize_small = 10
guiFontType_normal = 'Arial' # normal font type
guiFontType_uniform = 'Consolas' # font type used when characters must have a uniform width

# Save the settings file
np.savez(dirPvars+'settings',
         timestamp=datetime.datetime.fromtimestamp(time.time()).strftime('%Y/%m/%d %H:%M:%S'),
         dirHome=dirHome,
         dirPvars=dirPvars,
         softwareName=softwareName,
         recognizedImageExtensions=recognizedImageExtensions,
         figSize=figSize,
         dispRes=dispRes,
         guiColor_black=guiColor_black,
         guiColor_white=guiColor_white,
         guiColor_offwhite=guiColor_offwhite,
         guiColor_darkgreen=guiColor_darkgreen,
         guiColor_lightgreen=guiColor_lightgreen,
         guiColor_hotyellow=guiColor_hotyellow,
         guiColor_red=guiColor_red,
         guiColor_cherryred=guiColor_cherryred,
         guiColor_hotpink=guiColor_hotpink,
         guiColor_hotgreen=guiColor_hotgreen,
         guiFontSize_large=guiFontSize_large,
         guiFontSize_small=guiFontSize_small,
         guiFontType_normal=guiFontType_normal,
         guiFontType_uniform=guiFontType_uniform)
print('Embeddeded settings saved.')

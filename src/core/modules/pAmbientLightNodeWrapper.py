import pickle

from pandac.PandaModules import *

from core.modules.pLightNodeWrapper import LightNodeWrapper
from core.pModelController import modelController
from core.pConfigDefs import *

class AmbientLightNodeWrapper( LightNodeWrapper ):
  def __init__(self, parent=None):
    # define the name of this object
    name = 'AmbientLight'
    LightNodeWrapper.__init__(self, name, AmbientLight, AMBIENTLIGHT_WRAPPER_DUMMYOBJECT, name, parent)
    
    self.light.setColor(VBase4(.25,.25,.25,1))
  
  def getSaveData(self, relativeTo):
    instance = LightNodeWrapper.getSaveData(self, relativeTo)
    # get the data
    parameters = dict()
    if len(parameters) > 0:
      # add the data to the egg-file
      comment = EggComment( 'AmbientLightNodeWrapper-params', str(parameters) )
      instance.addChild(comment)
    return instance
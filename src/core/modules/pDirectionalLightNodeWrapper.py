import pickle

from pandac.PandaModules import *

from core.modules.pLightNodeWrapper import LightNodeWrapper
from core.pModelController import modelController
from core.pConfigDefs import *

class DirectionalLightNodeWrapper(LightNodeWrapper):
  def __init__(self, parent=None):
    # define the name of this object
    name = 'DirectionalLight'
    LightNodeWrapper.__init__(self, name, DirectionalLight, DIRECTIONALLIGHT_WRAPPER_DUMMYOBJECT, name, parent)
    
    self.light.setColor(VBase4(1,1,1,1))
  
  def getSaveData(self, relativeTo):
    instance = LightNodeWrapper.getSaveData(self, relativeTo)
    # get the data
    parameters = dict()
    if len(parameters):
      # add the data to the egg-file
      comment = EggComment( 'DirectionalLightNodeWrapper-params', str(parameters) )
      instance.addChild(comment)
    return instance

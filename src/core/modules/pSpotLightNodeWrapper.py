import pickle

from pandac.PandaModules import *

from core.modules.pLightNodeWrapper import LightNodeWrapper
from core.pModelController import modelController
from core.pConfigDefs import *

class SpotLightNodeWrapper(LightNodeWrapper):
  def __init__(self, parent=None):
    # define the name of this object
    name = 'SpotLight'
    LightNodeWrapper.__init__(self, name, Spotlight, SPOTLIGHT_WRAPPER_DUMMYOBJECT, name, parent)
  
  def getSaveData(self, relativeTo):
    instance = LightNodeWrapper.getSaveData(self, relativeTo)
    # get the data
    parameters = dict()
    if len(parameters) > 0:
      # add the data to the egg-file
      comment = EggComment( 'SpotLightNodeWrapper-params', str(parameters) )
      instance.addChild(comment)
    return instance

import pickle

from pandac.PandaModules import *

from core.modules.pLightNodeWrapper import LightNodeWrapper
from core.pModelController import modelController
from core.pConfigDefs import *

class PointLightNodeWrapper(LightNodeWrapper):
  def __init__(self, parent=None, name='PointLight'):
    # define the name of this object
    name = 'PointLight'
    LightNodeWrapper.__init__(self, parent, name, POINTLIGHT_WRAPPER_DUMMYOBJECT, PointLight)
  
  def getSaveData(self, relativeTo):
    instance = LightNodeWrapper.getSaveData(self, relativeTo)
    # get the data
    parameters = dict()
    if len(parameters) > 0:
      # add the data to the egg-file
      comment = EggComment( 'PointLightNodeWrapper-params', str(parameters) )
      instance.addChild(comment)
    return instance
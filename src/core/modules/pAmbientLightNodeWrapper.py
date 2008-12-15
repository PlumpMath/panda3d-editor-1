import pickle

from pandac.PandaModules import *

from core.modules.pLightNodeWrapper import LightNodeWrapper
from core.pModelController import modelController
from core.pConfigDefs import *

class AmbientLightNodeWrapper( LightNodeWrapper ):
  def __init__(self, parent=None, name='AmbientLight'):
    # define the name of this object
    LightNodeWrapper.__init__(self, parent, name, AMBIENTLIGHT_WRAPPER_DUMMYOBJECT, AmbientLight)
  
  def getSaveData(self, relativeTo):
    instance = LightNodeWrapper.getSaveData(self, relativeTo)
    # get the data
    parameters = dict()
    if len(parameters) > 0:
      # add the data to the egg-file
      comment = EggComment( 'AmbientLightNodeWrapper-params', str(parameters) )
      instance.addChild(comment)
    return instance
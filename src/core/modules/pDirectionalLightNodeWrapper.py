import pickle

from pandac.PandaModules import *

from core.modules.pLightNodeWrapper import LightNodeWrapper
from core.pModelController import modelController
from core.pConfigDefs import *

class DirectionalLightNodeWrapper(LightNodeWrapper):
  def __init__(self, parent=None, name='DirectionalLight'):
    # define the name of this object
    name = 'DirectionalLight'
    LightNodeWrapper.__init__(self, parent, name, DIRECTIONALLIGHT_WRAPPER_DUMMYOBJECT, DirectionalLight)
  
  def hasAttenuation(self, *args, **kwargs):
    return False

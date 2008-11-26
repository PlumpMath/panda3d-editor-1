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
    
    self.light.setColor(VBase4(1,1,1,1))

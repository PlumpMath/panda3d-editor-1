import pickle

from pandac.PandaModules import *

from core.modules.pLightNodeWrapper import LightNodeWrapper
from core.pModelController import modelController
from core.pConfigDefs import *

class PointLightNodeWrapper(LightNodeWrapper):
  def __init__(self, parent=None):
    # define the name of this object
    name = 'PointLight'
    LightNodeWrapper.__init__(self, name, PointLight, POINTLIGHT_WRAPPER_DUMMYOBJECT, name, parent)
    
    self.light.setColor(VBase4(1,1,1,1))

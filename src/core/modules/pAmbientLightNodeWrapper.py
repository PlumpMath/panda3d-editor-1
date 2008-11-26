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

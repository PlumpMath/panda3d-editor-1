__all__=['AmbientLightNodeWrapper']

from pandac.PandaModules import *

from core.modules.pLightNodeWrapper import LightNodeWrapper
from core.pConfigDefs import *

class AmbientLightNodeWrapper(LightNodeWrapper):
  className = 'AmbientLight'
  def __init__(self, parent=None, name='AmbientLight'):
    # define the name of this object
    LightNodeWrapper.__init__(self, parent, name, AMBIENTLIGHT_WRAPPER_DUMMYOBJECT, AmbientLight)

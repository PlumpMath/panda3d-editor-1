import pickle

from pandac.PandaModules import *

from core.modules.pVirtualNodeWrapper import VirtualNodeWrapper
from core.pModelController import modelController
from core.pConfigDefs import *

class AmbientLightNodeWrapper( VirtualNodeWrapper ):
  def __init__(self, parent=None):
    # define the name of this object
    name = 'AmbientLight'
    VirtualNodeWrapper.__init__(self, AMBIENTLIGHT_WRAPPER_DUMMYOBJECT, name, parent)
    
    self.light = AmbientLight(name)
    self.light.setColor(VBase4(.25,.25,.25,1))
    self.lightNodePath = self.attachNewNode(self.light)
    # create the spotLight
    render.setLight(self.lightNodePath)
  
  def destroy(self):
    # destroy this object
    render.clearLight(self.lightNodePath)
    self.lightNodePath.detachNode()
    VirtualNodeWrapper.destroy(self)
  
  def getSaveData(self, relativeTo):
    parameters = list()
    pickledData = pickle.dumps(parameters)
    return VirtualNodeWrapper.getSaveData(self, relativeTo, pickledData)

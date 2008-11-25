import pickle

from pandac.PandaModules import *

from core.modules.pVirtualNodeWrapper import VirtualNodeWrapper
from core.pModelController import modelController
from core.pConfigDefs import *

class DirectionalLightNodeWrapper(VirtualNodeWrapper):
  def __init__(self, parent=None):
    # define the name of this object
    name = 'DirectionalLight'
    VirtualNodeWrapper.__init__(self, DIRECTIONALLIGHT_WRAPPER_DUMMYOBJECT, name, parent)
    
    self.light = DirectionalLight('DirectionalLight')
    self.light.setColor(VBase4(1,1,1,1))
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

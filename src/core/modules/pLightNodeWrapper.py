import pickle

from pandac.PandaModules import *

from core.modules.pVirtualNodeWrapper import VirtualNodeWrapper
from core.pModelController import modelController
from core.pConfigDefs import *

class LightNodeWrapper(VirtualNodeWrapper):
  def __init__(self, parent, name, lightModel, lightType):
    VirtualNodeWrapper.__init__(self, parent, name, lightModel)
    
    # create a instance of the light
    self.light = lightType(name)
    self.lightNodePath = self.attachNewNode(self.light)
    # create the light
    # this should be made selectable
    render.setLight(self.lightNodePath)
    
    self.mutableParameters['color'] = [ Vec4,
      self.light.getColor,
      self.light.setColor,
      None,
      None ]
    self.mutableParameters['priority'] = [ int,
      self.light.getPriority,
      self.light.setPriority,
      None,
      None ]
  
  def destroy(self):
    # destroy this object
    render.clearLight(self.lightNodePath)
    self.lightNodePath.detachNode()
    VirtualNodeWrapper.destroy(self)

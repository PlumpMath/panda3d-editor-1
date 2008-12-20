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
      self.light.hasColor,
      self.light.clearColor ]
    self.mutableParameters['attenuation'] = [ Vec3,
      self.getAttenuation,
      self.setAttenuation,
      self.hasAttenuation,
      None ]
    self.mutableParameters['priority'] = [ int,
      self.getPriority,
      self.setPriority,
      self.hasPriority,
      None ]
    self.mutableParameters['spec_color'] = [ Vec4,
      self.getSpecularColor,
      self.setSpecularColor,
      self.hasSpecularColor,
      None ]
  
  # must be handled by ourself (saving)
  def getPriority(self, *args, **kwargs):
    return self.light.getPriority(*args, **kwargs)
  def setPriority(self, *args, **kwargs):
    return self.light.setPriority(*args, **kwargs)
  def hasPriority(self, *args, **kwargs):
    return True
  
  def getAttenuation(self, *args, **kwargs):
    return self.light.getAttenuation(*args, **kwargs)
  def setAttenuation(self, *args, **kwargs):
    return self.light.setAttenuation(*args, **kwargs)
  def hasAttenuation(self, *args, **kwargs):
    print "I: LightNodeWrapper.hasAttenuation"
    # is overridden by ambientlight, which hasnt got this parameter
    return True
  
  def getSpecularColor(self, *args, **kwargs):
    return self.light.getSpecularColor(*args, **kwargs)
  def setSpecularColor(self, *args, **kwargs):
    return self.light.setSpecularColor(*args, **kwargs)
  def hasSpecularColor(self, *args, **kwargs):
    # is overridden by ambientlight, which hasnt got this parameter
    return True
  
  def destroy(self):
    # destroy this object
    render.clearLight(self.lightNodePath)
    self.lightNodePath.detachNode()
    VirtualNodeWrapper.destroy(self)

__all__=['VirtualNodeWrapper']

from pandac.PandaModules import *

from core.modules.pBaseWrapper import BaseWrapper
from core.pConfigDefs import *

# parent class for all nodetypes that have no real model
# like lights, particle systems etc. (well most except the NodePath)
# (might be useful for all virtual objects?)
class VirtualNodeWrapper(BaseWrapper):
  className = 'Virtual'
  def __init__(self, parent, name, virtualModelpath):
    self.virtualModelpath = virtualModelpath
    self.virtualModel = None
    BaseWrapper.__init__(self, parent, name)
  
  def destroy( self ):
    # destroy this object
    self.stopEdit()
    self.setEditmodeDisabled()
    #modelIdManager.delObjectId( self.id )
    BaseWrapper.destroy( self )
  
  def setEditmodeEnabled(self):
    ''' enables the edit methods of this object
    makes it pickable etc.'''
    if not self.isEditmodeEnabled(): # variable will be changed by basewrapper
      # load a dummy model
      self.virtualModel = loader.loadModel(self.virtualModelpath)
      # set the model invisible in the scenegraphbrowser
      self.virtualModel.setLightOff()
      # make the model visible
      self.virtualModel.reparentTo(self.nodePath)
      # enable picking of the object
      self.nodePath.setCollideMask(DEFAULT_EDITOR_COLLIDEMASK)
      # edit mode is enabled
      BaseWrapper.setEditmodeEnabled(self)
  
  def setEditmodeDisabled(self):
    ''' disables the edit methods of this object
     -> performance increase'''
    if self.isEditmodeEnabled():
      # edit mode is disabled
      BaseWrapper.setEditmodeDisabled(self)
      # remove the dummy model
      self.virtualModel.removeNode()
      self.virtualModel.detachNode()
      # disable picking of the object
      self.nodePath.setCollideMask( BitMask32.allOff() )
  
  def startEdit( self ):
    # the object is selected to be edited
    # creates a directFrame to edit this object
    if self.isEditmodeEnabled():
      self.virtualModel.showBounds()
    BaseWrapper.startEdit(self)
  def stopEdit( self ):
    # the object is deselected from being edited
    if self.isEditmodeEnabled():
      self.virtualModel.hideBounds()
    BaseWrapper.stopEdit(self)

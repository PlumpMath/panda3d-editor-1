import pickle

from pandac.PandaModules import *

from core.modules.pBaseWrapper import *
from core.pModelController import modelController

# parent class for all nodetypes that have no real model
# like lights, particle systems etc. (well most except the NodePath)
# (might be useful for all virtual objects?)
class VirtualNodeWrapper(BaseWrapper):
  def __init__(self, parent, name, virtualModelpath):
    self.virtualModelpath = virtualModelpath
    self.virtualModel = None
    BaseWrapper.__init__(self, parent, name)
  
  def destroy( self ):
    # destroy this object
    self.stopEdit()
    self.disableEditmode()
    modelIdManager.delObjectId( self.id )
    BaseWrapper.destroy( self )
  
  def enableEditmode( self ):
    ''' enables the edit methods of this object
    makes it pickable etc.'''
    if not self.editModeEnabled: # variable will be changed by basewrapper
      # load a dummy model
      self.virtualModel = loader.loadModel( self.virtualModelpath )
      # set the model invisible in the scenegraphbrowser
      self.virtualModel.setTag(EXCLUDE_SCENEGRAPHBROWSER_MODEL_TAG,'')
      self.virtualModel.setLightOff()
      # make the model visible
      self.virtualModel.reparentTo( self )
      # enable picking of the object
      self.setCollideMask( DEFAULT_EDITOR_COLLIDEMASK )
      # edit mode is enabled
      BaseWrapper.enableEditmode( self )
  def disableEditmode( self ):
    ''' disables the edit methods of this object
     -> performance increase'''
    if self.editModeEnabled:
      # edit mode is disabled
      BaseWrapper.disableEditmode( self )
      # remove the dummy model
      self.virtualModel.removeNode()
      self.virtualModel.detachNode()
      # disable picking of the object
      self.setCollideMask( BitMask32.allOff() )
  
  def startEdit( self ):
    # the object is selected to be edited
    # creates a directFrame to edit this object
    if self.editModeEnabled:
      self.virtualModel.showBounds()
    BaseWrapper.startEdit(self)
  def stopEdit( self ):
    # the object is deselected from being edited
    if self.editModeEnabled:
      self.virtualModel.hideBounds()
    BaseWrapper.stopEdit(self)
  
  def getSaveData(self, relativeTo):
    instance = BaseWrapper.getSaveData(self, relativeTo)
    # get the data
    parameters = dict()
    if len(parameters) > 0:
      # add the data to the egg-file
      comment = EggComment( 'VirtualNodeWrapper-params', str(parameters) )
      instance.addChild(comment)
    return instance
  def loadFromData(self, eggGroup, filepath):
    BaseWrapper.loadFromData(self, eggGroup, filepath)

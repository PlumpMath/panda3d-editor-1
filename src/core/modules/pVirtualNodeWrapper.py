import pickle

from pandac.PandaModules import *

from core.modules.pBaseWrapper import *
from core.pModelController import modelController

# parent class for all nodetypes that have no real model
# like lights, particle systems etc. (well most except the NodePath)
# (might be useful for all virtual objects?)
class VirtualNodeWrapper( BaseWrapper ):
  def onCreateInstance(self, parent):
    ''' called when the user presses the button to create a nodePathWrapper
    '''
    objectInstance = self(parent)
    # enable this object to be editable
    objectInstance.enableEditmode()
    # the editor should select this model
    modelController.selectModel( objectInstance )
    # update the scenegraph
    messenger.send( EVENT_SCENEGRAPHBROWSER_REFRESH )
  onCreateInstance = classmethod(onCreateInstance)
  
  def loadFromEggGroup(self, eggGroup, parent, filepath):
    eggComment = eggGroup.getChildren()[0]
    #objectInstance = AmbientLightNodeWrapper( parent )
    objectInstance = self(parent)
    return objectInstance
  loadFromEggGroup = classmethod(loadFromEggGroup)
  
  def __init__(self, virtualModelpath, *args, **kwargs):
    self.virtualModel = None
    self.virtualModelpath = virtualModelpath
    BaseWrapper.__init__(self, *args, **kwargs)
  
  def destroy( self ):
    # destroy this object
    self.stopEdit()
    self.disableEditmode()
    modelIdManager.delObjectId( self.id )
    BaseWrapper.destroy( self )
  
  def enableEditmode( self ):
    # load a dummy model
    self.virtualModel = loader.loadModel( self.virtualModelpath )
    # set the model invisible in the scenegraphbrowser
    self.virtualModel.setTag(EXCLUDE_SCENEGRAPHBROWSER_MODEL_TAG,'')
    self.virtualModel.setLightOff()
    # make the model visible
    self.virtualModel.reparentTo( self )
    # enable picking of the object
    self.setCollideMask( DEFAULT_EDITOR_COLLIDEMASK )
    # enables the edit methods of this object
    # makes it pickable etc.
    # edit mode is enabled
    BaseWrapper.enableEditmode( self )
  def disableEditmode( self ):
    # disables the edit methods of this object
    # -> performance increase
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
    self.virtualModel.showBounds()
    BaseWrapper.startEdit( self )
  def stopEdit( self ):
    # the object is deselected from being edited
    self.virtualModel.hideBounds()
    BaseWrapper.stopEdit( self )
  
  def getSaveData(self, relativeTo, pickledData):
    # convert the matrix, very ugly right now
    om = self.getMat()
    nm = Mat4D()
    for x in xrange(4):
        for y in xrange(4):
            nm.setCell( x, y, om.getCell(x,y) )
    # the matrix we define must be applied to the nodes in "local space"
    nodeName = self.getName()
    instance = EggGroup( nodeName+"-Group" )
    instance.setGroupType(EggGroup.GTInstance)
    instance.setTransform3d( nm )
    className = self.__class__.__name__
    instance.setTag( MODEL_WRAPPER_TYPE_TAG, className )
    # add the data to the egg-file
    comment = EggComment( 'parameters', pickledData )
    instance.addChild(comment)
    return instance

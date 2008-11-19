from pandac.PandaModules import *
from direct.gui.DirectGui import *

from core.pModelIdManager import modelIdManager
from core.pConfigDefs import *
#from lib.filebrowser import FG
#from lib.directWindow.src.directWindow import DirectWindow

class BaseWrapper( NodePath ):
  def __init__( self, name=None, parent=None ):
    print "I: BaseWrapper.__init__:", name, parent
    self.mutableParameters = {
        'posX': ['float', 'getX', 'setX']
      , 'posY': ['float', 'getY', 'setY']
      , 'posZ': ['float', 'getZ', 'setZ']
      , 'H': ['float', 'getH', 'setH']
      , 'P': ['float', 'getP', 'setP']
      , 'R': ['float', 'getR', 'setR']
      , 'scaleX': ['float', 'getSx', 'setSx']
      , 'scaleY': ['float', 'getSy', 'setSy']
      , 'scaleZ': ['float', 'getSz', 'setSz']
      , 'transparency': ['bool', 'getTransparency', 'setTransparency' ]
      , 'nodeName': ['str', 'getName', 'setName' ]
    }
    self.mutableParametersSorting = [
      'posX', 'posY', 'posZ'
    , 'H', 'P', 'R'
    , 'scaleX', 'scaleY', 'scaleZ'
    , 'transparency'
    , 'nodeName'
    ]
    self.buttonsWindow = None
    
    # get a uniq id for this object
    self.id = modelIdManager.getId()
    # define a name for this object
    if name is None:
      name = 'BaseWrapper'
    name = '%s-%s' % (name, self.id)
    NodePath.__init__( self, name )
    # store this object
    modelIdManager.setObject( self, self.id )
    # reparent this nodePath
    if parent is None:
      parent = render
    self.reparentTo( parent )
    # make this a editable object
    self.setTag( EDITABLE_OBJECT_TAG, self.id )
    self.setTag( ENABLE_SCENEGRAPHBROWSER_MODEL_TAG, '' )
  
  def destroy( self ):
    self.detachNode()
    self.removeNode()
  
  def onCreate( self ):
    # open a file dialog
    # create a instance of NodePathWrapper
    return BaseWrapper()
  onCreate = classmethod(onCreate)
  def getSaveData( self ):
    # returns a eggGroup containing the data of this object
    pass
  
  def enableEditmode( self ):
    # enables the edit methods of this object
    # makes it pickable etc.
    # edit mode is enabled
    
    # make this a editable object
    self.setTag( EDITABLE_OBJECT_TAG, self.id )
    self.setTag( ENABLE_SCENEGRAPHBROWSER_MODEL_TAG, '' )
  def disableEditmode( self ):
    # disables the edit methods of this object
    # -> performance increase
    # edit mode is disabled
    pass
  
  def startEdit( self ):
    # the object is selected to be edited
    # creates a directFrame to edit this object
    #self.createEditWindow()
    self.model.showBounds()
  def stopEdit( self ):
    # the object is deselected from being edited
    #self.destroyEditWindow()
    self.model.hideBounds()

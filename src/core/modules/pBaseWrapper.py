from pandac.PandaModules import *
from direct.gui.DirectGui import *

from core.pModelIdManager import modelIdManager
from core.pConfigDefs import *
#from lib.filebrowser import FG
#from lib.directWindow.src.directWindow import DirectWindow

DEBUG = False

class BaseWrapper( NodePath ):
  def __init__( self, name=None, parent=None ):
    if DEBUG:
      print "I: BaseWrapper.__init__:", name, parent
    
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
  
  '''def getSaveData( self ):
    # returns a eggGroup containing the data of this object
    pass'''
  
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
    pass
  def stopEdit( self ):
    # the object is deselected from being edited
    #self.destroyEditWindow()
    pass

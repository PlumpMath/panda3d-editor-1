import os

from core.modules.pBaseWrapper import *
from core.pModelController import modelController
from core.pCommonPath import *

class NodePathWrapper( BaseWrapper ):
  wrapperTypeTag = 'NodePathWrapper'
  
  '''def onCreate( self, parent ):
    # this is called when the user presses the button to create
    # a nodePathWrapper
    # open a file browser
    
    #FG.openFileBrowser()
    #FG.accept('selectionMade', NodePathWrapper.onCreateInstance, [parent])
    pass
  onCreate = classmethod(onCreate)'''
  
  def onCreateInstance( self, parent, filename ):
    print "I: NodePathWrapper.onCreateInstance:", parent, "'%s'" % filename
    if filename != ' ':
      # single extension (.egg)
      base, ext1 = os.path.splitext(filename)
      # extension with 2 dots (.egg.pz)
      file, ext2 = os.path.splitext(base)
      e1 = ext1[1:]
      e2 = ext2[1:]+ext1
      if e1 in VALID_MODEL_FORMATS or e2 in VALID_MODEL_FORMATS:
        # check if model file is in pandaModelPath
        from pandac.PandaModules import getModelPath
        pandaPath = None
        filename = str(Filename.fromOsSpecific(filename))
        for searchPath in str(getModelPath()).split():
          if searchPath in filename:
            pandaPath = searchPath
            print "I: model found in pandaModelPath %s" % pandaPath
            break
        if pandaPath is None:
          pandaPath = '/'.join(filename.split('/')[:-1])
          print "W: adding %s to pandaModelPath" % pandaPath
          from pandac.PandaModules import getModelPath, getTexturePath, getSoundPath
          getModelPath( ).appendPath( pandaPath )
          getTexturePath( ).appendPath( pandaPath )
          getSoundPath( ).appendPath( pandaPath )
        filename = filename.replace( pandaPath, '.' )
        objectInstance = NodePathWrapper( filename, parent )
        #
        objectInstance.enableEditmode()
        # select this model
        modelController.selectModel( objectInstance )
      else:
        print "  - unknown model format: '%s' or '%s'" % (e1, e2)
    else:
      print "  - no file selected"
    messenger.send( EVENT_SCENEGRAPHBROWSER_REFRESH )
  onCreateInstance = classmethod(onCreateInstance)
  
  def __init__( self, modelFilename, parent=None ):
    print "I: NodePathWrapper.__init__:", modelFilename
    # define the name of this object
    name = modelFilename.split('/')[-1]
    BaseWrapper.__init__( self, name, parent )
    
    # the path to the model we handle
    self.modelFilename = modelFilename
    # load the model
    self.model = loader.loadModel( modelFilename )
    # if the model loading fails, use a dummy object
    if self.model is None:
      print "W: editorModelClass: model %s not found, loading dummy" % self.model
      self.model = loader.loadModel( MODEL_NOT_FOUND_MODEL )
    
    # set the model invisible in the scenegraphbrowser
    self.model.setTag(EXCLUDE_SCENEGRAPHBROWSER_MODEL_TAG,'')
    # make the model visible
    self.model.reparentTo( self )
  
  def destroy( self ):
    # destroy this object
    self.stopEdit()
    self.disableEditmode()
    modelIdManager.delObjectId( self.id )
    self.model.detachNode()
    self.model.removeNode()
    BaseWrapper.destroy( self )
  
  def enableEditmode( self ):
    # enables the edit methods of this object
    # makes it pickable etc.
    # edit mode is enabled
    BaseWrapper.enableEditmode( self )
    self.setCollideMask( DEFAULT_EDITOR_COLLIDEMASK )
  def disableEditmode( self ):
    # disables the edit methods of this object
    # -> performance increase
    # edit mode is disabled
    BaseWrapper.disableEditmode( self )
    self.setCollideMask( BitMask32.allOff() )
  
  def startEdit( self ):
    # the object is selected to be edited
    # creates a directFrame to edit this object
    self.model.showBounds()
    BaseWrapper.startEdit( self )
  def stopEdit( self ):
    # the object is deselected from being edited
    self.model.hideBounds()
    BaseWrapper.stopEdit( self )
  
  def getSaveData( self, relativeTo ):
    ''' link the egg-file into the egg we save
    '''
    name = self.getName()
    # convert the matrix, very ugly right now
    om = self.getMat()
    nm = Mat4D()
    for x in xrange(4):
        for y in xrange(4):
            nm.setCell( x, y, om.getCell(x,y) )
    # the matrix we define must be applied to the nodes in "local space"
    instance = EggGroup( name+"-Group" )
    instance.setGroupType(EggGroup.GTInstance)
    instance.setTransform3d( nm )
    # userdata is not written to the eggFile
    #instance.setUserData( self.wrapperTypeTag )
    instance.setTag( MODEL_WRAPPER_TYPE_TAG, self.wrapperTypeTag )
    # convert to a relative path
    modelFilename = relpath( relativeTo, os.path.abspath(self.modelFilename) )
    # add the reference to the egg-file
    ext = EggExternalReference( name+"-EggExternalReference", modelFilename )
    instance.addChild(ext)
    return instance
  
  def loadFromEggGroup( self, eggGroup, parent ):
    print "I: NodePathWrapper.loadFromEggGroup:"
    eggExternalReference = eggGroup.getChildren()[0]
    filename = str(eggExternalReference.getFilename())
    objectInstance = NodePathWrapper( filename, parent )
    return objectInstance
  loadFromEggGroup = classmethod(loadFromEggGroup)

if __name__ == '__main__':
  print "testing notdePathWrapper"
  a = NodePathWrapper.onCreate( 'test2' )
  print a.baseName, a.nodeName
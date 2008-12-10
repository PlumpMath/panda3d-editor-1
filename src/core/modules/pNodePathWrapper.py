import os

from core.modules.pBaseWrapper import *
from core.pModelController import modelController
from core.pCommonPath import *

DEBUG = False

class NodePathWrapper(BaseWrapper):
  def onCreateInstance(self, parent, filepath):
    if DEBUG:
      print "I: NodePathWrapper.onCreateInstance:", parent, "'%s'" % filepath
    filepath = str(Filename.fromOsSpecific(filepath))
    
    # add the model path to the panda-path
    pandaPath = None
    from pandac.PandaModules import getModelPath
    for searchPath in str(getModelPath()).split():
      if searchPath == filepath:
        pandaPath = searchPath
    if pandaPath is None:
      pandaPath = '/'.join(filepath.split('/')[:-1])
      from pandac.PandaModules import getModelPath
      if DEBUG:
        print "  - adding to pandapath:", pandaPath
      getModelPath().appendPath(pandaPath)
    
    # create instance of this class
    objectInstance = self(parent, filepath)
    
    return objectInstance
  onCreateInstance = classmethod(onCreateInstance)
  
  def loadFromEggGroup(self, eggGroup, parent, filepath):
    if DEBUG:
      print "I: NodePathWrapper.loadFromEggGroup:"
    # search for a external reference
    eggExternalReference = None
    for child in eggGroup.getChildren():
      if type(child) == EggExternalReference:
        eggExternalReference = child
    # read the reference if it is found
    if eggExternalReference is not None:
      referencedFilename = eggExternalReference.getFilename()
      filename = os.path.join(filepath,str(referencedFilename))
      objectInstance = self.onCreateInstance(parent, filename)
      objectInstance.setLoadData(eggGroup)
      return objectInstance
    else:
      print "I: NodePathWrapper.loadFromEggGroup: no externalReference found in"
      print "  -",eggGroup
    return None
  loadFromEggGroup = classmethod(loadFromEggGroup)
  
  def __init__(self, parent=None, filepath=None):
    if DEBUG:
      print "I: NodePathWrapper.__init__:", filepath
    # define the name of this object
    name = filepath.split('/')[-1]
    BaseWrapper.__init__(self, name, parent)
    
    # the path to the model we handle
    self.modelFilepath = filepath
    # load the model
    self.model = loader.loadModel(filepath)
    # if the model loading fails, use a dummy object
    if self.model is None:
      print "W: editorModelClass: model %s not found, loading dummy" % self.model
      self.model = loader.loadModel(MODEL_NOT_FOUND_MODEL)
    
    # make the model visible
    self.model.reparentTo(self)
  
  def destroy(self):
    # destroy this object
    self.stopEdit()
    self.disableEditmode()
    modelIdManager.delObjectId(self.id)
    self.model.detachNode()
    self.model.removeNode()
    BaseWrapper.destroy(self)
  
  def enableEditmode(self):
    # enables the edit methods of this object
    # makes it pickable etc.
    # edit mode is enabled
    BaseWrapper.enableEditmode(self)
    self.setCollideMask(DEFAULT_EDITOR_COLLIDEMASK)
  def disableEditmode(self):
    # disables the edit methods of this object
    # -> performance increase
    # edit mode is disabled
    BaseWrapper.disableEditmode( self )
    self.setCollideMask(BitMask32.allOff())
  
  def startEdit(self):
    # the object is selected to be edited
    # creates a directFrame to edit this object
    BaseWrapper.startEdit(self)
    self.model.showBounds()
  def stopEdit(self):
    # the object is deselected from being edited
    BaseWrapper.stopEdit(self)
    self.model.hideBounds()
  
  def getSaveData(self, relativeTo):
    ''' link the egg-file into the egg we save
    '''
    name = self.getName()
    instance = BaseWrapper.getSaveData(self, relativeTo)
    # convert to a relative path
    modelFilepath = relpath(relativeTo, os.path.abspath(self.modelFilepath))
    if DEBUG:
      print "I: pNodePathWrapper.getSaveData: modelFilepath:", modelFilepath, self.modelFilepath, relativeTo
    # add the reference to the egg-file
    ext = EggExternalReference(name+"-EggExternalReference", modelFilepath)
    instance.addChild(ext)
    return instance
  
  def getLoadData(self, eggGroup):
    BaseWrapper.getLoadData(self, eggGroup)

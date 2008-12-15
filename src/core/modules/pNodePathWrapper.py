import os

from core.modules.pBaseWrapper import *
from core.pModelController import modelController
from core.pCommonPath import *

DEBUG = False

class NodePathWrapper(BaseWrapper):
  def onCreateInstance(self, parent, filepath):
    # create instance of this class
    if filepath is not None:
      name = filepath.split('/')[-1]
    else:
      name = 'NodePath'
    objectInstance = super(NodePathWrapper, self).onCreateInstance(parent, name)
    objectInstance.setModel(filepath)
    return objectInstance
  onCreateInstance = classmethod(onCreateInstance)
  
  def __init__(self, parent=None, name=None):
    BaseWrapper.__init__(self, parent, name)
    self.model = None
    # content must be loaded using setModel
    # (done by onCreateInstance and loadFromEggGroup)
  
  def setModel(self, modelFilepath):
    # if there is already a model defined, remove it
    if self.model is not None:
      self.model.detachNode()
    
    if modelFilepath is not None:
      filepath = str(Filename.fromOsSpecific(modelFilepath))
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
          print "I: NodePathWrapper.setModel: adding to pandapath:"
          print "  -", pandaPath
        getModelPath().appendPath(pandaPath)
    
      # the path to the model we handle
      self.modelFilepath = modelFilepath
      # load the model
      self.model = loader.loadModel(modelFilepath)
    
    # if the model loading fails or no path given, use a dummy object
    if self.model is None:
      print "W: NodePathWrapper.setModel: model %s not found, loading dummy" % self.model
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
    if not self.editModeEnabled:
      # edit mode is enabled
      BaseWrapper.enableEditmode(self)
      self.setCollideMask(DEFAULT_EDITOR_COLLIDEMASK)
  def disableEditmode(self):
    if self.editModeEnabled:
      # edit mode is disabled
      BaseWrapper.disableEditmode( self )
      self.setCollideMask(BitMask32.allOff())
  
  def startEdit(self):
    # the object is selected to be edited
    # creates a directFrame to edit this object
    BaseWrapper.startEdit(self)
    if self.editModeEnabled:
      self.model.showBounds()
  def stopEdit(self):
    # the object is deselected from being edited
    if self.editModeEnabled:
      self.model.hideBounds()
    BaseWrapper.stopEdit(self)
  
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
  
  def loadFromData(self, eggGroup, filepath):
    # search for a external reference
    eggExternalReference = None
    for child in eggGroup.getChildren():
      if type(child) == EggExternalReference:
        eggExternalReference = child
    # read the reference if it is found
    if eggExternalReference is not None:
      referencedFilename = eggExternalReference.getFilename()
      filename = os.path.join(filepath,str(referencedFilename))
      self.setModel(filename)
    else:
      print "I: NodePathWrapper.loadFromData: no externalReference found in"
      print "  -",eggGroup
    BaseWrapper.loadFromData(self, eggGroup, filepath)

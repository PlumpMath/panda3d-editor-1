from core.modules.pBaseWrapper import *
from core.pModelController import modelController

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
        getModelPath().appendPath(pandaPath)
      
      # the path to the model we handle
      self.modelFilepath = modelFilepath
      # load the model
      self.model = loader.loadModel(filepath)
    
    # if the model loading fails or no path given, use a dummy object
    if self.model is None:
      print "W: NodePathWrapper.setModel: model could not be loaded, loading dummy"
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
    objectInstance = BaseWrapper.getSaveData(self, relativeTo)
    self.setExternalReference(self.modelFilepath, relativeTo, objectInstance)
    return objectInstance
  
  def loadFromData(self, eggGroup, filepath):
    extRefFilename = self.getExternalReference(eggGroup, filepath)
    self.setModel(extRefFilename)
    BaseWrapper.loadFromData(self, eggGroup, filepath)
  
  def makeCopy(self, original):
    objectInstance = super(NodePathWrapper, self).makeCopy(original)
    objectInstance.setModel(original.modelFilepath)
    return objectInstance
  makeCopy = classmethod(makeCopy)

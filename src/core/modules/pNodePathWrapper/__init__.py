__all__=['NodePathWrapper']

from pandac.PandaModules import *

from core.modules.pBaseWrapper import *
from core.pConfigDefs import *
from core.modules.pNodePathWrapper.pEggData import *
from core.modules.pNodePathWrapper.pEggGroup import *
from core.modules.pNodePathWrapper.pEggTexture import *
from core.modules.pNodePathWrapper.pEggVertexPool import *
from core.modules.pNodePathWrapper.pEggPolygon import *

DEBUG = False

def getEggDataEditable(parent, objectNode, modelFilepath):
  ''' Egg Data parser
  '''
  def recurse(parent, objectNode, eggParentData):
    ret = None
    if type(eggParentData) == EggData:
      subParent = ObjectEggData(parent, objectNode, eggParentData)
      for eggChildData in eggParentData.getChildren():
        recurse(subParent, objectNode, eggChildData)
      ret = subParent
    elif type(eggParentData) == EggGroup:
      subParent = ObjectEggGroup(parent, objectNode, eggParentData)
      for eggChildData in eggParentData.getChildren():
        recurse(subParent, objectNode, eggChildData)
      ret = subParent
    elif type(eggParentData) == EggPolygon:
      #ObjectEggPolygon(parent, objectNode, eggParentData)
      pass
    elif type(eggParentData) == EggTexture:
      ret = ObjectEggTexture(parent, objectNode, eggParentData)
    elif type(eggParentData) == EggVertexPool:
      ret = ObjectEggVertexPool(parent, objectNode, eggParentData)
    elif type(eggParentData) == EggComment:
      pass
    elif type(eggParentData) == EggExternalReference:
      pass
    elif type(eggParentData) == EggMaterial:
      pass
    else:
      print "core.pNodePathWrapper.bBase.getEditable: unknown type:", str(type(eggParentData))
    return ret
  
  eggData = EggData()
  eggData.read(Filename(modelFilepath))
  return recurse(parent, objectNode, eggData)

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
    
    # subnodes of this node
    self.eggTreeParent = None
  
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
      
      if self.isEditmodeEnabled():
        self.enableSubNodes()
    
    # if the model loading fails or no path given, use a dummy object
    if self.model is None:
      print "W: NodePathWrapper.setModel: model could not be loaded, loading dummy"
      self.model = loader.loadModel(MODEL_NOT_FOUND_MODEL)
    # make the model visible
    self.model.reparentTo(self.nodePath)
  
  def enableSubNodes(self):
    # create the children treeNodes of the nodepath
    if self.eggTreeParent is None:
      print "I: NodePathWrapper.enableSubNodes: creating child nodes"
      parent = self
      modelFilepath = self.modelFilepath
      node = self
      self.eggTreeParent = getEggDataEditable(parent, node, modelFilepath)
  
  def disableSubNodes(self):
    if self.eggTreeParent is not None:
      print "I: NodePathWrapper.disableSubNodes: destroying child nodes"
      self.eggTreeParent.destroy()
  
  def save(self, filepath):
    print "I: NodePathWrapper.save:", filepath
    if self.eggTreeParent:
      print "saving"
      self.eggTreeParent.save(filepath)
  
  def destroy(self):
    # destroy this object
    BaseWrapper.destroy(self)
    self.model.detachNode()
    self.model.removeNode()
  
  def setEditmodeEnabled(self, recurseException=[]):
    # if it was inactive before
    if not self.isEditmodeEnabled():
      self.nodePath.setCollideMask(DEFAULT_EDITOR_COLLIDEMASK)
      self.enableSubNodes()
    BaseWrapper.setEditmodeEnabled(self, recurseException)
  
  def setEditmodeDisabled(self, recurseException=[]):
    # if it was active before
    if self.isEditmodeEnabled():
      self.nodePath.setCollideMask(BitMask32.allOff())
      self.disableSubNodes()
    BaseWrapper.setEditmodeDisabled(self, recurseException)
  
  def startEdit(self):
    # the object is selected to be edited
    # creates a directFrame to edit this object
    BaseWrapper.startEdit(self)
    if self.isEditmodeEnabled():
      if self.highlightModel is None:
        self.highlightModel = self.model.copyTo(self.nodePath)
      self.highlightModel.setRenderModeWireframe(True)
      self.highlightModel.setLightOff(1000)
      self.highlightModel.setFogOff(1000)
      self.highlightModel.setTextureOff(1000)
      self.highlightModel.clearColorScale()
      self.highlightModel.setColor(HIGHLIGHT_COLOR[0], HIGHLIGHT_COLOR[1], HIGHLIGHT_COLOR[2], 1000)
      
  
  def stopEdit(self):
    # the object is deselected from being edited
    if self.isEditmodeEnabled():
      if self.highlightModel is not None:
        self.highlightModel.removeNode()
        self.highlightModel = None
    BaseWrapper.stopEdit(self)
  
  def getSaveData(self, relativeTo):
    objectInstance = BaseWrapper.getSaveData(self, relativeTo)
    self.setExternalReference(self.modelFilepath, relativeTo, objectInstance)
    return objectInstance
  
  def loadFromData(self, eggGroup, filepath):
    extRefFilename = self.getExternalReference(eggGroup, filepath)
    self.setModel(extRefFilename)
    BaseWrapper.loadFromData(self, eggGroup, filepath)
  
  def makeInstance(self, original):
    objectInstance = super(NodePathWrapper, self).makeInstance(original)
    objectInstance.setModel(original.modelFilepath)
    return objectInstance
  makeInstance = classmethod(makeInstance)
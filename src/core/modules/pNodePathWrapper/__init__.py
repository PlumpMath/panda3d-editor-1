__all__=['NodePathWrapper']

#import copy

from pandac.PandaModules import *

from core.modules.pBaseWrapper import *
from core.pConfigDefs import *
from core.modules.pNodePathWrapper.pObjectEggData import *
from core.modules.pNodePathWrapper.pObjectEggGroup import *
from core.modules.pNodePathWrapper.pObjectEggTexture import *
from core.modules.pNodePathWrapper.pObjectEggVertexPool import *
from core.modules.pNodePathWrapper.pObjectEggPolygon import *
from core.modules.pNodePathWrapper.pObjectEggPolygonGroup import *

DEBUG = False

def getEggDataEditable(parent, objectNode, modelFilepath):
  ''' Egg Data parser
  '''
  
  # the textures read from the polygons
  polygonTextures = dict()
  polygonTextures['all'] = list()
  # the textures found in the egg
  textures = dict()
  
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
      # store what texture is assigned to the polygon
      texList = eggParentData.getTextures()
      for tex in texList:
        if not tex in polygonTextures:
          polygonTextures[tex] = list()
        polygonTextures[tex].append(eggParentData)
      polygonTextures['all'].append(eggParentData)
    elif type(eggParentData) == EggTexture:
      ret = ObjectEggTexture(parent, objectNode, eggParentData)
      # store the textures we have
      textures[eggParentData] = ret
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
  newParent = recurse(parent, objectNode, eggData)
  
  print "--- model ---"
  print polygonTextures
  print textures
  print "--- done ---"
  i = 0
  for eggTex, texPolygons in polygonTextures.items():
    i += 1
    if eggTex in textures:
      # now we should create a polygon group, that is added to the objectEgg
      # so newly created textures may assign themself to this polygonGroup
      polyGroup = ObjectEggPolygonGroup(newParent, "polygonGroup-%i" % i)
      polyGroup.setPolygons(texPolygons)
      textures[eggTex].polygonGroup = polyGroup
    if eggTex == 'all':
      polyGroup = ObjectEggPolygonGroup(newParent, "polygonGroup-all")
      polyGroup.setPolygons(texPolygons)
      # define default polygon group
      parent.defaultPolygonGroup = polyGroup
    
  
  return newParent

class NodePathWrapper(BaseWrapper):
  className = 'Model'
  def onCreateInstance(self, parent, filepath):
    # create instance of this class
    if filepath is not None:
      name = filepath.split('/')[-1]
    else:
      name = 'NodePath'
    objectInstance = super(NodePathWrapper, self).onCreateInstance(parent, name)
    objectInstance.setModelFilepath(filepath)
    return objectInstance
  onCreateInstance = classmethod(onCreateInstance)
  
  def __init__(self, parent=None, name=None):
    BaseWrapper.__init__(self, parent, name)
    self.model = None
    
    # atm this type of node can have no new childrens
    #self.possibleChildren = []
    
    # content must be loaded using setModel
    # (done by onCreateInstance and loadFromEggGroup)
    
    # model used to show highlighting of this node
    self.highlightModel = None
    
    # the trigger can update the model, should not be saved into parameters
    self.mutableParameters['update'] = [ Trigger,
        None,
        self.updateModelFromEggData,
        None,
        None,
        False ]
    # this should actually not be saved into the parameters
    self.mutableParameters['model'] = [ Filepath,
        self.getModelFilepath,
        self.setModelFilepath,
        None,
        None,
        False ]
    
    # subnodes of this node
    self.eggTreeParent = None
  
  def getModelFilepath(self):
    return self.modelFilepath
  
  def setModelFilepath(self, modelFilepath):
    
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
      
      try:
        # load the model
        self.model = loader.loadModel(filepath)
      except:
        self.model = None
      
      if self.isEditmodeEnabled():
        self.enableSubNodes()
    
    if self.model is None:
      # if the model loading fails or no path given, use a dummy object
      print "W: NodePathWrapper.setModel: model could not be loaded, loading dummy"
      self.model = loader.loadModel(MODEL_NOT_FOUND_MODEL)
      # make the model visible
      self.model.reparentTo(self.getNodepath())
      # delete the filepath
      #self.clearFilepath()
    else:
      # store the full filepath of the model
      #self.setFilepath(filepath) # dont do that, in here, but in the egg-data
      
      if self.isEditmodeEnabled(): 
        # reread the model from the egg-data, this reloads the model when
        # editmode is enabled
        self.updateModelFromEggData()
      else:
        # parent the model to out nodepath
        self.model.reparentTo(self.getNodepath())
  
  # --- create the eggData subnodes for the nodepath ---
  def enableSubNodes(self):
    # create the children treeNodes of the nodepath
    if self.eggTreeParent is None:
      #print "I: NodePathWrapper.enableSubNodes: creating child nodes"
      parent = self
      modelFilepath = self.modelFilepath
      node = self
      self.eggTreeParent = getEggDataEditable(parent, node, modelFilepath)
    else:
      print "W: NodePathWrapper.enableSubNodes: eggTreeParent already created"
  
  def disableSubNodes(self):
    if self.eggTreeParent is not None:
      #print "I: NodePathWrapper.disableSubNodes: destroying child nodes"
      self.eggTreeParent.destroy()
    else:
      print "W: NodePathWrapper.disableSubNodes: eggTreeParent not created"
  # --- end create eggData ---
  
  # --- apply changes made in the eggData to the visuals ---
  def updateModelFromEggData(self, *args):
    # if there is already a model defined, remove it
    if self.model is not None:
      self.model.detachNode()
    
    egg = EggData()
    egg.read(StringStream(str(self.eggTreeParent.eggData)))
    self.model = NodePath(loadEggData(egg))
    self.model.reparentTo(self.getNodepath())
  # --- end apply changes ---
  
  def destroy(self):
    # destroy egg data
    def recurse(parent):
      for child in parent.getChildren()[:]: # accessing it directly causes it to miss childrens
        recurse(child)
        child.destroy()
    recurse(self.eggTreeParent)
    
    if self.model:
      loader.unloadModel(self.model)
    # destroy this object
    BaseWrapper.destroy(self)
    self.model.detachNode()
    self.model.removeNode()
  
  def setEditmodeEnabled(self):
    # if it was inactive before
    if not self.isEditmodeEnabled():
      self.getNodepath().setCollideMask(DEFAULT_EDITOR_COLLIDEMASK)
      self.enableSubNodes()
    BaseWrapper.setEditmodeEnabled(self)
  
  def setEditmodeDisabled(self):
    # if it was active before
    if self.isEditmodeEnabled():
      self.getNodepath().setCollideMask(BitMask32.allOff())
      self.disableSubNodes()
    BaseWrapper.setEditmodeDisabled(self)
  
  def startEdit(self):
    # the object is selected to be edited
    # creates a directFrame to edit this object
    BaseWrapper.startEdit(self)
    if self.isEditmodeEnabled():
      if self.highlightModel is None:
        self.highlightModel = self.model.copyTo(self.getNodepath())
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
    self.setModelFilepath(extRefFilename)
    BaseWrapper.loadFromData(self, eggGroup, filepath)
  
  def duplicate(self, original):
    objectInstance = super(NodePathWrapper, self).duplicate(original)
    objectInstance.setModelFilepath(original.modelFilepath)
    return objectInstance
  duplicate = classmethod(duplicate)
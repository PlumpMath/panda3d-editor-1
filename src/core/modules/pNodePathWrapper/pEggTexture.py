import posixpath

from pandac.PandaModules import *

from core.pTexturePainter import texturePainter
from core.pConfigDefs import * # imports Enum
from core.modules.pNodePathWrapper.pEggBase import *
from core.pCommonPath import relpath
from core.pEnums import *

class TextureLayer:
  ''' a texturelayer consists of a texture and a stage
  '''
  def __init__(self, texture=None, stage=None):
    self.texture = texture
    self.stage = stage

def getTextureLayers(nodePath):
  ''' return a TextureLayer object for each texture and stage that is found on
  a object '''
  def getStages(gnode, state, texStages): #, textures):
    for i in range(gnode.getNumGeoms()):
      gstate = state.compose(gnode.getGeomState(i))
      if hasattr(TextureAttrib, 'getClassSlot'): # 1.6 uses getClassSlot
        attrib = gstate.getAttrib(TextureAttrib.getClassSlot())
      elif hasattr(TextureAttrib, 'getClassType'): # 1.5.4 uses getClassType
        attrib = gstate.getAttrib(TextureAttrib.getClassType())
      else:
        print "E: getTextureLayers.getStages: cannot read attrib"
        return texStages
      if attrib != None:
        for j in range(attrib.getNumOnStages()):
          texStage = attrib.getOnStage(j)
          texture = attrib.getTexture()
          if (texStage not in texStages) or (texture not in textures):
            texStages.append(TextureLayer(stage=texStage, texture=texture))
    return texStages
  
  def rec(parent, state, texStages):
    print "I: getTextureLayers.rec:", type(parent)
    # in 1.5.4 the parent type nodepathcollection has no getChildren
    # type(parent) allways yields nodepath, so i must use try/except
    try:
      for child in parent.getChildren():
        texStages = rec(child, state, texStages)
        if child.node().isGeomNode():
          texStages = getStages(child.node(), state, texStages)
    except:
      for child in parent.getChildrenAsList():
        texStages = rec(child, state, texStages)
        if child.node().isGeomNode():
          texStages = getStages(child.node(), state, texStages)
    return texStages
  
  texStages = rec(nodePath, nodePath.getNetState(), [])
  return texStages


class ObjectEggTexture(ObjectEggBase):
  ''' when entering the texture editing mode, the model should be reparented to
  some other node, if some parent node texture overrides the local textures,
  it cant find the original ones anymore '''
  className = 'EggTexture'
  def __init__(self, parent, modelWrapper, eggTexture):
    ObjectEggBase.__init__(self, parent, modelWrapper, 'EggTexture')
    self.eggTexture = eggTexture
    self.possibleFunctions = ['save', 'saveAs', 'revert']
    
    self.mutableParameters['texture filename'] = [ P3Filepath,
        self.eggTexture.getFilename,
        self.setTexture,
        None,
        None,
        False ]
    
    '''self.mutableParameters['combine mode'] = [ EggTexture_CombineMode_Enum,
      self.eggTexture.getCombineMode,
      self.eggTexture.setCombineMode,
      None,
      None ]'''
    self.mutableParameters['env type'] = [ EggTexture_EnvType_Enum,
        self.eggTexture.getEnvType,
        self.eggTexture.setEnvType,
        None,
        None,
        False ]
    self.mutableParameters['u wrap mode'] = [ EggTexture_WrapMode_Enum,
        self.eggTexture.getWrapU,
        self.eggTexture.setWrapU,
        None,
        None,
        False ]
    self.mutableParameters['v wrap mode'] = [ EggTexture_WrapMode_Enum,
        self.eggTexture.getWrapV,
        self.eggTexture.setWrapV,
        None,
        None,
        False ]
    self.mutableParameters['w wrap mode'] = [ EggTexture_WrapMode_Enum,
        self.eggTexture.getWrapW,
        self.eggTexture.setWrapW,
        None,
        None,
        False ]
    self.mutableParameters['min filter'] = [ EggTexture_Min_FilterType_Enum,
        self.eggTexture.getMinfilter,
        self.eggTexture.setMinfilter,
        None,
        None,
        False ]
    self.mutableParameters['mag filter'] = [ EggTexture_Mag_FilterType_Enum,
        self.eggTexture.getMagfilter,
        self.eggTexture.setMagfilter,
        None,
        None,
        False ]
    
    self.editTexture = None
    self.editTextureFilename = None
  
  def setTexture(self, filename):
    assert(type(filename) == Filename)
    filename = filename.getFullpath()
    if filename:
      if filename[0] == '/':
        relativePath = posixpath.dirname(self.getParentFilepath())
        filename = relpath(relativePath, posixpath.abspath(filename))
    print "I: ObjectEggTexture.setTexture:", filename
    self.eggTexture.setFilename(Filename(filename))
    # update the visual model
    self.modelWrapper.updateModelFromEggData()
  
  def destroy(self):
    print "I: ObjectEggTexture.destroy"
    self.stopEdit()
    ObjectEggBase.destroy(self)
    self.eggTexture = None
    self.modelWrapper = None
    
    # TODO RELEASE OF TEXTURES DOESNT WORK YET
    if self.editTexture:
      print "  - release texture", self.editTextureFilename
      TexturePool.releaseTexture(self.editTexture)
    TexturePool.releaseAllTextures()
    
    self.editTexture = None
    self.editTextureFilename = None
  
  def startEdit(self):
    ''' as we are editing a egg-file, but for texture painting we modify a texture
    on the model, we need to find the corresponding texture's from the 3dmodel and
    the eggdata
    if we find it we start modifying it
    WARNING: the current implementation may select the wrong texture to edit
    if the filename of a texture is equal, but in different subdirectories
    '''
    if ObjectEggBase.isEditmodeEnabled(self):
      ObjectEggBase.startEdit(self)
      print "I: ObjectEggTexture.startEdit"
      # search for the corresponding nodepath-texture in the egg-file
      eggTextureFilename = str(self.eggTexture.getFilename()).lstrip('./')
      # the texture we will modify
      editTexture = None
      modelTextureLayers = getTextureLayers(self.modelWrapper.model)
      for modelTexLayer in modelTextureLayers:
        modelTexFilename = str(modelTexLayer.texture.getFullpath())
        if eggTextureFilename in modelTexFilename:
          editTexture = modelTexLayer.texture
      if editTexture:
        print "I: ObjectEggTexture.startEdit: start editing texture", eggTextureFilename
        print "  - selected from these: ", [tex.texture.getFullpath() for tex in modelTextureLayers]
        #texturePainter.selectPaintModel()
        self.editTexture = editTexture
        self.editTextureFilename = tex.texture.getFullpath()
        texturePainter.enableEditor()
        texturePainter.startEditor(self.modelWrapper.model, editTexture)
        #texturePainter.startEdit()
      else:
        print "I: ObjectEggTexture.startEdit: texture not found", eggTextureFilename
        print "  - fullpath", [tex.texture.getFullpath() for tex in modelTextureLayers]
        print "  - filename", [tex.texture.getFilename() for tex in modelTextureLayers]
    else:
      print "W: ObjectEggTexture.startEdit: editmode not enabled"
  
  def stopEdit(self):
    if ObjectEggBase.isEditmodeEnabled(self):
      ObjectEggBase.stopEdit(self)
      texturePainter.stopEditor()
      texturePainter.disableEditor()
    else:
      print "W: ObjectEggTexture.stopEdit: editmode not enabled"
  
  def revert(self):
    #TextureManager.release(self.editTextureFilename)
    self.stopEdit()
    #self.setTexture(self.editTextureFilename)
    #loader.unloadTexture(self.eggTexture.getFilename())
    #Texture.reload(self.eggTexture.getFilename())
    TexturePool.releaseTexture(self.editTexture)
    self.editTexture.reload()
    self.startEdit()
  
  def save(self):
    self.saveAs(self.editTextureFilename)
  
  def saveAs(self, filename):
    print "I: ObjectEggTexture.saveAs:", filename
    if self.editTexture:
      saveTex = PNMImage()
      self.editTexture.store(saveTex)
      saveTex.write(Filename(filename))

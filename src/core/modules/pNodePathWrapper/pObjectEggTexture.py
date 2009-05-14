# ------------------------------------------------------------------------------
# Copyright (c) 2009, Reto Spoerri
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name of the <ORGANIZATION> nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.
# ------------------------------------------------------------------------------

import posixpath

from pandac.PandaModules import *

from core.pTexturePainter import texturePainter
from core.pConfigDefs import * # imports Enum
from core.modules.pNodePathWrapper.pObjectEggBase import *
from core.pCommonPath import relpath
from core.pEnums import *
from core.pTreeNode import *
from core.modules.pNodePathWrapper.pObjectEggPolygonGroup import *

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
  def onCreateInstance(self, parent):
    # create instance of this class
    '''if filepath is not None:
      name = filepath.split('/')[-1]
    else:
      name = 'EggTexture'
    '''
    print dir(parent), type(parent)
    modelWrapper = parent.modelWrapper
    
    # the default texture
    relativePath = posixpath.dirname(parent.getParentFilepath())
    defaultTexturePath = relpath(relativePath, 'data/grid.png')
    
    eggTexture = EggTexture('texture', defaultTexturePath)
    eggTexture.setName('texture-%i' % hash(eggTexture))
    #print "I: ObjectEggTexture.onCreateInstance:"
    #print "  - parent:", parent
    #print "  - name:", eggTexture.getName()
    
    # we need to insert the texture at the beginning...
    origChildrens = parent.eggData.getChildren()
    parent.eggData.addChild(eggTexture)
    for c in origChildrens:
      parent.eggData.removeChild(c)
      parent.eggData.addChild(c)
    #for parent.eggData
    #print "  - parent.eggData:"
    print parent.eggData
    objectInstance = ObjectEggTexture(parent, modelWrapper, eggTexture)
    objectInstance.setPolygonGroup(parent.defaultPolygonGroup)
    
    return objectInstance
  onCreateInstance = classmethod(onCreateInstance)
  
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
    
    self.mutableParameters['env type'] = [ EggTexture_EnvType_Enum,
        self.getEnvType,
        self.setEnvType,
        None,
        None,
        False ]
    
    self.mutableParameters['combine mode'] = [ EggTexture_CombineMode_Enum,
        self.getCombineMode_Mode,
        self.setCombineMode_Mode,
        None,
        None,
        False ]
    self.mutableParameters['c. mode channel'] = [ EggTexture_CombineChannel_Enum,
        self.getCombineMode_Channel,
        self.setCombineMode_Channel,
        None,
        None,
        False ]
    self.combineMode_Mode = None
    self.combineMode_Channel = EggTexture.CCRgb # assuming something
    
    self.mutableParameters['combine operand'] = [ EggTexture_CombineOperand_Enum,
        self.getCombineOperand_Operand,
        self.setCombineOperand_Operand,
        None,
        None,
        False ]
    self.mutableParameters['c. operand channel'] = [ EggTexture_CombineChannel_Enum,
        self.getCombineOperand_Channel,
        self.setCombineOperand_Channel,
        None,
        None,
        False ]
    self.mutableParameters['c. operand number'] = [ int,
        self.getCombineOperand_Number,
        self.setCombineOperand_Number,
        None,
        None,
        False ]
    self.combineOperand_Number = 0
    self.combineOperand_Operand = None
    self.combineOperand_Channel = EggTexture.CCRgb # assuming something
    
    self.mutableParameters['combine source'] = [ EggTexture_CombineSource_Enum,
        self.getCombineSource_Source,
        self.setCombineSource_Source,
        None,
        None,
        False ]
    self.mutableParameters['c. Source channel'] = [ EggTexture_CombineChannel_Enum,
        self.getCombineSource_Channel,
        self.setCombineSource_Channel,
        None,
        None,
        False ]
    self.mutableParameters['c. source number'] = [ int,
        self.getCombineSource_Number,
        self.setCombineSource_Number,
        None,
        None,
        False ]
    self.combineSource_Number = 0
    self.combineSource_Source = None
    self.combineSource_Channel = EggTexture.CCRgb # assuming something
    
    self.mutableParameters['u wrap mode'] = [ EggTexture_WrapMode_Enum,
        self.getWrapU,
        self.setWrapU,
        None,
        None,
        False ]
    self.mutableParameters['v wrap mode'] = [ EggTexture_WrapMode_Enum,
        self.getWrapV,
        self.setWrapV,
        None,
        None,
        False ]
    '''
    # dont use 3d textures
    self.mutableParameters['w wrap mode'] = [ EggTexture_WrapMode_Enum,
        self.getWrapW,
        self.setWrapW,
        None,
        None,
        False ]
    '''
    self.mutableParameters['min filter'] = [ EggTexture_Min_FilterType_Enum,
        self.getMinfilter,
        self.setMinfilter,
        None,
        None,
        False ]
    self.mutableParameters['mag filter'] = [ EggTexture_Mag_FilterType_Enum,
        self.getMagfilter,
        self.setMagfilter,
        None,
        None,
        False ]
    '''
    # doesnt exist in eggTexture
    self.mutableParameters['sort'] = [ int,
        self.getSort,
        self.setSort,
        None,
        None,
        False ]
    '''
    
    self.polygonGroup = None
    self.mutableParameters['polygonGroup'] = [ TreeNode,
        self.getPolygonGroup,
        self.setPolygonGroup,
        None,
        None,
        False
    ]
    
    self.editTexture = None
    self.editTextureFilename = None
  
  def setPolygonGroup(self, polygonGroup):
    if type(polygonGroup) != ObjectEggPolygonGroup:
      print "I: ObjectEggTexture.setPolygonGroup: invalid polygonGroup", polygonGroup
      return
    if self.polygonGroup is not None:
      self.polygonGroup.removeTexture(self.eggTexture)
    # define new polygonGroup
    self.polygonGroup = polygonGroup
    if self.polygonGroup is not None:
      self.polygonGroup.addTexture(self.eggTexture)
    # update the visual model
    self.stopEdit()
    self.modelWrapper.updateModelFromEggData()
    print self.modelWrapper.eggTreeParent.eggData
    self.startEdit()
  def getPolygonGroup(self):
    return self.polygonGroup
  
  def getEnvType(self):
    return self.eggTexture.getEnvType()
  def setEnvType(self, envType):
    self.eggTexture.setEnvType(envType)
    # update the visual model
    self.stopEdit()
    self.modelWrapper.updateModelFromEggData()
    self.startEdit()
  
  def getCombineMode_Mode(self):
    return self.eggTexture.getCombineMode(self.combineMode_Channel)
  def setCombineMode_Mode(self, combineMode):
    self.combineMode_Mode = combineMode
    self.updateCombineMode()
  def getCombineMode_Channel(self):
    return self.combineMode_Channel
  def setCombineMode_Channel(self, combineChannel):
    self.combineMode_Channel = combineChannel
    self.updateCombineMode()
  def updateCombineMode(self):
    print "I: ObjectEggTexture.updateCombineMode:", self.combineMode_Channel, self.combineMode_Mode
    self.eggTexture.setCombineMode(self.combineMode_Channel, self.combineMode_Mode)
    # update the visual model
    self.stopEdit()
    self.modelWrapper.updateModelFromEggData()
    self.startEdit()
  
  def getCombineOperand_Operand(self):
    return self.eggTexture.getCombineOperand(self.combineOperand_Channel, self.combineOperand_Number)
  def setCombineOperand_Operand(self, combineOperand):
    self.combineOperand_Operand = combineOperand
    self.updateCombineOperand()
  def getCombineOperand_Channel(self):
    return self.combineOperand_Channel
  def setCombineOperand_Channel(self, combineChannel):
    self.combineOperand_Channel = combineChannel
    self.updateCombineOperand()
  def setCombineOperand_Number(self, combineNumber):
    self.combineOperand_Number = combineNumber
  def getCombineOperand_Number(self):
    return self.combineOperand_Number
  def updateCombineOperand(self):
    print "I: ObjectEggTexture.updateCombineOperand:", self.combineOperand_Channel, self.combineOperand_Operand
    self.eggTexture.setCombineOperand(self.combineOperand_Channel, self.combineOperand_Number, self.combineOperand_Operand)
    # update the visual model
    self.stopEdit()
    self.modelWrapper.updateModelFromEggData()
    self.startEdit()
  
  def getCombineSource_Source(self):
    return self.eggTexture.getCombineSource(self.combineSource_Channel, self.combineSource_Number)
  def setCombineSource_Source(self, combineSource):
    self.combineSource_Source = combineSource
    self.updateCombineSource()
  def getCombineSource_Channel(self):
    return self.combineSource_Channel
  def setCombineSource_Channel(self, combineChannel):
    self.combineSource_Channel = combineChannel
    self.updateCombineSource()
  def setCombineSource_Number(self, combineNumber):
    self.combineSource_Number = combineNumber
  def getCombineSource_Number(self):
    return self.combineSource_Number
  def updateCombineSource(self):
    print "I: ObjectEggTexture.updateCombineSource:", self.combineSource_Channel, self.combineSource_Source
    self.eggTexture.setCombineSource(self.combineSource_Channel, self.combineSource_Number, self.combineSource_Source)
    # update the visual model
    self.stopEdit()
    self.modelWrapper.updateModelFromEggData()
    self.startEdit()
  
  def getWrapU(self):
    return self.eggTexture.getWrapU()
  def setWrapU(self, wrapU):
    self.eggTexture.setWrapU(wrapU)
    # update the visual model
    self.stopEdit()
    self.modelWrapper.updateModelFromEggData()
    self.startEdit()
  
  def getWrapV(self):
    return self.eggTexture.getWrapV()
  def setWrapV(self, wrapV):
    self.eggTexture.setWrapV(wrapV)
    # update the visual model
    self.stopEdit()
    self.modelWrapper.updateModelFromEggData()
    self.startEdit()
  
  '''
  # dont allow 3d textures
  def getWrapW(self):
    return self.eggTexture.getWrapW()
  def setWrapW(self, wrapW):
    self.eggTexture.setWrapW(wrapW) #EggTexture_WrapMode_Enum[wrapW])
    # update the visual model
    self.modelWrapper.updateModelFromEggData()
  '''
  
  def getMinfilter(self):
    return self.eggTexture.getMinfilter()
  def setMinfilter(self, minFilter):
    self.eggTexture.setMinfilter(minFilter)
    # update the visual model
    self.stopEdit()
    self.modelWrapper.updateModelFromEggData()
    self.startEdit()
  
  def getMagfilter(self):
    return self.eggTexture.getMagfilter()
  def setMagfilter(self, magFilter):
    self.eggTexture.setMagfilter(magFilter)
    # update the visual model
    self.stopEdit()
    self.modelWrapper.updateModelFromEggData()
    self.startEdit()
  
  '''
  # doesnt exist...
  def getSort(self):
    return self.eggTexture.getSort()
  def setSort(self, sort):
    # sort must be minimum 0
    sort = max(0,sort)
    self.eggTexture.setSort(sort)
    # update the visual model
    self.stopEdit()
    self.modelWrapper.updateModelFromEggData()
    self.startEdit()
  '''
  
  def setTexture(self, filename):
    assert(type(filename) == Filename)
    filename = filename.getFullpath()
    print "I: ObjectEggTexture.setTexture:"
    print "  - filename:   ", filename
    print "  - parentpath: ", self.getParentFilepath()
    if filename:
      if filename[0] == '/':
        relativePath = posixpath.dirname(self.getParentFilepath())
        print "  -", relativePath
        filename = posixpath.abspath(filename)
        print "  -", filename
        filename = relpath(relativePath, filename)
    print "I: ObjectEggTexture.setTexture:", filename
    self.eggTexture.setFilename(Filename(filename))
    # update the visual model
    self.stopEdit()
    self.modelWrapper.updateModelFromEggData()
    self.startEdit()
  
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

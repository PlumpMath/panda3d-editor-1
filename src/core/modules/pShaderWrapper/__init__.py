__all__=['ShaderWrapper']

import traceback, posixpath

from pandac.PandaModules import *

from core.pModelIdManager import modelIdManager
from core.pCommonPath import relpath
from core.pConfigDefs import *
#from core.pTreeNode import *
from core.modules.pBaseWrapper import *
from core.pTexturePainter import texturePainter

from terrainShader import ShaderNode

class ShaderWrapper(BaseWrapper):
  def onCreateInstance(self, parent, name='ShaderWrapper'):
    # create instance of this class
    objectInstance = self(parent, name)
    objectInstance.setUpdateShader()
    return objectInstance
  onCreateInstance = classmethod(onCreateInstance)
  
  '''def loadFromEggGroup(self, eggGroup, parent, filepath):
    name = eggGroup.getName()
    objectInstance = self(parent, name)
    objectInstance.updateShader()
    return objectInstance
  loadFromEggGroup = classmethod(loadFromEggGroup)'''
  
  def __init__(self, parent, name):
    # define a name for this object
    BaseWrapper.__init__(self, parent, name)
    #BaseWrapper.reparentTo(self, parent)
    
    # all values that can be changed require a entry in the mutableParameters
    
    # when a value exists, it means that it's allowed to read/write the value
    # hasFunc defines if it's a vital property of the object and must be saved
    # into the comments
    
    # valueType, getFunc vtion, setFunction, hasFunction, clearFunction, saveToComments
    # hasFunction == None -> the value should be saved
    self.mutableParameters = dict()
    self.mutableParameters['mixmap'] = [ Filepath,
      self.getTex1,
      self.setTex1,
      None,
      self.clearTex1 ]
    self.mutableParameters['detailmap1'] = [ Filepath,
      self.getTex2,
      self.setTex2,
      None,
      self.clearTex2 ]
    self.mutableParameters['tex1scale'] = [ float,
      self.getTex2Scale,
      self.setTex2Scale,
      None,
      None ]
    self.mutableParameters['detailmap2'] = [ Filepath,
      self.getTex3,
      self.setTex3,
      None,
      self.clearTex3 ]
    self.mutableParameters['tex2scale'] = [ float,
      self.getTex3Scale,
      self.setTex3Scale,
      None,
      None ]
    self.mutableParameters['detailmap3'] = [ Filepath,
      self.getTex4,
      self.setTex4,
      None,
      self.clearTex4 ]
    self.mutableParameters['tex3scale'] = [ float,
      self.getTex4Scale,
      self.setTex4Scale,
      None,
      None ]
    self.mutableParameters['update'] = [ Trigger,
      self.getUpdateShader,
      self.setUpdateShader,
      None,
      None ]
    self.mutableParameters['paintColor'] = [ Vec4,
      self.getPaintColor,
      self.setPaintColor,
      None,
      None]
    self.mutableParameters['paintSize'] = [ float,
      self.getPaintSize,
      self.setPaintSize,
      None,
      None]
    
    self.tex1Path = Filepath('')
    self.tex2Path = Filepath('')
    self.tex3Path = Filepath('')
    self.tex4Path = Filepath('')
    self.tex2Scale = 1
    self.tex3Scale = 1
    self.tex4Scale = 1
    self.paintColor = Vec4(1,1,1,1)
    self.paintSize = 7
    
    self.relativePath = None
    self.shader = None
    self.paintActive = False
  
  def getUpdateShader(self):
    ''' this is just a dummy because i need a get&setFunc '''
    pass
  
  def setUpdateShader(self, *args):
    print "I: ShaderWrapper.updateShader:"
    if self.shader:
      self.shader.destroy()
      self.shader = None
    
    if self.shader is None:
      self.shader = ShaderNode(self.nodePath)
      
      if self.relativePath is None:
        # read the filepath of this node
        def recGetParent(treeNode):
          parent = treeNode.getParent()
          print "recGetParent", parent
          if parent:
            return recGetParent(parent)
          else:
            return treeNode
        topParent = recGetParent(self)
        self.relativePath = topParent.relativePath
        print "I: ShaderWrapper.updateShader: updateing relativePath", self.relativePath
      
      if self.tex1Path:
        tex1Path = posixpath.join(self.relativePath, self.tex1Path)
        print "  - tex1", tex1Path
        if self.tex2Path:
          tex2Path = posixpath.join(self.relativePath, self.tex2Path)
          print "  - tex2", tex2Path, self.tex2Scale
          self.shader.AddAlphaMap(tex2Path, tex1Path, alphamapchannel = "r", texscale = self.tex2Scale)
        if self.tex3Path:
          tex3Path = posixpath.join(self.relativePath, self.tex3Path)
          print "  - tex3", tex3Path, self.tex3Scale
          self.shader.AddAlphaMap(tex3Path, tex1Path, alphamapchannel = "g", texscale = self.tex3Scale)
        if self.tex4Path:
          tex4Path = posixpath.join(self.relativePath, self.tex4Path)
          print "  - tex4", tex4Path, self.tex4Scale
          self.shader.AddAlphaMap(tex4Path, tex1Path, alphamapchannel = "b", texscale = self.tex4Scale)
        self.shader.Initialize()
      
      if self.isEditmodeEnabled():
        self.startPaint()
  
  def loadFromData(self, eggGroup, filepath):
    # read the relative path we load the file from
    print "I: ShaderWrapper.loadFromData: filepath", filepath
    self.relativePath = filepath
    BaseWrapper.loadFromData(self, eggGroup, filepath)
    self.setUpdateShader()
  
  def startEdit(self):
    print "I: ShaderWrapper.startEdit:", self.isEditmodeEnabled()
    # the object is selected to be edited
    # creates a directFrame to edit this object
    if self.isEditmodeEnabled():
      print "E: ShaderWrapper.startEdit: object is not in editmode", self
      messenger.send(EVENT_SCENEPICKER_MODELSELECTION_DISABLE)
      
      if self.tex1Path:
        #print "I: ObjectEggTexture.startEdit: editing texture", texture
        self.startPaint()
  
  def startPaint(self):
    if not self.paintActive:
      texturePainter.selectPaintModel(self.nodePath)
      texturePainter.enableEditor()
      paintTex = self.shader.loadedMaps[posixpath.join(self.relativePath, self.tex1Path)]
      texturePainter.startEdit(paintTex)
      self.paintActive = True
  
  def stopEdit(self):
    # the object is deselected from being edited
    print "I: ShaderWrapper.stopEdit:", self.isEditmodeEnabled()
    messenger.send(EVENT_SCENEPICKER_MODELSELECTION_ENABLE)
  
  def stopPaint(self):
    if self.paintActive:
      texturePainter.stopEdit()
      texturePainter.disableEditor()
      self.paintActive = False
  
  def destroy(self):
    self.stopEdit()
    self.setEditmodeDisabled()
    BaseWrapper.destroy(self)
  
  def setTex1(self, texPath):
    if texPath[0] == '/':
      texPath = relpath(self.relativePath, posixpath.abspath(texPath))
    self.tex1Path = Filepath(texPath)
  def getTex1(self):
    return self.tex1Path
  def clearTex1(self):
    self.tex1Path = None
  
  def setTex2(self, texPath):
    if texPath[0] == '/':
      texPath = relpath(self.relativePath, posixpath.abspath(texPath))
    self.tex2Path = Filepath(texPath)
  def getTex2(self):
    return self.tex2Path
  def clearTex2(self):
    self.tex2Path = None
  
  def setTex3(self, texPath):
    if texPath[0] == '/':
      texPath = relpath(self.relativePath, posixpath.abspath(texPath))
    self.tex3Path = Filepath(texPath)
  def getTex3(self):
    return self.tex3Path
  def clearTex3(self):
    self.tex3Path = None
  
  def setTex4(self, texPath):
    if texPath[0] == '/':
      texPath = relpath(self.relativePath, posixpath.abspath(texPath))
    self.tex4Path = Filepath(texPath)
  def getTex4(self):
    return self.tex4Path
  def clearTex4(self):
    self.tex4Path = None
  
  def getTex2Scale(self):
    return self.tex2Scale
  def setTex2Scale(self, scale):
    self.tex2Scale = scale
  
  def getTex3Scale(self):
    return self.tex3Scale
  def setTex3Scale(self, scale):
    self.tex3Scale = scale
  
  def getTex4Scale(self):
    return self.tex4Scale
  def setTex4Scale(self, scale):
    self.tex4Scale = scale
  
  def getPaintColor(self):
    return self.paintColor
  def setPaintColor(self, color):
    self.paintColor = color
    col = VBase4D(self.paintColor[0], self.paintColor[1], self.paintColor[2], self.paintColor[3])
    texturePainter.setBrush(col, self.paintSize)
  
  def getPaintSize(self):
    return self.paintSize
  def setPaintSize(self, size):
    self.paintSize=size
    col = VBase4D(self.paintColor[0], self.paintColor[1], self.paintColor[2], self.paintColor[3])
    texturePainter.setBrush(col, self.paintSize)
__all__=['ShaderWrapper']

import traceback, posixpath

from pandac.PandaModules import *

from core.pModelIdManager import modelIdManager
from core.pCommonPath import relpath
from core.pConfigDefs import *
#from core.pTreeNode import *
from core.modules.pBaseWrapper import *

from terrainShader import ShaderNode

class ShaderWrapper(BaseWrapper):
  def onCreateInstance(self, parent, name='ShaderWrapper'):
    # create instance of this class
    objectInstance = self(parent, name)
    objectInstance.updateShader()
    return objectInstance
  onCreateInstance = classmethod(onCreateInstance)
  
  def loadFromEggGroup(self, eggGroup, parent, filepath):
    name = eggGroup.getName()
    objectInstance = self(parent, name)
    return objectInstance
  loadFromEggGroup = classmethod(loadFromEggGroup)
  
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
    self.mutableParameters['detailmap2'] = [ Filepath,
      self.getTex3,
      self.setTex3,
      None,
      self.clearTex3 ]
    self.mutableParameters['detailmap3'] = [ Filepath,
      self.getTex4,
      self.setTex4,
      None,
      self.clearTex4 ]
    self.mutableParameters['update'] = [ Trigger,
      self.updateShader,
      self.updateShader,
      None,
      None ]
    
    self.tex1Path = Filepath('')
    self.tex2Path = Filepath('')
    self.tex3Path = Filepath('')
    self.tex4Path = Filepath('')
    
    self.relativePath = None
    self.shader = None
  
  def updateShader(self):
    self.shader.destroy()
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
      if self.tex2Path:
        tex2Path = posixpath.join(self.relativePath, self.tex2Path)
        self.shader.AddAlphaMap(tex2Path, tex1Path, alphamapchannel = "r", texscale = 5)
      if self.tex3Path:
        tex3Path = posixpath.join(self.relativePath, self.tex3Path)
        self.shader.AddAlphaMap(tex3Path, tex1Path, alphamapchannel = "g", texscale = 5)
      if self.tex4Path:
        tex4Path = posixpath.join(self.relativePath, self.tex4Path)
        self.shader.AddAlphaMap(tex4Path, tex1Path, alphamapchannel = "b", texscale = 50)
      self.shader.Initialize()
  
  def loadFromData(self, eggGroup, filepath):
    # read the relative path we load the file from
    print "I: ShaderWrapper.loadFromData: filepath", filepath
    self.relativePath = filepath
    BaseWrapper.loadFromData(self, eggGroup, filepath)
  
  def startEdit(self):
    # the object is selected to be edited
    # creates a directFrame to edit this object
    if not self.isEditmodeEnabled():
      print "E: core.BaseWrapper.startEdit: object is not in editmode", self
  
  def stopEdit(self):
    # the object is deselected from being edited
    if not self.isEditmodeEnabled():
      print "E: core.BaseWrapper.stopEdit: object is not in editmode", self
  
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

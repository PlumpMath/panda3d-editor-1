__all__=['ShaderWrapper']

import traceback, posixpath

from pandac.PandaModules import *

from core.pModelIdManager import modelIdManager
from core.pCommonPath import relpath
from core.pConfigDefs import *
from core.pTreeNode import *

class ShaderWrapper(TreeNode):
  def onCreateInstance(self, parent, name='ShaderWrapper'):
    # create instance of this class
    objectInstance = self(parent, name)
    return objectInstance
  onCreateInstance = classmethod(onCreateInstance)
  
  def loadFromEggGroup(self, eggGroup, parent, filepath):
    name = eggGroup.getName()
    objectInstance = self(parent, name)
    return objectInstance
  loadFromEggGroup = classmethod(loadFromEggGroup)
  
  def __init__(self, parent, name):
    # define a name for this object
    TreeNode.__init__(self, name, self)
    TreeNode.reparentTo(self, parent)
    
    # all values that can be changed require a entry in the mutableParameters
    
    # when a value exists, it means that it's allowed to read/write the value
    # hasFunc defines if it's a vital property of the object and must be saved
    # into the comments
    
    # valueType, getFunc vtion, setFunction, hasFunction, clearFunction, saveToComments
    # hasFunction == None -> the value should be saved
    self.mutableParameters = dict()
    self.mutableParameters['texture1'] = [ Filepath,
      self.getTex1,
      self.setTex1,
      None,
      self.clearTex1 ]
    self.mutableParameters['texture2'] = [ Filepath,
      self.getTex2,
      self.setTex2,
      None,
      self.clearTex2 ]
    self.mutableParameters['texture3'] = [ Filepath,
      self.getTex3,
      self.setTex3,
      None,
      self.clearTex3 ]
    self.mutableParameters['texture4'] = [ Filepath,
      self.getTex4,
      self.setTex4,
      None,
      self.clearTex4 ]
    
    self.tex1Path = Filepath('')
    self.tex2Path = Filepath('')
    self.tex3Path = Filepath('')
    self.tex4Path = Filepath('')
    
    # just testing
    def recGetParent(treeNode):
      parent = treeNode.getParent()
      print "recGetParent", parent
      if parent:
        return recGetParent(parent)
      else:
        return treeNode
    topParent = recGetParent(self)
    self.relativePath = topParent.relativePath
  
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
    TreeNode.destroy(self)
  
  def setTex1(self, texPath):
    relativePath = relpath(self.relativePath, posixpath.abspath(texPath))
    self.tex1Path = Filepath(relativePath)
  def getTex1(self):
    return self.tex1Path
  def clearTex1(self):
    pass
  
  def setTex2(self, texPath):
    relativePath = relpath(self.relativePath, posixpath.abspath(texPath))
    self.tex2Path = Filepath(relativePath)
  def getTex2(self):
    return self.tex2Path
  def clearTex2(self):
    pass
  
  def setTex3(self, texPath):
    relativePath = relpath(self.relativePath, posixpath.abspath(texPath))
    self.tex3Path = Filepath(relativePath)
  def getTex3(self):
    return self.tex3Path
  def clearTex3(self):
    pass
  
  def setTex4(self, texPath):
    relativePath = relpath(self.relativePath, posixpath.abspath(texPath))
    self.tex4Path = Filepath(relativePath)
  def getTex4(self):
    return self.tex4Path
  def clearTex4(self):
    pass

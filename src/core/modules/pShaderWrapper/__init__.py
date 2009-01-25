__all__=['ShaderWrapper']

import traceback, posixpath

from pandac.PandaModules import *

from core.pModelIdManager import modelIdManager
from core.pCommonPath import relpath
from core.pConfigDefs import *
#from core.pTreeNode import *
from core.modules.pBaseWrapper import *
from core.pTexturePainter import texturePainter, PNMBrush_BrushEffect_Enum
from core.modules.pNodePathWrapper.pEggTexture import Texture_Mag_FilterType_Enum, Texture_Min_FilterType_Enum

from terrainShader import ShaderNode

class ShaderWrapper(BaseWrapper):
  className = 'TerrainShader'
  def onCreateInstance(self, parent, name='ShaderWrapper'):
    # create instance of this class
    objectInstance = self(parent, name)
    objectInstance.setUpdateShader()
    return objectInstance
  onCreateInstance = classmethod(onCreateInstance)
  
  '''def loadFromEggGroup(self, eggGroup, parent, filepath):
    name = eggGroup.getName()
    objectInstance = self(parent, name)
    objectInstance.setUpdateShader()
    return objectInstance
  loadFromEggGroup = classmethod(loadFromEggGroup)'''
  
  def __init__(self, parent, name):
    # define a name for this object
    BaseWrapper.__init__(self, parent, name)
    #BaseWrapper.reparentTo(self, parent)
    
    self.possibleFunctions = ['save']
    # all values that can be changed require a entry in the mutableParameters
    
    # when a value exists, it means that it's allowed to read/write the value
    # hasFunc defines if it's a vital property of the object and must be saved
    # into the comments
    
    # valueType, getFunc vtion, setFunction, hasFunction, clearFunction, saveToComments
    # hasFunction == None -> the value should be saved
    #self.mutableParameters = dict()
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
    self.mutableParameters['tex1 mag filter'] = [ Texture_Mag_FilterType_Enum,
      self.getTex2MagFiltertype,
      self.setTex2MagFiltertype,
      None,
      None ]
    self.mutableParameters['tex1 min filter'] = [ Texture_Min_FilterType_Enum,
      self.getTex2MinFiltertype,
      self.setTex2MinFiltertype,
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
    self.mutableParameters['tex2 mag filter'] = [ Texture_Mag_FilterType_Enum,
      self.getTex3MagFiltertype,
      self.setTex3MagFiltertype,
      None,
      None ]
    self.mutableParameters['tex2 min filter'] = [ Texture_Min_FilterType_Enum,
      self.getTex3MinFiltertype,
      self.setTex3MinFiltertype,
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
    self.mutableParameters['tex3 mag filter'] = [ Texture_Mag_FilterType_Enum,
      self.getTex4MagFiltertype,
      self.setTex4MagFiltertype,
      None,
      None ]
    self.mutableParameters['tex3 min filter'] = [ Texture_Min_FilterType_Enum,
      self.getTex4MinFiltertype,
      self.setTex4MinFiltertype,
      None,
      None ]
    
    self.mutableParameters['detailmap4'] = [ Filepath,
      self.getTex5,
      self.setTex5,
      None,
      self.clearTex4 ]
    self.mutableParameters['tex4scale'] = [ float,
      self.getTex5Scale,
      self.setTex5Scale,
      None,
      None ]
    self.mutableParameters['tex4 mag filter'] = [ Texture_Mag_FilterType_Enum,
      self.getTex5MagFiltertype,
      self.setTex5MagFiltertype,
      None,
      None ]
    self.mutableParameters['tex4 min filter'] = [ Texture_Min_FilterType_Enum,
      self.getTex5MinFiltertype,
      self.setTex5MinFiltertype,
      None,
      None ]
    
    self.mutableParameters['update'] = [ Trigger,
      self.getUpdateShader,
      self.setUpdateShader,
      None,
      None ]
    
    self.tex1Path = Filepath('')
    self.tex2Path = Filepath('')
    self.tex3Path = Filepath('')
    self.tex4Path = Filepath('')
    self.tex5Path = Filepath('')
    self.tex2Scale = 1
    self.tex3Scale = 1
    self.tex4Scale = 1
    self.tex5Scale = 1
    self.tex2MagFilter = Texture.FTNearest
    self.tex2MinFilter = Texture.FTNearest
    self.tex3MinFilter = Texture.FTNearest
    self.tex3MagFilter = Texture.FTNearest
    self.tex4MagFilter = Texture.FTNearest
    self.tex4MinFilter = Texture.FTNearest
    self.tex5MinFilter = Texture.FTNearest
    self.tex5MagFilter = Texture.FTNearest
    
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
        if self.tex5Path:
          tex5Path = posixpath.join(self.relativePath, self.tex5Path)
          print "  - tex5", tex5Path, self.tex5Scale
          self.shader.AddAlphaMap(tex5Path, tex1Path, alphamapchannel = "a", texscale = self.tex5Scale)
        self.shader.Initialize()
        
        print self.shader.loadedMaps
        print self.shader.AlphaMaps
        mixTex = self.shader.loadedMaps[tex1Path]
        if self.tex2Path:
          self.shader.AlphaMaps[(mixTex, 'r')][0].setMagfilter(self.tex2MagFilter)
          self.shader.AlphaMaps[(mixTex, 'r')][0].setMinfilter(self.tex2MinFilter)
          self.shader.AlphaMaps[(mixTex, 'r')][0].setWrapU(Texture.WMRepeat)
          self.shader.AlphaMaps[(mixTex, 'r')][0].setWrapV(Texture.WMRepeat)
        if self.tex3Path:
          self.shader.AlphaMaps[(mixTex, 'g')][0].setMagfilter(self.tex3MagFilter)
          self.shader.AlphaMaps[(mixTex, 'g')][0].setMinfilter(self.tex3MinFilter)
          self.shader.AlphaMaps[(mixTex, 'g')][0].setWrapU(Texture.WMRepeat)
          self.shader.AlphaMaps[(mixTex, 'g')][0].setWrapV(Texture.WMRepeat)
        if self.tex4Path:
          self.shader.AlphaMaps[(mixTex, 'b')][0].setMagfilter(self.tex4MagFilter)
          self.shader.AlphaMaps[(mixTex, 'b')][0].setMinfilter(self.tex4MinFilter)
          self.shader.AlphaMaps[(mixTex, 'b')][0].setWrapU(Texture.WMRepeat)
          self.shader.AlphaMaps[(mixTex, 'b')][0].setWrapV(Texture.WMRepeat)
        if self.tex5Path:
          self.shader.AlphaMaps[(mixTex, 'a')][0].setMagfilter(self.tex5MagFilter)
          self.shader.AlphaMaps[(mixTex, 'a')][0].setMinfilter(self.tex5MinFilter)
          self.shader.AlphaMaps[(mixTex, 'a')][0].setWrapU(Texture.WMRepeat)
          self.shader.AlphaMaps[(mixTex, 'a')][0].setWrapV(Texture.WMRepeat)
      #if self.isEditmodeEnabled():
      #  self.startPaint()
  
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
      messenger.send(EVENT_SCENEPICKER_MODELSELECTION_DISABLE)
      
      if self.tex1Path:
        print "  -", self.tex1Path
        #print "I: ObjectEggTexture.startEdit: editing texture", texture
        self.startPaint()
  
  def startPaint(self):
    if not self.paintActive:
      print "I: ShaderWrapper.startPaint"
      texPath = posixpath.join(self.relativePath, self.tex1Path)
      if texPath in self.shader.loadedMaps:
        self.paintTex = self.shader.loadedMaps[texPath]
        #texturePainter.startEdit(self.paintTex)
        success = texturePainter.enableEditor(self.nodePath, self.paintTex)
        if success:
          texturePainter.startEdit()
          self.paintActive = True
      else:
        print "E: ShaderWrapper.startPaint: unable to start painting, shader not initialized"
        self.paintActive = False
  
  def stopEdit(self):
    # the object is deselected from being edited
    print "I: ShaderWrapper.stopEdit:", self.isEditmodeEnabled()
    self.stopPaint()
    messenger.send(EVENT_SCENEPICKER_MODELSELECTION_ENABLE)
  
  def stopPaint(self):
    if self.paintActive:
      print "I: ShaderWrapper.stopPaint"
      texturePainter.stopEdit()
      texturePainter.disableEditor()
      self.paintActive = False
  
  def save(self):
    # saving the texture
    saveTex = PNMImage()
    self.paintTex.store(saveTex)
    savePath = posixpath.join(self.relativePath, self.tex1Path)
    print "I: ShaderWrapper.save:", savePath
    saveTex.write(Filename(savePath))
  
  def destroy(self):
    self.stopEdit()
    self.shader.destroy()
    self.setEditmodeDisabled()
    BaseWrapper.destroy(self)
  
  def makeInstance(self, originalInstance):
    ''' create a copy of this instance
    '''
    newInstance = self(originalInstance.getParent(), originalInstance.getName()+"-copy")
    newInstance.nodePath.setMat(originalInstance.nodePath.getMat())
    newInstance.setParameters(originalInstance.getParameters())
    newInstance.setUpdateShader()
    return newInstance
  makeInstance = classmethod(makeInstance)
  
  def setTex1(self, texPath):
    if texPath:
      if texPath[0] == '/':
        texPath = relpath(self.relativePath, posixpath.abspath(texPath))
    self.tex1Path = Filepath(texPath)
  def getTex1(self):
    return self.tex1Path
  def clearTex1(self):
    self.tex1Path = None
  
  def setTex2(self, texPath):
    if texPath:
      if texPath[0] == '/':
        texPath = relpath(self.relativePath, posixpath.abspath(texPath))
    self.tex2Path = Filepath(texPath)
  def getTex2(self):
    return self.tex2Path
  def clearTex2(self):
    self.tex2Path = None
  
  def setTex3(self, texPath):
    if texPath:
      if texPath[0] == '/':
        texPath = relpath(self.relativePath, posixpath.abspath(texPath))
    self.tex3Path = Filepath(texPath)
  def getTex3(self):
    return self.tex3Path
  def clearTex3(self):
    self.tex3Path = None
  
  def setTex4(self, texPath):
    if texPath:
      if texPath[0] == '/':
        texPath = relpath(self.relativePath, posixpath.abspath(texPath))
    self.tex4Path = Filepath(texPath)
  def getTex4(self):
    return self.tex4Path
  def clearTex4(self):
    self.tex4Path = None
  
  def setTex5(self, texPath):
    if texPath:
      if texPath[0] == '/':
        texPath = relpath(self.relativePath, posixpath.abspath(texPath))
    self.tex5Path = Filepath(texPath)
  def getTex5(self):
    return self.tex5Path
  def clearTex5(self):
    self.tex5Path = None
  
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
  
  def getTex5Scale(self):
    return self.tex5Scale
  def setTex5Scale(self, scale):
    self.tex5Scale = scale
  
  def getTex2MinFiltertype(self):
    return self.tex2MinFilter
  def setTex2MinFiltertype(self, filter):
    self.tex2MinFilter = filter
  def getTex2MagFiltertype(self):
    return self.tex2MagFilter
  def setTex2MagFiltertype(self, filter):
    self.tex2MagFilter = filter


  def getTex3MinFiltertype(self):
    return self.tex3MinFilter
  def setTex3MinFiltertype(self, filter):
    self.tex3MinFilter = filter
  def getTex3MagFiltertype(self):
    return self.tex3MagFilter
  def setTex3MagFiltertype(self, filter):
    self.tex3MagFilter = filter

  def getTex4MinFiltertype(self):
    return self.tex4MinFilter
  def setTex4MinFiltertype(self, filter):
    self.tex4MinFilter = filter
  def getTex4MagFiltertype(self):
    return self.tex4MagFilter
  def setTex4MagFiltertype(self, filter):
    self.tex4MagFilter = filter

  def getTex5MinFiltertype(self):
    return self.tex5MinFilter
  def setTex5MinFiltertype(self, filter):
    self.tex5MinFilter = filter
  def getTex5MagFiltertype(self):
    return self.tex5MagFilter
  def setTex5MagFiltertype(self, filter):
    self.tex5MagFilter = filter

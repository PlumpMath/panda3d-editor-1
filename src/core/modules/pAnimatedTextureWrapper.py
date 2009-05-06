__all__=['AnimatedTextureWrapper']

import os, posixpath, traceback

from core.pTreeNode import TreeNode
from core.pCommonPath import relpath
from core.pConfigDefs import *
from core.pEnums import TextureStage_Mode_Enum, Texture_WrapMode_Enum, \
  Texture_Min_FilterType_Enum, Texture_Mag_FilterType_Enum

class AnimatedTextureWrapper(TreeNode):
  ''' a texture which changes the image with playRate
  if you have images named image001.png, image002.png, ..., image010.png
  imageStart must be 1
  imageEnd must be 11
  imageBasename must be image%03i.png
  '''
  # define the name for the gui
  className = 'AnimatedTexture'
  def onCreateInstance(self, parent):
    # create instance of this class
    name=self.className
    objectInstance = super(AnimatedTextureWrapper, self).onCreateInstance(parent, name)
    return objectInstance
  onCreateInstance = classmethod(onCreateInstance)
  
  def __init__(self, parent, name=className):
    TreeNode.__init__(self, name)
    # create the nodepath first, so TreeNode.reparenting handles NodePath.parenting correctly
    self.setNodepath(NodePath("AnimatedTextureWrapper-"+str(self.__hash__)))
    
    self.reparentTo(parent)
    
    self.imageBasename = 'sample/image%04i.png'
    self.mutableParameters['image base'] = [ Filepath,
        self.getImageBasename,
        self.setImageBasename,
        None,
        None,
        True ]
    
    self.imageStartNumber = 0
    self.mutableParameters['image start'] = [ int,
        self.getImageStartNumber,
        self.setImageStartNumber,
        None,
        None,
        True ]
    
    self.imageEndNumber = 10
    self.mutableParameters['image end'] = [ int,
        self.getImageEndNumber,
        self.setImageEndNumber,
        None,
        None,
        True ]
    
    self.textureStageSort = 0
    self.mutableParameters['texture sort'] = [ int,
        self.getTextureSort,
        self.setTextureSort,
        None,
        None,
        True ]
    
    self.playRate = 30
    self.mutableParameters['playrate'] = [ float,
        self.getPlayRate,
        self.setPlayRate,
        None,
        None,
        True ]
    
    self.texturePriority = 1
    self.mutableParameters['priority'] = [ int,
        self.getPriority,
        self.setPriority,
        None,
        None,
        True]
    
    self.active = False
    self.mutableParameters['active'] = [ bool,
        self.getActive,
        self.setActive,
        None,
        None,
        True ]
    
    self.textureWrapU = EggTexture.WMRepeat
    self.mutableParameters['u wrap mode'] = [ Texture_WrapMode_Enum,
        self.getWrapU,
        self.setWrapU,
        None,
        None,
        True ]
    self.textureWrapV = EggTexture.WMRepeat
    self.mutableParameters['v wrap mode'] = [ Texture_WrapMode_Enum,
        self.getWrapV,
        self.setWrapV,
        None,
        None,
        True ]
    self.textureMinFilter = Texture.FTLinear
    self.mutableParameters['min filter'] = [ Texture_Min_FilterType_Enum,
        self.getMinfilter,
        self.setMinfilter,
        None,
        None,
        True ]
    self.textureMagFilter = Texture.FTLinear
    self.mutableParameters['mag filter'] = [ Texture_Mag_FilterType_Enum,
        self.getMagfilter,
        self.setMagfilter,
        None,
        None,
        True ]
    self.textureStageMode = TextureStage.MBlend
    self.mutableParameters['mode type'] = [ TextureStage_Mode_Enum,
        self.getTextureStageMode,
        self.setTextureStageMode,
        None,
        None,
        True ]
    
    self.shaderAutoPriority = None
    self.mutableParameters['shader auto'] = [ int,
        self.getShaderAuto,
        self.setShaderAuto,
        None,
        self.clearShaderAuto,
        True ]
  
  def getShaderAuto(self):
    return self.shaderAutoPriority
  def setShaderAuto(self, priority):
    self.stop()
    self.shaderAutoPriority = priority
    self.start()
  def clearShaderAuto(self):
    self.stop()
    self.shaderAutoPriority = None
    self.start()
  
  def getWrapU(self):
    return self.textureWrapU
  def setWrapU(self, wrapU):
    self.stop()
    self.textureWrapU = wrapU
    self.start()
  
  def getWrapV(self):
    return self.textureWrapV
  def setWrapV(self, wrapV):
    self.stop()
    self.textureWrapV = wrapV
    self.start()
  
  def getMinfilter(self):
    return self.textureMinFilter
  def setMinfilter(self, minFilter):
    self.stop()
    self.textureMinFilter = minFilter
    self.start()
  
  def getMagfilter(self):
    return self.textureMagFilter
  def setMagfilter(self, magFilter):
    self.stop()
    self.textureMagFilter = magFilter
    self.start()
  
  def getTextureStageMode(self):
    return self.textureStageMode
  def setTextureStageMode(self, mode):
    self.stop()
    self.textureStageMode = mode
    self.start()
  
  def setImageBasename(self, basename):
    self.stop()
    if basename:
      if basename[0] == '/':
        relativePath = posixpath.dirname(self.getParentFilepath())
        basename = relpath(relativePath, posixpath.abspath(basename))
    self.imageBasename = basename
    self.start()
  def getImageBasename(self):
    return self.imageBasename
  
  def setImageStartNumber(self, startNumber):
    self.stop()
    self.imageStartNumber = startNumber
    self.start()
  def getImageStartNumber(self):
    return self.imageStartNumber
  
  def setImageEndNumber(self, endNumber):
    self.stop()
    self.imageEndNumber = endNumber
    self.start()
  def getImageEndNumber(self):
    return self.imageEndNumber
  
  def setTextureSort(self, sort):
    self.stop()
    self.textureStageSort = sort
    self.start()
  def getTextureSort(self):
    return self.textureStageSort
  
  def setActive(self, state):
    self.stop()
    self.active = state
    self.start()
  def getActive(self):
    return self.active
  
  def setPlayRate(self, rate):
    self.stop()
    self.playRate = rate
    self.start()
  def getPlayRate(self):
    return self.playRate
  
  def setPriority(self, prio):
    self.stop()
    self.texturePriority = prio
    self.start()
  def getPriority(self):
    return self.texturePriority
  
  '''def update(self):
    if self.active:
      # start stuff
      self.start()
    else:
      # stop stuff
      self.stop()'''
  
  def start(self):
    if self.active:
      # load the textures
      self.textures = list()
      sizex = -1
      sizey = -1
      ctype = None
      format = None
      for i in xrange(self.imageStartNumber,self.imageEndNumber):
        try:
          if '%' in self.imageBasename:
            tex = loader.loadTexture(self.imageBasename % i)
          else:
            tex = loader.loadTexture(self.imageBasename)
          self.textures.append(tex)
          # Make sure they are all the same size and format
          assert sizex == -1 or tex.getXSize() == sizex
          assert sizey == -1 or tex.getYSize() == sizey
          assert ctype == None or tex.getComponentType() == ctype
          assert format == None or tex.getFormat() == format
          sizex = tex.getXSize()
          sizey = tex.getYSize()
          ctype = tex.getComponentType()
          format = tex.getFormat()
          tex.setWrapU(self.textureWrapU)
          tex.setWrapV(self.textureWrapV)
          tex.setMinfilter(self.textureMinFilter)
          tex.setMagfilter(self.textureMagFilter)
        except:
          print "W: AnimatedTextureWrapper.start: error loading the image", self.imageBasename, i
      self.textureStage = TextureStage("AnimatedTextureWrapper-texturestage-"+str(self.__hash__))
      self.textureStage.setSort(self.textureStageSort)
      self.textureStage.setMode(self.textureStageMode)
      if len(self.textures) > 0:
        # start the animated texture task
        taskName = "AnimatedTextureWrapper-task-"+str(self.__hash__)
        taskMgr.add(self.updateTask, taskName)
        if self.shaderAutoPriority is not None:
          self.getNodepath().setShaderAuto(self.shaderAutoPriority)
        else:
          self.getNodepath().clearShader()
  
  def stop(self):
    if self.active:
      taskName = "AnimatedTextureWrapper-task-"+str(self.__hash__)
      taskMgr.remove(taskName)
      # clear the loaded textures
      for i in xrange(self.imageStartNumber,self.imageEndNumber):
        try:
          loader.unloadTexture(self.imageBasename % i)
        except:
          print "W: AnimatedTextureWrapper.stop: error unloading the image", self.imageBasename, i
      del self.textures
      self.getNodepath().setTextureOff(self.texturePriority)
      if self.shaderAutoPriority is not None:
        self.getNodepath().setShaderOff(self.shaderAutoPriority)
      else:
        self.getNodepath().clearShader()
  
  def updateTask(self, task):
    # find the current image
    t = task.time
    i = int((t * self.playRate) % len(self.textures))
    # apply the texture
    try:
      texture = self.textures[i]
      if not self.getNodepath().hasTexture(self.textureStage):
        tex = Texture()
        tex.setup2dTexture(texture.getXSize(), texture.getYSize(), texture.getComponentType(), texture.getFormat())
        self.getNodepath().setTexture(self.textureStage, tex, self.texturePriority)
      self.getNodepath().getTexture(self.textureStage).setRamImage(texture.getRamImage())
    except:
      raise
      print "W: AnimatedTextureWrapper.updateTask: error with texture", i
    # do the task again
    return task.cont
  
  def destroy(self):
    self.stop()
    TreeNode.destroy(self)
  
  def getSaveData(self, relativeTo):
    print "I: AnimatedTextureWrapper.getSaveData:", relativeTo
    objectInstance = TreeNode.getSaveData(self, relativeTo)
    return objectInstance
  
  def loadFromData(self, eggGroup, filepath):
    TreeNode.loadFromData(self, eggGroup, filepath)
  
  def duplicate(self, original):
    objectInstance = super(AnimatedTextureWrapper, self).duplicate(original)
    return objectInstance
  duplicate = classmethod(duplicate)

__all__=['BaseWrapper']

import traceback, posixpath

from pandac.PandaModules import *

from core.pModelIdManager import modelIdManager
from core.pCommonPath import relpath
from core.pConfigDefs import *
from core.pTreeNode import *

DEBUG = False

BASEWRAPPER_DATA_TAG = 'parameters'

TransparencyEnum = Enum(
  MNone = TransparencyAttrib.MNone,
  MAlpha = TransparencyAttrib.MAlpha,
  MNotused = TransparencyAttrib.MNotused,
  MMultisample = TransparencyAttrib.MMultisample,
  MMultisampleMask = TransparencyAttrib.MMultisampleMask,
  MBinary = TransparencyAttrib.MBinary,
  MDual = TransparencyAttrib.MDual,
)

AntialiasEnum = Enum(
  MNone = AntialiasAttrib.MNone,
  MPoint = AntialiasAttrib.MPoint,
  MLine = AntialiasAttrib.MLine,
  MPolygon = AntialiasAttrib.MPolygon,
  MMultisample = AntialiasAttrib.MMultisample,
  MAuto = AntialiasAttrib.MAuto,
)

def getShaderAttrib(nodepath):
  if hasattr(ShaderAttrib, 'getClassType'): # 1.5.4 uses getClassType ??? not checked
    shaderAttrib = nodepath.getAttrib(ShaderAttrib.getClassType())
  elif hasattr(ShaderAttrib, 'getClassSlot'): # 1.6 uses getClassSlot ??? not checked
    shaderAttrib = nodepath.getAttrib(ShaderAttrib.getClassSlot())
  hasShader = None
  shaderPriority = None
  shaderAuto = None
  shaderFilename = None
  if shaderAttrib:
    hasShader = shaderAttrib.hasShader()
    shaderPriority = shaderAttrib.getShaderPriority()
    shaderAuto = shaderAttrib.autoShader()
    shader = shaderAttrib.getShader()
    if shader:
      shaderFilename = shader.getFilename()
  return hasShader, shaderPriority, shaderAuto, shaderFilename


class BaseWrapper(TreeNode):
  ''' a special version of a treenode
  features:
  - it has a visual representation (can be only a helper model (lights))
  - it has a position/rotation/scale
  todo:
  - maybe move color,antialias etc. to special implementations of this node
  '''
  className = 'Base'
  def onCreateInstance(self, parent, name='BaseWrapper'):
    # create instance of this class
    #print help(self.__init__)
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
    TreeNode.__init__(self, name)
    # get a uniq id for this object
    self.id = modelIdManager.getId()
    # store this object
    modelIdManager.setObject(self, self.id)
    # create a node for this object
    self.setNodepath(NodePath(name))
    self.reparentTo(parent)
    
    nodePath = self.getNodepath()
    self.mutableParameters['color'] = [ Vec4,
      nodePath.getColor,
      nodePath.setColor,
      nodePath.hasColor,
      nodePath.clearColor ]
    self.mutableParameters['colorScale'] = [ Vec4,
      nodePath.getColorScale,
      nodePath.setColorScale,
      nodePath.hasColorScale,
      nodePath.clearColorScale ]
    self.mutableParameters['transparency'] = [ TransparencyEnum,
      nodePath.getTransparency,
      nodePath.setTransparency,
      nodePath.hasTransparency,
      nodePath.clearTransparency ]
    self.mutableParameters['antialias'] = [ AntialiasEnum,
      nodePath.getAntialias,
      nodePath.setAntialias,
      nodePath.hasAntialias,
      nodePath.clearAntialias ]
    # should not be saved into the comments, but available to the gui-editor
    self.mutableParameters['position'] = [ Vec3,
      nodePath.getPos,
      nodePath.setPos,
      None,
      None ]
    self.mutableParameters['rotation'] = [ Vec3,
      nodePath.getHpr,
      nodePath.setHpr,
      None,
      None ]
    self.mutableParameters['scale'] = [ Vec3,
      nodePath.getScale,
      nodePath.setScale,
      None,
      None ]
    
    self.shaderOffPriority = None
    self.mutableParameters['shaderOff'] = [ int,
      self.getShaderOff,
      self.setShaderOff,
      None,
      self.clearShader ]
    self.lightOffPriority = None
    self.mutableParameters['lightOff'] = [ int,
      self.getLightOff,
      self.setLightOff,
      None,
      self.clearLightOff ]
    
    self.colorOffPriority = None
    self.mutableParameters['colorOff'] = [ int,
      self.getColorOff,
      self.setColorOff,
      None,
      self.clearColorOff ]
    
    self.textureOffEnabled = False
    self.mutableParameters['textureOffEnabled'] = [ bool,
      self.getTextureOffEnabled,
      self.setTextureOffEnabled,
      None,
      None ]
    self.textureOffPriority = None
    self.mutableParameters['textureOffPriority'] = [ int,
      self.getTextureOffPriority,
      self.setTextureOffPriority,
      None,
      self.clearTextureOffPriorty ]
  
  def reparentTo(self, parent):
    ''' overload the reparenting of treeNode
    the basewrapper also needs to reparent a nodePath '''
    # reparent
    TreeNode.reparentTo(self, parent)
    
    '''parentNodepath = self.getParentNodepath()
    if parentNodepath:
      self.getNodepath().reparentTo(parentNodepath)
    else:
      self.getNodepath().reparentTo(render) # <- XXX TODO, this should not be render'''
    
    parentNodepath = self.getParentNodepath()
    if parentNodepath:
      self.getNodepath().wrtReparentTo(parentNodepath)
    else:
      self.getNodepath().wrtReparentTo(render) # <- XXX TODO, this should not be render
    
    '''if hasattr(self.getParent(), 'nodePath'):
      parentNodepath = self.getParent().getNodepath()
    else:
      parentNodepath = render
    self.getNodepath().wrtReparentTo(parentNodepath)'''
  
  # --- functions to stop inheriting shader ---
  def setShaderOff(self, priority):
    if priority != None:
      self.getNodepath().setShaderOff(priority)
  def getShaderOff(self):
    hasShader, shaderPriority, shaderAuto, shaderFilename = getShaderAttrib(self.getNodepath())
    if hasShader and shaderAuto is 0 and shaderFilename is None:
      return shaderPriority
    return None
  def clearShader(self):
    self.getNodepath().clearShader()
  
  # --- functions to stop inheriting light ---
  def setLightOff(self, priority):
    self.lightOffPriority = priority
    if priority != None:
      self.getNodepath().setLightOff(priority)
  def getLightOff(self):
    return self.lightOffPriority
  def clearLightOff(self):
    self.lightOffPriority = None
    self.getNodepath().clearLight()
  
  # --- functions to stop inhertiting color ---
  def setColorOff(self, priority):
    self.colorOffPriority = priority
    if priority != None:
      self.getNodepath().setColorOff(priority)
  def getColorOff(self):
    return self.colorOffPriority
  def clearColorOff(self):
    self.colorOffPriority = None
    self.getNodepath().clearColor()
  
  # --- functions to stop inheriting textures (and turning textures off) ---
  def updateTextureOff(self):
    if self.textureOffEnabled:
      # set texture off
      if self.textureOffPriority is None:
        # stop inheriting textures (if they have not a too high priorty)
        self.getNodepath().setTextureOff()
      else:
        # clear textures anyway
        self.getNodepath().setTextureOff(self.textureOffPriority)
    else:
      # reset to the original state
      self.getNodepath().clearTexture()
  
  def getTextureOffEnabled(self):
    return self.textureOffEnabled
  def setTextureOffEnabled(self, state):
    self.textureOffEnabled = state
    self.updateTextureOff()
  
  def getTextureOffPriority(self):
    return self.textureOffPriority
  def setTextureOffPriority(self, priority):
    self.textureOffPriority = priority
    self.updateTextureOff()
  def clearTextureOffPriorty(self):
    self.textureOffPriority = None
    self.updateTextureOff()
  
  def __del__(self):
    print "I: BaseWrapper.__del__:", self.__class__.__name__
    pass
  
  def setEditmodeEnabled(self):
    ''' enables the edit methods of this object
    makes it pickable etc.
    edit mode is enabled'''
    if not self.isEditmodeEnabled():
      # make this a editable object
      self.getNodepath().setTag(ENABLE_SCENEGRAPHBROWSER_MODEL_TAG, '')
      self.getNodepath().setTag(EDITABLE_OBJECT_TAG, self.id)
      TreeNode.setEditmodeEnabled(self)
  
  def setEditmodeDisabled(self):
    ''' disables the edit methods of this object
    -> performance increase
    edit mode is disabled'''
    if self.isEditmodeEnabled():
      self.getNodepath().clearTag(ENABLE_SCENEGRAPHBROWSER_MODEL_TAG)
      self.getNodepath().clearTag(EDITABLE_OBJECT_TAG)
      TreeNode.setEditmodeDisabled(self)
  
  def destroy(self):
    modelIdManager.delObjectId( self.id )
    TreeNode.destroy(self)
    self.getNodepath().detachNode()
    self.getNodepath().removeNode()
  
  def getSaveData(self, relativeTo):
    instance = TreeNode.getSaveData(self, relativeTo)
    # convert the matrix, very ugly right now
    om = self.getNodepath().getMat()
    nm = Mat4D()
    for x in xrange(4):
      for y in xrange(4):
        nm.setCell(x, y, om.getCell(x,y))
    # apply the matrix onto the instance
    instance.setGroupType(EggGroup.GTInstance)
    instance.setTransform3d(nm)
    return instance
  
  ''' --- external reference saving / loading ---
  these are used by if a wrapper uses a external file
  (models, particlesystems, terrain, sounds)'''
  def setExternalReference(self, filepath, relativeTo, objectInstance):
    # convert to a relative path
    extRefPath = relpath(relativeTo, posixpath.abspath(filepath))
    # add the reference to the egg-file
    extRef = EggExternalReference("ExtRef", extRefPath)
    objectInstance.addChild(extRef)
  
  def getExternalReference(self, eggGroup, filepath):
    # search for a external reference
    eggExternalReference = None
    for child in eggGroup.getChildren():
      if type(child) == EggExternalReference:
        eggExternalReference = child
    # read the reference if it is found
    if eggExternalReference is not None:
      referencedFilename = eggExternalReference.getFilename()
      filename = posixpath.join(filepath,str(referencedFilename))
      return filename
    print "W: BaseWrapper.getExternalReference: no externalReference found in"
    print "  -",eggGroup
    return None
  ''' --- end : external reference saving / loading --- '''
  

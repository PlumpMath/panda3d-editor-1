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

class BaseWrapper(TreeNode):
  ''' a special version of a treenode
  features:
  - it has a visual representation (can be only a helper model (lights))
  - it has a position/rotation/scale
  todo:
  - maybe move color,antialias etc. to special implementations of this node
  '''
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
    # get a uniq id for this object
    self.id = modelIdManager.getId()
    # define a name for this object
    TreeNode.__init__(self, name)
    TreeNode.reparentTo(self, parent)
    self.nodePath = NodePath(name)
    # store this object
    modelIdManager.setObject(self, self.id)
    # reparent this nodePath
    if parent is None:
      parentNodepath = render
    else:
      parentNodepath = parent.nodePath
    self.nodePath.reparentTo(parentNodepath)
    
    # all values that can be changed require a entry in the mutableParameters
    
    # when a value exists, it means that it's allowed to read/write the value
    # hasFunc defines if it's a vital property of the object and must be saved
    # into the comments
    
    # valueType, getFunc vtion, setFunction, hasFunction, clearFunction, saveToComments
    # hasFunction == None -> the value should be saved
    self.mutableParameters['color'] = [ Vec4,
      self.nodePath.getColor,
      self.nodePath.setColor,
      self.nodePath.hasColor,
      self.nodePath.clearColor ]
    self.mutableParameters['colorScale'] = [ Vec4,
      self.nodePath.getColorScale,
      self.nodePath.setColorScale,
      self.nodePath.hasColorScale,
      self.nodePath.clearColorScale ]
    self.mutableParameters['transparency'] = [ TransparencyEnum,
      self.nodePath.getTransparency,
      self.nodePath.setTransparency,
      self.nodePath.hasTransparency,
      self.nodePath.clearTransparency ]
    self.mutableParameters['antialias'] = [ AntialiasEnum,
      self.nodePath.getAntialias,
      self.nodePath.setAntialias,
      self.nodePath.hasAntialias,
      self.nodePath.clearAntialias ]
    # should not be saved into the comments, but available to the gui-editor
    self.mutableParameters['position'] = [ Vec3,
      self.nodePath.getPos,
      self.nodePath.setPos,
      None,
      None ]
    self.mutableParameters['rotation'] = [ Vec3,
      self.nodePath.getHpr,
      self.nodePath.setHpr,
      None,
      None ]
    self.mutableParameters['scale'] = [ Vec3,
      self.nodePath.getScale,
      self.nodePath.setScale,
      None,
      None ]
  
  def __del__(self):
    print "I: BaseWrapper.__del__:", self.__class__.__name__
    pass
  
  def setEditmodeEnabled(self, recurseException=[]):
    ''' enables the edit methods of this object
    makes it pickable etc.
    edit mode is enabled'''
    if not self.isEditmodeEnabled():
      # make this a editable object
      self.nodePath.setTag(ENABLE_SCENEGRAPHBROWSER_MODEL_TAG, '')
      self.nodePath.setTag(EDITABLE_OBJECT_TAG, self.id)
      TreeNode.setEditmodeEnabled(self, recurseException)
  
  def setEditmodeDisabled(self, recurseException=[]):
    ''' disables the edit methods of this object
    -> performance increase
    edit mode is disabled'''
    if self.isEditmodeEnabled():
      self.nodePath.clearTag(ENABLE_SCENEGRAPHBROWSER_MODEL_TAG)
      self.nodePath.clearTag(EDITABLE_OBJECT_TAG)
      TreeNode.setEditmodeDisabled(self, recurseException)
  
  def destroy(self):
    modelIdManager.delObjectId( self.id )
    TreeNode.destroy(self)
    self.nodePath.detachNode()
    self.nodePath.removeNode()
  
  def getSaveData(self, relativeTo):
    instance = TreeNode.getSaveData(self, relativeTo)
    # convert the matrix, very ugly right now
    om = self.nodePath.getMat()
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
  

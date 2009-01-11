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
    self.name = name
    # define a name for this object
    TreeNode.__init__(self, name, self)
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
    self.editModeEnabled = False
    
    # model used to show highlighting of this node
    self.highlightModel = None
    
    # all values that can be changed require a entry in the mutableParameters
    
    # when a value exists, it means that it's allowed to read/write the value
    # hasFunc defines if it's a vital property of the object and must be saved
    # into the comments
    
    # valueType, getFunc vtion, setFunction, hasFunction, clearFunction, saveToComments
    # hasFunction == None -> the value should be saved
    self.mutableParameters = dict()
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
    self.mutableParameters['name'] = [ str,
      self.nodePath.getName,
      self.nodePath.setName,
      None,
      None ]
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
  
  def enableEditmode(self):
    ''' enables the edit methods of this object
    makes it pickable etc.
    edit mode is enabled'''
    if not self.editModeEnabled:
      # make this a editable object
      self.nodePath.setTag(ENABLE_SCENEGRAPHBROWSER_MODEL_TAG, '')
      self.nodePath.setTag(EDITABLE_OBJECT_TAG, self.id)
      self.editModeEnabled = True
  
  def disableEditmode(self):
    ''' disables the edit methods of this object
    -> performance increase
    edit mode is disabled'''
    if self.editModeEnabled:
      self.nodePath.clearTag(ENABLE_SCENEGRAPHBROWSER_MODEL_TAG)
      self.nodePath.clearTag(EDITABLE_OBJECT_TAG)
      self.editModeEnabled = False
  
  def startEdit(self):
    # the object is selected to be edited
    # creates a directFrame to edit this object
    if not self.editModeEnabled:
      print "E: core.BaseWrapper.startEdit: object is not in editmode", self
  
  def stopEdit(self):
    # the object is deselected from being edited
    if not self.editModeEnabled:
      print "E: core.BaseWrapper.stopEdit: object is not in editmode", self
  
  def destroy(self):
    modelIdManager.delObjectId( self.id )
    self.nodePath.detachNode()
    self.nodePath.removeNode()
  
  def getParameter(self, name):
    varType, getFunc, setFunc, hasFunc, clearFunc = self.mutableParameters[name]
    #getFunc = getattr(self, getFuncName)
    # store the parameters
    if hasFunc != None and not hasFunc():
      return None
    val = getFunc()
    if varType in [Vec4, Point4, VBase4]:
      return (val[0], val[1], val[2], val[3])
    elif varType in [Vec3, Point3, VBase3]:
      return (val[0], val[1], val[2])
    elif varType in [Vec2, Point2, VBase2]:
      return (val[0], val[1])
    elif varType in [float, int, str, bool]:
      return val
    elif isinstance(varType, Enum):
      for n, v in varType.items():
        if v == val:
          return n
      print "E: core.BaseWrapper.getParameters: invalid value %s for enum %s" % (val, varType.__name__)
    else:
      print "E: core.BaseWrapper.getParameters: unknown varType %s for %s" % (varType.__name__, name)
  
  def getParameters(self):
    # get the data
    parameters = dict()
    for name in self.mutableParameters.keys():
      value = self.getParameter(name)
      if value is not None:
        parameters[name] = value
    return parameters
  
  def setParameter(self, name, value):
    ''' name: name of the parameter
    value: value of the parameter, if parameter is a Vec or Point, give a tuple or list
    '''
    varType, getFunc, setFunc, hasFunc, clearFunc = self.mutableParameters[name]
    try:
      if clearFunc != None and (value == None or (isinstance(value, str) and value.lower() == "none")):
        clearFunc()
      elif isinstance(varType, type) and isinstance(value, varType):
        # It's already the correct type
        setFunc(value)
      elif isinstance(varType, Enum):
        '''if n in varType.keys():
          v = varType[n]
          setFunc(v)
        else:
          print "W: core.BaseWrapper.setParameter: invalid value %s for enum %s" % (value, varType.__name__)
        '''
        for n, v in varType.items():
          if n == value:
            setFunc(v)
            return
        print "W: core.BaseWrapper.setParameter: invalid value %s for enum %s" % (value, varType.__name__)
      else:
        if isinstance(value, str) or isinstance(value, unicode):
          try:
            value = tuple([float(i) for i in value.replace("(", "").replace(")", "").replace(" ", "").split(",")])
          except:
            print "E: core.BaseWrapper.setParameter: error converting string" % name, value
        if varType in [Vec4, Point4, VBase4, Point3, Vec3, VBase3, Point2, Vec2, VBase2]:
          setFunc(varType(*value))
        elif varType in [float, int, str, bool]:
          setFunc(varType(value))
        else:
          print "E: core.BaseWrapper.setParameter: unknown varType %s for %s" % (varType.__name__, name)
    except TypeError:
      # this must be catched as it's a user input
      print "E: core.BaseWrapper.setParameter: error handling %s in data:" % name, value
      traceback.print_exc()
  
  def setParameters(self, parameters):
    for name, value in parameters.items():
      self.setParameter(name, value)
  
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
  
  ''' --- load & save to files --- '''
  def getSaveData(self, relativeTo):
    # the given name of this object
    name = self.getName()
    # convert the matrix, very ugly right now
    om = self.getMat()
    nm = Mat4D()
    for x in xrange(4):
      for y in xrange(4):
        nm.setCell(x, y, om.getCell(x,y))
    # the matrix we define must be applied to the nodes in "local space"
    instance = EggGroup(name)
    instance.setGroupType(EggGroup.GTInstance)
    instance.setTransform3d(nm)
    # define the type of this object
    className = self.__class__.__name__
    instance.setTag(MODEL_WRAPPER_TYPE_TAG, className)
    
    # get all data to store in the eggfile
    parameters = self.getParameters()
    if len(parameters) > 0:
      del parameters['name']
      del parameters['position']
      del parameters['scale']
      del parameters['rotation']
      # add the data to the egg-file
      comment = EggComment(BASEWRAPPER_DATA_TAG, str(parameters))
      instance.addChild(comment)
    return instance
  
  def loadFromData(self, eggGroup, filepath):
    data = dict()
    for child in eggGroup.getChildren():
      if type(child) == EggComment:
        if child.getName() == BASEWRAPPER_DATA_TAG:
          data = eval(child.getComment())
    self.setParameters(data)
  ''' --- end : load & save to files --- '''
  
  def makeInstance(self, originalInstance):
    ''' create a copy of this instance
    '''
    newInstance = self(originalInstance.getParent(), originalInstance.getName())
    newInstance.setMat(originalInstance.getMat())
    newInstance.setParameters(originalInstance.getParameters())
    return newInstance
  makeInstance = classmethod(makeInstance)

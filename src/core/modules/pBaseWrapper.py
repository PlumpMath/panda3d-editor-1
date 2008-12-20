import pickle, traceback, posixpath

from pandac.PandaModules import *
from direct.gui.DirectGui import *

from core.pModelIdManager import modelIdManager
from core.pConfigDefs import *
from core.pCommonPath import relpath

DEBUG = False

BASEWRAPPER_DATA_TAG = 'parameters'

class Enum(dict):
  __name__ = "Enum"

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

class BaseWrapper(NodePath):
  def onCreateInstance(self, parent, name='BaseWrapper'):
    # create instance of this class
    objectInstance = self(parent, name)
    return objectInstance
  onCreateInstance = classmethod(onCreateInstance)
  
  def loadFromEggGroup(self, eggGroup, parent, filepath):
    if DEBUG:
      print "I: NodePathWrapper.loadFromEggGroup:"
    name = eggGroup.getName()
    objectInstance = self(parent, name)
    return objectInstance
  loadFromEggGroup = classmethod(loadFromEggGroup)
  
  def __init__(self, parent, name):
    if DEBUG:
      print "I: BaseWrapper.__init__:", parent, name
    
    # get a uniq id for this object
    self.id = modelIdManager.getId()
    # define a name for this object
    NodePath.__init__(self, name)
    # store this object
    modelIdManager.setObject(self, self.id)
    # reparent this nodePath
    if parent is None:
      parent = render
    self.reparentTo(parent)
    self.editModeEnabled = False
    
    # all values that can be changed require a entry in the mutableParameters
    
    # when a value exists, it means that it's allowed to read/write the value
    # hasFunc defines if it's a vital property of the object and must be saved
    # into the comments
    
    # valueType, getFunction, setFunction, hasFunction, clearFunction, saveToComments
    # hasFunction == None -> the value should be saved
    self.mutableParameters = dict()
    self.mutableParameters['color'] = [ Vec4,
      self.getColor,
      self.setColor,
      self.hasColor,
      self.clearColor ]
    self.mutableParameters['colorScale'] = [ Vec4,
      self.getColorScale,
      self.setColorScale,
      self.hasColorScale,
      self.clearColorScale ]
    self.mutableParameters['transparency'] = [ TransparencyEnum,
      self.getTransparency,
      self.setTransparency,
      self.hasTransparency,
      self.clearTransparency ]
    self.mutableParameters['antialias'] = [ AntialiasEnum,
      self.getAntialias,
      self.setAntialias,
      self.hasAntialias,
      self.clearAntialias ]
    # should not be saved into the comments, but available to the gui-editor
    self.mutableParameters['name'] = [ str,
      self.getName,
      self.setName,
      None,
      None ]
    self.mutableParameters['position'] = [ Vec3,
      self.getPos,
      self.setPos,
      None,
      None ]
    self.mutableParameters['rotation'] = [ Vec3,
      self.getHpr,
      self.setHpr,
      None,
      None ]
    self.mutableParameters['scale'] = [ Vec3,
      self.getScale,
      self.setScale,
      None,
      None ]
  
  def enableEditmode(self):
    ''' enables the edit methods of this object
    makes it pickable etc.
    edit mode is enabled'''
    if not self.editModeEnabled:
      # make this a editable object
      self.setTag(ENABLE_SCENEGRAPHBROWSER_MODEL_TAG, '')
      self.setTag(EDITABLE_OBJECT_TAG, self.id)
      self.editModeEnabled = True
  
  def disableEditmode(self):
    ''' disables the edit methods of this object
    -> performance increase
    edit mode is disabled'''
    if self.editModeEnabled:
      self.clearTag(ENABLE_SCENEGRAPHBROWSER_MODEL_TAG)
      self.clearTag(EDITABLE_OBJECT_TAG)
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
    self.detachNode()
    self.removeNode()
  
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
        print "I: core.BaseWrapper.setParameter: clear"
        clearFunc()
      elif isinstance(value, varType):
        print "I: core.BaseWrapper.setParameter: not converting"
        # It's already the correct type
        setFunc(value)
      elif isinstance(varType, Enum):
        print "I: core.BaseWrapper.setParameter: enum type"
        for n, v in varType.items():
          if n == value:
            setFunc(v)
            return
        print "E: core.BaseWrapper.setParameter: invalid value %s for enum %s" % (value, varType.__name__)
      else:
        # this cannot be in here, node names (strings) can also be set and they must not be changed
        print "I: core.BaseWrapper.setParameter: converting", name, value
        if isinstance(value, str) or isinstance(value, unicode):
          value = tuple([float(i) for i in value.replace("(", "").replace(")", "").replace(" ", "").split(",")])
        
        if varType in [Vec4, Point4, VBase4, Point3, Vec3, VBase3, Point2, Vec2, VBase2]:
          setFunc(varType(*value))
        elif varType in [float, int, str, bool]:
          setFunc(varType(value))
        else:
          print "E: core.BaseWrapper.setParameter: unknown varType %s for %s" % (varType.__name__, name)
    except TypeError:
      print "E: core.BaseWrapper.setParameter: error handling %s in data:" % name
      raise
    print "D: core.BaseWrapper.setParameter:", self.getColor()
  
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
      #print "I: NodePathWrapper.loadFromData:", filepath, str(referencedFilename)
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
  
  def makeCopy(self, originalInstance):
    ''' create a copy of this instance
    '''
    newInstance = self(originalInstance.getParent(), originalInstance.getName())
    newInstance.setMat(originalInstance.getMat())
    newInstance.setParameters(originalInstance.getParameters())
    return newInstance
  makeCopy = classmethod(makeCopy)

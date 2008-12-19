import pickle, traceback, posixpath

from pandac.PandaModules import *
from direct.gui.DirectGui import *

from core.pModelIdManager import modelIdManager
from core.pConfigDefs import *
from core.pCommonPath import *

DEBUG = False

BASEWRAPPER_DATA_TAG = 'parameters'

class BaseWrapper(NodePath):
  def onCreateInstance(self, parent, name='BaseWrapper'):
    # create instance of this class
    objectInstance = self(parent, name)
    return objectInstance
  onCreateInstance = classmethod(onCreateInstance)
  
  def loadFromEggGroup(self, eggGroup, parent, filepath):
    if DEBUG:
      print "I: NodePathWrapper.loadFromEggGroup:"
    objectInstance = self(parent)
    return objectInstance
  loadFromEggGroup = classmethod(loadFromEggGroup)
  
  def __init__(self, parent, name):
    if DEBUG:
      print "I: BaseWrapper.__init__:", parent, name
    
    # get a uniq id for this object
    self.id = modelIdManager.getId()
    # define a name for this object
    name = '%s-%s' % (name, self.id)
    NodePath.__init__(self, name)
    # store this object
    modelIdManager.setObject(self, self.id)
    # reparent this nodePath
    if parent is None:
      parent = render
    self.reparentTo(parent)
    self.editModeEnabled = False
    
    self.mutableParameters = dict()
    self.mutableParameters['color'] = [ Vec4,
      self.getColor,
      self.setColor,
      self.hasColor ]
    self.mutableParameters['colorScale'] = [ Vec4,
      self.getColorScale,
      self.setColorScale,
      self.hasColorScale ]
    self.mutableParameters['transparency'] = [ bool,
      self.getTransparency,
      self.setTransparency,
      self.hasTransparency ]
    self.mutableParameters['name'] = [ str,
      self.getName,
      self.setName,
      True ]
  
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
      print "E: code.BaseWrapper.startEdit: object is not in editmode", self
  def stopEdit(self):
    # the object is deselected from being edited
    if not self.editModeEnabled:
      print "E: code.BaseWrapper.stopEdit: object is not in editmode", self
  
  def destroy(self):
    self.detachNode()
    self.removeNode()
  
  def getParameters(self):
    # get the data
    parameters = dict()
    for name, [varType, getFunc, setFunc, hasFunc] in self.mutableParameters.items():
      # should we read the value
      read = False
      if hasFunc: # it's true or a func
        read = True
        if hasFunc != True: # it's a func
          read = hasFunc()
      # store the parameters
      if read:
        #getFunc = getattr(self, getFuncName)
        if varType == Vec4 or varType == Point4:
          parameters[name] = (getFunc()[0], getFunc()[1], getFunc()[2], getFunc()[3])
        elif varType == Vec3 or varType == Point3:
          parameters[name] = (getFunc()[0], getFunc()[1], getFunc()[2])
        elif varType == Vec2 or varType == Point2:
          parameters[name] = (getFunc()[0], getFunc()[1])
        elif varType == float or varType == int or varType == str or varType == bool:
          parameters[name] = getFunc()
        else:
          print "E: BaseWrapper.getParameters: unknown varType %s for %s" % (varType.__name__, name)
    return parameters
  
  def setParameters(self, parameters):
    for name, [varType, getFunc, setFunc, hasFunc] in self.mutableParameters.items():
      if name in parameters:
        try:
          if varType == Vec4 or varType == Point4:
            setFunc(varType(*parameters[name]))
          elif varType == Vec3 or varType == Point3:
            setFunc(varType(*parameters[name]))
          elif varType == Vec2 or varType == Point2:
            setFunc(varType(*parameters[name]))
          elif varType == float or varType == int or varType == str or varType == bool:
            setFunc(varType(parameters[name]))
          else:
            print "E: BaseWrapper.setParameters: unknown varType %s for %s" % (varType.__name__, name)
        except TypeError:
          print "E: BaseWrapper.setParameters: error handling %s in data:" % name
          print parameters
          traceback.print_exc()
  
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
        nm.setCell( x, y, om.getCell(x,y) )
    # the matrix we define must be applied to the nodes in "local space"
    instance = EggGroup(name)
    instance.setGroupType(EggGroup.GTInstance)
    instance.setTransform3d( nm )
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
          exec("data = %s" % child.getComment())
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

__all__ = ['TreeNode']#, 'TreeParentNode']

import traceback

from pandac.PandaModules import *

from core.pConfigDefs import *

# name of the egg-tag where parameters are saved into
BASEWRAPPER_DATA_TAG = 'parameters'

'''
- TreeNode
  - BaseWrapper
    - VirtualNodeWrapper
      - LightNodeWrapper
        - AmbientLightNodeWrapper
        - PointLightNodeWrapper
        - SpotLightNodeWrapper
        - DirectionalLightNodeWrapper
      - CodeNodeWrapper
      - ParticleSystemWrapper
      - SceneNodeWrapper
      - SoundNodeWrapper
    - GeoMipTerrainNodeWrapper
  - ShaderWrapper
  - ObjectEggBase
    - ObjectEggGroup
    - ObjectEggData
    - ObjectEggPolygon
    - ObjectEggTexture
    - ObjectVertexPool
'''

EDITMODE_ENABLED = 1
EDITMODE_STARTED = 2

class TreeNode(object):
  ''' a treenode is a node in the structure
  features:
  - it only has the name parameter
  functionality's:
  - it stores parents and children (the structure of the tree)
  - it saves if a object is editable (editmode enabled/disabled)
  - functions for setting/getting parameters of a wrapper
  - saving and loading of the data
  - making instances of objects
  '''
  def __init__(self, treeName='parent'): #, treeData=None):
    self.treeParent = None
    self.treeChildren = list()
    self.treeName = treeName
    #self.treeData = treeData
    self.editmodeStatus = int()
    self.mutableParameters = dict()
    self.mutableParameters['name'] = [ str,
      self.getName,
      self.setName,
      None,
      None ]
  
  def destroy(self):
    self.stopEdit()
    self.setEditmodeDisabled()
    TreeNode.detachNode(self)
  
  # --- parenting functions ---
  def reparentTo(self, treeParent):
    self.detachNode()
    if treeParent not in self.getRecChildren():
      self.treeParent = treeParent
      if self.treeParent:
        self.treeParent.treeChildren.append(self)
    else:
      print "W: TreeNode.reparentTo: cannot reparent to TreeNode in children"
      print "  - self: '%s' parent: '%s'" % (str(self.treeName), str(parent.treeName))
      print "  - childrens:", [c.treeName for c in self]
  
  def detachNode(self):
    if self.treeParent:
      if self in self.treeParent.treeChildren:
        self.treeParent.treeChildren.remove(self)
    self.treeParent = None
    #self.treeData = None
    del self.treeChildren
    self.treeChildren = list()
  
  def getParent(self):
    return self.treeParent
  
  def getRecChildren(self):
    l = list()
    for child in self.treeChildren:
      l.append(child)
      l.extend(child.getRecChildren())
    return l
  
  def getChildren(self, index=None):
    ''' if index is defined, return a specific children
    if no index defined, return whole list of children'''
    if index is not None:
      if 0 <= index < len(self.treeChildren):
        return self.treeChildren[index]
      else:
        print "W: TreeNode.getChildren: invalid index", index, "for", self.treeChildren
    return self.treeChildren
  
  def getNumChildren(self):
    return len(self.treeChildren)
  
  def printTree(self, depth=0):
    print " "*depth+" -"+str(self.treeName)
    for treeChild in self.treeChildren:
      treeChild.printTree(depth+1)
  
  
  # --- name of the node ---
  def getName(self):
    return self.treeName
  
  def setName(self, name):
    self.treeName = name
  
  
  # --- EDIT MODE OF THE OBJECT ---
  def setEditmodeEnabled(self, recurseException=[]):
    # add the editmode flag (or)
    self.editmodeStatus = self.editmodeStatus | EDITMODE_ENABLED
    
    for child in self.getChildren():
      if recurseException is not None:
        if type(child) in recurseException:
          child.setEditmodeEnabled(None)
        else:
          child.setEditmodeEnabled(recurseException)
  
  def setEditmodeDisabled(self, recurseException=[]):
    # remove the editmode flag (xor)
    self.editmodeStatus = self.editmodeStatus ^ EDITMODE_ENABLED
    
    for child in self.getChildren():
      if recurseException is not None:
        if type(child) in recurseException:
          child.setEditmodeDisabled(None)
        else:
          child.setEditmodeDisabled(recurseException)
  
  def isEditmodeEnabled(self):
    return (self.editmodeStatus & EDITMODE_ENABLED)
  
  
  # --- EDIT STATUS OF THE OBJECT ---
  def startEdit(self):
    # the object is selected to be edited
    # creates a directFrame to edit this object
    if not self.isEditmodeEnabled():
      print "E: core.BaseWrapper.startEdit: object is not in editmode", self
    else:
      # add the startedit flag (or)
      self.editmodeStatus = self.editmodeStatus | EDITMODE_STARTED
  
  def stopEdit(self):
    # the object is deselected from being edited
    if not self.isEditmodeEnabled():
      print "E: core.BaseWrapper.stopEdit: object is not in editmode", self
    else:
      # remove the startedit flag (xor)
      self.editmodeStatus = self.editmodeStatus ^ EDITMODE_STARTED
  
  def isEditmodeStarted(self):
    return (self.editmodeStatus & EDITMODE_STARTED)
  
  
  # --- PARAMETER LOADING AND SAVING ---
  def getParameter(self, name):
    varType, getFunc, setFunc, hasFunc, clearFunc = self.mutableParameters[name]
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
      print "E: core.TreeNode.getParameter: invalid value %s for enum %s" % (val, varType.__name__)
    elif isinstance(varType, Bitmask):
      return val
    elif varType.__name__ == 'Filepath': #elif isinstance(varType, Filepath):
      return val
    elif varType.__name__ == 'Trigger':
      return val
    else:
      print "E: core.TreeNode.getParameter: unknown varType %s for %s" % (varType.__name__, name)
      print "  - value", str(val)
      print "  - varType", varType
  
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
    if name in self.mutableParameters:
      varType, getFunc, setFunc, hasFunc, clearFunc = self.mutableParameters[name]
      try:
        if clearFunc != None and (value == None or (isinstance(value, str) and value.lower() == "none")):
          clearFunc()
        elif isinstance(varType, type) and isinstance(value, varType):
          # It's already the correct type
          setFunc(value)
        elif isinstance(varType, Enum):
          for n, v in varType.items():
            if n == value:
              setFunc(v)
              return
          print "W: core.TreeNode.setParameter: invalid value %s for enum %s" % (value, varType.__name__)
        elif isinstance(varType, Bitmask):
          setFunc(value)
        elif varType.__name__ == 'Filepath': #isinstance(varType, Filepath):
          setFunc(value)
        elif varType.__name__ == 'Trigger':
          setFunc()
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
            print "E: core.TreeNode.setParameter: unknown varType %s for %s" % (varType.__name__, name)
      except TypeError:
        # this must be catched as it's a user input
        print "E: core.TreeNode.setParameter: error handling %s in data:" % name, value
        traceback.print_exc()
  
  def setParameters(self, parameters):
    for name, value in parameters.items():
      self.setParameter(name, value)


  # --- LOADING & SAVING TO FILES ---
  def getSaveData(self, relativeTo):
    # the given name of this object
    name = self.getName()
    # the matrix we define must be applied to the nodes in "local space"
    instance = EggGroup(name)
    # define the type of this object
    className = self.__class__.__name__
    instance.setTag(MODEL_WRAPPER_TYPE_TAG, className)
    
    # get all data to store in the eggfile
    parameters = self.getParameters()
    if len(parameters) > 0:
      # dont store those values into the parameters
      for paramName in ['name', 'position', 'scale', 'rotation']:
        if paramName in parameters:
          del parameters[paramName]
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
  
  
  def makeInstance(self, originalInstance):
    ''' create a copy of this instance
    '''
    newInstance = self(originalInstance.getParent(), originalInstance.getName()+"-copy")
    newInstance.nodePath.setMat(originalInstance.nodePath.getMat())
    newInstance.setParameters(originalInstance.getParameters())
    return newInstance
  makeInstance = classmethod(makeInstance)



if __name__ == '__main__':
  a = TreeNode('a', 1)
  b = TreeNode('b', 2)
  c = TreeNode('c', 2)
  b.reparentTo(a)
  c.reparentTo(b)
  print "a.getRecChildren()"
  for x in a.getRecChildren():
    print "  -", x.treeName
  
  # this must fail
  a.reparentTo(c)
  
  print [obj for obj in a.getRecChildren()]
  
  b.detachNode()
  
  #x = obj[1]
  
  import gc
  gc.collect()
  for c in gc.get_referrers(b):
    print "  -", c
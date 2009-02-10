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
    
    # all values that can be changed require a entry in the mutableParameters
    # when a value exists, it means that it's allowed to read/write the value
    # hasFunc defines if it's a vital property of the object and must be saved
    # into the comments
    # valueType, getFunc vtion, setFunction, hasFunction, clearFunction
    # hasFunction == None -> the value should be saved
    self.mutableParameters = dict()
    self.mutableParameters['name'] = [ str,
      self.getName,
      self.setName,
      None,
      None,
      False ]
    self.mutableParameters['parent'] = [ TreeNode,
      self.getParent,
      self.reparentTo,
      None,
      None,
      False ]
    
    # functions that can be done with this node
    self.possibleFunctions = [
        'destroy',
        'duplicate',
      ]
    
    # this would define what type of node may be attached to this node,
    # defining a empty list disallows any children from being attached
    # not defining it will make it search in any parent node for this parameter
    # add names of the classes to this list that may be attached
    # self.possibleChildrens = list()
    
    # path where this node is saved to, not defining it will make the function
    # call getParentFilepath search any parent node for a defined filepath
    # this data is used by child nodes to know which path they should save
    # relative to
    # self.treeFilepath = ''
    
    # a optional nodepath, allows any child nodepaths to find a place to attach
    # themself to
    # self.treeNodepath = Nodepath()
  
  def destroy(self):
    ''' # this should maybe run
    def recurse(parent):
      for child in parent.getChildren()[:]: # accessing it directly causes it to miss childrens
        recurse(child)
        child.destroy()
    recurse(self)'''
    self.stopEdit()
    self.setEditmodeDisabled()
    TreeNode.detachNode(self)
    del self.treeChildren
    self.treeChildren = list()
  
  # --- parenting functions ---
  def reparentTo(self, treeParent):
    if hasattr(treeParent, 'possibleChildren'):
      if self.__class__.__name__ in treeParent.getPossibleChildren():
        pass
      else:
        print "I: TreeNode.reparentTo: invalid parent for reparenting:"
        print "  - new parent:", treeParent, treeParent.__class__.__name__
        print "  - own type", self, self.__class__.__name__
        print "  - possible children:", treeParent.getPossibleChildren()
        return False
    if treeParent not in self.getRecChildren() and treeParent != self:
      self.detachNode()
      self.treeParent = treeParent
      if self.treeParent:
        self.treeParent.treeChildren.append(self)
      return True
    else:
      print "W: TreeNode.reparentTo: cannot reparent to TreeNode in children"
      print "  - self: '%s' parent: '%s'" % (str(self.getName()), str(treeParent.getName()))
      print "  - childrens:", [c.getName() for c in self.getRecChildren()]
    return False
  
  def detachNode(self):
    if self.treeParent:
      if self in self.treeParent.treeChildren:
        self.treeParent.treeChildren.remove(self)
    self.treeParent = None
  
  def getParent(self):
    return self.treeParent
  
  def getRecParents(self):
    ''' get a list of parents of this node, ordered from children upwards'''
    def rec(treeNode, parentList=list()):
      parentNode = treeNode.getParent()
      if parentNode is not None:
        parentList.append(parentNode)
        parentList = rec(parentNode, parentList)
      return parentList
    return rec(self)
  
  def getRecParentsAndSelf(self):
    ''' get a list of parents of this node, ordered from children upwards
    including self '''
    def rec(treeNode, parentList=list()):
      parentList.append(treeNode)
      parentNode = treeNode.getParent()
      if parentNode is not None:
        parentList = rec(parentNode, parentList)
      return parentList
    return rec(self)
  
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
  
  def getPossibleChildren(self):
    parentList = self.getRecParentsAndSelf()
    for parent in parentList:
      if hasattr(parent, 'possibleChildren'):
        return parent.possibleChildren
    return []
  
  
  # --- functions useful for the gui ---
  def getPossibleFunctions(self):
    '''includes functions like destroying of nodes, duplication of nodes
    could be integrated into the mutableparameters once, but then it would
    need a additional parameter if the data should be saved with the object
    most of this functions are actually triggers'''
    parentList = self.getRecParentsAndSelf()
    for parent in parentList:
      if hasattr(parent, 'possibleFunctions'):
        return parent.possibleFunctions
    return []
  
  
  # --- name of the node ---
  def getName(self):
    return self.treeName
  
  def setName(self, name):
    self.treeName = name
  
  def __repr__(self):
    text = "(%s) %s" % (str(self.className), str(self.getName()))
    return text
  
  
  # --- filepath operations ---
  ''' the filepath stores where a object is saved to,
  (absolue path including filename and extension)
  this information can be used by child nodes to calculate relative path's
  for theyr own files
  not all filepaths should be saved as filepath! only if all child nodes should
  store theyr filenames relative to this filepath it should be defined'''
  def getParentFilepath(self):
    # this gets a ordered list of our parents (upwards)
    parents = self.getRecParents()
    for parent in parents:
      if hasattr(parent, 'treeFilepath'):
        return parent.getFilepath()
  
  def setFilepath(self, filepath):
    assert( type(filepath) == str )
    self.treeFilepath = filepath
  def getFilepath(self):
    return self.treeFilepath
  def clearFilepath(self):
    del self.treeFilepath
  
  
  # --- nodepath operations ---
  ''' the nodepath stores any nodepath that child nodes should attach themself
  to '''
  def getParentNodepath(self):
    # this gets a ordered list of our parents (upwards)
    parents = self.getRecParents()
    for parent in parents:
      if parent.hasNodepath():
      #if hasattr(parent, 'treeNodepath'):
        return parent.getNodepath()
    return None
  
  def setNodepath(self, nodepath):
    self.treeNodepath = nodepath
  
  def getNodepath(self):
    return self.treeNodepath
  
  def hasNodepath(self):
    if hasattr(self, 'treeNodepath'):
      return True
    return False
  
  # --- EDIT MODE OF THE OBJECT ---
  ''' if a object has the editmodeEnabled, it's possible to modify it
  if it's disabled it means we are in rendering mode only, as few ressources
  as possible should be used '''
  def setEditmodeEnabled(self):
    # add the editmode flag (or)
    self.editmodeStatus = self.editmodeStatus | EDITMODE_ENABLED
    
    # recursively set the editmode
    for child in self.getChildren():
      child.setEditmodeEnabled()
  
  def setEditmodeDisabled(self):
    # remove the editmode flag (xor)
    self.editmodeStatus = self.editmodeStatus ^ EDITMODE_ENABLED
    
    # recursively set the editmode disabled
    for child in self.getChildren():
      child.setEditmodeDisabled()
  
  def isEditmodeEnabled(self):
    return (self.editmodeStatus & EDITMODE_ENABLED)
  
  
  # --- EDIT STATUS OF THE OBJECT ---
  ''' when editing is started it means that this object is currently
  highlighted / selected to be edited in the editor
  this can be:
  - painting on a texture
  - moving a node around
  - modifying a particle system
  - etc.'''
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
    ''' return the requested parameter of this node '''
    varType, getFunc, setFunc, hasFunc, clearFunc, varSave = self.mutableParameters[name]
    
    if (hasFunc != None and not hasFunc()) or getFunc == None:
      # if the hasfunc is defined, and it's false (the parameter has no value)
      # or the getFunc is not defined (for example in triggers)
      return None
    
    # read the value
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
    elif varType.__name__ == 'Filepath' or varType.__name__ == 'P3Filepath':
      return val
    elif varType.__name__ == 'Trigger':
      return val
    elif varType.__name__ == 'TreeNode':
      return val
    elif varType in [list, tuple]:
      return val
    else:
      print "E: core.TreeNode.getParameter: unknown varType %s for %s" % (varType.__name__, name)
      print "  - value", str(val)
      print "  - varType", varType
  
  def getParameters(self):
    ''' return a dict with all parameters that are defined (!None) '''
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
      varType, getFunc, setFunc, hasFunc, clearFunc, varSave = self.mutableParameters[name]
      try:
        if clearFunc != None and (value == None or (isinstance(value, str) and value.lower() == "none")):
          # if a clearfunc is defined, and the value is None or 'none', call the function
          clearFunc()
        elif isinstance(varType, type) and isinstance(value, varType):
          # it's already the correct type
          setFunc(value)
        elif isinstance(varType, Enum):
          for n, v in varType.items():
            if n == value:
              setFunc(v)
              return
          print "W: core.TreeNode.setParameter: invalid value %s for enum %s" % (value, varType.__name__)
        elif isinstance(varType, Bitmask):
          setFunc(value)
        elif varType.__name__ == 'Filepath':
          setFunc(value)
        elif varType.__name__ == 'P3Filepath':
          setFunc(Filename(value))
        elif varType.__name__ == 'Trigger':
          # the trigger just calls the function
          setFunc()
        elif varType in [list, tuple]:
          setFunc(value)
        else:
          # some fallback handling of input
          
          if isinstance(value, str) or isinstance(value, unicode):
            # try converting into a tuple
            try:
              value = tuple([float(i) for i in value.replace("(", "").replace(")", "").replace(" ", "").split(",")])
            except:
              print "E: core.BaseWrapper.setParameter: error converting string" % name, value
          
          # set the value
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
    ''' set all parameters defined in the given dict '''
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
      for paramName in parameters.keys():
        # dont store those values into the parameters
        if self.mutableParameters.has_key(paramName): # this should allways be the case
          varType, getFunc, setFunc, hasFunc, clearFunc, varSave = self.mutableParameters[paramName]
          if varSave:
            pass
          else:
            # is not defined to be saved
            if paramName in parameters:
              # remove from parameters
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
    newInstance.getNodepath().setMat(originalInstance.getNodepath().getMat())
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
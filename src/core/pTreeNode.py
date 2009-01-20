__all__ = ['TreeNode']#, 'TreeParentNode']

import traceback

from pandac.PandaModules import *

from core.pConfigDefs import *

class TreeNode(object):
  ''' a treenode is a node in the structure that defines what can be changed
  '''
  def __init__(self, treeName='parent', treeData=None):
    self.treeParent = None
    self.treeChildren = list()
    self.treeName = treeName
    self.treeData = treeData
    self.editmodeStatus = False
  
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
    self.treeData = None
    del self.treeChildren
    self.treeChildren = list()
  
  def getParent(self):
    return self.treeParent
  
  def getRecChildren(self):
    l = list()
    for child in self.treeChildren:
#      print child.treeName
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
  
  '''def __iter__(self):
    # iterate over self and all childrens
    yield self
    for treeChild in self.treeChildren:
      for childIter in treeChild:
        yield childIter'''
  
  def printTree(self, depth=0):
    print " "*depth+" -"+str(self.treeName)
    for treeChild in self.treeChildren:
      treeChild.printTree(depth+1)
  
  def getName(self):
    return self.treeName
  
  def setName(self, name):
    self.treeName = name
  
  
  def setEditmodeEnabled(self, recurseException=[]):
    self.editmodeStatus = True
    
    for child in self.getChildren():
      if recurseException is not None:
        if type(child) in recurseException:
          child.setEditmodeEnabled(None)
        else:
          child.setEditmodeEnabled(recurseException)
  
  def setEditmodeDisabled(self, recurseException=[]):
    self.editmodeStatus = False
    
    for child in self.getChildren():
      if recurseException is not None:
        if type(child) in recurseException:
          child.setEditmodeDisabled(None)
        else:
          child.setEditmodeDisabled(recurseException)
  
  def isEditmodeEnabled(self):
    return self.editmodeStatus
  
  
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


'''class TreeParentNode(TreeNode):
  #the parent node of all tree objects
  #is used by the Main to parent all nodes under this one
  def __init__(self, parentNodepath):
    TreeNode.__init__(self, 'root', None)
    self.name = 'root'
    self.mutableParameters = dict()
    self.nodePath = parentNodepath
  def startEdit(self):
    pass
  def stopEdit(self):
    pass'''



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
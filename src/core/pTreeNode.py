__all__ = ['TreeParentNode', 'TreeNode']



class TreeNode(object):
  ''' a treenode is a node in the structure that defines what can be changed
  '''
  def __init__(self, treeName='parent', treeData=None):
    self.treeParent = None
    self.treeChildren = list()
    self.treeName = treeName
    self.treeData = treeData
  
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


class TreeParentNode(TreeNode):
  ''' the parent node of all tree objects
  is used by the Main to parent all nodes under this one '''
  def __init__(self, parentNodepath):
    TreeNode.__init__(self, 'root', None)
    self.name = 'root'
    self.mutableParameters = dict()
    self.nodePath = parentNodepath
  def startEdit(self):
    pass
  def stopEdit(self):
    pass



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
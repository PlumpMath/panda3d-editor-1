class TreeNode:
  ''' a treenode is a node in the structure that defines what can be changed
  '''
  def __init__(self, name, data):
    self.parent = None
    self.children = list()
    self.name = name
    self.data = data
  
  def reparentTo(self, parent=None):
    self.detachNode()
    if parent not in self:
      self.parent = parent
      if self.parent:
        self.parent.children.append(self)
    else:
      print "W: TreeNode.reparentTo: cannot reparent to TreeNode in children"
      print "  - self: '%s' parent: '%s'" % (str(self.name), str(parent.name))
      print "  - childrens:", [c.name for c in self]
  
  def detachNode(self):
    if self.parent:
      self.parent.children.remove(self)
    self.parent = None
  
  def __iter__(self):
    yield self
    for a in self.children:
      for b in a:
        yield b
  
  def __repr__(self):
    return "'%s'/'%s'" % (str(self.name), str(self.data))

if __name__ == '__main__':
  a = TreeNode('a', 1)
  b = TreeNode('b', 2)
  c = TreeNode('c', 2)
  b.reparentTo(a)
  c.reparentTo(b)
  
  # this must fail
  a.reparentTo(c)
  
  print [obj for obj in a]
  
  
__all__=['DirectTreeItem', 'DirectTree']

from pandac.PandaModules import NodePath, LineSegs, TextNode
from direct.gui.DirectGui import DirectFrame,DirectButton,DirectScrolledFrame,DGG
from direct.showbase.DirectObject import DirectObject

EVENT_DIRECTTREE_REFRESH = 'directTree-update'

class DirectTreeItem(object):
  ''' a tree structure object, which has a parent and childrens
  '''
  def __init__(self,parent=None,name=''):
    self.name=name
    self.childrens=list()
    self.parent=None
    self.setParent(parent)
    self.open=True
    self.highlighted=False
    self.button1Func=None
    self.button2Func=None
    self.button3Func=None
  def setOpen(self, newState=None):
    ''' close this node, hiding it's children
    '''
    if newState is None:
      newState = not self.open
    self.open = newState
    messenger.send(EVENT_DIRECTTREE_REFRESH)
  def getShow(self):
    ''' calculate if this node should be shown
    if any parent is closed, it's hidden
    '''
    if self.parent:
      return (self.parent.getShow() & self.parent.open)
    return True
  def getDepth(self):
    ''' calculate depth in the tree structure '''
    if self.parent is None: return 0
    return self.parent.getDepth()+1
  def setName(self, name):
    self.name = name
  def setParent(self, parent):
    ''' set a new parent to this item '''
    # remove from previous parent
    if self.parent is not None:
      self.parent.removeChild(self)
      self.parent = None
    # add to new parent
    if parent is not None:
      assert(type(parent) == DirectTreeItem)
      # parent & child are iterators, so we can check "in"
      if parent not in self.getRec() and self not in parent.getRec() and self != parent:
        self.parent = parent
        self.parent.addChild(self)
      else:
        print "W: DirectTreeItem.setParent: already in some list"
  def destroy(self):
    self.setParent(None)
    self.clearChildrens()
    self.button1Func=None
    self.button2Func=None
    self.button3Func=None
  def __del__(self):
    pass
  def clearChildrens(self):
    for child in self.childrens:
      child.setParent(None)
    self.childrens = list()
  def addChild(self, child):
    if child not in self.childrens:
      self.childrens.append(child)
  def removeChild(self, child):
    if child in self.childrens:
      child.parent = None
      self.childrens.remove(child)
  def printChildren(self):
    print " "*self.getDepth()+["- ","+ "][self.open]+self.name, self.getShow() #, self.isParentOpen()
    for c in self.childrens:
      c.printChildren()
  def getRec(self):
    l = [self]
    for child in self.childrens:
      l.extend(child.getRec())
    return l
  def getRecChildren(self):
    l = list()
    for child in self.childrens:
      l.append(child)
      l.extend(child.getRecChildren())
    return l
  '''def __iter__(self):
    yield self
    for a in self.childrens:
      for b in a:
        yield b'''
  def button1press(self, *args):
    if self.button1Func:
      self.button1Func(self)
  def button2press(self, *args):
    if self.button2Func:
      self.button2Func(self)
  def button3press(self, *args):
    if self.button3Func:
      self.button3Func(self)

class DirectTree(DirectObject):
  def __init__(self,
               pos=(0,0,0),
               parent=None,
               frameSize=(1,1),
               treeStructure=DirectTreeItem(),):
    if parent is None:
      parent = aspect2d
    self.treeStructure = treeStructure
    self.treeStructureNodes = dict()
    
    self.highlightedNodes = list()
    
    self.frameWidth = frameSize[0] #0.8
    self.frameHeight = frameSize[1] #1.5
    
    self.itemIndent = 0.05
    self.itemScale = 0.03
    self.itemTextScale = 1.2
    self.verticalSpacing = 0.0375
    self.__createTreeLines()
    
    self.childrenFrame = DirectScrolledFrame(
        parent=parent,pos=pos,
        relief=DGG.GROOVE,
        state=DGG.NORMAL, # to create a mouse watcher region
        manageScrollBars=0,
        enableEdit=0,
        #suppressMouse=1,
        sortOrder=1000,
        frameColor=(0,0,0,.7),
        borderWidth=(0.005,0.005),
        frameSize =(0, self.frameWidth, 0, self.frameHeight),
        canvasSize=(0, self.frameWidth-self.itemScale*2, 0, self.frameHeight),
        verticalScroll_frameSize   = [0,self.itemScale,0,1],
        horizontalScroll_frameSize = [0,1,0,self.itemScale],
      )
    self.childrenCanvas=self.childrenFrame.getCanvas().attachNewNode('myCanvas')
    self.childrenCanvas.setX(0.05)
    self.childrenCanvas.setZ(self.frameHeight-1) # some fix to have the list in the window
    
    self.accept(EVENT_DIRECTTREE_REFRESH, self.update)
  
  def destroy(self):
    self.treeStructure = DirectTreeItem()
    self.render()
    self.childrenFrame.destroy()
    #del self.treeStructureNodes
  
  def __createLine(self, length=1, color=(1,1,1,1), endColor=None):
    LS=LineSegs()
    LS.setColor(*color)
    LS.moveTo(0,0,0)
    LS.drawTo(length*1,0,0)
    node=LS.create()
    if endColor:
      LS.setVertexColor(1,*endColor)
    return node
  def __createTreeLines(self):
    # create horisontal tree line
    color=(1,0,0,.9)
    self.horizontalTreeLine=NodePath(self.__createLine(
      self.itemIndent+self.itemScale*.5,
      color,endColor=(1,1,1,.1)))
    self.horizontalTreeLine.setTwoSided(0,100)
    self.horizontalTreeLine.setTransparency(1)
    # create vertical tree line
    self.verticalTreeLine=NodePath(self.__createLine(
      self.verticalSpacing,color))
    self.verticalTreeLine.setR(90)
    self.verticalTreeLine.setTwoSided(0,100)
    self.verticalTreeLine.setTransparency(1)
  
  def render(self):
    ''' traverse the tree and update the visuals according to it
    '''
    for treeItem in self.treeStructure.getRec():
      # create nodes that have no visual elements
      if not treeItem in self.treeStructureNodes:
        treeNode = self.childrenCanvas.attachNewNode('')
        
        hor=self.horizontalTreeLine.instanceUnderNode(treeNode,'')
        vert=self.verticalTreeLine.instanceUnderNode(treeNode,'')
        vert.setZ(0.007)
        hor.setPos(-1.5*self.itemIndent,0,self.itemScale*.25)
        vert.setX(-.5*self.itemIndent)
        
        nodeButton = DirectButton(
            parent=treeNode,
            scale=self.itemScale,
            relief=DGG.FLAT,
            text_scale=self.itemTextScale,
            text_align=TextNode.ALeft,
            text=treeItem.name,
            rolloverSound=None,
            #clickSound=None,
          )
        nodeButton.bind(DGG.B1PRESS,treeItem.button1press)
        nodeButton.bind(DGG.B2PRESS,treeItem.button2press)
        nodeButton.bind(DGG.B3PRESS,treeItem.button3press)
        
        #treeButton = None
        #if len(treeItem.childrens) > 0:
        treeButton = DirectButton(
            parent=nodeButton,
            frameColor=(1,1,1,1),
            frameSize=(-.4,.4,-.4,.4),
            pos=(-.5*self.itemIndent/self.itemScale,0,.25),
            text='',
            text_pos=(-.1,-.22),
            text_scale=(1.6,1),
            text_fg=(0,0,0,1),
            enableEdit=0,
            command=treeItem.setOpen,
            sortOrder=1000,
            rolloverSound=None,
            #clickSound=None,
          )
        

        self.treeStructureNodes[treeItem] = [treeNode, nodeButton, treeButton, hor, vert]
    
    # destroy nodes no more used
    for treeItem in self.treeStructureNodes.keys()[:]:
      #treeItem = self.treeStructureNodes[treeName]
      if treeItem not in self.treeStructure.getRec():
        treeNode, nodeButton, treeButton, hor, vert = self.treeStructureNodes[treeItem]
        #nodeButton['text']=''
        nodeButton.unbind(DGG.B1PRESS)
        nodeButton.unbind(DGG.B2PRESS)
        nodeButton.unbind(DGG.B3PRESS)
        #nodeButton.detachNode()
        #nodeButton.removeNode()
        nodeButton.destroy()
        if treeButton:
          #treeButton['text']=''
          #treeButton['command']=None
          treeButton.detachNode()
          treeButton.removeNode()
        hor.detachNode()
        hor.removeNode()
        vert.detachNode()
        vert.removeNode()
        treeItem.destroy()
        #treeNode.detachNode()
        treeNode.removeNode()
        #treeNode.destroy()
        del self.treeStructureNodes[treeItem]
    
    frameHeight = len(self.treeStructureNodes) * self.verticalSpacing
    self.childrenFrame['canvasSize'] = (0, self.frameWidth-self.itemScale*2, 0, frameHeight)
    self.childrenCanvas.setZ(frameHeight-1)
  
  def highlight(self, selectedTreeNodes):
    for treeNode in self.highlightedNodes:
      treeNode.highlighted = False
    self.highlightedNodes = selectedTreeNodes
    for treeNode in self.highlightedNodes:
      treeNode.highlighted = True
    self.update()
  
  def update(self):
    ''' update the tree, updating the positions and hidden status of childrens
    '''
    idx = 0
    for treeItem in self.treeStructure.getRec():
      # show or hide the items
      treeNode, nodeButton, treeButton, hor, vert = self.treeStructureNodes[treeItem]
      if treeItem.getShow():
        treeNode.show()
        vert.show()
        if treeItem.parent: # dont show the horizontal line on the parent
          hor.show()
        else:
          hor.hide()
        idx += 1
      else:
        treeNode.hide()
        hor.hide()
        vert.hide()
      
      if len(treeItem.childrens) > 0:
        treeButton.show()
      else:
        treeButton.hide()
      
      if treeItem.highlighted:
        nodeButton['text_fg'] = (1,0,0,1)
      else:
        nodeButton['text_fg'] = (0,0,0,1)
      
      # update the vertical position of the node
      treeNode.setPos(treeItem.getDepth()*self.itemIndent,0,1-idx*self.verticalSpacing)
      
      # if the tree element has a treebutton (if it has childrens), update the +/-
      if treeButton:
        # update the text for the open/close button
        tag = ['+','-'][treeItem.open]
        treeButton['text']=tag
      
      # calculate length to the last children with the same depth as this treeitem
      # this gives the length of the vertical line
      c = -1; i = 0; treeItemDepth = treeItem.getDepth()
      for recItem in treeItem.getRec():
        if recItem.getShow():
          c+=1
        if recItem.getDepth() == treeItemDepth+1:
          i = c
      vert.setSz(i)

if __name__ == '__main__' and False:
  from string import ascii_letters
  from random import choice
  
  # create a random testing structure
  d = dict()
  for c in ascii_letters[:]:
    if len(d) > 0:
      parent = d[choice(d.keys())]
    else:
      parent = None
    print "creating", c
    d[c] = DirectTreeItem(parent, c*20)
  
  if False:
    # testing without gui
    for c in ascii_letters[:]:
      d[c].setParent(d['a'])
    for key in d.keys()[:]:
      d[key].destroy()
  else:
    # testing with gui
    from direct.directbase import DirectStart
    x = DirectTree(treeStructure=d['a'])
    x.render()
    x.update()
    x.treeStructure = d['C']
    x.render()
    x.update()
    x.destroy()
  
  import gc
  print len(gc.get_objects())
  del d
  gc.collect()
  gc.collect()
  print len(gc.get_objects())
  gc.collect()
  gc.collect()
  print len(gc.get_objects())
  for i in xrange(100):
    gc.collect()
  print len(gc.get_objects())

if __name__ == '__main__' and False:
  print "testing tree structure"
  
  from string import ascii_letters
  from random import choice
  
  # create a random testing structure
  d = dict()
  for c in ascii_letters[:]:
    if len(d) > 0:
      parent = d[choice(d.keys())]
    else:
      parent = None
    d[c] = DirectTreeItem(parent, c*20)
  
  from direct.directbase import DirectStart
  
  x = DirectTree(treeStructure=d['a'])
  x.render()
  x.update()
  
  for c in ascii_letters[:]:
    d[c].setParent(d['a'])
  
  for key in d.keys()[:]:
    d[key].destroy()
  del d
  x.destroy()
  x.render()
  x.update()
  import gc
  print len(gc.get_objects())
  gc.collect()
  gc.collect()
  print len(gc.get_objects())
  while True:
    gc.collect()
    #pass

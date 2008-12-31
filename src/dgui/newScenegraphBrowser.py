from pandac.PandaModules import *
from direct.gui.DirectGui import DirectFrame,DirectButton,DirectScrolledFrame,DGG
from direct.showbase.DirectObject import DirectObject

EVENT_DIRECTTREE_REFRESH = 'directTree-update'

class TreeItem(object):
  def __init__(self,parent=None,name=''):
    self.name=name
    self.childrens=list()
    self.parent=None
    self.setParent(parent)
    self.open=True
  def toggleClose(self, state=None):
    if state is None:
      state = not self.open
    self.open = state
    messenger.send(EVENT_DIRECTTREE_REFRESH)
  '''def getShow(self):
    # if any parent is closed, dont show
    if not self.parent:
      return True
    # we have a parent
    return self.isParentOpen() #parent.getShow()
    #if not self.open:
    #  
    #return True
    # if self is closed show
  def isParentOpen(self):
    if self.parent:
      return (self.parent.isParentOpen() & self.parent.open)
      #return (self.open & self.parent.open)
    return True'''
  def getShow(self):
    if self.parent:
      return (self.parent.getShow() & self.parent.open)
    return True
  def getDepth(self):
    ''' calculate depth in the tree structure '''
    if self.parent is None: return 0
    return self.parent.getDepth()+1
  def setParent(self, parent):
    ''' set a new parent to this item '''
    # remove from previous parent
    if self.parent is not None:
      assert(type(self.parent) == TreeItem)
      self.parent.removeChild(self)
      self.parent = None
    # add to new parent
    if parent is not None:
      assert(type(parent) == TreeItem)
      childList = self.getRecursiveChildrens()
      parentChildList = parent.getRecursiveChildrens()
      #print childList, parentChildList
      if parent not in childList and self not in parentChildList and self != parent:
        self.parent = parent
        self.parent.addChild(self)
      else:
        print "W: TreeItem.setParent: already in some list"
  def deleteChildren(self):
    for child in self.getRecursiveChildrens():
      print "deleting", child.name
      child.setParent(None)
  def addChild(self, child):
    self.childrens.append(child)
  def removeChild(self, child):
    self.childrens.remove(child)
  def getRecursiveChildrens(self):
    childList = self.childrens[:]
    for c in self.childrens:
      childList.extend(c.getRecursiveChildrens())
    return childList
  def printChildren(self):
    print " "*self.getDepth()+["- ","+ "][self.open]+self.name, self.getShow() #, self.isParentOpen()
    for c in self.childrens:
      c.printChildren()
  def __iter__(self):
    yield self
    for a in self.childrens:
      for b in a:
        yield b

class DirectTree(DirectObject):
  def __init__(self, parent=None, treeStructure=TreeItem()):
    if parent is None:
      parent = aspect2d
    self.treeStructure = treeStructure
    self.treeStructureNodes = dict()
    
    frameWidth = 0.5
    frameHeight = 0.5
    
    self.itemIndent = 0.05
    self.itemScale = 0.04
    self.itemTextScale = 1.2
    self.verticalSpacing = 0.05
    self.__createTreeLines()
    
    '''self.childrenFrame = DirectScrolledFrame(
                 parent=parent,pos=(0.06,0,0), relief=DGG.GROOVE,
                 state=DGG.NORMAL, # to create a mouse watcher region
                 frameSize=(0, frameWidth, frameHeight, 0), frameColor=(0,0,0,.7),
                 canvasSize=(0, 0, -frameHeight*.5, 0), borderWidth=(0.01,0.01),
                 manageScrollBars=0, enableEdit=0, #suppressMouse=DEFAULT_SUPRESS_MOUSE_OVER_GUI,
                 sortOrder=1000 )
    self.childrenCanvas=self.childrenFrame.getCanvas().attachNewNode('myCanvas')'''
    self.childrenFrame = DirectFrame(
                 parent=parent,pos=(0,0,-.5), relief=DGG.GROOVE,
                 state=DGG.NORMAL, # to create a mouse watcher region
                 frameSize=(0, frameWidth, frameHeight, 0), frameColor=(0,0,0,.7),
                 #canvasSize=(0, 0, -frameHeight*.5, 0), borderWidth=(0.01,0.01),
                 #manageScrollBars=0, enableEdit=0,
                 sortOrder=1000 )
    self.childrenCanvas = self.childrenFrame
    
    self.accept(EVENT_DIRECTTREE_REFRESH, self.update)
  
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
    for treeItem in self.treeStructure:
      #print "creating node for", treeItem.name
      treeNode = self.childrenCanvas.attachNewNode('')
      
      nodeButton = DirectButton(parent=treeNode,
          scale=self.itemScale, relief=DGG.FLAT,
          text_scale=self.itemTextScale,
          text=treeItem.name, #text_fg=textColors[c.editable],
          #text_font=self.font,
          text_align=TextNode.ALeft,
          #command=self.__selectSGitem,extraArgs=[c],
          #enableEdit=0, suppressMouse=DEFAULT_SUPRESS_MOUSE_OVER_GUI
        )
      if len(treeItem.childrens) > 0:
        treeButton = DirectButton(parent=nodeButton,
            frameColor=(1,1,1,1),frameSize=(-.4,.4,-.4,.4),
            pos=(-.5*self.itemIndent/self.itemScale,0,.25),
            text='', text_pos=(-.1,-.22), text_scale=(1.6,1), text_fg=(0,0,0,1),
            enableEdit=0, #suppressMouse=DEFAULT_SUPRESS_MOUSE_OVER_GUI,
            #command=self.__collapseTreeNupdate,extraArgs=[idx]
            command=treeItem.toggleClose
          )
      hor=self.horizontalTreeLine.instanceUnderNode(treeNode,'')
      hor.setPos(-1.5*self.itemIndent,0,self.itemScale*.25)
      vert=self.verticalTreeLine.instanceUnderNode(treeNode,'')
      vert.setX(-.5*self.itemIndent)
      self.treeStructureNodes[treeItem] = [treeNode, nodeButton, treeButton, hor, vert]
  
  def update(self):
    ''' update the tree, hiding childrens that are hidden with the lines shown
    '''
    self.treeStructure.printChildren()
    
    idx = 0
    for treeItem in self.treeStructure:
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
      tag = ['+','-'][treeItem.open]
      treeButton['text']=tag
      treeNode.setPos(treeItem.getDepth()*self.itemIndent,0,1-idx*self.verticalSpacing)
      
      # calculate length to the last children with the same depth as this treeitem
      height=len(treeItem.getRecursiveChildrens())
      c = -1; i = 0; treeItemDepth = treeItem.getDepth()
      for recItem in treeItem:
        if recItem.getShow():
          c+=1
        if recItem.getDepth() == treeItemDepth+1:
          print recItem.getDepth(), treeItemDepth+1, "equal", recItem.name, c
          i = c
        else:
          print recItem.getDepth(), treeItemDepth+1, "unequal"
      vert.setSz(i)

if __name__ == '__main__':
  print "testing tree structure"
  #a = TreeItem(None, 'a')
  from string import ascii_letters
  from random import choice
  d = dict()
  for c in ascii_letters[:]:
    if len(d) > 0:
      parent = d[choice(d.keys())]
    else:
      parent = None
    print c, parent
    d[c] = TreeItem(parent, c)
    #(ascii_letters)
  a = d['a']
  
  print "for"
  for item in a:
    print item.name
  print "end"
  
  from direct.directbase import DirectStart
  x = DirectTree(treeStructure=a)
  x.render()
  x.update()
  run()
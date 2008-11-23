from pandac.PandaModules import TextNode, Vec3
from direct.gui.DirectGui import DirectFrame,DirectButton,DirectScrolledFrame,DGG

from core.pWindow import WindowManager
if __name__ == '__main__':
  # to test the directWindow independantly
  WindowManager.startBase(showDefaultWindow = True, allowMultipleWindows = False)

# define model path, required if this settings is missing in the Config.pp
from pandac.PandaModules import *
for path in ['../data', './dgui/directWindow/data']:
  getModelPath( ).appendPath( path )


DEFAULT_TITLE_TEXTURE_LEFT   = 'titleLeft.png'
DEFAULT_TITLE_TEXTURE_CENTER = 'titleCenter.png'
DEFAULT_TITLE_TEXTURE_RIGHT  = None
DEFAULT_TITLE_GEOM_RIGHT  = 'titleRight.egg'
DEFAULT_RESIZE_GEOM       = 'resize.png'


Y_INVERTED = True

class DirectWindow( DirectFrame ):
  def __init__( self
              , pos         = ( -.5, .5)
              , title       = 'Title'
              , bgColor  = (.5,.5,.5,1)
              , buttonColor = (1,1,1,1) #( .6, .6, .6, 1 )
              #, minSize     = ( .5, .5 )
              #, maxSize     = ( 1, 1 )
              , minWindowSize = (0,0)
              , maxWindowSize = (10000,10000)
              , virtualSize = (1,1)
              , windowBorderTextureFiles = [ DEFAULT_TITLE_TEXTURE_LEFT
                                       , DEFAULT_TITLE_TEXTURE_CENTER
                                       , DEFAULT_TITLE_TEXTURE_RIGHT
                                       , DEFAULT_RESIZE_GEOM ]
              , windowBorderGeomFiles = [ DEFAULT_TITLE_GEOM_RIGHT ]
              , windowColors    = [ ( 1, 1, 1, 1 )
                                  , ( 1, 1, 1, 1 )
                                  , ( 1, 1, 1, 1 )
                                  , ( 1, 1, 1, 1 ) ]
              , borderSize = 0.01
              , dragbarSize = 0.05
              , parent=None):
    self.windowPos = pos
    self.minWindowSize = minWindowSize
    self.maxWindowSize = maxWindowSize
    self.virtualSize = virtualSize
    self.borderSize = borderSize
    self.dragbarSize = dragbarSize
    
    if parent is None:
      parent=aspect2d
    self.parent=parent
    
    self.previousSize = (10,10)
    self.collapsed = False
    
    # maybe we should check if aspect2d doesnt already contain the aspect2dMouseNode
    self.mouseNode = self.parent.attachNewNode( 'aspect2dMouseNode', sort = 999999 )
    taskMgr.add( self.mouseNodeTask, 'mouseNodeTask' )
    
    windowBorderTextures = list()
    for windowBorder in windowBorderTextureFiles:
      if windowBorder is not None:
        mdlFile = loader.loadTexture(windowBorder)
        windowBorderTextures.append(mdlFile)
      else:
        windowBorderTextures.append(None)
    windowBorderGeoms = list()
    for windowGeom in windowBorderGeomFiles:
      if windowGeom is not None:
        mdlFile = loader.loadModel(windowGeom)
        print mdlFile.ls()
        mdls = ( mdlFile.find('**/**-default'),
                 mdlFile.find('**/**-click'),
                 mdlFile.find('**/**-rollover'),
                 mdlFile.find('**/**-disabled') )
        print "I: DirectWindow: button geoms:", mdls
        windowBorderGeoms.append(mdls)
      else:
        windowBorderGeoms.append((None,None,None,None,),)
    
    # the main window we want to move around
    self.parentWindow = DirectFrame(
      parent=self.parent, pos=(self.windowPos[0], 0, self.windowPos[1]),
      #frameSize=# is defined in resize
      scale=(1, 1, -1),
      frameColor=bgColor,
      borderWidth=(0, 0), relief=DGG.FLAT, sortOrder=1, )
    
    # header of the window (drag&drop with it)
    # the title part of the window, drag around to move the window
    self.headerParent = DirectButton(
        parent=self.parentWindow, pos=(0, 0, 0), 
        #frameSize=# is defined in resize
        scale=(1, 1, self.dragbarSize),
        frameColor=(1, 1, 1, 1), 
        borderWidth=(0, 0), relief=DGG.FLAT, )
    self.headerParent.bind(DGG.B1PRESS,self.startWindowDrag)
    # images in the headerParent
    self.headerCenter = DirectFrame(
        parent=self.headerParent, pos=(0, 0, 1),
        #frameSize=# is defined in resize
        scale=(1,1,-1),
        frameColor=windowColors[1], frameTexture=windowBorderTextures[1],
        borderWidth=(0, 0), relief=DGG.FLAT, )
    self.headerLeft = DirectFrame(
        parent=self.headerParent, pos=(0, 0, 1),
        frameSize=(0, self.dragbarSize, 0, 1), scale=(1,1,-1),
        frameColor=windowColors[0], frameTexture=windowBorderTextures[0],
        borderWidth=(0, 0), relief=DGG.FLAT, )
    # collapse button
    self.headerRight = DirectButton(
        parent=self.headerParent, #pos=# is defined in resize
        frameSize=(0, self.dragbarSize, 0, 1), scale=(1,1,-1),
        frameColor=windowColors[2], #frameTexture=windowBorderTextures[2],
        borderWidth=(0, 0), relief=DGG.FLAT,
        command=self.toggleCollapsed,
        geom=windowBorderGeoms[0], geom_scale=(self.dragbarSize,1,1) )
    # the resize button of the window
    self.resizeButton = DirectButton(
        parent=self.parentWindow, pos=(1-self.dragbarSize, 0, 1),
        frameSize=(0, 1, 0, 1), scale=(self.dragbarSize,1,-self.dragbarSize),
        frameColor=windowColors[3], frameTexture=windowBorderTextures[3],
        borderWidth=(0, 0), relief=DGG.FLAT, sortOrder=1, )
    self.resizeButton.bind(DGG.B1PRESS,self.startResizeDrag)
    # text in the center of the window
    text = TextNode('WindowTitleTextNode')
    text.setText(title)
    text.setAlign(TextNode.ACenter)
    text.setTextColor( 0, 0, 0, 1 )
    text.setShadow(0.05, 0.05)
    text.setShadowColor( 1, 1, 1, 1 )
    self.textNodePath = self.headerCenter.attachNewNode(text)
    self.textNodePath.setPos(.5,0,.3)
    self.textNodePath.setScale(0.8*self.dragbarSize,1,0.8)
    
    if Y_INVERTED:
      scale = (1,1,-1)
    else:
      scale = (1,1,1)
    # the content part of the window, put stuff beneath
    # contentWindow.getCanvas() to put it into it
    self.contentWindow = DirectScrolledFrame(
        parent       = self.parentWindow,
        #pos          = # is defined in resize
        scale        = scale,
        canvasSize   = (0,self.virtualSize[0],0,self.virtualSize[1]),
        frameColor   = buttonColor,
        relief       = DGG.RAISED,
        borderWidth  = (0,0),
        verticalScroll_frameSize                = [0,self.dragbarSize,0,1],
        verticalScroll_frameTexture             = loader.loadTexture( 'rightBorder.png' ),
        verticalScroll_incButton_frameTexture   = loader.loadTexture( 'scrollDown.png' ),
        verticalScroll_decButton_frameTexture   = loader.loadTexture( 'scrollDown.png' ),
        verticalScroll_thumb_frameTexture       = loader.loadTexture( 'scrollBar.png' ),
        horizontalScroll_frameSize              = [0,1,0,self.dragbarSize],
        horizontalScroll_frameTexture           = loader.loadTexture( 'bottomBorder.png' ),
        horizontalScroll_incButton_frameTexture = loader.loadTexture( 'scrollDown.png' ),
        horizontalScroll_decButton_frameTexture = loader.loadTexture( 'scrollDown.png' ),
        horizontalScroll_thumb_frameTexture     = loader.loadTexture( 'scrollBar.png' ),
      )
    DirectFrame.__init__( self,
        parent       = self.contentWindow.getCanvas(),
        pos          = (0,0,self.virtualSize[1]),
        scale        = (1,1,1),
        frameSize    = ( 0, self.virtualSize[0]+2*self.borderSize, 0, self.virtualSize[1] ),
        #frameColor   = (0,0,0,1),
        relief       = DGG.RIDGE,
        borderWidth  = (0,0),
        )
    self.initialiseoptions(DirectWindow)
    
    # offset then clicking on the resize button from the mouse to the resizebutton
    # position, required to calculate the position / scaling
    self.offset = None
    self.resizeButtonTaskName = "resizeTask-%s" % str(hash(self))
    
    # do sizing of the window to virtualSize
    #self.resize( self.virtualSize[0]+2*self.borderSize
    #           , self.virtualSize[1]+self.dragbarSize+2*self.borderSize )
    self.resize(10,10)
  
  # a task that keeps a node at the position of the mouse-cursor
  def mouseNodeTask(self, task):
    if WindowManager.hasMouse():
      x=WindowManager.getMouseX()
      y=WindowManager.getMouseY()
      # the mouse position is read relative to render2d, so set it accordingly
      self.mouseNode.setPos( render2d, x, 0, y )
    return task.cont
  
  # dragging functions
  def startWindowDrag( self, param ):
    print "I: DirectWindow.startWindowDrag"
    self.parentWindow.wrtReparentTo( self.mouseNode )
    self.ignoreAll()
    self.accept( 'mouse1-up', self.stopWindowDrag )
  def stopWindowDrag( self, param=None ):
    # this could be called even after the window has been destroyed
    #if self:
    # this is called 2 times (bug), so make sure it's not already parented to aspect2d
    if self.parentWindow.getParent() != self.parent:
      self.parentWindow.wrtReparentTo(self.parent)
    self.ignoreAll()
  
  # resize functions
  def startResizeDrag(self, param):
    self.offset = self.resizeButton.getPos(aspect2d) - self.mouseNode.getPos(aspect2d)
    taskMgr.remove( self.resizeButtonTaskName )
    taskMgr.add( self.resizeButtonTask, self.resizeButtonTaskName )
    self.accept( 'mouse1-up', self.stopResizeDrag,['x'] )
  def resize(self,windowX,windowY):
    # limit max/min size of the window
    maxX = min(self.maxWindowSize[0], self.virtualSize[0]+2*self.borderSize)
    minX = max( self.dragbarSize*3, self.minWindowSize[0])
    windowWidth = min( maxX, max( minX, windowX ) )
    maxY = min( self.maxWindowSize[1], self.virtualSize[1]+self.dragbarSize+2*self.borderSize )
    minY = max( self.dragbarSize*4, self.minWindowSize[1])
    windowHeight = min( maxY, max( minY, windowY ) )
    if self.collapsed:
      windowHeight = 2*self.dragbarSize+2*self.borderSize
      windowWidth = windowWidth
      self.contentWindow.hide()
      # store changed window width only
      self.previousSize = windowWidth, self.previousSize[1]
    else:
      self.contentWindow.show()
      self.previousSize = windowWidth, windowHeight
    # set the window size
    self.headerParent['frameSize'] = (0, windowWidth, 0, 1)
    self.headerCenter['frameSize'] = (0, windowWidth, 0, 1)
    self.parentWindow['frameSize'] = (0, windowWidth, 0, windowHeight)
    self.contentWindow['frameSize'] = (0, windowWidth-self.borderSize*2, 0, windowHeight-self.dragbarSize-2*self.borderSize)
    self.contentWindow.setPos(self.borderSize,0,windowHeight-self.borderSize)
    self.headerRight.setPos(windowWidth-self.dragbarSize, 0, 1)
    self.textNodePath.setPos(windowWidth/2.,0,.3)
    self.resizeButton.setPos(windowWidth-self.dragbarSize, 0, windowHeight)
  def resizeButtonTask(self, task=None):
    mPos = self.mouseNode.getPos(self.parentWindow)
    # max height, the smaller of (given maxWindowSize and real size of content and borders
    windowX = mPos.getX() + self.offset.getX() + self.dragbarSize
    windowY = mPos.getZ() - self.offset.getZ()
    self.resize(windowX,windowY)
    return task.cont
  def stopResizeDrag(self, param):
    taskMgr.remove( self.resizeButtonTaskName )
    self.ignoreAll()
  
  
  # a bugfix for a wrong implementation
  def detachNode( self ):
    self.parentWindow.detachNode()
    #self. = None
    #DirectFrame.detachNode( self )
  def removeNode( self ):
    self.parentWindow.removeNode()
    #DirectFrame.removeNode( self )
  
  def toggleCollapsed(self,state=None):
    if state is None:
      state=not self.collapsed
    print "I: DirectWindow.toggleCollapsed:", state
    if state:
      self.collapse()
    else:
      self.uncollapse()
  def collapse(self):
    self.collapsed = True
    self.resize(*self.previousSize)
  def uncollapse(self):
    self.collapsed = False
    self.resize(*self.previousSize)



if __name__ == '__main__':
  # a first window
  vx = 0.5
  vy = 1.5
  s = 0.1
  window1 = DirectWindow( title='window1', pos = ( -1.23, 0.9), virtualSize=(vx,vy))
  windowContent = DirectButton(
      parent     = window1,
      pos        = (0.1,0,-1.4),
      frameSize  = (0,0.3,0,1.3),
      relief     = DGG.FLAT,
      frameColor = (0,0,0,1),
      )
  windowContent = DirectButton(
      parent     = window1,
      pos        = (.05,0,.05),
      frameSize  = (0,s,0,s),
      relief     = DGG.FLAT,
      frameColor = (1,0,0,1),
      )
  windowContent = DirectButton(
      parent     = window1,
      pos        = (vx-s-.1,0,.05),
      frameSize  = (0,s,0,s),
      relief     = DGG.FLAT,
      frameColor = (0,1,0,1),
      )
  windowContent = DirectButton(
      parent     = window1,
      pos        = (.05,0,vy-s-.1),
      frameSize  = (0,s,0,s),
      relief     = DGG.FLAT,
      frameColor = (0,0,1,1),
      )
  
  '''# a second window
  window2 = DirectWindow( title='window2', pos = ( -.4, .4), virtualSize= (1.5,1.5) )
  windowContent = DirectButton(
      parent     = window2,
      pos        = (.6,0,.6),
      frameSize  = (-.5,.5,-.5,.5),
      relief     = DGG.FLAT,
      frameColor = (0,1,1,1),
      )'''
  
  # a second window
  window3 = DirectWindow( title='window3', pos=(-.8,1), virtualSize=(1.8,1.8) )
  windowContent = DirectButton(
      parent     = window3,
      pos        = (.5,0,.5),
      frameSize  = (-.5,.5,-.5,.5),
      relief     = DGG.FLAT,
      frameColor = (0,1,1,1),
      scale      = 0.5,)
  window4 = DirectWindow( title='window3-child', pos=(.1,-1), parent=window3 )
  windowContent = DirectButton(
      parent     = window4,
      pos        = (-.5,0,-.5),
      frameSize  = (-.5,.5,-.5,.5),
      relief     = DGG.FLAT,
      frameColor = (0,1,1,1),
      scale      = 0.5,)
  
  def destroy():
    window3.detachNode()
  
  base.accept('a', destroy)
  base.accept('c', window3.collapse)
  base.accept('u', window3.uncollapse)
  
  run()

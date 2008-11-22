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

# a task that keeps a node at the position of the mouse-cursor
def mouseNodeTask( task ):
  if WindowManager.hasMouse():
    x=WindowManager.getMouseX()
    y=WindowManager.getMouseY()
    # the mouse position is read relative to render2d, so set it accordingly
    aspect2dMouseNode.setPos( render2d, x, 0, y )
  return task.cont
# maybe we should check if aspect2d doesnt already contain the aspect2dMouseNode
aspect2dMouseNode = aspect2d.attachNewNode( 'aspect2dMouseNode', sort = 999999 )
taskMgr.add( mouseNodeTask, 'mouseNodeTask' )

DEFAULT_TITLE_GEOM_LEFT   = 'titleLeft.png'
DEFAULT_TITLE_GEOM_CENTER = 'titleCenter.png'
DEFAULT_TITLE_GEOM_RIGHT  = 'titleRight.png'
DEFAULT_RESIZE_GEOM       = 'resize.png'

class DirectWindow( DirectFrame ):
  def __init__( self
              , pos         = ( -.5, .5)
              , title       = 'Title'
              , backgroundColor  = ( 1, 1, 1, 1 )
              , buttonColor = (1,1,1,1) #( .6, .6, .6, 1 )
              , minSize     = ( .5, .5 )
              , maxSize     = ( 1, 1 )
              , windowBordersFilenames   = [ DEFAULT_TITLE_GEOM_LEFT
                                  , DEFAULT_TITLE_GEOM_CENTER
                                  , DEFAULT_TITLE_GEOM_RIGHT
                                  , DEFAULT_RESIZE_GEOM ]
              , windowColors    = [ ( 1, 1, 1, 1 )
                                  , ( 1, 1, 1, 1 )
                                  , ( 1, 1, 1, 1 )
                                  , ( 1, 1, 1, 1 ) ]):
    windowBorders = list()
    for windowBorder in windowBordersFilenames:
      if windowBorder is not None:
        mdlFile = loader.loadTexture(windowBorder)
        windowBorders.append(mdlFile)
      else:
        windowBorders.append(None)
    
    # the main window we want to move around
    self.windowPos = pos
    self.window = DirectFrame(
        parent      = aspect2d,
        pos         = ( self.windowPos[0], 0, self.windowPos[1] ),
        frameColor  = ( 0, 0, 0, 1 ),
        )
    
    # the title part of the window, drag around to move the window
    self.headerHeight = 0.05
    h = -self.headerHeight
    self.windowHeaderLeft = DirectButton(
        parent       = self.window,
        frameTexture = windowBorders[0],
        frameSize    = ( -.5, .5, -.5, .5 ),
        borderWidth  = ( 0, 0 ),
        relief       = DGG.FLAT,
        frameColor   = windowColors[0],
        )
    self.windowHeaderCenter = DirectButton(
        parent       = self.window,
        frameTexture = windowBorders[1],
        frameSize    = ( -.5, .5, -.5, .5 ),
        borderWidth  = ( 0, 0 ),
        relief       = DGG.FLAT,
        frameColor   = windowColors[1],
        )
    self.windowHeaderRight = DirectButton(
        parent       = self.window,
        frameTexture = windowBorders[2],
        frameSize    = ( -.5, .5, -.5, .5 ),
        borderWidth  = ( 0, 0 ),
        relief       = DGG.FLAT,
        frameColor   = windowColors[2],
        )
    
    self.windowHeaderLeft.bind(DGG.B1PRESS,self.startWindowDrag)
    self.windowHeaderCenter.bind(DGG.B1PRESS,self.startWindowDrag)
    self.windowHeaderRight.bind(DGG.B1PRESS,self.startWindowDrag)
    
    # this is not handled correctly, if a window is dragged which has been
    # created before another it will not be released
    # check the bugfixed startWindowDrag function
    #self.windowHeader.bind(DGG.B1RELEASE,self.stopWindowDrag)
    
    text = TextNode('WindowTitleTextNode')
    text.setText(title)
    text.setAlign(TextNode.ACenter)
    text.setTextColor( 0, 0, 0, 1 )
    text.setShadow(0.05, 0.05)
    text.setShadowColor( 1, 1, 1, 1 )
    #cmr12 = loader.loadFont('cmr12.egg')
    #text.setFont(cmr12)
    self.textNodePath = self.window.attachNewNode(text)
    #textNodePath = self.windowHeader.attachNewNode(text)
    #self.textNodePath.setPos( )
    self.textNodePath.setScale(self.headerHeight*0.8)
    
    # the content part of the window, put stuff beneath
    # contentWindow.getCanvas() to put it into it
    self.maxVirtualSize = maxSize
    self.minVirtualSize = minSize
    self.resizeSize     = 0.04
    self.contentWindow = DirectScrolledFrame(
        parent       = self.window,
        pos          = ( 0, 0, -self.headerHeight ),
        canvasSize   = ( 0, self.maxVirtualSize[0], 0, self.maxVirtualSize[1] ),
        frameColor   = buttonColor,
        relief       = DGG.RAISED,
        borderWidth  = (0,0),
        verticalScroll_frameSize                = [0,self.resizeSize,0,1],
        verticalScroll_frameTexture             = loader.loadTexture( 'rightBorder.png' ),
        verticalScroll_incButton_frameTexture   = loader.loadTexture( 'scrollDown.png' ),
        verticalScroll_decButton_frameTexture   = loader.loadTexture( 'scrollDown.png' ),
        verticalScroll_thumb_frameTexture       = loader.loadTexture( 'scrollBar.png' ),
        horizontalScroll_frameSize              = [0,1,0,self.resizeSize],
        horizontalScroll_frameTexture           = loader.loadTexture( 'bottomBorder.png' ),
        horizontalScroll_incButton_frameTexture = loader.loadTexture( 'scrollDown.png' ),
        horizontalScroll_decButton_frameTexture = loader.loadTexture( 'scrollDown.png' ),
        horizontalScroll_thumb_frameTexture     = loader.loadTexture( 'scrollBar.png' ),
        )
    
    # TODO: BUG THIS IS INVISIBLE
    DirectFrame.__init__( self,
        parent       = self.contentWindow.getCanvas(),
        pos          = ( 0, 0, 0 ),
        frameSize    = ( 0, self.maxVirtualSize[0], 0, self.maxVirtualSize[1] ),
        frameColor   = backgroundColor,
        relief       = DGG.RIDGE,
        borderWidth  = ( .01, .01),
        )
    # BUGFIX FOR ABOVE
    self.backgroundColor = DirectFrame(
        parent       = self,
        frameSize    = ( 0, self.maxVirtualSize[0], 0, self.maxVirtualSize[1] ),
        frameColor   = backgroundColor,
        relief       = DGG.FLAT,
        borderWidth  = ( .01, .01),
        )
    
    # the resize button of the window
    self.windowResize = DirectButton(
        parent       = self.window,
        frameSize    = ( -.5, .5, -.5, .5 ),
        borderWidth  = ( 0, 0 ),
        scale        = ( self.resizeSize, 1, self.resizeSize ),
        relief       = DGG.FLAT,
        frameTexture = windowBorders[3],
        frameColor   = windowColors[3],
        )
    self.windowResize.bind(DGG.B1PRESS,self.startResizeDrag)
    self.windowResize.bind(DGG.B1RELEASE,self.stopResizeDrag)
    
    # offset then clicking on the resize button from the mouse to the resizebutton
    # position, required to calculate the position / scaling
    self.offset = None
    self.taskName = "resizeTask-%s" % str(hash(self))
    
    # do sizing of the window (minimum)
    self.resize( Vec3(0,0,0), Vec3(0,0,0) )
    # maximum
    self.resize( Vec3(100,0,-100), Vec3(0,0,0) )
  
  # dragging functions
  def startWindowDrag( self, param ):
    print "I: DirectWindow.startWindowDrag"
    self.window.wrtReparentTo( aspect2dMouseNode )
    self.window.ignoreAll()
    self.window.accept( 'mouse1-up', self.stopWindowDrag )
  def stopWindowDrag( self, param=None ):
    # this could be called even after the window has been destroyed
    if self.window:
      # this is called 2 times (bug), so make sure it's not already parented to aspect2d
      if self.window.getParent() != aspect2d:
        self.window.wrtReparentTo( aspect2d )
  
  # resize functions
  def resize( self, mPos, offset ):
    mXPos = max( min( mPos.getX(), self.maxVirtualSize[0] ), self.minVirtualSize[0])
    mZPos = max( min( mPos.getZ(), -self.minVirtualSize[1] ), -self.maxVirtualSize[1]-self.headerHeight)
    self.windowResize.setPos( mXPos-self.resizeSize/2., 0, mZPos+self.resizeSize/2. )
    self.window['frameSize'] = (0, mXPos, 0, mZPos)
    #self.window.setScale( mXPos, 1, -mZPos )
    self.windowHeaderLeft.setPos( self.headerHeight/2., 0, -self.headerHeight/2. )
    self.windowHeaderLeft.setScale( self.headerHeight, 1, self.headerHeight )
    self.windowHeaderCenter.setPos( mXPos/2., 0, -self.headerHeight/2. )
    self.windowHeaderCenter.setScale( mXPos - self.headerHeight*2., 1, self.headerHeight )
    self.windowHeaderRight.setPos( mXPos-self.headerHeight/2., 0, -self.headerHeight/2. )
    self.windowHeaderRight.setScale( self.headerHeight, 1, self.headerHeight )
    self.contentWindow['frameSize'] = ( 0, mXPos, mZPos+self.headerHeight, 0)
    self.textNodePath.setPos( mXPos/2., 0, -self.headerHeight/3.*2. )
  def resizeTask( self, task=None ):
    try:
      mPos = aspect2dMouseNode.getPos( self.window )+self.offset
      self.resize( mPos, self.offset )
    except:
      return task.done
    return task.cont
  def startResizeDrag( self, param ):
    self.offset  = self.windowResize.getPos( aspect2dMouseNode )
    taskMgr.remove( self.taskName )
    taskMgr.add( self.resizeTask, self.taskName )
  def stopResizeDrag( self, param ):
    taskMgr.remove( self.taskName )
  
  # a bugfix for a wrong implementation
  def detachNode( self ):
    self.window.detachNode()
    self.window = None
    DirectFrame.detachNode( self )
  def removeNode( self ):
    self.window.removeNode()
    DirectFrame.removeNode( self )




if __name__ == '__main__':
  # a first window
  window1 = DirectWindow( title='window1', pos = ( -.8, .8), windowBordersFilenames=(None,None,None,None,) )
  windowContent = DirectButton(
      parent     = window1,
      pos        = (.05,0,.05),
      frameSize  = (0,.9,0,.9),
      relief     = DGG.FLAT,
      frameColor = (0,1,0,1),
      )
  
  # a second window
  window2 = DirectWindow( title='window2', pos = ( -.4, .4), maxSize = (1.5,1.5) )
  windowContent = DirectButton(
      parent     = window2,
      pos        = (.6,0,.6),
      frameSize  = (-.5,.5,-.5,.5),
      relief     = DGG.FLAT,
      frameColor = (0,1,1,1),
#      geom       = DEFAULT_TITLE_GEOM,
      )
  
  # a second window
  window3 = DirectWindow( title='window3', pos = ( 0, 0) )
  windowContent = DirectButton(
      parent     = window3,
      pos        = (.5,0,.5),
      frameSize  = (-.5,.5,-.5,.5),
      relief     = DGG.FLAT,
      frameColor = (0,1,1,1),
#      geom       = DEFAULT_TITLE_GEOM,
      scale      = 0.5,
      )
  
  def destroy():
    window3.detachNode()
  
  base.accept('a', destroy)
  
  run()

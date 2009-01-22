from direct.showbase.DirectObject import *
from pandac.PandaModules import TextureAttrib, Texture, PNMImage, \
GraphicsOutput, NodePath, Filename, TextureStage, VBase4D, PNMPainter, \
PNMBrush, VBase3D

from core.pWindow import WindowManager
from core.pMouseHandler import mouseHandler
from core.pConfigDefs import *

PNMBrush_BrushEffect_Enum = Enum(
  BESet = PNMBrush.BESet,
  BEBlend = PNMBrush.BEBlend,
  BEDarken = PNMBrush.BEDarken,
  BELighten = PNMBrush.BELighten,
)

def createPickingImage(size):
  ''' create a picking image with uniq colors for each point in the image
  '''
  image = PNMImage(*size)
  for x in xrange(size[0]):
    for y in xrange(size[1]):
      r = x % 256
      g = y % 256
      b = (x // 256) + (y//256) * 16
      image.setXelVal(x,y,r,g,b)
  
  # Reverse way is:
  #    tx = r + ((b%16)*256)
  #    ty = g + ((b//16)*256)
  imageFilename = 'data/textures/index-%i-%i.png' % (size[0], size[1])
  image.write(Filename(imageFilename))

class TexturePainter(DirectObject):
  def __init__(self):
    self.origModel = None
    self.paintModel = None
    self.paintTexture = None
    self.origModel = None
    self.enabled = False
    self.paintModelSetup = False
    self.buffer = None
    self.backcam = None
    
    self.paintColor = VBase4D(1,1,1,1)
    self.paintSize = 10
    self.paintEffect = PNMBrush.BEBlend
    self.paintSmooth = True
    
    # some debugging stuff
    #self.accept("v", base.bufferViewer.toggleEnable)
    #self.accept("V", base.bufferViewer.toggleEnable)
    base.bufferViewer.setPosition("llcorner")
    base.bufferViewer.setCardSize(0.25, 0.0)
    base.bufferViewer.toggleEnable()
  
  def windowEvent(self, win):
    print "I: TexturePainter.windowEvent"
    # the window has been modified
    if WindowManager.activeWindow:
      # on window resize there seems to be never a active window
      win = WindowManager.activeWindow.win
    if self.buffer.getXSize() != win.getXSize() or self.buffer.getXSize() != win.getYSize():
      self.updateBackRender(win)
    self.updateModel()
  
  def updateBackRender(self, win):
    print "I: TexturePainter.updateBackRender"
    if self.buffer:
      # Destroy the buffer
      base.graphicsEngine.removeWindow(self.buffer)
      self.buffer = None
      # Remove the camera
      self.backcam.removeNode()
    if not self.buffer:
      # Create the buffer
      self.buffer = win.makeTextureBuffer("pickBuffer", win.getXSize(), win.getYSize())
      self.buffer.addRenderTexture(self.pickTex, GraphicsOutput.RTMCopyRam)
      # Create the camera again
      self.backcam = base.makeCamera(self.buffer, sort = -10)
      self.backcam.node().setScene(self.backgroundRender)
      self.backcam.reparentTo(self.backgroundRender)
  
  def updateModel(self):
    print "I: TexturePainter.updateModel", self.origModel
    if self.origModel:
      # create a image with the same size of the texture
      textureSize = (self.paintTexture.getXSize(), self.paintTexture.getYSize())
      createPickingImage( textureSize )
      
      # instance the model
      if self.paintModel:
        self.paintModel.removeNode()
      self.paintModel = self.origModel.copyTo(self.backgroundRender)
      self.paintModel.clearTexture()
      self.paintModel.clearShader()
      self.paintModel.setTexture(loader.loadTexture("textures/index-%i-%i.png" % (textureSize[0], textureSize[1])),1)
      self.paintModel.setMat(render, self.origModel.getMat(render))
  
  def enableEditor(self, paintModel, paintTexture):
    print "I: TexturePainter.enableEditor"
    self.origModel = paintModel
    self.paintTexture = paintTexture
    
    # setup an offscreen buffer for the colour index
    self.pickLayer = PNMImage()
    self.pickTex = Texture()
    
    self.backgroundRender = NodePath("backgroundRender")
    self.backgroundRender.setLightOff()
    self.backgroundRender.setFogOff()
    
    self.updateBackRender(WindowManager.windows[0].win)
    #self.backcam.reparentTo(self.backgroundRender)
    #self.backcam.node().copyLens(WindowManager.activeWindow.camera.node().getLens())
    
    if self.paintModel != None:
      self.stopEdit()
    
    if type(self.paintTexture) == Texture:
      # load the working texture (this must load the real texure of the object)
      self.workTex = self.paintTexture #loader.loadTexture('models/maps/smiley.rgb')
      # copy the image from the texture to the working layer
      self.workLayer = PNMImage()
      self.workTex.store(self.workLayer)
    else:
      self.workLayer = self.paintTexture
    
    self.painter = PNMPainter(self.workLayer)
    self.brush = PNMBrush.makeSpot(VBase4D(1, 0, 0, 1), 7, True, PNMBrush.BEBlend)
    
    self.updateModel()
    
    self.accept("window-event", self.windowEvent)
  
  def setBrushSettings(self, color, size, smooth, effect):
    print "I: TexturePainter.setBrushSettings", color, size, smooth, effect
    self.paintColor = color
    self.paintSize = size
    self.paintEffect = effect
    self.paintSmooth = smooth
    self.brush = PNMBrush.makeSpot(color, size, smooth, effect)
    if self.paintModel:
      self.painter.setPen(self.brush)
  
  def getBrushSettings(self):
    return self.paintColor,self.paintSize,self.paintSmooth,self.paintEffect
  
  def disableEditor(self):
    print "I: TexturePainter.disableEditor"
    self.stopEdit()
    
    if self.paintModel:
      self.paintModel.detachNode()
      self.paintModel = None
    self.workLayer = None
    self.painter = None
    
    self.ignoreAll()
  
  def startEdit(self):
    messenger.send(EVENT_TEXTUREPAINTER_STARTEDIT)
    self.accept("mouse1", self.startPaint)
    self.accept("mouse1-up", self.stopPaint)
    self.accept("mouse3", self.startGetColor)
    self.accept("mouse3-up", self.stopGetColor)
  
  def stopEdit(self):
    messenger.send(EVENT_TEXTUREPAINTER_STOPEDIT)
    self.ignore("mouse1")
    self.ignore("mouse1-up")
  
  def startPaint(self):
    self.backcam.node().copyLens(WindowManager.activeWindow.camera.node().getLens())
    taskMgr.add(self.paintTask, 'paintTask')
  
  def paintTask(self, task):
    if not WindowManager.activeWindow or not WindowManager.activeWindow.mouseWatcherNode.hasMouse():
      return
    
    if not self.paintModel:
      print "E: TexturePainter.paintTask: no paintModel"
      return
    # update the camera according to the active camera
    self.backcam.setMat(render, WindowManager.activeWindow.camera.getMat(render))
    # update the mat of the model we currently paint on
    self.paintModel.setMat(render, self.origModel.getMat(render))
    # save the rendering as texture
    #base.graphicsEngine.renderFrame() # not needed anymore
    try:
      self.pickTex.store(self.pickLayer)
    except:
      print "E: TexturePainter.paintTask: cannot store pickTex"
      return
    
    # get window size
    win = WindowManager.activeWindow.win
    self.windowSize = win.getXSize(), win.getYSize()
    
    # convert mouse coordinates to image coordinates
    mx, my = mouseHandler.getMousePos()
    mx = int(((mx+1)/2)*self.windowSize[0])
    my = self.windowSize[1] - int(((my+1)/2)*self.windowSize[1])
    
    # get the color below the mousepick from the rendered frame
    r = self.pickLayer.getRedVal(mx,my)
    g = self.pickLayer.getGreenVal(mx,my)
    b = self.pickLayer.getBlueVal(mx,my)
    # calculate uv-texture position from the color
    x = r + ((b%16)*256)
    y = g + ((b//16)*256)
    
    # render a spot into the texture
    self.painter.drawPoint(x, y)
    
    # display the modified texture
    if type(self.paintTexture) == Texture:
      self.workTex.load(self.workLayer)
    
    return task.cont
  
  def stopPaint(self):
    taskMgr.remove('paintTask')
  
  def startGetColor(self):
    pass
  def stopGetColor(self):
    pass


texturePainter = TexturePainter()

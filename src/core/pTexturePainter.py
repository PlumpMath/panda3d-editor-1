from direct.showbase.DirectObject import *
from pandac.PandaModules import TextureAttrib, Texture, PNMImage, \
GraphicsOutput, NodePath, Filename, TextureStage, VBase4D, PNMPainter, \
PNMBrush, VBase3D

from core.pWindow import WindowManager
from core.pMouseHandler import mouseHandler

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
    self.accept("window-event", self.windowEvent)
    self.enabled = False
  
  def selectPaintModel(self, selectModel):
    self.origModel = selectModel
  
  def addStageByNameSize(self, name='Texture', size=[512,512]):
    # create a image of size
    texture = Texture(name)
    texture.setXSize(size[0])
    texture.setYSize(size[1])
    return self.addStageByTex(texture)
  
  def addStageByTex(self, texture):
    stage = TextureStage(texture.getName())
    self.paintModel.setTexture(stage, texture)
    return stage
  
  def enableEditor(self):
    # setup an offscreen buffer for the colour index
    self.pickLayer = PNMImage()
    self.pickTex = Texture()
    
    self.backgroundRender = NodePath("backgroundRender")
    self.backgroundRender.setLightOff()
    self.backgroundRender.setFogOff()
    self.buffer = None
    self.backcam = None
    
    self.backgroundResize(WindowManager.windows[0].win)
    
    self.accept("v", base.bufferViewer.toggleEnable)
    self.accept("V", base.bufferViewer.toggleEnable)
    base.bufferViewer.setPosition("llcorner")
    base.bufferViewer.setCardSize(1.0, 0.0)
    
    self.painter = None
    self.brush = PNMBrush.makeSpot(VBase4D(1, 0, 0, 1), 7, True)
    
    self.enabled = True
    self.paintModelSetup = False
  
  def setBrush(self, color, size):
    self.brush = PNMBrush.makeSpot(color, size, True)
    if self.paintModelSetup:
      self.painter.setPen(self.brush)
  
  def windowEvent(self, win):
    # the window has been changed
    if self.enabled:
      if WindowManager.activeWindow:
        # on window resize there seems to be never a active window
        # get window size
        win = WindowManager.activeWindow.win
        if self.buffer.getXSize() != win.getXSize() or self.buffer.getXSize() != win.getYSize():
          self.backgroundResize(win)
      else:
        # but the win is given
        if self.buffer and win:
          if self.buffer.getXSize() != win.getXSize() or self.buffer.getXSize() != win.getYSize():
            self.backgroundResize(win)
        else:
          print "W: TexturePainter.windowEvent: buffer or win unavailable", self.buffer, win
  
  def backgroundResize(self, win):
    """ When the window is resized, we need to recreate the background renderer. """
    if self.buffer:
      # Destroy the buffer
      base.graphicsEngine.removeWindow(self.buffer)
      self.buffer = None
      # Remove the camera
      self.backcam.removeNode()
    
    # Create the buffer
    self.buffer = win.makeTextureBuffer("pickBuffer", win.getXSize(), win.getYSize())
    self.buffer.addRenderTexture(self.pickTex, GraphicsOutput.RTMCopyRam)
    # Create the camera again
    self.backcam = base.makeCamera(self.buffer, sort = -10)
  
  def disableEditor(self):
    if self.paintModel != None:
      self.stopEdit()
    
    self.ignoreAll()
    
    self.enabled = False
  
  def startEdit(self, texture):
    self.paintTexture = texture
    self.accept("mouse1", self.startPaint)
    self.accept("mouse1-up", self.stopPaint)
    self.setupPaintModel()
  
  def stopEdit(self):
    self.destroyPaintModel()
    self.ignore("mouse1")
    self.ignore("mouse1-up")
  
  def setupPaintModel(self):
    if not self.paintModelSetup:
      if self.enabled and self.origModel is not None:
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
        
        self.paintModel = self.origModel.copyTo(self.backgroundRender) #loader.loadModel('models/smiley.egg')
        self.paintModel.clearTexture()
        self.paintModel.clearShader()
        if self.paintModel:
          #tester.reparentTo(self.backgroundRender)
          self.paintModel.setMat(render, self.origModel.getMat(render))
          textureSize = (self.paintTexture.getXSize(), self.paintTexture.getYSize())
          createPickingImage( textureSize )
          self.paintModel.setTexture(loader.loadTexture("textures/index-%i-%i.png" % (textureSize[0], textureSize[1])),1)
          base.graphicsEngine.renderFrame()
          
          self.pickTex.store(self.pickLayer)
          
          self.textureSize = textureSize
        else:
          print "W: TexturePainter.startEdit: error copying model", model, texture
        self.paintModelSetup = True
      else:
        print "W: TexturePainter.startEdit: paint mode not enabled!"
  
  def destroyPaintModel(self):
    if self.paintModelSetup:
      if self.paintModel:
        self.paintModel.detachNode()
        self.paintModel = None
      self.workLayer = None
      self.painter = None
      self.paintModelSetup = False

  
  def startPaint(self):
    self.setupPaintModel()
    # could also be in the paintTask
    # update the camera according to the active camera
    self.backcam.reparentTo(self.backgroundRender)
    self.backcam.setMat(render, WindowManager.activeWindow.camera.getMat(render))
    self.backcam.node().copyLens(WindowManager.activeWindow.camera.node().getLens())
    # update the mat of the model we currently paint on
    self.paintModel.setMat(render, self.origModel.getMat(render))
    
    taskMgr.add(self.paintTask, 'paintTask')
  
  def paintTask(self, task):
    if self.enabled and self.paintModel and WindowManager.activeWindow != None:
      
      # render the backbuffer
      base.graphicsEngine.renderFrame()
      
      # save the rendering as texture
      self.pickTex.store(self.pickLayer)
      
      if not WindowManager.activeWindow.mouseWatcherNode.hasMouse():
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
      
      print "before", self.workLayer.getGray(x,y)
      
      print "painting at", x, y
      # render a spot into the texture
      self.painter.drawPoint(x, y)
      
      print "after", self.workLayer.getGray(x,y)
      
      # display the modified texture
      if type(self.paintTexture) == Texture:
        self.workTex.load(self.workLayer)
    else:
      print "W: TexturePainter.paint: paint mode not enabled!"
    return task.cont
  
  def stopPaint(self):
    taskMgr.remove('paintTask')


texturePainter = TexturePainter()

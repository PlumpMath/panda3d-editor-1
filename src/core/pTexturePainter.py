import random, math

from direct.showbase.DirectObject import *
from pandac.PandaModules import TextureAttrib, Texture, PNMImage, \
GraphicsOutput, NodePath, Filename, TextureStage, VBase4D, PNMPainter, \
PNMBrush, VBase3D

from core.pWindow import WindowManager
from core.pMouseHandler import mouseHandler
from core.pConfigDefs import *

TEXTUREPAINTER_BRUSH_SMOOTH = 'smooth'
TEXTUREPAINTER_BRUSH_RANDOMIZE = 'randomize'

PNMBrush_BrushEffect_Enum = Enum(
  BESet = PNMBrush.BESet,
  BEBlend = PNMBrush.BEBlend,
  BEDarken = PNMBrush.BEDarken,
  BELighten = PNMBrush.BELighten,
  Smooth = TEXTUREPAINTER_BRUSH_SMOOTH,
  Randomize = TEXTUREPAINTER_BRUSH_RANDOMIZE,
)

TEXTUREPAINTER_FUNCTION_PAINT_POINT = 'paintPoint'
TEXTUREPAINTER_FUNCTION_PAINT_LINE = 'paintLine'
TEXTUREPAINTER_FUNCTION_PAINT_RECTANGLE = 'paintRectangle'
TEXTUREPAINTER_FUNCTION_READ = 'readColor'

TexturePainter_PaintMode_Enum = Enum(
  PointPaint = TEXTUREPAINTER_FUNCTION_PAINT_POINT,
  LinePaint = TEXTUREPAINTER_FUNCTION_PAINT_LINE,
  RectanglePaint = TEXTUREPAINTER_FUNCTION_PAINT_RECTANGLE,
  ReadColor = TEXTUREPAINTER_FUNCTION_READ,
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
    
    self.initialized = False
    
    self.paintColor = VBase4D(1,1,1,1)
    self.paintSize = 10
    self.paintEffect = PNMBrush.BEBlend
    self.paintSmooth = True
    self.paintMode = TEXTUREPAINTER_FUNCTION_PAINT_POINT
    
    # some debugging stuff
    #self.accept("v", base.bufferViewer.toggleEnable)
    #self.accept("V", base.bufferViewer.toggleEnable)
    #base.bufferViewer.setPosition("llcorner")
    #base.bufferViewer.setCardSize(0.25, 0.0)
    #base.bufferViewer.toggleEnable()
  
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
      
      '''if not self.workLayer.hasRamImage():
        print "E: TexturePainter.enableEditor: paintTexture has not ramMipmapImage"
        self.initialized = False
        return False'''
      
      self.workTex.store(self.workLayer)
    else:
      self.workLayer = self.paintTexture
    
    self.painter = PNMPainter(self.workLayer)
    self.brush = PNMBrush.makeSpot(VBase4D(1, 0, 0, 1), 7, True, PNMBrush.BEBlend)
    
    self.updateModel()
    
    self.accept("window-event", self.windowEvent)
    
    self.initialized = True
    return True
  
  def setBrushSettings(self, color, size, smooth, effect):
    print "I: TexturePainter.setBrushSettings", color, size, smooth, effect
    self.paintColor = color
    self.paintSize = size
    self.paintEffect = effect
    self.paintSmooth = smooth
    if effect in [PNMBrush.BESet, PNMBrush.BEBlend, PNMBrush.BEDarken, PNMBrush.BELighten]:
      self.brush = PNMBrush.makeSpot(color, size, smooth, effect)
      if self.paintModel:
        self.painter.setPen(self.brush)
  
  def getBrushSettings(self):
    return self.paintColor,self.paintSize,self.paintSmooth,self.paintEffect
  
  def setPaintMode(self, newMode):
    self.paintMode = newMode
    # clear last point if mode changed
    if newMode == TEXTUREPAINTER_FUNCTION_PAINT_POINT or \
       newMode == TEXTUREPAINTER_FUNCTION_READ:
      self.lastPoint = None
  
  def getPaintMode(self):
    return self.paintMode
  
  def disableEditor(self):
    print "I: TexturePainter.disableEditor"
    self.stopEdit()
    
    if self.paintModel:
      self.paintModel.detachNode()
      self.paintModel = None
    self.workLayer = None
    self.painter = None
    
    self.initialized = False
    
    self.ignoreAll()
  
  def startEdit(self):
    if self.initialized:
      messenger.send(EVENT_TEXTUREPAINTER_STARTEDIT)
      # start paint events
      self.accept("mouse1", self.startPaint)
      self.accept("control-mouse1", self.startPaint)
      self.accept("shift-mouse1", self.startPaint)
      #self.accept("alt-mouse1", self.startPaint)
      
      # stop paint events
      self.accept("mouse1-up", self.stopPaint)
      self.accept("shift-mouse1-up", self.stopPaint)
      self.accept("control-mouse1-up", self.stopPaint)
      self.accept("alt-mouse1-up", self.stopPaint)
      self.accept("shift-alt-mouse1-up", self.stopPaint)
      self.accept("control-alt-mouse1-up", self.stopPaint)
      self.accept("shift-control-mouse1-up", self.stopPaint)
      self.accept("shift-control-alt-mouse1-up", self.stopPaint)
    else:
      print "E: TexturePainter.startEdit: not initialized"
  
  def stopEdit(self):
    messenger.send(EVENT_TEXTUREPAINTER_STOPEDIT)
    self.ignore("mouse1")
    self.ignore("mouse1-up")
  
  def startPaint(self):
    self.backcam.node().copyLens(WindowManager.activeWindow.camera.node().getLens())
    self.paintFunction = TEXTUREPAINTER_FUNCTION_PAINT_POINT
    taskMgr.add(self.paintTask, 'paintTask')
    taskMgr.doMethodLater(1.0/30, self.textureUpdateTask, 'textureUpdateTask')
    #self.lastPoint = None
  def stopPaint(self):
    taskMgr.remove('paintTask')
    taskMgr.remove('textureUpdateTask')
    #self.lastPoint = None
  
  def textureUpdateTask(self, task):
    # display the modified texture
    if type(self.paintTexture) == Texture:
      self.workTex.load(self.workLayer)
    return task.again
  
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
    
    if x > self.workLayer.getXSize() or y > self.workLayer.getYSize():
      pass
    else:
      if self.paintMode == TEXTUREPAINTER_FUNCTION_PAINT_POINT:
        if self.paintEffect in [PNMBrush.BESet, PNMBrush.BEBlend, PNMBrush.BEDarken, PNMBrush.BELighten]:
          # render a spot into the texture
          self.painter.drawPoint(x, y)
        
        elif self.paintEffect in [TEXTUREPAINTER_BRUSH_SMOOTH, TEXTUREPAINTER_BRUSH_RANDOMIZE]:
          radius = int(round(self.paintSize/2.0))
          dividor = 0
          
          if self.paintEffect == TEXTUREPAINTER_BRUSH_SMOOTH:
            average = VBase4D(0)
            for dx in xrange(-radius, radius+1):
              for dy in xrange(-radius, radius+1):
                multiplier = ((radius-math.fabs(dx))*(radius-math.fabs(dy))) / (radius*radius)
                dividor += multiplier
                average += self.workLayer.getXelA(x+dx,y+dy) * multiplier
            average /= dividor
            for dx in xrange(-radius, radius+1):
              for dy in xrange(-radius, radius+1):
                multiplier = ((radius-math.fabs(dx))*(radius-math.fabs(dy))) / (radius*radius)
                currentValue = self.workLayer.getXelA(x+dx,y+dy)
                r = currentValue.getX() * (1-multiplier*self.paintColor.getX()) + average.getX() * multiplier*self.paintColor.getX()
                g = currentValue.getY() * (1-multiplier*self.paintColor.getY()) + average.getY() * multiplier*self.paintColor.getY()
                b = currentValue.getZ() * (1-multiplier*self.paintColor.getZ()) + average.getZ() * multiplier*self.paintColor.getZ()
                a = currentValue.getW() * (1-multiplier*self.paintColor.getW()) + average.getW() * multiplier*self.paintColor.getW()
                if self.workLayer.hasAlpha():
                  self.workLayer.setXelA(x+dx,y+dy,VBase4D(r,g,b,a))
                else:
                  self.workLayer.setXel(x+dx,y+dy,VBase3D(r,g,b))
          
          elif self.paintEffect == TEXTUREPAINTER_BRUSH_RANDOMIZE:
            for dx in xrange(-radius, radius+1):
              for dy in xrange(-radius, radius+1):
                r = VBase4D(random.random()*self.paintColor.getX()-self.paintColor.getX()/2.,
                           random.random()*self.paintColor.getY()-self.paintColor.getY()/2.,
                           random.random()*self.paintColor.getZ()-self.paintColor.getZ()/2.,
                           random.random()*self.paintColor.getW()-self.paintColor.getW()/2.)
                multiplier = ((radius-math.fabs(dx))*(radius-math.fabs(dy))) / (radius*radius)
                currentValue = self.workLayer.getXelA(x+dx,y+dy)
                self.workLayer.setXelA(x+dx,y+dy,currentValue+r*multiplier)
      
      elif self.paintMode == TEXTUREPAINTER_FUNCTION_READ:
        col = self.workLayer.getXelA(x,y)
        if self.workLayer.hasAlpha():
          self.paintColor = VBase4D(col[0], col[1], col[2], col[3])
        else:
          self.paintColor = VBase4D(col[0], col[1], col[2], 1.0)
        messenger.send(EVENT_TEXTUREPAINTER_BRUSHCHANGED)
      
      elif self.paintMode == TEXTUREPAINTER_FUNCTION_PAINT_LINE:
        if self.lastPoint != None:
          self.painter.drawLine(x, y, self.lastPoint[0], self.lastPoint[1])
      
      elif self.paintMode == TEXTUREPAINTER_FUNCTION_PAINT_RECTANGLE:
        if self.lastPoint != None:
          self.painter.drawRectangle(x, y, self.lastPoint[0], self.lastPoint[1])
      
      self.lastPoint = (x,y)
    
    return task.cont
  

texturePainter = TexturePainter()

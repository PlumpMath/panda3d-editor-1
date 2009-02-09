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

# the status the texture painter is in
# it has not been initialized, disable all functions, free all objects
TEXTURE_PAINTER_STATUS_DISABLED = 0
# it has been enabled, create all required buffers etc.
TEXTURE_PAINTER_STATUS_ENABLED = 1
# the object and texture has been defined (ready to paint)
TEXTURE_PAINTER_STATUS_INITIALIZED = 2
# we are painting
TEXTURE_PAINTER_STATUS_RUNNING = 3



class TexturePainter(DirectObject):
  def __init__(self):
    self.editTexture = None
    self.editModel = None
    
    self.texturePainterStatus = TEXTURE_PAINTER_STATUS_DISABLED
    
    '''self.paintModel = None
    
    self.enabled = False
    self.paintModelSetup = False
    self.buffer = None
    self.backcam = None
    
    self.initialized = False'''
    
    self.paintColor = VBase4D(1,1,1,1)
    self.paintSize = 10
    self.paintEffect = PNMBrush.BEBlend
    self.paintSmooth = True
    self.paintMode = TEXTUREPAINTER_FUNCTION_PAINT_POINT
  
  # --- creation and destroying of the whole editor ---
  def enableEditor(self):
    ''' create the editor
    change from disabled to enabled'''
    if self.texturePainterStatus == TEXTURE_PAINTER_STATUS_DISABLED:
      self.texturePainterStatus = TEXTURE_PAINTER_STATUS_ENABLED
      self.__enableEditor()
    else:
      print "E: TexturePainter.enableEditor: not disabled", self.texturePainterStatus
  
  def disableEditor(self):
    ''' destroy the editor, automatically stop the editor and painting
    change from enabled to disabled'''
    if self.texturePainterStatus == TEXTURE_PAINTER_STATUS_INITIALIZED:
      self.stopEditor()
    self.texturePainterStatus = TEXTURE_PAINTER_STATUS_DISABLED
    self.__disableEditor(self)
  
  # --- 
  def startEditor(self, editModel, editTexture):
    ''' prepare to paint
    change from enabled to initialized'''
    if self.texturePainterStatus == TEXTURE_PAINTER_STATUS_ENABLED:
      self.texturePainterStatus = TEXTURE_PAINTER_STATUS_INITIALIZED
      self.__startEditor(editModel, editTexture)
    else:
      print "E: TexturePainter.startEditor: not initialized", self.texturePainterStatus
  
  def stopEditor(self):
    ''' stop painting, automatically stop painting
    change from initialized to enabled'''
    if self.texturePainterStatus == TEXTURE_PAINTER_STATUS_INITIALIZED:
      self.stopPaint()
    self.texturePainterStatus = TEXTURE_PAINTER_STATUS_ENABLED
    self.__stopEditor()
  
  """ # this is not externally callable
  # ---
  def startPaint(self):
    ''' start painting on the model
    change from initialized to running '''
    if self.texturePainterStatus == TEXTURE_PAINTER_STATUS_INITIALIZED:
      self.texturePainterStatus = TEXTURE_PAINTER_STATUS_RUNNING
      self.__startPaint()
    else:
      print "E: TexturePainter.startPaint: not enabled", self.texturePainterStatus"""
  
  def stopPaint(self):
    ''' stop painting
    change from running to initialized '''
    if self.texturePainterStatus == TEXTURE_PAINTER_STATUS_RUNNING:
      self.texturePainterStatus = TEXTURE_PAINTER_STATUS_INITIALIZED
      self.__stopPaint()
    else:
      print "E: TexturePainter.stopPaint: not running", self.texturePainterStatus
  
  
  # --- brush settings for painting ---
  ''' changing brush settings is possible all the time '''
  def setBrushSettings(self, color, size, smooth, effect):
    #print "I: TexturePainter.setBrushSettings", color, size, smooth, effect
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
  
  
  
  def __enableEditor(self):
    ''' create the background rendering etc., but the model is not yet defined '''
    print "I: TexturePainter.__enableEditor"
    # setup an offscreen buffer for the colour index
    self.pickLayer = PNMImage()
    self.pickTex = Texture()
    
    self.backgroundRender = NodePath("backgroundRender")
    self.backgroundRender.setLightOff(10000)
    self.backgroundRender.setFogOff(10000)
    self.backgroundRender.setTextureOff(10000)
    self.backgroundRender.setShaderOff(10000)
    self.backgroundRender.setColorScaleOff(10000)
    self.backgroundRender.setColorOff(10000)
    '''self.backgroundRender.setShaderOff(10000)
    self.backgroundRender.setTextureOff(10000)
    self.backgroundRender.setLightOff(10000)
    self.backgroundRender.setFogOff(10000)'''
    
    self.buffer = None
    self.backcam = None
    self.__createBuffer()
    
    # when the window is resized, the background buffer etc must be updated.
    self.accept("window-event", self.__windowEvent)
    
    # some debugging stuff
    self.accept("v", base.bufferViewer.toggleEnable)
    self.accept("V", base.bufferViewer.toggleEnable)
  
  def __disableEditor(self):
    print "I: TexturePainter.__disableEditor"
    
    self.__destroyBuffer()
    
    # ignore window-event and debug
    self.ignoreAll()
  
  def __createBuffer(self):
    ''' create the buffer we render in the background into '''
    # the window has been modified
    if WindowManager.activeWindow:
      # on window resize there seems to be never a active window
      win = WindowManager.activeWindow.win
    else:
      win = base.win
    
    # Create the buffer
    self.buffer = win.makeTextureBuffer("pickBuffer", win.getXSize(), win.getYSize())
    self.buffer.addRenderTexture(self.pickTex, GraphicsOutput.RTMCopyRam)
    # Create the camera again
    self.backcam = base.makeCamera(self.buffer, sort = -10)
    self.backcam.node().setScene(self.backgroundRender)
    self.backcam.reparentTo(self.backgroundRender)
    '''else:
      print "W: TexturePainter.__createBuffer: no win"'''
  
  def __destroyBuffer(self):
    print "I: TexturePainter.__destroyBuffer:", self.buffer
    if self.buffer:
      # Destroy the buffer
      base.graphicsEngine.removeWindow(self.buffer)
      self.buffer = None
      # Remove the camera
      self.backcam.removeNode()
      del self.backcam
      self.backcam = None
  
  def __windowEvent(self, win=None):
    ''' when the editor is enabled, update the buffers etc. when the window
    is resized '''
    print "I: TexturePainter.windowEvent"
    #if self.texturePainterStatus != TEXTURE_PAINTER_STATUS_DISABLED:
    if self.buffer:
      if WindowManager.activeWindow:
        # on window resize there seems to be never a active window
        win = WindowManager.activeWindow.win
      else:
        win = base.win
      if self.buffer.getXSize() != win.getXSize() or self.buffer.getXSize() != win.getYSize():
        # if the buffer size doesnt match the window size (window has been resized)
        self.__destroyBuffer()
        self.__createBuffer()
    else:
      print "W: TexturePainter.__windowEvent: no buffer"
      self.__createBuffer()
  
  
  
  def __startEditor(self, editModel, editTexture):
    #print "I: TexturePainter.__startEditor:", editModel, editTexture
    # this is needed as on startup the editor may not have had a window etc.
    self.__windowEvent()
    
    
    self.editModel = editModel
    self.editTexture = editTexture
    self.editImage = None
    
    if type(self.editTexture) == Texture:
      #print "  - is texture"
      # if the image to modify is a texture, create a pnmImage which we modify
      self.editImage = PNMImage()
      # copy the image from the texture to the working layer
      self.editTexture.store(self.editImage)
    else:
      #print "  - is image"
      self.editImage = self.editTexture
    
    #print "  -", self.editImage
    self.painter = PNMPainter(self.editImage)
    self.brush = PNMBrush.makeSpot(VBase4D(1, 0, 0, 1), 7, True, PNMBrush.BEBlend)
    
    self.paintModel = None
    self.__updateModel()
    
    self.__startEdit()
  
  def __stopEditor(self):
    self.__stopEdit()
    
    if self.paintModel:
      self.paintModel.detachNode()
      self.paintModel = None
    self.editImage = None
    self.editTexture = None
    self.painter = None
    self.brush = None
  
  def __updateModel(self): #, overlayTexture=None):
    #print "I: TexturePainter.__updateModel", self.editModel
    if self.editModel:
      # create a image with the same size of the texture
      textureSize = (self.editTexture.getXSize(), self.editTexture.getYSize())
      createPickingImage( textureSize )
      
      # instance the model
      if self.paintModel:
        self.paintModel.removeNode()
      self.paintModel = self.editModel.copyTo(self.backgroundRender)
      # the backgroundRender should disable all shaders etc.
      self.paintModel.setLightOff(10000)
      self.paintModel.setFogOff(10000)
      self.paintModel.setTextureOff(10000)
      self.paintModel.setShaderOff(10000)
      self.paintModel.setColorScaleOff(10000)
      self.paintModel.setColorOff(10000)
      #self.paintModel.clearTexture()
      #self.paintModel.clearShader()
      #self.paintModel.setTextureOff(10000)
      # tex stage for picking texture
      colorTextureStage = TextureStage("color")
      colorTextureStage.setSort(1) # the color texture is on sort 1
      # load picking texture
      tex = loader.loadTexture("textures/index-%i-%i.png" % (textureSize[0], textureSize[1]))
      tex.setMinfilter(Texture.FTNearest)
      tex.setMagfilter(Texture.FTNearest)
      tex.setWrapU(Texture.WMMirror)
      tex.setWrapV(Texture.WMMirror)
      self.paintModel.setTexture(colorTextureStage,tex,10001)
      self.paintModel.setMat(render, self.editModel.getMat(render))
      
      # define a second texture (may be needed for shaders)
      if False:
        if overlayTexture:
          heightTextureStage = TextureStage("height")
          heightTextureStage.setSort(2) # the color texture is on sort 1
          self.paintModel.setTexture(heightTextureStage,overlayTexture,10001)
  
  # --- modification of the textures ---
  def __startEdit(self):
    messenger.send(EVENT_TEXTUREPAINTER_STARTEDIT)
    # start paint events
    self.accept("mouse1", self.__startPaint)
    self.accept("control-mouse1", self.__startPaint)
    self.accept("shift-mouse1", self.__startPaint)
    self.accept("alt-mouse1", self.__startPaint)
    
    # stop paint events
    self.accept("mouse1-up", self.__stopPaint)
    self.accept("shift-mouse1-up", self.__stopPaint)
    self.accept("control-mouse1-up", self.__stopPaint)
    self.accept("alt-mouse1-up", self.__stopPaint)
    self.accept("shift-alt-mouse1-up", self.__stopPaint)
    self.accept("control-alt-mouse1-up", self.__stopPaint)
    self.accept("shift-control-mouse1-up", self.__stopPaint)
    self.accept("shift-control-alt-mouse1-up", self.__stopPaint)
  
  def __stopEdit(self):
    messenger.send(EVENT_TEXTUREPAINTER_STOPEDIT)
    self.ignore("mouse1")
    self.ignore("mouse1-up")
  
  # --- start the paint tasks ---
  def __startPaint(self):
    self.backcam.node().copyLens(WindowManager.activeWindow.camera.node().getLens())
    self.paintFunction = TEXTUREPAINTER_FUNCTION_PAINT_POINT
    
    # the modification task, which reads the mousepos and modifies the image
    taskMgr.add(self.__paintTask, 'paintTask')
    
    if type(self.editTexture) == Texture:
      # if the image to modify is a texture, start a task up update the image
      taskMgr.doMethodLater(1.0/30, self.__textureUpdateTask, 'textureUpdateTask')
  
  def __stopPaint(self):
    taskMgr.remove('paintTask')
    taskMgr.remove('textureUpdateTask')
  
  # --- modification tasks ---
  def __textureUpdateTask(self, task):
    ''' modify the texture using the edited image
    '''
    self.editTexture.load(self.editImage)
    return task.again
  
  def __paintTask(self, task):
    if not WindowManager.activeWindow or not WindowManager.activeWindow.mouseWatcherNode.hasMouse():
      return
    
    if not self.paintModel:
      print "E: TexturePainter.paintTask: no paintModel"
      return
    # update the camera according to the active camera
    self.backcam.setMat(render, WindowManager.activeWindow.camera.getMat(render))
    # update the mat of the model we currently paint on
    self.paintModel.setMat(render, self.editModel.getMat(render))
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
    
    self.__paintPixel(x,y)
    
    return task.cont
  
  def __paintPixel(self, x, y):
    ''' paint at x/y with the defined settings '''
    if x > self.editImage.getXSize() or y > self.editImage.getYSize():
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
                average += self.editImage.getXelA(x+dx,y+dy) * multiplier
            average /= dividor
            for dx in xrange(-radius, radius+1):
              for dy in xrange(-radius, radius+1):
                multiplier = ((radius-math.fabs(dx))*(radius-math.fabs(dy))) / (radius*radius)
                currentValue = self.editImage.getXelA(x+dx,y+dy)
                r = currentValue.getX() * (1-multiplier*self.paintColor.getX()) + average.getX() * multiplier*self.paintColor.getX()
                g = currentValue.getY() * (1-multiplier*self.paintColor.getY()) + average.getY() * multiplier*self.paintColor.getY()
                b = currentValue.getZ() * (1-multiplier*self.paintColor.getZ()) + average.getZ() * multiplier*self.paintColor.getZ()
                a = currentValue.getW() * (1-multiplier*self.paintColor.getW()) + average.getW() * multiplier*self.paintColor.getW()
                if self.editImage.hasAlpha():
                  self.editImage.setXelA(x+dx,y+dy,VBase4D(r,g,b,a))
                else:
                  self.editImage.setXel(x+dx,y+dy,VBase3D(r,g,b))
          
          elif self.paintEffect == TEXTUREPAINTER_BRUSH_RANDOMIZE:
            for dx in xrange(-radius, radius+1):
              for dy in xrange(-radius, radius+1):
                r = VBase4D(random.random()*self.paintColor.getX()-self.paintColor.getX()/2.,
                           random.random()*self.paintColor.getY()-self.paintColor.getY()/2.,
                           random.random()*self.paintColor.getZ()-self.paintColor.getZ()/2.,
                           random.random()*self.paintColor.getW()-self.paintColor.getW()/2.)
                multiplier = ((radius-math.fabs(dx))*(radius-math.fabs(dy))) / (radius*radius)
                currentValue = self.editImage.getXelA(x+dx,y+dy)
                self.editImage.setXelA(x+dx,y+dy,currentValue+r*multiplier)
      
      elif self.paintMode == TEXTUREPAINTER_FUNCTION_READ:
        col = self.editImage.getXelA(x,y)
        if self.editImage.hasAlpha():
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

texturePainter = TexturePainter()

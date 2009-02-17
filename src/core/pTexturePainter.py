import random, math

from direct.showbase.DirectObject import *
from pandac.PandaModules import TextureAttrib, Texture, PNMImage, \
GraphicsOutput, NodePath, Filename, TextureStage, VBase4D, PNMPainter, \
PNMBrush, VBase3D

from core.pWindow import WindowManager
from core.pMouseHandler import mouseHandler
from core.pConfigDefs import *
from core.pModelModificator import modelModificator

TEXTUREPAINTER_START_PAINT_EVENTS = [
        'mouse1',
        'control-mouse1',
        'shift-mouse1',
        'alt-mouse1',
        ]
TEXTUREPAINTER_STOP_PAINT_EVENTS = [
        'mouse1-up',
        'shift-mouse1-up',
        'control-mouse1-up',
        'alt-mouse1-up',
        'shift-alt-mouse1-up',
        'control-alt-mouse1-up',
        'shift-control-mouse1-up',
        'shift-control-alt-mouse1-up',
]


TEXTUREPAINTER_BRUSH_FLATTEN = 'flatten'
TEXTUREPAINTER_BRUSH_SMOOTH = 'smooth'
TEXTUREPAINTER_BRUSH_RANDOMIZE = 'randomize'

PNMBrush_BrushEffect_Enum = Enum(
  BESet = PNMBrush.BESet,
  BEBlend = PNMBrush.BEBlend,
  BEDarken = PNMBrush.BEDarken,
  BELighten = PNMBrush.BELighten,
  Flatten = TEXTUREPAINTER_BRUSH_FLATTEN,
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

def createOffscreenBuffer(sort, xsize, ysize):
  winprops = WindowProperties.size(xsize,ysize)
  props = FrameBufferProperties()
  props.setRgbColor(1)
  props.setAlphaBits(1)
  props.setDepthBits(1)
  return base.graphicsEngine.makeOutput(
      base.pipe, "offscreenBuffer",
      sort, props, winprops,
      GraphicsPipe.BFRefuseWindow,
      base.win.getGsg(), base.win) 

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


COLOR_PICKER_SHADER = '''//Cg
  
  void vshader(
      uniform float4x4 mat_modelproj,
      in float4 vtx_position : POSITION,
      in float2 vtx_texcoord0 : TEXCOORD0,
      out float2 l_my : TEXCOORD0,
      out float4 l_position : POSITION)
  {
      l_position = mul(mat_modelproj, vtx_position);
      l_my = vtx_texcoord0;
  }
  
  void fshader(
      uniform sampler2D k_paintmap,
      uniform float4 k_mousepos,
      out float4 o_color : COLOR)
  {
      o_color = tex2D(k_paintmap, float2(k_mousepos.r, k_mousepos.g));
  }
  '''

MODEL_COLOR_SHADER = '''//Cg
  
  void vshader(
      uniform float4x4 mat_modelproj,
      in float4 vtx_position : POSITION,
      in float2 vtx_texcoord0 : TEXCOORD0,
      out float2 l_my : TEXCOORD0,
      out float4 l_position : POSITION)
  {
      l_position = mul(mat_modelproj, vtx_position);
      l_my = vtx_texcoord0;
  }
  
  void fshader(
      uniform float4 k_texsize,
      in float2 l_my : TEXCOORD0,
      out float4 o_color : COLOR)
  {
      int x = int((k_texsize.r) * l_my.x);
      int y = int(k_texsize.g)-int((k_texsize.g) * l_my.y);
      float r = float((x%256)/float(255));
      float g = float((y%256)/float(255));
      float b = float( (int(x/256) + int(y/256) * 16) / float(255) );
      o_color = float4(r, g, b, 1);
  }
  '''

class TexturePainter(DirectObject):
  def __init__(self):
    self.editTexture = None
    self.editModel = None
    
    self.texturePainterStatus = TEXTURE_PAINTER_STATUS_DISABLED
    
    self.paintColor = VBase4D(1,1,1,1)
    self.paintSize = 10
    self.paintEffect = PNMBrush.BEBlend
    self.paintSmooth = True
    self.paintMode = TEXTUREPAINTER_FUNCTION_PAINT_POINT
    
    self.painter = None
  
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
    # try stopping if more advanced mode
    #if self.texturePainterStatus == TEXTURE_PAINTER_STATUS_INITIALIZED:
    #  self.stopEditor()
    
    if self.texturePainterStatus == TEXTURE_PAINTER_STATUS_ENABLED:
      self.texturePainterStatus = TEXTURE_PAINTER_STATUS_DISABLED
      self.__disableEditor()
    else:
      print "E: TexturePainter.disableEditor: not enabled", self.texturePainterStatus
  
  # --- 
  def startEditor(self, editModel, editTexture, backgroundShader=MODEL_COLOR_SHADER):
    ''' prepare to paint
    change from enabled to initialized'''
    if self.texturePainterStatus == TEXTURE_PAINTER_STATUS_ENABLED:
      self.texturePainterStatus = TEXTURE_PAINTER_STATUS_INITIALIZED
      self.__startEditor(editModel, editTexture, backgroundShader)
    else:
      print "E: TexturePainter.startEditor: not enabled", self.texturePainterStatus
  
  def stopEditor(self):
    ''' stop painting, automatically stop painting
    change from initialized to enabled'''
    #if self.texturePainterStatus == TEXTURE_PAINTER_STATUS_INITIALIZED:
    #  self.stopPaint()
    if self.texturePainterStatus == TEXTURE_PAINTER_STATUS_INITIALIZED:
      self.texturePainterStatus = TEXTURE_PAINTER_STATUS_ENABLED
      return self.__stopEditor()
    else:
      print "E: TexturePainter.startEditor: not initialized", self.texturePainterStatus
  
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
      #if self.paintModel:
      if self.painter:
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
    # the buffer the model with the color texture is rendered into
    self.modelColorBuffer = None
    self.modelColorCam = None
    # the buffer the picked position color is rendered into
    self.colorPickerBuffer = None
    self.colorPickerCam = None
    # create the buffers
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
  
  def __windowEvent(self, win=None):
    ''' when the editor is enabled, update the buffers etc. when the window
    is resized '''
    print "I: TexturePainter.windowEvent"
    
    # with a fixed backgroudn buffer size this is not needed anymore
    
    if False:
      #if self.texturePainterStatus != TEXTURE_PAINTER_STATUS_DISABLED:
      if self.modelColorBuffer:
        if WindowManager.activeWindow:
          # on window resize there seems to be never a active window
          win = WindowManager.activeWindow.win
        else:
          win = base.win
        if self.modelColorBuffer.getXSize() != win.getXSize() or self.modelColorBuffer.getYSize() != win.getYSize():
          '''print "  - window resized",\
              self.modelColorBuffer.getXSize(),\
              win.getXSize(),\
              self.modelColorBuffer.getYSize(),\
              win.getYSize()'''
          # if the buffer size doesnt match the window size (window has been resized)
          self.__destroyBuffer()
          self.__createBuffer()
          self.__updateModel()
      else:
        print "W: TexturePainter.__windowEvent: no buffer"
        self.__createBuffer()
  
  def __createBuffer(self):
    ''' create the buffer we render in the background into '''
    print "I: TexturePainter.__createBuffer"
    # the window has been modified
    if WindowManager.activeWindow:
      # on window resize there seems to be never a active window
      win = WindowManager.activeWindow.win
    else:
      win = base.win
    
    # get the window size
    self.windowSizeX = win.getXSize()
    self.windowSizeY = win.getYSize()
    
    # create a buffer in which we render the model using a shader
    self.paintMap = Texture()
    # 1.5.4 cant handle non power of 2 buffers
    self.modelColorBuffer = createOffscreenBuffer(-3, TEXTUREPAINTER_BACKGROUND_BUFFER_RENDERSIZE[0], TEXTUREPAINTER_BACKGROUND_BUFFER_RENDERSIZE[1]) #self.windowSizeX, self.windowSizeY)
    self.modelColorBuffer.addRenderTexture(self.paintMap, GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)
    self.modelColorCam = base.makeCamera(self.modelColorBuffer, lens=base.cam.node().getLens(), sort=1)
    
    # Create a small buffer for the shader program that will fetch the point from the texture made
    # by the self.modelColorBuffer
    self.colorPickerImage = PNMImage()
    self.colorPickerTex = Texture()
    self.colorPickerBuffer = base.win.makeTextureBuffer("color picker buffer", 2, 2, self.colorPickerTex, True)
    
    self.colorPickerScene = NodePath('color picker scene')
    
    self.colorPickerCam = base.makeCamera(self.colorPickerBuffer, lens=base.cam.node().getLens(), sort=2)
    self.colorPickerCam.reparentTo(self.colorPickerScene)
    self.colorPickerCam.setY(-2)
    
    cm = CardMaker('color picker scene card')
    cm.setFrameFullscreenQuad()
    pickerCard = self.colorPickerScene.attachNewNode(cm.generate())
    
    loadPicker = NodePath(PandaNode('pointnode'))
    loadPicker.setShader(Shader.make(COLOR_PICKER_SHADER), 10001)
    
    # Feed the paintmap from the paintBuffer to the shader and initial mouse positions
    self.colorPickerScene.setShaderInput('paintmap', self.paintMap)
    self.colorPickerScene.setShaderInput('mousepos', 0, 0, 0, 1)
    self.colorPickerCam.node().setInitialState(loadPicker.getState())
  
  def __destroyBuffer(self):
    print "I: TexturePainter.__destroyBuffer"
    if self.modelColorBuffer:
      
      # Destroy the buffer
      base.graphicsEngine.removeWindow(self.modelColorBuffer)
      self.modelColorBuffer = None
      # Remove the camera
      self.modelColorCam.removeNode()
      del self.modelColorCam
      
      self.colorPickerScene.removeNode()
      del self.colorPickerScene
      # remove cam
      self.colorPickerCam.removeNode()
      del self.colorPickerCam
      # Destroy the buffer
      base.graphicsEngine.removeWindow(self.colorPickerBuffer)
      self.colorPickerBuffer = None
      
      del self.colorPickerTex
      del self.colorPickerImage
  
  def __startEditor(self, editModel, editTexture, backgroundShader=MODEL_COLOR_SHADER):
    print "I: TexturePainter.__startEditor"
    
    # this is needed as on startup the editor may not have had a window etc.
    self.__windowEvent()
    
    if not editModel or not editTexture:
      print "W: TexturePainter.__startEditor: model or texture invalid", editModel, editTexture
      return False
    
    self.editModel = editModel
    self.editTexture = editTexture
    self.editImage = None
    self.backgroundShader = backgroundShader
    
    if type(self.editTexture) == Texture:
      # if the image to modify is a texture, create a pnmImage which we modify
      self.editImage = PNMImage()
      # copy the image from the texture to the working layer
      self.editTexture.store(self.editImage)
    else:
      self.editImage = self.editTexture
    
    # create the brush for painting
    self.painter = PNMPainter(self.editImage)
    self.setBrushSettings( *self.getBrushSettings() )
    
    self.__updateModel()
    
    # start edit
    messenger.send(EVENT_TEXTUREPAINTER_STARTEDIT)
    
    for startEvent in TEXTUREPAINTER_START_PAINT_EVENTS:
      self.accept(startEvent, self.__startPaint)
    for stopEvent in TEXTUREPAINTER_STOP_PAINT_EVENTS:
      self.accept(stopEvent, self.__stopPaint)
    
    self.modelColorCam.node().copyLens(WindowManager.activeWindow.camera.node().getLens())
    
    taskMgr.add(self.__paintTask, 'paintTask')
    
    modelModificator.toggleEditmode(False)
    
    self.isPainting = False
  
  def __stopEditor(self):
    print "I: TexturePainter.__stopEditor"
    # stop edit
    messenger.send(EVENT_TEXTUREPAINTER_STOPEDIT)
    
    for startEvent in TEXTUREPAINTER_START_PAINT_EVENTS:
      self.ignore(startEvent)
    for stopEvent in TEXTUREPAINTER_STOP_PAINT_EVENTS:
      self.ignore(stopEvent)
    
    taskMgr.remove('paintTask')
    # stop edit end
    
    self.editImage = None
    self.editTexture = None
    self.painter = None
    self.brush = None
    
    modelModificator.toggleEditmode(True)
    
    if self.editModel and self.editTexture and self.editImage:
      # hide the model from cam 2
      self.editModel.hide(BitMask32.bit(1))
      self.editModel = None
  
  def __updateModel(self):
    if self.editModel:
      # create a image with the same size of the texture
      textureSize = (self.editTexture.getXSize(), self.editTexture.getYSize())
      
      # create a dummy node, where we setup the parameters for the background rendering
      loadPaintNode = NodePath(PandaNode('paintnode'))
      loadPaintNode.setShader(Shader.make(self.backgroundShader), 10001)
      loadPaintNode.setShaderInput('texsize', textureSize[0], textureSize[1], 0, 0)
      
      # copy the state onto the camera
      self.modelColorCam.node().setInitialState(loadPaintNode.getState())
      
      # the camera gets a special bitmask, to show/hide models from it
      self.modelColorCam.node().setCameraMask(BitMask32.bit(1))
      
      if False:
        # doesnt work, but would be nicer (not messing with the default render state)
        
        hiddenNode = NodePath(PandaNode('hiddennode'))
        hiddenNode.hide(BitMask32.bit(1))
        showTroughNode = NodePath(PandaNode('showtroughnode'))
        showTroughNode.showThrough(BitMask32.bit(1))
        
        self.modelColorCam.node().setTagStateKey('show-on-backrender-cam')
        self.modelColorCam.node().setTagState('False', hiddenNode.getState())
        self.modelColorCam.node().setTagState('True', showTroughNode.getState())
        
        render.setTag('show-on-backrender-cam', 'False')
        self.editModel.setTag('show-on-backrender-cam', 'True')
      else:
        # make only the model visible to the background camera
        render.hide(BitMask32.bit(1))
        self.editModel.showThrough(BitMask32.bit(1))
  
  # --- start the paint tasks ---
  def __startPaint(self):
    self.isPainting = True
  
  def __stopPaint(self):
    self.isPainting = False
  
  # --- modification tasks ---
  def __textureUpdateTask(self, task=None):
    ''' modify the texture using the edited image
    '''
    if type(self.editTexture) == Texture:
      self.editTexture.load(self.editImage)
    
    if task: # task may be None
      return task.again
  
  def __paintTask(self, task):
    #print "I: TexturePainter.__paintTask:"
    
    if not WindowManager.activeWindow or not WindowManager.activeWindow.mouseWatcherNode.hasMouse():
      '''print "  - abort:", WindowManager.activeWindow
      if WindowManager.activeWindow:
        print "  - mouse:", WindowManager.activeWindow.mouseWatcherNode.hasMouse()'''
      return task.cont
    
    
    # update the camera according to the active camera
    #self.modelColorCam.setMat(render, WindowManager.activeWindow.camera.getMat(render))
    
    mpos = base.mouseWatcherNode.getMouse()
    x_ratio = min( max( ((mpos.getX()+1)/2), 0), 1)
    y_ratio = min( max( ((mpos.getY()+1)/2), 0), 1)
    mx = int(x_ratio*self.windowSizeX)
    my = self.windowSizeY - int(y_ratio*self.windowSizeY)
    
    self.colorPickerScene.setShaderInput('mousepos', x_ratio, y_ratio, 0, 1)
    
    if self.colorPickerTex.hasRamImage():
      self.colorPickerTex.store(self.colorPickerImage)
      
      # get the color below the mousepick from the rendered frame
      r = self.colorPickerImage.getRedVal(0,0)
      g = self.colorPickerImage.getGreenVal(0,0)
      b = self.colorPickerImage.getBlueVal(0,0)
      # calculate uv-texture position from the color
      x = r + ((b%16)*256)
      y = g + ((b//16)*256)
      
      if self.isPainting:
        self.__paintPixel(x,y)
        self.__textureUpdateTask()
    else:
      # this might happen if no frame has been rendered yet since creation of the texture
      print "W: TexturePainter.__paintTask: colorPickerTex.hasRamMipmapImage() =", self.colorPickerTex.hasRamImage()
    
    return task.cont
  
  def __paintPixel(self, x, y):
    ''' paint at x/y with the defined settings '''
    
    imageMaxX = self.editImage.getXSize()
    imageMaxY = self.editImage.getYSize()
    def inImage(x,y):
      ''' is the given x/y position within the image '''
      return ((imageMaxX > x >= 0) and (imageMaxY > y >= 0))
    
    # how smooth should be painted
    if self.paintSmooth:
      # a smooth brush
      hardness = 1.0
    else:
      # a hard brush
      hardness = 0.1
    hardness = min(1.0, max(0.05, hardness))
    
    # the paint radius
    radius = int(round(self.paintSize/2.0))
    radiusSquare = float(radius*radius)
    
    # a function to get the brush color/strength, depending on the radius
    def getBrushColor(diffPosX, diffPosY):
      distance = diffPosX**2 + diffPosY**2
      brushStrength = (1 - (min(distance, radiusSquare) / radiusSquare)) / hardness
      return min(1.0, max(0.0, brushStrength))
    
    if inImage(x,y):
      if self.paintMode == TEXTUREPAINTER_FUNCTION_PAINT_POINT:
        if self.paintEffect in [PNMBrush.BESet, PNMBrush.BEBlend, PNMBrush.BEDarken, PNMBrush.BELighten]:
          # render a spot into the texture
          self.painter.drawPoint(x, y)
        
        elif self.paintEffect in [TEXTUREPAINTER_BRUSH_FLATTEN, TEXTUREPAINTER_BRUSH_SMOOTH, TEXTUREPAINTER_BRUSH_RANDOMIZE]:
          
          if self.paintEffect == TEXTUREPAINTER_BRUSH_SMOOTH:
            # calculate average values
            data = dict()
            smoothRadius = 2
            for dx in xrange(-radius, radius+1):
              for dy in xrange(-radius, radius+1):
                if inImage(x+dx,y+dy):
                  average = VBase4D(0)
                  dividor = 0
                  for px in xrange(-smoothRadius,smoothRadius+1):
                    for py in xrange(-smoothRadius,smoothRadius+1):
                      if inImage(x+dx+px,y+dy+py):
                        average += self.editImage.getXelA(x+dx+px,y+dy+py)
                        dividor += 1
                  average /= float(dividor)
                  data[(x+dx,y+dy)] = average
            
            # save to image
            for (px,py), newValue in data.items():
              currentValue = self.editImage.getXelA(px,py)
              diffValue = currentValue - newValue
              
              dx = px - x
              dy = py - y
              
              
              multiplier = getBrushColor(dx, dy)
              print dx, dy, multiplier
              '''if self.paintSmooth:
                multiplier = ((radius-math.fabs(dx))*(radius-math.fabs(dy))) / (radius*radius)
              else:
                # not sure if this is correct
                multiplier = ((radius-math.fabs(dx))*(radius-math.fabs(dy)))'''
              
              '''r = currentValue.getX() * (1-multiplier*self.paintColor.getX()) + diffValue.getX() * multiplier*self.paintColor.getX()
              g = currentValue.getY() * (1-multiplier*self.paintColor.getY()) + diffValue.getY() * multiplier*self.paintColor.getY()
              b = currentValue.getZ() * (1-multiplier*self.paintColor.getZ()) + diffValue.getZ() * multiplier*self.paintColor.getZ()
              a = currentValue.getW() * (1-multiplier*self.paintColor.getW()) + diffValue.getW() * multiplier*self.paintColor.getW()'''
              r = currentValue.getX() - multiplier * diffValue.getX()
              g = currentValue.getY() - multiplier * diffValue.getY()
              b = currentValue.getZ() - multiplier * diffValue.getZ()
              a = currentValue.getW() - multiplier * diffValue.getW()
              if self.editImage.hasAlpha():
                self.editImage.setXelA(px,py,VBase4D(r,g,b,a))
              else:
                self.editImage.setXel(px,py,VBase3D(r,g,b))
              
              #self.editImage.setXelA(x,y,value)
            
          if self.paintEffect == TEXTUREPAINTER_BRUSH_FLATTEN:
            dividor = 0
            average = VBase4D(0)
            for dx in xrange(-radius, radius+1):
              for dy in xrange(-radius, radius+1):
                if inImage(x+dx,y+dy):
                  multiplier = getBrushColor(dx, dy)
                  '''if self.paintSmooth:
                    multiplier = ((radius-math.fabs(dx))*(radius-math.fabs(dy))) / (radius*radius)
                  else:
                    multiplier = ((radius-math.fabs(dx))*(radius-math.fabs(dy)))'''
                  dividor += multiplier
                  average += self.editImage.getXelA(x+dx,y+dy) * multiplier
            average /= dividor
            for dx in xrange(-radius, radius+1):
              for dy in xrange(-radius, radius+1):
                if inImage(x+dx,y+dy):
                  multiplier = getBrushColor(dx, dy)
                  '''if self.paintSmooth:
                    multiplier = ((radius-math.fabs(dx))*(radius-math.fabs(dy))) / (radius*radius)
                  else:
                    # not sure if this is correct
                    multiplier = ((radius-math.fabs(dx))*(radius-math.fabs(dy)))'''
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
                if inImage(x+dx,y+dy):
                  r = VBase4D(random.random()*self.paintColor.getX()-self.paintColor.getX()/2.,
                             random.random()*self.paintColor.getY()-self.paintColor.getY()/2.,
                             random.random()*self.paintColor.getZ()-self.paintColor.getZ()/2.,
                             random.random()*self.paintColor.getW()-self.paintColor.getW()/2.)
                  multiplier = getBrushColor(dx, dy)
                  '''if self.paintSmooth:
                    multiplier = ((radius-math.fabs(dx))*(radius-math.fabs(dy))) / (radius*radius)
                  else:
                    # not sure if this is correct
                    multiplier = ((radius-math.fabs(dx))*(radius-math.fabs(dy)))'''
                  currentValue = self.editImage.getXelA(x+dx,y+dy)
                  self.editImage.setXelA(x+dx,y+dy,currentValue+r*multiplier)
      
      elif self.paintMode == TEXTUREPAINTER_FUNCTION_READ:
        if inImage(x,y):
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

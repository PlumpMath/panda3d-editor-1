from direct.showbase.DirectObject import *
from pandac.PandaModules import TextureAttrib, Texture, PNMImage, \
GraphicsOutput, NodePath, Filename, TextureStage, VBase4D, PNMPainter, \
PNMBrush, VBase3D

from core.pWindow import WindowManager
from core.pMouseHandler import mouseHandler

def getTextureAndStage(nodePath):
  def getStages(gnode, state, texStages): #, textures):
    for i in range(gnode.getNumGeoms()):
      gstate = state.compose(gnode.getGeomState(i))
      attrib = gstate.getAttrib(TextureAttrib.getClassSlot())
      if attrib != None:
        for j in range(attrib.getNumOnStages()):
          texStage = attrib.getOnStage(j)
          texture = attrib.getTexture()
          if (texStage not in texStages) or (texture not in textures):
            texStages.append([texStage, texture])
    return texStages
  
  def rec(parent, state, texStages):
    for child in parent.getChildren():
      texStages = rec(child, state, texStages)
      if child.node().isGeomNode():
        texStages = getStages(child.node(), state, texStages)
    return texStages
  
  texStages = rec(nodePath, nodePath.getNetState(), [])
  return texStages

def createPickingImage(size):
  # Create the image
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
  image.write(imageFilename)

class TexturePainter(DirectObject):
  def __init__(self):
    self.paintModel = None
    self.origModel = None
    self.accept("window-event", self.windowEvent)
    self.enabled = False
  
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
    
    self.accept("mouse1", self.startPaint)
    self.accept("mouse1-up", self.stopPaint)
    self.accept("v", base.bufferViewer.toggleEnable)
    self.accept("V", base.bufferViewer.toggleEnable)
    base.bufferViewer.setPosition("llcorner")
    base.bufferViewer.setCardSize(1.0, 0.0)
    
    self.painter = None
    self.brush = PNMBrush.makeSpot(VBase4D(1, 0, 0, 1), 7, True)
    
    self.enabled = True
  
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
    self.ignoreAll()
    
    self.enabled = False
    
    if self.paintModel != None:
      self.stopEdit()
  
  def startEdit(self, model, texture):
    if self.enabled:
      
      if self.paintModel != None:
        self.stopEdit()
      
      # load the working texture (this must load the real texure of the object)
      self.workTex = texture #loader.loadTexture('models/maps/smiley.rgb')
      
      # copy the image from the texture to the working layer
      self.workLayer = PNMImage()
      self.painter = PNMPainter(self.workLayer)
      self.painter.setPen(self.brush)
      self.workTex.store(self.workLayer)
      
      self.paintModel = model.copyTo(self.backgroundRender) #loader.loadModel('models/smiley.egg')
      if self.paintModel:
        #tester.reparentTo(self.backgroundRender)
        self.paintModel.setMat(render, model.getMat(render))
        textureSize = (texture.getXSize(), texture.getYSize())
        createPickingImage( textureSize )
        self.paintModel.setTexture(loader.loadTexture("textures/index-%i-%i.png" % (textureSize[0], textureSize[1])),1)
        base.graphicsEngine.renderFrame()
        
        self.pickTex.store(self.pickLayer)
        
        self.origModel = model
        self.textureSize = textureSize
      else:
        print "W: TexturePainter.startEdit: error copying model", model, texture
    else:
      print "W: TexturePainter.startEdit: paint mode not enabled!"
  
  def stopEdit(self):
    if self.enabled:
      if self.paintModel:
        self.paintModel.detachNode()
        self.paintModel = None
        self.origModel = None
      self.workLayer = None
      self.painter = None
  
  def startPaint(self):
    taskMgr.add(self.paintTask, 'paintTask')
  def paintTask(self, task):
    self.paint()
    return task.cont
  def stopPaint(self):
    taskMgr.remove('paintTask')
  
  def paint(self):
    if self.enabled and self.paintModel and WindowManager.activeWindow != None:
      # update the camera according to the active camera
      self.backcam.reparentTo(self.backgroundRender)
      self.backcam.setMat(render, WindowManager.activeWindow.camera.getMat(render))
      self.backcam.node().copyLens(WindowManager.activeWindow.camera.node().getLens())
      # update the mat of the model we currently paint on
      self.paintModel.setMat(render, self.origModel.getMat(render))
      
      # render the backbuffer
      base.graphicsEngine.renderFrame()
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
      
      # render a spot into the texture
      self.painter.drawPoint(x, y)
      
      # display the modified texture
      self.workTex.load(self.workLayer)
    else:
      print "W: TexturePainter.paint: paint mode not enabled!"

'''
1,1,1   *   1,0,0  * 100%   => 1,0,0
1,1,1   *   1,0,0  * 50%    => 0.75,0.5,0.5

0,1,1   *   1,0,0  * 100%   >  1,0,0
0,1,1   *   1,0,0  * 50%   >  0.5,0.5,0.5
'''

texturePainter = TexturePainter()

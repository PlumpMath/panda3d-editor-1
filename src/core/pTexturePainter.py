from direct.showbase.DirectObject import *
from pandac.PandaModules import TextureAttrib, Texture, PNMImage, \
GraphicsOutput, NodePath, Filename, TextureStage, VBase3D

from core.pWindow import WindowManager

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

def createPickingImage( size ):
  # create the image
  image = PNMImage(*size)
  for x in xrange(size[0]):
    for y in xrange(size[1]):
      r = x % 256
      g = y % 256
      b = (x // 256) + (y//256) * 16
      image.setXelVal(x,y,r,g,b)
  
  # reverse way is:
  #    tx = r + ((b%16)*256)
  #    ty = g + ((b//16)*256)
  imageFilename = 'data/textures/index-%i-%i.png' % (size[0], size[1])
  image.write(imageFilename)

TEXTURESIZE = [512, 256]
WINDOWSIZE = [800, 600]
PAINTCOLOR = [255,0,0]

class TexturePainter(DirectObject):
  def __init__(self):
    self.paintModel = None
    self.origModel = None
  
  def enableEditor(self):
    # setup an offscreen buffer for the colour index
    self.pickTex = Texture()
    self.pickLayer = PNMImage()
    
    self.buffer = base.win.makeTextureBuffer("pickBuffer", *WINDOWSIZE)
    self.buffer.addRenderTexture(self.pickTex, GraphicsOutput.RTMCopyRam)
    
    self.backcam = base.makeCamera(self.buffer, sort=-10)
    self.backcam.node().copyLens(WindowManager.activeWindow.camera.node().getLens())
    self.background = NodePath("background")
    self.backcam.reparentTo(self.background)
    self.background.setLightOff()
    
    self.accept( "mouse1", self.paint )
    self.accept("v", base.bufferViewer.toggleEnable)
    self.accept("V", base.bufferViewer.toggleEnable)
    base.bufferViewer.setPosition("llcorner")
    base.bufferViewer.setCardSize(1.0, 0.0)
    
    self.setPaintColor( VBase3D(1,0,0) )
    self.setPaintSize( 7 )
    
    self.enabled = True
  
  def disableEditor(self):
    self.ignoreAll()
    
    self.enabled = False
    
    if self.paintModel != None:
      self.stopEdit(self.paintModel)
  
  def setPaintColor(self, paintColor):
    self.paintColor = paintColor
  
  def setPaintSize(self, paintSize):
    self.paintSize = int(paintSize)
  
  def startEdit(self, model, texture):
    if self.enabled:
      
      if self.paintModel != None:
        self.stopEdit(self.paintModel)
      
      # load the working texture (this must load the real texure of the object)
      self.workTex = texture #loader.loadTexture('models/maps/smiley.rgb')
      
      # copy the image from the texture to the working layer
      self.workLayer = PNMImage()
      self.workTex.store( self.workLayer )
      
      self.paintModel = model.copyTo(self.background) #loader.loadModel('models/smiley.egg')
      #tester.reparentTo(self.background)
      self.paintModel.setMat(render, model.getMat(render))
      textureSize = (texture.getXSize(), texture.getYSize())
      createPickingImage( textureSize )
      self.paintModel.setTexture(loader.loadTexture("textures/index-%i-%i.png" % (textureSize[0], textureSize[1])),1)
      base.graphicsEngine.renderFrame()
      self.pickTex.store(self.pickLayer)
      
      self.origModel = model
    else:
      print "W: TexturePainter.startEdit: paint mode not enabled!"
  
  def stopEdit(self, model):
    if self.enabled:
      model.detachNode()
      
      self.paintModel = None
      self.origModel = None
  
  def paint(self):
    if self.enabled:
      self.paintModel.setMat(render, self.origModel.getMat(render))
      
      # copy cameraposition from user-camera
      self.backcam.setMat(render, WindowManager.activeWindow.camera.getMat(render))
      # render the backbuffer
      base.graphicsEngine.renderFrame()
      # save the rendering as texture
      self.pickTex.store(self.pickLayer)
      
      if not base.mouseWatcherNode.hasMouse():
          return
      
      mpos = base.mouseWatcherNode.getMouse()
      mx = int(((mpos.getX()+1)/2)*WINDOWSIZE[0])
      my = WINDOWSIZE[1] - int(((mpos.getY()+1)/2)*WINDOWSIZE[1])
      
      # get the color below the mousepick from the rendered frame
      r = self.pickLayer.getRedVal(mx,my)
      g = self.pickLayer.getGreenVal(mx,my)
      b = self.pickLayer.getBlueVal(mx,my)
      # calculate uv-texture position from the color
      x = r + ((b%16)*256)
      y = g + ((b//16)*256)
      
      # make a square on the worklayer
      for i in xrange(-self.paintSize, self.paintSize+1):
        ny = i + y
        if 0 <= ny < TEXTURESIZE:
          for j in xrange(-self.paintSize, self.paintSize+1):
            nx = j + x
            if 0 <= nx < TEXTURESIZE:
              c = self.workLayer.getXel(nx,ny)
              density = min(1.0,max(0.0, ((i**2+j**2)*1.414 / float(self.paintSize**2*2))))
              p = c*density + (self.paintColor * (1-density))
              self.workLayer.setXel(nx,ny,p[0],p[1],p[2])
      
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
texturePainter.enableEditor()
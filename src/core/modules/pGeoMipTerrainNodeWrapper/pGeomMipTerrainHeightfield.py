import posixpath

from pandac.PandaModules import *

from core.pTexturePainter import texturePainter, PNMBrush_BrushEffect_Enum

from core.pTreeNode import *
from core.pConfigDefs import *

SHADER = """//Cg

void vshader(in  varying float4 vtx_position : POSITION,
             in  varying float2 vtx_texcoord0 : TEXCOORD0,
             in  uniform sampler2D k_heightmap,
             in  uniform float4x4 mat_modelproj,
             out varying float4 l_position : POSITION,
             out float l_bright)
{
// THE ONLY IMPORTANT LINE:
  vtx_position.z = tex2D(k_heightmap, vtx_texcoord0).r;
// THAT WAS THE ONLY IMPORTANT LINE
  l_position=mul(mat_modelproj, vtx_position);
  l_bright = vtx_position.z;
}

void fshader(in float l_bright,
             in float4 l_position : POSITION,
             out float4 o_color:COLOR)
{
  o_color = float4(.1,.1,.1,.1)+l_bright*float4(.8,.8,.8,.8);
} """

class GeoMipTerrainHeightfield(TreeNode):
  def __init__(self, parent=None, geoMipTerrain=None, name='heightfield'):
    self.geoMipTerrain = geoMipTerrain
    self.heightfield = ''
    TreeNode.__init__(self, name)
    TreeNode.reparentTo(self, parent)
    self.mutableParameters['heightfield'] = [ Filepath,
      self.getHeightfield,
      self.setHeightfield,
      None,
      None ]
    self.mutableParameters['paintColor'] = [ Vec4,
      self.getPaintColor,
      self.setPaintColor,
      None,
      None]
    self.mutableParameters['paintSize'] = [ float,
      self.getPaintSize,
      self.setPaintSize,
      None,
      None]
    self.mutableParameters['paintEffect'] = [ PNMBrush_BrushEffect_Enum,
      self.getpaintEffect,
      self.setpaintEffect,
      None,
      None]
    self.paintActive = False
    self.paintColor = Vec4(1,1,1,1)
    self.paintSize = 7
    self.paintEffect = PNMBrush.BESet
    
    self.renderMode = 1
    self.mutableParameters['renderMode'] = [ int,
      self.getRenderMode,
      self.setRenderMode,
      None,
      None]
  
  def startEdit(self):
    # disable the 3d window object selection
    messenger.send(EVENT_SCENEPICKER_MODELSELECTION_DISABLE)
    #self.geoMipTerrain.terrain.setBruteforce(True)
    self.startPaint()
  
  def startPaint(self):
    if not self.paintActive:
      print "I: ShaderWrapper.startPaint"
      texturePainter.selectpaintEffectl(self.geoMipTerrain.terrainNode)
      texturePainter.enableEditor()
      if self.renderMode == 0:
        # update terrain height using geoMip.generate
        texturePainter.startEdit(self.geoMipTerrain.terrain.heightfield())
      if self.renderMode == 1:
        # rendering using a shader
        self.paintImage = self.geoMipTerrain.terrain.heightfield()
        self.paintTexture = Texture()
        self.paintTexture.load(self.paintImage)
        texturePainter.startEdit(self.paintImage)
        self.geoMipTerrain.terrainNode.setShaderInput("heightmap", self.paintTexture)
        self.geoMipTerrain.terrainNode.setShader(Shader.make(SHADER))
        # also apply the shader on the paint-model, hmm how to keep the texture?
        #texturePainter.paintEffectl.setShaderInput("heightmap", self.paintTexture)
        #texturePainter.paintEffectl.setShader(Shader.make(SHADER))
      
      col = VBase4D(self.paintColor[0], self.paintColor[1], self.paintColor[2], self.paintColor[3])
      texturePainter.setBrush(col, self.paintSize, self.paintEffect)
      self.paintActive = True
      self.lastUpdateTime = 0
      taskMgr.add(self.updateTask, 'geoMipUpdateTask')
  
  def updateTask(self, task):
    # update 5 times a second
    if self.renderMode == 0:
      if task.time > self.lastUpdateTime + 0.5:
        print "I: GeoMipTerrainHeightfield.updateTask: updating terrain", task.time
        self.geoMipTerrain.terrain.generate()
        self.lastUpdateTime = task.time
    elif self.renderMode == 1:
      self.paintTexture.load(self.paintImage)
    return task.cont
  
  def stopEdit(self):
    # enable the 3d window object selection
    messenger.send(EVENT_SCENEPICKER_MODELSELECTION_ENABLE)
    if self.renderMode == 0:
      pass
    elif self.renderMode == 1:
      self.geoMipTerrain.terrainNode.clearShader()
      self.geoMipTerrain.terrain.generate()
    self.stopPaint()
  
  def stopPaint(self):
    if self.paintActive:
      taskMgr.remove('geoMipUpdateTask')
      texturePainter.stopEdit()
      texturePainter.disableEditor()
      self.paintActive = False
      # saving the texture
      
      savePath = self.heightfield
      print "I: ShaderWrapper.stopPaint: saving heightfield to:", savePath
      self.geoMipTerrain.terrain.heightfield().write(Filename(savePath))
  
  def setHeightfield(self, heightfield):
    self.heightfield = heightfield
  
  def getHeightfield(self):
    return self.heightfield
  
  def getPaintColor(self):
    return self.paintColor
  def setPaintColor(self, color):
    self.paintColor = color
    col = VBase4D(self.paintColor[0], self.paintColor[1], self.paintColor[2], self.paintColor[3])
    texturePainter.setBrush(col, self.paintSize, self.paintEffect)
  
  def getPaintSize(self):
    return self.paintSize
  def setPaintSize(self, size):
    self.paintSize=size
    col = VBase4D(self.paintColor[0], self.paintColor[1], self.paintColor[2], self.paintColor[3])
    texturePainter.setBrush(col, self.paintSize, self.paintEffect)
  
  def getpaintEffect(self):
    return self.paintEffect
  def setpaintEffect(self, paintEffect):
    self.paintEffect= paintEffect
    col = VBase4D(self.paintColor[0], self.paintColor[1], self.paintColor[2], self.paintColor[3])
    texturePainter.setBrush(col, self.paintSize, self.paintEffect)
  
  def getRenderMode(self):
    return self.paintEffect
  def setRenderMode(self, renderMode):
    if not (renderMode == 0 or renderMode == 1):
      renderMode = 1
    self.renderMode = renderMode
  

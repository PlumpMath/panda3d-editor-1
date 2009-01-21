import posixpath

from pandac.PandaModules import *

from core.pTexturePainter import texturePainter

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
  o_color = l_bright;
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
    self.paintActive = False
    self.paintColor = Vec4(1,1,1,1)
    self.paintSize = 7
    
    self.paintMode = 1
    self.mutableParameters['paintMode'] = [ int,
      self.getPaintMode,
      self.setPaintMode,
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
      texturePainter.selectPaintModel(self.geoMipTerrain.terrainNode)
      texturePainter.enableEditor()
      if self.paintMode == 0:
        # rendering using geoMip.generate
        texturePainter.startEdit(self.geoMipTerrain.terrain.heightfield())
      if self.paintMode == 1:
        # rendering using a shader
        self.paintImage = self.geoMipTerrain.terrain.heightfield()
        self.paintTexture = Texture()
        self.paintTexture.load(self.paintImage)
        texturePainter.startEdit(self.paintImage)
        self.geoMipTerrain.terrainNode.setShaderInput("heightmap", self.paintTexture)
        self.geoMipTerrain.terrainNode.setShader(Shader.make(SHADER))
      
      col = VBase4D(self.paintColor[0], self.paintColor[1], self.paintColor[2], self.paintColor[3])
      texturePainter.setBrush(col, self.paintSize)
      self.paintActive = True
      self.lastUpdateTime = 0
      taskMgr.add(self.updateTask, 'geoMipUpdateTask')
  
  def updateTask(self, task):
    # update 5 times a second
    if self.paintMode == 0:
      if task.time > self.lastUpdateTime + 0.5:
        print "I: GeoMipTerrainHeightfield.updateTask: updating terrain", task.time
        self.geoMipTerrain.terrain.generate()
        self.lastUpdateTime = task.time
    elif self.paintMode == 1:
      self.paintTexture.load(self.paintImage)
    return task.cont
  
  def stopEdit(self):
    # enable the 3d window object selection
    messenger.send(EVENT_SCENEPICKER_MODELSELECTION_ENABLE)
    if self.paintMode == 0:
      pass
    else:
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
    texturePainter.setBrush(col, self.paintSize)
  
  def getPaintSize(self):
    return self.paintSize
  def setPaintSize(self, size):
    self.paintSize=size
    col = VBase4D(self.paintColor[0], self.paintColor[1], self.paintColor[2], self.paintColor[3])
    texturePainter.setBrush(col, self.paintSize)
  
  def getPaintMode(self):
    return self.paintMode
  def setPaintMode(self, paintMode):
    self.paintMode = paintMode
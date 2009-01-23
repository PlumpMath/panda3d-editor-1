import posixpath

from pandac.PandaModules import *

from core.pTexturePainter import texturePainter, PNMBrush_BrushEffect_Enum

from core.pTreeNode import *
from core.pConfigDefs import *

SHADER = """//Cg

void vshader(in  varying float4 vtx_position : POSITION,
             in  varying float2 vtx_texcoord0 : TEXCOORD0,
             in  varying float3 vtx_normal,
             in  uniform sampler2D k_heightmap,
             in  uniform float4x4 mat_modelproj,
             in  uniform float4x4 mat_projection,
             out varying float4 l_position : POSITION,
             out varying float4 l_bright)
{
  //l_bright = float4(0,0,0,vtx_position.z); // +vtx_normal.x,vtx_normal.y,0
  float a = tex2D(k_heightmap, vtx_texcoord0).r;
  float b = tex2D(k_heightmap, vtx_texcoord0+float2(1./128,1./128)).r;
  float c = tex2D(k_heightmap, vtx_texcoord0+float2(0,1./128)).r;
  float d = tex2D(k_heightmap, vtx_texcoord0+float2(1./128,0)).r;
  l_bright = float4(a-b,b-c,c-d,d-a)*2 + float4(.5,.5,.5,.5)*a; //mul(mat_projection, 
// THE ONLY IMPORTANT LINE:
  vtx_position.z = a;
// THAT WAS THE ONLY IMPORTANT LINE
  l_position=mul(mat_modelproj, vtx_position);
}

void fshader(in float4 l_bright,
             in float4 l_position : POSITION,
             out float4 o_color:COLOR)
{
  o_color = l_bright;
} """

COMPILED_SHADER = Shader.make(SHADER)

BACKGROUND_SHADER = """//Cg

void vshader(in  varying float4 vtx_position : POSITION,
             in  varying float2 vtx_texcoord0 : TEXCOORD0,
             in  varying float3 vtx_normal,
             in  uniform sampler2D k_heightmap,
             in  uniform sampler2D tex_0,
             in  uniform float4x4 mat_modelproj,
             in  uniform float4x4 mat_projection,
             out varying float4 l_position : POSITION,
             out varying float4 l_bright)
{
  float a = tex2D(k_heightmap, vtx_texcoord0);
// THE ONLY IMPORTANT LINE:
  vtx_position.z = a;
// THAT WAS THE ONLY IMPORTANT LINE
  l_position=mul(mat_modelproj, vtx_position);
// coloring
  l_bright = tex2D(tex_0, vtx_texcoord0);
}

void fshader(in float4 l_bright,
             in float4 l_position : POSITION,
             out float4 o_color:COLOR)
{
  o_color = l_bright;
} """
COMPILED_BACKGROUND_SHADER = Shader.make(BACKGROUND_SHADER)

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
    
    self.renderMode = 1
    self.mutableParameters['renderMode'] = [ int,
      self.getRenderMode,
      self.setRenderMode,
      None,
      None]
  
  def startEdit(self):
    # disable the 3d window object selection
    messenger.send(EVENT_SCENEPICKER_MODELSELECTION_DISABLE)
    
    if self.renderMode == 0:
      # update terrain height using geoMip.generate
      texturePainter.enableEditor(self.geoMipTerrain.terrainNode, self.geoMipTerrain.terrain.heightfield())
    if self.renderMode == 1:
      # rendering using a shader
      self.paintImage = self.geoMipTerrain.terrain.heightfield()
      self.paintTexture = Texture()
      self.paintTexture.load(self.paintImage)
      texturePainter.enableEditor(self.geoMipTerrain.terrainNode, self.paintImage)
      texturePainter.startEdit()
      self.geoMipTerrain.terrainNode.setShaderInput("heightmap", self.paintTexture)
      self.geoMipTerrain.terrainNode.setShader(COMPILED_SHADER)
      # also apply the shader on the paint-model, hmm how to keep the texture?
      texturePainter.paintModel.setShaderInput("heightmap", self.paintTexture)
      texturePainter.paintModel.setShader(COMPILED_BACKGROUND_SHADER)
    
    self.lastUpdateTime = 0
    taskMgr.add(self.updateTask, 'geoMipUpdateTask')
  
  def updateTask(self, task):
    # update 5 times a second
    if task.time > self.lastUpdateTime + 0.5:
      self.lastUpdateTime = task.time
      if self.renderMode == 0:
          print "I: GeoMipTerrainHeightfield.updateTask: updating terrain", task.time
          self.geoMipTerrain.terrain.generate()
      elif self.renderMode == 1:
        texturePainter.paintModel.setShader(COMPILED_BACKGROUND_SHADER)
        texturePainter.paintModel.setShaderInput("heightmap", self.paintTexture)
    if self.renderMode == 1:
      self.paintTexture.load(self.geoMipTerrain.terrain.heightfield())
    return task.cont
  
  def stopEdit(self):
    taskMgr.remove('geoMipUpdateTask')
    
    # enable the 3d window object selection
    messenger.send(EVENT_SCENEPICKER_MODELSELECTION_ENABLE)
    
    # saving the texture
    print "saving the heightfield to", self.heightfield
    self.geoMipTerrain.terrain.heightfield().write(Filename(self.heightfield))
    
    # stop the shader and regenerate the terrain
    if self.renderMode == 0:
      pass
    elif self.renderMode == 1:
      self.geoMipTerrain.terrainNode.clearShader()
      self.geoMipTerrain.terrain.generate()
    
    # stop painting
    texturePainter.stopEdit()
    texturePainter.disableEditor()
  
  def setHeightfield(self, heightfield):
    self.heightfield = heightfield
    self.stopEdit()
    self.geoMipTerrain.update()
    self.startEdit()
  
  def getHeightfield(self):
    return self.heightfield
  
  def getRenderMode(self):
    return self.renderMode
  def setRenderMode(self, renderMode):
    if not (renderMode == 0 or renderMode == 1):
      renderMode = 1
    self.renderMode = renderMode

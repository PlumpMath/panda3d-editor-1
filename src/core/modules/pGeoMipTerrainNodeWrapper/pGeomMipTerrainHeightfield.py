import posixpath

from pandac.PandaModules import *

from core.pTexturePainter import texturePainter, PNMBrush_BrushEffect_Enum
from core.pCommonPath import relpath
from core.pTreeNode import *
from core.pConfigDefs import *

# uniform float4 texpix_x contains the same as i manually input using k_heightmapSize
# thuogh k_heightmapSize adds another value, the color scaling
# color is on tex0
# height is on tex1
SHADER = """//Cg
  
  void vshader(
          in  varying float4 vtx_position : POSITION,
          in  varying float2 vtx_texcoord0 : TEXCOORD0,
          in  varying float3 vtx_normal,
          in  uniform sampler2D tex_0,
          in  uniform sampler2D tex_1,
          //in  uniform sampler2D k_heightmap,
          in  uniform float4x4 mat_modelproj,
          in  uniform float4x4 mat_projection,
          out varying float4 l_position : POSITION,
          out varying float4 l_bright)
  {
    // vertex height
    float a = tex2D(tex_1, vtx_texcoord0).r;
    vtx_position.z = a;
    l_position=mul(mat_modelproj, vtx_position);
    // color
    float b = tex2D(tex_1, vtx_texcoord0+float2(1./128,0)).r;
    float c = tex2D(tex_1, vtx_texcoord0+float2(0,1./128)).r;
    float multiplier = float(8.0);
    l_bright = float4(0.5+multiplier*(a-b), .5+multiplier*(a-b)+4*(a-c), .5+multiplier*(a-c), 1);
  }
  
  void fshader(
          in float4 l_bright,
          in float4 l_position : POSITION,
          out float4 o_color:COLOR)
  {
    o_color = l_bright;
  }
  """
COMPILED_SHADER = Shader.make(SHADER)

BACKGROUND_SHADER_OLD = """//Cg
  
  void vshader(
          in  varying float4 vtx_position : POSITION,
          in  varying float2 vtx_texcoord0 : TEXCOORD0,
          in  varying float3 vtx_normal,
          in  uniform sampler2D tex_0,
          in  uniform sampler2D tex_1,
          in  uniform float4x4 mat_modelproj,
          in  uniform float4x4 mat_projection,
          out varying float4 l_position : POSITION,
          out varying float4 l_bright,
          out float2 l_texcoord0 : TEXCOORD0
        )
  {
    // vertex height
    float a = tex2D(tex_1, vtx_texcoord0);
    vtx_position.z = a;
    l_position=mul(mat_modelproj, vtx_position);
    // coloring
    l_texcoord0 = vtx_texcoord0;
    
    // this is somehow required..........
    l_bright = tex2D(tex_0, vtx_texcoord0);
  }
  
  void fshader(
          in float4 l_bright,
          in float2 l_texcoord0 : TEXCOORD0,
          uniform sampler2D tex_0 : TEXUNIT0,
          uniform sampler2D tex_1 : TEXUNIT1,
          in float4 l_position : POSITION,
          out float4 o_color:COLOR)
  {
    o_color = tex2D(tex_1, l_texcoord0);
  }
  """
BACKGROUND_SHADER = """//Cg
  
  void vshader(
          in  varying float4 vtx_position : POSITION,
          in  varying float2 vtx_texcoord0 : TEXCOORD0,
          in  varying float3 vtx_normal,
          in  uniform sampler2D tex_0,
          in  uniform sampler2D tex_1,
          in  uniform float4x4 mat_modelproj,
          in  uniform float4x4 mat_projection,
          out varying float4 l_position : POSITION,
          out varying float4 l_bright,
          out float2 l_texcoord0 : TEXCOORD0
        )
  {
    // vertex height
    float a = tex2D(tex_1, vtx_texcoord0);
    vtx_position.z = a;
    l_position=mul(mat_modelproj, vtx_position);
    // coloring
    l_texcoord0 = vtx_texcoord0;
    
    // this is somehow required..........
    //l_bright = tex2D(tex_0, vtx_texcoord0);
  }
  
  void fshader(
      uniform float4 k_texsize,
      in float2 l_texcoord0 : TEXCOORD0,
      out float4 o_color : COLOR)
  {
      int x = int((k_texsize.r) * l_texcoord0.x);
      int y = int(k_texsize.g)-int((k_texsize.g) * l_texcoord0.y);
      float r = float((x%256)/float(255));
      float g = float((y%256)/float(255));
      float b = float( (int(x/256) + int(y/256) * 16) / float(255) );
      o_color = float4(r, g, b, 1);
  }
  
  /*void fshader(
          in float4 l_bright,
          in float2 l_texcoord0 : TEXCOORD0,
          uniform sampler2D tex_0 : TEXUNIT0,
          uniform sampler2D tex_1 : TEXUNIT1,
          in float4 l_position : POSITION,
          out float4 o_color:COLOR)
  {
    o_color = tex2D(tex_1, l_texcoord0);
  }*/
  """
COMPILED_BACKGROUND_SHADER = Shader.make(BACKGROUND_SHADER)

class GeoMipTerrainHeightfield(TreeNode):
  ''' this node handles the height texture of the geomipterrain
  '''
  className = 'Heightfield'
  def __init__(self, parent=None, geoMipTerrain=None, name='heightfield'):
    self.geoMipTerrain = geoMipTerrain
    self.heightfield = ''
    TreeNode.__init__(self, name)
    TreeNode.reparentTo(self, parent)
    
    self.renderMode = 1
    self.mutableParameters['paint mode (shader)'] = [ int,
        self.getRenderMode,
        self.setRenderMode,
        None,
        None,
        False ] # should not be saved into the parameters, as it's compuer dependant
    self.shaderColor = 8.0
    self.mutableParameters['colorstrength'] = [ float,
        self.getShaderColor,
        self.setShaderColor,
        None,
        None,
        True]
    
    self.possibleChildren = []
    self.possibleFunctions = ['save', 'saveAs', 'revert']
    
    self.lastUpdateTime = 0
  
  def getShaderColor(self):
    return self.shaderColor
  def setShaderColor(self, color):
    color = max(0.1, min(64., color))
    self.shaderColor = color
    if TreeNode.isEditmodeStarted(self) and self.renderMode == 1:
      self.geoMipTerrain.terrain.getRoot().setShaderInput("heightmapSize",
          float(self.geoMipTerrain.terrain.heightfield().getXSize()),
          float(self.geoMipTerrain.terrain.heightfield().getYSize()), self.shaderColor, 0 )
  
  def startEdit(self):
    if not TreeNode.isEditmodeStarted(self):
      TreeNode.startEdit(self)
      
      # disable the 3d window object selection
      messenger.send(EVENT_SCENEPICKER_MODELSELECTION_DISABLE)
      
      if self.renderMode == 0:
        # update terrain height using geoMip.generate
        texturePainter.startEditor(self.geoMipTerrain.terrain.getRoot(), self.geoMipTerrain.terrain.heightfield())
        #texturePainter.startEdit()
      if self.renderMode == 1:
        # backup bruteforce state, and activate it
        self.bruteforceState =self.geoMipTerrain.terrain.getBruteforce()
        self.geoMipTerrain.terrain.setBruteforce(True)
        self.geoMipTerrain.terrain.update()
        
        # get the paint texture
        self.paintImage = self.geoMipTerrain.terrain.heightfield()
        self.paintTexture = Texture()
        self.paintTexture.load(self.paintImage)
        
        # prepare the shader inputs
        colorTextureStage = TextureStage("color")
        colorTextureStage.setSort(1) # the color texture is on sort 1
        heightTextureStage = TextureStage("height")
        heightTextureStage.setSort(2) # the color texture is on sort 1
        # create a copy of the terrain and update it with a shader
        self.geoMipTerrainCopy = self.geoMipTerrain.terrain.getRoot().copyTo(self.getParentNodepath())
        self.geoMipTerrainCopy.setTextureOff(10000)
        self.geoMipTerrainCopy.setTexture(heightTextureStage, self.paintTexture, 10001)
        self.geoMipTerrainCopy.setTexture(colorTextureStage, self.paintTexture, 10001)
        self.geoMipTerrainCopy.setShader(COMPILED_SHADER)
        
        # start the texture painter
        #texturePainter.setEditTexture(self.paintImage)
        #texturePainter.setEditModel(self.geoMipTerrain.terrain.getRoot())
        texturePainter.enableEditor()
        texturePainter.startEditor(self.geoMipTerrainCopy, self.geoMipTerrain.terrain.heightfield(), BACKGROUND_SHADER) #, self.paintTexture)
        #texturePainter.startPaint()
        heightTextureStage = TextureStage("height")
        heightTextureStage.setSort(2) # the color texture is on sort 1
        #texturePainter.backgroundRender.setTexture(heightTextureStage,self.paintTexture,10001)
        #texturePainter.backgroundRender.setShader(COMPILED_BACKGROUND_SHADER,10001)
        #texturePainter.paintModel.setTexture(heightTextureStage,self.paintTexture,10001)
        #texturePainter.paintModel.setShader(COMPILED_BACKGROUND_SHADER,10001)
        
        # hide the original terrain
        self.geoMipTerrain.terrain.getRoot().hide()
      
      taskMgr.add(self.updateTask, 'geoMipUpdateTask')
  
  def updateTask(self, task):
    # update 5 times a second
    if task.time > self.lastUpdateTime + 0.5:
      self.lastUpdateTime = task.time
      if self.renderMode == 0:
          print "I: GeoMipTerrainHeightfield.updateTask: updating terrain", task.time
          self.geoMipTerrain.terrain.update()
      elif self.renderMode == 1:
        pass
        '''if base.mouseWatcherNode.hasMouse(): # the mouse leaving the window makes shaders crash, maybe this fixes it?
          texturePainter.paintModel.setShader(COMPILED_BACKGROUND_SHADER)'''
        #heightTextureStage = TextureStage("height")
        #heightTextureStage.setSort(2) # the color texture is on sort 1
        #texturePainter.paintModel.setTexture(heightTextureStage,self.paintTexture,10001)
        #texturePainter.paintModel.setShader(COMPILED_BACKGROUND_SHADER,10001)
        self.paintTexture.load(self.paintImage)
    if self.renderMode == 1:
      self.paintTexture.load(self.geoMipTerrain.terrain.heightfield())
      '''heightTextureStage = TextureStage("height")
      heightTextureStage.setSort(2) # the color texture is on sort 1
      texturePainter.backgroundRender.setTexture(heightTextureStage,self.paintTexture,10001)'''
    return task.cont
  
  def stopEdit(self):
    if TreeNode.isEditmodeStarted(self):
      taskMgr.remove('geoMipUpdateTask')
      
      # enable the 3d window object selection
      messenger.send(EVENT_SCENEPICKER_MODELSELECTION_ENABLE)
      
      # stop the shader and regenerate the terrain
      if self.renderMode == 0:
        pass
      elif self.renderMode == 1:
        pass
      
      # stop painting
      texturePainter.stopEditor()
      texturePainter.disableEditor()
      
      # restore bruteforce state
      #self.geoMipTerrain.terrain.colorMap().copyFrom(editedImage)
      self.geoMipTerrain.terrain.setBruteforce(self.bruteforceState)
      self.geoMipTerrain.terrain.getRoot().clearShader()
      #self.geoMipTerrain.terrain.update()
      # restore the real terrain
      self.geoMipTerrainCopy.removeNode()
      # must use generate, update is not recognizing the chagnes
      self.geoMipTerrain.terrain.generate()
      self.geoMipTerrain.terrain.getRoot().show()
      
      TreeNode.stopEdit(self)
  
  def revert(self):
    self.stopEdit()
    self.geoMipTerrain.setHeightfield(self.heightfield)
    self.geoMipTerrain.terrain.generate()
    self.startEdit()
  
  def save(self):
    # saving the texture
    print "I: GeoMipTerrainHeightfield.save: saving as:", self.heightfield
    self.geoMipTerrain.terrain.heightfield().write(Filename(self.heightfield))
  
  def saveAs(self, filename):
    print "I: GeoMipTerrainHeightfield.save: saving as:", self.heightfield
    self.geoMipTerrain.terrain.heightfield().write(Filename(filename))
  
  def getRenderMode(self):
    return self.renderMode
  
  def setRenderMode(self, renderMode):
    # backup editing
    editStarted = TreeNode.isEditmodeStarted(self)
    if editStarted:  self.stopEdit()
    # change stuff
    if not (renderMode == 0 or renderMode == 1):
      renderMode = 1
    self.renderMode = renderMode
    # restore editing
    if editStarted:  self.startEdit()

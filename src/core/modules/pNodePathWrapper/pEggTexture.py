from core.pTexturePainter import texturePainter
from core.pConfigDefs import * # imports Enum
from core.modules.pNodePathWrapper.pEggBase import *

class TextureLayer:
  ''' a texturelayer consists of a texture and a stage
  '''
  def __init__(self, texture=None, stage=None):
    self.texture = texture
    self.stage = stage

def getTextureLayers(nodePath):
  ''' return a TextureLayer object for each texture and stage that is found on
  a object '''
  def getStages(gnode, state, texStages): #, textures):
    for i in range(gnode.getNumGeoms()):
      gstate = state.compose(gnode.getGeomState(i))
      attrib = gstate.getAttrib(TextureAttrib.getClassSlot())
      if attrib != None:
        for j in range(attrib.getNumOnStages()):
          texStage = attrib.getOnStage(j)
          texture = attrib.getTexture()
          if (texStage not in texStages) or (texture not in textures):
            texStages.append(TextureLayer(stage=texStage, texture=texture))
    return texStages
  
  def rec(parent, state, texStages):
    for child in parent.getChildren():
      texStages = rec(child, state, texStages)
      if child.node().isGeomNode():
        texStages = getStages(child.node(), state, texStages)
    return texStages
  
  texStages = rec(nodePath, nodePath.getNetState(), [])
  return texStages


TextureStage_ModeEnum = Enum(
  MModulate = TextureStage.MModulate,
  MDecal = TextureStage.MDecal,
  MBlend = TextureStage.MBlend,
  MReplace = TextureStage.MReplace,
  MAdd = TextureStage.MAdd,
  MCombine = TextureStage.MCombine,
  MBlendColorScale = TextureStage.MBlendColorScale,
  MModulateGlow = TextureStage.MModulateGlow,
  MModulateGloss = TextureStage.MModulateGloss,
  MNormal = TextureStage.MNormal,
  MNormalHeight = TextureStage.MNormalHeight,
  MGlow = TextureStage.MGlow,
  MGloss = TextureStage.MGloss,
  MHeight = TextureStage.MHeight,
  MSelector = TextureStage.MSelector,
)

TextureStage_CombineModeEnum = Enum(
  CMUndefined = TextureStage.CMUndefined,
  CMReplace = TextureStage.CMReplace,
  CMModulate = TextureStage.CMModulate,
  CMAdd = TextureStage.CMAdd,
  CMAddSigned = TextureStage.CMAddSigned,
  CMInterpolate = TextureStage.CMInterpolate,
  CMSubtract = TextureStage.CMSubtract,
  CMDot3Rgb = TextureStage.CMDot3Rgb,
  CMDot3Rgba = TextureStage.CMDot3Rgba,
)

TextureStage_CombineSourceEnum = Enum(
  CSUndefined = TextureStage.CSUndefined,
  CSTexture = TextureStage.CSTexture,
  CSConstant = TextureStage.CSConstant,
  CSPrimaryColor = TextureStage.CSPrimaryColor,
  CSPrevious = TextureStage.CSPrevious,
  CSConstantColorScale = TextureStage.CSConstantColorScale,
  CSLastSavedResult = TextureStage.CSLastSavedResult,
)

TextureStage_CombineOperandEnum = Enum(
  COUndefined        = TextureStage.COUndefined,
  COSrcColor         = TextureStage.COSrcColor,
  COOneMinusSrcColor = TextureStage.COOneMinusSrcColor,
  COSrcAlpha         = TextureStage.COSrcAlpha,
  COOneMinusSrcAlpha = TextureStage.COOneMinusSrcAlpha,
)

TexGenAttrib_PandaCompareFuncEnum = Enum(
  MNone = TexGenAttrib.MNone,
  MNever = TexGenAttrib.MNever,
  MLess = TexGenAttrib.MLess,
  MEqual = TexGenAttrib.MEqual,
  MLessEqual = TexGenAttrib.MLessEqual,
  MGreater = TexGenAttrib.MGreater,
  MNotEqual = TexGenAttrib.MNotEqual,
  MGreaterEqual = TexGenAttrib.MGreaterEqual,
  MAlways = TexGenAttrib.MAlways,
)

TexGenAttrib_TexGenModeEnum = Enum(
  MOff = TexGenAttrib.MOff,
  MEyeSphereMap = TexGenAttrib.MEyeSphereMap,
  MWorldCubeMap = TexGenAttrib.MWorldCubeMap,
  MEyeCubeMap = TexGenAttrib.MEyeCubeMap,
  MWorldNormal = TexGenAttrib.MWorldNormal,
  MEyeNormal = TexGenAttrib.MEyeNormal,
  MWorldPosition = TexGenAttrib.MWorldPosition,
  MUnused = TexGenAttrib.MUnused,
  MEyePosition = TexGenAttrib.MEyePosition,
  MPointSprite = TexGenAttrib.MPointSprite,
  MLightVector = TexGenAttrib.MLightVector,
  MConstant = TexGenAttrib.MConstant,
)

Texture_WrapModeEnum = Enum(
  WMClamp = Texture.WMClamp,
  WMRepeat = Texture.WMRepeat,
  WMMirror = Texture.WMMirror,
  WMMirrorOnce = Texture.WMMirrorOnce,
  WMBorderColor = Texture.WMBorderColor,
  WMInvalid = Texture.WMInvalid,
)

Texture_CompressionMode = Enum(
  CMDefault = Texture.CMDefault,
  CMOff = Texture.CMOff,
  CMOn = Texture.CMOn,
  CMFxt1 = Texture.CMFxt1,
  CMDxt1 = Texture.CMDxt1,
  CMDxt2 = Texture.CMDxt2,
  CMDxt3 = Texture.CMDxt3,
  CMDxt4 = Texture.CMDxt4,
  CMDxt5 = Texture.CMDxt5,
)

class ObjectEggTexture(ObjectEggBase):
  def __init__(self, parent, modelWrapper, eggTexture):
    ObjectEggBase.__init__(self, parent, modelWrapper, 'EggTexture')
    self.eggTexture = eggTexture
  
  def destroy(self):
    self.stopEdit()
    ObjectEggBase.destroy(self)
    self.eggTexture = None
    self.modelWrapper = None
  
  def startEdit(self):
    ObjectEggBase.startEdit(self)
    print "I: ObjectEggTexture.startEdit"
    # search for the corresponding nodepath-texture in the egg-file
    eggTextureFilename = self.eggTexture.getFilename()
    texture = None
    for texLayer in getTextureLayers(self.modelWrapper.model):
      if str(eggTextureFilename) in str(texLayer.texture.getFullpath()):
        #print "I: ObjectEggTexture.startEdit: modifying texture", str(eggTextureFilename), str(texLayer.texture.getFullpath())
        texture = texLayer.texture
    if texture:
      #print "I: ObjectEggTexture.startEdit: editing texture", texture
      texturePainter.selectPaintModel(self.modelWrapper.model)
      texturePainter.enableEditor()
      texturePainter.startEdit(texture)
    else:
      print "I: ObjectEggTexture.startEdit: texture not found", eggTextureFilename
  
  def stopEdit(self):
    ObjectEggBase.stopEdit(self)
    texturePainter.stopEdit()
    texturePainter.disableEditor()
  
  def setParameters(self, parameters):
    pass
  
  def getParameters(self):
    parameters = dict()
    return parameters
  

from pandac.PandaModules import *

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
      if hasattr(TextureAttrib, 'getClassSlot'): # 1.6 uses getClassSlot
        attrib = gstate.getAttrib(TextureAttrib.getClassSlot())
      elif hasattr(TextureAttrib, 'getClassType'): # 1.5.4 uses getClassType
        attrib = gstate.getAttrib(TextureAttrib.getClassType())
      else:
        print "E: getTextureLayers.getStages: cannot read attrib"
        return texStages
      if attrib != None:
        for j in range(attrib.getNumOnStages()):
          texStage = attrib.getOnStage(j)
          texture = attrib.getTexture()
          if (texStage not in texStages) or (texture not in textures):
            texStages.append(TextureLayer(stage=texStage, texture=texture))
    return texStages
  
  def rec(parent, state, texStages):
    print "I: getTextureLayers.rec:", type(parent)
    # in 1.5.4 the parent type nodepathcollection has no getChildren
    # type(parent) allways yields nodepath, so i must use try/except
    try:
      for child in parent.getChildren():
        texStages = rec(child, state, texStages)
        if child.node().isGeomNode():
          texStages = getStages(child.node(), state, texStages)
    except:
      for child in parent.getChildrenAsList():
        texStages = rec(child, state, texStages)
        if child.node().isGeomNode():
          texStages = getStages(child.node(), state, texStages)
    return texStages
  
  texStages = rec(nodePath, nodePath.getNetState(), [])
  return texStages


TextureStage_Mode_Enum = Enum(
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

TextureStage_CombineMode_Enum = Enum(
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

TextureStage_CombineSource_Enum = Enum(
  CSUndefined = TextureStage.CSUndefined,
  CSTexture = TextureStage.CSTexture,
  CSConstant = TextureStage.CSConstant,
  CSPrimaryColor = TextureStage.CSPrimaryColor,
  CSPrevious = TextureStage.CSPrevious,
  CSConstantColorScale = TextureStage.CSConstantColorScale,
  CSLastSavedResult = TextureStage.CSLastSavedResult,
)

TextureStage_CombineOperand_Enum = Enum(
  COUndefined        = TextureStage.COUndefined,
  COSrcColor         = TextureStage.COSrcColor,
  COOneMinusSrcColor = TextureStage.COOneMinusSrcColor,
  COSrcAlpha         = TextureStage.COSrcAlpha,
  COOneMinusSrcAlpha = TextureStage.COOneMinusSrcAlpha,
)

TexGenAttrib_PandaCompareFunc_Enum = Enum(
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

TexGenAttrib_TexGenMode_Enum = Enum(
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

Texture_WrapMode_Enum = Enum(
  WMClamp = Texture.WMClamp,
  WMRepeat = Texture.WMRepeat,
  WMMirror = Texture.WMMirror,
  WMMirrorOnce = Texture.WMMirrorOnce,
  WMBorderColor = Texture.WMBorderColor,
  WMInvalid = Texture.WMInvalid,
)

Texture_CompressionMode_Enum = Enum(
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

Texture_TextureType_Enum = Enum(
TT1dTexture = Texture.TT1dTexture,
TT2dTexture = Texture.TT2dTexture,
TT3dTexture = Texture.TT3dTexture,
TTCubeMap  = Texture.TTCubeMap,
)

Texture_ComponentType_Enum = Enum(
  TUnsignedByte = Texture.TUnsignedByte,
  TUnsignedShort = Texture.TUnsignedShort,
  TFloat = Texture.TFloat,
)

Texture_Format_Enum = Enum(
  FDepthStencil = Texture.FDepthStencil,
  FDepthComponent = Texture.FDepthComponent,
  FColorIndex = Texture.FColorIndex,
  FRed = Texture.FRed,
  FGreen = Texture.FGreen,
  FBlue = Texture.FBlue,
  FAlpha = Texture.FAlpha,
  FRgb = Texture.FRgb,
  FRgb5 = Texture.FRgb5,
  FRgb8 = Texture.FRgb8,
  FRgb12 = Texture.FRgb12,
  FRgb332 = Texture.FRgb332,
  FRgba = Texture.FRgba,
  FRgbm = Texture.FRgbm,
  FRgba4 = Texture.FRgba4,
  FRgba5 = Texture.FRgba5,
  FRgba8 = Texture.FRgba8,
  FRgba12 = Texture.FRgba12,
  FLuminance = Texture.FLuminance,
  FLuminanceAlpha = Texture.FLuminanceAlpha,
  FLuminanceAlphamask = Texture.FLuminanceAlphamask,
  FRgba16 = Texture.FRgba16,
  FRgba32 = Texture.FRgba32,
)

Texture_Min_FilterType_Enum = Enum(
  FTNearest = Texture.FTNearest,
  FTLinear = Texture.FTLinear,
  FTDefault = Texture.FTDefault,
  FTInvalid = Texture.FTInvalid,
)

Texture_Mag_FilterType_Enum = Enum(
  FTNearest = Texture.FTNearest,
  FTLinear = Texture.FTLinear,
  FTNearestMipmapNearest = Texture.FTNearestMipmapNearest,
  FTLinearMipmapNearest = Texture.FTLinearMipmapNearest,
  FTNearestMipmapLinear = Texture.FTNearestMipmapLinear,
  FTLinearMipmapLinear = Texture.FTLinearMipmapLinear,
  FTShadow = Texture.FTShadow,
  FTDefault = Texture.FTDefault,
  FTInvalid = Texture.FTInvalid,
)

Texture_QualityLevel_Enum = Enum(
  QLDefault = Texture.QLDefault,
  QLFastest = Texture.QLFastest,
  QLNormal = Texture.QLNormal,
  QLBest = Texture.QLBest,
)

class ObjectEggTexture(ObjectEggBase):
  className = 'EggTexture'
  def __init__(self, parent, modelWrapper, eggTexture):
    ObjectEggBase.__init__(self, parent, modelWrapper, 'EggTexture')
    self.eggTexture = eggTexture
    self.possibleFunctions = ['save']
    
    self.editTexture = None
    self.editTextureFilename = None
  
  def destroy(self):
    print "I: ObjectEggTexture.destroy"
    self.stopEdit()
    ObjectEggBase.destroy(self)
    self.eggTexture = None
    self.modelWrapper = None
    
    # TODO RELEASE OF TEXTURES DOESNT WORK YET
    if self.editTexture:
      print "  - release texture", self.editTextureFilename
      TexturePool.releaseTexture(self.editTexture)
    TexturePool.releaseAllTextures()
    
    self.editTexture = None
    self.editTextureFilename = None
  
  def startEdit(self):
    ''' as we are editing a egg-file, but for texture painting we modify a texture
    on the model, we need to find the corresponding texture's from the 3dmodel and
    the eggdata
    if we find it we start modifying it
    WARNING: the current implementation may select the wrong texture to edit
    if the filename of a texture is equal, but in different subdirectories
    '''
    if ObjectEggBase.isEditmodeEnabled(self):
      ObjectEggBase.startEdit(self)
      print "I: ObjectEggTexture.startEdit"
      # search for the corresponding nodepath-texture in the egg-file
      eggTextureFilename = str(self.eggTexture.getFilename()).lstrip('./')
      # the texture we will modify
      editTexture = None
      modelTextureLayers = getTextureLayers(self.modelWrapper.model)
      for modelTexLayer in modelTextureLayers:
        modelTexFilename = str(modelTexLayer.texture.getFullpath())
        if eggTextureFilename in modelTexFilename:
          editTexture = modelTexLayer.texture
      if editTexture:
        print "I: ObjectEggTexture.startEdit: start editing texture", eggTextureFilename
        print "  - selected from these: ", [tex.texture.getFullpath() for tex in modelTextureLayers]
        #texturePainter.selectPaintModel()
        self.editTexture = editTexture
        self.editTextureFilename = tex.texture.getFullpath()
        texturePainter.enableEditor(self.modelWrapper.model, editTexture)
        texturePainter.startEdit()
      else:
        print "I: ObjectEggTexture.startEdit: texture not found", eggTextureFilename
        print "  - fullpath", [tex.texture.getFullpath() for tex in modelTextureLayers]
        print "  - filename", [tex.texture.getFilename() for tex in modelTextureLayers]
    else:
      print "W: ObjectEggTexture.startEdit: editmode not enabled"
  
  def stopEdit(self):
    if ObjectEggBase.isEditmodeEnabled(self):
      ObjectEggBase.stopEdit(self)
      texturePainter.stopEdit()
      texturePainter.disableEditor()
    else:
      print "W: ObjectEggTexture.stopEdit: editmode not enabled"
  
  def save(self):
    if self.editTexture:
      saveTex = PNMImage()
      self.editTexture.store(saveTex)
      savePath = self.editTextureFilename #posixpath.join(self.relativePath, self.tex1Path)
      print "I: ObjectEggTexture.save:", savePath
      saveTex.write(Filename(savePath))


from pandac.PandaModules import *

from core.pConfigDefs import Enum

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


EggTexture_WrapMode_Enum = Enum(
  WMUnspecified = EggTexture.WMUnspecified,
  WMClamp = EggTexture.WMClamp,
  WMRepeat = EggTexture.WMRepeat,
  WMMirror = EggTexture.WMMirror,
  WMMirrorOnce = EggTexture.WMMirrorOnce,
  WMBorderColor = EggTexture.WMBorderColor,
)

EggTexture_Mag_FilterType_Enum = Enum(
  FTUnspecified = EggTexture.FTUnspecified,
  FTNearest = EggTexture.FTNearest,
  FTLinear = EggTexture.FTLinear,
  FTNearestMipmapNearest = EggTexture.FTNearestMipmapNearest,
  FTLinearMipmapNearest = EggTexture.FTLinearMipmapNearest,
  FTNearestMipmapLinear = EggTexture.FTNearestMipmapLinear,
  FTLinearMipmapLinear = EggTexture.FTLinearMipmapLinear,
)

EggTexture_Min_FilterType_Enum = Enum(
  FTUnspecified = EggTexture.FTUnspecified,
  FTNearest = EggTexture.FTNearest,
  FTLinear = EggTexture.FTLinear,
)

EggTexture_EnvType_Enum = Enum(
  ETUnspecified = EggTexture.ETUnspecified,
  ETModulate = EggTexture.ETModulate,
  ETDecal = EggTexture.ETDecal,
  ETBlend = EggTexture.ETBlend,
  ETReplace = EggTexture.ETReplace,
  ETAdd = EggTexture.ETAdd,
  ETBlendColorScale = EggTexture.ETBlendColorScale,
  ETModulateGlow = EggTexture.ETModulateGlow,
  ETModulateGloss = EggTexture.ETModulateGloss,
  ETNormal = EggTexture.ETNormal,
  ETNormalHeight = EggTexture.ETNormalHeight,
  ETGlow = EggTexture.ETGlow,
  ETGloss = EggTexture.ETGloss,
  ETHeight = EggTexture.ETHeight,
  ETSelector = EggTexture.ETSelector,
)

EggTexture_CombineMode_Enum = Enum(
  CMUnspecified = EggTexture.CMUnspecified,
  CMReplace = EggTexture.CMReplace,
  CMModulate = EggTexture.CMModulate,
  CMAdd = EggTexture.CMAdd,
  CMAddSigned = EggTexture.CMAddSigned,
  CMInterpolate = EggTexture.CMInterpolate,
  CMSubtract = EggTexture.CMSubtract,
  CMDot3Rgb = EggTexture.CMDot3Rgb,
  CMDot3Rgba = EggTexture.CMDot3Rgba,
)


from pandac.PandaModules import *

# --- you may edit these ---

PARTICLESYSTEMWRAPPER_SHOW_PARTICLEPANEL = True

EDITOR_TOGGLE_OFF_EVENT = 'pandaEditorToggleOff'
EDITOR_TOGGLE_ON_EVENT = 'pandaEditorToggleOn'

EVENT_SCENEGRAPHBROWSER_REFRESH = 'refreshSceneGraph'

# --- not recommmended to change any of the following ---

VALID_MODEL_FORMATS = ['egg', 'bam', 'egg.pz']
VALID_SOUND_FORMATS = ['mp3', 'wav']

DEFAULT_EDITOR_COLLIDEMASK = BitMask32(0x80)

# this may have caused a crash under osx, however it is likely to be solved
DISABLE_SHADERS_WHILE_EDITING = False

# model with translation, rotation and scale arrows
# named:
# xTranslate, yTranslate, zTranslate
# xRotate, yRotate, zRotate
# xScale, yScale, zScale
# must contain: <Collide> { Polyset keep descend }
MODEL_MODIFICATION_MODEL = 'models/modificators.egg'
#                                translate  , rotate      , scale
MODEL_MODIFICATION_FUNCTIONS =  {
    'xTranslate'  : [ Vec3(.5, 0, 0), Vec3(.5, 0, 0), Vec3(0,0, 0), Vec3(0,0, 0), Vec3(0,0,0), Vec3(0,0,0) ]
  , 'yTranslate'  : [ Vec3( 0,.5, 0), Vec3( 0,.5, 0), Vec3(0,0, 0), Vec3(0,0, 0), Vec3(0,0,0), Vec3(0,0,0) ]
  , 'zTranslate'  : [ Vec3( 0, 0,.5), Vec3( 0, 0,.5), Vec3(0,0, 0), Vec3(0,0, 0), Vec3(0,0,0), Vec3(0,0,0) ]
  , 'xyTranslate' : [ Vec3( 1, 0, 0), Vec3( 0, 1, 0), Vec3(0,0, 0), Vec3(0,0, 0), Vec3(0,0,0), Vec3(0,0,0) ]
  , 'yzTranslate' : [ Vec3( 0, 1, 0), Vec3( 0, 0, 1), Vec3(0,0, 0), Vec3(0,0, 0), Vec3(0,0,0), Vec3(0,0,0) ]
  , 'xzTranslate' : [ Vec3( 1, 0, 0), Vec3( 0, 0, 1), Vec3(0,0, 0), Vec3(0,0, 0), Vec3(0,0,0), Vec3(0,0,0) ]
  , 'xRotate'     : [ Vec3( 0, 0, 0), Vec3( 0, 0, 0), Vec3(0,1, 0), Vec3(0,1, 0), Vec3(0,0,0), Vec3(0,0,0) ]
  , 'yRotate'     : [ Vec3( 0, 0, 0), Vec3( 0, 0, 0), Vec3(0,0,-1), Vec3(0,0,-1), Vec3(0,0,0), Vec3(0,0,0) ]
  , 'zRotate'     : [ Vec3( 0, 0, 0), Vec3( 0, 0, 0), Vec3(1,0, 0), Vec3(1,0, 0), Vec3(0,0,0), Vec3(0,0,0) ]
  , 'xScale'      : [ Vec3( 0, 0, 0), Vec3( 0, 0, 0), Vec3(0,0, 0), Vec3(0,0, 0), Vec3(1,0,0), Vec3(1,0,0) ]
  , 'yScale'      : [ Vec3( 0, 0, 0), Vec3( 0, 0, 0), Vec3(0,0, 0), Vec3(0,0, 0), Vec3(0,1,0), Vec3(0,1,0) ]
  , 'zScale'      : [ Vec3( 0, 0, 0), Vec3( 0, 0, 0), Vec3(0,0, 0), Vec3(0,0, 0), Vec3(0,0,1), Vec3(0,0,1) ]
  , 'uniScale'    : [ Vec3( 0, 0, 0), Vec3( 0, 0, 0), Vec3(0,0, 0), Vec3(0,0, 0), Vec3(1,1,1), Vec3(1,1,1) ] }
MODEL_MODIFICATION_TRANSLATE = ['xTranslate','yTranslate','zTranslate','xyTranslate','yzTranslate','xzTranslate']
MODEL_MODIFICATION_ROTATE    = ['xRotate','yRotate','zRotate']
MODEL_MODIFICATION_SCALE     = ['xScale','yScale','zScale','uniScale']
MODEL_MODIFICATION_MODES_FUNCTIONS = [MODEL_MODIFICATION_TRANSLATE, MODEL_MODIFICATION_ROTATE, MODEL_MODIFICATION_SCALE]
MODEL_MODIFICATION_MODE_TRANSLATE_LOCAL = 0
MODEL_MODIFICATION_MODE_ROTATE_LOCAL = 2
MODEL_MODIFICATION_MODE_SCALE_LOCAL = 4
MODEL_MODIFICATION_MODE_TRANSLATE_GLOBAL = 1
MODEL_MODIFICATION_MODE_ROTATE_GLOBAL = 3
MODEL_MODIFICATION_MODE_SCALE_GLOBAL = 5
MODEL_MODIFICATION_MODES =  [ MODEL_MODIFICATION_MODE_TRANSLATE_LOCAL
                            , MODEL_MODIFICATION_MODE_TRANSLATE_GLOBAL
                            , MODEL_MODIFICATION_MODE_ROTATE_LOCAL
                            , MODEL_MODIFICATION_MODE_ROTATE_GLOBAL
                            , MODEL_MODIFICATION_MODE_SCALE_LOCAL
                            , MODEL_MODIFICATION_MODE_SCALE_GLOBAL ]

# some tag's that are used in the engine
# a object that can be edited requires to have this tag
EDITABLE_OBJECT_TAG = 'editorObject'
# tag assigned to the arrows for moving/rotating/scaling a object
MODEL_MODIFICATOR_TAG = 'modelController'
# to suppress the model from showing up in the scenegraphBrowser
EXCLUDE_SCENEGRAPHBROWSER_MODEL_TAG = 'editorExcludedObject'
ENABLE_SCENEGRAPHBROWSER_MODEL_TAG = 'editorEnabledObject'

# model shown when the real model is not found
MODEL_NOT_FOUND_MODEL = 'models/modelnotfound.egg'

# tag set to the object which defines the type of wrapper used to edit
MODEL_WRAPPER_TYPE_TAG = 'modelWrapperTypeTag'

PARTICLE_WRAPPER_DUMMYOBJECT = 'models/sphere.egg.pz'
SPOTLIGHT_WRAPPER_DUMMYOBJECT = 'models/Spotlight.egg.pz'

CAMERACONTROLLER_PIVOT_MODEL = 'models/sphere.egg'

MODELCONTROLLER_AXISCUBE_MODEL = 'models/axisCube.bam'


from pandac.PandaModules import *

# --- you may edit these ---

#EDITOR_TOGGLE_OFF_EVENT = 'pandaEditorToggleOff'
#EDITOR_TOGGLE_ON_EVENT = 'pandaEditorToggleOn'

EDITOR_MODE_DISABLED = 'pandaEditorDisabledMode'
EDITOR_MODE_WORLD_EDIT = 'pandaEditorWorldEditMode'
EDITOR_MODE_OBJECT_EDIT = 'pandaEditorObjectEditMode'

EVENT_SCENEGRAPHBROWSER_REFRESH = 'refreshSceneGraph'
# this event is sent when a object has been selected
# (extraArgs contains module class object)
EVENT_MODELCONTROLLER_SELECT_MODEL_CHANGE = 'modelEdit-selectModel-change'
EVENT_MODELCONTROLLER_SELECT_MODEL_AGAIN = 'modelEdit-selectModel-again'
# this event is sent when a object has been modified (only sent rarely)
EVENT_MODELCONTROLLER_FULL_REFRESH = 'refreshModelEdit-full'
# this event is sent when a object has been modified (can be sent every frame)
EVENT_MODELCONTROLLER_FAST_REFRESH = 'refreshModelEdit-fast'
# this event is invoked when you have multiple windows and the focus switches from one to the other.
EVENT_WINDOW_FOCUS_CHANGE = 'active-window-changed'

EVENT_MODELCONTROLLER_EDITTOOL_SELECTED = 'modelController-edittool-selected'
EVENT_MODELCONTROLLER_EDITTOOL_DESELECTED = 'modelController-edittool-deselected'
# --- not recommmended to change any of the following ---

VALID_MODEL_FORMATS = ['egg', 'bam', 'egg.pz']
VALID_SOUND_FORMATS = ['mp3', 'wav']

DEFAULT_EDITOR_COLLIDEMASK = BitMask32(0x80)

# model with translation, rotation and scale arrows
# named:
# xTranslate, yTranslate, zTranslate
# xRotate, yRotate, zRotate
# xScale, yScale, zScale
# must contain: <Collide> { Polyset keep descend }
MODEL_MODIFICATION_MODEL = 'models/misc/modificators.egg'
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
ENABLE_SCENEGRAPHBROWSER_MODEL_TAG = 'editorEnabledObject'

# tag set to the object, which defines the type of wrapper used to edit
MODEL_WRAPPER_TYPE_TAG = 'modelWrapperTypeTag'

# model shown when the real model is not found
MODEL_NOT_FOUND_MODEL = 'models/nodes/ModelNotFound.egg.pz'
SOUND_NOT_FOUND_SOUND = 'soundnotfound.mp3'
SOUNDNODE_WRAPPER_DUMMYOBJECT = 'models/nodes/SoundNode.egg.pz'
PARTICLE_WRAPPER_DUMMYOBJECT = 'models/nodes/PartcielSystem.egg.pz'
CODE_WRAPPER_DUMMYOBJECT = 'models/nodes/CodeNode.egg.pz'
# light nodes, visual objects
SPOTLIGHT_WRAPPER_DUMMYOBJECT = 'models/nodes/Spotlight.egg.pz'
DIRECTIONALLIGHT_WRAPPER_DUMMYOBJECT = 'models/nodes/Dirlight.egg.pz'
POINTLIGHT_WRAPPER_DUMMYOBJECT = 'models/nodes/Pointlight.egg.pz'
AMBIENTLIGHT_WRAPPER_DUMMYOBJECT = 'models/nodes/AmbientLight.egg.pz'

# helper models for the scene
CAMERACONTROLLER_PIVOT_MODEL = 'models/misc/sphere.egg'
MODELCONTROLLER_AXISCUBE_MODEL = 'models/misc/axisCube.bam'


MOUSE_ROTATION_SPEED = 25.0
MOUSE_MOVEMENT_SPEED = 25.0
# camera distance parameters
MOUSE_ZOOM_SPEED = 10.0
STARTUP_CAMERA_DISTANCE = 100
STARTUP_CAMERA_HPR = Vec3( 30,-30,0 )
MIN_CAMERA_DISTANCE = 10
MAX_CAMERA_DISTANCE = 1000


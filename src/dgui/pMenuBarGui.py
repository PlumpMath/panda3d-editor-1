from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectGui import *
from direct.gui.DirectCheckBox import DirectCheckBox
from direct.gui.DirectScrolledList import DirectScrolledList

from core.pModelController import modelController
from core.pConfigDefs import *
from core.modules import *

from dgui.filebrowser import FG
from dgui.directWindow.src.directWindow import DirectWindow
from dgui.directSidebar import *
from dgui.pConfigDefs import *

class MenuBarGui(DirectObject):
  def __init__(self, guiEditorInstance):
    self.guiEditorInstance = guiEditorInstance
    self.shaderAuto = False
    self.nodeButtons = None
    self.lightButtons = None
    self.editButtons = None
  
  def enable(self):
    sceneButtonDefinitions = [
      ['new', self.createNewScene, []],
      ['load', self.loadEggModelsFile, []],
    ]
    self.sceneButtons = self.createInterface(sceneButtonDefinitions, 'scene', align=ALIGN_LEFT|ALIGN_TOP, pos=Vec3(0.05,0,0))
    
    settingsButtonDefinitions = [
      ['pix-light', self.toggleShaderAuto, []],
    ]
    self.settingsButtons = self.createInterface(settingsButtonDefinitions, 'settings', align=ALIGN_LEFT|ALIGN_TOP, pos=Vec3(0.45,0,0))
    
    #self.accept(EVENT_MODELCONTROLLER_SELECTED_OBJECT_CHANGE, self.createObjectEditor)
    #self.create()
  
  def disable(self):
    self.sceneButtons.destroy()
    self.sceneButtons.detachNode()
    self.settingsButtons.destroy()
    self.settingsButtons.detachNode()
    
    self.ignore(EVENT_MODELCONTROLLER_SELECTED_OBJECT_CHANGE)
    #self.destroy()
  
  def create(self):
    selectedObject = modelController.getSelectedObject()
    possibleChildren = selectedObject.getPossibleChildren()
    possibleFunctions = selectedObject.getPossibleFunctions()
    
    nodeButtonDefinitions = list()
    if 'NodePathWrapper' in possibleChildren:
      nodeButtonDefinitions.append( ['model', self.createFilebrowserModelWrapper, ['NodePathWrapper']] )
    if 'ParticleSystemWrapper' in possibleChildren:
      nodeButtonDefinitions.append( ['particlesystem', self.createFilebrowserModelWrapper, ['ParticleSystemWrapper']] )
    if 'CodeNodeWrapper' in possibleChildren:
      nodeButtonDefinitions.append( ['codeNode', self.createFilebrowserModelWrapper, ['CodeNodeWrapper']] )
    if 'GeoMipTerrainNodeWrapper' in possibleChildren:
      nodeButtonDefinitions.append( ['GeoMipTerrain', self.createFilebrowserModelWrapper, ['GeoMipTerrainNodeWrapper']] )
    if 'SoundNodeWrapper' in possibleChildren:
      nodeButtonDefinitions.append( ['sound', self.createFilebrowserModelWrapper, ['SoundNodeWrapper']] )
    if 'SceneNodeWrapper' in possibleChildren:
      nodeButtonDefinitions.append( ['scene', self.createFilebrowserModelWrapper, ['SceneNodeWrapper']] )
    if 'ShaderWrapper' in possibleChildren:
      nodeButtonDefinitions.append( ['paintshader', self.createModelWrapper, ['ShaderWrapper']] )
    if 'CurveNodeWrapper' in possibleChildren:
      nodeButtonDefinitions.append( ['curve', self.createModelWrapper, ['CurveNodeWrapper']] )
    if 'CurveSurfaceNodeWrapper' in possibleChildren:
      nodeButtonDefinitions.append( ['surfaceCurve', self.createModelWrapper, ['CurveSurfaceNodeWrapper']] )
    self.nodeButtons = self.createInterface(nodeButtonDefinitions, 'nodes', align=ALIGN_RIGHT|ALIGN_TOP, pos=Vec3(-.85,0,0))
    
    lightButtonDefinitions = list()
    if 'SpotLightNodeWrapper' in possibleChildren:
      lightButtonDefinitions.append( ['spotlight', self.createModelWrapper, ['SpotLightNodeWrapper']] )
    if 'DirectionalLightNodeWrapper' in possibleChildren:
      lightButtonDefinitions.append( ['directionallight', self.createModelWrapper, ['DirectionalLightNodeWrapper']] )
    if 'AmbientLightNodeWrapper' in possibleChildren:
      lightButtonDefinitions.append( ['ambientlight', self.createModelWrapper, ['AmbientLightNodeWrapper']] )
    if 'PointLightNodeWrapper' in possibleChildren:
      lightButtonDefinitions.append( ['pointlight', self.createModelWrapper, ['PointLightNodeWrapper']] )
    self.lightButtons = self.createInterface(lightButtonDefinitions, 'lights', align=ALIGN_RIGHT|ALIGN_TOP, pos=Vec3(-.45,0,0))
    
    editButtonDefinitions = list()
    if 'destroy' in possibleFunctions:
      editButtonDefinitions.append( ['destroy', self.guiEditorInstance.editorInstance.destroyModel, []] )
    if 'duplicate' in possibleFunctions:
      editButtonDefinitions.append( ['duplicate', self.duplicateModelWrapper, []] )
    if 'save' in possibleFunctions:
      editButtonDefinitions.append( ['save', selectedObject.save, []] )
    if 'saveAs' in possibleFunctions:
      editButtonDefinitions.append( ['saveAs', self.saveAsFile, [selectedObject]] )
    self.editButtons = self.createInterface(editButtonDefinitions, 'edit'+selectedObject.className, align=ALIGN_RIGHT|ALIGN_TOP, pos=Vec3(-.05,0,0))
  
  def update(self):
    self.destroy()
    self.create()
  
  def destroy(self):
    if self.nodeButtons:
      self.nodeButtons.destroy()
      self.nodeButtons.detachNode()
    if self.lightButtons:
      self.lightButtons.destroy()
      self.lightButtons.detachNode()
    if self.editButtons:
      self.editButtons.destroy()
      self.editButtons.detachNode()
  
  def toggleShaderAuto(self, state=None):
    if state is None:
      state = not self.shaderAuto
    self.shaderAuto = state
    if self.shaderAuto:
      render.setShaderAuto()
    else:
      render.setShaderOff()
  
  def duplicateModelWrapper(self):
    originalModel = modelController.getSelectedObject()
    objectInstance = originalModel.makeInstance(originalModel)
    if objectInstance is not None:
      objectInstance.setEditmodeEnabled([])
    #objectInstance.loadFromData( originalModel.getSaveData('.') )
    messenger.send( EVENT_SCENEGRAPH_REFRESH )
    modelController.selectObject( objectInstance )
  
  def saveAsFile(self, object):
    FG.openFileBrowser()
    FG.accept('selectionMade', self.saveAsFileCallback, [object])
  def saveAsFileCallback(self, object, filepath):
    if filepath != None and filepath != '' and filepath != ' ':
      filepath = Filename.fromOsSpecific(filepath).getFullpath()
      object.saveAs(filepath)
  
  def loadEggModelsFile(self):
    FG.openFileBrowser()
    FG.accept('selectionMade', self.loadEggModelsFileCallback)
  def loadEggModelsFileCallback(self, filepath):
    if filepath != None and filepath != '' and filepath != ' ':
      filepath = Filename.fromOsSpecific(filepath).getFullpath()
      self.guiEditorInstance.editorInstance.loadEggModelsFile(filepath)
  
  def createObjectEditor(self, object):
    if object == self.editorObject:
      # same object is selected again
      pass
    else:
      if self.editorObject is not None:
        # destroy the current editorObject
        pass
  
  def createNewScene(self):
    FG.openFileBrowser()
    FG.accept('selectionMade', self.createNewSceneCallback)
  def createNewSceneCallback(self, filepath):
    if filepath != None and filepath != '' and filepath != ' ':
      self.guiEditorInstance.editorInstance.newScene(filepath)
  
  def createFilebrowserModelWrapper(self, objectType):
    # open the file browser to select a object
    FG.openFileBrowser()
    FG.accept('selectionMade', self.onCreateFilebrowserModelWrapper, [objectType])
  def onCreateFilebrowserModelWrapper(self, objectType, filepath):
    if filepath != None and filepath != '' and filepath != ' ':
      filepath = Filename.fromOsSpecific(filepath).getFullpath()
      modelParent = modelController.getSelectedObject()
      module = __import__("core.modules.p%s" % objectType, globals(), locals(), [objectType], -1)
      objectInstance = getattr(module, objectType).onCreateInstance(modelParent, filepath)
      if objectInstance is not None:
        objectInstance.setEditmodeEnabled()
      messenger.send(EVENT_SCENEGRAPH_REFRESH)
      modelController.selectObject(objectInstance)
  
  def createModelWrapper(self, type):
    # create the actual wrapper of the object
    module = __import__("core.modules.p%s" % type, globals(), locals(), [type], -1)
    modelParent = modelController.getSelectedObject()
    objectInstance = getattr(module, type).onCreateInstance(modelParent)
    if objectInstance is not None:
      objectInstance.setEditmodeEnabled()
    messenger.send(EVENT_SCENEGRAPH_REFRESH)
    modelController.selectObject(objectInstance)
  
  def createInterface( self, buttonDefinitions, title, align, pos ):
    buttons = list()
    for name, functionCall, extraArgs in buttonDefinitions:
      button = DirectButton(text = (name, name, name, name),
                      text_scale=0.1, borderWidth = (0.01, 0.01),
                      relief=2,
                      command=functionCall,
                      extraArgs=extraArgs,
                      frameSize=(-0.3,0.3,-.02,.08))
      buttons.append( button )
    itemHeight = 0.11
    
    height = 0.03+(itemHeight - 0.055) * len(buttonDefinitions)
    buttonsWindow  = DirectSidebar(
        frameSize=(0.35, height),
        pos=pos,
        align=align,
        text=title,
        frameColor=(0,0,0,.8),
      )
    
    myScrolledList = DirectScrolledList(
        pos = Vec3(.175, 0, height-0.05 ),
        items = buttons,
        scale = 0.5,
        parent = buttonsWindow,
        numItemsVisible = len(buttons),
        forceHeight = itemHeight,
        incButton_scale = (0, 0, 0),
        decButton_scale = (0, 0, 0),
        )
    
    return buttonsWindow

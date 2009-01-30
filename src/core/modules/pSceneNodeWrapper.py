import traceback, posixpath

from core.modules.pVirtualNodeWrapper import VirtualNodeWrapper
from core.pConfigDefs import *
from core.modules.pBaseWrapper import *
from core.modules.pShaderWrapper import *
#from core.modules import POSSIBLE_SCENE_CHILDRENS

DEBUG = False


# model nodes
'''from pNodePathWrapper import *
from pGeoMipTerrainNodeWrapper import *

# light nodes
from pAmbientLightNodeWrapper import *
from pDirectionalLightNodeWrapper import *
from pPointLightNodeWrapper import *
from pSpotLightNodeWrapper import *

# virtual nodes
from pCodeNodeWrapper import *
from pParticleSystemWrapper import *
from pSoundNodeWrapper import *
#from pSceneNodeWrapper import *

from pShaderWrapper import *'''

class SceneNodeWrapper(VirtualNodeWrapper):
  ''' this node contains a scene (so that a scene may contain other scenes)
  PROBLEM's:
  modelIdManager should be part of this node
  -> modelIdManager must be given to object when loading (not a global class)
  objects loaded from this scene should not be mutable, when loaded as subscene
  objects loaded from this scene should be mutable, when loaded as parent scene
  '''
  className = 'Scene'
  def onCreateInstance(self, parent, filepath):
    # create instance of this class
    objectInstance = super(SceneNodeWrapper, self).onCreateInstance(parent, 'SceneNode')
    #print "I: SceneNodeWrapper.onCreateInstance:", filepath
    objectInstance.setScene(filepath)
    return objectInstance
  onCreateInstance = classmethod(onCreateInstance)
  
  def __init__(self, parent, name='SceneNode'):
    self.objectInstance = None
    VirtualNodeWrapper.__init__(self, parent, name, SCENE_WRAPPER_DUMMYOBJECT)
    self.possibleChildren = [
        'NodePathWrapper',
        'GeoMipTerrainNodeWrapper',
        'AmbientLightNodeWrapper',
        'DirectionalLightNodeWrapper',
        'SpotLightNodeWrapper',
        'CodeNodeWrapper',
        'ParticleSystemWrapper',
        'PointLightNodeWrapper',
        'SoundNodeWrapper',
        'SceneNodeWrapper',
        'ShaderWrapper',
        'CurveNodeWrapper',
        'CurveSurfaceNodeWrapper'
      ]
    self.possibleFunctions = [
        'saveAs',
        'save',
        'destroy',
        'duplicate',
      ]
  
  def setScene(self, relativePath):
    # load the scene
    
    def loadRecursiveChildrens(eggParentData, parent, transform, filepath, loadedObjects):
      if type(eggParentData) == EggData:
        # search the childrens
        for childData in eggParentData.getChildren():
          # search the children
          parent, loadedObjects = loadRecursiveChildrens(childData, parent, transform, filepath, loadedObjects)
      
      elif type(eggParentData) == EggGroup:
        
        # a eggGroup modifies the matrix of the model
        if type(eggParentData) == EggGroup:
          # convert the matrix from double to single
          mat4d = eggParentData.getTransform3d()
          mat4 = Mat4()
          for x in xrange(4):
              for y in xrange(4):
                  mat4.setCell(x, y, mat4d.getCell(x,y))
          # multiply the matrix for later applial onto model
          transform = mat4 * transform
        
        if eggParentData.hasTag(MODEL_WRAPPER_TYPE_TAG):
          # if the eggData contains a tag that specifies the type of the object
          wrapperType = eggParentData.getTag(MODEL_WRAPPER_TYPE_TAG)
          wrapperTypeDecap = wrapperType[0].lower() + wrapperType[1:]
          try:
            # import the module responsible for handling the data
            module = __import__('core.modules.p%s' % wrapperType, globals(), locals(), [wrapperType], -1)
            # load the eggParentData using the module
            #print "I: EditorClass.loadEggModelsFile: parent", wrapperType, parent 
            object = getattr(module, wrapperType).loadFromEggGroup(eggParentData, parent, filepath)
            # append loaded object to list
            loadedObjects.append([object, eggParentData])
          except:
            print "W: EditorClass.loadEggModelsFile: unknown or invalid entry"
            traceback.print_exc()
            print "W: --- start of invalid data ---"
            print eggParentData
            print "W: --- end of invalid data ---"
            #object = parent.attachNewNode('%s-failed' % wrapperType)
            object = None
          
          if object is not None:
            if object.hasNodepath():
              # apply the transformation on the object
              object.getNodepath().setMat(transform)
              transform = Mat4.identMat()
            # if it contains additional childrens recurse into them
            for childData in eggParentData.getChildren()[1:]:
              # search the children
              loadRecursiveChildrens(childData, object, transform, filepath, loadedObjects)
          else:
            print "E: core.EditorClass.loadEggModelsFile: no object returned (most likely error in module)"
            print "  -", wrapperType
        else:
          # search for childrens
          for childData in eggParentData.getChildren():
            # search the children
            parent, loadedObjects = loadRecursiveChildrens(childData, parent, transform, filepath, loadedObjects)
      else:
        if DEBUG:
          print "W: EditorApp.loadEggModelsFile.loadRecursiveChildrens:"
          print "   - skipping unkown eggData", type(eggParentData)
      
      return parent, loadedObjects
    
    if relativePath != None and relativePath != '' and relativePath != ' ':
      p3filename = Filename.fromOsSpecific(relativePath)
      p3filename.makeAbsolute()
      # destroy old models
      #self.destroyAllModels()
      
      eggData = EggData()
      eggData.read(p3filename)
      
      # the absolute path of the file we load, referenced files are relative
      # to this path
      filepath = p3filename.getDirname()
      
      # store the full filepath of the model
      self.setFilepath(p3filename)
      # add the path to the model-path
      from pandac.PandaModules import getModelPath
      getModelPath().appendPath(filepath)
      # read the eggData
      parent, loadedObjects = loadRecursiveChildrens(eggData, self, Mat4.identMat(), filepath, list())
      
      for objectInstance, eggData in loadedObjects:
        objectInstance.loadFromData(eggData, filepath)
      
      # refresh the scenegraphbrowser
      messenger.send(EVENT_SCENEGRAPH_REFRESH)
    
    # relative path to editor / or parent scene
    self.relativePath = relativePath # examples/sample.egs
    # absolute path of the file (different on every computer)
    self.fullPath = posixpath.abspath(relativePath) # /home/user/editor/example/samples.egs
    # folder where the file is at
    self.dirname = posixpath.dirname(self.fullPath) # /home/user/editor/example/
    print "I: SceneNodeWrapper.setScene: loaded"
    print "  - relativePath", self.relativePath
    print "  - fullPath", self.fullPath
    print "  - relativePath", self.relativePath
  
    #print "I: pSceneNodeWrapper.setScene:"
    #print "  -", relativePath
    #print "  -", posixpath.abspath(relativePath)
    #print "  -", posixpath.dirname(posixpath.abspath(relativePath))
  
  def save(self):
    print "I: SceneNodeWrapper.save: using path", self.fullPath
    self.saveAs(self.fullPath)
  
  def saveAs(self, filepath):
    def saveRecursiveChildrens(parent, eggParentData, relativeTo):
      for child in parent.getChildren():
        # save the childs data
        hasNodePath = BaseWrapper in child.__class__.__mro__ or type(child) == ShaderWrapper
        #print "saveRecursiveChildrens", type(child)
        isSceneNode = type(child) == SceneNodeWrapper
        if hasNodePath:
          # editModeEnabled is only true for SceneNodeWrappers, which have not
          # been referenced (it's the root node). thus the childrens data
          # should not be included if False
          modelData = child.getSaveData(relativeTo)
          # XXX TODO, this must be done again, we may save stuff that is not
          # supposed to be saved
          if modelData is not None:
            eggParentData.addChild(modelData)
            # if there is data of the model walk the childrens
            if modelData:
              # but not if it's a sceneNode
              # (this would save the scene twice, once as linked scene and
              # once the models within the scene referenced)
              if not isSceneNode:
                # search childrens
                saveRecursiveChildrens(child, modelData, relativeTo)
          else:
            print "I: SceneNodeWrapper.saveAs.saveRecursiveChildrens: got NodeData"
    
    # create a eggData to save the data
    eggData = EggData()
    eggData.setCoordinateSystem(1)
    # start reading the childrens of render
    relativeTo = Filename(filepath).getDirname()
    relativeTo = str(Filename.fromOsSpecific(relativeTo))
    saveRecursiveChildrens(self, eggData, relativeTo)
    # save the egg file
    eggData.writeEgg(Filename(filepath))
  
  def setEditmodeEnabled(self):
    VirtualNodeWrapper.setEditmodeEnabled(self)
  
  def setEditmodeDisabled(self):
    VirtualNodeWrapper.setEditmodeDisabled(self)
  
  def destroy(self, recursive=True):
    # destroy the scene
    #if recursive:
    def recurse(parent):
      for child in parent.getChildren()[:]: # accessing it directly causes it to miss childrens
        recurse(child)
        child.destroy()
    recurse(self)
    
    VirtualNodeWrapper.destroy(self)
  
  def getSaveData(self, relativeTo):
    objectInstance = VirtualNodeWrapper.getSaveData(self, relativeTo)
    self.setExternalReference(self.relativePath, relativeTo, objectInstance)
    return objectInstance
  
  def loadFromData(self, eggGroup, filepath):
    extRefFilename = self.getExternalReference(eggGroup, filepath)
    self.setScene(extRefFilename)
    VirtualNodeWrapper.loadFromData(self, eggGroup, filepath)
  
  def makeInstance(self, original):
    ''' make a instance of this node somewhere else '''
    objectInstance = super(SceneNodeWrapper, self).makeInstance(original)
    objectInstance.setScene(original.relativePath)
    return objectInstance
  makeInstance = classmethod(makeInstance)

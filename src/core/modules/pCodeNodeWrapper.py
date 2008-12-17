import posixpath, imp, traceback

from core.modules.pVirtualNodeWrapper import VirtualNodeWrapper
from core.pModelController import modelController
from core.pCommonPath import *
from core.pConfigDefs import *

DEBUG = False

class CodeNodeWrapper(VirtualNodeWrapper):
  def onCreateInstance(self, parent, filepath):
    # create instance of this class
    name='CodeNode'
    objectInstance = super(CodeNodeWrapper, self).onCreateInstance(parent, name)
    objectInstance.setScript(filepath)
    return objectInstance
  onCreateInstance = classmethod(onCreateInstance)
  
  def __init__(self, parent, name='CodeNode'):
    self.objectInstance = None
    #name = filepath.split('/')[-1]
    VirtualNodeWrapper.__init__(self, parent, name, CODE_WRAPPER_DUMMYOBJECT) 
  
  def setScript(self, filepath):
    if filepath != ' ':
      if self.objectInstance is not None:
        self.objectInstance.destroy()
        del self.objectInstance
        self.objectInstance = None
      
      filename=os.path.basename(filepath)
      dirname=os.path.dirname(filepath)
      filebase, fileext = os.path.splitext(filename)
      print "I: CodeNodeWrapper.setScript:"
      print "  - filebase:", filebase
      dirname = Filename(dirname).toOsSpecific()
      print "  - dirname:", dirname
      if fileext == '.py':
        try:
          fp, filename, description=imp.find_module(filebase, [dirname])
          module = imp.load_module(filebase, fp, filename, description)
          objectClass = getattr(module, filebase[0].upper()+filebase[1:])
          objectInstance = objectClass(self)
          self.objectInstance = objectInstance
        except:
          print "W: CodeNodeWrapper.setScript: error creating code instance"
          traceback.print_exc()
      self.scriptFilepath = filepath
  
  def destroy(self):
    VirtualNodeWrapper.destroy(self)
    if self.objectInstance is not None:
      self.objectInstance.destroy()
      del self.objectInstance
      self.objectInstance = None
  
  def getSaveData(self, relativeTo):
    ''' link the egg-file into the egg we save
    '''
    name = self.getName()
    instance = VirtualNodeWrapper.getSaveData(self, relativeTo)
    className = 'CodeNodeWrapper' #self.__class__.__name__ -> yields the wrong classname
    #instance.setTag( MODEL_WRAPPER_TYPE_TAG, className )
    # convert to a relative path
    scriptFilepath = relpath( relativeTo, posixpath.abspath(self.scriptFilepath) )
    #print "I: CodeNodeWrapper.getSaveData: scriptFilepath:", scriptFilepath, self.scriptFilepath, relativeTo
    # add the reference to the egg-file
    ext = EggExternalReference( className+"-EggExternalReference", scriptFilepath )
    instance.addChild(ext)
    return instance
  
  def loadFromData(self, eggGroup, filepath):
    # search for a external reference
    eggExternalReference = None
    for child in eggGroup.getChildren():
      if type(child) == EggExternalReference:
        eggExternalReference = child
    # read the reference if it is found
    if eggExternalReference is not None:
      referencedFilename = eggExternalReference.getFilename()
      filename = posixpath.join(filepath,str(referencedFilename))
      self.setScript(filename)
    else:
      print "I: NodePathWrapper.loadFromData: no externalReference found in"
      print "  -",eggGroup
    VirtualNodeWrapper.loadFromData(self, eggGroup, filepath)

import imp, os

from core.modules.pVirtualNodeWrapper import VirtualNodeWrapper
from core.pModelController import modelController
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
      dirname = Filename(dirname).toOsSpecific()
      if DEBUG:
        print "I: CodeNodeWrapper.setScript:"
        print "  - filebase:", filebase
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
    objectInstance = VirtualNodeWrapper.getSaveData(self, relativeTo)
    self.setExternalReference(self.scriptFilepath, relativeTo, objectInstance)
    return objectInstance
  
  def loadFromData(self, eggGroup, filepath):
    extRefFilename = self.getExternalReference(eggGroup, filepath)
    self.setScript(extRefFilename)
    VirtualNodeWrapper.loadFromData(self, eggGroup, filepath)
  
  def makeCopy(self, original):
    objectInstance = super(CodeNodeWrapper, self).makeCopy(original)
    objectInstance.setScript(original.scriptFilepath)
    return objectInstance
  makeCopy = classmethod(makeCopy)

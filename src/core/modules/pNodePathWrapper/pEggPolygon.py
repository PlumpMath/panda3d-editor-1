from pandac.PandaModules import *

class ObjectEggPolygon:
  def __init__(self, eggPolygon, modelWrapper):
    self.eggPolygon = eggPolygon
    self.modelWrapper = modelWrapper
    self.mutableParameters = dict()
    
    # testing
    print "I: ObjectEggPolygon: textures"
    print self.eggPolygon.getNumTextures()
    for i in xrange(eggPolygon.getNumTextures()):
      print eggPolygon.getTexture(i)
    print dir(eggPolygon)
    if self.eggPolygon.getNumTextures() > 2:
      tex0 = self.eggPolygon.getTexture(0)
      tex1 = self.eggPolygon.getTexture(1)
      self.eggPolygon.clearTexture()
      print self.eggPolygon.getNumTextures()
      self.eggPolygon.addTexture(tex0)
      self.eggPolygon.addTexture(tex1)
      print self.eggPolygon.getNumTextures()
      print self.eggPolygon.getTexture(0)
      print self.eggPolygon.getTexture(1)
  
  def destroy(self):
    self.eggPolygon = None
    self.modelWrapper = None
  
  def setParameters(self, parameters):
    pass
  
  def getParameters(self):
    parameters = dict()
    return parameters
  

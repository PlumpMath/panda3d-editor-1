from pandac.PandaModules import *

from core.modules.pNodePathWrapper.pEggBase import *

class ObjectEggPolygon(ObjectEggBase):
  def __init__(self, parent, modelWrapper, eggPolygon):
    ObjectEggBase.__init__(self, parent, modelWrapper, 'EggPolygon')
    self.eggPolygon = eggPolygon
    
    # testing
    #print "I: ObjectEggPolygon.__init__: textures"
    #print self.eggPolygon.getNumTextures()
    #for i in xrange(eggPolygon.getNumTextures()):
    #  print eggPolygon.getTexture(i)
    #print dir(eggPolygon)
    '''if self.eggPolygon.getNumTextures() > 2:
      tex0 = self.eggPolygon.getTexture(0)
      tex1 = self.eggPolygon.getTexture(1)
      self.eggPolygon.clearTexture()
      print self.eggPolygon.getNumTextures()
      self.eggPolygon.addTexture(tex0)
      self.eggPolygon.addTexture(tex1)
      print self.eggPolygon.getNumTextures()
      print self.eggPolygon.getTexture(0)
      print self.eggPolygon.getTexture(1)'''
  
  def destroy(self):
    ObjectEggBase.destroy(self)
    self.eggPolygon = None
    self.modelWrapper = None

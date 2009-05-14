# ------------------------------------------------------------------------------
# Copyright (c) 2009, Reto Spoerri
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name of the <ORGANIZATION> nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.
# ------------------------------------------------------------------------------

from pandac.PandaModules import *

from core.modules.pNodePathWrapper.pObjectEggBase import *

class ObjectEggPolygon(ObjectEggBase):
  className = 'EggPolygon'
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

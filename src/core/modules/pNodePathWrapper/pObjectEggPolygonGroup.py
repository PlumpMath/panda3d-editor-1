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

from core.pTreeNode import *

class ObjectEggPolygonGroup(TreeNode):
  # a virtual class, which groups together polygons with the same texture
  # it is used so new textures can be added to a egg
  className = 'EggPolygonGroup'
  def __init__(self, parent, name):
    TreeNode.__init__(self, name)
    TreeNode.reparentTo(self, parent)
    self.polygons = list()
  
  def setPolygons(self, polygons):
    self.polygons = polygons
  
  def addTexture(self, texture):
    for polygon in self.polygons:
      oldTextures = list()
      for i in xrange(polygon.getNumTextures()):
        oldTextures.append(polygon.getTexture(i))
      
      if not texture in oldTextures:
        oldTextures.append(texture)
      
      polygon.clearTexture()
      for tex in oldTextures:
        polygon.addTexture(tex)
  
  def removeTexture(self, texture):
    for polygon in self.polygons:
      oldTextures = list()
      for i in xrange(polygon.getNumTextures()):
        oldTextures.append(polygon.getTexture(i))
      
      if texture in oldTextures:
        oldTextures.remove(texture)
      
      polygon.clearTexture()
      for tex in oldTextures:
        polygon.addTexture(tex)
  
  def destroy(self):
    ObjectEggBase.destroy(self)

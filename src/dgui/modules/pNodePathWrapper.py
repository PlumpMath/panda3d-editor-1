import os

from core.modules.pBaseWrapper import *
from core.pModelController import modelController
from core.pCommonPath import *

class NodePathWrapper( BaseWrapper ):
  def startEdit( self ):
    # the object is selected to be edited
    # creates a directFrame to edit this object
    self.model.showBounds()
    BaseWrapper.startEdit( self )
  def stopEdit( self ):
    # the object is deselected from being edited
    self.model.hideBounds()
    BaseWrapper.stopEdit( self )

if __name__ == '__main__':
  print "testing notdePathWrapper"
  a = NodePathWrapper.onCreate( 'test2' )
  print a.baseName, a.nodeName
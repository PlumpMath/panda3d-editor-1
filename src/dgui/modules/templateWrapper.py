
class NodePathWrapper:
  def __init__( self, params ):
    print "NodePathWrapper", params
    self.name = params
  def onCreate( self, params ):
    # open a file dialog
    # create a instance of NodePathWrapper
    print "NodePathWrapper.onCreate", self, params
    return NodePathWrapper(params)
  onCreate = classmethod(onCreate)
  def enableEdit( self ):
    # enables the edit methods of this object
    pass
  def disableEdit( self ):
    # disables the edit methods of this object
    # -> performance increase
    pass
  def getSaveData( self ):
    # returns a eggGroup containing the data of this object
    pass
  def getEditFrame( self ):
    # returns a directFrame containing the buttons to edit the parameters of
    # this object
    pass

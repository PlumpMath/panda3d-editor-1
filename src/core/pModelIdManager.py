class ModelIdManager:
  def __init__( self ):
    self.modelId = 0
    self.modelIdDict = dict()
  
  def getId( self ):
    # get next free modelId
    self.modelId += 1
    while self.modelId in self.modelIdDict.keys():
      self.modelId += 1
    return str(self.modelId)
  
  def setObject( self, model_, modelId ):
    self.modelIdDict[ modelId ] = model_
  
  def getObjectId( self, model ):
    #objectIds = list()
    for objId, obj in self.modelIdDict.items():
      if obj == model:
        return objId
  
  def getObject( self, modelId ):
    if self.modelIdDict.has_key( modelId ):
      obj = self.modelIdDict[modelId]
      #print "found model with tag", modelId, ":", obj
      return obj
    return None
  
  def delObjectId( self, modelId ):
    if self.modelIdDict.has_key( modelId ):
      del self.modelIdDict[modelId]
  
  def delObject( self, model ):
    objectIds = list()
    for objId, obj in self.modelIdDict.items():
      if obj == model:
        objectIds.append( objId )
    for objId in objectIds:
      self.delObjectId( objId )
  
  def getAllModels( self ):
    return self.modelIdDict.values()

modelIdManager = ModelIdManager()
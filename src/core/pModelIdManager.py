VALIDITYCHECK_RATE = None

class ModelIdManager:
  def __init__( self ):
    self.modelId = 0
    self.modelIdDict = dict()
    if VALIDITYCHECK_RATE:
      taskMgr.doMethodLater(VALIDITYCHECK_RATE, self.validityCheck, 'ModelIdManager-validityCheck')
  
  def getId( self ):
    # get next free modelId
    self.modelId += 1
    while self.modelId in self.modelIdDict.keys():
      self.modelId += 1
    return str(self.modelId)
  
  def setObject( self, model_, modelId ):
    self.modelIdDict[ modelId ] = model_
  
  def getObjectId( self, model ):
    for objId, obj in self.modelIdDict.items():
      if obj == model:
        return objId
    return None
  
  def getObject( self, modelId ):
    if self.modelIdDict.has_key( modelId ):
      obj = self.modelIdDict[modelId]
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
  
  def getAllModels(self):
    return self.modelIdDict.values()
  
  def validityCheck(self, task):
    print "I: ModelIdManager.validityCheck: running"
    for objId, obj in self.modelIdDict.items():
      try:
        obj.getName()
      except:
        print "E: ModelIdManager.validityCheck: failed for object", objId, obj
        del self.modelIdDict[objId]
    return task.again

modelIdManager = ModelIdManager()
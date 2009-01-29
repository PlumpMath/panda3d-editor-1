__all__ = ['CurveNodeWrapper', 'CurveNodePointWrapper']

from pandac.PandaModules import *

from core.modules.pVirtualNodeWrapper import VirtualNodeWrapper
from core.pConfigDefs import *

from pCurveNodePointWrapper import CurveNodePointWrapper

class CurveNodeWrapper(VirtualNodeWrapper):
  className = 'Curve'
  def __init__(self, parent, name='Curve', curveNodeModel='data/models/misc/sphere.egg'):
    #curveNodeModel = 
    VirtualNodeWrapper.__init__(self, parent, name, curveNodeModel)
    #self.nurbsCurveNodes = list()
    self.nurbsCurveEvaluator = NurbsCurveEvaluator()
    self.nurbsCurveDetail = 4
    #self.setNodepath(NodePath('curveNodeWrapper'))
    #self.getNodepath().reparentTo(self.getParentNodepath())
    self.lineRenderNp = self.getNodepath().attachNewNode('lineRender')
    self.possibleChildren = ['CurveNodePointWrapper']
    
    self.mutableParameters['add node'] = [ Trigger,
        self.getAddNode,
        self.setAddNode,
        None,
        None
      ]
    self.mutableParameters['remove node'] = [ Trigger,
        self.getRemoveNode,
        self.setRemoveNode,
        None,
        None
      ]
    self.mutableParameters['curve detail'] = [ int,
        self.getCurveDetail,
        self.setCurveDetail,
        None,
        None
      ]
  
  def destroy(self):
    self.lineRenderNp.detachNode()
    self.lineRenderNp.removeNode()
    VirtualNodeWrapper.destroy(self)
  
  def getAddNode(self):
    pass
  def setAddNode(self):
    print "  - creating"
    # find where to position this node
    if len(self.getChildren()) > 0:
      # place relative to last added node
      prevNode = self.getChildren()[-1]
    else:
      # the first node is not placed
      prevNode = self
    
    curveNode = CurveNodePointWrapper.onCreateInstance(self)
    # every new node is placed 5units right of the previous
    curveNode.getNodepath().setPos(render, prevNode.getNodepath().getPos(render)+Vec3(5,0,0))
    
    # enable editmode
    if self.isEditmodeEnabled():
      curveNode.setEditmodeEnabled()
    self.update()
  
  def getRemoveNode(self):
    pass
  def setRemoveNode(self):
    # we need to destroy some of the child nodes
    print "  - destroying"
    nurbsCurveNodes = self.getChildren()
    if len(nurbsCurveNodes) > 0:
    #for i in xrange(currentNumNodes-newNumNodes):
      curveNode = self.getChildren()[-1]
      print "    -", curveNode
      curveNode.destroy()
      self.update()
    else:
      print "I: CurveNodeWrapper.setRemoveNode: cannot remove with no childrens"
  
  def getNumNodes(self):
    nurbsCurveLen = len(self.getChildren())
    return nurbsCurveLen
  
  def setCurveDetail(self, detail):
    detail = max(4, detail)
    self.nurbsCurveDetail = detail
    self.update()
  
  def getCurveDetail(self):
    return self.nurbsCurveDetail
  
  def update(self):
    ''' update the line from the positions, and render it
    '''
    nurbsCurveNodes = self.getChildren()
    nurbsCurveLen = len(nurbsCurveNodes)
    
    # destroy the previous line rendering
    for child in self.lineRenderNp.getChildrenAsList():
      child.removeNode()
    
    if nurbsCurveLen >= 4:
      # update the curve with the points in nurbsCurvePositions
      print "writing", nurbsCurveLen
      self.nurbsCurveEvaluator.reset(nurbsCurveLen)
      for i in xrange(nurbsCurveLen):
        position = nurbsCurveNodes[i].getNodepath().getPos(self.getNodepath())
        vtxPos = Vec4(position.getX(),position.getY(),position.getZ(),1)
        self.nurbsCurveEvaluator.setVertex(i, vtxPos)
      nurbsCurveResult = self.nurbsCurveEvaluator.evaluate()
      
      # setup the line segments for rendering
      lineSegs = LineSegs()
      lineSegs.setThickness(1)
      
      # create the line segments
      startT = nurbsCurveResult.getStartT()
      endT = nurbsCurveResult.getEndT()
      stepT = (endT - startT) / (self.nurbsCurveDetail-1)
      for i in xrange(self.nurbsCurveDetail):
        # which point in the curve are we at
        curT = startT+stepT*i
        # determine the point
        p = Point3()
        nurbsCurveResult.evalPoint(curT,p)
        if i == 0:
          # 
          lineSegs.moveTo(p)
        else:
          lineSegs.drawTo(p)
      node = lineSegs.create()
      lineSegsNodePath = NodePath(node)
      
      lineSegsNodePath.reparentTo(self.lineRenderNp)
    else:
      print "I: CurveNodeWrapper.update: requires at least 4 nodes to render"
    print
  
  def loadFromData(self, eggGroup, filepath):
    VirtualNodeWrapper.loadFromData(self, eggGroup, filepath)
    # we call udpate in here, because this function is called after all nodes
    # have been loaded
    self.update()

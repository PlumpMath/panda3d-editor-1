__all__ = ['CurveSurfaceNodeWrapper']

import math

from pandac.PandaModules import *

from core.pConfigDefs import *

from pCurveNodeWrapper import CurveNodeWrapper


class PlaneProfile:
  ''' defines a profile for the curve '''
  def __init__(self):
    self.curvePos = None
    self.curve = NurbsCurveEvaluator()
  
  def setCurvePositions(self, positions):
    ''' define the curve profile
    '''
    self.curvePos = positions
    curveLen = len(self.curvePos)
    
    if self.curvePos is not None:
      self.curve.reset(curveLen)
      
      for i in xrange(curveLen):
        self.curve.setVertex(i, Vec4(i,self.curvePos[i],0,1))
    
    self.curveResult = self.curve.evaluate()
  
  def getCurvePositions(self):
    return self.curvePos
  
  def getH(self, x):
    ''' get the y position of the profile
    '''
    curveLen = len(self.curvePos) - 3
    point = Point3()
    xPos = math.fabs(x) * curveLen
    self.curveResult.evalPoint(xPos, point)
    yPos = point.getY()
    return yPos

ANIMATED_TEXTURE = True



class CurveSurfaceNodeWrapper(CurveNodeWrapper):
  className = 'CurveSurface'
  def __init__(self, parent, name='CurveSurface'):
    surfaceNodeModel = 'data/models/misc/sphere.egg'
    CurveNodeWrapper.__init__(self, parent, name, surfaceNodeModel)
    
    #self.nurbsSurfaceEvaluator = NurbsSurfaceEvaluator()
    self.surfaceRenderNP = self.getNodepath().attachNewNode('surfaceRender')
    
    self.profile = PlaneProfile()
    profile = [.05,.05,.05,.05,0,0]
    self.profile.setCurvePositions(profile)
    
    self.mutableParameters['profile'] = [ list,
        self.getProfile,
        self.setProfile,
        None,
        None
      ]
    self.profileDetail = 6
    self.mutableParameters['profile detail'] = [ int,
        self.getProfileDetail,
        self.setProfileDetail,
        None,
        None
      ]
    
    self.surfaceWidth = 1
    self.mutableParameters['width'] = [ float,
        self.getSurfaceWidth,
        self.setSurfaceWidth,
        None,
        None
      ]
    self.uTexScale = 1.0
    self.mutableParameters['uTexScale'] = [ float,
        self.getUTexScale,
        self.setUTexScale,
        None,
        None
      ]
    self.vTexScale = 1.0
    self.mutableParameters['vTexScale'] = [ float,
        self.getVTexScale,
        self.setVTexScale,
        None,
        None
      ]
  
  def destroy(self):
    self.lineRenderNp.detachNode()
    self.lineRenderNp.removeNode()
    CurveNodeWrapper.destroy(self)
  
  def setSurfaceWidth(self, width):
    self.surfaceWidth = width
    self.update()
  def getSurfaceWidth(self):
    return self.surfaceWidth
  
  def getProfile(self):
    return self.profile.getCurvePositions()
  def setProfile(self, profile):
    if len(profile) > 3:
      self.profile.setCurvePositions(profile)
      self.update()
  
  def getProfileDetail(self):
    return self.profileDetail
  def setProfileDetail(self, detail):
    if detail >= 4:
      self.profileDetail = detail
      self.update()
  
  def setUTexScale(self, uTexScale):
    self.uTexScale = uTexScale
    self.update()
  def getUTexScale(self):
    return self.uTexScale
  
  def setVTexScale(self, vTexScale):
    self.vTexScale = vTexScale
    self.update()
  def getVTexScale(self):
    return self.vTexScale
  
  
  def update(self):
    ''' override the curveRendering
    '''
    # clear the previous children
    for child in self.surfaceRenderNP.getChildrenAsList():
      child.removeNode()
    
    nurbsCurveNodes = self.getChildren()
    nurbsCurveLen = len(nurbsCurveNodes)
    
    if nurbsCurveLen >= 4:
      # update the curve with the points in nurbsCurvePositions
      nurbsCurveEvaluator = NurbsCurveEvaluator()
      nurbsCurveEvaluator.reset(nurbsCurveLen)
      for i in xrange(nurbsCurveLen):
        position = nurbsCurveNodes[i].getNodepath().getPos(self.getNodepath())
        posVec = Vec4(position.getX(),position.getY(),position.getZ(),1)
        nurbsCurveEvaluator.setVertex(i, posVec)
      nurbsCurveResult = nurbsCurveEvaluator.evaluate()
      
      nurbsSurfaceEvaluator = NurbsSurfaceEvaluator()
      nurbsSurfaceEvaluator.reset(nurbsCurveLen,self.profileDetail)
      for ui in xrange(nurbsCurveLen):
        for vi in xrange(self.profileDetail):
          u = ui
          point = Point3()
          nurbsCurveResult.evalPoint(u,point)
          tangent = Point3()
          nurbsCurveResult.evalTangent(u,tangent)
          tangent.normalize()
          normal = tangent.cross(Vec3(0,0,1)) / 2.0
          w = ((vi/float(self.profileDetail-1)) - 0.5) * 2
          h = self.profile.getH(w)
          #print "w", w, h
          #  center + side              + height
          p = point + normal * w * self.surfaceWidth + Vec3(0,0,1) * h
          xVal = p.getX()
          yVal = p.getY()
          zVal = p.getZ()
          
          nurbsSurfaceEvaluator.setVertex(ui, vi, Vec4(xVal,yVal,zVal,1))
      nurbsSurfaceResult = nurbsSurfaceEvaluator.evaluate()
      
      # egg data
      data = EggData()
      vtxPool = EggVertexPool('fan')
      data.addChild(vtxPool)
      eggGroup = EggGroup('group')
      data.addChild(eggGroup)
      
      # --- calc ---
      self.vertices = dict()
      uDetail = nurbsCurveLen*self.nurbsCurveDetail
      vDetail = self.profileDetail*2
      for xi in xrange(uDetail+1):
        for yi in xrange(vDetail+1):
          x = xi/float(uDetail) * nurbsCurveLen
          y = yi/float(vDetail) * self.profileDetail
          point = Point3()
          nurbsSurfaceResult.evalPoint(x,y,point)
          normal = Vec3()
          nurbsSurfaceResult.evalNormal(x,y,normal)
          uvX = -xi/float(uDetail) * self.uTexScale
          uvY = yi/float(vDetail) * self.vTexScale
          uv = Point2D(uvX, uvY)
          
          # not yet correct
          #normal = Vec3D(0,0,1)
          #tangent = -Vec3D(0,0,1)
          #binormal = -Vec3D(0,0,1)
          #print uv
          
          eggVtxUv = EggVertexUV('a', uv)
          # not needed to define the tangent and binormal
          #eggVtxUv.setTangent(tangent)
          #eggVtxUv.setBinormal(binormal)
          #eggVtxUv.setUv(uv)
          
          point3D = Point3D(point.getX(), point.getY(), point.getZ())
          normal3D = -Vec3D(normal.getX(), normal.getY(), normal.getZ())
          # now we have the point and the uv
          eggVtx = EggVertex()
          eggVtx.setPos(point3D)
          eggVtx.setNormal(normal3D)
          #eggVtx.setTangent(tangent)
          #eggVtx.setBinormal(binormal)
          #eggVtx.setUv(uv)
          
          eggVtx.setUvObj(eggVtxUv)
          
          self.vertices[(xi,yi)] = eggVtx
          
          vtxPool.addVertex(eggVtx)
      
      mat1 = EggMaterial('waterMat')
      mat1.setDiff(Vec4(1,1,1,1))
      mat1.setAmb(Vec4(0,0,0,0))
      mat1.setEmit(Vec4(0,0,0,0))
      mat1.setShininess(0.0)
      mat1.setSpec(Vec4(0,0,0,0))
      
      texBase = 'diffuse'
      texFn = 'examples/water.png'
      tex1 = EggTexture( texBase, texFn )
      #tex1.setAlphaMode( EggRenderMode.AMMsMask )
      tex1.setMagfilter( EggTexture.FTLinearMipmapLinear )
      tex1.setMinfilter( EggTexture.FTNearestMipmapLinear )
      tex1.setUvName('a')
      #eggGroup.addChild(tex)
      
      texBase = 'normal'
      texFn = 'examples/water-render/0001.png'
      tex2 = EggTexture( texBase, texFn )
      #tex2.setAlphaMode( EggRenderMode.AMMsMask )
      tex2.setMagfilter( EggTexture.FTLinearMipmapLinear )
      tex2.setMinfilter( EggTexture.FTNearestMipmapLinear )
      tex2.setEnvType( EggTexture.ETNormal )
      tex2.setUvName('a')
      
      for x, y in self.vertices.keys():
        xyPos = (x+1,y+1,)
        if xyPos in self.vertices:
          p1 = self.vertices[(x  ,y  )]
          p2 = self.vertices[(x+1,y  )]
          p3 = self.vertices[(x  ,y+1)]
          p4 = self.vertices[(x+1,y+1)]
          
          eggPoly = EggPolygon()
          eggPoly.addVertex(p3)
          eggPoly.addVertex(p2)
          eggPoly.addVertex(p1)
          eggPoly.addTexture(tex1)
          eggPoly.addTexture(tex2)
          eggPoly.setMaterial(mat1)
          
          eggGroup.addChild(eggPoly)
          
          eggPoly = EggPolygon()
          eggPoly.addVertex(p2)
          eggPoly.addVertex(p3)
          eggPoly.addVertex(p4)
          eggPoly.addTexture(tex1)
          eggPoly.addTexture(tex2)
          eggPoly.setMaterial(mat1)
          
          eggGroup.addChild(eggPoly)
      # --- calc done ---
      
      eggGroup.recomputeTangentBinormalAuto()
      #raise()
      
      #print "saving egg"
      #data.writeEgg(Filename('test.egg'))
      
      #print data
      
      # To load the egg file and render it immediately, use this:
      self.mdl = NodePath(loadEggData(data))
      #mdl.setRenderModeWireframe()
      self.mdl.reparentTo(self.surfaceRenderNP)
      
      if ANIMATED_TEXTURE:
        self.mdl.setShaderAuto()
        
        taskMgr.remove('surfaceTextureTask'+str(self))
        
        #self.diffuseTs = self.mdl.findTextureStage('diffuse')
        self.normalMapTs = self.mdl.findTextureStage('normal')
      
        self.waterNormalTextures = list()
        for i in xrange(1,101):
          waterNormalTex = loader.loadTexture('examples/water-render/%04i.png' % i)
          self.waterNormalTextures.append(waterNormalTex)
        #self.waterDiffuseTexture = loader.loadTexture('examples/water.png')
        taskMgr.add(self.textureTask, 'surfaceTextureTask'+str(self))
  
  def textureTask(self, task):
    t = task.time
    i = int((t * 30.0) % 100)
    waterNormalTexture = self.waterNormalTextures[i]
    
    #print "normalMapTs", normalMapTs
    self.mdl.setTexture(self.normalMapTs, waterNormalTexture, 1)
    
    '''if False:
      # update texture
      diffuseTs = main.mdl.findTextureStage('diffuse')
      #print "diffuseTs", diffuseTs
      main.mdl.setTexture(diffuseTs, waterDiffuseTexture, 0)'''
    
    return task.cont
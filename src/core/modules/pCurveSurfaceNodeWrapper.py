__all__ = ['CurveSurfaceNodeWrapper']

import math

from pandac.PandaModules import *

from core.pConfigDefs import *

from pCurveNodeWrapper import CurveNodeWrapper

# ----
# maybe we should use HermiteCurve instead, which gives more control of the
# curve parameters (in and out tangent)
# ----

DEBUG = True

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
  
  def getPoint(self, x):
    ''' get the y position of the profile
    '''
    curveLen = len(self.curvePos) - 3
    point = Point3()
    xPos = math.fabs(x) * curveLen
    self.curveResult.evalPoint(xPos, point)
    return point
  
  def getH(self, x):
    return self.getPoint(x).getY()
  
  def getTangent(self, x):
    ''' get the y position of the profile
    '''
    curveLen = len(self.curvePos) - 3
    point = Point3()
    xPos = math.fabs(x) * curveLen
    self.curveResult.evalTangent(xPos, point)
    #yPos = point.getY()
    return point

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
    self.surfaceDetail = 6
    self.mutableParameters['surface detail'] = [ int,
        self.getSurfaceDetail,
        self.setSurfaceDetail,
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
    
    if DEBUG:
      self.debugNode = self.getNodepath().attachNewNode('debugNode')
  
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
  
  def getSurfaceDetail(self):
    return self.surfaceDetail
  def setSurfaceDetail(self, detail):
    if detail >= 4:
      self.surfaceDetail = detail
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
    # method using a nurbsSurfaceEvaluator
    self.updateUsingSurface()
    # method using only the 2 curves
    #self.updataUsingCurves()
  
  def updateUsingSurface(self):
    ''' override the curveRendering
    '''
    # clear the previous children
    for child in self.surfaceRenderNP.getChildrenAsList():
      child.removeNode()
    
    if DEBUG:
      self.debugNode.removeNode()
      self.debugNode = self.getNodepath().attachNewNode('debugNode')
    
    nurbsCurveNodes = self.getChildren()
    nurbsCurveLen = len(nurbsCurveNodes)
    
    if nurbsCurveLen >= 4:
      '''#
      hermitePosCurve = HermiteCurve()
      #hermitePosCurve.removeAllCvs()'''
      
      # update the curve position with the points in nurbsCurvePositions
      nurbsCurvePosEvaluator = NurbsCurveEvaluator()
      nurbsCurvePosEvaluator.reset(nurbsCurveLen)
      # update the curve position with the points in nurbsCurvePositions
      nurbsCurveHprEvaluator = NurbsCurveEvaluator()
      nurbsCurveHprEvaluator.reset(nurbsCurveLen)
      # update the curve position with the points in nurbsCurvePositions
      nurbsCurveScaleEvaluator = NurbsCurveEvaluator()
      nurbsCurveScaleEvaluator.reset(nurbsCurveLen)
      for i in xrange(nurbsCurveLen):
        # the nodepath we are reading the pos/hpr/scale from
        curveNodepath = nurbsCurveNodes[i].getNodepath()
        position = curveNodepath.getPos(self.getNodepath())
        hpr      = curveNodepath.getHpr(self.getNodepath())
        scale    = curveNodepath.getScale(self.getNodepath())
        #print "nodepath", position, hpr, scale
        
        # convert
        posVec = Vec4(position.getX(), position.getY(), position.getZ(),1)
        hprVec = Vec4(hpr.getX(), hpr.getY(), hpr.getZ(),1)
        scaleVec = Vec4(scale.getX(), scale.getY(), scale.getZ(),1)
        #print "converted", posVec, hprVec, scaleVec
        
        # set position
        nurbsCurvePosEvaluator.setVertex(i, posVec)
        # set rotation (to calculate the normal)
        nurbsCurveHprEvaluator.setVertex(i, hprVec)
        # set scale
        nurbsCurveScaleEvaluator.setVertex(i, scaleVec)
        
        '''# some other method testing
        hermitePosCurve.insertCv(i) # is required, else it's invalid
        hermitePosCurve.setCvPoint(i, position)
        inVec = self.getNodepath().getRelativeVector(curveNodepath, Vec3(1,0,0))
        hermitePosCurve.setCvIn(i, inVec)
        outVec = self.getNodepath().getRelativeVector(curveNodepath, Vec3(-1,0,0))
        hermitePosCurve.setCvOut(i, inVec)'''
      
      nurbsCurvePosResult = nurbsCurvePosEvaluator.evaluate()
      nurbsCurveHprResult = nurbsCurveHprEvaluator.evaluate()
      nurbsCurveScaleResult = nurbsCurveScaleEvaluator.evaluate()
      '''hermitePosCurve.recompute()'''
      
      # store into the surface
      nurbsSurfaceEvaluator = NurbsSurfaceEvaluator()
      nurbsSurfaceEvaluator.reset(self.nurbsCurveDetail,self.profileDetail)
      
      # step's for evaulating the nurbsCurve (is the same for all results)
      startT = nurbsCurvePosResult.getStartT()
      endT = nurbsCurvePosResult.getEndT()
      stepT = (endT - startT) / (self.nurbsCurveDetail-1)
      
      '''sT = 0 #hermitePosCurve.getStartT()
      eT = hermitePosCurve.getMaxT()
      dT = (eT - sT) / (self.nurbsCurveDetail-1)'''
      
      dummyNode = self.getNodepath().attachNewNode('dummy')
      dummyParent = self.getParentNodepath()
      
      for xi in xrange(self.nurbsCurveDetail):
        curT = startT+stepT*xi
        # read from the curve position
        posPoint = Point3()
        nurbsCurvePosResult.evalPoint(curT,posPoint)
        '''posTangent = Point3()
        nurbsCurvePosResult.evalTangent(curT,posTangent)
        posTangent.normalize()'''
        
        '''# testing
        hermitePoint = Point3()
        hermiteTangent = Point3()
        cT = sT+dT*xi
        hermitePosCurve.getPt(cT, hermitePoint, hermiteTangent)
        hermiteTangent.normalize()'''
        
        # read from the curve rotation
        hprPoint = Point3()
        nurbsCurveHprResult.evalPoint(curT,hprPoint)
        '''hprTangent = Point3()
        nurbsCurveHprResult.evalTangent(curT,hprTangent)
        hprTangent.normalize()'''
        
        # read from the curve scale
        scalePoint = Point3()
        nurbsCurveScaleResult.evalPoint(curT,scalePoint)
        '''scaleTangent = Point3()
        nurbsCurveScaleResult.evalTangent(curT,scaleTangent)
        scaleTangent.normalize()'''
        
        for yi in xrange(self.profileDetail):
          dummyNode.setPos(dummyParent, posPoint)
          dummyNode.setScale(dummyParent, scalePoint)
          dummyNode.setHpr(dummyParent, hprPoint)
          
          # read from the profile
          w = ((yi/float(self.profileDetail-1)) - 0.5) * 2
          h = self.profile.getH(w) # input must be -1..1
          
          # calculate the profile position in 3d space
          dummyNode.setPos(dummyNode, Vec3(0,-w * self.surfaceWidth,h))
          p = dummyNode.getPos(dummyParent)
          
          surfaceVtx = Vec4(p.getX(),p.getY(),p.getZ(),1)
          nurbsSurfaceEvaluator.setVertex(xi, yi, surfaceVtx)
      
      nurbsSurfaceResult = nurbsSurfaceEvaluator.evaluate()
      dummyNode.removeNode() # destroy the dummy
      
      if DEBUG:
        self.debugNode.flattenStrong()
      
      # egg data
      data = EggData()
      vtxPool = EggVertexPool('fan')
      data.addChild(vtxPool)
      eggGroup = EggGroup('group')
      data.addChild(eggGroup)
      
      startU = nurbsSurfaceResult.getStartU()
      endU = nurbsSurfaceResult.getEndU()
      stepU = (endU - startU) / (self.surfaceDetail-1)
      startV = nurbsSurfaceResult.getStartV()
      endV = nurbsSurfaceResult.getEndV()
      stepV = (endV - startV) / (self.profileDetail-1)
      
      # --- calc ---
      self.vertices = dict()
      for xi in xrange(self.surfaceDetail):
        curU = startU+stepU*xi
        for yi in xrange(self.profileDetail):
          curV = startV+stepV*yi
          
          surfacePoint = Point3()
          nurbsSurfaceResult.evalPoint(curU,curV,surfacePoint)
          surfaceNormal = Vec3()
          nurbsSurfaceResult.evalNormal(curU,curV,surfaceNormal)
          surfaceNormal.normalize()
          
          '''x = xi/float(uDetail) * nurbsCurveLen
          y = yi/float(vDetail) * self.profileDetail'''
          uvX = -xi/float(self.surfaceDetail-1) * self.uTexScale
          uvY = yi/float(self.profileDetail-1) * self.vTexScale
          uv = Point2D(uvX, uvY)
          
          eggVtxUv = EggVertexUV('a', uv)
          # not needed to define the tangent and binormal, will calculated automatically
          #eggVtxUv.setTangent(tangent)
          #eggVtxUv.setBinormal(binormal)
          #eggVtxUv.setUv(uv)
          
          vtxPoint = Point3D(surfacePoint.getX(), surfacePoint.getY(), surfacePoint.getZ())
          vtxNormal = -Vec3D(surfaceNormal.getX(), surfaceNormal.getY(), surfaceNormal.getZ())
          # now we have the point and the uv
          eggVtx = EggVertex()
          eggVtx.setPos(vtxPoint)
          eggVtx.setNormal(vtxNormal)
          
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
      
      # To load the egg file and render it immediately, use this:
      self.mdl = NodePath(loadEggData(data))
      #mdl.setRenderModeWireframe()
      self.mdl.reparentTo(self.surfaceRenderNP)
      
      if ANIMATED_TEXTURE:
        self.mdl.setShaderAuto()
        
        taskName = 'surfaceTextureTask'+str(hash(self))
        
        taskMgr.remove(taskName) #'surfaceTextureTask'+str(self.__module__.__hash__()))
        
        #self.diffuseTextureStage = self.mdl.findTextureStage('diffuse')
        self.normalTextureStage = self.mdl.findTextureStage('normal')
      
        self.normalTextures = list()
        for i in xrange(1,101):
          waterNormalTex = loader.loadTexture('examples/water-render/%04i.png' % i)
          self.normalTextures.append(waterNormalTex)
        #self.waterDiffuseTexture = loader.loadTexture('examples/water.png')
        taskMgr.add(self.textureTask, taskName) #'surfaceTextureTask'+str(self.__module__.__hash__()))
  
  """def updataUsingCurves(self):
    ''' override the curveRendering
    calculate the curve, using it's point and tangent and a defined normal vector
    we calculate a profile
    
    TRYING TO IMPLEMENT IT W/O USING nurbsSurfaceEvaluator
    '''
    # clear the previous children
    for child in self.surfaceRenderNP.getChildrenAsList():
      child.removeNode()
    
    nurbsCurveNodes = self.getChildren()
    nurbsCurveLen = len(nurbsCurveNodes)
    
    if nurbsCurveLen >= 4:
      # update the curve with the points in nurbsCurvePositions
      # define the curve using the number of childrens we have
      nurbsCurveEvaluator = NurbsCurveEvaluator()
      nurbsCurveEvaluator.reset(nurbsCurveLen)
      for i in xrange(nurbsCurveLen):
        position = nurbsCurveNodes[i].getNodepath().getPos(self.getNodepath())
        posVec = Vec4(position.getX(),position.getY(),position.getZ(),1)
        nurbsCurveEvaluator.setVertex(i, posVec)
      nurbsCurveResult = nurbsCurveEvaluator.evaluate()
      
      # egg data
      data = EggData()
      vtxPool = EggVertexPool('fan')
      data.addChild(vtxPool)
      eggGroup = EggGroup('group')
      data.addChild(eggGroup)
      
      self.vertices = dict()
      
      # get "time" in the curve
      startTx = nurbsCurveResult.getStartT()
      endTx = nurbsCurveResult.getEndT()
      stepTx = (endTx - startTx) / (self.nurbsCurveDetail-1)
      # calculate the surface by generating a profile and the curve
      for ix in xrange(self.nurbsCurveDetail):
        # length of the model (0..1)
        #px = ix / float(self.nurbsCurveDetail-1)
        
        curTx = startTx+stepTx*ix
        
        # the point on the curve
        curvePoint = Point3()
        nurbsCurveResult.evalPoint(curTx,curvePoint)
        curvePoint3D = Point3D(
            curvePoint.getX(),
            curvePoint.getY(),
            curvePoint.getZ() )
        # the tangent on the curve
        curveTangent = Point3()
        nurbsCurveResult.evalPoint(curTx,curveTangent)
        curveTangent.normalize()
        curveTangent3D = Point3D(
            curveTangent.getX(),
            curveTangent.getY(),
            curveTangent.getZ() )
        widthVec = curveTangent.cross(Vec3(0,0,1)) / 2.0 * self.surfaceWidth
        widthVec.normalize()
        
        for iy in xrange(self.profileDetail):
          # width of the model (0..1)
          py = iy / float(self.profileDetail-1)
          ty = py - 0.5
          
          # get the profile
          #profilePoint = self.profile.getPoint(py-0.5)
          profileHeight = self.profile.getH(py-0.5)
          #profileTangent = self.profile.getTangent(py-0.5)
          #profileNormal = profileTangent.cross(Vec3(curveTangent))
          
          surfacePoint = curvePoint + widthVec * ty + Vec3(0,0,1) * profileHeight
          
          vtxPos = Point3D(surfacePoint.getX(), surfacePoint.getY(), surfacePoint.getZ())
          #vtxNormal = Vec3D(profileNormal.getX(), profileNormal.getY(), profileNormal.getZ())
          vtxNormal = Vec3D(0,0,1)
          vtxUv = Point2D(
              -curTx * self.uTexScale,
               py * self.vTexScale )
          
          # uv coordinates, 
          eggVtxUv = EggVertexUV('a', vtxUv)
          
          # vertex
          eggVtx = EggVertex()
          eggVtx.setPos(vtxPos)
          eggVtx.setNormal(vtxNormal)
          eggVtx.setUvObj(eggVtxUv)
          
          # store the values
          self.vertices[(ix,iy)] = eggVtx
          vtxPool.addVertex(eggVtx)
      
      mat1 = EggMaterial('waterMat')
      mat1.setDiff(Vec4(1,1,1,1))
      mat1.setAmb(Vec4(0,0,0,0))
      mat1.setEmit(Vec4(0,0,0,0))
      mat1.setShininess(0.0)
      mat1.setSpec(Vec4(0,0,0,0))
      
      # diffuse texture
      texBase = 'diffuse'
      texFn = 'examples/water.png'
      tex1 = EggTexture( texBase, texFn )
      #tex1.setAlphaMode( EggRenderMode.AMMsMask )
      tex1.setMagfilter( EggTexture.FTLinearMipmapLinear )
      tex1.setMinfilter( EggTexture.FTNearestMipmapLinear )
      tex1.setUvName('a')
      
      # normal texture
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
      
      # calculate tangents and binormal
      eggGroup.recomputeTangentBinormalAuto()
      
      # To load the egg file and render it immediately, use this:
      self.mdl = NodePath(loadEggData(data))
      self.mdl.reparentTo(self.surfaceRenderNP)
      
      if ANIMATED_TEXTURE:
        # texture stages
        self.diffuseTextureStage = self.mdl.findTextureStage('diffuse')
        self.normalTextureStage = self.mdl.findTextureStage('normal')
        
        # list of normal texture
        self.normalTextures = list()
        for i in xrange(1,101):
          normalTexture = loader.loadTexture('examples/water-render/%04i.png' % i)
          self.normalTextures.append(normalTexture)
        
        # enable auto shader
        self.mdl.setShaderAuto()
        
        # task to change the texture
        taskMgr.remove('surfaceTextureTask'+str(self))
        taskMgr.add(self.textureTask, 'surfaceTextureTask'+str(self))"""
  
  def textureTask(self, task):
    t = task.time
    i = int((t * 30.0) % 100)
    normalTexture = self.normalTextures[i]
    
    #print "normalTextureStage", normalTextureStage
    self.mdl.setTexture(self.normalTextureStage, normalTexture, 1)
    
    '''if False:
      # update texture
      diffuseTextureStage = main.mdl.findTextureStage('diffuse')
      #print "diffuseTextureStage", diffuseTextureStage
      main.mdl.setTexture(diffuseTextureStage, waterDiffuseTexture, 0)'''
    
    return task.cont
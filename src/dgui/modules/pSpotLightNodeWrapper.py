from dgui.modules.pLightNodeWrapper import *

class SpotLightNodeWrapper(LightNodeWrapper):
  def __init__(self, object):
    LightNodeWrapper.__init__(self, object)
    #self.mutableParameters['H-Fov'] = ['float', 'getHfov', 'setHfov', None]
    #self.mutableParameters['V-Fov'] = ['float', 'getVfov', 'setVfov', None]
    #self.mutableParametersSorting.append(['H-Fov', 'V-Fov'])
    self.mutableParameters['Fov'] = ['vec2', 'getFov', 'setFov', None]
    self.mutableParametersSorting.append('Fov')
    #self.mutableParameters['FilmSize'] = ['float2', 'getFilmSize, 'setFilmSize', None]
    #self.mutableParameters['FocalLength'] = ['float', 'getFocalLength', 'setFocalLength', None]
    #self.mutableParameters['AspectRatio'] = ['float', 'getAspectRatio', 'setAspectRatio', None]
    self.mutableParameters['Near'] = ['float', 'getNear', 'setNear', None]
    self.mutableParameters['Far'] = ['float', 'getFar', 'setFar', None]
    self.mutableParametersSorting.append(['Near', 'Far'])

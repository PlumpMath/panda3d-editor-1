#!/usr/bin/env python

''' sample showing the usage of the editor in scene loading
'''

from pandac.PandaModules import *

if __name__ == '__main__':
  from direct.directbase import DirectStart
  from core.pMain import *
  
  editor = EditorClass(render)
  editor.loadEggModelsFile("examples/save-1.egg")
  
  #print dir(editor)
  #print objectEditor
  #print dir(modelIdManager)
  print modelIdManager.getAllModels()
  #print modelController
  
  run()

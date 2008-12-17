__all__ = []

if __name__ == "__main__":
  # Whether to load dgui or wxgui.
  # use the directgui interface
  USE_GUI = "dgui"
  # use the wx-windows gui
  #USE_GUI = "wxgui"
  # just load the scene, dont start the editor
  #USE_GUI = None
  
  # First phase: load the configurations.
  if USE_GUI == "dgui":
    from dgui.pConfig import Config
  elif USE_GUI == "wxgui":
    from wxgui.pConfig import Config
  if USE_GUI is not None:
    Config.loadConfig()
  
  # Second phase: initialize the window manager (which starts ShowBase)
  from core.pWindow import WindowManager
  if USE_GUI == "dgui":
    WindowManager.startBase(showDefaultWindow = True, allowMultipleWindows = False)
  elif USE_GUI == "wxgui":
    WindowManager.startBase(showDefaultWindow = False, allowMultipleWindows = True)
  
  if USE_GUI is None:
    from direct.directbase import DirectStart
  # Third phase: load up the core of the editor.
  from core.pMain import EditorClass
  editor = EditorClass(render)
  editor.loadEggModelsFile("examples/save-1.egg")
  
  # Fourth phase: load one of the two interface layers.
  if USE_GUI == "dgui":
    from dgui.pEditorApp import EditorApp
    app = EditorApp(editor)
    app.toggle(True)
  elif USE_GUI == "wxgui":
    # wxgui needs to be opened before the editor, as it opens the window later
    from wxgui.pEditorApp import EditorApp
    app = EditorApp(editor)
  
  # Now, get it running :)
  if USE_GUI == "dgui":
    editor.toggle(True)
  
  editor.saveEggModelsFile("/l/_PROGRAMMING/_PROJECTS/eggEditor-cvs/panda3d-editor/examples/win-save-1.egg")
  
  import time
  while True:
    taskMgr.step()
    #time.sleep(0.05)


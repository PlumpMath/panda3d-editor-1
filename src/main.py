__all__ = []

if __name__ == "__main__":
  # Whether to load dgui or wxgui.
  from optparse import OptionParser
  parser = OptionParser()
  parser.add_option("-d", "--dgui",  action="store_true", dest="usedgui",  default=False, help="use the DirectGUI editor interface")
  parser.add_option("-w", "--wxgui", action="store_true", dest="usewxgui", default=False, help="use the wxWidgets editor interface")
  parser.add_option("-n", "--nogui", action="store_true", dest="usenogui", default=False, help="don't use any editor interface")
  options = parser.parse_args()[0]
  USE_GUI = None
  if options.usewxgui:  USE_GUI = "wxgui"
  elif options.usedgui: USE_GUI = "dgui"
  print "I: main: using interface:", USE_GUI
  
  # i put everything into the editor, because the external interface
  # must be as small as possible
  from core.pMain import EditorClass
  editor = EditorClass(parent=None, gui=USE_GUI)
  editor.loadEggModelsFile("examples/mytestscene.egs")
  #editor.loadEggModelsFile("examples/newscene.egs")
  #editor.loadEggModelsFile("examples/newscene2.egs")
  
  editor.toggle(True)
  
  run()

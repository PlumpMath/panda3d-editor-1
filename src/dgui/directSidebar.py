from direct.gui.DirectGui import DirectFrame,DirectButton,DirectScrolledFrame,DGG

ALIGN_LEFT=1
ALIGN_RIGHT=2
ALIGN_TOP=3
ALIGN_BOTTOM=4

class DirectSidebar(DirectFrame):
  def __init__(self,
               parent=None,
               frameSize=(1, 1),
               dragbarSize=0.05,
               align=ALIGN_BOTTOM,
               pos=(0,0,-0.5),):
    if parent is None:
      parent=aspect2d
    self.dragbarSize=dragbarSize
    self.align=align
    self.pos=pos
    self.frameSize=frameSize
    
    self.collapsed=False
    
    DirectFrame.__init__(self, parent=parent,
                         frameSize=(0,frameSize[0],0,frameSize[1]),
                         frameColor=(1,1,1,1), )
    self.initialiseoptions(DirectSidebar)
    self.collapseButton = DirectButton(parent=parent, 
                                       borderWidth=(0, 0), relief=DGG.FLAT,
                                       command=self.toggleCollapsed )
    
    self.accept('window-event', self.update)
  
  def update(self, args=None):
    aspectRatio=base.getAspectRatio()
    if self.align==ALIGN_LEFT:
      framePos=(-aspectRatio,0,self.pos[2])
      buttonSize=(0,self.dragbarSize,0,self.frameSize[1]),
      if self.collapsed:
        buttonPos=(-aspectRatio,0,self.pos[2])
      else:
        buttonPos=(self.frameSize[0]-aspectRatio,0,self.pos[2])
    elif self.align==ALIGN_RIGHT:
      framePos=(-aspectRatio,0,self.pos[2])
      buttonSize=(0,self.dragbarSize,0,self.frameSize[1]),
      if self.collapsed:
        buttonPos=(aspectRatio-self.dragbarSize,0,self.pos[2])
      else:
        buttonPos=(aspectRatio-self.frameSize[0]-self.dragbarSize,0,self.pos[2])
    elif self.align==ALIGN_TOP:
      framePos=(self.pos[0],0,1-self.frameSize[1])
      buttonSize=(0,self.frameSize[0],0,self.dragbarSize)
      if self.collapsed:
        buttonPos=(self.pos[0],0,1-self.dragbarSize)
      else:
        buttonPos=(self.pos[0],0,1-self.frameSize[1]-self.dragbarSize)
    elif self.align==ALIGN_BOTTOM:
      framePos=(self.pos[0],0,-1)
      buttonSize=(0,self.frameSize[0],0,self.dragbarSize)
      if self.collapsed:
        buttonPos=(self.pos[0],0,-1)
      else:
        buttonPos=(self.pos[0],0,-1+self.frameSize[1])
    
    if self.collapsed:
      self.hide()
    else:
      self.show()
    
    self.setPos(*framePos)
    self.collapseButton.setPos(*buttonPos)
    self.collapseButton['frameSize']=buttonSize
  
  def toggleCollapsed(self,state=None):
    if state is None:
      state=not self.collapsed
    print "I: DirectWindow.toggleCollapsed:", state
    self.collapsed=state
    self.update()

if __name__ == '__main__':
  from direct.directbase import DirectStart
  sideFrame = DirectSidebar(frameSize=(0.8,1.6), pos=(0,0,-.8))
  run()
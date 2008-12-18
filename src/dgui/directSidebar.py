import traceback

from direct.gui.DirectGui import DirectFrame,DirectButton,DirectScrolledFrame,DGG,DirectLabel
from pandac.PandaModules import *

#ALIGN_NONE=0
ALIGN_LEFT=1
ALIGN_RIGHT=2
ALIGN_TOP=4
ALIGN_BOTTOM=8

HORIZONTAL=10
VERTICAL=11

RIGHT_OR_DOWN=20
LEFT_OR_UP=21

class DirectSidebar(DirectFrame):
  def __init__(self,
               parent=None,
               frameSize=(1, 1),
               dragbarSize=0.05,
               align=ALIGN_LEFT|ALIGN_TOP,
               orientation=HORIZONTAL,
               opendir=RIGHT_OR_DOWN,
               pos=Vec3(0,0,0),
               text='',
               toggleFunc=None):
    if parent is None:
      parent=aspect2d
    self.dragbarSize=dragbarSize
    self.align=align
    self.orientation=orientation
    self.opendir=opendir
    self.pos=pos
    self.frameSize=frameSize
    self.toggleFunc=toggleFunc
    
    self.collapsed=False
    
    DirectFrame.__init__(self, parent=parent,
                         frameSize=(0,frameSize[0],0,frameSize[1]),
                         frameColor=(1,1,1,1), )
    self.initialiseoptions(DirectSidebar)
    self.collapseButton = DirectButton(parent=parent, 
                                       borderWidth=(0, 0), relief=DGG.FLAT,
                                       command=self.toggleCollapsed,
                                       )
    self.label = DirectLabel(parent=self.collapseButton,
                             scale=0.05,
                             text=text,
                             text_align=TextNode.ACenter
                             )
    if self.orientation == HORIZONTAL:
      self.label.setPos(Vec3(frameSize[0]/2.,0,0.015))
    if self.orientation == VERTICAL:
      self.label.setPos(Vec3(0.04,0,frameSize[1]/2.))
      self.label.setR(-90)
    
    self.accept('window-event', self.update)
    self.update()
  
  def destroy(self):
    print "I: DirectSidebar.__del__"
    self.label.detachNode()
    self.collapseButton.detachNode()
    self.detachNode()
    self.ignoreAll()#'window-event', self.update)
  
  def __del__(self):
    self.destroy()
  
  def update(self, args=None):
    aspectRatio=base.getAspectRatio()
    framePos=Vec3(self.pos[0],0,self.pos[2])
    
    if self.align & ALIGN_LEFT:
      framePos+=Vec3(-aspectRatio,0,0)
    if self.align & ALIGN_RIGHT:
      framePos+=Vec3(aspectRatio,0,0)
    if self.align & ALIGN_TOP:
      framePos+=Vec3(0,0,1-self.frameSize[1])
    if self.align & ALIGN_BOTTOM:
      framePos+=Vec3(0,0,-1)
    
    if self.orientation == HORIZONTAL:
      if self.align & ALIGN_RIGHT: # a small help for the user
        framePos-=Vec3(self.frameSize[0],0,0)
      buttonSize=(0,self.frameSize[0],0,self.dragbarSize)
      if self.opendir == RIGHT_OR_DOWN: # correct
        if self.collapsed:
          buttonPos=framePos+Vec3(0,0,self.frameSize[1]-self.dragbarSize)
        else:
          buttonPos=framePos+Vec3(0,0,-self.dragbarSize)
      elif self.opendir == LEFT_OR_UP:
        if self.collapsed:
          buttonPos=framePos
        else:
          buttonPos=framePos+Vec3(0,0,self.frameSize[1])
    
    elif self.orientation == VERTICAL:
      buttonSize=(0,self.dragbarSize,0,self.frameSize[1])
      if self.opendir == RIGHT_OR_DOWN:
        if self.collapsed:
          buttonPos=framePos
        else:
          buttonPos=framePos+Vec3(self.frameSize[0],0,0)
      elif self.opendir == LEFT_OR_UP:
        framePos-=Vec3(self.frameSize[0],0,0) # a small help for the user
        if self.collapsed:
          buttonPos=framePos+Vec3(self.frameSize[0]-self.dragbarSize,0,0)
        else:
          buttonPos=framePos
    
    if self.collapsed:
      self.hide()
    else:
      self.show()
    
    self.setPos(framePos)
    self.collapseButton.setPos(buttonPos)
    self.collapseButton['frameSize']=buttonSize
  
  def toggleCollapsed(self,state=None):
    if state is None:
      state=not self.collapsed
    print "I: DirectWindow.toggleCollapsed:", state
    self.collapsed=state
    if self.toggleFunc:
      try:
        self.toggleFunc(state)
      except:
        traceback.print_exc()
    self.update()

if __name__ == '__main__':
  from direct.directbase import DirectStart
  # from top
  sideFrame = DirectSidebar(frameSize=(0.4,0.8), pos=(-0.1,0,-0.05), align=ALIGN_RIGHT|ALIGN_TOP, opendir=RIGHT_OR_DOWN, text='right-top')
  sideFrame.toggleCollapsed(True)
  sideFrame = DirectSidebar(frameSize=(0.4,0.8), pos=(0.1,0,-0.05), align=ALIGN_LEFT|ALIGN_TOP, opendir=RIGHT_OR_DOWN, text='left-top')
  sideFrame.toggleCollapsed(True)
  # from bottom
  sideFrame = DirectSidebar(frameSize=(0.4,0.8), pos=(-0.1,0,0.05), align=ALIGN_RIGHT|ALIGN_BOTTOM, opendir=LEFT_OR_UP, text='right-bottom')
  sideFrame.toggleCollapsed(True)
  sideFrame = DirectSidebar(frameSize=(0.4,0.8), pos=(0.1,0,0.05), align=ALIGN_LEFT|ALIGN_BOTTOM, opendir=LEFT_OR_UP, text='left-bottom')
  sideFrame.toggleCollapsed(True)
  # from left
  sideFrame = DirectSidebar(frameSize=(0.8,0.4), pos=(0.05,0,-0.1), align=ALIGN_LEFT|ALIGN_TOP, opendir=RIGHT_OR_DOWN, orientation=VERTICAL, text='left-top')
  sideFrame.toggleCollapsed(True)
  sideFrame = DirectSidebar(frameSize=(0.8,0.4), pos=(0.05,0,0.1), align=ALIGN_LEFT|ALIGN_BOTTOM, opendir=RIGHT_OR_DOWN, orientation=VERTICAL, text='left-bottom')
  sideFrame.toggleCollapsed(True)
  # from right
  sideFrame = DirectSidebar(frameSize=(0.8,0.4), pos=(-.05,0,-0.1), align=ALIGN_RIGHT|ALIGN_TOP, opendir=LEFT_OR_UP, orientation=VERTICAL, text='right-top')
  sideFrame.toggleCollapsed(True)
  sideFrame = DirectSidebar(frameSize=(0.8,0.4), pos=(-.05,0,0.1), align=ALIGN_RIGHT|ALIGN_BOTTOM, opendir=LEFT_OR_UP, orientation=VERTICAL, text='right-bottom')
  sideFrame.toggleCollapsed(True)
  run()
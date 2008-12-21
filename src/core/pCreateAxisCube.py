from pandac.PandaModules import *

print "generating axisCube.bam ...",

# object highlighting
modelHelperLines = LineSegs()
modelHelperLines.reset()
# generate the cube
r = Vec4(1,0,0,1)
g = Vec4(0,1,0,1)
b = Vec4(0,0,1,1)
modelHelperLines.setThickness( 1 ) 
for [sx,sy,sz], [ex,ey,ez], col in \
        [ [[0,0,0], [1,0,0], r], [[0,0,0], [0,1,0], g], [[0,0,0], [0,0,1], b]
        , [[1,0,0], [1,1,0], g], [[1,0,0], [1,0,1], b]
        , [[0,1,0], [1,1,0], r], [[0,1,0], [0,1,1], b]
        , [[0,0,1], [0,1,1], g], [[0,0,1], [1,0,1], r]
        , [[1,1,0], [1,1,1], b], [[0,1,1], [1,1,1], r], [[1,0,1], [1,1,1], g] ]:
    modelHelperLines.setColor( col )
    modelHelperLines.moveTo( sx, sy, sz )
    modelHelperLines.drawTo( ex, ey, ez )
modelHelperLinesNode = modelHelperLines.create()
modelHelperLinesNodePath = NodePath(modelHelperLinesNode)
modelHelperLinesNodePath.writeBamFile( 'axisCube.bam' )

print "done"
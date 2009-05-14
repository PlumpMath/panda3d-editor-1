#!/usr/bin/env python
#
# Author: Cimarron Taylor
# Date: July 6, 2003
# File Name: relpath.py
# Program Description: Print relative path from /a/b/c/d to /a/b/c1/d1

#
# helper functions for relative paths
#
import os
import posixpath

def pathsplit(p, rest=[]):
    (h,t) = posixpath.split(p) #.split('/')
    if len(h) < 1: return [t]+rest
    if len(t) < 1: return [h]+rest
    return pathsplit(h,[t]+rest)

def commonpath(l1, l2, common=[]):
    if len(l1) < 1: return (common, l1, l2)
    if len(l2) < 1: return (common, l1, l2)
    if l1[0] != l2[0]: return (common, l1, l2)
    return commonpath(l1[1:], l2[1:], common+[l1[0]])

def relpath(p1, p2):
    (common,l1,l2) = commonpath(pathsplit(p1), pathsplit(p2))
    p = []
    if len(l1) > 0:
        p = [ '../' * len(l1) ]
    p = p + l2
    result = '/'.join( p )
#    print "I: commonPath.relpath: %s | %s -> %s" % (p1, p2, result)
    return result

# relpath.py
# R.Barran 30/08/2004
# (http://code.activestate.com/recipes/302594/)
def relpath(base=os.curdir, target=''):
    """
    Return a relative path to the target from either the current dir or an optional base dir.
    Base can be a directory specified either as absolute or relative to current dir.
    """

    #if not os.path.exists(target):
    #    raise OSError, 'Target does not exist: '+target

    #if not os.path.isdir(base):
    #    raise OSError, 'Base is not a directory or does not exist: '+base

    base_list = (os.path.abspath(base)).split(os.sep)
    target_list = (os.path.abspath(target)).split(os.sep)

    # On the windows platform the target may be on a completely different drive from the base.
    if os.name in ['nt','dos','os2'] and base_list[0] <> target_list[0]:
        raise OSError, 'Target is on a different drive to base. Target: '+target_list[0].upper()+', base: '+base_list[0].upper()

    # Starting from the filepath root, work out how much of the filepath is
    # shared by base and target.
    for i in range(min(len(base_list), len(target_list))):
        if base_list[i] <> target_list[i]: break
    else:
        # If we broke out of the loop, i is pointing to the first differing path elements.
        # If we didn't break out of the loop, i is pointing to identical path elements.
        # Increment i so that in all cases it points to the first differing path elements.
        i+=1

    rel_list = [os.pardir] * (len(base_list)-i) + target_list[i:]
    return os.path.join(*rel_list)


def test(p1,p2):
    print "from", p1, "to", p2, " -> ", relpath(p1, p2)

if __name__ == '__main__':
    test('/a/b/c/d', '/a/b/c1/d1')
    test('./test', '/home/rspoerri/')
    test('/home/_PROJECTS/_PROGRAMMING/_P3D_EDITOR/eggEditor-cvs/panda3d-editor/terrain.png', '/home/_PROJECTS/_PROGRAMMING/_P3D_EDITOR/eggEditor-cvs/panda3d-editor/examples/models/plants/shrubbery.egg')
    test('/home/_PROJECTS/_PROGRAMMING/_P3D_EDITOR/eggEditor-cvs/panda3d-editor/', '/home/_PROJECTS/_PROGRAMMING/_P3D_EDITOR/eggEditor-cvs/panda3d-editor/examples/models/plants/shrubbery.egg')
    test('/home/_PROJECTS/_PROGRAMMING/_P3D_EDITOR/eggEditor-cvs/panda3d-editor/terrain.png', '/home/_PROJECTS/_PROGRAMMING/_P3D_EDITOR/eggEditor-cvs/panda3d-editor/examples/models/plants/')


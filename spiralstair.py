import maya.cmds as mc
import functools

def createUI(pWinTitle, pApply):
    winID = "spiralst"

    if mc.window(winID, exists = True):
        mc.deleteUI(winID)

    mc.window(winID, title = pWinTitle, sizeable = False, resizeToFitChildren = True)
    mc.rowColumnLayout(numberOfColumns = 3, columnWidth = [[1,75],[2,60],[3,60]], columnOffset = [[1,'right',3]])

    #row 1
    mc.text('Height Range')
    hm = mc.floatField(value = 0)
    hM = mc.floatField(value = 20)

    hr = [hm,hM]

    #row 2
    mc.text('Turns')
    nt = mc.intField(value = 3)
    mc.separator(h = 10, style = 'none')

    #row 3
    mc.text('Radius')
    r = mc.floatField(value = 1)
    mc.separator(h = 10, style = 'none')

    #row 4
    mc.text('Steps')
    st = mc.intField(value = 50)
    mc.separator(h=10, style = 'none')

    #blank row
    mc.separator(h=10, style = 'none')
    mc.separator(h=10, style = 'none')
    mc.separator(h=10, style = 'none')

    def cancel(*pArgs):
        if mc.window(winID, exists=True):
            mc.deleteUI(winID)

    #buttons
    mc.separator(h=10, style = 'none')
    mc.button(label = 'Apply', command = functools.partial(pApply, hr, nt, r, st))
    mc.button(label = 'Cancel', command = cancel)

    mc.showWindow()

def pieslice(pStAn, pEnAn, pR, pH = 0.1):
    cyl = mc.polyCylinder(h = pH, r = pR)
    cx = mc.objectCenter(x = True)
    cy = mc.objectCenter(y = True)
    cz = mc.objectCenter(z = True)

    h = pH
    cut = mc.polyCut(cyl, 
               cutPlaneCenter = [cx,h/2,cz],
               cutPlaneRotate = [0,pStAn,0],
               extractFaces = True, 
               extractOffset = [0,0,0])
    cut = mc.polyCut(cyl, 
               cutPlaneCenter = [cx,h/2,cz],
               cutPlaneRotate = [0,pEnAn,0],
               extractFaces = True, 
               extractOffset = [0,0,0])
    obj = mc.polySeparate(cyl)
    names = []
    for i in range(len(obj)):
        mc.rename(obj[i],'part'+str(i))
        names.append('part'+str(i))   
         
    mc.delete(names[0:2] + names[3:], s=True)
    mc.polyCloseBorder(names[2])
    myBlinn = mc.shadingNode('blinn', asShader = True)
    mc.select(names[2])
    mc.hyperShade(assign = myBlinn)
    return names[2]



def spiralst(pNS, pH, pNT, pR):
    stepangle = float(pNT*360)/float(pNS)
    stepht = float(pH)/float(pNS)
    currentangle = 0
    currentht = 0
    stair = pieslice(stepangle+0.5, 0.5, pR, stepht/2)
    stairlist = [stair]
    for i in range(1,pNS):
        newstair = mc.duplicate(stair, n = "stair"+str(i))
        currentht += stepht
        currentangle+=stepangle
        mc.move(0,currentht,0,newstair)
        mc.rotate(0,currentangle,0,newstair)
        stairlist.append(newstair)
    spine = mc.polyCylinder(h = pH, r = 0.05)
    mc.move(0,pH/2,0, spine)
    stairlist.append(spine)
    staircase = mc.polyUnite(*stairlist, n = "spiralstairs")
    return staircase

def apply(pHr, pNT, pR, pS, *pArgs):
    hr = [mc.floatField(i, query = True, value = True) for i in pHr]
    nt = mc.intField(pNT, query = True, value = True)
    r = mc.floatField(pR, query = True, value = True)
    st = mc.intField(pS, query = True, value = True)

    staircase = spiralst(st,hr[1]-hr[0],nt,r)
    mc.move(0,hr[0],0,staircase)

createUI('Spiral Staircase Maker',apply)
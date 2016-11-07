import maya.cmds as mc
import functools

#function to create the UI for the script
#params - pWinTitle  - Title of the Window
#         pApply     - The function that's called on pressing the Apply button
#return - nothing
def createUI(pWinTitle, pApply):
    winID = "spiralst"

    if mc.window(winID, exists = True):
        mc.deleteUI(winID)

    mc.window(winID, title = pWinTitle, sizeable = False, resizeToFitChildren = True)
    mc.rowColumnLayout(numberOfColumns = 3, columnWidth = [[1,75],[2,60],[3,60]], columnOffset = [[1,'right',3]])

    #row 1 - obtaining the height range for the staircase
    mc.text('Height Range')
    hm = mc.floatField(value = 0)
    hM = mc.floatField(value = 20)
    
    #saving the height range as a list (min, max)
    hr = [hm,hM]

    #row 2 - obtaining the number of turns that the spiral staircase goes through
    mc.text('Turns')
    nt = mc.intField(value = 3)
    mc.separator(h = 10, style = 'none')

    #row 3 - obtaining the radius of the each stair
    mc.text('Radius')
    r = mc.floatField(value = 1)
    mc.separator(h = 10, style = 'none')

    #row 4 - obtaining the number of steps of the staircase
    mc.text('Steps')
    st = mc.intField(value = 50)
    mc.separator(h=10, style = 'none')

    #blank row
    mc.separator(h=10, style = 'none')
    mc.separator(h=10, style = 'none')
    mc.separator(h=10, style = 'none')
    
    #cancel callback
    def cancel(*pArgs):
        if mc.window(winID, exists=True):
            mc.deleteUI(winID)

    #buttons - apply calls the pApply callback using a partial function
    mc.separator(h=10, style = 'none')
    mc.button(label = 'Apply', command = functools.partial(pApply, hr, nt, r, st))
    mc.button(label = 'Cancel', command = cancel)
    
    #display the window
    mc.showWindow()

#to make ONE stair
#params - pStAn - Start Angle of pieslice,
#         pEnAn - End Angle of pieslice
#         pR    - Radius of pieslice
#         pH    - Height of pieslice
#return - name of the pieslice that's created
def pieslice(pStAn, pEnAn, pR, pH = 0.1):
    cyl = mc.polyCylinder(h = pH, r = pR)
    cx = mc.objectCenter(x = True)
    cy = mc.objectCenter(y = True)
    cz = mc.objectCenter(z = True)

    h = pH
    #cut the cylinder, and separate different parts
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
    
    #delete useless parts from the now separated cylinder     
    mc.delete(names[0:2] + names[3:], s=True)
    #fill hole of the leftover pieslice
    mc.polyCloseBorder(names[2])
    #add and assign a material (which was deleted when delete was called)
    myBlinn = mc.shadingNode('blinn', asShader = True)
    mc.select(names[2])
    mc.hyperShade(assign = myBlinn)
    return names[2]


#function to make the spiral staircase
#params - pNS - Number of stairs
#         pH  - Height of staircase
#         pNT - Number of turns
#         pR  - Radius of stair
#return - the staircase object
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

#apply callback
#params - pHr - Height range (list of 2)
#         pNT - Number of turns
#         pR  - Radius of a stair
#         pS  - Number of stairs
#return - nothing
def apply(pHr, pNT, pR, pS, *pArgs):
    #obtain the values from the UI
    hr = [mc.floatField(i, query = True, value = True) for i in pHr]
    nt = mc.intField(pNT, query = True, value = True)
    r = mc.floatField(pR, query = True, value = True)
    st = mc.intField(pS, query = True, value = True)
    #generate the staircase
    staircase = spiralst(st,hr[1]-hr[0],nt,r)
    #move the staircase to the correct initial point
    mc.move(0,hr[0],0,staircase)

#create and display the UI
createUI('Spiral Staircase Maker',apply)

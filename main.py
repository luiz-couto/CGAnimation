from OpenGL.GL import *
import sys
import struct
from PIL import Image
import numpy
import re
from codecs import decode

import ctypes

import OpenGL.GL.shaders
import glfw
import glm
from OpenGL.GLU import *
from OpenGL.GLUT import *


NUMVERTEXNORMALS = 162
SHADEOUT_QUANT = 16
MAX_ANIMATIONS = 22
anorms = []
anorms_dots = []

m_vertices      = []
m_glcmds        = []
m_lightnormals  = []

m_currentTime = 0
m_lastTime = 0

num_frames      = 0
num_xyz         = 0
num_glcmds      = 0

animlist = []

m_texid         = 0
m_scale         = 1.0


class md2_t:
    def __init__(self,content):
        self.ident = int.from_bytes(content[0:4],"little")
        self.version = int.from_bytes(content[4:8],"little")
        
        self.skinwidth = int.from_bytes(content[8:12],"little")
        self.skinheight = int.from_bytes(content[12:16],"little")
        self.framesize = int.from_bytes(content[16:20],"little")

        self.num_skins = int.from_bytes(content[20:24],"little")
        self.num_xyz = int.from_bytes(content[24:28],"little")
        self.num_st = int.from_bytes(content[28:32],"little")
        self.num_tris = int.from_bytes(content[32:36],"little")
        self.num_glcmds = int.from_bytes(content[36:40],"little")
        self.num_frames = int.from_bytes(content[40:44],"little")

        self.ofs_skins = int.from_bytes(content[44:48],"little")
        self.ofs_st = int.from_bytes(content[48:52],"little")
        self.ofs_tris = int.from_bytes(content[52:56],"little")
        self.ofs_frames = int.from_bytes(content[56:60],"little")
        self.ofs_glcmds = int.from_bytes(content[60:64],"little")
        self.ofs_end = int.from_bytes(content[64:68],"little")

class vertex_t:
    def __init__(self,content):
        self.v = [content[0],content[1],content[2]]
        self.lightnormalindex = content[3]

class frame_t:
    def __init__(self,content):
        x = struct.unpack('f',content[0:4])
        x = float(x[0])
        y = struct.unpack('f',content[4:8])
        y = float(y[0])
        z = struct.unpack('f',content[8:12])
        z = float(z[0])
        self.scale = [x,y,z]
        x = struct.unpack('f',content[12:16])
        x = float(x[0])
        y = struct.unpack('f',content[16:20])
        y = float(y[0])
        z = struct.unpack('f',content[20:24])
        z = float(z[0])
        self.translate = [x,y,z]
        self.name = content[24:40].decode("utf-8")
        self.verts = []
        aux = 40
        for i in range(num_xyz):
            vertex = vertex_t(content[aux:aux+4])
            self.verts.append(vertex)
            aux = aux + 4

class anim_t:
    def __init__(self,first,last,fps):
        self.first_frame = first
        self.last_frame = last
        self.fps = fps

class animState_t:
    def __init__(self):
        self.startframe = 0
        self.endframe = 0
        self.fps = 0

        self.curr_time = 0.0
        self.old_time = 0.0
        self.interpol = 0.0

        self._type = 0

        self.curr_frame = 0
        self.next_frame = 0



def LoadModel(filename):
   
    f = open(filename,"rb")
    content = f.read()
    
    # Verify if its a .md2 file
    if(content[0:4] != b'IDP2') or (int.from_bytes(content[4:8],"little") != 8):
        print("It's not a .md2 file!")
        return

    # Read header file
    header_content = content[0:69]
    header = md2_t(header_content)
    
    # Initialize member variables
    global num_xyz
    global num_frames
    global num_glcmds
    num_frames = header.num_frames
    num_xyz = header.num_xyz
    num_glcmds = header.num_glcmds

    # Read file data
    #buffer = content[header.ofs_frames:num_frames*header.framesize]
    buffer = content[header.ofs_frames:header.ofs_frames+(num_frames*header.framesize)]
    global m_glcmds
    m_glcmds = content[header.ofs_glcmds:header.ofs_glcmds+num_glcmds*4]
  
    w,h = 3,num_frames
    
    global m_vertices
    global m_lightnormals

    
    #frame = frame_t(buffer[header.framesize * 0:])
    #print(float(frame.scale[0])*frame.verts[0].v[0] + frame.translate[0])
   
   
    for j in range(0,num_frames):
        frame = frame_t(buffer[header.framesize * j:])
        for i in range(0,num_xyz):
            m_vertices.append([((frame.verts[i].v[0] * frame.scale[0]) + frame.translate[0]),((frame.verts[i].v[1] * frame.scale[1]) + frame.translate[1]),((frame.verts[i].v[2] * frame.scale[2]) + frame.translate[2])])
            m_lightnormals.append(frame.verts[i].lightnormalindex)
            
    #print(m_vertices[78][0])
    #print(frame.verts[5].v)

def LoadSkin(filename):
    # this function: credits to http://www.magikcode.com/?p=122
    # PIL can open BMP, EPS, FIG, IM, JPEG, MSP, PCX, PNG, PPM
    # and other file types.  We convert into a texture using GL.
    print('trying to open', filename)
    try:
        image = Image.open(filename)
    except IOError as ex:
        print('IOError: failed to open texture file')
        message = template.format(type(ex).__name__, ex.args)
        print(message)
        return -1
    print('opened file: size=', image.size, 'format=', image.format)
    imageData = numpy.array(list(image.getdata()), numpy.uint8)

    textureID = glGenTextures(1)
    #glBindTexture(GL_TEXTURE_2D, textureID)
    

    glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

    gluBuild2DMipmaps( GL_TEXTURE_2D, GL_RGBA, image.size[0], image.size[1], GL_RGBA, GL_UNSIGNED_BYTE, imageData )
    
    #image.close()
    return textureID

def DrawModel(time):
    #print(time)
    if(time > 0.0):
        Animate(time)
    
    glPushMatrix()
    
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    glRotatef(-90.0, 0.0, 0.0, 1.0)

    RenderFrame()
    glPopMatrix()

def ScaleModel(s):
    global m_scale
    m_scale = s

def Interpolate(vertlist):

    curr_v = m_vertices[num_xyz * m_anim.curr_frame:]
    next_v = m_vertices[num_xyz * m_anim.next_frame:]

    #for i in range(0,num_xyz):
       #vertlist[i][0] = (curr_v[i][0] + m_anim.interpol * (next_v[i][0] - curr_v[i][0])) * m_scale
       #vertlist[i][1] = (curr_v[i][1] + m_anim.interpol * (next_v[i][1] - curr_v[i][1])) * m_scale
       #vertlist[i][2] = (curr_v[i][2] + m_anim.interpol * (next_v[i][2] - curr_v[i][2])) * m_scale

    for i in range(0,num_xyz):
        x = [(curr_v[i][0] + m_anim.interpol * (next_v[i][0] - curr_v[i][0])) * m_scale,(curr_v[i][1] + m_anim.interpol * (next_v[i][1] - curr_v[i][1])) * m_scale,(curr_v[i][2] + m_anim.interpol * (next_v[i][2] - curr_v[i][2])) * m_scale]
        vertlist.append(x)

    return vertlist



def PopulateAnorms(filename):
    f = open(filename,"r")
    content = f.readlines()
    global anorms
    for i in range(0,NUMVERTEXNORMALS):
        anorms.append([float(content[i][2:11]),float(content[i][14:23]),float(content[i][26:35])])

def PopulateAnormsDots(filename):
    f = open(filename,"r")
    content = f.read()
    global anorms_dots
    aux = content.split('\n')

    for j in range(0,SHADEOUT_QUANT):
        aux[j] = aux[j].replace('{ ','')
        aux[j] = aux[j].replace(' }','')
        aux[j] = aux[j].replace(', ','')
        k = 0
        y = [] # auxiliar
        for i in range(0,256):
            x = float(aux[j][k:k+4])
            y.append(x)
            k = k+4
        anorms_dots.append(y)
        

g_lightcolor = [1.0,1.0,1.0]
g_ambientlight = 32
g_shadelight = 128
g_angle = 0.0
lcolor = [0,0,0]
shadedots = anorms_dots[0:]

def ProcessLighting():
    lightvar = (g_shadelight + g_ambientlight)/256.0

    global lcolor
    lcolor[0] = (g_lightcolor[0]*lightvar)
    lcolor[1] = (g_lightcolor[1]*lightvar)
    lcolor[2] = (g_lightcolor[2]*lightvar)

    global shadedots
    shadedots = anorms_dots[int((g_angle * (SHADEOUT_QUANT / 360.0))) & (SHADEOUT_QUANT - 1):]


def IntToFloat(number):
    s = bin(number)
    q = int(s,0)
    b8 = struct.pack('<i',q)
    f = struct.unpack('<f',b8)[0]
    return f

def RenderFrame():
    vertlist = []

    # Reverse the orientation of front-facing
    glPushAttrib(GL_POLYGON_BIT)
    glFrontFace(GL_CW)
   
    # Enable backface culling
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)

    ProcessLighting()

    vertlist = Interpolate(vertlist)

    global m_texid
    glBindTexture(GL_TEXTURE_2D,m_texid)

    c = 0
    aux = []
    for d in range(int(len(m_glcmds)/4)):
        aux.append(int.from_bytes(m_glcmds[c:c+4],"little"))
        c = c+4


    k = 0
    i = ctypes.c_int(aux[k]).value
    
    while(i != 0):
        
        if(i > 0):
            glBegin(GL_TRIANGLE_STRIP)
        if(i < 0):
            glBegin(GL_TRIANGLE_FAN)
            i = -i
        
        for j in range(0,i):
            k = k+1
            l = shadedots[0][m_lightnormals[aux[k+2]]]
            glColor3f( l * lcolor[0], l * lcolor[1], l * lcolor[2] )
            glTexCoord2f(IntToFloat(aux[k]),IntToFloat(aux[k+1]))
            glNormal3fv(anorms[m_lightnormals[aux[k+2]]])
            glVertex3fv(vertlist[aux[k+2]])
            k = k + 2

        k = k + 1
        glEnd()
        i = ctypes.c_int(aux[k]).value

    glDisable(GL_CULL_FACE)
    glPopAttrib()        



def PopulateAnimlist():
    global animlist
    animlist = [
        anim_t(0,39,9),
        anim_t(40,45,10),
        anim_t(46,53,10),
        anim_t(54,57,7),
        anim_t(58,61,7),
        anim_t(62,65,7),
        anim_t(66,71,7),
        anim_t(72,83,7),
        anim_t(84,94,7),
        anim_t(95,111,10),
        anim_t(112,122,7),
        anim_t(123,134,6),
        anim_t(135,153,10),
        anim_t(154,159,7),
        anim_t(160,168,10),
        anim_t(196,172,7),
        anim_t(173,177,5),
        anim_t(178,183,7),
        anim_t(184,189,7),
        anim_t(190,197,7),
        anim_t(198,198,5)
    ]

m_anim = animState_t()
c_anim = 0

def SetAnim(_type):
    global m_anim
    if(_type < 0) or (_type > MAX_ANIMATIONS):
        _type = 0
    
    m_anim.startframe   = animlist[ _type ].first_frame
    m_anim.endframe     = animlist[ _type ].last_frame
    m_anim.next_frame   = animlist[ _type ].first_frame + 1
    m_anim.fps          = animlist[ _type ].fps
    m_anim._type        = _type


def Animate(time):
    global m_anim
    m_anim.curr_time = time

    if(m_anim.curr_time - m_anim.old_time > (1.0/m_anim.fps)):
        
        m_anim.curr_frame = m_anim.next_frame
        m_anim.next_frame = m_anim.next_frame + 1

        if(m_anim.next_frame > m_anim.endframe):
            m_anim.next_frame = m_anim.startframe
        
        m_anim.old_time = m_anim.curr_time
    
    if( m_anim.curr_frame > (num_frames - 1) ):
        m_anim.curr_frame = 0
    
    if( m_anim.next_frame > (num_frames - 1) ):
        m_anim.next_frame = 0

    m_anim.interpol = m_anim.fps * (m_anim.curr_time - m_anim.old_time)


def DrawFrame(frame):
    global m_anim
    #set new animation parameters...
    m_anim.startframe   = frame
    m_anim.endframe     = frame
    m_anim.next_frame   = frame
    m_anim.fps          = 1
    m_anim._type        = -1

    #draw the model
    DrawModel( 1.0 )


def GetTimeMSec():
    return glutGet( GLUT_ELAPSED_TIME )

def GetTime():
    return m_currentTime

def GetFps():
    return float(1000.0)/(float(m_currentTime - m_lastTime))

def InitializeTime():
    global m_currentTime
    m_currentTime = GetTimeMSec()


def UpdateTime():
    global m_currentTime
    global m_lastTime
    m_lastTime = m_currentTime
    m_currentTime = GetTimeMSec()

    
bAnimated = True
g_angle = 1.0
angle = 2.0
bTextured = True
bLighGL	= True


def Display():
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    UpdateTime()
    timesec = GetTimeMSec()/1000.0

    global g_angle
    global angle

    if(g_angle > 360.0):
        g_angle = g_angle-360.0
    
    if(g_angle < 0):
        g_angle = g_angle+360.0
    
    if(angle < 0.0):
        angle = angle+360.0
    
    if(angle > 360.0):
        angle = angle-360.0
    
    glTranslatef(0.0,0.0,-25.0)
    glRotatef(angle,0.0,1.0,0.0)

    if(bAnimated == True):
        DrawModel(timesec)
    else:
        DrawModel(0.0)
    
    glutSwapBuffers()
    glutPostRedisplay()

def Reshape(width,height):
    #prevent division by zero
	if( height == 0 ):
		height = 1

	glViewport( 0, 0, width, height )

	#reset projection matrix
	glMatrixMode( GL_PROJECTION )
	glLoadIdentity()
	gluPerspective( 45.0, float(width)/float(height), 0.1, 100.0 )

	#reset model/view matrix
	glMatrixMode( GL_MODELVIEW )
	glLoadIdentity()

def to8(string):
    return as_8_bit(string)

def ChangeAnim():
    global c_anim
    c_anim = c_anim + 1
    if(c_anim == 20):
        c_anim = 0
    SetAnim( c_anim )


def Keyboard(key,x,y):
    global bAnimated
    global bLighGL
    global bTextured


    if (key == to8('a') or key == to8('A')):
        bAnimated =  not bAnimated
    elif (key == to8('l') or key == to8('L')):
        bLighGL = not bLighGL
        if(bLighGL):
            glEnable(GL_LIGHTING)
        else:
            glDisable(GL_LIGHTING)
       
    elif (key == to8('p') or key == to8('P')):
        glPolygonMode( GL_FRONT_AND_BACK, GL_POINT )
        
    elif(key == to8('s') or key == to8('S')):
        glPolygonMode( GL_FRONT_AND_BACK, GL_FILL )
        
    elif(key == to8('t') or key == to8('T')):
        bTextured = not bTextured
        if(bTextured):
            glEnable(GL_TEXTURE_2D)
        else:
            glDisable(GL_TEXTURE_2D)
        
    elif(key == to8('w') or key == to8('W')):
        glPolygonMode( GL_FRONT_AND_BACK, GL_LINE )
    elif(key == to8('c') or key == to8('C')):
        ChangeAnim()
    

        

def Special(key,x,y):

    global angle
    global g_angle

    if (key == GLUT_KEY_LEFT):
        angle -= 5.0
    elif (key == GLUT_KEY_RIGHT):
        angle += 5.0
    elif (key == GLUT_KEY_UP):
        g_angle -= 10.0
    elif(key == GLUT_KEY_DOWN):
        g_angle += 10.0
       


def Init():
    
    glClearColor(0.0,0.0,0.0,0.0)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
 
    InitializeTime()
    LoadModel("Models/Ogros.md2")
    global m_texid
    m_texid = LoadSkin("Models/igdosh.pcx")
    PopulateAnorms("lib/anorms.txt")
    PopulateAnormsDots("lib/anormtab.txt")
    PopulateAnimlist()

    SetAnim( c_anim )
    glDisable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    ScaleModel(0.25)
    
    lightpos = [10.0,10.0,100.0]
    lightcolor = [1.0,1.0,1.0,1.0]

    glLightfv( GL_LIGHT0, GL_POSITION, lightpos )
    glLightfv( GL_LIGHT0, GL_DIFFUSE, lightcolor )
    glLightfv( GL_LIGHT0, GL_SPECULAR, lightcolor )



def main():
    
    glutInit(sys.argv)
    glutInitDisplayMode( GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH )

    glutInitWindowSize( 640, 480 )

    glutInitWindowPosition( 100, 100 )

    glutCreateWindow( "CG Animation" )

    Init()

    glutKeyboardFunc( Keyboard )
    glutSpecialFunc( Special )
    glutReshapeFunc( Reshape )
    glutDisplayFunc( Display )

    glutMainLoop()

    
main()
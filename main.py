from OpenGL.GL import *
import sys
import struct
from PIL import Image
import numpy
import re


NUMVERTEXNORMALS = 162
SHADEOUT_QUANT = 16
anorms = []
anorms_dots = []

m_vertices      = []
m_glcmds        = 0
m_lightnormals  = []

num_frames      = 0
num_xyz         = 0
num_glcmds      = 0

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
    m_glcmds = content[header.ofs_glcmds:header.ofs_glcmds+num_glcmds*4]
    
    
    w,h = 3,num_frames
    
    global m_vertices
    global m_lightnormals

    frame = frame_t(buffer[header.framesize * 0:])
    #print(float(frame.scale[0])*frame.verts[0].v[0] + frame.translate[0])
    
   
    for j in range(0,num_frames):
        frame = frame_t(buffer[header.framesize * j:])
        for i in range(0,num_xyz):
            m_vertices.append([((frame.verts[i].v[0] * frame.scale[0]) + frame.translate[0]),((frame.verts[i].v[1] * frame.scale[1]) + frame.translate[1]),((frame.verts[i].v[2] * frame.scale[2]) + frame.translate[2])])
            m_lightnormals.append(frame.verts[i].lightnormalindex)
            
    print(m_vertices[78][0])
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
    glPixelStorei(GL_UNPACK_ALIGNMENT, 4)
    glBindTexture(GL_TEXTURE_2D, textureID)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.size[0], image.size[1],
        0, GL_RGB, GL_UNSIGNED_BYTE, imageData)

    image.close()
    return textureID

def DrawModel(time):
    glPushMatrix()
    
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    glRotatef(-90.0, 0.0, 0.0, 1.0)

    RenderFrame()
    glPopMatrix()

def Interpolate(vertlist):
    for i in range(0,num_xyz):
        vertlist[i][0] = m_vertices[ i + (num_xyz * m_anim.curr_frame) ][0] * m_scale
        vertlist[i][1] = m_vertices[ i + (num_xyz * m_anim.curr_frame) ][1] * m_scale
        vertlist[i][2] = m_vertices[ i + (num_xyz * m_anim.curr_frame) ][2] * m_scale

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
    #anorms_dots = re.split('{ | } ',content)
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

    lcolor[0] = (g_lightcolor[0]*lightvar)
    lcolor[1] = (g_lightcolor[1]*lightvar)
    lcolor[2] = (g_lightcolor[2]*lightvar)

    global shadedots
    shadedots = anorms_dots[(g_angle * (SHADEOUT_QUANT / 360.0)) & (SHADEOUT_QUANT - 1):]
    


def main():
    LoadModel("Weapon.md2")
    global m_texid
    m_texid = LoadSkin("Weapon.pcx")
    PopulateAnorms("anorms.txt")
    PopulateAnormsDots("anormtab.txt")
    
main()
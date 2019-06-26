from OpenGL.GL import *

m_vertices      = 0
m_glcmds        = 0
m_lightnormals  = 0

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
    num_frames = header.num_frames
    num_xyz = header.num_xyz
    num_glcmds = header.num_glcmds

    # Read file data
    buffer = content[header.ofs_frames:num_frames*header.framesize]
    m_glcmds = content[header.ofs_glcmds:num_glcmds*4]

def main():
    LoadModel("Weapon.md2")
main()
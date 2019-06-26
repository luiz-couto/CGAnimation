from OpenGL.GL import *

# Converts a byte object to an integer
def bytes_to_int (input_bytes):
    isinstance(input_bytes, bytes) or exit (99)
    if (len(input_bytes) == 0): return 0
    (input_bytes[0] <= 0x80) or exit (98)

    shift = i1 = 0
    for p in range(1, len(input_bytes)+1):
        i1 += (input_bytes[-p] << shift)
        shift += 8

    return i1


def LoadModel(filename):
   
    f = open(filename,"rb")
   
    # Verify if its a .md2 file
    content = f.read(64)
    print(bytes_to_int(b'\x80\x00\x00\x00'))
    if(content[0:4] == b'IDP2') and (bytes_to_int(content)):
        print("TRUE")





def main():
    LoadModel("Weapon.md2")
main()
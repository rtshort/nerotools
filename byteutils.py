from math import ceil

#------------------------------------------------------------
# Utility routines to read and write common file structures.

def printInHex(nradata, end=''):
    print( nradata.hex(), end=end )
    
def printInText(nradata, end='\n'):
    print( ''.join([chr(b) if ( (b>=32)&(b<127) ) else '.' for b in nradata]), end=end )
    
def printInHexAndText(nradata, end='\n'):
    printInHex(nradata, end=' | ')
    printInText(nradata, end=end)

def printInChunks(nradata, chunksize=8):
    nbytes = len(nradata)
    chunksize = 8
    nchunks = ceil(nbytes/chunksize)
    for chunk in range(nchunks):
        printInHexAndText(nradata[chunk*chunksize:(chunk+1)*chunksize])

def printNextBytes(nradata, position, nbytes=10):
    print('Next bytes at position',position, '%x'%position)
    printInHexAndText(nradata[position:position+nbytes])

# nbyte byte ints encoded little endian.
def readInt(nradata, position=0, nbytes=4):
    myint = 0
    for pos in range(position+nbytes-1,position-1,-1):
        myint = 256*myint+nradata[pos]
    position = position + nbytes
    return position, myint

# Each "short text" string begins with a preamble 0xfffeff.
# I think the 0xfffe is a unicode byte order marker.  I
# don't think the 0xff is part of the unicode structure.
# Following the preamble is a 1 byte length.
def readShortText(nradata, position):
    bom = nradata[0:2]
    position = position + 3
    cnt = nradata[position]
    position = position + 1
    bts = bom + nradata[position:position+2*cnt]
    text = bts.decode('utf-16')
    position += 2*cnt
    return position, text

# Long text is in the same encoding as short text, but
# there is no byte order marker and the length field is
# a 4 byte int.
def readLongText(nradata, position):
    position,cnt = readInt(nradata,position)
    bts = bytearray(nradata[position:position+2*cnt])
    text = bts.decode('utf-16')
    position += 2*(cnt+1) # Eat the trailing c-style zero bytes.
    return position, text

def writeInt(value, nbytes=4):
    outbytes = bytearray(nbytes)
    for idx in range(nbytes):
        outbytes[idx] = value & 0xff
        value = value >> 8
    return bytes(outbytes)

def writeShortString(strng):
    strbytes = strng.encode('utf-16')
    encoding    = strbytes[0:2]
    lengthfield = bytearray(2)
    lengthfield[0] = 0xff
    lengthfield[1] = len(strng)
    strfield    = strbytes[2:]

    return encoding + lengthfield + strfield

def writeLongString(strng):
    strbytes = strng.encode('utf-16')
    lengthfield = writeInt(len(strng))

    return lengthfield + strbytes[2:] + b'\x00\x00'


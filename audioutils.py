"""
Routines to read and manipulate audio files.
"""

import sys
from byteutils import printInHexAndText, readInt

def readWavefileHeader(filename):
    """
    Read a wavefile header.  Return a dictionary with the parameters.
    
    """

    waveheader = {}
    with open(filename, 'rb') as file:

        riffhdr  = file.read(4)
        if (riffhdr != b'RIFF'):
            print(filename, 'is not a RIFF file', file=sys.stderr)
            raise ValueError

        p,whdrlength = readInt(file.read(4))

        hdrbytes = file.read(whdrlength)
        
        wavehdr = hdrbytes[0:4]
        if (wavehdr == b'WAVE'):
            hdrbytes = hdrbytes[4:]
        else:
            print(filename, 'is not a WAVE file', file=sys.stderr)
            raise ValueError

        # The format section begins with the string 'fmt ' and describes the
        # format of the file.  I am only interested in PCM encoded audio
        # data so I bail out if it is anything else.

        fmtstring = hdrbytes[0:4]
        if (fmtstring!=b'fmt '):
            print('This is not a PCM file', file=sys.stderr)
            raise ValueError
        hdrbytes = hdrbytes[4:]
    
        pos,dhdrlength = readInt(hdrbytes)
        hdrbytes = hdrbytes[pos:]
    
        pos,pcm = readInt(hdrbytes,0,2)
        if (pcm!=1):
            print('This is not a PCM file', file=sys.stderr)
            raise ValueError

        pos,channels = readInt(hdrbytes,pos,2)
        pos,rate = readInt(hdrbytes,pos,4)
        pos,byterate = readInt(hdrbytes,pos,4)
        pos,bytespersample = readInt(hdrbytes,pos,2)
        pos,bps = readInt(hdrbytes,pos,2)
        data = hdrbytes[pos:pos+4]
        pos = pos+4
        if (data != b'data'):
            print('There is no data section', file=sys.stderr)
            raise ValueError
        pos,nbytes = readInt(hdrbytes,pos,4)

        waveheader["channels"] = channels
        waveheader["rate"] = rate
        waveheader["byterate"] = byterate
        waveheader["bytespersample"] = bytespersample
        waveheader["bitsperchannel"] = bps
        waveheader["nbytes"] = nbytes

    return waveheader


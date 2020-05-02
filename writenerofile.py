#!/usr/bin/python3

"""

Routine and tests to write a Nero project (.nra) file.

Written by Robert T. Short.


""" 

import argparse
from math import ceil

from byteutils import writeInt, writeShortString, writeLongString
from audioutils import readWavefileHeader
from cdutils import Album, Disc, Track

def writeNeroFile(album, discno=1):

    # Initialize a buffer that we will fill with the nra data.

    position = 0
    outbytes = bytearray()

    # Fixed CD and track options.
    header     = 'NeroCDAV8.0.0'

    cd_options = [0,0,1,1,9,0,0]

    hex_value = b'\x0a\x00\x00\x80\x0b\xee\x20\x5e\x00\x00\x00\x00'

    global_track_options = [0,0,1]

    gulptag = b'GULP'
    busttag = b'BUST'

    track_protection = 0x40
    filter_bytes     = b'ENON\x08\x00\x00\x00' + b'\x00'*8
    mystery_bytes1   = b'\x00'*14
    mystery_bytes2   = b'\x00'*4
    mystery_str1   = ""
    mystery_str2   = ""
    
    burn_options     = [120,0,1,1,1,0,0,1,1,0,0,65536,65535,0,0,1,0,1,0,0,0,0,0,0,1,0,0]
    burn_tail        = b'\xff'*4 + b'\00'*4

    num_tracks = len(album.discs[discno-1].tracks)

    # Do the header.

    headerbytes = writeShortString(header)
    nextpos = position + len(headerbytes)
    outbytes = outbytes + headerbytes
    position = nextpos

    # The track options count field.
    cnt = 40 + 4*num_tracks
    cntbytes = writeInt(cnt)
    nextpos = position + len(cntbytes)
    outbytes = outbytes + cntbytes
    position = nextpos

    # CD Text.

    cdtextbytes = writeShortString(album.title)
    nextpos = position + len(cdtextbytes)
    outbytes = outbytes + cdtextbytes
    position = nextpos

    cdtextbytes = writeShortString(album.artist)
    nextpos = position + len(cdtextbytes)
    outbytes = outbytes + cdtextbytes
    position = nextpos

    cdtextbytes = writeShortString(album.copyright)
    nextpos = position + len(cdtextbytes)
    outbytes = outbytes + cdtextbytes
    position = nextpos

    cdtextbytes = writeShortString(album.author)
    nextpos = position + len(cdtextbytes)
    outbytes = outbytes + cdtextbytes
    position = nextpos

    cdtextbytes = writeShortString(album.mcn)
    nextpos = position + len(cdtextbytes)
    outbytes = outbytes + cdtextbytes
    position = nextpos

    cdtextbytes = writeShortString(album.rdate)
    nextpos = position + len(cdtextbytes)
    outbytes = outbytes + cdtextbytes
    position = nextpos

    cdtextbytes = writeShortString(album.comment)
    nextpos = position + len(cdtextbytes)
    outbytes = outbytes + cdtextbytes
    position = nextpos

    # The global CD and track options.
    outbytes = outbytes + b'\x00'
    position = position + 1

    for option in cd_options:
        optbytes = writeInt(option)
        nextpos = position + 4
        outbytes = outbytes + optbytes
        position = nextpos

    trkbytes = writeInt(num_tracks)
    nextpos = position + 4
    outbytes = outbytes + trkbytes
    position = nextpos

    for cnt in range(num_tracks):
        optbytes = writeInt(1)
        nextpos = position + 4
        outbytes = outbytes + optbytes
        position = nextpos

    nextpos = position + len(hex_value)
    outbytes = outbytes + hex_value
    position = nextpos

    for option in global_track_options:
        optbytes = writeInt(option)
        nextpos = position + 4
        outbytes = outbytes + optbytes
        position = nextpos

    outbytes = outbytes + b'\x00'
    position = position + 1
    outbytes = outbytes + b'\x00'
    position = position + 1

    # Track info.

    trkbytes = writeInt(num_tracks)
    nextpos = position + 4
    outbytes = outbytes + trkbytes
    position = nextpos

    frames_per_second = 75
    silence_time = 2
    last_frame = 0
    for trackno,track in enumerate(album.discs[discno-1].tracks):

        full_file_name = track.file_name
        file_name      = full_file_name[full_file_name.rfind('\\')+1:]
        track_artist   = track.artist_name
        track_title    = track.track_name
        track_isrc     = track.isrc

        real_file_name = track.linux_file_name

        track_bytes = writeLongString(full_file_name)
        track_bytes = track_bytes + writeLongString(mystery_str1)
        track_bytes = track_bytes + writeLongString(file_name)
        track_bytes = track_bytes + writeLongString(track_artist)
        track_bytes = track_bytes + writeLongString(track_title)
        track_bytes = track_bytes + writeLongString(mystery_str2)
        track_bytes = track_bytes + writeLongString(track_isrc)

        trklength = [0,0,0,0,0,0,0]
        wavehdr = readWavefileHeader(real_file_name)
        trklength[2] = ceil(frames_per_second*wavehdr["nbytes"]/wavehdr["byterate"])-1
        trklength[4] = ceil(frames_per_second*silence_time)
        trklength[6] = last_frame + trklength[4]
        trklength[5] = trklength[6] + trklength[2]
        last_frame = trklength[5]
        for tl in trklength:
            track_bytes = track_bytes + writeInt(tl)

        track_bytes = track_bytes + writeInt(trackno+1,2)
        track_bytes = track_bytes + writeInt(track_protection)
        track_bytes = track_bytes + filter_bytes
        track_bytes = track_bytes + mystery_bytes1
        track_bytes = track_bytes + writeLongString(full_file_name)
        track_bytes = track_bytes + mystery_bytes2

        nextpos = position + len(gulptag)
        outbytes = outbytes + gulptag
        position = nextpos

        lenbytes = writeInt(len(track_bytes))
        nextpos = nextpos + 4
        outbytes = outbytes + lenbytes
        position = nextpos
    
        nextpos = position + len(track_bytes)
        outbytes = outbytes + track_bytes
        position = nextpos

    # Burn info
    nextpos = position + 4
    outbytes = outbytes + busttag
    position = nextpos

    for option in burn_options:
        optbytes = writeInt(option)
        nextpos = position + 4
        outbytes = outbytes + optbytes
        position = nextpos

    nextpos = position + len(burn_tail)
    outbytes = outbytes + burn_tail
    position = nextpos


    return outbytes

if __name__ == '__main__':

    # Get the file name.

    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Nero nra file name", \
                        nargs="?", default="Output.nra")
    args = parser.parse_args()
    filename = args.filename
    print('File:',filename)


    # Define the CD data.

    num_tracks = 3

    # Chords
    #  Note that the full_file_name should contain the complete Windows file name. 
    #  For example C:\Users\whodis\Music\xxx.wav
    full_file_name = ["00Samples\\CChord.wav",
                      "00Samples\\FChord.wav",
                      "00Samples\\GChord.wav"]
    linux_file_name = ["00Samples/CChord.wav",
                       "00Samples/FChord.wav",
                       "00Samples/GChord.wav"]
    track_artist   = ["DB1","DB2",""]
    track_title    = ["CChord","FChord","GChord"]
    track_isrc     = ["USK401402290","USK401402291","USK401402292"]

    album = Album('Chords')
    album.artist    = 'Doctor Bob'
    album.copyright = '12/08/2019'
    album.author    = 'R. T. Short'
    album.mcn       = '123456789012 '
    album.rdate     = '01/16/2020'
    album.comment   = 'No comment'
    album.discs.append(Disc('disc 1'))

    for trackno in range(num_tracks):
        track = Track()
        track.fileName(full_file_name[trackno])
        track.linuxFileName(linux_file_name[trackno])
        track.artistName(track_artist[trackno])
        track.trackName(track_title[trackno])
        track.ISRC(track_isrc[trackno])
        album.discs[0].tracks.append(track)

    outbytes = writeNeroFile(album, discno=1)

    # Write the output to files.

    with open(filename, 'wb') as file:
        file.write(outbytes)

    

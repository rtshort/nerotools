#!/usr/bin/python3

"""
Read and interpret a Nero project file (.nra file).

This exists for the purpose of trying to understand the .nra file
format and as such is really noisy.  Prints everything out.

Written by Robert T. Short.

"""

import sys
import argparse
from math import ceil

from cdutils import Track, Disc, Album
from byteutils import printInHexAndText, readInt, readShortString, readLongString
from byteutils import printInChunks, printNextBytes

#------------------------------------------------------------
# Routine to step through a .nra file piece by piece.

def readNeroFile(filename):

    # read the file into a buffer.

    nradata  = open(filename, "rb").read()
    position = 0

    # Nero header.  See below for encoding of "short text".
    # I have only looked at audio CD projects so far.
    position,header = readShortString(nradata, position)
    if (header != 'NeroCDAV8.0.0'):
        print( 'invalid header' )
        sys.exit()

    album = Album()

    print()
    print('------------------------------------------------------------')
    print('File', filename, 'is a Nero compilation file', 'with', len(nradata), 'bytes')

    # Integer byte field.  This seems to count from the end of
    # the CD options block (the beginning of the 32 bit int field that contains
    # the value 9) to the beginning of the track sections (the two byte field
    # containing zeros).
    position,track_option_length = readInt(nradata,position)
    print('Track options length', track_option_length, "(0x%x)"%track_option_length)

    # Parse the strings.  There are seven strings that are always present
    # but possibly empty.
    #  - CD title
    #  - CD artist
    #  - CD copyright
    #  - CD author
    #  - MCN
    #  - Date
    #  - Comment
    # Each string is preceded by 0xfffeff, then a 1 byte count (possibly zero).
    # The 0xffef is the unicode byte order marker.  The text (and everything
    # else) is little-endian.

    # Get the CD title and artist.
    # These are 16 bit characters.  No clue what encoding is used.
    # The format of this text seems to be 0x.. 0x00 where .. are
    # ASCII characters for all of the stuff I have tried.
    position,title = readShortString(nradata, position)
    print('CD Title', title)
    album.title = title

    position,artist = readShortString(nradata, position)
    print('CD Artist', artist)
    album.artist = artist

    position,copyright = readShortString(nradata, position)
    print('Copyright', copyright)
    album.copyright = copyright

    position,author = readShortString(nradata, position)
    print('Author', author)
    album.author = author

    position,mcn = readShortString(nradata, position)
    print('MCN', mcn)
    album.mcn = mcn

    position,rdate = readShortString(nradata, position)
    print('Date', rdate)
    album.rdate = rdate

    position,comment = readShortString(nradata, position)
    print('Comment', comment)
    album.comment = comment

    # The next group of bytes are global CD options (as opposed to track
    # options).  There seems to be a fixed number of bytes, followed by
    # the number of tracks and then by track_number ints followed by some
    # more stuff not necessarily of fixed length.

    # 28 bytes(14 short ints, 7 long ints) of CD options.  I think
    # these are 32 bit fields encoded as little endian ints.
    #
    # Offset 0x10 always contains 0x0009 and seems to be the last global CD
    # option and the remaining flags are global track options.  The
    # track_option_length variable above seems to be the number of bytes 
    # between the end of the 0x0009 and the count for the number of tracks.

    # In the following Offset is the offset in bytes from the end of the comment field.
    # offset   field
    # 00       Single byte. Always zero.
    # 01-04    A 32 bit integer.  Always 0.
    # 05-08    A 32 bit integer.  Always 0.
    # 09-0c    The write cd text to disc flag (32 bit integer).
    # 0d-10    A 32 bit integer.  Always 1.   
    # 11-14    A 32 bit integer.  Always 9.  The track_option_length starts at offset 0x11.
    # 15-18    A 32 bit integer.  Always 0.
    # 19-1c    A 32 bit integer.  Always 0.
    # 1d-20    A 32 bit integer.  The number of tracks, followed by track_number*(4 bytes).
    #          The track fields consist of a single 32 bit integer for each track
    #          The integer is always 1.
    #
    # In the following, Offset is from the end of the track fields.
    # 00       0x0a 
    # 03-0a    A large hex value
    # 0c-0f    32 bit int Normalize all tracks flag.
    # 10-13    32 bit int No pause between tracks flag
    # 14-17    32 bit int Remove silence at end of tracks.   
    # 18-19    zeros.  The track_option_length ends at offset 0x18.
    # 1a       32 bit int Number of tracks (again)

    # The track info starts with the tag "GULP".  The first "GULP"
    # is preceded by the number of tracks, and the number of tracks
    # follows the global CD and track options.

    # Find the first GULP tag.

    nextpos = nradata.find(b"GULP")-4
    nbytes = nextpos-position
    print(nbytes, "(0x%x) CD option bytes from"%nbytes, position, "to", nextpos-1)

    #  Raw dump of everything up to the tag.
    print('Bytes from end of comment to next GULP tag')
    printInChunks(nradata[position:nextpos])

    # Skip the single zero byte.
    print('Skipping byte with value',nradata[position], 'at position',position)
    position = position + 1

    print()
    print('Broken down CD options')
    intlist = []
    print( 'CD Options' )
    for cnt in range(0,5):
        position, myint = readInt(nradata, position)
        intlist += [myint]
        print( myint, end=" " )
    print()
    print('  -- "write cd text" is',intlist[2])
    print()

    global_track_position = position-4
    print("global_track_position", global_track_position, "(%x)"%global_track_position)

    intlist = []
    print( 'Global Track Options' )
    for cnt in range(2):
        position, myint = readInt(nradata, position)
        print( myint, end=" " )
        intlist.append(myint)
    print()
    position, num_tracks = readInt(nradata, position)
    print('number of tracks', num_tracks)
    intlist = []
    for cnt in range(num_tracks):
        position, myint = readInt(nradata, position)
        intlist += [myint]
        print( myint, end=" ")
    print()

    #  The hex value.
    print('The hex value')
    hexvalue = nradata[position:position+12]
    printInHexAndText(hexvalue)
    position = position + 12

    # More global track options.  Some of my newer projects have more bytes than the older ones.
    print('More global track options,', nextpos-2-position, 'bytes')
    intlist = []
    while position < nextpos-2:
        position, myint = readInt(nradata, position)
        intlist += [myint]
        print( myint, end=" " )
    print()
    if (len(intlist) > 0):
        print('  -- "normalize all tracks" is',intlist[0])
    else:
        print('  -- "normalize all tracks" is not present')
    if (len(intlist) > 1):
        print('  -- "No pause between tracks" is',intlist[1])
    else:
        print('  -- "No pause between tracks" is not present')
    if (len(intlist) > 2):
        print('  -- "Remove silence at end of tracks" is',intlist[2])
    else:
        print('  -- "Remove silence at end of tracks" is not present')
    print()


    # Swallow two bytes.
    print('End of global track options section', position, '(%x)'%position,
          'length', position-global_track_position)
    print('Skipping bytes with value',nradata[position:position+2],
          'at position',position,"(%x)"%position)
    position = position + 2

    # The next big chunk is track information.  At least up to the "BUST" tag.
    # Each track starts with a "GULP" tag.  The 32 bits preceding the GULP
    # tag the number of bytes up to the next section.

    # The beginning of the track section.
    print()
    print('Track section header')
    position, num_tracks_again = readInt(nradata, position)
    print('Number of tracks',num_tracks_again)

    for track_number in range(num_tracks_again):
        track = Track()
        album.tracks.append(track)
        
        print('Track number',track_number+1)

        track_header = nradata[position:position+4]
        position = position + 4
        position,cnt = readInt(nradata, position)
        next_section = position+cnt
        print('Track header', track_header, 'offset to next header', cnt, "(0x%x)"%cnt)
        print('bytes at next header',end=' ')
        printInHexAndText(nradata[next_section:next_section+8])

        #  The next chunk is track information.
        #  There are 7 strings.  Each string starts with a 32 bit count, is composed of
        #  16 bit chars (as in the CD section) and a 16 bit null trailer.

        # Full file name.
        position, full_file_name = readLongString(nradata,position)
        print('Full file name "',full_file_name,'"',sep='')

        # Empty string.
        position, empty_string = readLongString(nradata,position)
        print('Empty string "', empty_string, '"', sep='')

        # File name.
        position, file_name = readLongString(nradata,position)
        print('File name "', file_name, '"', sep='')

        # Artist
        position, artist = readLongString(nradata,position)
        print('Artist "', artist, '"', sep='')
        track.artistName(artist)

        # Track title
        position, track_title = readLongString(nradata,position)
        print('Track title "', track_title, '"', sep='')
        track.trackName(track_title)

        # Empty string.
        position, empty_string = readLongString(nradata,position)
        print('Empty string "', empty_string, '"', sep='')

        # ISRC
        position, isrc = readLongString(nradata,position)
        print('ISRC "', isrc, '"', sep='')
        track.ISRC(isrc)

        # The following are hex offsets from the end of the ISRC string.
        # Most of these are track times in (I think) CD-DA frames.  From 
        # brief internet scan, each frame is 588 bytes and the frame rate
        # is 75 frames/s.  I could be wrong about this but the numbers
        # work.
        # offset   field
        # 0 - 3    unknown
        # 4 - 7    unknown
        # 8 - b    Length of track.
        # c - f    unknown
        # 12-15    Length of silence prepended to track.
        # 16-19    Track start (frame at start of actual data not including silence)
        # 1a-1b    Track end (frame at end of actual data)
        # 1c-1d    2 byte track number.
        # 1e-21    Protection flag.  0x40 is no protection, 0x00 is protected.
        # 22       Filter field.  ENON is no filter.  The filter flag is
        #          followed by a 4 byte field length.

        print()
        print('Track length ints')
        intlist = []
        for cnt in range(7):
            position, myint = readInt(nradata, position)
            intlist += [myint]
            print( myint, end=" " )
        print()
        print('  -- "unknown" is',intlist[0], "(",intlist[0]/75.0,"s)")
        print('  -- "unknown" is',intlist[1], "(",intlist[1]/75.0,"s)")
        print('  -- "track length" is',intlist[2], "(",intlist[2]/75.0,"s)")
        print('  -- "unknown" is',intlist[3], "(",intlist[3]/75.0,"s)")
        print('  -- "silence time" is',intlist[4], "(",intlist[4]/75.0,"s)")
        print('  -- "track end" is',intlist[5], "(",intlist[5]/75.0,"s)")
        print('  -- "track start" is',intlist[6], "(",intlist[6]/75.0,"s)")
        print()
        position,trkno = readInt(nradata,position,2)
        position,protection = readInt(nradata,position)
        print('track number',trkno, 'protection',protection,'(%x)'%protection)

        print('Filter section')
        nextpos = position+4
        filter_tag = nradata[position:nextpos]
        print('filter tag', filter_tag)
        position = nextpos

        position,cnt = readInt(nradata,position)
        nextpos = position+cnt
        print(cnt, 'filter section bytes', end=' ')
        printInHexAndText(nradata[position:nextpos])
        position = nextpos

        nextpos = position+14
        print('mystery bytes ',end='')
        printInHexAndText(nradata[position:nextpos])
        position = nextpos

        position, full_file_name_again = readLongString(nradata,position)
        print('Full file name (again) "', full_file_name_again, '"', sep='')

        nextpos = position+4
        print('mystery bytes ',end='')
        printInHexAndText(nradata[position:nextpos], end='\n\n')
        position = nextpos

    # The final section contains options relating to the disc burning.
    #
    # After the BUST header and length field.
    #
    # offset  field
    #  0x10   Track at once/Disc at once
    #  0x1c   Write flag
    #  0x20   Finalize disc
    #
    #  There are some values that could be end-of-file flags, etc.

    burn_options_header = nradata[position:position+4]
    position = position + 4
    position,cnt = readInt(nradata, position)
    next_section = position+cnt
    print()
    print('Burn options header', burn_options_header, 'offset to next header', cnt, "(0x%x)"%cnt)
    print('Bytes from BUST tag to end of file')
    printInChunks(nradata[position:])

    print('Burn option ints')
    intlist = []
    for cnt in range(26):
        position, myint = readInt(nradata, position)
        intlist += [myint]
        print( "%x"%myint, end=" " )
    print()
    print('  -- "Disc at once" is',intlist[3])
    print('  -- "Write" is',intlist[6])
    print('  -- "Finalize disc" is',intlist[7])
    print()

    printNextBytes(nradata,position,8)

    return album

if __name__ == '__main__':

    # Get the file name, and open it

    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Nero nra file name",         \
                        nargs='?', default="00Samples/Chords.nra" )
    args = parser.parse_args()
    filename = args.filename

    album = readNeroFile(filename)
    print()
    print('-----------------------------------------------------------')
    album.printAlbum()

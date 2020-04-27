

class Track:
    def __init__(self):
        self.artist_name     = ''
        self.track_name      = ''
        self.album_name      = ''
        self.isrc            = ''
        self.file_name       = ''
        self.linux_file_name = ''
        self.track_count     = 0
        self.track_number    = 0
        self.disc_count      = 0
        self.disc_number     = 0
        self.track_year      = ''

    def __str__(self):
        return self.track_name
    def __repr__(self):
        return self.track_name
    def trackName(self,track_name):
        self.track_name = str(track_name)
    def artistName(self,artist_name):
        self.artist_name = str(artist_name)
    def albumName(self,album_name):
        self.album_name = str(album_name)
    def fileName(self,file_name):
        self.file_name = str(file_name)
    def linuxFileName(self,file_name):
        self.linux_file_name = str(file_name)
    def trackCount(self,track_count):
        self.track_count = int(track_count)
    def trackNumber(self,track_number):
        self.track_number = int(track_number)
    def discNumber(self,disc_number):
        self.disc_number = int(disc_number)
    def discCount(self,disc_count):
        self.disc_count = int(disc_count)
    def year(self,my_year):
        self.track_year = my_year
    def ISRC(self,isrc):
        self.isrc = str(isrc)
        
class Disc:
    def __init__(self,title):
        self.title  = title
        self.discno = 0
        self.tracks = []

    def __str__(self):
        return self.title
    def __repr__(self):
        return self.title

class Album:
    def __init__(self, title=''):
        self.title      = title
        self.artist     = ''
        self.copyright  = ''
        self.author     = ''
        self.mcn        = ''
        self.rdate      = ''
        self.comment    = ''
        self.disc_count = 0;
        self.discs      = []
        self.tracks     = []

    def __str__(self):
        return self.artist + ' ' + self.title
    def __repr__(self):
        return self.artist + ' ' + self.title

    def printAlbum(self):
        print(self.artist, ':', self.title)
        print('  ', 'copyright:      ', self.copyright)
        print('  ', 'author:         ', self.author)
        print('  ', 'mcn:            ', self.mcn)
        print('  ', 'recording date: ', self.rdate)
        print('  ', 'comment:        ', self.comment)
        for trackno, track in enumerate(self.tracks):
            print('  ', 'track number', trackno+1, ', title:', track.track_name)
            print('    ', 'composer:       ', track.artist_name)
            print('    ', 'ISRC:           ', track.isrc)
        

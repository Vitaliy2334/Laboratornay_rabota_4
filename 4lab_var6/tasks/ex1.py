import os
import argparse
import struct

class Sound:
    def __init__(self):
        self.author = ""
        self.name = ""
        self.album_name = ""
        self.tag = ""
        self.number = ""
        self.genre = 0

class Ex1:
    def __init__(self, path, bit=16):
        self.files = os.listdir(path=path)
        self.bit = bit
        self.path = path
        self.tracklist = []

    def decoding(self):
        print(self.files)
        for file in self.files:
            with open (os.path.join(self.path, file), 'rb') as file:
                file.seek(-128, 2)
                obj = file.read()
                sound = Sound()
                sound.tag, sound.name, sound.author, sound.album_name, sound.number, sound.genre = struct.unpack('<3s30s30s30s34s1s', obj)
                self.tracklist.append(sound)
        for track in self.tracklist:
            print(f'[{track.author.decode("windows-1251")}] [{track.name.decode("windows-1251")}] [{track.album_name.decode("windows-1251")}]')

def ex1():
    parser = argparse.ArgumentParser(description="Read ID3v1 tags from MP3 files")
    parser.add_argument("directory", type=str, help="Directory containing MP3 files")
    parser.add_argument("-d", "--dump", action="store_true", help="Show 16-bit dump of ID3v1 tag")
    parser.add_argument("-g", "--genre", type=int, default=12, help="Genre index to use if not present in tag")
    args = parser.parse_args()

    obj = Ex1(args.directory)
    obj.decoding()

# py .\tasks\ex1.py "ex1_music/"
if __name__ == '__main__':
    ex1()

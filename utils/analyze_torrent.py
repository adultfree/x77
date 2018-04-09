# 本工具用于读取torrent文件中的内容，并保存至文本文件中
# 基本功能：
# 1. 指定一个目录，搜索该目录下的*.torrent文件，读取torrent文件内容并保存为对应的*.txt
# 2. 指定一个torrent文件，读取该torrent文件的内容并保存为对应的txt文件

import glob
import os
import argparse

class Bencode:
    data = bytes()
    s = 0
    l = 0
    enc = False

    def encode(self, x):
        """param:
            object, contains int, str, list, dict or bytes.
        return:
            bytes, return the bencoded data.
        """
        if type(x) == int:
            return 'i'.encode() + str(x).encode() + 'e'.encode()
        elif type(x) == str:
            x = x.encode('utf-8')
            return (str(len(x)) + ':').encode('ascii') + x
        elif type(x) == dict:
            keys = list(x.keys())
            keys.sort()
            end = 'd'.encode()
            for i in keys:
                if type(i) == str:
                    end += self.encode(i)
                else:
                    raise TypeError("the key must be str for dict.")
                end += self.encode(x[i])
            end += 'e'.encode()
            return end
        elif type(x) == list:
            end = 'l'.encode()
            for i in x:
                end += self.encode(i)
            end += 'e'.encode()
            return end
        else:
            try:
                return (str(len(x)) + ':').encode('ascii') + x
            except:
                raise TypeError('the arg data type is not support for bencode.')

    def decode(self, x=None, enc=False):
        """param:
            1. bytes, the bytes will be decode.
            2. str or list, when can not decode with utf-8 charset will try using this charset decoding.
        return:
            object, unable decoding data will return bytes.
        """
        if enc:
            self.enc = enc
        if type(x) != bytes and x is not None:
            raise TypeError("To decode the data type must be bytes.")
        elif x is not None:
            self.s = 0
            self.l = 0
            self.data = x
            self.l = len(self.data)
        # dict
        if self.data[self.s] == 100:
            self.s += 1
            d = {}
            while self.s < self.l - 1:
                if self.data[self.s] not in range(48, 58):
                    break
                    # raise RuntimeError("the dict key must be str.")
                key = self.decode()
                value = self.decode()
                d.update({key: value})
            self.s += 1
            return d
        # int
        elif self.data[self.s] == 105:
            temp = self.s + 1
            key = ''
            while self.data[temp] in range(48, 58):
                key += str(self.data[temp] - 48)
                temp += 1
            self.s += len(key) + 2
            return int(key)
        # string
        elif self.data[self.s] in range(48, 58):
            temp = self.s
            key = ''
            while self.data[temp] in range(48, 58):
                key += str(self.data[temp] - 48)
                temp += 1
            temp += 1
            key = self.data[temp:temp + int(key)]
            self.s = len(key) + temp
            if type(self.enc) == list:
                for ii in self.enc:
                    try:
                        return key.decode(ii)
                    except:
                        continue
            else:
                try:
                    return key.decode('utf-8')
                except:
                    try:
                        return key.decode(self.enc)
                    except:
                        return key
        # list
        elif self.data[self.s] == 108:
            li = []
            self.s += 1
            while self.s < self.l:
                if self.data[self.s] == 101:
                    self.s += 1
                    break
                li.append(self.decode())
            return li

    def load(self, path, enc='utf-8'):
        """loading bencode object from file
        param:
            str, path and filename.
        return:
            bencode object.
        """
        with open(path, 'rb') as f:
            d = f.read()
        f.close()
        return self.decode(d, enc)

    def save(self, obj, path):
        """encoding object and save.
        param:
            1. bencode object, 2. filename.
        return:
            boolean.
        """
        with open(path, 'wb') as f:
            f.write(self.encode(obj))
        f.close()
        return True

    def parse(self, tf):
        name = None
        files = []
        with open(tf, "rb") as fin:
            bt = self.decode(fin.read())
            info = bt['info']
            if 'name' in info:
                name = info['name']
            if 'files' in info:
                for dirdict in info['files']:
                    if not dirdict['path'][0].startswith("_____padding_file"):
                        files.append("/".join(dirdict['path']) + "\n")
        txt_filename = os.path.splitext(tf)[0] + ".txt"
        if len(files) == 0:
            files.append(name)
        else:
            files.sort()
        with open(txt_filename, "w", encoding="UTF-8") as fout:
            fout.writelines(files)

    def handle(self, path):
        if os.path.isfile(path):
            self.parse(path)
        else:
            fullpath = os.path.abspath(path)
            for torrent in glob.glob(os.path.join(fullpath, "*.torrent")):
                self.parse(torrent)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="本工具用于读取torrent文件中的内容，并保存至文本文件中")
    parser.add_argument(dest="filedirs", metavar="path", nargs='*')
    args = parser.parse_args()
    bencode = Bencode()
    for filedir in args.filedirs:
        if os.path.exists(filedir):
            bencode.handle(filedir)


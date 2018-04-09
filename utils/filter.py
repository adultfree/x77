# 本文件根据网页中的文字说明，判断此torrent文件的归属（自拍系列或日本系列）

import shutil
import os

if __name__ == "__main__":
    asia_bt = os.path.join(os.path.abspath(os.path.curdir), "data", "AsiaBT")
    selfie = os.path.join(asia_bt, "自拍系列")
    japan = os.path.join(asia_bt, "日本系列")
    os.makedirs(selfie, exist_ok=True)
    os.makedirs(japan, exist_ok=True)
    for subdir in os.listdir(asia_bt):
        if subdir == "自拍系列" or subdir == "日本系列":
            continue
        subdir_path = os.path.join(asia_bt, subdir)
        info_file = os.path.join(subdir_path, "info.txt")
        from_japan = True
        with open(info_file, "r", encoding="UTF-8") as fin:
            for line in fin.readlines():
                if line.find("ALL") > 0 or line.find("all") > 0 or line.find("All") > 0:
                    from_japan = False
                    break
        if from_japan:
            shutil.move(subdir_path, japan)
        else:
            shutil.move(subdir_path, selfie)

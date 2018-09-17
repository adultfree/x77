import shutil
import random
import os
import re

if __name__ == "__main__":
    data_dir_path = "D:\\shared\\desktop\\data"
    production_dir_path = "D:\\shared\\desktop\\production"
    for subdir in os.listdir(data_dir_path):
        subdir_path = os.path.join(data_dir_path, subdir)
        production_subdir_path = os.path.join(production_dir_path, subdir)
        files = random.sample(os.listdir(subdir_path), k=200)
        for filename in files:
            # 随机选择200个
            shutil.move(os.path.join(subdir_path, filename), os.path.join(production_subdir_path, filename))
            # filename1 = re.sub("Q\d+", "", filename)
            # filename1 = filename.replace("████", "").replace("▃▄▅███", "")
            # filename1 = filename.replace("！", "")
            # if filename.endswith("...txt"):
            # filename1 = filename.replace("...txt", ".txt")
            # filename1 = filename.strip()
            # filename1 = filename.replace("██", "")
            # filename1 = filename.replace("［", "[").replace("］", "]")
            # if filename != filename1:
            #     shutil.move(os.path.join(subdir_path, filename), os.path.join(subdir_path, filename1))
            #     print("%s renamed to %s" % (filename, filename1))
        # if subdir == "自拍系列" or subdir == "日本系列":
        #     continue
        # subdir_path = os.path.join(asia_bt, subdir)
        # info_file = os.path.join(subdir_path, "info.txt")
        # from_japan = True
        # with open(info_file, "r", encoding="UTF-8") as fin:
        #     for line in fin.readlines():
        #         if line.find("ALL") > 0 or line.find("all") > 0 or line.find("All") > 0:
        #             from_japan = False
        #             break
        # if from_japan:
        #     shutil.move(subdir_path, japan)
        # else:
        #     shutil.move(subdir_path, selfie)

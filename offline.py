from datetime import datetime

from PIL import Image
from feature_extractor import FeatureExtractor
from pathlib import Path
import numpy as np
import json
import hashlib
import os


def loadNpyDataMap():
    filepath = Path("./static/npyToFilePath.json")
    if not filepath.exists():
        return {}
    with open(filepath, 'r') as f:
        dataMap = json.load(f)
    return dataMap


def get_file_md5(file_path):
    with open(file_path, 'rb') as f:
        md5 = hashlib.md5()
        while True:
            data = f.read(8192)
            if not data:
                break
            md5.update(data)
        return md5.hexdigest()


def save_dataMap(dataMap):
    # datamap to json and save to file
    json_data = json.dumps(dataMap, indent=4)
    with open('static/npyToFilePath.json', 'w') as f:
        f.write(json_data)


# 在保存特征的时候，同时保存文件的修改时间
def save_feature(feature_path, feature, img_path):
    np.save(feature_path, feature)
    dataMap[str(feature_path)] = {
        'img_path': str(img_path),
        'mtime': os.path.getmtime(img_path),
    }


# 在提取特征的时候，先检查文件的修改时间是否发生了改变
def extract_feature(img_path):
    # 使用文件的全路径来生成特征文件的名称，并将路径中的`/`和`\`字符替换为`_`
    feature_filename = str(img_path).replace('/', '_').replace('\\', '_') + ".npy"
    feature_path = Path("./static/feature") /feature_filename
    path_str = str(feature_path)
    if path_str in dataMap:
        info = dataMap[path_str]
        if abs(info['mtime'] - os.path.getmtime(img_path)) < 1.0:  # 使用容差值比较时间戳
            # print("load feature from file : ", feature_path)
            return False
        # else:
            # print("time diff : ", info['mtime'] - os.path.getmtime(img_path),path_str)
            # return np.load(feature_path)
    feature = fe.extract(img=Image.open(img_path))
    save_feature(feature_path, feature, img_path)
    # print("extract feature from img : ", img_path)
    return True


if __name__ == '__main__':
    fe = FeatureExtractor()
    dataMap = loadNpyDataMap()
    paths = sorted(Path("./static/img/svn").rglob("*.png"))
    all_count = len(paths)
    print("all paths : ", len(paths))
    start_time = datetime.now()
    updateNpyCount = 0
    index = 0
    for img_path in paths:
        index += 1
        # if (index == 15):
        #     break
        if index % 100 == 0:
            print("scan progress {0}/{1} ".format(index, all_count))
        # print(img_path)  # e.g., ./static/img/xxx.jpg
        if extract_feature(img_path):
            updateNpyCount += 1
    save_dataMap(dataMap)
    end_time = datetime.now()
    print("update npy count : ", updateNpyCount)
    print("cost time : ", end_time - start_time)

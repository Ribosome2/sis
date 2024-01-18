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

def scanRootDir(rootDir):
    paths = sorted(Path(rootDir).rglob("*.png"))
    all_count = len(paths)
    print(rootDir,"all paths : ", len(paths))
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
    print(rootDir ,"update npy count : ", updateNpyCount)



def remove_not_exist_file_and_data():
    not_exist_count = 0
    keys_to_remove = {}
    for k, v in dataMap.items():
        if not os.path.exists(v['img_path']):
            not_exist_count += 1
            keys_to_remove[k]=v
    all_count = len(dataMap)
    if(all_count>1000 and not_exist_count>100):
        for k, v in keys_to_remove.items():
            if not os.path.exists(v['img_path']):
                if os.path.exists(k):
                    print("delete "+k)
                    os.remove(k)
                del dataMap[k]
        print("remove not exist data count: ", not_exist_count)



if __name__ == '__main__':
    start_time = datetime.now()
    fe = FeatureExtractor()
    dataMap = loadNpyDataMap()
    scanRootDir("./static/img/svn")
    scanRootDir("./static/img/UnityProject/Assets")
    remove_not_exist_file_and_data()
    save_dataMap(dataMap)
    end_time = datetime.now()
    print("cost time : ", end_time - start_time)

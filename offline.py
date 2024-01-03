from datetime import datetime

from PIL import Image
from feature_extractor import FeatureExtractor
from pathlib import Path
import numpy as np
import json

def save_dataMap(dataMap):
    # datamap to json and save to file
    json_data = json.dumps(dataMap, indent=4)
    with open('static/npyToFilePath.json', 'w') as f:
        f.write(json_data)


if __name__ == '__main__':
    fe = FeatureExtractor()
    dataMap = {}
    paths= sorted(Path("./static/img/svn").rglob("*.png"))
    all_count = len(paths)
    print("all paths : ", len(paths))
    start_time = datetime.now()
    index = 0
    for img_path in paths:
        index += 1
        if(index==10):
            break
        if index % 100 == 0:
            print("scan progress {0}/{1} ".format(index,all_count))
        print(img_path)  # e.g., ./static/img/xxx.jpg

        feature = fe.extract(img=Image.open(img_path))
        feature_path = Path("./static/feature") / (img_path.stem + ".npy")  # e.g., ./static/feature/xxx.npy
        dataMap[str(feature_path)] = str(img_path)
        np.save(feature_path, feature)
    save_dataMap(dataMap)
    end_time = datetime.now()
    print("cost time : ", end_time - start_time)

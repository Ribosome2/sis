import json
import os

import numpy as np
from PIL import Image
from feature_extractor import FeatureExtractor
from datetime import datetime
from flask import Flask, request, render_template
from pathlib import Path

app = Flask(__name__)


def loadNpyDataMap():
    dataMap = {}
    with open('static/npyToFilePath.json', 'r') as f:
        cacheMap = json.load(f)
        for key in cacheMap:
            cache_data = cacheMap[key]
            if os.path.exists(cache_data["img_path"]):
                dataMap[key] = cache_data
            # else:
            #     print("remove cache : ", cache_data["img_path"])

    return dataMap

npyFileMap = loadNpyDataMap()

# Read image features
fe = FeatureExtractor()
svn_files_features = []
unity_files_features = []
img_paths_svn = []
img_paths_unity = []
for feature_path in Path("./static/feature").glob("*.npy"):
    feature_path_str = str(feature_path)
    if feature_path_str in npyFileMap:
        # print("feature_path_str : ", feature_path_str)
        if "static_img_UnityProject" in feature_path_str :
            unity_files_features.append(np.load(feature_path))
            img_paths_unity.append(npyFileMap[feature_path_str]["img_path"])
        else:
            svn_files_features.append(np.load(feature_path))
            img_paths_svn.append(npyFileMap[feature_path_str]["img_path"])
        # print("feature_path : ", feature_path, "  img_path : ", npyFileMap[str(feature_path)])


print("svn features: ", len(svn_files_features))
print("unity_files_features : ", len(unity_files_features))
svn_files_features = np.array(svn_files_features)
unity_files_features = np.array(unity_files_features)

def response_result_as_text(scores):
    result = ""
    for score in scores:
        cleanPath = score[1].replace("static\\img\\svn\\", "")
        cleanPath = cleanPath.replace("static\\img\\UnityProject\\", "")
        result += cleanPath + "\n"
    return result


def find_by_feature(feature_pool, query,img_paths):
    dists = np.linalg.norm(feature_pool - query, axis=1)
    ids = np.argsort(dists)[:15]  # Top 15 results
    scores = [(str(dists[id]), img_paths[id]) for id in ids]
    return scores

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['query_img']
        # check file is empty
        if not file:
            return "No file uploaded"
        remote_addr = request.environ.get('REMOTE_ADDR', None)
        print("--- ",remote_addr)
        print("remote_addr : ", request.remote_addr)
        if request.remote_addr == '127.0.0.1' or request.remote_addr == 'localhost':
            print("local request")
        else:
            print("remote request")


        # Save query image
        img = Image.open(file.stream)  # PIL image
        time_str = datetime.now().isoformat().replace(":", ".")
        date_time_folder =time_str[:10]  # 2020-12-12 prefix as folderName
        target_folder = "static/uploaded/" + date_time_folder
        # create dir if not exist
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        file_name = time_str + "_" + file.filename
        uploaded_img_path = target_folder+ "/"+ file_name
        img.save(uploaded_img_path)

        is_search_svn = False
        if 'isSVN' in request.form and request.form['isSVN']=="true":
            is_search_svn = True


        # Run search
        query = fe.extract(img)
        # python的三目运算
        scores = []
        if is_search_svn:
            if len(svn_files_features)  ==0 :
                print("no svn features file")
            else:
                scores = find_by_feature(svn_files_features, query,img_paths_svn)
        else:
            scores = find_by_feature(unity_files_features, query,img_paths_unity)


         # Check if resultAsText field is set
        if 'resultAsText' in request.form and request.form['resultAsText']:
            return response_result_as_text(scores)

        return render_template('index.html',
                               query_path=uploaded_img_path,
                               scores=scores)
    else:
        return render_template('index.html')


if __name__=="__main__":
    app.run("0.0.0.0")

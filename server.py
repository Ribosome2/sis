import json

import numpy as np
from PIL import Image
from feature_extractor import FeatureExtractor
from datetime import datetime
from flask import Flask, request, render_template
from pathlib import Path

app = Flask(__name__)


def loadNpyDataMap():
    with open('static/npyToFilePath.json', 'r') as f:
        dataMap = json.load(f)
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
        cleanPath = score[1].replace("static\img\svn\\", "")
        cleanPath = cleanPath.replace("static\img\\UnityProject\\", "")
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


        # Save query image
        img = Image.open(file.stream)  # PIL image
        uploaded_img_path = "static/uploaded/" + datetime.now().isoformat().replace(":", ".") + "_" + file.filename
        img.save(uploaded_img_path)

        is_search_svn = False
        if 'isSVN' in request.form and request.form['isSVN']:
            is_search_svn = True

        print("is_search_svn : ", is_search_svn)


        # Run search
        query = fe.extract(img)
        # python的三目运算
        scores = []
        if(is_search_svn):
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

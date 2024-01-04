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
img_paths = []
for feature_path in Path("./static/feature").glob("*.npy"):
    feature_path_str = str(feature_path)
    if feature_path_str in npyFileMap:
        # print("feature_path_str : ", feature_path_str)
        if feature_path_str.startswith("static\\feature\\static_img_svn"):
            svn_files_features.append(np.load(feature_path))
        else:
            unity_files_features.append(np.load(feature_path))
        # print("feature_path : ", feature_path, "  img_path : ", npyFileMap[str(feature_path)])
        img_paths.append(npyFileMap[feature_path_str]["img_path"])

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


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['query_img']

        # Save query image
        img = Image.open(file.stream)  # PIL image
        uploaded_img_path = "static/uploaded/" + datetime.now().isoformat().replace(":", ".") + "_" + file.filename
        img.save(uploaded_img_path)

        is_search_svn = False
        if 'isSVN' in request.form and request.form['isSVN']:
            is_search_svn = True


        # Run search
        query = fe.extract(img)
        # python的三目运算

        feature_pool = svn_files_features if is_search_svn  else unity_files_features
        dists = np.linalg.norm(feature_pool - query, axis=1)
        ids = np.argsort(dists)[:30]  # Top 30 results
        scores = [(str(dists[id]), img_paths[id]) for id in ids]



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

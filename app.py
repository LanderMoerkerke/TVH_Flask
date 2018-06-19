import os

# Imports FLASK
from flask import Flask, render_template, request, redirect, url_for
from flask_uploads import UploadSet, configure_uploads, IMAGES

# Imports ML
from keras.models import load_model

import numpy as np
import pandas as pd

from skimage.io import imread
from skimage import transform

from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import _tree

import cv2
import operator

# Functies
_TREE = []
counter1 = 0
counter2 = 0


def tree_to_code(tree, feature_names, y):
    global counter1, counter2
    _TREE = []
    counter1 = 0
    counter2 = 0
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
        for i in tree_.feature
    ]

    function = "def tree():\n"

    # print("def tree():")

    def get_output(a):
        output = np.array(a).ravel().tolist()
        return (y[output.index(1.0)])

    def recurse(node, depth):
        nonlocal function
        global counter1
        global counter2
        # Indent voor indent
        indent = "  " * depth
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            counter2 += 1
            name = feature_name[node]
            function += "{}input_user = input('{} | Y&N')\n".format(
                indent, name)
            if counter2 == 1:
                _TREE.append(name)
            else:
                _TREE.append(name)
            # print("{}input_user = input('{} | Y&N')".format(indent, name))
            function += "{}if input_user == 'Y':\n".format(indent)
            # print("{}if input_user == 'Y':".format(indent))
            recurse(tree_.children_left[node], depth + 1)
            function += "{}else:\n".format(indent)
            # print("{}else:".format(indent))
            recurse(tree_.children_right[node], depth + 1)
        else:
            counter1 += 1
            print(counter1)
            function += "{}return {}\n".format(indent,
                                               get_output(tree_.value[node]))
            if counter1 == 1:
                _TREE.append(get_output(tree_.value[node]))
            elif counter1 == 3:
                _TREE.append(get_output(tree_.value[node]))
            else:
                _TREE.append(get_output(tree_.value[node]))
            # print("{}return {}".format(indent, get_output(tree_.value[node])))

    recurse(0, 1)
    function += "result = tree()"
    return _TREE


def get_key_by_value(dict, search_acc):
    for groupcode, acc in dict.items():
        if acc == search_acc:
            return groupcode


# Start app
app = Flask(__name__)

# Variabelen
klasses = [
    '1011000', '1020700', '1021100', '1030500', '1030901', '2030900',
    '2050300', '2060701', '2061100', '2120300', '2120803', '2140300',
    '2170701', '2170705', '3010201', '3020200', '3030100', '3031101',
    '3060205', '3070403', '6020100', '6020300', '6030300', '7010500',
    '8020205', '8040000', '9020100', '10010300', '11000100', '13010100',
    '14010802', '17010000', '18010100', '18020100', '18030500', '18040100',
    '18060301', '18060302', '18080000', '18100200', '18110000', '18120000',
    '20010200', '23010000', '23020000'
]
filename = ""

# Initialise model
filename_model = os.path.join(os.path.dirname(__file__), 'static/model', 'my_model_test.h5')

model = load_model(filename_model)
model._make_predict_function()
dataset_one_hot_encoding = pd.read_excel(
    open(os.path.join(os.path.dirname(__file__), 'static/data', 'one_hot_encoding.xlsx'), 'rb'), sheet_name='Sheet1')


@app.route('/')
def index():
    """Model inlezen & dataset."""
    return render_template('index.html')


photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(os.path.dirname(__file__), 'static/uploads')
configure_uploads(app, photos)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    # Globale variabelen
    global klasses, d, counter_answer, _QUESTIONS, _IMAGE, filename

    if request.method == 'POST' and 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        print(filename)

        # Inlezen van image (gekregen van vorige pagina, beslissen in load_image naar welke pagina.)
        _IMAGE = os.path.join(os.path.dirname(__file__), 'static/uploads', filename)
        _IMAGE = imread(_IMAGE, as_grey=True)
        _IMAGE = cv2.resize(_IMAGE, (256, 256), interpolation=cv2.INTER_LINEAR)

        _IMAGE = _IMAGE.reshape(-1, 256, 256, 1)

        # Predictie doen op image.
        # Indien maximum uit deze lijst groter is dan 95 meteen naar eindpagina.

        proba = model.predict_proba(_IMAGE)
        proba = proba[0].tolist()

        # Dictionary maken & sorteren#
        d = dict(zip(klasses, proba))
        sorted_d = sorted(d.items(), key=operator.itemgetter(1), reverse=True)

        # Dataset maken van gesorteerde predictie#
        dataset = pd.DataFrame(sorted_d, columns=['GroupId', 'Proba'])

        _MAXIMUM = max(proba)
        if _MAXIMUM > 0.95:

            # Waardes (max & klasse) om door te sturen naar eindpagina
            _GROUP = get_key_by_value(d, _MAXIMUM)
            return prediction(_GROUP, _MAXIMUM)
        else:
            _QUESTIONS = []

            # Navigeren naar vragenronde met beste 3 categorieën
            decisionList = list(dataset['GroupId'][:3])

            # Enkel data uithalen met de gekregen groupcodes
            dataset_tree = dataset_one_hot_encoding.loc[
                dataset_one_hot_encoding.GroupCode.isin(decisionList), :]
            dataset_tree.reset_index(drop=True, inplace=True)

            # Tree genereren & in code plaatsen.
            X = dataset_tree.iloc[:, 1:]
            y = dataset_tree.iloc[:, 0]

            tree = DecisionTreeClassifier()
            tree.fit(X, y)

            tree_in_code = ""

            _QUESTIONS = tree_to_code(tree, X.columns, y)

            print('QUESTIONS', _QUESTIONS)
            print(len(_QUESTIONS))
            print((_QUESTIONS[1]))

            while len(_QUESTIONS) < 5 and isinstance(_QUESTIONS[1], int):
                _QUESTIONS = tree_to_code(tree, X.columns, y)

            print('BOOOOOOOM', _QUESTIONS)
            print(type(_QUESTIONS))

            # Doorsturen output
            return questions(_QUESTIONS)

    counter_answer = 0
    # tree_in_code = ""
    print('Lege boom.')
    return render_template('load_image.html')


@app.route('/questions')
def questions(lijst):
    print('questions lijst', _QUESTIONS)
    return render_template('questions.html', lijst=_QUESTIONS[0])


@app.route('/button_press_yes')
def button_press_yes():
    global _QUESTIONS
    global counter_answer
    counter_answer += 1

    print('counter answer', counter_answer)
    print('yes lijst', _QUESTIONS)
    if counter_answer == 1:
        print("YES x1")
        _PERC = d.get(int(_QUESTIONS[4]).__str__())
        return prediction(_QUESTIONS[4], _PERC)
        # return render_template('questions.html', lijst = _QUESTIONS[1])
    else:
        print("YES als je NEE eerder antwoordde.")
        _PERC = d.get(int(_QUESTIONS[3]).__str__())
        return prediction(_QUESTIONS[3], _PERC)
        #return render_template('prediction.html', group=lijst[2], maximum=_PERC)

@app.route('/button_press_no')
def button_press_no():
    global _QUESTIONS, counter_answer
    global d
    counter_answer += 1
    print('no lijst' ,_QUESTIONS)
    if counter_answer == 1:
        print("NEE 1x")
        return render_template('questions.html', lijst = _QUESTIONS[1])

        #_PERC = d.get(int(_QUESTIONS[4]).__str__())
        #return prediction(_QUESTIONS[4], _PERC)
        #return render_template('prediction.html', group=lijst[4], maximum=_PERC)
    else:
        print("NEE 2x")
        _PERC = d.get(int(_QUESTIONS[2]).__str__())
        return prediction(_QUESTIONS[2], _PERC)
        #return render_template('prediction.html', group=lijst[3], maximum=_PERC)



@app.route('/prediction/<group>/<maximum>')
def prediction(group, maximum):
    global filename
    print('prediction vars', group, maximum)


    d_chars = pd.read_excel(
        open(os.path.join(os.path.dirname(__file__), 'static/data', 'output.xlsx'), 'rb'), sheet_name='Sheet1')

    chars_list = list(
        d_chars.loc[d_chars.GroupCode.isin([int(group)]), 'CHARS'])

    chars_list = chars_list[0].split(',')
    chars_list = [x.strip() for x in chars_list]

    print('chars', chars_list)

    return render_template(
        'prediction.html',
        group=str(group),
        maximum=int(maximum * 100),
        chars_list=chars_list[:5], image=filename)


if __name__ == '__main__':
    app.run(debug=False)

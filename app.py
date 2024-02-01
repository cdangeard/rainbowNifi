from flask import Flask, request, jsonify, render_template
import json
import os

colorPatern = json.load(open(os.path.join(os.path.dirname(__file__),'colorPatern.json')))

def addColor(flowContents : dict, dictColors : dict) -> dict:
    '''
    Attribut:
        flowContents: dict
            The json file to coloriage
        dictColors: dict
            The dictionnary with the colors
    Return:
        ff: dict
            The json file coloriated

    Add color to the processors recursively
    '''
    ff = flowContents.copy()
    for processors in ff['processors']:
        try:
            processors['style']['background-color'] = dictColors[processors['type']]
        except:
            print(processors['type'])
    for processGroups in ff['processGroups']:
        addColor(processGroups, dictColors)
    return ff

app = Flask(__name__) #create the Flask app
app.config['DEBUG'] = True

@app.route('/')
def index():
    '''
    This function is the main page of the website
    The main page has a form to input json file
    and a coloriage button to coloriage the json file
    '''
    return render_template('index.html')

@app.route('/coloriage', methods=['POST'])
def coloriage():
    '''
    This function is the coloriage page of the website
    The coloriage page has a form to input json file
    and a coloriage button to coloriage the json file
    '''
    if request.method == 'POST':
        # validate if data is json
        try:
            jsonContent = json.loads(request.data)
        except:
            return {'error': 'The json file is not valid'}, 400
        # Coloriage the json file
        
        if jsonContent == {}:
            return {'error': 'The json file is empty'}, 400
        try:
            print("coloriage json")
            ff = jsonContent.copy()
            ff['flowContents'] = addColor(ff['flowContents'], colorPatern)
        except:
            return {'error': 'The json file is not coloriable'}, 400
        # Return the coloriage json file
        return jsonify(ff)

# Run the application
if __name__ == '__main__':
    app.run()
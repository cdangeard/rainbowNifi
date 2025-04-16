from flask import Flask, request, jsonify, render_template
import json
import os
import xml.etree.ElementTree as ET
from src.color import addColor_json, colorTemplate
from src.updateAtribute import createUpdateAtribute_template

colorPatern = json.load(open(os.path.join(os.path.dirname(__file__),'colorPatern.json')))



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

@app.route('/coloriageXML', methods=['POST'])
def coloriageXML():
    '''
    This function is the coloriage page of the website
    The coloriage page has a form to input json file
    and a coloriage button to coloriage the json file
    '''
    if request.method == 'POST':
        # validate if data is json
        try:
            strXml = request.data.decode('utf-8')
            xmlContent = ET.fromstring(strXml)
        except:
            return {'error': 'The xml file is not valid'}, 400
        # Coloriage the xml file
        try:
            print("coloriage xml")
            coloredXML = colorTemplate(xmlContent, colorPatern)
        except:
            return {'error': 'The xml file is not coloriable'}, 400
        # Send back xml
        return ET.tostring(coloredXML, encoding='utf-8', method='xml', xml_declaration=True).decode('utf-8')

@app.route('/coloriageJSON', methods=['POST'])
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
            ff['flowContents'] = addColor_json(ff['flowContents'], colorPatern)
        except:
            return {'error': 'The json file is not coloriable'}, 400
        # Return the coloriage json file
        return jsonify(ff)

@app.route('/updateAttribute')
def updateAttributePage():
    '''
    This function returns the updateAttribute page where users can submit JSON
    to create XML templates with simplified or full key paths
    '''
    return render_template('updateAttribute.html')

@app.route('/updateAttributeSimplified', methods=['POST'])
def updateAttributeSimplified():
    '''
    This function create a XML template of a updateAttribute processor
    based on the json file given in input
    The json file must be a valid json file
    '''
    return updateAttribute(simplifiedKeys=True)

@app.route('/updateAttributeFull', methods=['POST'])
def updateAttributeFull():
    '''
    This function create a XML template of a updateAttribute processor
    based on the json file given in input
    The json file must be a valid json file
    '''
    return updateAttribute(simplifiedKeys=False)

def updateAttribute(simplifiedKeys: bool = True):
    '''
    This function create a XML template of a updateAttribute processor
    based on the json file given in input
    The json file must be a valid json file
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
            print("Création updateAtribute Template json")
            xml = createUpdateAtribute_template(jsonContent, simplifiedKeys)
        except:
            return {'error': 'The json file is not coloriable'}, 400
        # Return the coloriage json file
        return xml


# Run the application
if __name__ == '__main__':
    app.run()
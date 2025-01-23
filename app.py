from flask import Flask, request, jsonify, render_template
import json
import os
import xml.etree.ElementTree as ET

colorPatern = json.load(open(os.path.join(os.path.dirname(__file__),'colorPatern.json')))

def addColor_json(flowContents : dict, dictColors : dict) -> dict:
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
        addColor_json(processGroups, dictColors)
    return ff

def colorTemplate(XMLfile : ET.ElementTree, colorPatern : dict) -> ET.ElementTree:
    print('coloriage xml colorTemplate')
    try:
        root = XMLfile
        print('rooted')
        root.find('name').text += '_colored'
    except:
        print('not conform')
        raise Exception('Invalid XML file')
    i = 0
    for child in root.iter():
        if child.tag == 'processors':
            i += 1
            typeChild = child.find('type').text
            color = colorPatern[typeChild] if typeChild in colorPatern else None
            if color:
                # Cas ou le style est déjà défini
                if (colorProc := child.find('style/entry/value')) is not None:
                    #print('Type:', typeChild, 'Actual Color:', colorProc.text, 'New Color:', color)
                    colorProc.text = color
                else:
                    style = child.find('style')
                    if style is None:
                        style = ET.Element('style')
                        child.insert(-2, style)
                    entry = ET.Element('entry')
                    key = ET.Element('key')
                    key.text = 'background-color'
                    value = ET.Element('value')
                    value.text = color
                    entry.insert(0, key)
                    entry.insert(1, value)
                    style.insert(0, entry)
                    
            else:
                print('Type:', typeChild, 'No Color')
    print('Total:', i)
    ET.indent(XMLfile, space="\t", level=0)
    return XMLfile

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

# Run the application
if __name__ == '__main__':
    app.run()
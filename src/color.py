import xml.etree.ElementTree as ET
import json

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
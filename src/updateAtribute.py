# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
from datetime import datetime
from uuid import uuid4

BASE_XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<template encoding-version="1.3">
    <description></description>
    <name></name>
    <groupId></groupId>
    <snippet>
        <processors>
            <id></id>
            <parentGroupId></parentGroupId>
            <position>
                <x>0.0</x>
                <y>0.0</y>
            </position>
            <bundle>
                <artifact>nifi-standard-nar</artifact>
                <group>org.apache.nifi</group>
                <version>1.18.0.2.1.5.0-215</version>
            </bundle>
            <config>
                <backoffMechanism>PENALIZE_FLOWFILE</backoffMechanism>
                <bulletinLevel>WARN</bulletinLevel>
                <comments></comments>
                <concurrentlySchedulableTaskCount>1</concurrentlySchedulableTaskCount>
                <descriptors>
                    <entry>
                        <key>Destination</key>
                        <value>
                            <name>Destination</name>
                        </value>
                    </entry>
                    <entry>
                        <key>Return Type</key>
                        <value>
                            <name>Return Type</name>
                        </value>
                    </entry>
                    <entry>
                        <key>Path Not Found Behavior</key>
                        <value>
                            <name>Path Not Found Behavior</name>
                        </value>
                    </entry>
                    <entry>
                        <key>Null Value Representation</key>
                        <value>
                            <name>Null Value Representation</name>
                        </value>
                    </entry>
                </descriptors>
                <executionNode>ALL</executionNode>
                <lossTolerant>false</lossTolerant>
                <maxBackoffPeriod>10 mins</maxBackoffPeriod>
                <penaltyDuration>30 sec</penaltyDuration>
                <properties>
                    <entry>
                        <key>Destination</key>
                        <value>flowfile-attribute</value>
                    </entry>
                    <entry>
                        <key>Return Type</key>
                        <value>auto-detect</value>
                    </entry>
                    <entry>
                        <key>Path Not Found Behavior</key>
                        <value>ignore</value>
                    </entry>
                    <entry>
                        <key>Null Value Representation</key>
                        <value>empty string</value>
                    </entry>
                </properties>
                <retryCount>10</retryCount>
                <runDurationMillis>0</runDurationMillis>
                <schedulingPeriod>0 sec</schedulingPeriod>
                <schedulingStrategy>TIMER_DRIVEN</schedulingStrategy>
                <yieldDuration>1 sec</yieldDuration>
            </config>
            <executionNodeRestricted>false</executionNodeRestricted>
            <name>EvaluateJsonPath</name>
            <relationships>
                <autoTerminate>false</autoTerminate>
                <name>failure</name>
                <retry>false</retry>
            </relationships>
            <relationships>
                <autoTerminate>false</autoTerminate>
                <name>matched</name>
                <retry>false</retry>
            </relationships>
            <relationships>
                <autoTerminate>false</autoTerminate>
                <name>unmatched</name>
                <retry>false</retry>
            </relationships>
            <state>STOPPED</state>
            <style/>
            <type>org.apache.nifi.processors.standard.EvaluateJsonPath</type>
        </processors>
    </snippet>
    <timestamp>04/16/2025 10:31:48 CEST</timestamp>
</template>
"""

def add_Attributes(tree: ET.ElementTree, elements: list[dict]) -> ET.ElementTree:
    for element in elements:
        try:
            key = element['key']
            value = element['value']
        except KeyError as e:
            print('Key Not Found')
            print(e)
            break

        try:
            #create descriptor Entry
            descriptorEntry = ET.Element('entry')
            entryValue = ET.Element('value')
            newEntry_key = ET.Element('key')
            entryValuename = ET.Element('name')

            newEntry_key.text = key
            entryValuename.text = value
            
            entryValue.append(entryValuename)
            descriptorEntry.append(newEntry_key)
            descriptorEntry.append(entryValue)
            tree.find(".//snippet//processors//config//descriptors").append(descriptorEntry)

            #create properties Entry
            propertyEntry = ET.Element('entry')
            propertyEntryKey = ET.Element('key')
            propertyEntryValue = ET.Element('value')

            propertyEntryKey.text = key
            propertyEntryValue.text = value

            propertyEntry.append(propertyEntryKey)
            propertyEntry.append(propertyEntryValue)

            tree.find(".//snippet//processors//config//properties").append(propertyEntry)
        except Exception as e:
            print('Erreur création XML')
            print(e)
    return tree

def flatten_dic(y : dict):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '.')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + '[' + str(i) + ']' + '.')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

def simplify_keys(dic: dict) -> dict:
    """
    Simplify the keys of a dictionary by removing the prefix up to the last dot.
    For example, 'a.b.c' becomes 'c'.
    if c exist and a.b.c exist, c will remain and a.b.c will become c
    :param dic: Dictionary with keys to be simplified
    :return: New dictionary with simplified keys ex: {'key': 'c', 'value': '$.a.b.c'}
    """
    sorted_by_length = sorted(dic.keys(), key=lambda x: len(x.split('.')), reverse=False)
    simplified_keys = {}
    for key in sorted_by_length:
        parts = key.split('.')
        simplified_key = parts[-1]
        if simplified_key not in simplified_keys.keys():
            simplified_keys[simplified_key] = key
        else:
            # If the simplified key already exists, keep the original key
            simplified_keys[key] = key
    # Convert to list of dictionaries
    elements = [{'key': k, 'value': f'$.{v}'} for k, v in simplified_keys.items()]
    return elements

def createUpdateAtribute_template(json_data: dict = None, simplifiedKeys : bool = True) -> str:
    """
    Create a template XML file for NiFi attribute to json processor.
    based on exemple jsonData each key will be mapped as an attribute

    :param json_data: JSON data to be converted to XML attributes
    """
    xml_template = ET.fromstring(BASE_XML_TEMPLATE)
    
    # Add a name
    name = f"AttributeToJson_generated{datetime.now().strftime('%Y%m%d%H%M%S')}"
    xml_template.find(".//name").text = name
    xml_template.find(".//timestamp").text = datetime.now().strftime('%m/%d/%Y %H:%M:%S CEST')#04/16/2025 10:31:48 CEST
    xml_template.find(".//snippet//processors//id").text = str(uuid4())
    # add attributes

    if json_data is not None:
        # Flatten the JSON data
        flat_json_data = flatten_dic(json_data)
        # Simplify keys
        if simplifiedKeys:
            elements = simplify_keys(flat_json_data)
        else:
            elements = [{'key': k, 'value': f'$.{k}'} for k in flat_json_data.keys()]
        # Convert to list of dictionaries
        # Add attributes to the XML template
        xml_template = add_Attributes(xml_template, elements)

    ET.indent(xml_template, space="\t", level=0)
    return ET.tostring(xml_template, encoding='unicode')
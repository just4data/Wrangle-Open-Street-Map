#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import csv
import codecs
import pprint
# import schema
import os, sys
import cerberus
import xml.etree.cElementTree as ET
from collections import defaultdict

dataset = 'cairo.osm'

node_table = ['id', 'lat', 'lon', 'version']
node_tags_table = ['id', 'key', 'value', 'type']
way_header = ['id', 'version']
way_tags_header = ['id', 'key', 'value', 'type']
way_nodes_header = ['id', 'node_id', 'position']

# =====================
#  Cleaning Functions  
# =====================

mapping = { # english cities
			'Al Manteqah Al Oula CAIRO' : 'Cairo',
			'Cairo Governorate' : 'Cairo',
			'el zaitoun' : 'Cairo',
			'Al Manial' : 'Cairo',
			'Bangalore' : 'Cairo',
			'New Cairo' : 'Cairo',
			'Bangalore' : 'Cairo',
			'El Cairo' : 'Cairo',
			'Mokkatam' : 'Cairo',
			'Zamalek' : 'Cairo',
			'Agouza' : 'Cairo',
			'Haram' : 'Cairo',
			'cairo' : 'Cairo',
			# english streets
			'Dokki Str' : 'Dokki Street',
			'Ibrahim St.' : 'Ibrahim Street',
			'El Muez St.' : 'El Muez Street',
			'Misr Helwan Rd' : 'Misr Helwan Road',
			'51 Khedr El Touny St.' : '51 Khedr El Touny Street',
			'Ibn Iyas El-Masry St.' : 'Ibn Iyas El-Masry Street',
			'Mohamed Al Maqrife Steet' : 'Mohamed Al Maqrife Street',
			'Alex-Cairo Desert Red. Ext.' : 'Alex-Cairo Desert Road Extension',
			'Elzahar st., Block 53, District 9, Nasr City' : 'Elzahar Street, Block 53, District 9, Nasr City',
			'50 El Tahrir, Al Balaqsah, Abdeen, Cairo Governorate, Cairo, Egypt' : '50 El Tahrir, Al Balaqsah, Abdeen',
			# arabic cities
			u'الكيلو 4.5 بجوار مطار الماظة' : 'القاهرة',
			u'دار السلام' : 'القاهرة',
			u'مدينة نصر' : 'القاهرة',
			u'تاج سلطان' : 'القاهرة',
			u'المهندسين' : 'القاهرة',
			u'قاهرة' : 'القاهرة',
			u'هرم' : 'الجيزة',
			# arabic streets			
			u',شارع' : 'شارع عبد العزيز فهمى',
			u'١١٨شارع' : '١١٨ شارع الازهر',
            }


def is_city(name):
    return (name == 'addr:city')

def update_city(name, mapping):
    if name in mapping:
        name = mapping[name]
    return name

def is_street(name):
	return (name == 'addr:street')

def update_street(name, mapping):
    if name in mapping:
        name = mapping[name]
    return name

def adjust_element(element, node_attr_fields = node_table, way_attr_fields = way_header,
                  odd_chars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]'), default_tag_type = 'regular'):
    
    # adjust way/node element to fit python dict
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  

    if element.tag == 'node':
        for attrib in element.attrib:
            if attrib in node_table:
                node_attribs[attrib] = element.attrib[attrib]
        for child in element:
            node_tag = {}
            
            if is_street(child.attrib['k']):
                child.attrib['v'] = update_street(child.attrib['v'], mapping)
            if is_city(child.attrib['k']):
                child.attrib['v'] = update_city(child.attrib['v'], mapping)

            # lower colon match
            if re.compile(r'^([a-z]|_)+:([a-z]|_)+').match(child.attrib['k']):
                node_tag['type'] = child.attrib['k'].split(':',1)[0]
                node_tag['key'] = child.attrib['k'].split(':',1)[1]
                node_tag['id'] = element.attrib['id']
                node_tag['value'] = child.attrib['v']
                tags.append(node_tag)

            # odd chars match
            elif re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]').match(child.attrib['k']):
                continue
            else:
                node_tag['type'] = 'regular'
                node_tag['key'] = child.attrib['k']
                node_tag['id'] = element.attrib['id']
                node_tag['value'] = child.attrib['v']
            tags.append(node_tag)
        return {'node': node_attribs, 'node_tags': tags}
        
    elif element.tag == 'way':
        for attrib in element.attrib:
            if attrib in way_header:
                way_attribs[attrib] = element.attrib[attrib]
        
        position = 0
        for child in element:
            way_tag = {}
            way_node = {}
            
            if child.tag == 'tag':
                if is_street(child.attrib['k']):
                    child.attrib['v'] = update_street(child.attrib['v'], mapping)
                    
                if is_city(child.attrib['k']):
                    child.attrib['v'] = update_city(child.attrib['v'], mapping)

                if re.compile(r'^([a-z]|_)+:([a-z]|_)+').match(child.attrib['k']):
                    way_tag['type'] = child.attrib['k'].split(':',1)[0]
                    way_tag['key'] = child.attrib['k'].split(':',1)[1]
                    way_tag['id'] = element.attrib['id']
                    way_tag['value'] = child.attrib['v']
                    tags.append(way_tag)
                
                elif re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]').match(child.attrib['k']):
                    continue
                
                else:
                    way_tag['type'] = 'regular'
                    way_tag['key'] = child.attrib['k']
                    way_tag['id'] = element.attrib['id']
                    way_tag['value'] = child.attrib['v']
                    tags.append(way_tag)

            elif child.tag == 'nd':
                way_node['id'] = element.attrib['id']
                way_node['node_id'] = child.attrib['ref']
                way_node['position'] = position
                position += 1
                way_nodes.append(way_node)
        
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
        
        
# ==================
#  Helper Functions  
# ==================

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

class UnicodeDictWriter(csv.DictWriter, object):
    # extend csv.DictWriter to handle unicode chars
    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

# =================
#   Main Function  
# =================

def process_map(osm_file):
    # loop over each xml element and write into csv files

    with codecs.open('nodes.csv', 'w') as nodes_file, \
         codecs.open('nodes_tags.csv', 'w') as nodes_tags_file, \
         codecs.open('ways.csv', 'w') as ways_file, \
         codecs.open('ways_nodes.csv', 'w') as way_nodes_file, \
         codecs.open('ways_tags.csv', 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, node_table)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, node_tags_table)
        ways_writer = UnicodeDictWriter(ways_file, way_header)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, way_nodes_header)
        way_tags_writer = UnicodeDictWriter(way_tags_file, way_tags_header)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        for element in get_element(osm_file, tags=('node', 'way')):
            ele = adjust_element(element)
            if ele:
                if element.tag == 'node':
                    nodes_writer.writerow(ele['node'])
                    node_tags_writer.writerows(ele['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(ele['way'])
                    way_nodes_writer.writerows(ele['way_nodes'])
                    way_tags_writer.writerows(ele['way_tags'])

process_map(dataset)


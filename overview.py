#!/usr/bin/python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint
import re


dataset = 'cairo.osm'


# get total no. of tags  

def total_tags(dataset):
    tags = defaultdict(int)
    tree = ET.parse(dataset)
    root = tree.getroot()
    for elem in root.iter():
        tags[elem.tag] += 1
    return tags

tags_count = total_tags(dataset)
print tags_count


# explore trends
lower = re.compile(r'^([a-z]|_)*$')
arabic = re.compile(ur'[ا-ي]|[١-٩]', re.UNICODE)
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problem_chars = re.compile(r'[=\+-/&<>;\'"\?%#$@\,\. \t\r\n]')

def tag_keys(elem, keys):
    if elem.tag == 'tag':
        if lower.search(elem.attrib['k']):
            keys['lower_keys'] += 1
            # print "lower: " + elem.attrib['k']
        elif lower_colon.search(elem.attrib['k']):
            keys['lower_colon_keys'] += 1
            # print "lower_colon: " + elem.attrib['k']
        elif arabic.search(elem.attrib['k']):
            keys['arabic_keys'] += 1
            # print "arabic: " + elem.attrib['k']
        elif problem_chars.search(elem.attrib['k']):
            keys['problem_chars_keys'] += 1
            # print "problem_chars: " + elem.attrib['k']
        else:
            keys['other_keys'] += 1
            # print "other: " + elem.attrib['k']
    return keys


def processing(dataset):
    keys = {'lower_keys': 0, 'lower_colon_keys': 0, 'arabic_keys': 0, 'problem_chars_keys': 0, 'other_keys': 0}
    for _, elem in ET.iterparse(dataset):
        keys = tag_keys(elem, keys)
    return keys

keys = processing(dataset)
pprint.pprint(keys)



# get arabic tag values
arabic = re.compile(ur'[ا-ي]|[١-٩]', re.UNICODE) 

def tag_values(elem, values):
    if elem.tag == 'tag':
        #print elem.attrib['v']
        if arabic.search(elem.attrib['v']):
            values['arabic_values'] += 1
            # print "arabic: " + elem.attrib['v']
        else:
            values['other_values'] += 1
            # print "other: " + elem.attrib['v']
    return values

def processing(dataset):
    values = {"arabic_values": 0, "other_values": 0}
    for _, elem in ET.iterparse(dataset):
        values = tag_values(elem, values)
    return values


values = processing(dataset)
pprint.pprint(values)


#!/usr/bin/python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint
import re

dataset = 'cairo.osm'


# auditing street & city names in both arabic & english languages 
expected_en = ['Road', 'Street', 'Highway', 'Autostrad']
expected_ar = ['شارع' , 'الشارع', 'طريق', 'الطريق']

# ====================
#  Auditing Functions  
# ====================

def audit_street_en(street_en, street_name):
    suffix = re.compile(r'\b\S+\.?$', re.IGNORECASE).search(street_name)
    if suffix:
        street_type = suffix.group()
        if street_type not in expected_en:
            street_en[street_type].add(street_name)

def audit_street_ar(street_ar, street_name):
    suffix = re.compile(r'[^\s]+').search(street_name)
    if suffix:
        street_type = suffix.group()
        if street_type.encode('utf-8') not in expected_ar:
            # print street_type.encode('utf-8')
            street_ar[street_type].add(street_name)

def audit_city_en(city_names_en, city_name):
    if city_name != 'Cairo':
        city_names_en[city_name].add(city_name)

def audit_city_ar(city_names_ar, city_name):
    if city_name.encode('utf-8') != 'القاهرة':
        city_names_ar[city_name].add(city_name)

def is_street_name(elem):
    return (elem.attrib['k'] == 'addr:street')

def is_city_name(elem):
    return (elem.attrib['k'] == 'addr:city')

# =================
#   Main Function  
# =================

def audit(osmfile):
    osm_file = open(osmfile, 'r')
    street_en = defaultdict(set)
    street_ar = defaultdict(set)

    city_names_ar = defaultdict(set)
    city_names_en = defaultdict(set)
    
    for event, elem in ET.iterparse(osm_file, events=('start',)):

        if elem.tag == 'node' or elem.tag == 'way':
            for tag in elem.iter('tag'):
                if is_city_name(tag):
                    #print tag.attrib['v']
                    val = re.compile(ur'[ا-ي]|[١-٩]', re.UNICODE).search(tag.attrib['v'])
                    if val:
                        audit_city_ar(city_names_ar, tag.attrib['v'])
                    else:
                        audit_city_en(city_names_en, tag.attrib['v'])
                elif is_street_name(tag):
                    val = re.compile(ur'[ا-ي]|[١-٩]', re.UNICODE).search(tag.attrib['v'])
                    if val:
                        audit_street_ar(street_ar, tag.attrib['v'])
                    else:
                        audit_street_en(street_en, tag.attrib['v'])
    osm_file.close()
    return street_en, street_ar, city_names_ar, city_names_en


st_en, st_ar, city_ar, city_en = audit(dataset)

print 'English Streets:'
pprint.pprint(dict(st_en))

print '\nArabic Streets:'
for key, value in st_ar.iteritems(): 
    print 'Word: ' + key
    for v in value:
        print '     Occurrence: ' + v

print '\nEnglish Cities:'
pprint.pprint(dict(city_en))

print '\nArabic Cities:'
for key, value in city_ar.iteritems(): 
    print 'Word: ' + key
    for v in value:
        print '     Occurrence: ' + v

import glob
import xml.etree.ElementTree as ElTree
import spacy
import matplotlib.pyplot as plt
import os
from collections import defaultdict


# utility function fot printing
def divide(title):
    divider = '=' * 80
    print('\n{}\n{}\n{}\n'.format(divider, title, divider))
    pass


# utility function to create csv from dictionary
def create_csv(file_name, header, data):
    file = open(os.path.join('output', '{}.csv'.format(file_name)), 'w+')
    file.write('{},occurrences\n'.format(header))
    for c, item in sorted([(value, key) for (key, value) in data.items()], reverse=True):
        file.write('{},{}\n'.format(item, c))
    file.close()


# load spacy data
nlp = spacy.load("en_core_web_sm")

# initialize dictionaries for various statistics
pos_count_dict = defaultdict(int)
token_entity_dict = defaultdict(list)
token_count_dict = defaultdict(int)
qslink_type_count_dict = defaultdict(int)
sentence_length_count_dict = defaultdict(int)
qslink_trigger_count_dict = defaultdict(int)
olink_trigger_count_dict = defaultdict(int)
motion_count_dict = defaultdict(int)

# load all xml files in data folder
xml_files = glob.glob('./data/**/*.xml', recursive=True)

# iterate over xml files
for xml_file in xml_files:

    # get text of current file
    tree = ElTree.parse(xml_file)
    text = tree.find('TEXT').text

    sentence_length = 0

    # generate pos tokens for text
    doc = nlp(text)
    for token in doc:

        # add pos token to dictionary
        pos_count_dict[token.pos_] += 1

        # count words until sentence ends, add word count to dictionary.
        if token.tag_ == '.':
            sentence_length_count_dict[sentence_length] += 1
            sentence_length = 0
        elif token.pos_ not in ['SPACE', 'PUNCT', 'SYM']:
            sentence_length += 1

    # read IsoSpace tags and add to dictionary
    entities = tree.find('TAGS')
    spatial_signals = [e for e in entities if e.tag == 'SPATIAL_SIGNAL']
    for entity in entities:
        token_entity_dict[entity.tag].append(entity)

        # find trigger of QsLinks and OLinks, add trigger text to dictionary
        if entity.tag in ['QSLINK', 'OLINK']:
            trigger = next((s for s in spatial_signals if s.get('id') == entity.get('trigger')), None)
            if trigger is not None:
                trigger_text = trigger.get('text').lower()
                if entity.tag == 'QSLINK':
                    qslink_trigger_count_dict[trigger_text] += 1
                else:
                    olink_trigger_count_dict[trigger_text] += 1

        if entity.tag == 'MOTION':
            motion_count_dict[entity.get('text').lower()] += 1

# create PoS tag count csv
create_csv('pos_tags', 'PoS-Tag', pos_count_dict)

# create IsoSpace token count csv
for token in ['SPATIAL_ENTITY', 'PLACE', 'MOTION', 'SPATIAL_SIGNAL', 'MOTION_SIGNAL', 'QSLINK', 'OLINK']:
    token_count_dict[token] = len(token_entity_dict[token])
create_csv('tokens', 'IsoSpace Token', token_count_dict)

# create QsLink type count csv
qslinks = token_entity_dict['QSLINK']
for qslink in qslinks:
    qslink_type = qslink.get('relType')
    qslink_type_count_dict[qslink_type if qslink_type != '' else 'UNKNOWN'] += 1
create_csv('qslink_types', 'QsLink Type', qslink_type_count_dict)

# create QsLink trigger count csv
create_csv('qslink_triggers', 'QsLink Trigger', qslink_trigger_count_dict)

# create OLink trigger count csv
create_csv('olink_triggers', 'OLink Trigger', olink_trigger_count_dict)

# create csv for five most used Motion verbs
motion_count_top_dict = {}
for count, motion in sorted([(count, motion) for (motion, count) in motion_count_dict.items()], reverse=True)[:5]:
    motion_count_top_dict[motion] = count
create_csv('motion_verbs', 'Motion Verb', motion_count_top_dict)

# create sentence length bar chart image
plt.bar(sentence_length_count_dict.keys(), sentence_length_count_dict.values())
plt.xlabel('words')
plt.ylabel('occurrences')
plt.savefig(os.path.join('output', 'sentence_length.jpg'))

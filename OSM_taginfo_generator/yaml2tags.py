import yaml
import sqlparse

'''
docker run -it -v ${PWD}:/data ods2qml:1.0  /bin/bash

pip3 install pyyaml
pip3 install sqlparse
python3 yaml2tags.py
echo

'''

def filter2keyvalye(text):
    # <man_made> IS NOT NULL OR <leisure> IS NOT NULL OR <amenity> IS NOT NULL OR <office> IS NOT NULL OR <shop> IS NOT NULL OR <tourism> IS NOT NULL OR <sport> IS NOT NULL
    # <railway> IN ('tram_stop') OR <highway> IN ('bus_stop') OR <public_transport> IN ('platform')
    pass
    
    
    
def get_tokens(where):
    sql_tokens = []
    for i in where.tokens:
        try:
            name = i.get_real_name()
            if name and not isinstance(i, sqlparse.sql.Parenthesis):
                # sql_tokens.append("{0} - {1} - {2}".format(str(i), str(name), i.value))
                sql_tokens.append({
                    'key': str(name),
                    'value': i.value,
                })
            else:
                sql_tokens.append(get_tokens(i))
        except Exception as e:
            pass
    return sql_tokens
    
def remb(src):
    src = src.replace('<','').replace('>','').strip()
    return src

def geomtype(src):
    if src=='point': return 'node'
    if src=='multilinestring': return 'way'
    if src=='line': return 'way'
    if src=='polygon': return 'area'
    
    raise ValueError('not known geometry type '+src)

all_tags=[]
all_secondary_tags=[]

hardcoded_tags=[

{'object_types':['relation','area'],'key':'ISO3166-2','description':'Regions boundaries for clipping'},
]

            
with open('layers.txt', 'r') as stream:
    try:
        parsed_yaml=yaml.safe_load(stream)
        #print(parsed_yaml)
    except yaml.YAMLError as exc:
        print(exc)
    
    for k in(parsed_yaml):
        print()
        print(parsed_yaml[k]['f'])
        sql='SELECT a FROM tablename WHERE '+parsed_yaml[k]['f']
        where = parsed_yaml[k]['f']
        words = where.split()
        tags=[]
        for word in words:
            if word.startswith('<') and word.endswith('>'):
                #tags.append(word)
                all_tags.append({'object_types':geomtype(parsed_yaml[k]['type']),"key":remb(word)})
        for word in parsed_yaml[k]['fields']:
            if word.startswith('<') and word.endswith('>'):
                all_secondary_tags.append({'object_types':geomtype(parsed_yaml[k]['type']),"key":remb(word)})

    #remove dublicates
    print(len(all_tags))
    all_tags = [dict(t) for t in {tuple(d.items()) for d in all_tags}]
    print(len(all_tags))
    print(len(all_secondary_tags))
    all_secondary_tags = [dict(t) for t in {tuple(d.items()) for d in all_secondary_tags}]
    print(len(all_secondary_tags))
    
    

    for element in all_secondary_tags:
        all_tags.append(element)
    del all_secondary_tags
    all_tags = [dict(t) for t in {tuple(d.items()) for d in all_tags}]
    
    sorted_all_tags = sorted(all_tags, key=lambda d: d['key']) 
    all_tags = sorted_all_tags
    
    for element in hardcoded_tags:
        all_tags.insert(0,element)
    
    output_text='['
    for element in (all_tags):
        #print(element,',')
        output_text+=str(element)+",\n"
    output_text+=']'
    
    print(output_text)
    with open('tags.json', 'w') as f:
        f.write(output_text)
    
    print(' ^^^text saved to tags.json ^^^ ')
        

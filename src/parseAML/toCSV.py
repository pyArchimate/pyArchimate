import csv
import json
import re

from archiObjects import elems_list, rels_list


def _to_csv(elems, file_name):

    rows = []
    fieldnames = elems[list(elems.keys())[0]].__dict__.keys()
    for r in  elems.values():
        o = r.__dict__
        if o is None:
            continue
        if 'desc' in o:
            if o['desc'] is not None:
                desc = re.findall(r'\s*(.*?)\s*properties', o['desc'], re.DOTALL)
                if len(desc) != 0:
                    o['desc'] = desc[0]
        if 'desc' in o:
            if o['desc'] is not None:
                desc = re.findall(r'\s*(.*?)\s*properties', o['desc'], re.DOTALL)
                if len(desc) != 0:
                    o['desc'] = desc[0]
        rows.append(o)

    with open(file_name, 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _to_csv_props(elems, file_name):
    rows = []
    for r in elems.values():
        for k,v in r.properties.items():
            if k == 'UUID':
                continue

            if  k == 'AT_DESC':
                pat = r'properties=({.*})'
                m = re.findall(pat, v, re.DOTALL)
                if len(m) != 0:
                    props = json.loads(m[0])
                    for k, v in props.items():
                        p = {
                            'uuid': r.uuid,
                            'key': k,
                            'value': v
                        }
                        rows.append(p)
                continue

            p = {
                'uuid': r.uuid,
                'key': k,
                'value': v
            }
            rows.append(p)

    fieldnames = ['uuid', 'key', 'value']

    with open(file_name, 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def to_csv():
    _to_csv_props(elems_list, 'properties.csv')

    elems = elems_list.copy()
    for k in elems:
        try:
            del elems[k].properties
        except:
            pass
        try:
            del elems[k].data
        except:
            pass
    _to_csv(elems, 'elements.csv')

    rels = rels_list.copy()
    for k in rels:
        try:
            del rels[k].relationship
        except:
            pass
    _to_csv(rels_list, 'relationships.csv')

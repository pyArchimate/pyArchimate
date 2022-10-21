"""

"""

from .. import *
import os
import csv


def csv_writer(model: Model, file_path: str):
    """
    The CSV writer generates three output files:
    - one for all elements
    - one for all relationships
    - one for all properties
    The file path is postfixed accordingly to the output file type
    :param model:
    :param file_path:
    """

    def convert_elements():
        fpath = os.path.join(path, file_name + '_elements.' + file_ext)
        with open(fpath, 'w', encoding='UTF8', newline='') as fd:
            header = ['ID', 'Type', 'Name', 'Documentation', 'Specialization']
            writer = csv.writer(fd, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(header)

            writer.writerow([model.uuid, 'ArchimateModel', model.name, model.desc, ''])
            for e in model.elements:
                writer.writerow([e.uuid, e.type, e.name, e.desc, ''])

    def convert_relationships():
        fpath = os.path.join(path, file_name + '_relations.' + file_ext)
        with open(fpath, 'w', encoding='UTF8', newline='') as fd:
            header = ['ID', 'Type', 'Name', 'Documentation', 'Source', 'Target', 'Specialization']
            writer = csv.writer(fd, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(header)
            for r in model.relationships:
                writer.writerow([r.uuid, r.type, r.name, r.desc, r.source.uuid, r.target.uuid, ''])

    def convert_properties():
        fpath = os.path.join(path, file_name + '_properties.' + file_ext)
        with open(fpath, 'w', encoding='UTF8', newline='') as fd:
            header = ['ID', 'Key', 'Value']
            writer = csv.writer(fd, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(header)
            for key, value in model.props.items():
                writer.writerow([model.uuid, key, value])
            for e in model.elements:
                for key, value in e.props.items():
                    writer.writerow([e.uuid, key, value])
            for r in model.relationships:
                for key, value in r.props.items():
                    writer.writerow([e.uuid, key, value])

    model = model
    file_path = file_path
    path, file_name = os.path.split(file_path)
    file_ext = file_name.split('.')[1]
    file_name = file_name.split('.')[0]
    convert_elements()
    convert_relationships()
    convert_properties()



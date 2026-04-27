"""

"""

import sys

try:
    from ..model import Model
except ImportError:
    sys.path.insert(0, "..")
    from pyArchimate import Model  # type: ignore[no-redef,attr-defined]

import csv
import os


def _write_elements_csv(model: Model, path: str, file_name: str, file_ext: str) -> None:
    fpath = os.path.join(path, file_name + '_elements.' + file_ext)
    with open(fpath, 'w', encoding='UTF8', newline='') as fd:
        writer = csv.writer(fd, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['ID', 'Type', 'Name', 'Documentation', 'Specialization'])
        writer.writerow([model.uuid, 'ArchimateModel', model.name, model.desc, ''])
        for e in model.elements:
            writer.writerow([e.uuid, e.type, e.name, e.desc, ''])


def _write_relationships_csv(model: Model, path: str, file_name: str, file_ext: str) -> None:
    fpath = os.path.join(path, file_name + '_relations.' + file_ext)
    with open(fpath, 'w', encoding='UTF8', newline='') as fd:
        writer = csv.writer(fd, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['ID', 'Type', 'Name', 'Documentation', 'Source', 'Target', 'Specialization'])
        for r in model.relationships:
            writer.writerow([r.uuid, r.type, r.name, r.desc, r.source.uuid, r.target.uuid, ''])


def _write_properties_csv(model: Model, path: str, file_name: str, file_ext: str) -> None:
    fpath = os.path.join(path, file_name + '_properties.' + file_ext)
    with open(fpath, 'w', encoding='UTF8', newline='') as fd:
        writer = csv.writer(fd, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['ID', 'Key', 'Value'])
        for key, value in model.props.items():
            writer.writerow([model.uuid, key, value])
        for e in model.elements:
            for key, value in e.props.items():
                writer.writerow([e.uuid, key, value])
        for r in model.relationships:
            for key, value in r.props.items():
                writer.writerow([r.uuid, key, value])


def csv_writer(model: Model, file_path: str) -> None:
    """
    The CSV writer generates three output files:
    - one for all elements
    - one for all relationships
    - one for all properties
    The file path is postfixed accordingly to the output file type

    :param model:
    :param file_path:
    """
    path, file_name = os.path.split(file_path)
    file_ext = file_name.split('.')[1]
    file_name = file_name.split('.')[0]
    _write_elements_csv(model, path, file_name, file_ext)
    _write_relationships_csv(model, path, file_name, file_ext)
    _write_properties_csv(model, path, file_name, file_ext)

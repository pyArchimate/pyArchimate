"""

"""

from src.pyArchimate.pyArchimate import *
import os
import csv


class CSVWriter:
    def __init__(self, model: Model, file_path:str):
        """

        :param model:
        :param file_path:
        """
        self.model = model
        self.file_path = file_path
        self.path, self.file_name = os.path.split(file_path)
        self.file_ext = self.file_name.split('.')[1]
        self.file_name = self.file_name.split('.')[0]
        self.convert_elements()
        self.convert_relationships()
        self.convert_properties()

    def convert_elements(self):
        fpath = os.path.join(self.path, self.file_name + '_elements.' + self.file_ext)
        with open(fpath, 'w', encoding='UTF8', newline='') as fd:
            header = ['ID', 'Type', 'Name', 'Documentation', 'Specialization']
            writer = csv.writer(fd, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(header)

            writer.writerow([self.model.uuid, 'ArchimateModel', self.model.name, self.model.desc, ''])
            for e in self.model.elements:
                writer.writerow([e.uuid, e.type, e.name, e.desc, ''])

    def convert_relationships(self):
        fpath = os.path.join(self.path, self.file_name + '_relations.' + self.file_ext)
        with open(fpath, 'w', encoding='UTF8', newline='') as fd:
            header = ['ID', 'Type', 'Name', 'Documentation', 'Source', 'Target', 'Specialization']
            writer = csv.writer(fd, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(header)
            for r in self.model.relationships:
                writer.writerow([r.uuid, r.type, r.name, r.desc, r.source.uuid, r.target.uuid,''])

    def convert_properties(self):
        fpath = os.path.join(self.path, self.file_name + '_properties.' + self.file_ext)
        with open(fpath, 'w', encoding='UTF8', newline='') as fd:
            header = ['ID', 'Key', 'Value']
            writer = csv.writer(fd, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(header)
            for key, value in self.model.props.items():
                writer.writerow([self.model.uuid, key, value])
            for v in self.model.views:
                for key, value in v.props.items():
                    writer.writerow([e.uuid, key, value])
            for e in self.model.elements:
                for key, value in e.props.items():
                    writer.writerow([e.uuid, key, value])
            for r in self.model.relationships:
                for key, value in r.props.items():
                    writer.writerow([e.uuid, key, value])


if __name__ == '__main__':
    m = Model('test')
    m.read(r'C:\Users\XY56RE\PycharmProjects\P13596-architecture-model\mfAppFiles\ARIS-Archi exchange files\GAL.xml')
    m.embed_props()
    m.expand_props(clean_doc=True)
    m.write('out.csv', writer=CSVWriter)

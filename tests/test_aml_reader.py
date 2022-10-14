
from src.pyArchimate.pyArchimate import *
from src.pyArchimate.readers.arisAMLreader import aris_reader

f = r'CADP.aml'
out = r'out.xml'


m = Model('imported')
m.read(f, reader=aris_reader)
m.write(out)
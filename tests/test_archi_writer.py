
from src.pyArchimate.pyArchimate import *
from src.pyArchimate.writers.archiWriter import archi_writer

f = r'in.xml'
out = r'out.archimate'


m = Model('test')
m.read(f)
m.write(out, writer=Writers.archimate)
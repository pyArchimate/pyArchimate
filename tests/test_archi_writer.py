
from src.pyArchimate.pyArchimate import *

f = r'in.xml'
out = r'out.archimate'


m = Model('test')
m.read(f)
m.write(out, writer=Writers.archi)

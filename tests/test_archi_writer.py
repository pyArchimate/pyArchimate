
from src.pyArchimate.pyArchimate import *

f = r'myModel.archimate'
out = r'out.archimate'


m = Model(f)
m.read(f)
m.write(out, writer=Writers.archi)
m.write('out.xml', writer=Writers.archimate)

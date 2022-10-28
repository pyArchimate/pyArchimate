
from src.pyArchimate.pyArchimate import *


f = r'C:\Users\XY56RE\PycharmProjects\createModel\createModel\output\CADP MF App Decomm.archimate'
out = r'out.archimate'


m = Model('test')
m.merge(f)
m.check_invalid_conn()
m.check_invalid_nodes()
m.write(out, writer=Writers.archi)
m.write('out.xml', writer=Writers.archimate)

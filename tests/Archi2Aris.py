#!python
import argparse
from src.pyArchimate.pyArchimate import *
from src.pyArchimate.readers.archiReader import archi_reader
from src.pyArchimate.writers.archimateWriter import archimate_writer

parse = argparse.ArgumentParser()
parse.add_argument('filename', help='Archi file to convert to ARIS Archimate XML')
parse.add_argument('-o', '--output', help='Output file pathname')

args = parse.parse_args()

f = args.filename.split('.archimate')[0]
out = args.output if args.output else f + '.xml'

m = Model(' ')
m.read(args.filename, reader=Readers.archi)
m.write(out, writer=Writers.archimate)


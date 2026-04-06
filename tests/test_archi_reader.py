
import tempfile
from pathlib import Path

from src.pyArchimate.pyArchimate import *

BASE = Path(__file__).resolve().parent
INPUT = BASE / 'test.archimate'


def _run():
    with tempfile.TemporaryDirectory() as tmp_dir:
        out = Path(tmp_dir) / 'out.archimate'
        m = Model('test')
        m.read(INPUT, reader=Readers.archi)
        m.check_invalid_conn()
        m.check_invalid_nodes()
        m.write(out, writer=Writers.archi)
        m.write(out.with_suffix('.xml'), writer=Writers.archimate)


_run()

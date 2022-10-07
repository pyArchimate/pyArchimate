import os
import re
import sys

import xmltodict

r = re.compile(r'[^\x09\x0A\x0D\x20-\x7E\x85\xA0-\xFF' \
  + r'\u0100-\uD7FF\uE000-\uFDCF\uFDE0-\uFFFD]')
def escapeInvalidXML(string):
  def replacer(m):
    return "<u>"+('%04X' % ord(m.group(0)))+"</u>"
  return re.sub(r,replacer,string)

if len(sys.argv) > 1:
    file = sys.argv[1]
else:
    file = os.path.join(r'C:\Users\XY56RE\PycharmProjects\P13596-architecture-model\mfAppFiles\ARIS-Archi exchange files', 'Capability Agreement Overview BE Realization.xml')

data = xmltodict.parse(open(file, 'r').read(), )
xml=xmltodict.unparse(data)


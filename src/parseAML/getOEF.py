from python.pyArchimate import newArchiObjects as ao

file_path = r'C:\Users\XY56RE\PycharmProjects\P13596-architecture-model\mfAppFiles\ARIS-Archi exchange files\test-template.xml'

m = ao.OpenExchange()
m.parse_xml(file_path)
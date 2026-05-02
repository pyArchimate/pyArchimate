from pyArchimate import Model, ArchiType

model = Model("e-commerce platform")
print(f"Model Type: {model.type}")   # Model
print(f"Model Name: {model.name}")   # e-commerce platform
app = model.add(ArchiType.ApplicationComponent, "Order Service")
svc = model.add(ArchiType.ApplicationService, "Place Order")
actor = model.add(ArchiType.BusinessActor, "Customer")

rel = model.add_relationship(ArchiType.Serving, source=app, target=svc)

print(f"Number of elements: {len(model.elements)}")       # 3
print(f"Number of relationships: {len(model.relationships)}")  # 1
print(f"Relationship type: {rel.type}")                  # Serving

view = model.add(ArchiType.View, "Application Layer")
node_app = view.add(app, x=0, y=0, w=120, h=55)
node_svc = view.add(svc, x=200, y=0, w=120, h=55)
conn = view.add_connection(rel, source=node_app, target=node_svc)

print(f"Number of nodes in view: {len(view.nodes)}")  # 2
print(f"Number of connections in view: {len(view.conns)}")  # 1
from pyArchimate import Writers
model.write("demo.xml",writer=Writers.archimate)
model.write("export_demo.archimate", writer=Writers.archi)

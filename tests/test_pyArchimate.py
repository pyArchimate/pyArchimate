import logging
import unittest
from src.pyArchimate import *

__mod__ = __name__.split('.')[len(__name__.split('.')) - 1]
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

log_to_stderr()
log_set_level(logging.INFO)

def create_model():
    """
    create a model
    :return: model
    :rtype: OpenExchange
    """
    # create model with a name
    m = Model('New Model')
    # add a description
    m.desc = 'This is my new Model'
    m.prop('version', '1.0')
    m.prop('author', 'Xavier Mayeur')
    return m


def add_some_elems(m):
    """
    add some elements

    :param m: model
    :type m: OpenExchange
    :return:
    """
    e = m.add(concept_type="ApplicationCollaboration", name="AIP", desc="AIP MF Cobol App")
    e.prop('Architect', 'Kathy Mottet')
    e2 = m.add(name='PAN', concept_type='ApplicationCollaboration')
    rel = m.add_relationship(source=e, target=e2, rel_type='Flow', name='Account Agreement')
    return e, e2, rel


def add_some_view(m):
    """

    :param m:
    :type m: OpenExchange
    :return:
    """
    v = m.add(archi_type.View, name="My View", desc="It is a view")
    v.prop('version', '1.1')
    e = m.find_elements(name="AIP")[0]
    e2 = m.find_elements(name="PAN")[0]
    n = v.add(ref=e.uuid, x=40, y=40, w=120, h=55)
    n2 = v.add(ref=e2.uuid, x=40, y=200, w=120, h=55)

    e3 = m.add(archi_type.ApplicationFunction)
    m.add_elements(e3)
    n3 = n.add(n2, x=60, y=220, w=60, h=30)
    r = m.add_relationship("Assignment", e, e3)
    m.add_relationships(r)
    n2.add_node(n3)

    rels = [r for r in m.find_relationships('Flow', e, direction='out') if r.target == e2.uuid]
    if len(rels) > 0:
        r = rels[0]
        conn = v.add_connection(r, n.uuid, n2.uuid)
        v.add_node(n, n2)
        v.add.add_connection(conn)
    m.add_views(v)
    return v


class MyTestCase(unittest.TestCase):
    def test_new_model(self):
        log.name = "test_new_model"
        m = create_model()
        self.assertEqual(m.name, 'New Model')
        self.assertEqual(m.desc, 'This is my new Model')
        val = m.prop('version')
        self.assertEqual(val, '1.0')
        val = m.prop('author')
        self.assertEqual(val, 'Xavier Mayeur')
        m.write('out.xml')

    def test_orgs(self):
        log.name = "test_orgs"
        m = Model('test')
        v = m.add(archi_type.View, 'X')
        e = m.add(archi_type.ApplicationComponent, 'Bus App')
        e.folder = '/Application/level1/level2'
        e2 = m.add(archi_type.ApplicationComponent, "Bus App 2")
        e2.folder = '/Oops'
        e2.folder = None
        e2.folder = '/Application/level1'
        m.write('out.xml')

    def test_crud_prop(self):
        log.name = "test_crud_prop"
        m = Model('New Model')
        m.prop('version', '1.0')
        m.prop('author', 'xavier')
        self.assertEqual(m.prop('version'), '1.0')
        m.prop('version', '2.0')
        self.assertEqual(m.prop('version'), '2.0')
        m.remove_prop('version')
        self.assertTrue((m.prop('version') is None))
        m.add(concept_type=archi_type.ApplicationComponent, name='coco')
        m.write('out.xml')
        m2 = Model('another model')
        m2.read('out.xml')
        self.assertEqual(m.prop('author'), m2.prop('author'))
        self.assertEqual(m2.prop('author'), 'xavier')

    def test_add_elem(self):
        log.name = "test_add_elem"
        m = create_model()
        try:
            e = m.add(name="coco", concept_type='bad_type')
            self.assertFalse(True)
        except ArchimateConceptTypeError:
            # Oops!
            e = m.add(concept_type="ApplicationCollaboration", name='AIS', desc="New way to create Element")
        self.assertTrue(e.uuid in m.elems_dict)
        e.prop('cmdb', '12345')
        self.assertEqual(e.prop('cmdb'), '12345')
        self.assertEqual(e.name, "AIS")
        self.assertEqual(e.type, "ApplicationCollaboration")
        self.assertEqual(e.desc, "New way to create Element")
        # self.assertTrue(e.uuid in m.names_dict[e.name])
        # find elem back by property
        elems = m.filter_elements(lambda x: x.prop('cmdb') == '12345')
        self.assertEqual(len(elems), 1)
        m.write('out.xml')
        m.read('out.xml')

    def test_del_elem(self):
        log.name = "test_del_elem"
        m = create_model()
        e = m.add(concept_type="ApplicationCollaboration", name='AIS', desc="New way to create Element")
        e.delete()
        del e
        self.assertEqual(len(m.elems_dict), 0)

        m.write()

    def test_merge_elem(self):
        log.name = "test_merge_elem"
        m = Model('test merge elem')
        v1 = m.add(archi_type.View, 'View 1')
        v2 = m.add(archi_type.View, 'View 2')
        n1 = v1.get_or_create_node(elem="App A", elem_type=archi_type.ApplicationCollaboration,
                                   x=20, y=20, create_node=True, create_elem=True)
        n2 = v1.get_or_create_node(elem="App B", elem_type=archi_type.ApplicationCollaboration,
                                   x=200, y=100, create_node=True, create_elem=True)
        n3 = v1.get_or_create_node(elem="App B.1", elem_type=archi_type.ApplicationComponent,
                                   x=400, y=100, create_node=True, create_elem=True)
        n4 = v1.get_or_create_node(elem="App B.2", elem_type=archi_type.ApplicationComponent,
                                   x=400, y=200, create_node=True, create_elem=True)
        r23 = v1.get_or_create_connection(rel=None, name="r23", source=n3, target=n2,
                                          rel_type=archi_type.Flow, create_conn=True)
        r24 = v1.get_or_create_connection(rel=None, name="r24", source=n4, target=n2,
                                          rel_type=archi_type.Flow, create_conn=True)

        e1 = n1.concept
        e2 = n2.concept
        e2.prop("version", "1")
        e1.merge(e2, merge_props=True)
        self.assertFalse(e2.uuid in m.elems_dict)
        self.assertEqual(e1.prop('version'), '1')
        m.write('out.xml')

    def test_add_rel(self):
        log.name = "test_add_rel"
        m = create_model()
        e = m.add(concept_type="ApplicationCollaboration", name='AIS', desc="It's AIS")
        e2 = m.add(concept_type="ApplicationCollaboration", name='PAN', desc="it's PAN")
        r: m.add_relationship = m.add_relationship(source=e, target=e2, rel_type="Flow", name="Flows to")
        r.prop("data", "agreement")
        self.assertEqual(r.prop("data"), "agreement")
        self.assertEqual(r.name, "Flows to")
        self.assertEqual(r.type, "Flow")
        self.assertEqual(r.source.uuid, e.uuid)
        self.assertEqual(r.target.uuid, e2.uuid)
        self.assertTrue(r.uuid in m.rels_dict)

        # Try
        m.write('out.xml')

    def test_del_rel(self):
        log.name = "test_del_rel"
        m = create_model()
        e = m.add(concept_type="ApplicationCollaboration", name='AIS', desc="It's AIS")
        e2 = m.add(concept_type="ApplicationCollaboration", name='PAN', desc="it's PAN")
        r: m.add_relationship = m.add_relationship(source=e, target=e2, rel_type="Flow", name="Flows to")
        r.prop("data", "agreement")
        r.delete()
        del r
        self.assertEqual(len(m.rels_dict), 0)

        m.write()

    def test_add_view(self):
        log.name = "test_add_view"
        m = create_model()
        e, e2, rel = add_some_elems(m)
        v = m.add(archi_type.View, 'New View using new method')
        v.prop("version", "2.1")
        self.assertEqual(v.prop('version'), '2.1')
        self.assertEqual(v.name, "New View using new method")
        self.assertEqual(v.desc, None)

        m.write()

    def test_add_node(self):
        log.name = "test_add_node"
        m = create_model()
        e, e2, rel = add_some_elems(m)
        v = m.add(archi_type.View, 'New View using new method')
        n = v.add(e, 100, 150)
        self.assertEqual(n.x, 100)
        self.assertEqual(n.y, 150)
        self.assertEqual(n.w, 120)
        self.assertEqual(n.h, 55)
        self.assertEqual(n.ref, e.uuid)
        # add node in node
        n2 = n.add(e2, 40, 50)
        self.assertEqual(n2.ref, e2.uuid)
        v2 = n2.view
        self.assertEqual(v.uuid, v2.uuid)
        m.write('out.xml')

    def test_del_node(self):
        log.name = "test_del_node"
        m = Model('test')
        v = m.add(archi_type.View, 'View1')
        n1 = v.get_or_create_node(elem='APP', elem_type=archi_type.ApplicationComponent,
                                  create_node=True, create_elem=True
                                  )
        n2 = v.get_or_create_node(
            elem='APP B', elem_type=archi_type.ApplicationComponent,
            x=200, w=240, h=110,
            create_node=True, create_elem=True
        )
        n3 = n2.get_or_create_node(
            elem='APP C', elem_type=archi_type.ApplicationComponent,
            create_node=True, create_elem=True
        )
        e3 = n3.concept

        n4 = n2.get_or_create_node(
            elem='APP D', elem_type=archi_type.ApplicationComponent,
            create_node=True, create_elem=True
        )
        r23 = m.get_or_create_relationship(rel_type=archi_type.Composition, name='', source=n2.concept,
                                           target=n3.concept,
                                           create_rel=True)
        r13 = n1.view.get_or_create_connection(rel=None, name='Flow to', rel_type=archi_type.Flow, source=n3,
                                               target=n1, create_conn=True)
        n2.resize()
        e2 = n2.concept
        n2.delete(delete_from_model=True)
        # e2.delete()
        # n3.delete(delete_from_model=True)
        e4 = n4.concept
        # n4.delete(delete_from_model=True)
        # e4.delete()
        # self.assertTrue(e4.uuid not in m.elems_dict)
        m.check_invalid_conn()

        m.write('out.xml')

    def test_add_conn(self):
        log.name = "test_add_conn"
        m: Model = create_model()
        e, e2, rel = add_some_elems(m)
        r: m.add_relationship = m.add_relationship(source=e, target=e2, rel_type="Flow", name="Flows to")
        v = m.add(archi_type.View, 'New View using new method')
        n = v.add(e, 100, 150)
        n2 = v.add(e2, 40, 50)
        c = v.add_connection(r, n, n2)
        c.add_bendpoint(Point(60, 100))
        bps = c.get_all_bendpoints()
        self.assertEqual(bps[0].x, 60)
        self.assertEqual(bps[0].y, 100)
        c.remove_all_bendpoints()
        bps = c.get_all_bendpoints()
        self.assertEqual(len(bps), 0)
        n3 = n2.get_or_create_node(elem='New one', elem_type=archi_type.ApplicationComponent,
                                   create_elem=True, create_node=True)
        n2.resize()
        c3 = v.get_or_create_connection(rel=None, rel_type=archi_type.Flow, name="flows to",
                                        source=n3, target=n,
                                        create_conn=True)
        m.write('out.xml')

    def test_del_view(self):
        log.name = "test_del_view"
        m = create_model()
        e, e2, rel = add_some_elems(m)
        r = m.add_relationship(source=e, target=e2, rel_type="Flow", name="Flows to")
        v = m.add(archi_type.View, 'New View using new method')
        v2 = m.add(archi_type.View, name="View 2")
        n = v.add(e, 100, 150)
        n2 = v.add(e2, 40, 50)
        c = v.add_connection(r, n, n2)
        cid = c.uuid
        nid = n.uuid
        n2id = n2.uuid
        eid = e.uuid
        vid = v.uuid

        self.assertTrue(vid in m.views_dict)
        self.assertTrue(nid in m.nodes_dict)
        self.assertTrue(n2id in m.nodes_dict)
        self.assertTrue(cid in m.conns_dict)

        v.delete()
        del v

        self.assertEqual(len(m.views), 1)
        self.assertTrue(vid not in m.views_dict)
        self.assertTrue(nid not in m.elems_dict)
        self.assertTrue(n2id not in m.elems_dict)
        self.assertTrue(cid not in m.conns_dict)
        self.assertTrue(eid in m.elems_dict)
        m.write()

    def test_export_import(self):
        log.name = "test_export_import"
        # create model"id-d840874664824b20a456fcbdfb6769f5"
        m = Model('TEST MODEL')
        m.prop('key', 'val')
        # create elements
        app_x = m.add(concept_type='ApplicationCollaboration', name='APP X',
                      uuid="id-d7af75c01dc5433a8846c802bf54a0f4")
        app_y = m.add(concept_type='ApplicationCollaboration', name='APP Y',
                      uuid="id-7950c5bfb5284df190b8ce40b13fce5b")
        x1 = m.add(concept_type='ApplicationFunction', name='App X.1', uuid="id-97fb76d01fa1469fad900919678f3334")
        x2 = m.add(concept_type='ApplicationFunction', name='App X.2', uuid="id-d840874664824b20a456fcbdfb6769f5")
        y1 = m.add(concept_type='ApplicationFunction', name='App Y.1', uuid="id-6cd060f5df494fd6b531d30416df4f81")
        i1 = m.add(concept_type='ApplicationInterface', name='Application Interface',
                   uuid="id-43b030e355bf4fa1ba833c13c2f94e93")

        # create relationships
        rxx1 = m.add_relationship(source=app_x, target=x1, rel_type='Assignment',
                                  uuid='id-d0cfce5b20d5437db42105ffa52d5b7d')
        rxx2 = m.add_relationship(source=app_x, target=x2, rel_type='Assignment',
                                  uuid='id-b0ffc6c18ffa4a249d52842db3875d5f')
        ryy1 = m.add_relationship(source=app_y, target=y1, rel_type='Assignment',
                                  uuid='id-a3fbfce0c86e4840ba44d7a2ab980a66')
        rx1i = m.add_relationship(source=x1, target=i1, rel_type='Serving', uuid='id-d9c7f88b5e99428fb93655ca4a9115f0')
        ry1i = m.add_relationship(source=y1, target=i1, rel_type='Flow', uuid='id-4a629319011246a3acae5ac615bd8a27')
        rx1y1 = m.add_relationship(source=x1, target=y1, rel_type='Flow')

        # create view
        v = m.add(archi_type.View, name='View 1', uuid='id-958b9bef4e5445f9bfa296e3d0b9655f')

        # create nodes
        n_app_x = v.add(ref=app_x, x=144, y=96, w=428, h=212, uuid='id-f098babec7384b9d8f9d4cfe89760911')
        nx1 = n_app_x.add(ref=x1, x=204, y=158, nested_rel_type=archi_type.Assignment)
        nx2 = n_app_x.add(ref=x2, x=384, y=158, nested_rel_type=archi_type.Assignment)
        ni1 = nx1.add(ref=i1, x=420, y=182)
        ni1.rx = 20
        ni1.ry = 20
        nx1.resize(recurse=False)

        n_app_y = v.add(ref=app_y, x=780, y=84, w=277, h=224, uuid='id-382bdf60593c4ba19a4c93947989875f')
        ny1 = n_app_y.add(ref=y1, x=861, y=172, nested_rel_type=archi_type.Assignment)

        # Create.add_connections
        cx1y1 = v.add_connection(ref=rx1y1, source=nx1, target=ny1, uuid='id-867c07640ac749c9bb111804572fc828')
        cx1y1.add_bendpoint(Point(264, 336), Point(924, 336))
        cy1i1 = v.add_connection(ref=ry1i, source=ny1, target=ni1, uuid='id-751335cd0d57413b95d32d86b1f5b00d')

        # Export the model to a file
        xml = m.write('out.xml')
        # print(xml)

    def test_allowed_rel(self):
        log.name = "test_allowed_rel"
        try:
            check_valid_relationship(archi_type.Access,
                                     archi_type.ApplicationCollaboration,
                                     archi_type.ApplicationCollaboration)
            self.assertFalse(True)
        except ArchimateRelationshipError:
            pass

        try:
            check_valid_relationship(archi_type.Flow,
                                     archi_type.ApplicationCollaboration,
                                     archi_type.ApplicationCollaboration)
        except:
            self.assertFalse(True)
        try:
            check_valid_relationship("archi_type.Access",
                                     archi_type.ApplicationCollaboration,
                                     archi_type.ApplicationCollaboration)
            self.assertFalse(True)
        except ArchimateConceptTypeError:
            pass

    def test_node_position(self):
        log.name = "test_node_position"
        m = Model('test')
        v = m.add(archi_type.View, 'View1')
        n1 = v.get_or_create_node(elem='E1', elem_type=archi_type.ApplicationComponent,
                                  create_elem=True, create_node=True)

        n2 = v.get_or_create_node(elem='E2', elem_type=archi_type.ApplicationComponent,
                                  x=200, y=0, create_elem=True, create_node=True)
        n2.x = 200
        n2.y = 0
        pos = n1.get_obj_pos(n2)
        self.assertEqual(pos.dx, 200)
        self.assertEqual(pos.angle, 0)
        self.assertEqual(pos.gap_x, 80)
        self.assertEqual(pos.orientation, "R!")

        n2.x = 0
        n2.y = 200
        pos = n1.get_obj_pos(n2)
        self.assertEqual(pos.angle, 270)
        self.assertEqual(pos.gap_y, 145)
        self.assertEqual(pos.orientation, "B!")

        n2.x = 200
        n2.y = 200
        pos = n1.get_obj_pos(n2)
        self.assertTrue(pos.angle == 315)
        self.assertEqual(pos.gap_y, 145)
        self.assertEqual(pos.gap_x, 80)
        self.assertEqual(pos.orientation, "B")
        del n1
        del n2
        m.write('out.xml')
        del m

    def test_point_pos(self):
        log.name = "test_point_pos"
        m = Model('Test')
        v = m.add(archi_type.View, 'View1')
        n1 = v.get_or_create_node(elem='E1', elem_type=archi_type.ApplicationComponent,
                                  x=-50, y=-50, w=100, h=100,
                                  create_elem=True, create_node=True)

        pt = Point(100, 100)
        pos = n1.get_point_pos(point=pt)
        self.assertEqual(pos.angle, 315)
        self.assertEqual(pos.gap_x, 50)

        pt = Point(0, -25)
        pos = n1.get_point_pos(pt)
        # print(pos.__dict__)
        self.assertTrue(n1.is_inside(point=pt))
        m.write()

    def test_distribute_conn(self):
        log.name = "test_distribute_conn"
        m = Model('test')
        v = m.add(archi_type.View, 'View1')
        n = []
        r = []
        # create a node in the middle of the view
        middle_node = v.get_or_create_node(elem_type=archi_type.ApplicationCollaboration,
                                           elem='App',
                                           x=500, y=500, w=100, h=100,
                                           create_node=True, create_elem=True
                                           )
        # create 10 nodes around the middle node
        delta = (2 * math.pi) / 10
        theta = 0
        dist = 350
        for i in range(1, 11):
            x = int(middle_node.cx + dist * math.sin(theta))
            y = int(middle_node.cy + dist * math.cos(theta))

            node = v.get_or_create_node(elem_type=archi_type.ApplicationComponent,
                                        elem='App ' + str(i),
                                        x=x, y=y,
                                        create_node=True, create_elem=True
                                        )
            node.cx = x
            node.cy = y
            c = v.get_or_create_connection(rel=None, rel_type=archi_type.Flow,
                                           name=str(i), source=middle_node, target=node, create_conn=True)

            angle = 360 * theta / (2 * math.pi)
            if (45 < angle < 135) or (225 < angle < 315):
                c.s_shape(direction=0)
            else:
                c.s_shape(direction=1)
            n.append(node)
            r.append(c)
            theta += delta

        middle_node.distribute_connections()
        bp4 = r[4].get_all_bendpoints()
        self.assertEqual(len(bp4), 2)
        if len(bp4) == 2:
            bp4 = bp4[0]
        self.assertEqual(bp4.x - middle_node.x, 3 * middle_node.w / 4)
        bp6 = r[6].get_all_bendpoints()
        if len(bp6) == 2:
            bp6 = bp6[0]
        self.assertEqual(bp6.x - middle_node.x, middle_node.w / 4)
        m.write('out.xml')
        del m

    def test_styles(self):
        log.name = "test_styles"
        m: Model = Model('test')
        v = m.add(archi_type.View, 'View1')
        n1: Node = v.get_or_create_node(elem_type=archi_type.ApplicationCollaboration,
                                        elem='App 1',
                                        create_node=True, create_elem=True
                                        )
        n2: Node = v.get_or_create_node(elem_type=archi_type.ApplicationCollaboration,
                                        elem='App 2',
                                        x=500, w=200, h=100,
                                        create_node=True, create_elem=True
                                        )
        n3: Node = n2.get_or_create_node(elem_type=archi_type.ApplicationCollaboration,
                                         elem='App 3',
                                         x=550, y=40,
                                         create_node=True, create_elem=True
                                         )
        conn = v.get_or_create_connection(rel=None, rel_type=archi_type.Flow,
                                          name="Flows to", source=n1, target=n2, create_conn=True)
        n1.fill_color = "#FF0000"
        self.assertEqual(n1.fill_color, "#FF0000")
        n2.font_color = "#0000FF"
        self.assertEqual(n2.font_color, "#0000FF")
        n2.fill_color = "#00FF00"
        n3.fill_color = "#FFFFFF"
        n3.opacity = 0
        n3.line_color = "#FFFFFF"
        n3.font_color = '#FFFFFF'
        self.assertEqual(n3.opacity, 0)
        self.assertEqual(n3.font_color, '#FFFFFF')

        conn.font_name = 'Arial'
        conn.font_size = 15
        conn.line_width = 3
        conn.font_color = "#FF0000"
        conn.line_color = "#00FF00"
        self.assertEqual(conn.line_color, "#00FF00")
        self.assertEqual(conn.line_color, '#00FF00')
        self.assertEqual(conn.line_width, 3)
        self.assertEqual(conn.font_name, 'Arial')
        self.assertEqual(conn.font_size, 15)

        # reset to default color
        n1.fill_color = None
        self.assertEqual(n1.fill_color, "#B5FFFF")
        m.write('out.xml')

    def test_embed_props(self):
        log.name = "test_embed_props"
        m = Model('test')
        m.prop('author', 'Xavier')
        m.prop('version', '1')
        a = m.add(archi_type.ApplicationComponent, 'A')
        b = m.add(archi_type.BusinessObject, 'B')
        r = m.add_relationship(archi_type.Access, a, b, name='ACCESS', access_type=access_type.Write)
        m.embed_props()
        self.assertTrue('properties' in m.desc)
        self.assertTrue('properties' in r.prop('Identifier'))
        for p in m.props.copy():
            m.remove_prop(p)
        for p in r.props.copy():
            if p != 'Identifier':
                r.remove_prop(p)
        r.access_type = access_type.Read
        self.assertTrue(m.prop('author') is None)
        m.expand_props()
        self.assertEqual(m.prop('author'), 'Xavier')
        self.assertEqual(m.prop('version'), '1')
        self.assertTrue('properties' not in m.desc)
        self.assertTrue(r.access_type == access_type.Write)
        self.assertEqual(r.name, 'ACCESS')
        m.write()
        del m

    def test_get_or_create(self):
        log.name = "test_get_or_create"
        m = Model('test')
        v = m.add(archi_type.View, 'view1')
        n1 = v.get_or_create_node(elem='Toto', elem_type=archi_type.ApplicationComponent,
                                  create_elem=True, create_node=True)
        n2 = n1.get_or_create_node(elem='Coco', elem_type=archi_type.ApplicationComponent,
                                   create_elem=True, create_node=True)
        n3 = n1.get_or_create_node(elem='Coco', elem_type=archi_type.ApplicationComponent,
                                   create_elem=True, create_node=True)
        self.assertEqual(n3.uuid, n2.uuid)
        m.write()
        del m

    def test_center_resize(self):
        log.name = "test_center_resize"
        m = Model('test')
        v = m.add(archi_type.View, 'View 1')
        gr = v.get_or_create_node(elem='GROUP', elem_type=archi_type.Grouping,
                                  create_elem=True, create_node=True)
        for i in range(0, 10):
            gr.get_or_create_node(elem='#' + str(i), elem_type=archi_type.ApplicationComponent,
                                  create_elem=True, create_node=True)
        gr.resize(max_in_row=4, justify='center', gap_x=70, recurse=False)
        m.write('out.xml')

    def test_xml_validation(self):
        log.name = "test_xml_validation"
        m = Model()
        v = m.add(archi_type.View, 'View 1')
        e1 = v.get_or_create_node(elem='App1', elem_type=archi_type.ApplicationComponent,
                                  create_node=True, create_elem=True)
        e2 = v.get_or_create_node(elem='App2 ', elem_type=archi_type.ApplicationComponent,
                                  create_node=True, create_elem=True)
        r = v.get_or_create_connection(rel=None, rel_type=archi_type.Flow, name=None,
                                       source=e1, target=e2, create_conn=True)
        e1.fill_color = '#FF0000'
        e2.fill_color = '#00FF00'
        # e2.ref = 'id-123456'
        xml = m.write('out.xml')

        # xmlschema.validate(xml, m.schemaD)
        # xmlschema.validate(xml, m.schemaM)
        # xmlschema.validate(xml, m.schemaV)

    def test_merge_models(self):
        log.name = "test_merge_models"
        m1 = Model('model1')
        v = m1.add(archi_type.View, 'View 1')
        n1 = v.get_or_create_node(elem='Elem1', elem_type=archi_type.ApplicationComponent,
                                  x=100, y=100, w=240, h=110,
                                  create_node=True, create_elem=True)
        n11 = n1.get_or_create_node(elem='Elem1.1', elem_type=archi_type.ApplicationComponent,
                                    x=120, y=120, w=120, h=55,
                                    create_node=True, create_elem=True,
                                    nested_rel_type=archi_type.Specialization)
        n1.resize(keep_kids_size=False, recurse=False)
        m1.write('out1.xml')

        m2 = Model('model1')
        v2 = m2.add(archi_type.View, 'View 2')
        n2 = v2.get_or_create_node(elem='Elem2', elem_type=archi_type.ApplicationComponent,
                                   x=100, y=100, w=240, h=110,
                                   create_node=True, create_elem=True)
        n21 = n2.get_or_create_node(elem='Elem2.1', elem_type=archi_type.ApplicationComponent,
                                    create_node=True, create_elem=True)
        n2.resize(keep_kids_size=False)

        m2.merge('out1.xml')
        m2.write('out.xml')

    def test_rel_props(self):
        log.name = "test_rel_props"
        m = Model('test')
        e1 = m.add(archi_type.ApplicationComponent, 'C1')
        e2 = m.add(archi_type.BusinessObject, 'O')
        r = m.add_relationship(archi_type.Access, e1, e2, access_type='Read')
        m.embed_props()
        m.write('out.xml')
        self.assertTrue(r.prop('Identifier') is not None)

    def test_move_node(self):
        log.name = "test_move_node"
        m = Model('test')
        v = m.add(archi_type.View, 'view')
        n1 = v.get_or_create_node('APP1', archi_type.ApplicationComponent, 20, 20, create_elem=True, create_node=True)
        n2 = v.get_or_create_node('APP2', archi_type.ApplicationComponent, 100, 100, create_elem=True, create_node=True)
        m.add_relationship(archi_type.Aggregation, n1.concept, n2.concept)
        n2.move(n1)
        n1.resize()
        self.assertTrue(n2.parent.uuid == n1.uuid)
        self.assertTrue(n2.uuid in n1.nodes_dict)
        self.assertFalse(n2.uuid in v.nodes_dict)
        m.write('out.xml')

    def test_default_rel(self):
        log.name = "test_default_rel"
        m = Model('test')
        e1 = m.add(archi_type.ApplicationCollaboration, "App")
        e2 = m.add(archi_type.ApplicationFunction, 'Comp')
        t = get_default_rel_type(archi_type.ApplicationComponent, archi_type.ApplicationComponent)

    def test_model_validation(self):
        log.name = "test_model_validation"
        m = Model('test')
        v = m.add(archi_type.View, 'view')
        n1 = v.get_or_create_node(elem='App1', elem_type=archi_type.ApplicationCollaboration,
                                  create_node=True, create_elem=True)
        n2 = v.get_or_create_node(elem='App2', elem_type=archi_type.ApplicationCollaboration,
                                  create_node=True, create_elem=True)
        c = v.get_or_create_connection(rel_type=archi_type.Flow, source=n1, target=n2)
        m.check_invalid_nodes()
        m.check_invalid_conn()
        id = n1.uuid
        e1 = m.elems_dict.pop(n1.concept.uuid)
        inv_n = m.check_invalid_nodes()
        inv_c = m.check_invalid_conn()
        self.assertTrue(id in inv_n)
        log.info(f" Orphan Node with ID {id} effectively detected")

    def test_new_arch_reader(self):
        log.name = "test_new_arch_reader"
        m = Model('test')

        m.read('MyModel.xml')
        m.default_theme('aris')
        m.write('out.xml')
        from src.pyArchimate.writers.csvWriter import csv_writer
        m.write('out.csv', writer=csv_writer)


    def test_rel_with_rel(self):
        log.name = "test_rel_with_rel"
        m = Model('test')
        app1 = m.add(archi_type.ApplicationComponent, 'App1')
        app2 = m.add(archi_type.ApplicationComponent, 'App2')
        bo = m.add(archi_type.BusinessObject, 'O')
        r = m.add_relationship(archi_type.Flow, app1, app2, access_type='Read')
        rr = m.add_relationship(archi_type.Association, bo, r)
        m.write('out.xml')


if __name__ == '__main__':
    unittest.main()

import pyArchimate as pa
from pyArchimate.writers.archimateWriter import archimate_writer


def main():
    # create a new model
    m = pa.Model("My Model")
    m.prop("author", "X. Mayeur")
    m.prop("version", "1.0.0")

    # Add a view
    v = m.add(concept_type=pa.ArchiType.View, name="view 1")

    # Add an node in the view and create the related element
    n_app_srv = v.get_or_create_node(
        "Application Service",
        pa.ArchiType.ApplicationService,
        20,
        20,
        create_elem=True,
        create_node=True,
    )
    # Add another one
    n_app_comp = v.get_or_create_node(
        "Application Component",
        pa.ArchiType.ApplicationComponent,
        x=200,
        y=20,
        create_elem=True,
        create_node=True,
    )
    # and create a relation between both
    v.get_or_create_connection(
        rel_type=pa.ArchiType.Serving,
        source=n_app_comp,
        target=n_app_srv,
        create_conn=True,
        name="Serves",
    )

    m.write("my_model.archimate", writer=archimate_writer)


if __name__ == "__main__":
    main()

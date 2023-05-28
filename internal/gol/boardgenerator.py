from internal import databasemanager
from database.tilenodedoc import TileNodeDoc


def generate_line(nodes, n_forking, length):
    nodes.append(TileNodeDoc(index=len(nodes), exits=[n_forking._id]))
    for n in range(length - 1):
        nodes.append(TileNodeDoc(index=len(nodes), exits=[nodes[-1]._id]))


def generate_branch(nodes, n_merging, length_path_right, length_path_left):
    # Path right
    for n in range(length_path_right + 1):
        nodes.append(TileNodeDoc(index=len(nodes), exits=[nodes[-1]._id]))
    n_forking = nodes[-1]
    # Path left
    nodes.append(TileNodeDoc(index=len(nodes), exits=[n_merging._id]))
    for n in range(length_path_left):
        nodes.append(TileNodeDoc(index=len(nodes), exits=[nodes[-1]._id]))
    n_forking.exits.append(nodes[-1]._id)
    return n_forking


async def generate_board():
    nodes = []

    nodes.append(TileNodeDoc(index=len(nodes)))  # End node
    generate_line(nodes, nodes[-1], 25)
    n_forking = generate_branch(nodes, nodes[-1], 2, 3)
    generate_line(nodes, n_forking, 11)
    n_forking = generate_branch(nodes, nodes[-1], 3, 3)
    generate_line(nodes, n_forking, 18)
    n_forking = generate_branch(nodes, nodes[-1], 6, 2)

    # Save the board
    nodes_formatted = []
    for n in nodes:
        nodes_formatted.append(n.to_mongo())
    await databasemanager.instance.db.tile_node_doc.insert_many(nodes_formatted)

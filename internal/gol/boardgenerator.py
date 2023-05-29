from internal.gol.tilenode import TileNode


def generate_line(game_id, nodes, n_forking, length):
    nodes.append(TileNode(game_id, len(nodes)))
    nodes[-1].exits = [n_forking]
    for n in range(length - 1):
        nodes.append(TileNode(game_id, len(nodes)))
        nodes[-1].exits = [nodes[-2]]


def generate_branch(game_id, nodes, n_merging, length_path_right, length_path_left):
    # Path right
    for n in range(length_path_right + 1):
        nodes.append(TileNode(game_id, len(nodes)))
        nodes[-1].exits = [nodes[-2]]
    n_forking = nodes[-1]

    # Path left
    nodes.append(TileNode(game_id, len(nodes)))
    nodes[-1].exits = [n_merging]
    for n in range(length_path_left):
        nodes.append(TileNode(game_id, len(nodes)))
        nodes[-1].exits = [nodes[-2]]
    n_forking.exits.append(nodes[-1])

    return n_forking


def generate_board(game_id):
    nodes = []

    nodes.append(TileNode(game_id, index=len(nodes)))  # End node
    generate_line(game_id, nodes, nodes[-1], 26)
    n_forking = generate_branch(game_id, nodes, nodes[-1], 2, 3)
    generate_line(game_id, nodes, n_forking, 11)
    n_forking = generate_branch(game_id, nodes, nodes[-1], 3, 3)
    generate_line(game_id, nodes, n_forking, 18)
    n_forking = generate_branch(game_id, nodes, nodes[-1], 6, 2)

    return nodes

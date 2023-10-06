class PuzzleNode:
    def __init__(self, state, parent=None, prev_move=None, g_cost=0):
        self.state = state
        self.parent = parent  # Pointer to the parent node
        self.prev_move = prev_move  # Previous move to reach this node
        self.g_cost = g_cost  # Cost from the start to this node

    def set_parent(self, parent):
        self.parent = parent

    def set_prev_move(self, prev_move):
        self.prev_move = prev_move

    def set_g_cost(self, g_cost):
        self.g_cost = g_cost


def get_blank_position(state):
    # Find the position of the blank (0) tile in the state
    for row in range(3):
        for col in range(3):
            if state[row][col] == 0:
                return row, col


def is_valid_move(state, move):
    # Check if the move is valid given the current state
    row, col = get_blank_position(state)
    if move == 'up' and row > 0:
        return True
    elif move == 'down' and row < 2:
        return True
    elif move == 'left' and col > 0:
        return True
    elif move == 'right' and col < 2:
        return True
    return False


def apply_move(state, move):
    # Apply the move to the current state
    row, col = get_blank_position(state)
    new_state = [row[:] for row in state]  # Create a copy of the current state

    if move == 'up':
        new_state[row][col], new_state[row - 1][col] = new_state[row - 1][col], new_state[row][col]
    elif move == 'down':
        new_state[row][col], new_state[row + 1][col] = new_state[row + 1][col], new_state[row][col]
    elif move == 'left':
        new_state[row][col], new_state[row][col - 1] = new_state[row][col - 1], new_state[row][col]
    elif move == 'right':
        new_state[row][col], new_state[row][col + 1] = new_state[row][col + 1], new_state[row][col]

    return new_state


def reconstruct_path(node, is_reverse=False):
    path = []
    while node and node.prev_move:
        move = node.prev_move
        if is_reverse:
            # Reverse the direction of the move
            if move == 'up':
                move = 'down'
            elif move == 'down':
                move = 'up'
            elif move == 'left':
                move = 'right'
            elif move == 'right':
                move = 'left'
        path.append(move)
        node = node.parent
    return list(reversed(path))
def manhattan_distance(state, goal_state):
    """
    Calculate the Manhattan distance heuristic for the 8-puzzle.
    """
    distance = 0
    for i in range(3):
        for j in range(3):
            if state[i][j] != 0:
                # Find the current position of the tile in the state
                current_pos = (i, j)
                # Find the goal position of the tile in the goal state
                goal_value = state[i][j]
                goal_pos = [(x, y) for x in range(3) for y in range(3) if goal_state[x][y] == goal_value][0]
                # Calculate Manhattan distance
                distance += abs(current_pos[0] - goal_pos[0]) + abs(current_pos[1] - goal_pos[1])
    return distance



def bidirectional_search(start_state, end_state):
    start_node = PuzzleNode(tuple(map(tuple, start_state)))
    end_node = PuzzleNode(tuple(map(tuple, end_state)))

    start_queue = [start_node]
    end_stack = [end_node]

    start_visited = {}
    end_visited = {}

    start_visited[start_node.state] = start_node
    end_visited[end_node.state] = end_node

    while start_queue and end_stack:
        # Forward (BFS) search from start state
        # Sort the open set by f_cost = g_cost + heuristic
        start_queue.sort(key=lambda node: node.g_cost + manhattan_distance(node.state, end_state))
        current_node_start = start_queue.pop(0)
        current_state_start = current_node_start.state

        for move in ['up', 'down', 'left', 'right']:
            if is_valid_move(list(map(list, current_state_start)), move):
                new_state_start = apply_move(list(map(list, current_state_start)), move)
                if tuple(map(tuple, new_state_start)) not in start_visited:
                    child_node_start = PuzzleNode(tuple(map(tuple, new_state_start)), parent=current_node_start)
                    child_node_start.set_prev_move(move)
                    child_node_start.set_g_cost(current_node_start.g_cost + 1)

                    start_queue.append(child_node_start)
                    start_visited[tuple(map(tuple, new_state_start))] = child_node_start

        # Check if there's an intersection with the end state
        if current_state_start in end_visited:
            intersection_node = end_visited[current_state_start]
            forward_moves = reconstruct_path(current_node_start)  # Paths from forward search
            backward_moves = reconstruct_path(intersection_node, is_reverse=True)  # Reverse moves for backward search
            return forward_moves + backward_moves

        # Backward (DFS) search from end state
        # Sort the open set by f_cost = g_cost + heuristic
        end_stack.sort(key=lambda node: node.g_cost + manhattan_distance(node.state, start_state))
        current_node_end = end_stack.pop()
        current_state_end = current_node_end.state

        for move in ['up', 'down', 'left', 'right']:
            if is_valid_move(list(map(list, current_state_end)), move):
                new_state_end = apply_move(list(map(list, current_state_end)), move)
                if tuple(map(tuple, new_state_end)) not in end_visited:
                    child_node_end = PuzzleNode(tuple(map(tuple, new_state_end)), parent=current_node_end)
                    child_node_end.set_prev_move(move)
                    child_node_end.set_g_cost(current_node_end.g_cost + 1)

                    end_stack.append(child_node_end)
                    end_visited[tuple(map(tuple, new_state_end))] = child_node_end

        # Check if there's an intersection with the start state
        if current_state_end in start_visited:
            intersection_node = start_visited[current_state_end]
            forward_moves = reconstruct_path(intersection_node)  # Paths from forward search
            backward_moves = reconstruct_path(current_node_end, is_reverse=True)  # Reverse moves for backward search
            return forward_moves + backward_moves

    return None


if __name__ == "__main__":
    start_state = [[1, 0, 2], [3, 4, 5], [6, 7, 8]]
    end_state = [[1, 7, 2], [4, 3, 0], [6, 8, 5]]

    sequence_of_moves = bidirectional_search(start_state, end_state)

    if sequence_of_moves is not None:
        print("Solution found! Sequence of moves:", sequence_of_moves)
    else:
        print("No solution found.")

# Autor: Petra Miková

import copy
import random
import time

# Trieda Node, ktorá definuje údaje obsiahnute v každom uzle a základné settre.
# Každý uzol v mojej implementácii obsahuje informáciu o stave hlavolamu, jeho predchodcu,
# operáciu ktorou sa dostal hlavolam do tohto stavu, a jeho cenu, t.j. vzdialenosť od  začiatku k tomuto uzlu.
class Node:
    def __init__(self, state, parent=None, move=None, cost=0):
        self.state = state
        self.parent = parent
        self.move = move
        self.cost = cost

    def set_parent(self, parent):
        self.parent = parent

    def set_move(self, move):
        self.move = move

    def set_cost(self, cost):
        self.cost = cost

# Funkcia, ktorá nájde a vráti pozíciu prázdneho políčka v hlavolame.
def find_blank_position(state):
    # Find the position of the blank (0) tile in the state
    for row in range(len(state)):
        for col in range(len(state)):
            if state[row][col] == 0:
                return row, col

# Funkcia, ktorá skontroluje či daný krok/operácia, ktorá sa ide vykonať, je valídna, teda možná v hlavolame tak,
# aby sa prázdne políčko nepresúvalo cez "hranice"
def valid_move_check(state, move):
    row, col = find_blank_position(state)
    n = len(state)
    if move == 'hore' and row > 0:
        return True
    elif move == 'dole' and row < n - 1:
        return True
    elif move == 'vlavo' and col > 0:
        return True
    elif move == 'vpravo' and col < n - 1:
        return True
    return False

# Funkcia pre vykonanie kroku pohybu v aktuálnom stave hlavolamu. Vráti nový stav.
def apply_move(state, move):
    row, col = find_blank_position(state)
    new_state = copy.deepcopy(state)

    if move == 'hore' and row > 0:
        new_state[row][col], new_state[row - 1][col] = new_state[row - 1][col], new_state[row][col]
    elif move == 'dole' and row < len(state) - 1:
        new_state[row][col], new_state[row + 1][col] = new_state[row + 1][col], new_state[row][col]
    elif move == 'vlavo' and col > 0:
        new_state[row][col], new_state[row][col - 1] = new_state[row][col - 1], new_state[row][col]
    elif move == 'vpravo' and col < len(state) - 1:
        new_state[row][col], new_state[row][col + 1] = new_state[row][col + 1], new_state[row][col]

    return new_state

# Jednoduchá funkcia pre pekný výpis hlavolamu.
def print_state(state):
    for row in state:
        print(row)
    print()

# Funkcia pre vytvorenie toku cesty z rootu po daný uzol. Ak ide o cestu odzadu, obráca operátory.

def reconstruct_path(node, is_reverse=False):
    path = []
    while node and node.move:
        move = node.move
        if is_reverse:
            if move == 'hore':
                move = 'dole'
            elif move == 'dole':
                move = 'hore'
            elif move == 'vlavo':
                move = 'vpravo'
            elif move == 'vpravo':
                move = 'vlavo'
        path.append(move)
        node = node.parent
    return list(reversed(path))


# Heuristika pre algoritmus - Manhattanská vzdialenosť - pre hlavolam typu n x n.
def manhattan_distance(state, goal_state):
    distance = 0
    n = len(state)
    for i in range(n):
        for j in range(n):
            if state[i][j] != 0:
                current_position = (i, j)
                goal_value = state[i][j]
                goal_position = [(x, y) for x in range(n) for y in range(n) if goal_state[x][y] == goal_value][0]
                distance += abs(current_position[0] - goal_position[0]) + abs(current_position[1] - goal_position[1])
    return distance

# Hlavná funkcia - algoritmus obojsmerného hľadania.
def bidirectional_search(start_state, end_state):
    start_node = Node(tuple(map(tuple, start_state)))
    end_node = Node(tuple(map(tuple, end_state)))

    start_queue = [start_node]
    end_stack = [end_node]

    start_visited = {}
    end_visited = {}

    start_visited[start_node.state] = start_node
    end_visited[end_node.state] = end_node

    while start_queue and end_stack:
        # Vyhľadávanie od začiatočného stavu so sortovaním open setu pomocou ceny uzla a Manhattanskej vzdialenosti
        start_queue.sort(key=lambda node: node.cost + manhattan_distance(node.state, end_state))
        current_node_start = start_queue.pop(0)
        current_state_start = current_node_start.state

        for move in ['hore', 'dole', 'vlavo', 'vpravo']:
            if valid_move_check(list(map(list, current_state_start)), move):
                new_state_start = apply_move(list(map(list, current_state_start)), move)
                if tuple(map(tuple, new_state_start)) not in start_visited:
                    child_node_start = Node(tuple(map(tuple, new_state_start)), parent=current_node_start)
                    child_node_start.set_move(move)
                    child_node_start.set_cost(current_node_start.cost + 1)
                    start_queue.append(child_node_start)
                    start_visited[tuple(map(tuple, new_state_start))] = child_node_start

        # Check pre pretnutie s koncovým stavom (intersection)
        if current_state_start in end_visited:
            intersection_node = end_visited[current_state_start]
            forward_moves = reconstruct_path(current_node_start)
            backward_moves = reconstruct_path(intersection_node, is_reverse=True)
            return forward_moves + backward_moves

        # Vyhľadávanie od koncového stavu so sortovaním open setu pomocou ceny uzla a Manhattanskej vzdialenosti
        end_stack.sort(key=lambda node: node.cost + manhattan_distance(node.state, start_state))
        current_node_end = end_stack.pop()
        current_state_end = current_node_end.state

        for move in ['hore', 'dole', 'vlavo', 'vpravo']:
            if valid_move_check(list(map(list, current_state_end)), move):
                new_state_end = apply_move(list(map(list, current_state_end)), move)
                if tuple(map(tuple, new_state_end)) not in end_visited:
                    child_node_end = Node(tuple(map(tuple, new_state_end)), parent=current_node_end)
                    child_node_end.set_move(move)
                    child_node_end.set_cost(current_node_end.cost + 1)
                    end_stack.append(child_node_end)
                    end_visited[tuple(map(tuple, new_state_end))] = child_node_end

        # Check pre pretnutie so začiatočným stavom (intersection)
        if current_state_end in start_visited:
            intersection_node = start_visited[current_state_end]
            forward_moves = reconstruct_path(intersection_node)
            backward_moves = reconstruct_path(current_node_end, is_reverse=True)
            return forward_moves + backward_moves

    return None

# Funkcia pre sparsovanie testovacích txt súborov
def parse_input_file(file_path):
    start_state = None
    end_state = None
    size = None

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('size:'):
                size_line = line.split(':')
                size_str = size_line[1].strip()
                size = int(size_str.split('x')[0])
            elif line.startswith('start:'):
                start_line = line.split(':')
                start_values = start_line[1].strip()
            elif line.startswith('end:'):
                end_line = line.split(':')
                end_values = end_line[1].strip()

    if size is not None and start_values and end_values:
        start_state = parse_state(size, start_values)
        end_state = parse_state(size, end_values)

    return start_state, end_state

# Funkcia pre parsovanie stavu z testovacieho txt súboru
def parse_state(size, values):
    values_list = list(map(int, values.split()))
    state = [values_list[i:i+size] for i in range(0, len(values_list), size)]
    return state

# Funkcia pre koncový výpis postupnosti krokov s vizualizáciou stavov
def print_solution_sequence(start_state, sequence_of_moves):
    if sequence_of_moves is not None:
        current_state = start_state
        print("Začiatočný stav:")
        print_state(current_state)

        for move in sequence_of_moves:
            current_state = apply_move(current_state, move)
            print("Pohyb:", move)
            print_state(current_state)

    else:
        print("Riešenie neexistuje.")


if __name__ == "__main__":

    print()
    print("*----------------------------------------------------------------------------*")
    print("|                8-hlavolam: riešenie obojsmerným hľadaním                   |")
    print("|                           Autor: Petra Miková                              |")
    print("|                             UI, ZS 2023/2024                               |")
    print("*----------------------------------------------------------------------------*")
    print()
    user_size = int(input("Zadajte, či chcete riešiť hlavolam 3x3 (zadajte 3) alebo 4x4 (zadajte 4): "))

    if user_size == 3:
        x = int(input("Zadajte, či chcete spustiť príklad z testovacej sady (zadajte 1), alebo zadať vlastný začiatočný a koncový stav (zadajte 2):"))
        if x == 1:
            file_names = ["vstupy/3x3_vstup1", "vstupy/3x3_vstup2", "vstupy/3x3_vstup3", "vstupy/3x3_vstup_tazsi", "vstupy/3x3_vstup_viceversa1", "vstupy/3x3_vstup_viceversa2"]
            random_file = random.choice(file_names)
            file_path = random_file
            start_state, end_state = parse_input_file(file_path)
            start_time = time.time()
            sequence_of_moves = bidirectional_search(start_state, end_state)
            end_time = time.time()
            elapsed_time_ms = round((end_time - start_time) * 1000, 2)
            print("Čas:", elapsed_time_ms, "milisekúnd")
            print_solution_sequence(start_state,sequence_of_moves)
        else:
            start_state = input("Zadajte začiatočný stav vo formáte x x x 0 x x x x x, kde 0 predstavuje vaše prázdne políčko:")
            end_state = input("Zadajte koncový stav vo formáte x x x 0 x x x x x, kde 0 predstavuje vaše prázdne políčko:")
            start_state = parse_state(3, start_state)
            end_state = parse_state(3, end_state)
            start_time = time.time()
            sequence_of_moves = bidirectional_search(start_state, end_state)
            end_time = time.time()
            elapsed_time_ms = round((end_time - start_time) * 1000, 2)
            print("Čas:", elapsed_time_ms, "milisekúnd")
            print_solution_sequence(start_state,sequence_of_moves)
    else:
        x = int(input(
            "Zadajte, či chcete spustiť príklad z testovacej sady (zadajte 1), alebo zadať vlastný začiatočný a koncový stav (zadajte 2):"))
        if x == 1:
            file_names = ["vstupy/4x4_vstup1", "vstupy/4x4_vstup2", "vstupy/4x4_vstup3", "vstupy/4x4_vstup_tazsi"]
            random_file = random.choice(file_names)
            file_path = random_file
            start_state, end_state = parse_input_file(file_path)
            start_time = time.time()
            sequence_of_moves = bidirectional_search(start_state, end_state)
            end_time = time.time()
            elapsed_time_ms = round((end_time - start_time) * 1000, 2)
            print("Čas:", elapsed_time_ms, "milisekúnd")
            print_solution_sequence(start_state, sequence_of_moves)
        else:
            start_state = input("Zadajte začiatočný stav vo formáte x x x x x 0 x x x x x x x x x x x, kde 0 predstavuje vaše prázdne políčko:")
            end_state = input("Zadajte koncový stav vo formáte x x x x x x x x x x x x 0 x x x, kde 0 predstavuje vaše prázdne políčko:")
            start_state = parse_state(4, start_state)
            end_state = parse_state(4, end_state)
            start_time = time.time()
            sequence_of_moves = bidirectional_search(start_state, end_state)
            end_time = time.time()
            elapsed_time_ms = round((end_time - start_time) * 1000, 2)
            print("Čas:", elapsed_time_ms, "milisekúnd")
            print_solution_sequence(start_state, sequence_of_moves)
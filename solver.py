# Generalised solver for hectic sudoku from felix
# Author : RadaanMadhan

class HecticSudokuSolver:
    def __init__(self, board, rules):
        # 2D Matrix of sudoku board adressed as row, column
        # (0, 0) is top left coordinate
        self.board = board

        # Dictionary of rule location for hectic sudoku represented as list of points per line
        # "green" - pair of two adjacent digits must have difference of at least 5
        # "blue" - digits along the arrow must add up to the total number in the circle(first coordinate)
        # "purple" - Numbers on line must be in between  values in the circle(first and last coordinate)
        self.rules = rules

        self.green_paths = [self._generate_path(p) for p in rules["green"]]
        self.blue_paths = [self._generate_path(p) for p in rules["blue"]]
        self.purple_paths = [self._generate_path(p) for p in rules["purple"]]

        # Reverse index: for each cell, which (rule_type, path) touch it
        # Store tuples as (r, c) for faster access
        self.cell_rules = [[[] for _ in range(9)] for _ in range(9)]
        for path in self.green_paths:
            tp = tuple(tuple(c) for c in path)
            for coord in path:
                self.cell_rules[coord[0]][coord[1]].append(("green", tp))
        for path in self.blue_paths:
            tp = tuple(tuple(c) for c in path)
            for coord in path:
                self.cell_rules[coord[0]][coord[1]].append(("blue", tp))
        for path in self.purple_paths:
            tp = tuple(tuple(c) for c in path)
            for coord in path:
                self.cell_rules[coord[0]][coord[1]].append(("purple", tp))

    # Generate all coordinates on path from list of corners 
    @staticmethod
    def _generate_path(path):
        path_coords = []
        prev_corner = path[0]
        for corner in path[1:]:
            # Row edge 
            if prev_corner[0] == corner[0]:
                step = 1 if corner[1] > prev_corner[1] else -1
                for j in range(prev_corner[1], corner[1], step):
                    path_coords.append([prev_corner[0], j])
            # Column edge 
            elif prev_corner[1] == corner[1]:
                step = 1 if corner[0] > prev_corner[0] else -1
                for i in range(prev_corner[0], corner[0], step):
                    path_coords.append([i, prev_corner[1]])
            prev_corner = corner
        path_coords.append(path[-1])
        return path_coords

    # Incremental rule check - only checks rules touching cell (r, c)
    def _check_rules_for_cell(self, r, c):
        board = self.board
        for rule_type, path in self.cell_rules[r][c]:
            if rule_type == "green":
                for i in range(1, len(path)):
                    ar, ac = path[i - 1]
                    br, bc = path[i]
                    a = board[ar][ac]
                    b = board[br][bc]
                    if a != "." and b != "." and abs(int(a) - int(b)) < 5:
                        return False

            elif rule_type == "blue":
                target_cell = board[path[0][0]][path[0][1]]
                if target_cell == ".":
                    continue
                target = int(target_cell)
                total = 0
                all_filled = True
                for i in range(1, len(path)):
                    v = board[path[i][0]][path[i][1]]
                    if v == ".":
                        all_filled = False
                    else:
                        total += int(v)
                if total > target:
                    return False
                if all_filled and total != target:
                    return False

            elif rule_type == "purple":
                end_a = board[path[0][0]][path[0][1]]
                end_b = board[path[-1][0]][path[-1][1]]
                if end_a == "." or end_b == ".":
                    continue
                high = max(int(end_a), int(end_b))
                low = min(int(end_a), int(end_b))
                for i in range(1, len(path) - 1):
                    v = board[path[i][0]][path[i][1]]
                    if v != "." and not (low < int(v) < high):
                        return False
        return True

    # solve for valid solution and update board
    # output final path taken to solve
    # mimics human check to solve
    def solve(self):
        # Bitmask availability - bits 0-8 represent digits 1-9
        ALL = 0x1FF
        row_avail = [ALL] * 9
        col_avail = [ALL] * 9
        box_avail = [ALL] * 9

        empty_cells = []
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == ".":
                    empty_cells.append((i, j))
                else:
                    bit = 1 << (int(self.board[i][j]) - 1)
                    row_avail[i] &= ~bit
                    col_avail[j] &= ~bit
                    box_avail[i // 3 + (j // 3) * 3] &= ~bit

        n_empty = len(empty_cells)
        check_rules = self._check_rules_for_cell
        solve_path = []

        # recursive fill with MRV cell selection and bitmask ops
        def dfs(remaining):
            if remaining == 0:
                return True

            # Pick empty cell with fewest candidates (MRV)
            min_count = 10
            best_r = best_c = best_box = best_cands = -1
            for idx in range(n_empty):
                r, c = empty_cells[idx]
                if self.board[r][c] != ".":
                    continue
                box = r // 3 + (c // 3) * 3
                cands = row_avail[r] & col_avail[c] & box_avail[box]
                count = bin(cands).count('1')
                if count == 0:
                    return False
                if count < min_count:
                    min_count = count
                    best_r, best_c, best_box, best_cands = r, c, box, cands
                    if count == 1:
                        break

            # Iterate candidate digits via bit manipulation
            bits = best_cands
            while bits:
                bit = bits & (-bits)
                bits &= bits - 1
                num = bit.bit_length()

                self.board[best_r][best_c] = str(num)
                row_avail[best_r] &= ~bit
                col_avail[best_c] &= ~bit
                box_avail[best_box] &= ~bit

                # Incremental rule check
                if check_rules(best_r, best_c):
                    solve_path.append((best_r, best_c, num, min_count))
                    if dfs(remaining - 1):
                        return True
                    solve_path.pop()

                row_avail[best_r] |= bit
                col_avail[best_c] |= bit
                box_avail[best_box] |= bit
                self.board[best_r][best_c] = "."

            return False

        dfs(n_empty)

        print(f"\nSolve path ({len(solve_path)} steps):")
        for step, (r, c, num, candidates) in enumerate(solve_path, 1):
            print(f"  Step {step:3d}: ({r},{c}) = {num}  (candidates: {candidates})")

import ast

from solver import HecticSudokuSolver

def main():
    board_file_path = "board.txt"
    rules_file_path = "rules.txt"

    bf = open(board_file_path)
    board = ast.literal_eval(bf.read())

    rf = open(rules_file_path)
    rules = ast.literal_eval(rf.read())

    solver = HecticSudokuSolver(board, rules)
    solver.solve() 

    print(solver.board)

if __name__ == "__main__":
    main()


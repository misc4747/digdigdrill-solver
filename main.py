import sys
import json


def load_blocks(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)["blocks"]


def load_grid(filename):
    grid = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # '1' は使えるセル、その他は使えない
            grid.append([True if ch == "1" else False for ch in line])
    return grid


def can_place(block_pattern, grid, occupied, i, j):
    n_rows = len(block_pattern)
    n_cols = len(block_pattern[0])
    if i + n_rows > len(grid) or j + n_cols > len(grid[0]):
        return False
    for di in range(n_rows):
        for dj in range(n_cols):
            if block_pattern[di][dj] == 1:
                if not grid[i + di][j + dj] or occupied[i + di][j + dj] is not None:
                    return False
    return True


def place_block(block_pattern, occupied, marker, i, j):
    n_rows = len(block_pattern)
    n_cols = len(block_pattern[0])
    for di in range(n_rows):
        for dj in range(n_cols):
            if block_pattern[di][dj] == 1:
                occupied[i + di][j + dj] = marker


def print_board(occupied):
    for row in occupied:
        line = ""
        for cell in row:
            if cell is None:
                line += "."
            else:
                line += str(cell)
        print(line)


def solve(grid, blocks):
    # occupied: 有効セルはNone, 無効セルは '#' とする
    occupied = [[None if cell else "#" for cell in row] for row in grid]

    # best solutionを記録する辞書
    best = {"score": -1, "occupied": None, "placements": None}

    # ブロックをスコアが高い順にソートし、そのcountをremainingに格納
    blocks_sorted = sorted(blocks, key=lambda b: b.get("score", 0), reverse=True)
    remaining = [b.get("count", 0) for b in blocks_sorted]

    def find_next_empty():
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] and occupied[i][j] is None:
                    return i, j
        return None

    def backtrack(current_score, placements):
        # 枝刈り: 残り可能なスコアの上限を計算
        potential = current_score + sum(
            r * block.get("score", 0) for r, block in zip(remaining, blocks_sorted)
        )
        if potential <= best["score"]:
            return

        pos = find_next_empty()
        # 全ての有効セルが埋まっている場合、解を更新
        if pos is None:
            if current_score > best["score"]:
                best["score"] = current_score
                best["occupied"] = [row[:] for row in occupied]
                best["placements"] = placements.copy()
            return

        i, j = pos
        # 各ブロックを試す（スコアが高い順）
        for idx, block in enumerate(blocks_sorted):
            if remaining[idx] > 0:
                pattern = block.get("pattern")
                for use_flip in [False, True]:
                    # 左右反転の候補パターンを生成
                    candidate_pattern = (
                        pattern if not use_flip else [row[::-1] for row in pattern]
                    )
                    if can_place(candidate_pattern, grid, occupied, i, j):
                        mark = block.get("name")[0]
                        placed_positions = []
                        for di in range(len(candidate_pattern)):
                            for dj in range(len(candidate_pattern[0])):
                                if candidate_pattern[di][dj] == 1:
                                    occupied[i + di][j + dj] = mark
                                    placed_positions.append((i + di, j + dj))
                        remaining[idx] -= 1
                        placements.append(
                            {
                                "name": block.get("name"),
                                "position": (i, j),
                                "score": block.get("score", 0),
                                "flip": use_flip,
                            }
                        )
                        backtrack(current_score + block.get("score", 0), placements)
                        # 戻す
                        for a, b in placed_positions:
                            occupied[a][b] = None
                        placements.pop()
                        remaining[idx] += 1

    backtrack(0, [])
    if best["occupied"] is None:
        print("解が見つかりませんでした")
        return None, 0, []
    else:
        return best["occupied"], best["score"], best["placements"]


def main():
    if len(sys.argv) < 3:
        print("使い方: python main.py grid_file blocks_file")
        sys.exit(1)
    grid_file = sys.argv[1]
    blocks_file = sys.argv[2]
    grid = load_grid(grid_file)
    blocks = load_blocks(blocks_file)
    occupied, total_score, placements = solve(grid, blocks)
    print("最終スコア:", total_score)
    print("盤面配置:")
    print_board(occupied)
    print("各ブロックの配置:")
    for p in placements:
        print(p)


if __name__ == "__main__":
    main()

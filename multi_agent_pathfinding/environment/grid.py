"""
网格环境类
"""

import numpy as np
from typing import List, Tuple, Dict, Set


class GridEnvironment:
    """网格环境类，管理地图和移动"""

    # 移动方向（上，右，下，左，等待）
    MOVES = [(0, 0), (-1, 0), (0, 1), (1, 0), (0, -1)]
    MOVE_NAMES = ['Wait', 'Up', 'Right', 'Down', 'Left']

    def __init__(self, grid: np.ndarray):
        self.grid = grid
        self.height, self.width = grid.shape

    def get_neighbors(self, state: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        """
        获取相邻状态（时空状态）
        state: (x, y, t)
        返回: 相邻状态列表
        """
        x, y, t = state
        neighbors = []

        for dx, dy in [(0, 0), (-1, 0), (0, 1), (1, 0), (0, -1)]:
            nx, ny = x + dx, y + dy

            # 检查边界和障碍物
            if 0 <= nx < self.height and 0 <= ny < self.width:
                if self.grid[nx, ny] == 0:  # 可通行
                    neighbors.append((nx, ny, t + 1))

        return neighbors

    def get_manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """计算曼哈顿距离"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def check_collision(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        """检查两个位置是否冲突（占据同一位置）"""
        return pos1 == pos2

    def check_edge_collision(self, pos1: Tuple[int, int], next_pos1: Tuple[int, int],
                             pos2: Tuple[int, int], next_pos2: Tuple[int, int]) -> bool:
        """检查边冲突（交换位置）"""
        return (pos1 == next_pos2 and pos2 == next_pos1)

    def is_valid_state(self, state: Tuple[int, int]) -> bool:
        """检查状态是否有效"""
        x, y = state
        return (0 <= x < self.height and 0 <= y < self.width and
                self.grid[x, y] == 0)
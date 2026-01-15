"""
地图加载和解析模块
"""

import numpy as np


class MapLoader:
    """加载和解析地图文件"""

    def __init__(self, file_path):
        self.file_path = file_path
        self.width = 0
        self.height = 0
        self.grid = None

    def load_map(self):
        """加载地图文件"""
        with open(self.file_path, 'r') as f:
            lines = f.readlines()

        # 解析地图头信息
        map_data_start = 0
        for i, line in enumerate(lines):
            if line.startswith('width'):
                self.width = int(line.split()[1])
            elif line.startswith('height'):
                self.height = int(line.split()[1])
            elif line.strip() == 'map':
                map_data_start = i + 1
                break

        # 解析地图数据
        self.grid = np.zeros((self.height, self.width), dtype=int)

        for i in range(self.height):
            line = lines[map_data_start + i].strip()
            for j, char in enumerate(line):
                if char == '@':  # 障碍物
                    self.grid[i, j] = 1
                elif char == '.':  # 可通行区域
                    self.grid[i, j] = 0
                else:  # 其他字符视为障碍物
                    self.grid[i, j] = 1

        return self.grid

    def get_free_cells(self):
        """获取所有可通行单元格"""
        free_cells = []
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i, j] == 0:
                    free_cells.append((i, j))
        return free_cells

    def is_valid_position(self, x, y):
        """检查位置是否有效"""
        if 0 <= x < self.height and 0 <= y < self.width:
            return self.grid[x, y] == 0
        return False
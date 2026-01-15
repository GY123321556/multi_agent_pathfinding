"""
时空A*算法实现
"""

import heapq
import numpy as np
from typing import List, Tuple, Dict, Set, Optional
from collections import defaultdict

from environment.grid import GridEnvironment
from algorithms.constraints import ConstraintsSet


class SippNode:
    """时空A*节点"""

    def __init__(self, x: int, y: int, t: int, g: float = 0, h: float = 0,
                 parent=None, interval_start: int = 0, interval_end: int = float('inf')):
        self.x = x
        self.y = y
        self.t = t
        self.g = g  # 实际成本
        self.h = h  # 启发式成本
        self.f = g + h  # 总成本
        self.parent = parent
        self.interval_start = interval_start
        self.interval_end = interval_end

    def __lt__(self, other):
        return self.f < other.f

    def __eq__(self, other):
        return (self.x == other.x and self.y == other.y and
                self.t == other.t)

    def __hash__(self):
        return hash((self.x, self.y, self.t))

    def __repr__(self):
        return f"Node({self.x},{self.y},t={self.t},f={self.f:.2f})"


class SpaceTimeAStar:
    """时空A*算法"""

    def __init__(self, environment: GridEnvironment, agent_id: int,
                 constraints: ConstraintsSet, config):
        self.env = environment
        self.agent_id = agent_id
        self.constraints = constraints
        self.config = config

    def search(self, start: Tuple[int, int], goal: Tuple[int, int],
               max_time: int = 100) -> List[Tuple[int, int]]:
        """
        执行时空A*搜索
        返回路径（位置列表）
        """
        # 初始化开放列表和关闭列表
        open_list = []
        closed_set = set()

        # 创建起始节点
        start_node = SippNode(start[0], start[1], 0, 0,
                              self.env.get_manhattan_distance(start, goal))
        heapq.heappush(open_list, start_node)

        # 用于快速查找的节点字典
        node_dict = {(start_node.x, start_node.y, start_node.t): start_node}

        while open_list:
            # 获取f值最小的节点
            current_node = heapq.heappop(open_list)

            # 检查是否到达目标
            if (current_node.x, current_node.y) == goal:
                return self._reconstruct_path(current_node)

            # 检查是否超过最大时间
            if current_node.t >= max_time:
                continue

            # 添加到关闭列表
            closed_set.add((current_node.x, current_node.y, current_node.t))

            # 生成后继节点
            neighbors = self.env.get_neighbors((current_node.x, current_node.y, current_node.t))

            for nx, ny, nt in neighbors:
                # 检查顶点约束
                if self.constraints.is_constrained(self.agent_id, (nx, ny), nt):
                    continue

                # 检查边约束
                if self.constraints.is_edge_constrained(self.agent_id,
                                                        (current_node.x, current_node.y),
                                                        (nx, ny), current_node.t):
                    continue

                # 计算成本
                g = current_node.g + 1  # 每个移动成本为1
                h = self.env.get_manhattan_distance((nx, ny), goal)

                # 创建新节点
                new_node = SippNode(nx, ny, nt, g, h, current_node)

                # 检查是否在关闭列表中
                if (nx, ny, nt) in closed_set:
                    continue

                # 检查是否在开放列表中
                existing_node = node_dict.get((nx, ny, nt))
                if existing_node:
                    if new_node.g < existing_node.g:
                        existing_node.g = new_node.g
                        existing_node.f = new_node.g + existing_node.h
                        existing_node.parent = new_node.parent
                        heapq.heapify(open_list)
                else:
                    heapq.heappush(open_list, new_node)
                    node_dict[(nx, ny, nt)] = new_node

        # 如果没有找到路径，返回空列表
        return []

    def _reconstruct_path(self, goal_node: SippNode) -> List[Tuple[int, int]]:
        """重建路径"""
        path = []
        current = goal_node

        while current is not None:
            path.append((current.x, current.y))
            current = current.parent

        # 反转路径（从起点到终点）
        path.reverse()

        # 如果路径太短，确保至少有一个点
        if not path:
            path = [goal_node.x, goal_node.y]

        return path
"""
智能体管理器
"""

import random
from typing import List, Tuple, Dict
import numpy as np


class Agent:
    """智能体类"""

    def __init__(self, agent_id: int, start: Tuple[int, int], goal: Tuple[int, int]):
        self.id = agent_id
        self.start = start
        self.goal = goal
        self.path = []
        self.cost = 0

    def __repr__(self):
        return f"Agent{self.id}(start={self.start}, goal={self.goal})"


class AgentManager:
    """智能体管理器"""

    def __init__(self, grid: np.ndarray):
        self.grid = grid
        self.height, self.width = grid.shape
        self.agents = []

    def generate_random_agents(self, num_agents: int, min_distance: int = 10) -> List[Agent]:
        """随机生成智能体的起点和终点"""
        free_cells = self._get_free_cells()

        if len(free_cells) < 2 * num_agents:
            raise ValueError("Not enough free cells for all agents")

        # 打乱可用单元格
        random.shuffle(free_cells)

        # 选择起点和终点，确保它们之间有最小距离
        starts_goals = []
        for i in range(num_agents):
            valid_pair = False
            attempts = 0

            while not valid_pair and attempts < 100:
                start_idx = random.randint(0, len(free_cells) - 1)
                goal_idx = random.randint(0, len(free_cells) - 1)

                if start_idx != goal_idx:
                    start = free_cells[start_idx]
                    goal = free_cells[goal_idx]

                    # 检查距离是否足够
                    distance = abs(start[0] - goal[0]) + abs(start[1] - goal[1])
                    if distance >= min_distance:
                        # 检查是否与其他起点/终点太近
                        too_close = False
                        for other_start, other_goal in starts_goals:
                            if (abs(start[0] - other_start[0]) + abs(start[1] - other_start[1]) < min_distance // 2 or
                                    abs(goal[0] - other_goal[0]) + abs(goal[1] - other_goal[1]) < min_distance // 2):
                                too_close = True
                                break

                        if not too_close:
                            starts_goals.append((start, goal))
                            valid_pair = True

                attempts += 1

            if not valid_pair:
                # 如果找不到合适的对，使用任意一对
                start = free_cells[i * 2]
                goal = free_cells[i * 2 + 1]
                starts_goals.append((start, goal))

        # 创建智能体
        self.agents = []
        for i, (start, goal) in enumerate(starts_goals):
            agent = Agent(i, start, goal)
            self.agents.append(agent)

        return self.agents

    def _get_free_cells(self) -> List[Tuple[int, int]]:
        """获取所有可通行单元格"""
        free_cells = []
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i, j] == 0:
                    free_cells.append((i, j))
        return free_cells

    def get_agent_paths(self) -> Dict[int, List[Tuple[int, int]]]:
        """获取所有智能体的路径"""
        paths = {}
        for agent in self.agents:
            paths[agent.id] = agent.path
        return paths

    def get_makespan(self) -> int:
        """计算makespan（最长路径长度）"""
        if not self.agents:
            return 0
        return max(len(agent.path) for agent in self.agents if agent.path)

    def get_sum_of_costs(self) -> int:
        """计算总成本"""
        return sum(agent.cost for agent in self.agents if agent.path)
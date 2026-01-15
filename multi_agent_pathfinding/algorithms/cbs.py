"""
冲突基础搜索 (CBS) 算法
"""

import heapq
import copy
from typing import List, Dict, Tuple, Set, Optional
from collections import defaultdict

from environment.grid import GridEnvironment
from environment.agent_manager import Agent
from algorithms.astar import SpaceTimeAStar
from algorithms.constraints import ConstraintsSet, VertexConstraint, EdgeConstraint


class CBSNode:
    """CBS节点"""

    def __init__(self, constraints: ConstraintsSet = None,
                 solutions: Dict[int, List[Tuple[int, int]]] = None,
                 cost: int = 0):
        self.constraints = constraints if constraints else ConstraintsSet()
        self.solutions = solutions if solutions else {}
        self.cost = cost
        self.conflicts = []

    def __lt__(self, other):
        return self.cost < other.cost


class Conflict:
    """冲突类"""

    def __init__(self, agent1: int, agent2: int,
                 position: Tuple[int, int], time: int,
                 conflict_type: str = "vertex"):
        self.agent1 = agent1
        self.agent2 = agent2
        self.position = position
        self.time = time
        self.conflict_type = conflict_type

    def __repr__(self):
        return f"Conflict({self.agent1},{self.agent2},pos={self.position},t={self.time},{self.conflict_type})"


class CBS:
    """冲突基础搜索算法"""

    def __init__(self, environment: GridEnvironment, agents: List[Agent], config):
        self.env = environment
        self.agents = agents
        self.config = config

    def search(self) -> Dict[int, List[Tuple[int, int]]]:
        """执行CBS搜索"""
        # 初始化根节点
        root = CBSNode()
        root.solutions = self._find_initial_solutions(root.constraints)
        root.cost = self._calculate_solution_cost(root.solutions)
        root.conflicts = self._find_conflicts(root.solutions)

        # 初始化开放列表（优先队列）
        open_list = []
        heapq.heappush(open_list, root)

        iteration = 0

        while open_list and iteration < self.config.CBS_MAX_ITERATIONS:
            iteration += 1

            # 获取成本最低的节点
            current_node = heapq.heappop(open_list)

            # 如果没有冲突，返回解决方案
            if not current_node.conflicts:
                return current_node.solutions

            # 选择第一个冲突进行解决
            conflict = current_node.conflicts[0]

            # 为每个冲突的智能体创建新节点
            for agent_id in [conflict.agent1, conflict.agent2]:
                # 创建新的约束集
                new_constraints = copy.deepcopy(current_node.constraints)

                # 添加新约束
                if conflict.conflict_type == "vertex":
                    new_constraints.add_vertex_constraint(
                        VertexConstraint(agent_id, conflict.position, conflict.time)
                    )
                elif conflict.conflict_type == "edge":
                    # 对于边冲突，我们需要知道具体的方向
                    # 这里简化处理，假设是顶点冲突
                    new_constraints.add_vertex_constraint(
                        VertexConstraint(agent_id, conflict.position, conflict.time)
                    )

                # 创建新节点
                new_node = CBSNode(new_constraints)

                # 重新规划受影响的智能体
                new_node.solutions = copy.deepcopy(current_node.solutions)

                # 重新规划受影响智能体的路径
                self._replan_agent(agent_id, new_node)

                # 计算新节点的成本
                new_node.cost = self._calculate_solution_cost(new_node.solutions)

                # 查找新解决方案中的冲突
                new_node.conflicts = self._find_conflicts(new_node.solutions)

                # 如果没有冲突，返回解决方案
                if not new_node.conflicts:
                    return new_node.solutions

                # 添加到开放列表
                heapq.heappush(open_list, new_node)

        # 如果达到最大迭代次数，返回当前最佳解决方案
        if open_list:
            best_node = heapq.heappop(open_list)
            return best_node.solutions

        return {}

    def _find_initial_solutions(self, constraints: ConstraintsSet) -> Dict[int, List[Tuple[int, int]]]:
        """为每个智能体找到初始解决方案（无约束）"""
        solutions = {}

        for agent in self.agents:
            astar = SpaceTimeAStar(self.env, agent.id, constraints, self.config)
            path = astar.search(agent.start, agent.goal, self.config.MAX_TIME_STEPS)

            if path:
                solutions[agent.id] = path
                agent.path = path
                agent.cost = len(path) - 1  # 成本是移动次数

        return solutions

    def _replan_agent(self, agent_id: int, node: CBSNode):
        """重新规划指定智能体的路径"""
        agent = self.agents[agent_id]
        astar = SpaceTimeAStar(self.env, agent_id, node.constraints, self.config)
        new_path = astar.search(agent.start, agent.goal, self.config.MAX_TIME_STEPS)

        if new_path:
            node.solutions[agent_id] = new_path
            agent.path = new_path
            agent.cost = len(new_path) - 1

    def _calculate_solution_cost(self, solutions: Dict[int, List[Tuple[int, int]]]) -> int:
        """计算解决方案的总成本"""
        total_cost = 0
        for agent_id, path in solutions.items():
            total_cost += len(path) - 1  # 每个路径的成本是移动次数
        return total_cost

    def _find_conflicts(self, solutions: Dict[int, List[Tuple[int, int]]]) -> List[Conflict]:
        """查找解决方案中的所有冲突"""
        conflicts = []

        # 将路径扩展到相同长度
        max_length = max(len(path) for path in solutions.values())
        extended_paths = {}

        for agent_id, path in solutions.items():
            extended_path = list(path)
            if len(extended_path) < max_length:
                # 用最后一个位置填充
                extended_path.extend([extended_path[-1]] * (max_length - len(extended_path)))
            extended_paths[agent_id] = extended_path

        # 检查每个时间步的冲突
        for t in range(max_length):
            positions = {}

            # 收集所有智能体在时间t的位置
            for agent_id, path in extended_paths.items():
                if t < len(path):
                    positions[agent_id] = path[t]

            # 检查顶点冲突
            for i, (agent1, pos1) in enumerate(positions.items()):
                for agent2, pos2 in list(positions.items())[i + 1:]:
                    if pos1 == pos2:
                        conflicts.append(Conflict(agent1, agent2, pos1, t, "vertex"))

            # 检查边冲突（交换位置）
            if t > 0:
                for i, (agent1, pos1) in enumerate(positions.items()):
                    prev_pos1 = extended_paths[agent1][t - 1] if t - 1 < len(extended_paths[agent1]) else pos1
                    for agent2, pos2 in list(positions.items())[i + 1:]:
                        prev_pos2 = extended_paths[agent2][t - 1] if t - 1 < len(extended_paths[agent2]) else pos2

                        if prev_pos1 == pos2 and prev_pos2 == pos1:
                            conflicts.append(Conflict(agent1, agent2, pos1, t, "edge"))

        return conflicts
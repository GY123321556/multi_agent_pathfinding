"""
性能指标计算
"""

from typing import Dict, List, Tuple
import numpy as np


class Metrics:
    """性能指标计算类"""

    @staticmethod
    def calculate_makespan(paths: Dict[int, List[Tuple[int, int]]]) -> int:
        """计算makespan（最长路径长度）"""
        if not paths:
            return 0
        return max(len(path) - 1 for path in paths.values())  # -1因为起点不算一步

    @staticmethod
    def calculate_sum_of_costs(paths: Dict[int, List[Tuple[int, int]]]) -> int:
        """计算总成本（所有路径长度之和）"""
        return sum(len(path) - 1 for path in paths.values())  # -1因为起点不算一步

    @staticmethod
    def calculate_average_cost(paths: Dict[int, List[Tuple[int, int]]]) -> float:
        """计算平均成本"""
        if not paths:
            return 0.0
        return Metrics.calculate_sum_of_costs(paths) / len(paths)

    @staticmethod
    def check_collisions(paths: Dict[int, List[Tuple[int, int]]]) -> List[Dict]:
        """检查路径中的冲突"""
        collisions = []

        if not paths:
            return collisions

        # 将路径扩展到相同长度
        max_length = max(len(path) for path in paths.values())
        extended_paths = {}

        for agent_id, path in paths.items():
            extended_path = list(path)
            if len(extended_path) < max_length:
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
                        collisions.append({
                            'type': 'vertex',
                            'agents': (agent1, agent2),
                            'position': pos1,
                            'time': t
                        })

            # 检查边冲突（交换位置）
            if t > 0:
                for i, (agent1, pos1) in enumerate(positions.items()):
                    prev_pos1 = extended_paths[agent1][t - 1] if t - 1 < len(extended_paths[agent1]) else pos1
                    for agent2, pos2 in list(positions.items())[i + 1:]:
                        prev_pos2 = extended_paths[agent2][t - 1] if t - 1 < len(extended_paths[agent2]) else pos2

                        if prev_pos1 == pos2 and prev_pos2 == pos1:
                            collisions.append({
                                'type': 'edge',
                                'agents': (agent1, agent2),
                                'positions': (prev_pos1, pos1),
                                'time': t
                            })

        return collisions

    @staticmethod
    def calculate_success_rate(paths: Dict[int, List[Tuple[int, int]]],
                               agents: List) -> float:
        """计算成功率（到达目标的智能体比例）"""
        if not agents:
            return 0.0

        successful = 0
        for agent in agents:
            if agent.path and len(agent.path) > 0:
                if agent.path[-1] == agent.goal:
                    successful += 1

        return successful / len(agents)
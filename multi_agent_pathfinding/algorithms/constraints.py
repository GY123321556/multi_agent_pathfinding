"""
约束管理模块
"""

from typing import Tuple, Dict, List, Set, Optional


class Constraint:
    """约束基类"""

    def __init__(self, agent_id: int, position: Tuple[int, int], time: int):
        self.agent_id = agent_id
        self.position = position
        self.time = time

    def __repr__(self):
        return f"Constraint(agent={self.agent_id}, pos={self.position}, t={self.time})"

    def __eq__(self, other):
        return (self.agent_id == other.agent_id and
                self.position == other.position and
                self.time == other.time)

    def __hash__(self):
        return hash((self.agent_id, self.position, self.time))


class VertexConstraint(Constraint):
    """顶点约束：智能体在特定时间不能位于特定位置"""
    pass


class EdgeConstraint(Constraint):
    """边约束：智能体在特定时间不能从位置A移动到位置B"""

    def __init__(self, agent_id: int, from_pos: Tuple[int, int],
                 to_pos: Tuple[int, int], time: int):
        super().__init__(agent_id, (from_pos, to_pos), time)
        self.from_pos = from_pos
        self.to_pos = to_pos

    def __repr__(self):
        return f"EdgeConstraint(agent={self.agent_id}, {self.from_pos}->{self.to_pos}, t={self.time})"


class ConstraintsSet:
    """约束集合"""

    def __init__(self):
        self.vertex_constraints: Set[VertexConstraint] = set()
        self.edge_constraints: Set[EdgeConstraint] = set()

    def add_vertex_constraint(self, constraint: VertexConstraint):
        self.vertex_constraints.add(constraint)

    def add_edge_constraint(self, constraint: EdgeConstraint):
        self.edge_constraints.add(constraint)

    def is_constrained(self, agent_id: int, position: Tuple[int, int], time: int) -> bool:
        """检查是否有顶点约束"""
        constraint = VertexConstraint(agent_id, position, time)
        return constraint in self.vertex_constraints

    def is_edge_constrained(self, agent_id: int, from_pos: Tuple[int, int],
                            to_pos: Tuple[int, int], time: int) -> bool:
        """检查是否有边约束"""
        constraint = EdgeConstraint(agent_id, from_pos, to_pos, time)
        return constraint in self.edge_constraints

    def get_all_constraints(self):
        """获取所有约束"""
        return list(self.vertex_constraints) + list(self.edge_constraints)

    def __repr__(self):
        return f"ConstraintsSet(vertex={len(self.vertex_constraints)}, edge={len(self.edge_constraints)})"
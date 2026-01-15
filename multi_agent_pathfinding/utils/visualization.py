"""
可视化工具
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from typing import List, Tuple, Dict
import matplotlib.animation as animation


class Visualizer:
    """可视化类"""

    def __init__(self, grid: np.ndarray, agent_colors=None):
        self.grid = grid
        self.height, self.width = grid.shape

        # 智能体颜色
        if agent_colors is None:
            self.agent_colors = plt.cm.tab10.colors
        else:
            self.agent_colors = agent_colors

        # 创建图形
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.set_aspect('equal')
        self.ax.invert_yaxis()  # 使y轴向下增加

        # 绘制网格
        self._draw_grid()

    def _draw_grid(self):
        """绘制网格和障碍物"""
        # 绘制障碍物
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i, j] == 1:  # 障碍物
                    rect = patches.Rectangle(
                        (j, i), 1, 1,
                        linewidth=0.5,
                        edgecolor='black',
                        facecolor='black',
                        alpha=0.7
                    )
                    self.ax.add_patch(rect)
                else:  # 可通行区域
                    rect = patches.Rectangle(
                        (j, i), 1, 1,
                        linewidth=0.2,
                        edgecolor='gray',
                        facecolor='white'
                    )
                    self.ax.add_patch(rect)

        # 添加网格线
        self.ax.set_xticks(np.arange(0, self.width + 1, 1))
        self.ax.set_yticks(np.arange(0, self.height + 1, 1))
        self.ax.grid(which='both', color='gray', linestyle='-', linewidth=0.2, alpha=0.3)
        self.ax.tick_params(which='both', length=0)

    def plot_paths(self, agents: List, paths: Dict[int, List[Tuple[int, int]]],
                   show_start_goal: bool = True):
        """绘制所有智能体的路径"""

        # 绘制起点和终点
        if show_start_goal:
            for agent in agents:
                # 起点
                start_rect = patches.Rectangle(
                    (agent.start[1], agent.start[0]), 1, 1,
                    linewidth=1, edgecolor='green', facecolor='green', alpha=0.7
                )
                self.ax.add_patch(start_rect)
                self.ax.text(agent.start[1] + 0.5, agent.start[0] + 0.5,
                             f"S{agent.id}", color='white',
                             ha='center', va='center', fontsize=8, fontweight='bold')

                # 终点
                goal_rect = patches.Rectangle(
                    (agent.goal[1], agent.goal[0]), 1, 1,
                    linewidth=1, edgecolor='red', facecolor='red', alpha=0.7
                )
                self.ax.add_patch(goal_rect)
                self.ax.text(agent.goal[1] + 0.5, agent.goal[0] + 0.5,
                             f"G{agent.id}", color='white',
                             ha='center', va='center', fontsize=8, fontweight='bold')

        # 绘制路径
        for agent_id, path in paths.items():
            if not path:
                continue

            # 获取颜色
            color = self.agent_colors[agent_id % len(self.agent_colors)]

            # 绘制路径线
            x_coords = [p[1] + 0.5 for p in path]
            y_coords = [p[0] + 0.5 for p in path]

            self.ax.plot(x_coords, y_coords, color=color, linewidth=2, alpha=0.7)

            # 绘制路径点
            for i, (x, y) in enumerate(path):
                if i == 0 or i == len(path) - 1:
                    continue  # 跳过起点和终点（已经有标记）

                circle = patches.Circle(
                    (y + 0.5, x + 0.5), 0.2,
                    facecolor=color, edgecolor='black', linewidth=0.5, alpha=0.5
                )
                self.ax.add_patch(circle)

        plt.title("Multi-Agent Path Planning Results")
        plt.tight_layout()

    def animate_paths(self, agents: List, paths: Dict[int, List[Tuple[int, int]]],
                      interval: int = 200):
        """动画显示路径执行过程"""

        # 找出最长路径
        max_length = max(len(path) for path in paths.values())

        # 扩展所有路径到相同长度
        extended_paths = {}
        for agent_id, path in paths.items():
            extended_path = list(path)
            if len(extended_path) < max_length:
                extended_path.extend([extended_path[-1]] * (max_length - len(extended_path)))
            extended_paths[agent_id] = extended_path

        # 创建动画函数
        def update(frame):
            self.ax.clear()
            self._draw_grid()

            # 绘制起点和终点
            for agent in agents:
                # 起点
                start_rect = patches.Rectangle(
                    (agent.start[1], agent.start[0]), 1, 1,
                    linewidth=1, edgecolor='green', facecolor='green', alpha=0.7
                )
                self.ax.add_patch(start_rect)
                self.ax.text(agent.start[1] + 0.5, agent.start[0] + 0.5,
                             f"S{agent.id}", color='white',
                             ha='center', va='center', fontsize=8, fontweight='bold')

                # 终点
                goal_rect = patches.Rectangle(
                    (agent.goal[1], agent.goal[0]), 1, 1,
                    linewidth=1, edgecolor='red', facecolor='red', alpha=0.7
                )
                self.ax.add_patch(goal_rect)
                self.ax.text(agent.goal[1] + 0.5, agent.goal[0] + 0.5,
                             f"G{agent.id}", color='white',
                             ha='center', va='center', fontsize=8, fontweight='bold')

            # 绘制智能体当前位置
            for agent_id, path in extended_paths.items():
                if frame < len(path):
                    x, y = path[frame]
                    color = self.agent_colors[agent_id % len(self.agent_colors)]

                    # 绘制智能体
                    circle = patches.Circle(
                        (y + 0.5, x + 0.5), 0.4,
                        facecolor=color, edgecolor='black', linewidth=1.5
                    )
                    self.ax.add_patch(circle)

                    # 添加智能体ID
                    self.ax.text(y + 0.5, x + 0.5, str(agent_id),
                                 color='white', ha='center', va='center',
                                 fontsize=10, fontweight='bold')

            self.ax.set_title(f"Time Step: {frame}")

            return self.ax

        # 创建动画
        ani = animation.FuncAnimation(
            self.fig, update, frames=max_length,
            interval=interval, repeat=True
        )

        plt.tight_layout()
        return ani

    def save_animation(self, ani, filename: str, fps: int = 5):
        """保存动画为文件"""
        from matplotlib.animation import FFMpegWriter

        writer = FFMpegWriter(fps=fps, metadata=dict(artist='MAPF'), bitrate=1800)
        ani.save(filename, writer=writer)

    def show(self):
        """显示图形"""
        plt.show()
"""
交互式演示脚本 - 集成新的可视化系统
专门为八个智能体设计
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np
import time
from config import Config
from environment.map_loader import MapLoader
from environment.grid import GridEnvironment
from environment.agent_manager import AgentManager
from algorithms.cbs import CBS
from utils.visualization import EnhancedVisualizer
from utils.metrics import Metrics


class EightAgentDemo:
    """八个智能体演示类"""

    def __init__(self):
        self.config = Config()
        self.grid = None
        self.env = None
        self.agents = []
        self.solutions = {}
        self.visualizer = None

    def load_map(self):
        """加载地图"""
        print("Loading map...")
        map_loader = MapLoader(self.config.MAP_FILE)
        self.grid = map_loader.load_map()
        self.env = GridEnvironment(self.grid)
        print(f"✓ Map loaded: {self.grid.shape[0]} x {self.grid.shape[1]}")
        return self.grid is not None

    def generate_eight_agents(self):
        """生成八个智能体"""
        print("\nGenerating 8 agents with good separation...")
        agent_manager = AgentManager(self.grid)

        # 尝试多次以获得好的分布
        best_agents = []
        best_score = -1

        for attempt in range(5):
            agents = agent_manager.generate_random_agents(8, min_distance=30)

            # 计算分布得分（起点和终点之间的距离总和）
            score = 0
            for agent in agents:
                # 起点到终点的距离
                dist = abs(agent.start[0] - agent.goal[0]) + abs(agent.start[1] - agent.goal[1])
                score += dist

            if score > best_score:
                best_score = score
                best_agents = agents

        self.agents = best_agents

        print("Agents generated:")
        for agent in self.agents:
            dist = abs(agent.start[0] - agent.goal[0]) + abs(agent.start[1] - agent.goal[1])
            print(f"  Agent {agent.id}: Start={agent.start}, Goal={agent.goal}, Distance={dist}")

        return len(self.agents) == 8

    def plan_paths(self):
        """规划八个智能体的路径"""
        if len(self.agents) != 8:
            print("Error: Need exactly 8 agents!")
            return False

        print("\nPlanning paths for 8 agents using CBS algorithm...")
        print("This may take a while...")
        start_time = time.time()

        cbs = CBS(self.env, self.agents, self.config)
        self.solutions = cbs.search()

        end_time = time.time()
        computation_time = end_time - start_time

        print(f"✓ Planning completed in {computation_time:.2f} seconds")

        # 更新智能体路径
        success_count = 0
        for agent in self.agents:
            if agent.id in self.solutions:
                agent.path = self.solutions[agent.id]
                agent.cost = len(self.solutions[agent.id]) - 1
                success_count += 1
                print(f"  Agent {agent.id}: ✓ Path found ({len(agent.path)} steps)")
            else:
                print(f"  Agent {agent.id}: ✗ No path found!")
                agent.path = [agent.start]

        print(f"\n✓ Paths found for {success_count}/8 agents")
        return success_count > 0

    def show_metrics(self):
        """显示性能指标"""
        if not self.solutions:
            print("No solutions to analyze!")
            return

        print("\n" + "=" * 60)
        print("PERFORMANCE METRICS")
        print("=" * 60)

        makespan = Metrics.calculate_makespan(self.solutions)
        sum_of_costs = Metrics.calculate_sum_of_costs(self.solutions)
        average_cost = Metrics.calculate_average_cost(self.solutions)
        success_rate = Metrics.calculate_success_rate(self.solutions, self.agents)

        print(f"Makespan (longest path): {makespan}")
        print(f"Sum of Costs (total steps): {sum_of_costs}")
        print(f"Average Cost: {average_cost:.1f}")
        print(f"Success Rate: {success_rate:.1%}")

        collisions = Metrics.check_collisions(self.solutions)
        if collisions:
            print(f"\n⚠  Found {len(collisions)} collisions!")
        else:
            print(f"\n✓ No collisions found!")

        print("=" * 60)

    def show_animation(self, speed=1.0, save=False):
        """显示八个智能体同时移动的动画"""
        if not self.visualizer:
            self.visualizer = EnhancedVisualizer(self.grid, self.config)

        print("\nCreating 8-agent simultaneous movement animation...")
        interval = int(self.config.ANIMATION_INTERVAL / speed)

        animation = self.visualizer.animate(self.agents, self.solutions, interval=interval)

        if save:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"eight_agents_animation_{timestamp}.mp4"
            print(f"Saving animation to {filename}...")
            self.visualizer.save_animation_to_file(filename, fps=int(10 * speed))

        print("\n" + "=" * 60)
        print("ANIMATION CONTROLS:")
        print("- The animation shows all 8 agents moving simultaneously")
        print("- Each agent has a unique color")
        print("- Left panel: Main map with agents, trails, and paths")
        print("- Top right: Agent status (Waiting, Moving, Arrived)")
        print("- Bottom: Progress bar and statistics")
        print("=" * 60)

        print("\nDisplaying animation...")
        self.visualizer.show_animation()

    def show_summary(self):
        """显示总结视图"""
        if not self.visualizer:
            self.visualizer = EnhancedVisualizer(self.grid, self.config)

        print("\nShowing summary view of all 8 agents...")
        self.visualizer.create_summary_view(self.agents, self.solutions)

    def run_interactive_demo(self):
        """运行交互式演示"""
        print("=" * 60)
        print("8-AGENT PATH PLANNING DEMONSTRATION")
        print("=" * 60)
        print("This demo will:")
        print("1. Load the Berlin map")
        print("2. Generate 8 agents with good separation")
        print("3. Plan collision-free paths using CBS algorithm")
        print("4. Show animated visualization of all agents moving simultaneously")
        print("=" * 60)

        input("\nPress Enter to begin...")

        # 步骤1: 加载地图
        if not self.load_map():
            print("Failed to load map! Exiting...")
            return

        # 步骤2: 生成八个智能体
        if not self.generate_eight_agents():
            print("Failed to generate 8 agents! Exiting...")
            return

        # 步骤3: 规划路径
        input("\nPress Enter to start path planning...")
        if not self.plan_paths():
            print("Path planning failed! Exiting...")
            return

        # 步骤4: 显示性能指标
        self.show_metrics()

        # 步骤5: 交互式菜单
        while True:
            print("\n" + "=" * 60)
            print("VISUALIZATION MENU")
            print("=" * 60)
            print("1. 🎬 Show Animation (8 agents moving simultaneously)")
            print("2. 🚀 Fast Animation (2x speed)")
            print("3. 🐢 Slow Animation (0.5x speed)")
            print("4. 📊 Show Summary View (all paths)")
            print("5. 💾 Save Animation to File")
            print("6. 📈 Show Metrics Again")
            print("7. 🔄 Regenerate Agents and Replan")
            print("8. 🚪 Exit")
            print("=" * 60)

            choice = input("\nSelect an option (1-8): ").strip()

            if choice == "1":
                self.show_animation(speed=1.0)
            elif choice == "2":
                self.show_animation(speed=2.0)
            elif choice == "3":
                self.show_animation(speed=0.5)
            elif choice == "4":
                self.show_summary()
            elif choice == "5":
                save_choice = input("Save animation? (y/n): ").strip().lower()
                if save_choice == 'y':
                    self.show_animation(save=True)
                else:
                    self.show_animation()
            elif choice == "6":
                self.show_metrics()
            elif choice == "7":
                print("\nRegenerating agents and replanning...")
                if not self.generate_eight_agents():
                    print("Failed to regenerate agents!")
                    continue
                if not self.plan_paths():
                    print("Path planning failed!")
                    continue
                self.show_metrics()
            elif choice == "8":
                print("\nThank you for using the 8-Agent Path Planning Demo!")
                break
            else:
                print("Invalid choice. Please select 1-8.")

            # 关闭图形窗口
            plt.close('all')

    def run_automatic_demo(self):
        """运行自动演示（无用户交互）"""
        print("Running automatic 8-agent demo...")

        # 加载地图
        if not self.load_map():
            return

        # 生成八个智能体
        if not self.generate_eight_agents():
            return

        # 规划路径
        print("\nPlanning paths...")
        if not self.plan_paths():
            return

        # 显示性能指标
        self.show_metrics()

        # 显示动画
        print("\nLaunching animation in 3 seconds...")
        time.sleep(3)

        self.show_animation(speed=1.0)

        print("\nDemo completed!")


def main():
    """主函数"""
    demo = EightAgentDemo()

    print("Select demo mode:")
    print("1. Interactive Demo (with menu)")
    print("2. Automatic Demo (straight to animation)")

    mode = input("Select mode (1 or 2): ").strip()

    if mode == "1":
        demo.run_interactive_demo()
    elif mode == "2":
        demo.run_automatic_demo()
    else:
        print("Invalid selection. Running interactive demo...")
        demo.run_interactive_demo()


if __name__ == "__main__":
    main()
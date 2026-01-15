"""
多智能体寻路系统主程序
"""

import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from environment.map_loader import MapLoader
from environment.grid import GridEnvironment
from environment.agent_manager import AgentManager
from algorithms.cbs import CBS
from utils.visualization import Visualizer
from utils.metrics import Metrics
from utils.logger import setup_logger


def main():
    """主函数"""

    # 设置日志
    logger = setup_logger("MAPF")
    logger.info("Starting Multi-Agent Path Finding System")

    # 加载配置
    config = Config()
    logger.info(f"Configuration loaded: {config.NUM_AGENTS} agents")

    # 加载地图
    logger.info(f"Loading map from {config.MAP_FILE}")
    map_loader = MapLoader(config.MAP_FILE)
    grid = map_loader.load_map()

    if grid is None:
        logger.error("Failed to load map!")
        return

    logger.info(f"Map loaded: {grid.shape[0]} x {grid.shape[1]}")

    # 创建环境
    env = GridEnvironment(grid)

    # 创建智能体管理器并生成智能体
    logger.info(f"Generating {config.NUM_AGENTS} random agents...")
    agent_manager = AgentManager(grid)
    agents = agent_manager.generate_random_agents(config.NUM_AGENTS, min_distance=20)

    # 显示智能体信息
    for agent in agents:
        logger.info(f"  {agent}")

    # 执行CBS算法
    logger.info("Starting CBS algorithm...")
    start_time = time.time()

    cbs = CBS(env, agents, config)
    solutions = cbs.search()

    end_time = time.time()
    computation_time = end_time - start_time

    logger.info(f"CBS completed in {computation_time:.2f} seconds")

    # 更新智能体路径
    for agent in agents:
        if agent.id in solutions:
            agent.path = solutions[agent.id]
            agent.cost = len(solutions[agent.id]) - 1

    # 计算性能指标
    logger.info("\n=== Performance Metrics ===")

    makespan = Metrics.calculate_makespan(solutions)
    sum_of_costs = Metrics.calculate_sum_of_costs(solutions)
    average_cost = Metrics.calculate_average_cost(solutions)
    success_rate = Metrics.calculate_success_rate(solutions, agents)

    logger.info(f"Makespan: {makespan}")
    logger.info(f"Sum of Costs: {sum_of_costs}")
    logger.info(f"Average Cost: {average_cost:.2f}")
    logger.info(f"Success Rate: {success_rate:.2%}")

    # 检查冲突
    collisions = Metrics.check_collisions(solutions)
    if collisions:
        logger.warning(f"Found {len(collisions)} collisions!")
        for i, collision in enumerate(collisions[:5]):  # 只显示前5个冲突
            logger.warning(f"  Collision {i + 1}: {collision}")
    else:
        logger.info("No collisions found!")

    # 可视化结果
    if config.VISUALIZE:
        logger.info("Visualizing results...")

        # 创建可视化器
        visualizer = Visualizer(grid)

        # 绘制路径
        visualizer.plot_paths(agents, solutions, show_start_goal=True)

        # 显示图形
        visualizer.show()

        # 创建动画（可选）
        # ani = visualizer.animate_paths(agents, solutions, interval=config.VISUALIZE_INTERVAL)
        # visualizer.show()

        # 保存动画（可选）
        # visualizer.save_animation(ani, "mapf_animation.mp4", fps=2)

    # 保存结果
    if config.SAVE_RESULTS:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        result_file = f"results_{timestamp}.txt"

        with open(result_file, 'w') as f:
            f.write("=== MAPF Results ===\n")
            f.write(f"Map: {config.MAP_FILE}\n")
            f.write(f"Number of Agents: {config.NUM_AGENTS}\n")
            f.write(f"Computation Time: {computation_time:.2f}s\n")
            f.write(f"Makespan: {makespan}\n")
            f.write(f"Sum of Costs: {sum_of_costs}\n")
            f.write(f"Average Cost: {average_cost:.2f}\n")
            f.write(f"Success Rate: {success_rate:.2%}\n")
            f.write(f"Collisions: {len(collisions)}\n\n")

            f.write("=== Agent Details ===\n")
            for agent in agents:
                f.write(f"Agent {agent.id}:\n")
                f.write(f"  Start: {agent.start}\n")
                f.write(f"  Goal: {agent.goal}\n")
                f.write(f"  Path Length: {len(agent.path) if agent.path else 0}\n")
                f.write(f"  Cost: {agent.cost}\n")
                if agent.path:
                    f.write(f"  Path: {' -> '.join(str(pos) for pos in agent.path)}\n")
                f.write("\n")

        logger.info(f"Results saved to {result_file}")

    logger.info("Program completed successfully!")


if __name__ == "__main__":
    main()
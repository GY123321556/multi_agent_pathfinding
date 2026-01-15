"""
配置参数文件
"""


class Config:
    # 地图参数
    MAP_FILE = "Berlin_1_256.map"
    MAP_WIDTH = 256
    MAP_HEIGHT = 256

    # 智能体参数
    NUM_AGENTS = 8
    AGENT_RADIUS = 0.5  # 智能体半径（用于碰撞检测）

    # 算法参数
    MAX_TIME_STEPS = 300  # 最大时间步数
    MAX_NODES = 10000  # 最大搜索节点数

    # A*算法参数
    ASTAR_WEIGHT = 1.0  # 启发式权重
    ALLOW_DIAGONAL = False  # 是否允许对角线移动

    # CBS算法参数
    CBS_MAX_ITERATIONS = 1000  # CBS最大迭代次数
    HIGH_LEVEL_MAX_NODES = 10000  # 高层搜索最大节点数

    # 可视化参数
    VISUALIZE = True
    VISUALIZE_INTERVAL = 100  # 可视化间隔(ms)

    # 输出参数
    PRINT_PROGRESS = True
    SAVE_RESULTS = True
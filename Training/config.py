# file name : config.py
# content : Configuration for Gomoku game, including board size, winning condition, and AI parameters

# Board configuration
GENE_BOUNDS = [
    (1, 50), # 活二
    (1, 30), # 跳二
    (100, 2000), # 活三
    (50, 1000), # 跳三
    (5000, 50000), # 活四
    (10000, 1000000), # 五  
    (1, 30), # 眠二
    (10, 200), # 眠三
    (500, 10000), # 眠四
    (0.1, 1.5) # defense weight
]

CHROM_LENGTH = len(GENE_BOUNDS)

DEFAULT_CHROM = [10, 5, 1000, 500, 10000, 10000, 5, 50, 2000, 0.5]

# 默认情况下，两者存在差异
round(0.5) # Julia返回0，Matlab返回1
round(1.5) # Julia返回2, Matlab返回2
# 以下用法与Matlab的`round(X)`等价
round(-1.5, RoundNearestTiesAway) # -2.0
round(-0.5, RoundNearestTiesAway) # -1.0
round(-0, RoundNearestTiesAway)  # 0
round(0, RoundNearestTiesAway)  # 0
round(0.5, RoundNearestTiesAway) # 1
round(1.5, RoundNearestTiesAway) # 2






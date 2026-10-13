def _position_label(percentile: float) -> str:
    # 用当前净值在近期历史中的位置，粗略判断高位、低位还是中间位置。
    if percentile >= 70:
        return "偏高位"
    if percentile <= 30:
        return "偏低位"
    return "中部位置"


def summarize_trend(history: list[float]) -> str:
    # 走势判断只需要近期净值。少于两条数据时无法计算变化，直接返回提示。
    if len(history) < 2:
        return "历史净值不足，暂时无法判断走势"

    recent_window = history[-60:] if len(history) >= 60 else history
    recent_20 = history[-20:] if len(history) >= 20 else history
    latest_nav = history[-1]

    # 近 20 个净值点的涨跌幅，用来描述最近是在涨还是在跌。
    recent_change = (latest_nav / recent_20[0] - 1) * 100

    # 分位数可以理解成：近期净值里有多少比例比当前值低。
    lower_count = sum(1 for nav in recent_window if nav < latest_nav)
    percentile = lower_count / len(recent_window) * 100

    # 从最后一天往前数，统计连续上涨或连续下跌的点数。
    daily_changes = [history[index] - history[index - 1] for index in range(1, len(history))]
    streak = 0
    last_change = daily_changes[-1]
    direction = "上涨" if last_change > 0 else "下跌"

    for change in reversed(daily_changes):
        if direction == "上涨" and change > 0:
            streak += 1
        elif direction == "下跌" and change < 0:
            streak += 1
        else:
            break

    if recent_change > 0.5:
        recent_label = f"近20个净值点上涨{recent_change:.1f}%"
    elif recent_change < -0.5:
        recent_label = f"近20个净值点下跌{abs(recent_change):.1f}%"
    else:
        recent_label = f"近20个净值点震荡{recent_change:+.1f}%"

    return f"{recent_label}，当前处于近60个净值点{_position_label(percentile)}，近期{direction}{streak}个点"

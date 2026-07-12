"""
转会简报格式化器
生成漂亮的 Markdown 表格简报，适合钉钉机器人推送
"""
from datetime import datetime, timezone, timedelta
from src.scraper import lookup_chinese_player, cn as club_to_cn

LEAGUE_ORDER = ["英超", "西甲", "德甲", "意甲", "法甲"]
LEAGUE_EMOJI = {
    "英超": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "西甲": "🇪🇸",
    "德甲": "🇩🇪",
    "意甲": "🇮🇹",
    "法甲": "🇫🇷",
}

STATUS_MAP = {
    "completed":   "✅ 已完成",
    "negotiating": "🟡 谈判中",
    "rumor":       "🔶 传闻中",
}


def fmt_player(t: dict) -> str:
    """球员名显示：英文名（中文名）"""
    en = t.get("player", "")
    cn_name = lookup_chinese_player(en)
    if cn_name:
        return f"{en}（{cn_name}）"
    return en


def fmt_fee(fee: str) -> str:
    """格式化转会费"""
    if not fee or fee in ("—", "-", "", "?", "--"):
        return "—"
    return fee


def fmt_direction(t: dict) -> str:
    """转会方向：原俱乐部 → 新俱乐部"""
    from_c = club_to_cn(t.get("from_club", ""))
    to_c = club_to_cn(t.get("to_club", ""))
    if from_c and to_c:
        return f"{from_c} → {to_c}"
    if to_c:
        return f"→ {to_c}"
    if from_c:
        return f"{from_c} →"
    return "—"


def fmt_status(status: str) -> str:
    """状态文本"""
    return STATUS_MAP.get(status, f"❓ {status}")


def format_briefing(data: dict) -> str:
    """生成完整的 Markdown 简报"""
    now = datetime.now(timezone(timedelta(hours=8)))
    date_str = now.strftime("%Y年%m月%d日")

    lines = [
        f"# 📰 五大联赛转会日报",
        f"*{date_str}  ·  数据来源：Transfermarkt*",
        "",
    ]

    total = 0
    for league in LEAGUE_ORDER:
        items = data.get(league, [])
        if not items:
            continue
        total += len(items)
        emoji = LEAGUE_EMOJI.get(league, "⚽")

        lines.append(f"## {emoji} {league}（{len(items)} 条）")
        lines.append("")
        lines.append("| 球员 | 方向 | 转会费 | 状态 |")
        lines.append("|:----:|:----:|:-----:|:----:|")

        for t in items:
            player = fmt_player(t)
            direction = fmt_direction(t)
            fee = fmt_fee(t.get("fee", ""))
            status = fmt_status(t.get("status", "completed"))

            # 限制方向列长度（钉钉表格宽度有限）
            if len(direction) > 22:
                direction = direction[:20] + ".."

            lines.append(f"| {player} | {direction} | {fee} | {status} |")

        lines.append("")

    # 其他联赛
    other = data.get("其他", [])
    if other:
        lines.append(f"## ⚽ 其他联赛（{len(other)} 条）")
        lines.append("")
        lines.append("| 球员 | 方向 | 转会费 | 状态 |")
        lines.append("|:----:|:----:|:-----:|:----:|")
        for t in other[:8]:  # 只显示前8条
            player = fmt_player(t)
            direction = fmt_direction(t)
            fee = fmt_fee(t.get("fee", ""))
            status = fmt_status(t.get("status", "completed"))
            if len(direction) > 22:
                direction = direction[:20] + ".."
            lines.append(f"| {player} | {direction} | {fee} | {status} |")
        if len(other) > 8:
            lines.append(f"| … | 还有 {len(other)-8} 条 | … | … |")
        lines.append("")

    # 页脚
    lines.append("---")
    lines.append(f"> 📊 五大联赛共 **{total}** 条转会动态")
    lines.append("")
    lines.append("> ⏰ *每日 09:00 自动推送 · 小虾米简报* 🦐")

    return "\n".join(lines)

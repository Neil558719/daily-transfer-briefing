"""
五大联赛转会爬虫 - Transfermarkt
使用 BeautifulSoup 解析结构化数据，只取五大联赛相关转会
"""
import requests
from bs4 import BeautifulSoup
from src.players import PLAYERS_CN

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
}

# 五大联赛俱乐部判定（含常见变体）
LEAGUE_CLUBS = {
    "英超": [
        "Arsenal", "Arsenal FC",
        "Aston Villa",
        "AFC Bournemouth", "Bournemouth",
        "Brentford FC", "Brentford",
        "Brighton & Hove Albion", "Brighton",
        "Chelsea", "Chelsea FC",
        "Crystal Palace",
        "Everton", "Everton FC",
        "Fulham", "Fulham FC",
        "Ipswich Town",
        "Leicester City",
        "Liverpool", "Liverpool FC",
        "Manchester City", "Man City",
        "Manchester United", "Man Utd", "Manchester Utd",
        "Newcastle United", "Newcastle",
        "Nottingham Forest",
        "Southampton", "Southampton FC",
        "Tottenham Hotspur", "Tottenham",
        "West Ham United", "West Ham",
        "Wolverhampton Wanderers", "Wolves",
    ],
    "西甲": [
        "FC Barcelona", "Barcelona",
        "Real Madrid",
        "Atletico Madrid", "Atlético Madrid",
        "Sevilla", "Sevilla FC",
        "Villarreal", "Villarreal CF",
        "Real Sociedad",
        "Real Betis Balompie", "Real Betis",
        "Athletic Bilbao", "Athletic Club",
        "Valencia", "Valencia CF",
        "Girona FC", "Girona",
        "CA Osasuna", "Osasuna",
        "Getafe CF", "Getafe",
        "RC Celta de Vigo", "Celta Vigo",
        "RCD Mallorca", "Mallorca",
        "Rayo Vallecano",
        "Deportivo Alaves", "Alaves",
        "RCD Espanyol", "Espanyol",
        "Real Valladolid",
        "CD Leganes", "Leganes",
    ],
    "德甲": [
        "FC Bayern Munchen", "FC Bayern München", "Bayern Munich", "Bayern Munchen",
        "Borussia Dortmund", "Dortmund",
        "Bayer 04 Leverkusen", "Bayer Leverkusen",
        "RB Leipzig", "Leipzig",
        "Eintracht Frankfurt",
        "VfB Stuttgart", "Stuttgart",
        "Borussia Mönchengladbach", "Borussia Mönchengladbach", "Gladbach",
        "VfL Wolfsburg", "Wolfsburg",
        "1. FSV Mainz 05", "Mainz",
        "SV Werder Bremen", "Werder Bremen",
        "SC Freiburg", "Freiburg",
        "FC Augsburg", "Augsburg",
        "TSG 1899 Hoffenheim", "Hoffenheim",
        "1. FC Union Berlin", "Union Berlin",
        "VfL Bochum", "Bochum",
        "FC St. Pauli", "St. Pauli",
        "1. FC Heidenheim 1846", "Heidenheim",
        "Holstein Kiel",
    ],
    "意甲": [
        "Juventus", "Juventus FC",
        "AC Milan", "Milan",
        "Inter Milan", "Inter",
        "SSC Napoli", "Napoli",
        "AS Roma", "Roma",
        "SS Lazio", "Lazio",
        "Atalanta BC", "Atalanta",
        "ACF Fiorentina", "Fiorentina",
        "Bologna FC", "Bologna",
        "Torino FC", "Torino",
        "Udinese Calcio", "Udinese",
        "Genoa CFC", "Genoa",
        "Cagliari Calcio", "Cagliari",
        "US Lecce", "Lecce",
        "Como 1907", "Como",
        "Empoli FC", "Empoli",
        "Parma Calcio 1913", "Parma",
        "Venezia FC", "Venezia",
        "AC Monza", "Monza",
        "Hellas Verona", "Verona",
    ],
    "法甲": [
        "Paris Saint-Germain", "PSG",
        "Olympique Marseille", "Marseille",
        "Olympique Lyonnais", "Lyon",
        "AS Monaco", "Monaco",
        "LOSC Lille", "Lille",
        "OGC Nice", "Nice",
        "Stade Rennais FC", "Rennes",
        "RC Lens", "Lens",
        "RC Strasbourg Alsace", "Strasbourg",
        "Stade Brestois 29", "Brest",
        "Toulouse FC", "Toulouse",
        "Montpellier HSC", "Montpellier",
        "FC Nantes", "Nantes",
        "Le Havre AC", "Le Havre",
        "Stade de Reims", "Reims",
        "AJ Auxerre", "Auxerre",
        "Angers SCO", "Angers",
        "AS Saint-Etienne", "Saint-Etienne",
    ],
}

CLUB_CN = {
    # 英超
    "Arsenal": "阿森纳", "Arsenal FC": "阿森纳",
    "Aston Villa": "阿斯顿维拉",
    "Bournemouth": "伯恩茅斯", "AFC Bournemouth": "伯恩茅斯",
    "Brentford": "布伦特福德", "Brentford FC": "布伦特福德",
    "Brighton": "布莱顿", "Brighton & Hove Albion": "布莱顿",
    "Chelsea": "切尔西", "Chelsea FC": "切尔西",
    "Crystal Palace": "水晶宫",
    "Everton": "埃弗顿", "Everton FC": "埃弗顿",
    "Fulham": "富勒姆", "Fulham FC": "富勒姆",
    "Ipswich Town": "伊普斯维奇",
    "Leicester City": "莱斯特城",
    "Liverpool": "利物浦", "Liverpool FC": "利物浦",
    "Man City": "曼城", "Manchester City": "曼城",
    "Man Utd": "曼联", "Manchester United": "曼联", "Manchester Utd": "曼联",
    "Newcastle": "纽卡", "Newcastle United": "纽卡",
    "Nottingham Forest": "诺丁汉森林",
    "Southampton": "南安普顿", "Southampton FC": "南安普顿",
    "Tottenham": "热刺", "Tottenham Hotspur": "热刺",
    "West Ham": "西汉姆", "West Ham United": "西汉姆",
    "Wolves": "狼队", "Wolverhampton Wanderers": "狼队",
    # 西甲
    "Barcelona": "巴萨", "FC Barcelona": "巴萨",
    "Real Madrid": "皇马",
    "Atletico Madrid": "马竞", "Atlético Madrid": "马竞",
    "Sevilla": "塞维利亚", "Sevilla FC": "塞维利亚",
    "Villarreal": "比利亚雷亚尔", "Villarreal CF": "比利亚雷亚尔",
    "Real Sociedad": "皇家社会",
    "Real Betis": "贝蒂斯", "Real Betis Balompie": "贝蒂斯",
    "Athletic Bilbao": "毕尔巴鄂", "Athletic Club": "毕尔巴鄂",
    "Valencia": "瓦伦西亚", "Valencia CF": "瓦伦西亚",
    "Girona": "赫罗纳", "Girona FC": "赫罗纳",
    "Osasuna": "奥萨苏纳", "CA Osasuna": "奥萨苏纳",
    "Getafe": "赫塔费", "Getafe CF": "赫塔费",
    "Celta Vigo": "塞尔塔", "RC Celta de Vigo": "塞尔塔",
    "Mallorca": "马洛卡", "RCD Mallorca": "马洛卡",
    "Rayo Vallecano": "巴列卡诺",
    "Alaves": "阿拉维斯", "Deportivo Alaves": "阿拉维斯",
    "Espanyol": "西班牙人", "RCD Espanyol": "西班牙人",
    "Real Valladolid": "巴拉多利德",
    "Leganes": "莱加内斯", "CD Leganes": "莱加内斯",
    # 德甲
    "Bayern Munich": "拜仁", "Bayern Munchen": "拜仁",
    "FC Bayern Munchen": "拜仁", "FC Bayern München": "拜仁",
    "Dortmund": "多特", "Borussia Dortmund": "多特",
    "Bayer Leverkusen": "勒沃库森", "Bayer 04 Leverkusen": "勒沃库森",
    "Leipzig": "莱比锡", "RB Leipzig": "莱比锡",
    "Eintracht Frankfurt": "法兰克福",
    "Stuttgart": "斯图加特", "VfB Stuttgart": "斯图加特",
    "Gladbach": "门兴", "Borussia Mönchengladbach": "门兴",
    "Wolfsburg": "狼堡", "VfL Wolfsburg": "狼堡",
    "Mainz": "美因茨", "1. FSV Mainz 05": "美因茨",
    "Werder Bremen": "不莱梅", "SV Werder Bremen": "不莱梅",
    "Freiburg": "弗赖堡", "SC Freiburg": "弗赖堡",
    "Augsburg": "奥格斯堡", "FC Augsburg": "奥格斯堡",
    "Hoffenheim": "霍芬海姆", "TSG 1899 Hoffenheim": "霍芬海姆",
    "Union Berlin": "柏林联合", "1. FC Union Berlin": "柏林联合",
    "Bochum": "波鸿", "VfL Bochum": "波鸿",
    "St. Pauli": "圣保利", "FC St. Pauli": "圣保利",
    "Heidenheim": "海登海姆", "1. FC Heidenheim 1846": "海登海姆",
    "Holstein Kiel": "荷尔斯泰因基尔",
    # 意甲
    "Juventus": "尤文", "Juventus FC": "尤文",
    "AC Milan": "AC米兰", "Milan": "AC米兰",
    "Inter": "国米", "Inter Milan": "国米",
    "Napoli": "那不勒斯", "SSC Napoli": "那不勒斯",
    "Roma": "罗马", "AS Roma": "罗马",
    "Lazio": "拉齐奥", "SS Lazio": "拉齐奥",
    "Atalanta": "亚特兰大", "Atalanta BC": "亚特兰大",
    "Fiorentina": "佛罗伦萨", "ACF Fiorentina": "佛罗伦萨",
    "Bologna": "博洛尼亚", "Bologna FC": "博洛尼亚",
    "Torino": "都灵", "Torino FC": "都灵",
    "Udinese": "乌迪内斯", "Udinese Calcio": "乌迪内斯",
    "Genoa": "热那亚", "Genoa CFC": "热那亚",
    "Cagliari": "卡利亚里", "Cagliari Calcio": "卡利亚里",
    "Lecce": "莱切", "US Lecce": "莱切",
    "Como": "科莫", "Como 1907": "科莫",
    "Empoli": "恩波利", "Empoli FC": "恩波利",
    "Parma": "帕尔马", "Parma Calcio 1913": "帕尔马",
    "Venezia": "威尼斯", "Venezia FC": "威尼斯",
    "Monza": "蒙扎", "AC Monza": "蒙扎",
    "Verona": "维罗纳", "Hellas Verona": "维罗纳",
    # 法甲
    "PSG": "巴黎", "Paris Saint-Germain": "巴黎",
    "Marseille": "马赛", "Olympique Marseille": "马赛",
    "Lyon": "里昂", "Olympique Lyonnais": "里昂",
    "Monaco": "摩纳哥", "AS Monaco": "摩纳哥",
    "Lille": "里尔", "LOSC Lille": "里尔",
    "Nice": "尼斯", "OGC Nice": "尼斯",
    "Rennes": "雷恩", "Stade Rennais FC": "雷恩",
    "Lens": "朗斯", "RC Lens": "朗斯",
    "Strasbourg": "斯特拉斯堡", "RC Strasbourg Alsace": "斯特拉斯堡",
    "Brest": "布雷斯特", "Stade Brestois 29": "布雷斯特",
    "Toulouse": "图卢兹", "Toulouse FC": "图卢兹",
    "Montpellier": "蒙彼利埃", "Montpellier HSC": "蒙彼利埃",
    "Nantes": "南特", "FC Nantes": "南特",
    "Le Havre": "勒阿弗尔", "Le Havre AC": "勒阿弗尔",
    "Reims": "兰斯", "Stade de Reims": "兰斯",
    "Auxerre": "欧塞尔", "AJ Auxerre": "欧塞尔",
    "Angers": "昂热", "Angers SCO": "昂热",
    "Saint-Etienne": "圣埃蒂安", "AS Saint-Etienne": "圣埃蒂安",
}


def get_league(club: str) -> str:
    """通过俱乐部名判断联赛，支持模糊匹配"""
    if not club:
        return None
    c = club.lower().strip()
    for league, clubs in LEAGUE_CLUBS.items():
        for cl in clubs:
            cl_lower = cl.lower().strip()
            # 精确匹配 或 包含匹配
            if c == cl_lower or cl_lower in c or c in cl_lower:
                return league
    return None


def cn(club: str) -> str:
    """英文俱乐部名 -> 中文"""
    if not club:
        return ""
    # 尝试精确匹配
    if club in CLUB_CN:
        return CLUB_CN[club]
    # 尝试去掉后缀匹配
    simplified = club.replace(" FC", "").replace(" CF", "").strip()
    if simplified in CLUB_CN:
        return CLUB_CN[simplified]
    # 尝试从 CLUB_CN 的 key 中匹配
    for key, val in CLUB_CN.items():
        if key.lower() in club.lower() or club.lower() in key.lower():
            return val
    return club


def fetch_tm_transfers() -> list[dict]:
    """获取 Transfermarkt 最新已完成转会"""
    url = "https://www.transfermarkt.com/statistik/neuestetransfers"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"  ⚠ Transfermarkt 抓取失败: {e}")
        return []

    soup = BeautifulSoup(resp.text, 'lxml')

    table = soup.find('table', class_='items')
    if not table:
        print("  ⚠ 未找到转会数据表格")
        return []

    tbody = table.find('tbody')
    if not tbody:
        return []

    transfers = []
    rows = tbody.find_all('tr', recursive=False)
    for tr in rows:
        t = _parse_row(tr)
        if t:
            transfers.append(t)

    return transfers


def _parse_row(tr) -> dict | None:
    """用 BeautifulSoup 解析一行转会数据"""
    try:
        tds = tr.find_all('td', recursive=False)
        if len(tds) < 6:
            return None

        # 球员名（第1列）
        player_a = tds[0].find('a', title=True)
        if not player_a:
            return None
        player = player_a.get('title', '').strip()
        if not player:
            return None

        # 离开的俱乐部（第4列, index 3）
        left_club = _extract_club(tds[3])

        # 加入的俱乐部（第5列, index 4）
        joined_club = _extract_club(tds[4])

        # 转会费（第6列, index 5）
        fee = tds[5].get_text(strip=True)

        # 联赛判定
        league = get_league(left_club) or get_league(joined_club) or "其他"

        return {
            "player": player,
            "from_club": left_club,
            "to_club": joined_club,
            "fee": _normalize_fee(fee),
            "status": "completed",   # completed | negotiating | rumor
            "league": league,
        }
    except Exception:
        return None


def _extract_club(td) -> str:
    """从 td 中提取俱乐部名"""
    a = td.find('a', title=True)
    if a:
        return a.get('title', '').strip()
    return ""


def _normalize_fee(fee: str) -> str:
    """归一化转会费显示"""
    if not fee:
        return "—"
    fee = fee.strip()
    if fee in ("-", "?", "--"):
        return "—"
    fl = fee.lower()
    if "loan" in fl:
        return "租借"
    if "free" in fl:
        return "免签"
    return fee


def lookup_chinese_player(en_name: str) -> str:
    """英 -> 中文球员名"""
    if en_name in PLAYERS_CN:
        return PLAYERS_CN[en_name]
    en_lower = en_name.lower()
    for key, cn_name in PLAYERS_CN.items():
        if key.lower() == en_lower:
            return cn_name
    return ""


def collect_transfer_news() -> dict:
    """入口：获取转会数据并按联赛分类"""
    print("🔍 从 Transfermarkt 获取最新转会记录...")
    all_t = fetch_tm_transfers()
    print(f"  ✅ 共获取 {len(all_t)} 条转会记录")

    leagues = ["英超", "西甲", "德甲", "意甲", "法甲"]
    result = {l: [] for l in leagues}
    result["其他"] = []

    for t in all_t:
        league = t["league"]
        if league in result:
            result[league].append(t)
        else:
            result["其他"].append(t)

    print()
    for l in leagues:
        if result[l]:
            print(f"   {l}: {len(result[l])} 条")

    return result

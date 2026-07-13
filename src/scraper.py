"""
五大联赛转会爬虫 - Transfermarkt（带多重防屏蔽 & 自动重试）
"""
import time
import cloudscraper
import requests
from bs4 import BeautifulSoup
from src.players import PLAYERS_CN

# ============================================================
# 不同浏览器特征配置，轮换使用绕过 Cloudflare
# ============================================================
_SCRAPER_CONFIGS = [
    {"browser": "chrome", "platform": "windows", "mobile": False},
    {"browser": "chrome", "platform": "linux",   "mobile": False},
    {"browser": "firefox", "platform": "windows","mobile": False},
    {"browser": "safari",  "platform": "ios",    "mobile": True},
]

_HEADERS_TEMPLATES = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/125.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,de;q=0.8",
        "Referer": "https://www.transfermarkt.com/",
    },
    {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/131.0.0.0 Safari/537.36",
        "Accept-Language": "en-GB,en;q=0.9",
        "Referer": "https://www.google.com/",
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) "
                      "Gecko/20100101 Firefox/130.0",
        "Accept-Language": "en-US,en;q=0.8",
        "Referer": "https://duckduckgo.com/",
    },
]

# 五大联赛俱乐部判定（含常见变体）
LEAGUE_CLUBS = {
    "英超": [
        "Arsenal", "Arsenal FC", "Aston Villa",
        "Bournemouth", "AFC Bournemouth",
        "Brentford FC", "Brentford",
        "Brighton & Hove Albion", "Brighton",
        "Chelsea", "Chelsea FC", "Crystal Palace",
        "Everton", "Everton FC",
        "Fulham", "Fulham FC",
        "Ipswich Town", "Leicester City",
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
        "Atletico Madrid", "Atletico Madrid",
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
        "Borussia Mönchengladbach", "Gladbach",
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
    "Arsenal": "阿森纳", "Arsenal FC": "阿森纳",
    "Aston Villa": "阿斯顿维拉",
    "Bournemouth": "伯恩茅斯", "AFC Bournemouth": "伯恩茅斯",
    "Brentford": "布伦特福德", "Brentford FC": "布伦特福德",
    "Brighton": "布莱顿", "Brighton & Hove Albion": "布莱顿",
    "Chelsea": "切尔西", "Chelsea FC": "切尔西",
    "Crystal Palace": "水晶宫",
    "Everton": "埃弗顿", "Everton FC": "埃弗顿",
    "Fulham": "富勒姆", "Fulham FC": "富勒姆",
    "Ipswich Town": "伊普斯维奇", "Leicester City": "莱斯特城",
    "Liverpool": "利物浦", "Liverpool FC": "利物浦",
    "Man City": "曼城", "Manchester City": "曼城",
    "Man Utd": "曼联", "Manchester United": "曼联",
    "Newcastle": "纽卡", "Newcastle United": "纽卡",
    "Nottingham Forest": "诺丁汉森林",
    "Southampton": "南安普顿", "Southampton FC": "南安普顿",
    "Tottenham": "热刺", "Tottenham Hotspur": "热刺",
    "West Ham": "西汉姆", "West Ham United": "西汉姆",
    "Wolves": "狼队", "Wolverhampton Wanderers": "狼队",
    "Barcelona": "巴萨", "FC Barcelona": "巴萨",
    "Real Madrid": "皇马",
    "Atletico Madrid": "马竞", "Atletico Madrid": "马竞",
    "Sevilla": "塞维利亚", "Sevilla FC": "塞维利亚",
    "Villarreal": "比利亚雷亚尔", "Villarreal CF": "比利亚雷亚尔",
    "Real Sociedad": "皇家社会", "Real Betis": "贝蒂斯",
    "Athletic Bilbao": "毕尔巴鄂", "Athletic Club": "毕尔巴鄂",
    "Valencia": "瓦伦西亚", "Valencia CF": "瓦伦西亚",
    "Girona": "赫罗纳", "Girona FC": "赫罗纳",
    "Osasuna": "奥萨苏纳", "Getafe": "赫塔费", "Getafe CF": "赫塔费",
    "Celta Vigo": "塞尔塔", "RCD Mallorca": "马洛卡",
    "Rayo Vallecano": "巴列卡诺", "Alaves": "阿拉维斯",
    "Espanyol": "西班牙人", "Real Valladolid": "巴拉多利德",
    "Leganes": "莱加内斯", "CD Leganes": "莱加内斯",
    "Bayern Munich": "拜仁", "FC Bayern München": "拜仁",
    "Dortmund": "多特", "Borussia Dortmund": "多特",
    "Bayer Leverkusen": "勒沃库森",
    "Leipzig": "莱比锡", "RB Leipzig": "莱比锡",
    "Eintracht Frankfurt": "法兰克福",
    "Stuttgart": "斯图加特", "VfB Stuttgart": "斯图加特",
    "Gladbach": "门兴", "Borussia Mönchengladbach": "门兴",
    "Wolfsburg": "狼堡", "VfL Wolfsburg": "狼堡",
    "Mainz": "美因茨", "Werder Bremen": "不莱梅",
    "Freiburg": "弗赖堡", "FC Augsburg": "奥格斯堡",
    "Hoffenheim": "霍芬海姆", "Union Berlin": "柏林联合",
    "Bochum": "波鸿", "VfL Bochum": "波鸿",
    "St. Pauli": "圣保利", "Heidenheim": "海登海姆",
    "Holstein Kiel": "荷尔斯泰因基尔",
    "Juventus": "尤文", "Juventus FC": "尤文",
    "AC Milan": "AC米兰", "Milan": "AC米兰",
    "Inter": "国米", "Inter Milan": "国米",
    "Napoli": "那不勒斯", "SSC Napoli": "那不勒斯",
    "Roma": "罗马", "AS Roma": "罗马",
    "Lazio": "拉齐奥", "SS Lazio": "拉齐奥",
    "Atalanta": "亚特兰大", "Fiorentina": "佛罗伦萨",
    "Bologna": "博洛尼亚", "Torino": "都灵",
    "Udinese": "乌迪内斯", "Genoa": "热那亚",
    "Cagliari": "卡利亚里", "Lecce": "莱切",
    "Como": "科莫", "Como 1907": "科莫",
    "Empoli": "恩波利", "Parma": "帕尔马",
    "Venezia": "威尼斯", "Monza": "蒙扎", "AC Monza": "蒙扎",
    "Verona": "维罗纳", "Hellas Verona": "维罗纳",
    "PSG": "巴黎", "Paris Saint-Germain": "巴黎",
    "Marseille": "马赛", "Olympique Marseille": "马赛",
    "Lyon": "里昂", "Monaco": "摩纳哥",
    "Lille": "里尔", "LOSC Lille": "里尔",
    "Nice": "尼斯", "OGC Nice": "尼斯",
    "Rennes": "雷恩", "Stade Rennais FC": "雷恩",
    "Lens": "朗斯", "RC Lens": "朗斯",
    "Strasbourg": "斯特拉斯堡", "Brest": "布雷斯特",
    "Toulouse": "图卢兹", "Montpellier": "蒙彼利埃",
    "Nantes": "南特", "Le Havre": "勒阿弗尔",
    "Reims": "兰斯", "Auxerre": "欧塞尔",
    "Angers": "昂热", "Saint-Etienne": "圣埃蒂安",
}


def get_league(club):
    if not club:
        return None
    c = club.lower().strip()
    for league, clubs in LEAGUE_CLUBS.items():
        for cl in clubs:
            cl_lower = cl.lower().strip()
            if c == cl_lower or cl_lower in c or c in cl_lower:
                return league
    return None


def cn(club):
    if not club:
        return ""
    if club in CLUB_CN:
        return CLUB_CN[club]
    for key, val in CLUB_CN.items():
        if key.lower() in club.lower() or club.lower() in key.lower():
            return val
    return club


# ====================================================================
# 核心：解析 Transfermarkt 页面（被多个入口共用）
# ====================================================================
def _parse_transfermarkt_page(html: str, source_label: str) -> list:
    """解析 Transfermarkt HTML 中的转会表格"""
    soup = BeautifulSoup(html, "lxml")
    title_tag = soup.find("title")
    print(f"  📄 [{source_label}] 页面标题: {title_tag.get_text(strip=True) if title_tag else 'N/A'}")

    table = soup.find("table", class_="items")
    if not table:
        print(f"  ⚠ [{source_label}] 未找到 table.items")
        return []

    tbody = table.find("tbody")
    if not tbody:
        print(f"  ⚠ [{source_label}] 表格内无 tbody")
        return []

    rows = tbody.find_all("tr", recursive=False)
    transfers = []
    for tr in rows:
        t = _parse_row(tr)
        if t:
            transfers.append(t)
    print(f"  ✅ [{source_label}] 解析到 {len(transfers)} 条转会")
    return transfers


# ====================================================================
# 方案 A：cloudscraper（多配置轮换 + 自动重试）
# ====================================================================
def _fetch_tm_cloudscraper(url: str, headers: dict, config: dict,
                           timeout: int = 30) -> tuple:
    """
    使用指定配置的 cloudscraper 发起请求
    返回 (status_ok, html_content_or_error_msg)
    """
    scraper = cloudscraper.create_scraper(browser=config)
    try:
        resp = scraper.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return True, resp.text
    except Exception as e:
        return False, str(e)


def _strategy_cloudscraper() -> list:
    """
    主方案：轮流使用 4 种浏览器特征 + 3 种 Header
    组合最多 12 次尝试，每次遇到 Cloudflare 就换一种特征
    """
    url = "https://www.transfermarkt.com/statistik/neuestetransfers"
    combined_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                  "image/avif,image/webp,image/apng,*/*;q=0.8",
    }

    for attempt, config in enumerate(_SCRAPER_CONFIGS, 1):
        for h_idx, h_template in enumerate(_HEADERS_TEMPLATES, 1):
            headers = {**combined_headers, **h_template}
            browser_label = f"{config['browser']}/{config['platform']}"
            print(f"  🔄 尝试 cloudscraper [{browser_label}] (第{attempt}组, 第{h_idx}个头)...")

            ok, result = _fetch_tm_cloudscraper(url, headers, config)
            if not ok:
                print(f"  ⚠ 请求失败: {result}")
                time.sleep(1)
                continue

            transfers = _parse_transfermarkt_page(result, "cloudscraper")
            if transfers:
                print(f"  ✅ cloudscraper [{browser_label}] 成功抓到 {len(transfers)} 条")
                return transfers

            # 页面拿到了但没解析出数据 → 检查是否被 Cloudflare 拦截
            if "Checking your browser" in result[:500]:
                print(f"  ⚠ 被 Cloudflare 拦截，切换配置重试...")
                time.sleep(2)
            else:
                print(f"  ⚠ 页面结构异常，尝试下一种配置...")
                time.sleep(1)

    print("  ❌ cloudscraper 全部 12 种配置均失败")
    return []


# ====================================================================
# 方案 B：普通 requests（备用，用于特定页面）
# ====================================================================
def _strategy_plain_requests() -> list:
    """备用方案：用普通 requests + 模拟真实浏览器"""
    urls = [
        # 方案 B1：常规页面
        "https://www.transfermarkt.com/statistik/neuestetransfers",
        # 方案 B2：替代页面（德国站有时更稳定）
        "https://www.transfermarkt.de/statistik/neuestetransfers",
    ]

    for url in urls:
        for h_idx, h_template in enumerate(_HEADERS_TEMPLATES, 1):
            headers = {
                **h_template,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            print(f"  🔄 尝试 requests [{url.split('/')[2]}] (头{h_idx})...")
            try:
                resp = requests.get(url, headers=headers, timeout=25)

                # 检查是否被 CF 拦截
                if "Checking your browser" in resp.text[:500]:
                    print(f"  ⚠ 被 Cloudflare 拦截")
                    continue

                soup = BeautifulSoup(resp.text, "lxml")

                # 直接找表格
                table = soup.find("table", class_="items")
                if not table:
                    print(f"  ⚠ 未找到表格")
                    continue

                tbody = table.find("tbody")
                if not tbody:
                    continue

                rows = tbody.find_all("tr", recursive=False)
                transfers = []
                for tr in rows:
                    t = _parse_row(tr)
                    if t:
                        transfers.append(t)

                if transfers:
                    print(f"  ✅ plain-requests 成功抓到 {len(transfers)} 条")
                    return transfers
            except Exception as e:
                print(f"  ⚠ 请求异常: {e}")
                continue

    return []


# ====================================================================
# 方案 C：简化版 scraping - 尝试 ESPN 转会数据
# ====================================================================
def _strategy_espn() -> list:
    """
    最终备用方案：从 ESPN FC 获取转会新闻
    注意：ESPN 页面结构可能变化，此方案只作兜底
    """
    print("  🔄 尝试备用数据源 ESPN...")
    url = "https://www.espn.com/soccer/transfers"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/125.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if "transfers" in resp.text.lower():
            print("  ✅ ESPN 页面可访问，但结构化数据提取受限")
            # ESPN 页面以 JS 渲染为主，文本抽取有限
        return []
    except Exception:
        return []


# ====================================================================
# 统一入口：自动降级
# ====================================================================
def fetch_tm_transfers() -> list:
    """
    自动降级三段式：
    1. cloudscraper （4 浏览器 x 3 UA = 12 轮）
    2. plain requests（2 URL x 3 UA）
    3. ESPN fallback
    """
    # 阶段 1 - cloudscraper
    print("  📡 [阶段1/3] cloudscraper 多配置轮换...")
    result = _strategy_cloudscraper()
    if result:
        return result

    # 阶段 2 - plain requests
    print("\n  📡 [阶段2/3] 普通 requests 尝试...")
    result = _strategy_plain_requests()
    if result:
        return result

    # 阶段 3 - 终极备用
    print("\n  📡 [阶段3/3] 备用数据源...")
    result = _strategy_espn()

    if not result:
        print("\n  ❌ 所有数据源均获取失败")

    return result


def _parse_row(tr):
    try:
        tds = tr.find_all("td", recursive=False)
        if len(tds) < 6:
            return None

        player_a = tds[0].find("a", title=True)
        if not player_a:
            return None
        player = player_a.get("title", "").strip()
        if not player:
            return None

        left_club = _extract_club(tds[3])
        joined_club = _extract_club(tds[4])
        fee = tds[5].get_text(strip=True)
        league = get_league(left_club) or get_league(joined_club) or "其他"

        return {
            "player": player,
            "from_club": left_club,
            "to_club": joined_club,
            "fee": _fmt_fee(fee),
            "status": "completed",
            "league": league,
        }
    except Exception:
        return None


def _extract_club(td):
    a = td.find("a", title=True)
    return a.get("title", "").strip() if a else ""


def _fmt_fee(fee):
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


def lookup_chinese_player(en_name):
    if en_name in PLAYERS_CN:
        return PLAYERS_CN[en_name]
    en_lower = en_name.lower()
    for key, cn_name in PLAYERS_CN.items():
        if key.lower() == en_lower:
            return cn_name
    return ""


def collect_transfer_news():
    """入口：获取转会数据并按联赛分类"""
    print("🔍 获取转会数据...")
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

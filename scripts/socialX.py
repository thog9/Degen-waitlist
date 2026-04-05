import os
import asyncio
import aiohttp
import random
import hashlib
import time
import secrets
import base64
from typing import List, Optional, Dict
from urllib.parse import parse_qs, urlparse, quote
from aiohttp_socks import ProxyConnector
from colorama import init, Fore, Style
from datetime import datetime, timezone, timedelta
from yarl import URL

init(autoreset=True)

BORDER_WIDTH = 80

CLIENT_ID             = "QVotTnk2ZUZfT09PTzFLVW1jVmw6MTpjaQ"
REDIRECT_URI          = "https://api.dream.degen.tips/api/oauth/x/login/callback"
SCOPE                 = "tweet.read users.read follows.read like.read offline.access"
CODE_CHALLENGE_METHOD = "S256"
BEARER_TOKEN          = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
DEGEN_BACKEND         = "https://api.dream.degen.tips"
DEGEN_FRONTEND        = "https://dream.degen.tips"

VN_TZ = timezone(timedelta(hours=7))

SKIP_TASK_TYPES = {
    "wallet_connect",   # cần kết nối ví thật
    "meme_post",        # cần đăng meme
    "dreams_upload",    # cần upload dream
    "x_comment",        # cần comment thật
}

CONFIG = {
    "DELAY_BETWEEN_ACCOUNTS": 5,
    "DELAY_BETWEEN_TASKS":    12,
    "THREADS":                4,
    "TIMEOUT":                60,
}

LANG = {
    'vi': {
        'title':                'DREAM DEGEN AUTO TASKS - TWITTER LOGIN',
        'loading_accounts':     'Đang tải tài khoản Twitter...',
        'found_accounts':       'Tìm thấy {count} tài khoản',
        'loading_proxies':      'Đang tải proxy...',
        'found_proxies':        'Tìm thấy {count} proxy',
        'no_proxies':           'Không tìm thấy proxy, chạy không proxy',
        'processing':           '⚙ ĐANG XỬ LÝ {count} TÀI KHOẢN',
        'init_login_failed':    'Không lấy được OAuth params từ server',
        'twitter_auth':         'Đang xác thực Twitter...',
        'twitter_auth_success': 'Twitter xác thực thành công!',
        'twitter_auth_failed':  'Twitter xác thực thất bại',
        'logging_in':           'Đang đăng nhập Dream Degen...',
        'login_success':        'Đăng nhập thành công!',
        'login_failed':         'Đăng nhập thất bại',
        'user_name':            'Name',
        'user_point':           'Point',
        'user_wallet':          'Wallet',
        'user_balance':         'Balance $DEGEN',
        'user_no_wallet':       'Chưa kết nối',
        'fetching_tasks':       'Đang lấy danh sách nhiệm vụ...',
        'found_tasks':          'Tìm thấy {total} nhiệm vụ | Có thể làm: {doable} | Bỏ qua: {skip}',
        'no_tasks':             'Không có nhiệm vụ nào để thực hiện',
        'task_doing':           'Đang thực hiện nhiệm vụ',
        'task_starting':        'Đang bắt đầu nhiệm vụ...',
        'task_waiting':         'Chờ xác minh ({sec}s)...',
        'task_verifying':       'Đang xác minh nhiệm vụ...',
        'task_success':         'Nhiệm vụ thành công!',
        'task_failed':          'Nhiệm vụ thất bại',
        'task_already_done':    'Đã hoàn thành trước đó',
        'task_skipped':         'Bỏ qua (không hỗ trợ tự động)',
        'task_points':          'Điểm nhận được',
        'task_balance':         'Balance mới',
        'task_type':            'Loại',
        'task_platform':        'Nền tảng',
        'all_tasks_done':       'Tất cả nhiệm vụ đã hoàn thành!',
        'summary':              'Tóm tắt',
        'summary_done':         'Đã làm',
        'summary_points':       'Điểm kiếm được',
        'summary_skip':         'Bỏ qua',
        'summary_fail':         'Thất bại',
        'success':              '✅ Thành công',
        'failed':               '❌ Thất bại',
        'completed':            '✅ HOÀN THÀNH: {successful}/{total} TÀI KHOẢN THÀNH CÔNG',
        'pausing':              'Tạm dừng',
        'seconds':              'giây',
        'public_ip':            'IP công khai',
        'unknown':              'Không xác định',
    },
    'en': {
        'title':                'DREAM DEGEN AUTO TASKS - TWITTER LOGIN',
        'loading_accounts':     'Loading Twitter accounts...',
        'found_accounts':       'Found {count} accounts',
        'loading_proxies':      'Loading proxies...',
        'found_proxies':        'Found {count} proxies',
        'no_proxies':           'No proxies found, running without proxy',
        'processing':           '⚙ PROCESSING {count} ACCOUNTS',
        'init_login_failed':    'Could not get OAuth params from server',
        'twitter_auth':         'Authenticating Twitter...',
        'twitter_auth_success': 'Twitter authentication successful!',
        'twitter_auth_failed':  'Twitter authentication failed',
        'logging_in':           'Logging in to Dream Degen...',
        'login_success':        'Login successful!',
        'login_failed':         'Login failed',
        'user_name':            'Name',
        'user_point':           'Point',
        'user_wallet':          'Wallet',
        'user_balance':         'Balance $DEGEN',
        'user_no_wallet':       'Not connected',
        'fetching_tasks':       'Fetching task list...',
        'found_tasks':          'Found {total} tasks | Doable: {doable} | Skipped: {skip}',
        'no_tasks':             'No tasks to perform',
        'task_doing':           'Performing task',
        'task_starting':        'Starting task...',
        'task_waiting':         'Waiting for verification ({sec}s)...',
        'task_verifying':       'Verifying task...',
        'task_success':         'Task successful!',
        'task_failed':          'Task failed',
        'task_already_done':    'Already completed',
        'task_skipped':         'Skipped (not supported)',
        'task_points':          'Points earned',
        'task_balance':         'New balance',
        'task_type':            'Type',
        'task_platform':        'Platform',
        'all_tasks_done':       'All tasks completed!',
        'summary':              'Summary',
        'summary_done':         'Done',
        'summary_points':       'Points earned',
        'summary_skip':         'Skipped',
        'summary_fail':         'Failed',
        'success':              '✅ Success',
        'failed':               '❌ Failed',
        'completed':            '✅ COMPLETED: {successful}/{total} ACCOUNTS SUCCESSFUL',
        'pausing':              'Pausing',
        'seconds':              'seconds',
        'public_ip':            'Public IP',
        'unknown':              'Unknown',
    }
}

def print_border(text: str, color=Fore.CYAN, language='vi'):
    width = BORDER_WIDTH
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}")

def print_separator(color=Fore.MAGENTA):
    print(f"{color}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")

def print_message(text: str, color=Fore.WHITE, language='vi'):
    print(f"{color}  {text}{Style.RESET_ALL}")

def generate_fingerprint(account_index: int) -> dict:
    seed = f"degen_tasks_{account_index}_{time.time()}"
    hash_val = hashlib.md5(seed.encode()).hexdigest()
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    ]
    return {
        "user_agent": user_agents[int(hash_val[:2], 16) % len(user_agents)],
        "fp_hash": hash_val[:12]
    }

def generate_pkce():
    verifier = secrets.token_urlsafe(96)
    digest = hashlib.sha256(verifier.encode('ascii')).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b'=').decode('ascii')
    return verifier, challenge

def load_accounts(filepath: str = "tokenX.txt", language='vi') -> List[Dict]:
    if not os.path.exists(filepath):
        print(f"{Fore.RED}  ❌ File {filepath} không tìm thấy!{Style.RESET_ALL}")
        return []
    accounts = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '|' in line:
                    parts = line.split('|')
                elif ':' in line:
                    parts = line.split(':')
                else:
                    continue
                if len(parts) >= 2:
                    accounts.append({
                        "auth_token": parts[0].strip(),
                        "ct0": parts[1].strip()
                    })
        if not accounts:
            print(f"{Fore.RED}  ❌ Không tìm thấy tài khoản hợp lệ trong {filepath}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}  ❌ Lỗi đọc file: {str(e)}{Style.RESET_ALL}")
    return accounts

def load_proxies(language='vi') -> List[str]:
    if not os.path.exists('proxies.txt'):
        print(f"{Fore.YELLOW}  ℹ {LANG[language]['no_proxies']}{Style.RESET_ALL}")
        return []
    proxies = []
    with open('proxies.txt', 'r', encoding='utf-8') as f:
        for line in f:
            proxy = line.strip()
            if proxy and not proxy.startswith('#'):
                proxies.append(proxy)
    if proxies:
        print(f"{Fore.YELLOW}  ℹ {LANG[language]['found_proxies'].format(count=len(proxies))}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}  ℹ {LANG[language]['no_proxies']}{Style.RESET_ALL}")
    return proxies

def parse_proxy(proxy: str) -> Optional[str]:
    if not proxy:
        return None
    try:
        if '://' in proxy:
            return proxy
        parts = proxy.split(':')
        if len(parts) == 2:
            return f"http://{parts[0]}:{parts[1]}"
        elif len(parts) == 4:
            return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
    except:
        pass
    return None

async def check_proxy_ip(session: aiohttp.ClientSession) -> str:
    try:
        async with session.get(
            'https://api.ipify.org?format=json',
            timeout=aiohttp.ClientTimeout(total=10)
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get('ip', 'Unknown')
    except:
        pass
    return 'Unknown'

class TwitterOAuth:
    def __init__(self, auth_token: str, ct0: str, fingerprint: dict, session: aiohttp.ClientSession):
        self.auth_token = auth_token
        self.ct0 = ct0
        self.fingerprint = fingerprint
        self.session = session

    def _get_headers(self, referer: str = None) -> dict:
        headers = {
            "User-Agent": self.fingerprint["user_agent"],
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Authorization": f"Bearer {BEARER_TOKEN}",
            "X-Csrf-Token": self.ct0,
            "x-twitter-active-user": "yes",
            "x-twitter-auth-type": "OAuth2Session",
            "x-twitter-client-language": "en",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-ch-ua": '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }
        if referer:
            headers["Referer"] = referer
        return headers

    def _get_cookies(self) -> dict:
        return {"auth_token": self.auth_token, "ct0": self.ct0}

    async def get_authorization_code(self, state: str, challenge: str) -> Optional[str]:
        auth_url = "https://twitter.com/i/api/2/oauth2/authorize"
        params = {
            "client_id": CLIENT_ID,
            "code_challenge": challenge,
            "code_challenge_method": CODE_CHALLENGE_METHOD,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": SCOPE,
            "state": state
        }
        referer = (
            f"https://twitter.com/i/oauth2/authorize?response_type=code"
            f"&client_id={CLIENT_ID}"
            f"&redirect_uri={quote(REDIRECT_URI, safe='')}"
            f"&scope={SCOPE.replace(' ', '%20')}"
            f"&state={state}"
            f"&code_challenge={challenge}"
            f"&code_challenge_method={CODE_CHALLENGE_METHOD}"
        )
        try:
            async with self.session.get(
                auth_url, params=params,
                headers=self._get_headers(referer),
                cookies=self._get_cookies(),
                timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])
            ) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                auth_code = data.get("auth_code")
                if not auth_code:
                    return None
                return await self._approve_authorization(auth_code, state, challenge, referer)
        except:
            return None

    async def _approve_authorization(self, auth_code: str, state: str, challenge: str, referer: str) -> Optional[str]:
        approve_url = "https://twitter.com/i/api/2/oauth2/authorize"
        headers = self._get_headers(referer)
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        data = f"approval=true&code={auth_code}"
        try:
            async with self.session.post(
                approve_url,
                headers=headers,
                cookies=self._get_cookies(),
                data=data,
                timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    redirect_uri = result.get("redirect_uri", "")
                    if redirect_uri:
                        parsed = urlparse(redirect_uri)
                        qp = parse_qs(parsed.query)
                        if 'code' in qp:
                            return qp['code'][0]
        except:
            pass
        return None

class DegenAPI:
    def __init__(self, fingerprint: dict, session: aiohttp.ClientSession):
        self.fingerprint = fingerprint
        self.session = session
        self.degen_token = None

    def _headers(self, extra: dict = None) -> dict:
        h = {
            "User-Agent": self.fingerprint["user_agent"],
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Origin": DEGEN_FRONTEND,
            "Referer": f"{DEGEN_FRONTEND}/",
            "sec-ch-ua": '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
        }
        if extra:
            h.update(extra)
        return h

    async def initiate_login(self) -> Optional[dict]:
        login_url = f"{DEGEN_BACKEND}/api/oauth/x/login?ref=thog399"
        headers = {
            "User-Agent": self.fingerprint["user_agent"],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Referer": f"{DEGEN_FRONTEND}/",
            "sec-ch-ua": '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-site",
        }
        try:
            async with self.session.get(
                login_url, headers=headers,
                allow_redirects=False,
                timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])
            ) as resp:
                location = resp.headers.get('Location', '')
                if location and ('twitter.com' in location or 'x.com' in location):
                    parsed = urlparse(location)
                    params = parse_qs(parsed.query)
                    state     = params.get('state', [None])[0]
                    challenge = params.get('code_challenge', [None])[0]
                    if state and challenge:
                        return {'state': state, 'challenge': challenge}
        except:
            pass
        return None

    async def handle_oauth_callback(self, code: str, state: str) -> bool:
        callback_url = f"{REDIRECT_URI}?state={state}&code={code}"
        headers = {
            "User-Agent": self.fingerprint["user_agent"],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Referer": "https://twitter.com/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "sec-ch-ua": '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }
        try:
            async with self.session.get(
                callback_url, headers=headers,
                allow_redirects=False,
                timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])
            ) as resp:
                for cookie_str in resp.headers.getall('Set-Cookie', []):
                    if 'degen_token=' in cookie_str:
                        token = cookie_str.split('degen_token=')[1].split(';')[0].strip()
                        if token:
                            self.session.cookie_jar.update_cookies(
                                {"degen_token": token}, URL(DEGEN_BACKEND)
                            )
                            self.degen_token = token
                            return True
        except:
            pass
        return False

    async def get_me(self) -> Optional[dict]:
        try:
            async with self.session.get(
                f"{DEGEN_BACKEND}/api/auth/me",
                headers=self._headers(),
                timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('user')
        except:
            pass
        return None

    async def get_tasks(self) -> List[dict]:
        try:
            async with self.session.get(
                f"{DEGEN_BACKEND}/api/tasks",
                headers=self._headers(),
                timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('tasks', [])
        except:
            pass
        return []

    async def start_task(self, task_id: str) -> Optional[dict]:
        try:
            async with self.session.post(
                f"{DEGEN_BACKEND}/api/tasks/{task_id}/start",
                headers=self._headers({"Content-Length": "0"}),
                timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
        except:
            pass
        return None

    async def verify_task(self, task_id: str) -> Optional[dict]:
        try:
            async with self.session.post(
                f"{DEGEN_BACKEND}/api/tasks/{task_id}/verify",
                headers=self._headers({"Content-Length": "0"}),
                timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
        except:
            pass
        return None

async def process_account(account: dict, account_index: int, proxy: Optional[str], language: str) -> bool:
    L = LANG[language]
    auth_token = account['auth_token']
    ct0 = account['ct0']
    fingerprint = generate_fingerprint(account_index)

    print(f"{Fore.MAGENTA}{'─' * BORDER_WIDTH}{Style.RESET_ALL}")
    print()
    print(f"{Fore.CYAN}  Tài khoản #{account_index + 1} (FP: {fingerprint['fp_hash']}){Style.RESET_ALL}")
    print()

    connector = None
    if proxy:
        proxy_url = parse_proxy(proxy)
        if proxy_url:
            connector = ProxyConnector.from_url(proxy_url)

    timeout = aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        if proxy:
            public_ip = await check_proxy_ip(session)
            print(f"{Fore.CYAN}  🔄 Proxy: {proxy} | {L['public_ip']}: {public_ip}{Style.RESET_ALL}")

        degen_api = DegenAPI(fingerprint, session)

        oauth_params = await degen_api.initiate_login()
        if not oauth_params:
            print(f"{Fore.RED}  ✖ {L['init_login_failed']}{Style.RESET_ALL}")
            return False

        print(f"{Fore.CYAN}  > {L['twitter_auth']}{Style.RESET_ALL}")
        twitter_oauth = TwitterOAuth(auth_token, ct0, fingerprint, session)
        twitter_code = await twitter_oauth.get_authorization_code(
            oauth_params['state'], oauth_params['challenge']
        )
        if not twitter_code:
            print(f"{Fore.RED}  ✖ {L['twitter_auth_failed']}{Style.RESET_ALL}")
            return False
        print(f"{Fore.GREEN}  ✓ {L['twitter_auth_success']}{Style.RESET_ALL}")
        await asyncio.sleep(random.uniform(0.5, 1.0))

        print(f"{Fore.CYAN}  > {L['logging_in']}{Style.RESET_ALL}")
        login_ok = await degen_api.handle_oauth_callback(twitter_code, oauth_params['state'])
        if not login_ok:
            print(f"{Fore.RED}  ✖ {L['login_failed']}{Style.RESET_ALL}")
            return False
        print(f"{Fore.GREEN}  ✓ {L['login_success']}{Style.RESET_ALL}")

        user_info = await degen_api.get_me()
        if user_info:
            twitter_acc   = user_info.get('connectedAccounts', {}).get('twitter', {})
            display_name  = twitter_acc.get('displayName') or user_info.get('firstName', L['unknown'])
            points        = user_info.get('points', 0)
            wallet        = user_info.get('walletAddress') or L['user_no_wallet']
            token_balance = user_info.get('tokenBalance', 0)
            print(f"{Fore.WHITE}  {'─' * 40}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}  - {L['user_name']}: {Fore.YELLOW}{display_name}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}  - {L['user_point']}: {Fore.YELLOW}{points}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}  - {L['user_wallet']}: {Fore.YELLOW}{wallet}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}  - {L['user_balance']}: {Fore.YELLOW}{token_balance}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}  {'─' * 40}{Style.RESET_ALL}")

        await asyncio.sleep(random.uniform(0.5, 1.0))

        print(f"{Fore.CYAN}  > {L['fetching_tasks']}{Style.RESET_ALL}")
        all_tasks = await degen_api.get_tasks()

        doable_tasks = [
            t for t in all_tasks
            if t.get('isActive')
            and not t.get('isCompleted')
            and t.get('canStart')
            and t.get('taskType') not in SKIP_TASK_TYPES
        ]
        skip_tasks = [
            t for t in all_tasks
            if t.get('taskType') in SKIP_TASK_TYPES
            or not t.get('canStart')
        ]

        print(f"{Fore.YELLOW}  ℹ {L['found_tasks'].format(total=len(all_tasks), doable=len(doable_tasks), skip=len(skip_tasks))}{Style.RESET_ALL}")

        if not doable_tasks:
            print(f"{Fore.YELLOW}  ℹ {L['no_tasks']}{Style.RESET_ALL}")
            print()
            print(f"{Fore.GREEN}  ✅ {L['success']}{Style.RESET_ALL}")
            print()
            return True

        done_count   = 0
        total_points = 0
        fail_count   = 0

        for i, task in enumerate(doable_tasks):
            task_id    = task['_id']
            task_title = task.get('title', L['unknown'])
            task_type  = task.get('taskType', '')
            platform   = task.get('platform', '')
            delay_ms   = task.get('delayMs') or (task.get('delaySeconds', 10) * 1000)
            delay_sec  = max(int(delay_ms / 1000), 10)

            print()
            print(f"{Fore.CYAN}  > [{i+1}/{len(doable_tasks)}] {L['task_doing']}: {Fore.WHITE}{task_title}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}    - {L['task_type']}: {Fore.YELLOW}{task_type}{Fore.WHITE} | {L['task_platform']}: {Fore.YELLOW}{platform}{Style.RESET_ALL}")

            print(f"{Fore.CYAN}    > {L['task_starting']}{Style.RESET_ALL}")
            start_result = await degen_api.start_task(task_id)

            if not start_result or not start_result.get('success'):
                completion = start_result.get('completion', {}) if start_result else {}
                if completion.get('status') == 'completed':
                    print(f"{Fore.YELLOW}    ℹ {L['task_already_done']}{Style.RESET_ALL}")
                    done_count += 1
                    continue
                print(f"{Fore.RED}    ✖ {L['task_failed']}{Style.RESET_ALL}")
                fail_count += 1
                continue

            completion    = start_result.get('completion', {})
            verify_type   = completion.get('verificationType', 'delay')

            wait_sec = delay_sec + random.randint(1, 3)
            print(f"{Fore.YELLOW}    ⏳ {L['task_waiting'].format(sec=wait_sec)}{Style.RESET_ALL}")
            await asyncio.sleep(wait_sec)

            print(f"{Fore.CYAN}    > {L['task_verifying']}{Style.RESET_ALL}")
            verify_result = await degen_api.verify_task(task_id)

            if verify_result and verify_result.get('success'):
                pts         = verify_result.get('pointsEarned', task.get('points', 0))
                new_balance = verify_result.get('newBalance', '?')
                total_points += pts
                done_count   += 1
                print(f"{Fore.GREEN}    ✓ {L['task_success']}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}      - {L['task_points']}: {Fore.YELLOW}+{pts}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}      - {L['task_balance']}: {Fore.YELLOW}{new_balance}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}    ✖ {L['task_failed']}{Style.RESET_ALL}")
                fail_count += 1

            if i < len(doable_tasks) - 1:
                gap = CONFIG['DELAY_BETWEEN_TASKS'] + random.randint(1, 4)
                await asyncio.sleep(gap)

        print()
        print(f"{Fore.WHITE}  {'─' * 40}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  📊 {L['summary']}:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}     - {L['summary_done']}: {Fore.GREEN}{done_count}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}     - {L['summary_points']}: {Fore.YELLOW}+{total_points}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}     - {L['summary_skip']}: {Fore.YELLOW}{len(skip_tasks)}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}     - {L['summary_fail']}: {Fore.RED}{fail_count}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  {'─' * 40}{Style.RESET_ALL}")
        print()
        print(f"{Fore.GREEN}  ✅ {L['success']}{Style.RESET_ALL}")
        print()
        return True

async def run_socialX(language: str = 'vi'):
    print()
    print_border(LANG[language]['title'], Fore.CYAN, language)
    print()

    proxies = load_proxies(language)
    print()

    accounts = load_accounts('tokenX.txt', language)
    print(f"{Fore.YELLOW}  ℹ {LANG[language]['found_accounts'].format(count=len(accounts))}{Style.RESET_ALL}")
    print()

    if not accounts:
        return

    print_separator()
    print_border(LANG[language]['processing'].format(count=len(accounts)), Fore.MAGENTA, language)
    print()

    successful = 0
    total = len(accounts)
    semaphore = asyncio.Semaphore(CONFIG['THREADS'])

    async def process_with_semaphore(idx, acc):
        nonlocal successful
        async with semaphore:
            proxy = proxies[idx % len(proxies)] if proxies else None
            success = await process_account(acc, idx, proxy, language)
            if success:
                successful += 1
            if idx < total - 1:
                delay = CONFIG['DELAY_BETWEEN_ACCOUNTS']
                print_message(
                    f"{LANG[language]['pausing']} {delay} {LANG[language]['seconds']}...",
                    Fore.YELLOW, language
                )
                await asyncio.sleep(delay)

    tasks_coro = [process_with_semaphore(i, acc) for i, acc in enumerate(accounts)]
    await asyncio.gather(*tasks_coro, return_exceptions=True)

    print()
    print_border(
        LANG[language]['completed'].format(successful=successful, total=total),
        Fore.GREEN, language
    )
    print()


if __name__ == "__main__":
    asyncio.run(run_socialX('vi'))

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

WALLET_CONNECT_TASK_ID = "69a067f4416267f248f9a5d1"

CONFIG = {
    "DELAY_BETWEEN_ACCOUNTS": 6,
    "RETRY_ATTEMPTS":         3,
    "RETRY_DELAY":            8,
    "THREADS":                4,
    "TIMEOUT":                60,
}

LANG = {
    'vi': {
        'title':                   'DREAM DEGEN AUTO CONNECT WALLET - TWITTER LOGIN',
        'loading_accounts':        'Đang tải tài khoản Twitter...',
        'found_accounts':          'Tìm thấy {count} tài khoản',
        'loading_proxies':         'Đang tải proxy...',
        'found_proxies':           'Tìm thấy {count} proxy',
        'no_proxies':              'Không tìm thấy proxy, chạy không proxy',
        'processing':              '⚙ ĐANG XỬ LÝ {count} TÀI KHOẢN',
        'init_login_failed':       'Không lấy được OAuth params từ server',
        'twitter_auth':            'Đang xác thực Twitter...',
        'twitter_auth_success':    'Twitter xác thực thành công!',
        'twitter_auth_failed':     'Twitter xác thực thất bại',
        'logging_in':              'Đang đăng nhập Dream Degen...',
        'login_success':           'Đăng nhập thành công!',
        'login_failed':            'Đăng nhập thất bại',
        'loading_addresses':       'Đang tải địa chỉ ví từ address.txt...',
        'found_addresses':         'Tìm thấy {count} địa chỉ ví',
        'no_addresses':            'Không tìm thấy địa chỉ ví nào trong address.txt',
        'user_name':               'Name',
        'user_point':              'Point',
        'user_tier':               'Tier',
        'user_wallet':             'Wallet',
        'user_balance':            'Balance $DEGEN',
        'user_no_wallet':          'Chưa kết nối',
        'wallet_already_connected':'Ví đã kết nối trước đó',
        'wallet_new':              'Ví mới kết nối',
        'task_finding':            'Đang tìm task wallet_connect...',
        'task_found':              'Tìm thấy task wallet_connect (ID: {task_id})',
        'task_fallback':           'Dùng task ID mặc định: {task_id}',
        'task_already_done':       'Task wallet_connect đã hoàn thành trước đó',
        'task_starting':           'Đang bắt đầu task wallet_connect...',
        'task_start_ok':           'Task started!',
        'task_start_failed':       'Không thể start task',
        'connecting_wallet':       'Đang kết nối ví...',
        'connect_success':         'Kết nối ví thành công!',
        'connect_failed':          'Kết nối ví thất bại',
        'task_waiting':            'Chờ xác minh ({sec}s)...',
        'task_verifying':          'Đang xác minh task...',
        'task_verify_ok':          'Task xác minh thành công!',
        'task_verify_failed':      'Xác minh task thất bại (ví đã kết nối)',
        'task_points':             'Điểm nhận được',
        'task_balance':            'Balance mới',
        'success':                 '✅ Thành công',
        'failed':                  '❌ Thất bại',
        'completed':               '✅ HOÀN THÀNH: {successful}/{total} TÀI KHOẢN THÀNH CÔNG',
        'pausing':                 'Tạm dừng',
        'seconds':                 'giây',
        'public_ip':               'IP công khai',
        'unknown':                 'Không xác định',
    },
    'en': {
        'title':                   'DREAM DEGEN AUTO CONNECT WALLET - TWITTER LOGIN',
        'loading_accounts':        'Loading Twitter accounts...',
        'found_accounts':          'Found {count} accounts',
        'loading_proxies':         'Loading proxies...',
        'found_proxies':           'Found {count} proxies',
        'no_proxies':              'No proxies found, running without proxy',
        'processing':              '⚙ PROCESSING {count} ACCOUNTS',
        'init_login_failed':       'Could not get OAuth params from server',
        'twitter_auth':            'Authenticating Twitter...',
        'twitter_auth_success':    'Twitter authentication successful!',
        'twitter_auth_failed':     'Twitter authentication failed',
        'logging_in':              'Logging in to Dream Degen...',
        'login_success':           'Login successful!',
        'login_failed':            'Login failed',
        'loading_addresses':       'Loading wallet addresses from address.txt...',
        'found_addresses':         'Found {count} wallet addresses',
        'no_addresses':            'No wallet addresses found in address.txt',
        'user_name':               'Name',
        'user_point':              'Point',
        'user_tier':               'Tier',
        'user_wallet':             'Wallet',
        'user_balance':            'Balance $DEGEN',
        'user_no_wallet':          'Not connected',
        'wallet_already_connected':'Wallet already connected',
        'wallet_new':              'Newly connected wallet',
        'task_finding':            'Looking for wallet_connect task...',
        'task_found':              'Found wallet_connect task (ID: {task_id})',
        'task_fallback':           'Using default task ID: {task_id}',
        'task_already_done':       'wallet_connect task already completed',
        'task_starting':           'Starting wallet_connect task...',
        'task_start_ok':           'Task started!',
        'task_start_failed':       'Could not start task',
        'connecting_wallet':       'Connecting wallet...',
        'connect_success':         'Wallet connected successfully!',
        'connect_failed':          'Wallet connection failed',
        'task_waiting':            'Waiting for verification ({sec}s)...',
        'task_verifying':          'Verifying task...',
        'task_verify_ok':          'Task verified successfully!',
        'task_verify_failed':      'Task verification failed (wallet connected)',
        'task_points':             'Points earned',
        'task_balance':            'New balance',
        'success':                 '✅ Success',
        'failed':                  '❌ Failed',
        'completed':               '✅ COMPLETED: {successful}/{total} ACCOUNTS SUCCESSFUL',
        'pausing':                 'Pausing',
        'seconds':                 'seconds',
        'public_ip':               'Public IP',
        'unknown':                 'Unknown',
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
    seed = f"degen_connect_{account_index}_{time.time()}"
    hash_val = hashlib.md5(seed.encode()).hexdigest()
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    ]
    return {
        "user_agent": user_agents[int(hash_val[:2], 16) % len(user_agents)],
        "fp_hash":    hash_val[:12]
    }

def generate_pkce():
    verifier = secrets.token_urlsafe(96)
    digest   = hashlib.sha256(verifier.encode('ascii')).digest()
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
                        "ct0":        parts[1].strip()
                    })
        if not accounts:
            print(f"{Fore.RED}  ❌ Không tìm thấy tài khoản hợp lệ trong {filepath}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}  ❌ Lỗi đọc file: {str(e)}{Style.RESET_ALL}")
    return accounts

def load_wallet_addresses(filepath: str = "address.txt", language='vi') -> List[str]:
    if not os.path.exists(filepath):
        print(f"{Fore.RED}  ❌ File {filepath} không tồn tại!{Style.RESET_ALL}")
        return []
    addresses = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                addr = line.strip()
                if addr and not addr.startswith('#'):
                    addresses.append(addr)
        if addresses:
            print(f"{Fore.YELLOW}  ℹ {LANG[language]['found_addresses'].format(count=len(addresses))}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}  ❌ {LANG[language]['no_addresses']}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}  ❌ Lỗi đọc file address.txt: {str(e)}{Style.RESET_ALL}")
    return addresses

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
        self.auth_token  = auth_token
        self.ct0         = ct0
        self.fingerprint = fingerprint
        self.session     = session

    def _get_headers(self, referer: str = None) -> dict:
        headers = {
            "User-Agent":                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Accept":                    "*/*",
            "Accept-Language":           "en-US,en;q=0.9",
            "Accept-Encoding":           "gzip, deflate, br",
            "Authorization":             f"Bearer {BEARER_TOKEN}",
            "X-Csrf-Token":              self.ct0,
            "x-twitter-active-user":     "yes",
            "x-twitter-auth-type":       "OAuth2Session",
            "x-twitter-client-language": "en",
            "sec-fetch-dest":            "empty",
            "sec-fetch-mode":            "cors",
            "sec-fetch-site":            "same-origin",
            "sec-ch-ua":                 '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            "sec-ch-ua-mobile":          "?0",
            "sec-ch-ua-platform":        '"Windows"',
        }
        if referer:
            headers["Referer"] = referer
        return headers

    def _get_cookies(self) -> dict:
        return {"auth_token": self.auth_token, "ct0": self.ct0}

    async def get_authorization_code(self, state: str, challenge: str) -> Optional[str]:
        auth_url = "https://twitter.com/i/api/2/oauth2/authorize"
        params = {
            "client_id":             CLIENT_ID,
            "code_challenge":        challenge,
            "code_challenge_method": CODE_CHALLENGE_METHOD,
            "redirect_uri":          REDIRECT_URI,
            "response_type":         "code",
            "scope":                 SCOPE,
            "state":                 state
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
        self.session     = session
        self.degen_token = None

    def _headers(self, extra: dict = None) -> dict:
        h = {
            "User-Agent":         self.fingerprint["user_agent"],
            "Accept":             "application/json, text/plain, */*",
            "Accept-Language":    "en-US,en;q=0.9",
            "Accept-Encoding":    "gzip, deflate, br",
            "Origin":             DEGEN_FRONTEND,
            "Referer":            f"{DEGEN_FRONTEND}/",
            "sec-ch-ua":          '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            "sec-ch-ua-mobile":   "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest":     "empty",
            "sec-fetch-mode":     "cors",
            "sec-fetch-site":     "same-site",
        }
        if self.degen_token:
            h["Cookie"] = f"degen_token={self.degen_token}"
        if extra:
            h.update(extra)
        return h

    async def initiate_login(self) -> Optional[dict]:
        login_url = f"{DEGEN_BACKEND}/api/oauth/x/login?ref=thog399"
        headers = {
            "User-Agent":         self.fingerprint["user_agent"],
            "Accept":             "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language":    "en-US,en;q=0.9",
            "Accept-Encoding":    "gzip, deflate",
            "Referer":            f"{DEGEN_FRONTEND}/",
            "sec-ch-ua":          '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            "sec-ch-ua-mobile":   "?0",
            "sec-ch-ua-platform": '"Windows"',
            "Sec-Fetch-Dest":     "document",
            "Sec-Fetch-Mode":     "navigate",
            "Sec-Fetch-Site":     "same-site",
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
            "User-Agent":              self.fingerprint["user_agent"],
            "Accept":                  "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language":         "en-US,en;q=0.9",
            "Accept-Encoding":         "gzip, deflate, br",
            "Referer":                 "https://twitter.com/",
            "Sec-Fetch-Dest":          "document",
            "Sec-Fetch-Mode":          "navigate",
            "Sec-Fetch-Site":          "cross-site",
            "Sec-Fetch-User":          "?1",
            "Upgrade-Insecure-Requests": "1",
            "sec-ch-ua":               '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            "sec-ch-ua-mobile":        "?0",
            "sec-ch-ua-platform":      '"Windows"',
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

    async def get_wallet_connect_task(self) -> tuple:
        """Trả về (task_id, task_data). Fallback dùng hardcode nếu không tìm thấy."""
        try:
            async with self.session.get(
                f"{DEGEN_BACKEND}/api/tasks",
                headers=self._headers(),
                timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for t in data.get('tasks', []):
                        if t.get('taskType') == 'wallet_connect':
                            return t['_id'], t
        except:
            pass
        return WALLET_CONNECT_TASK_ID, {}

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

    async def connect_wallet(self, address: str) -> Optional[dict]:
        try:
            async with self.session.post(
                f"{DEGEN_BACKEND}/api/users/wallet/connect",
                headers=self._headers({"Content-Type": "application/json"}),
                json={"address": address},
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

async def process_account(account: dict, account_index: int, proxy: Optional[str], language: str, wallet_addresses: List[str]) -> bool:
    L           = LANG[language]
    auth_token  = account['auth_token']
    ct0         = account['ct0']
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
        twitter_code  = await twitter_oauth.get_authorization_code(
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
        await asyncio.sleep(random.uniform(0.5, 1.0))

        user_info      = await degen_api.get_me()
        current_wallet = ''
        tier           = L['unknown']
        token_balance  = 0
        if user_info:
            twitter_acc    = user_info.get('connectedAccounts', {}).get('twitter', {})
            display_name   = twitter_acc.get('displayName') or user_info.get('displayName') or user_info.get('firstName', L['unknown'])
            points         = user_info.get('points', 0)
            current_wallet = user_info.get('walletAddress') or ''
            tier           = user_info.get('tier', L['unknown'])
            token_balance  = user_info.get('tokenBalance', 0)
            print(f"{Fore.WHITE}  {'─' * 40}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}  - {L['user_name']}: {Fore.YELLOW}{display_name}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}  - {L['user_point']}: {Fore.YELLOW}{points}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}  - {L['user_tier']}: {Fore.YELLOW}{tier}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}  - {L['user_wallet']}: {Fore.YELLOW}{current_wallet or L['user_no_wallet']}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}  - {L['user_balance']}: {Fore.YELLOW}{token_balance}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}  {'─' * 40}{Style.RESET_ALL}")
        await asyncio.sleep(random.uniform(0.5, 1.0))

        if current_wallet and current_wallet.lower() not in ('', 'null', 'none'):
            print(f"{Fore.YELLOW}  ℹ {L['wallet_already_connected']}: {Fore.CYAN}{current_wallet}{Style.RESET_ALL}")
            print()
            print(f"{Fore.GREEN}  ✅ {L['success']}{Style.RESET_ALL}")
            print()
            return True

        if not wallet_addresses:
            print(f"{Fore.RED}  ✖ {L['no_addresses']}{Style.RESET_ALL}")
            return False

        wallet_addr = wallet_addresses[account_index % len(wallet_addresses)]

        print(f"{Fore.CYAN}  > {L['task_finding']}{Style.RESET_ALL}")
        task_id, task_data = await degen_api.get_wallet_connect_task()

        if task_data:
            print(f"{Fore.GREEN}  ✓ {L['task_found'].format(task_id=task_id)}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}  ℹ {L['task_fallback'].format(task_id=task_id)}{Style.RESET_ALL}")

        if task_data.get('isCompleted'):
            print(f"{Fore.YELLOW}  ℹ {L['task_already_done']}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}  > {L['connecting_wallet']} {wallet_addr}{Style.RESET_ALL}")
            result = await degen_api.connect_wallet(wallet_addr)
            if result and result.get('success'):
                print(f"{Fore.GREEN}  ✓ {L['connect_success']}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}    - {L['wallet_new']}: {Fore.YELLOW}{result.get('walletAddress', wallet_addr)}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}    - {L['user_tier']}: {Fore.YELLOW}{result.get('tier', tier)}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}    - {L['user_balance']}: {Fore.YELLOW}{result.get('tokenBalance', token_balance)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}  ✖ {L['connect_failed']}{Style.RESET_ALL}")
                if result:
                    print(f"{Fore.RED}    - Message: {result.get('message', 'Unknown error')}{Style.RESET_ALL}")
                return False
            print()
            print(f"{Fore.GREEN}  ✅ {L['success']}{Style.RESET_ALL}")
            print()
            return True

        print(f"{Fore.CYAN}  > {L['task_starting']}{Style.RESET_ALL}")
        start_result = await degen_api.start_task(task_id)
        delay_ms     = 3000  # default

        if not start_result or not start_result.get('success'):
            completion = (start_result or {}).get('completion', {})
            if completion.get('status') == 'completed':
                print(f"{Fore.YELLOW}  ℹ {L['task_already_done']}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}  ✖ {L['task_start_failed']}{Style.RESET_ALL}")
                if start_result:
                    print(f"{Fore.RED}    - Message: {start_result.get('message', 'Unknown')}{Style.RESET_ALL}")
                return False
        else:
            completion = start_result.get('completion', {})
            delay_ms   = completion.get('delayMs') or 3000
            print(f"{Fore.GREEN}  ✓ {L['task_start_ok']}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}    - verificationType: {Fore.YELLOW}{completion.get('verificationType', '?')}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}    - status: {Fore.YELLOW}{completion.get('status', '?')}{Style.RESET_ALL}")

        await asyncio.sleep(random.uniform(0.8, 1.5))

        print(f"{Fore.CYAN}  > {L['connecting_wallet']} {wallet_addr}{Style.RESET_ALL}")
        connect_result = await degen_api.connect_wallet(wallet_addr)

        if connect_result and connect_result.get('success'):
            print(f"{Fore.GREEN}  ✓ {L['connect_success']}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}    - {L['wallet_new']}: {Fore.YELLOW}{connect_result.get('walletAddress', wallet_addr)}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}    - {L['user_tier']}: {Fore.YELLOW}{connect_result.get('tier', tier)}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}    - {L['user_balance']}: {Fore.YELLOW}{connect_result.get('tokenBalance', token_balance)}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}  ✖ {L['connect_failed']}{Style.RESET_ALL}")
            if connect_result:
                print(f"{Fore.RED}    - Message: {connect_result.get('message', 'Unknown error')}{Style.RESET_ALL}")
            return False

        await asyncio.sleep(random.uniform(1.0, 2.0))

        wait_sec = max(int(delay_ms / 1000), 3) + random.randint(1, 3)
        print(f"{Fore.YELLOW}  ⏳ {L['task_waiting'].format(sec=wait_sec)}{Style.RESET_ALL}")
        await asyncio.sleep(wait_sec)

        print(f"{Fore.CYAN}  > {L['task_verifying']}{Style.RESET_ALL}")
        verify_result = await degen_api.verify_task(task_id)

        if verify_result and verify_result.get('success'):
            pts         = verify_result.get('pointsEarned', 0)
            new_balance = verify_result.get('newBalance', '?')
            print(f"{Fore.GREEN}  ✓ {L['task_verify_ok']}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}    - {L['task_points']}: {Fore.YELLOW}+{pts}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}    - {L['task_balance']}: {Fore.YELLOW}{new_balance}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}  ⚠ {L['task_verify_failed']}{Style.RESET_ALL}")
            if verify_result:
                print(f"{Fore.YELLOW}    - Message: {verify_result.get('message', 'Unknown')}{Style.RESET_ALL}")

        print()
        print(f"{Fore.GREEN}  ✅ {L['success']}{Style.RESET_ALL}")
        print()
        return True

async def run_connect(language: str = 'vi'):
    print()
    print_border(LANG[language]['title'], Fore.CYAN, language)
    print()

    proxies = load_proxies(language)
    print()

    accounts = load_accounts('tokenX.txt', language)
    print(f"{Fore.YELLOW}  ℹ {LANG[language]['found_accounts'].format(count=len(accounts))}{Style.RESET_ALL}")
    print()

    print(f"{Fore.CYAN}  ℹ {LANG[language]['loading_addresses']}{Style.RESET_ALL}")
    wallet_addresses = load_wallet_addresses('address.txt', language)
    print()

    if not accounts:
        print(f"{Fore.RED}  ❌ Cần tokenX.txt để chạy!{Style.RESET_ALL}")
        return

    if not wallet_addresses:
        print(f"{Fore.RED}  ❌ Cần address.txt để chạy!{Style.RESET_ALL}")
        return

    print_separator()
    print_border(LANG[language]['processing'].format(count=len(accounts)), Fore.MAGENTA, language)
    print()

    successful = 0
    total      = len(accounts)
    semaphore  = asyncio.Semaphore(CONFIG['THREADS'])

    async def process_with_semaphore(idx, acc):
        nonlocal successful
        async with semaphore:
            proxy   = proxies[idx % len(proxies)] if proxies else None
            success = await process_account(acc, idx, proxy, language, wallet_addresses)
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
    asyncio.run(run_connect('vi'))

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

CONFIG = {
    "DELAY_BETWEEN_ACCOUNTS": 5,
    "RETRY_ATTEMPTS": 3,
    "RETRY_DELAY": 6,
    "THREADS": 4,
    "TIMEOUT": 60,
}

LANG = {
    'vi': {
        'title':                   'DREAM DEGEN AUTO SPIN - TWITTER LOGIN',
        'loading_accounts':        'Đang tải tài khoản Twitter...',
        'found_accounts':          'Tìm thấy {count} tài khoản',
        'loading_proxies':         'Đang tải proxy...',
        'found_proxies':           'Tìm thấy {count} proxy',
        'no_proxies':              'Không tìm thấy proxy, chạy không proxy',
        'processing':              '⚙ ĐANG XỬ LÝ {count} TÀI KHOẢN',
        'init_login':              'Đang khởi tạo phiên đăng nhập...',
        'init_login_failed':       'Không lấy được OAuth params từ server',
        'twitter_auth':            'Đang xác thực Twitter...',
        'twitter_auth_success':    'Twitter xác thực thành công!',
        'twitter_auth_failed':     'Twitter xác thực thất bại',
        'logging_in':              'Đang đăng nhập Dream Degen...',
        'login_success':           'Đăng nhập thành công!',
        'login_failed':            'Đăng nhập thất bại',
        'user_name':               'Name',
        'user_point':              'Point',
        'user_wallet':             'Wallet',
        'user_balance':            'Balance $DEGEN',
        'user_no_wallet':          'Chưa kết nối',
        'spinning_action':         'Thực hiện quay ( Spin The Wheel )...',
        'spinning_doing':          'Đang thực hiện quay ( Spin The Wheel )...',
        'spin_success':            'Thực hiện quay ( Spin The Wheel ) thành công!',
        'spin_failed':             'Quay thất bại',
        'spin_point':              'Point',
        'spin_reward':             'Phần thưởng',
        'spin_balance':            'Balance',
        'spin_next':               'Thời gian thực hiện lại',
        'already_spun_title':      'Tài khoản này đã quay rồi! Vui lòng thực hiện lại sau...',
        'already_spun_point':      'Point đã quay',
        'already_spun_reward':     'Phần thưởng',
        'already_spun_date':       'Thời gian đã quay',
        'already_spun_next':       'Thời gian thực hiện lại',
        'merch_redeemed':          'Đã đổi Merchandising rồi',
        'whitelist_redeemed':      'Đã đổi Whitelist rồi',
        'out_of_stock':            'Hết hàng',
        'success':                 '✅ Thành công',
        'failed':                  '❌ Thất bại',
        'error':                   'Lỗi',
        'using_proxy':             'Proxy',
        'no_proxy':                'Không proxy',
        'completed':               '✅ HOÀN THÀNH: {successful}/{total} TÀI KHOẢN THÀNH CÔNG',
        'pausing':                 'Tạm dừng',
        'seconds':                 'giây',
        'account':                 'Tài khoản',
        'public_ip':               'IP công khai',
        'unknown':                 'Không xác định',
    },
    'en': {
        'title':                   'DREAM DEGEN AUTO SPIN - TWITTER LOGIN',
        'loading_accounts':        'Loading Twitter accounts...',
        'found_accounts':          'Found {count} accounts',
        'loading_proxies':         'Loading proxies...',
        'found_proxies':           'Found {count} proxies',
        'no_proxies':              'No proxies found, running without proxy',
        'processing':              '⚙ PROCESSING {count} ACCOUNTS',
        'init_login':              'Initializing login session...',
        'init_login_failed':       'Could not get OAuth params from server',
        'twitter_auth':            'Authenticating Twitter...',
        'twitter_auth_success':    'Twitter authentication successful!',
        'twitter_auth_failed':     'Twitter authentication failed',
        'logging_in':              'Logging in to Dream Degen...',
        'login_success':           'Login successful!',
        'login_failed':            'Login failed',
        'user_name':               'Name',
        'user_point':              'Point',
        'user_wallet':             'Wallet',
        'user_balance':            'Balance $DEGEN',
        'user_no_wallet':          'Not connected',
        'spinning_action':         'Performing Spin The Wheel...',
        'spinning_doing':          'Spinning The Wheel...',
        'spin_success':            'Spin The Wheel successful!',
        'spin_failed':             'Spin failed',
        'spin_point':              'Point',
        'spin_reward':             'Reward',
        'spin_balance':            'Balance',
        'spin_next':               'Next spin at',
        'already_spun_title':      'Already spun! Please try again later...',
        'already_spun_point':      'Points earned',
        'already_spun_reward':     'Reward',
        'already_spun_date':       'Spin date',
        'already_spun_next':       'Next spin at',
        'merch_redeemed':          'Merchandising already redeemed',
        'whitelist_redeemed':      'Whitelist already redeemed',
        'out_of_stock':            'Out of stock',
        'success':                 '✅ Success',
        'failed':                  '❌ Failed',
        'error':                   'Error',
        'using_proxy':             'Proxy',
        'no_proxy':                'No proxy',
        'completed':               '✅ COMPLETED: {successful}/{total} ACCOUNTS SUCCESSFUL',
        'pausing':                 'Pausing',
        'seconds':                 'seconds',
        'account':                 'Account',
        'public_ip':               'Public IP',
        'unknown':                 'Unknown',
    }
}


def format_vn_time(iso_str: str) -> str:
    """Chuyển ISO 8601 UTC sang giờ Việt Nam: dd-mm-yyyy HH:MM:SS AM/PM"""
    try:
        dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        dt_vn = dt.astimezone(VN_TZ)
        return dt_vn.strftime('%d-%m-%Y %H:%M:%S %p')
    except:
        return iso_str


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
    seed = f"degen_spin_{account_index}_{time.time()}"
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
                auth_url,
                params=params,
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
                        query_params = parse_qs(parsed.query)
                        if 'code' in query_params:
                            return query_params['code'][0]
        except:
            pass
        return None


class DegenAPI:
    def __init__(self, fingerprint: dict, session: aiohttp.ClientSession):
        self.fingerprint = fingerprint
        self.session = session
        self.degen_token = None

    async def initiate_login(self) -> Optional[dict]:
        """Gọi /api/oauth/x/login → server tạo session, redirect về Twitter với state + challenge."""
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
                login_url,
                headers=headers,
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
                callback_url,
                headers=headers,
                allow_redirects=False,
                timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])
            ) as resp:
                all_set_cookies = resp.headers.getall('Set-Cookie', [])
                degen_token = None
                for cookie_str in all_set_cookies:
                    if 'degen_token=' in cookie_str:
                        token_part = cookie_str.split('degen_token=')[1].split(';')[0].strip()
                        if token_part:
                            degen_token = token_part
                            break
                if not degen_token:
                    return False
                self.session.cookie_jar.update_cookies(
                    {"degen_token": degen_token},
                    URL(DEGEN_BACKEND)
                )
                self.degen_token = degen_token
                return True
        except:
            return False

    async def get_me(self) -> Optional[dict]:
        """Lấy thông tin user từ /api/auth/me"""
        url = f"{DEGEN_BACKEND}/api/auth/me"
        headers = {
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
        try:
            async with self.session.get(
                url, headers=headers,
                timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('user')
        except:
            pass
        return None

    async def get_spin_status(self) -> Optional[dict]:
        url = f"{DEGEN_BACKEND}/api/spin/status"
        headers = {
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
        try:
            async with self.session.get(
                url, headers=headers,
                timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
        except:
            pass
        return None

    async def spin_wheel(self) -> Optional[dict]:
        url = f"{DEGEN_BACKEND}/api/spin"
        headers = {
            "User-Agent": self.fingerprint["user_agent"],
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Content-Length": "0",
            "Origin": DEGEN_FRONTEND,
            "Referer": f"{DEGEN_FRONTEND}/",
            "sec-ch-ua": '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
        }
        try:
            async with self.session.post(
                url, headers=headers,
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
            print(f"{Fore.CYAN}  🔄 Proxy: {proxy} | IP công khai: {public_ip}{Style.RESET_ALL}")

        degen_api = DegenAPI(fingerprint, session)

        oauth_params = await degen_api.initiate_login()
        if not oauth_params:
            print(f"{Fore.RED}  ✖ {L['init_login_failed']}{Style.RESET_ALL}")
            return False

        server_state     = oauth_params['state']
        server_challenge = oauth_params['challenge']

        print(f"{Fore.CYAN}  > {L['twitter_auth']}{Style.RESET_ALL}")
        twitter_oauth = TwitterOAuth(auth_token, ct0, fingerprint, session)
        twitter_code = await twitter_oauth.get_authorization_code(server_state, server_challenge)

        if not twitter_code:
            print(f"{Fore.RED}  ✖ {L['twitter_auth_failed']}{Style.RESET_ALL}")
            return False

        print(f"{Fore.GREEN}  ✓ {L['twitter_auth_success']}{Style.RESET_ALL}")
        await asyncio.sleep(random.uniform(0.5, 1.0))

        print(f"{Fore.CYAN}  > {L['logging_in']}{Style.RESET_ALL}")
        login_success = await degen_api.handle_oauth_callback(twitter_code, server_state)

        if not login_success:
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

        print(f"{Fore.CYAN}  > {L['spinning_action']}{Style.RESET_ALL}")
        status = await degen_api.get_spin_status()

        if status and status.get('success') and not status.get('canSpin', False):
            last_spin = status.get('lastSpin', {})
            next_at   = format_vn_time(status.get('nextSpinAt', ''))

            print(f"{Fore.YELLOW}  ℹ  {L['already_spun_title']}{Style.RESET_ALL}")
            if last_spin:
                print(f"{Fore.WHITE}     - {L['already_spun_point']}: {Fore.YELLOW}{last_spin.get('points', 0)}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}     - {L['already_spun_reward']}: {Fore.YELLOW}{last_spin.get('label', L['unknown'])}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}     - {L['already_spun_date']}: {Fore.YELLOW}{format_vn_time(last_spin.get('spinDate', ''))}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}  → {L['already_spun_next']}: {Fore.CYAN}{next_at}{Style.RESET_ALL}")
            print()
            print(f"{Fore.GREEN}  ✅ {L['success']}{Style.RESET_ALL}")
            print()
            return True

        print(f"{Fore.CYAN}  > {L['spinning_doing']}{Style.RESET_ALL}")
        result = await degen_api.spin_wheel()

        if result and result.get('success'):
            spin_result = result.get('result', {})
            points      = spin_result.get('points', 0)
            label       = spin_result.get('label', L['unknown'])
            new_balance = result.get('newBalance', '?')
            next_at     = format_vn_time(result.get('nextSpinAt', ''))

            prize_note = ''
            if spin_result.get('alreadyRedeemedMerch'):
                prize_note = f" ({L['merch_redeemed']})"
            elif spin_result.get('alreadyRedeemedWhitelist'):
                prize_note = f" ({L['whitelist_redeemed']})"
            elif spin_result.get('outOfStock'):
                prize_note = f" ({L['out_of_stock']})"

            print(f"{Fore.GREEN}  ✓ {L['spin_success']}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}     - {L['spin_point']}: {Fore.YELLOW}{points}{Fore.WHITE} | {L['spin_reward']}: {Fore.YELLOW}{label}{prize_note}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}     - {L['spin_balance']}: {Fore.YELLOW}{new_balance}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}  → {L['spin_next']}: {Fore.CYAN}{next_at}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}  ✖ {L['spin_failed']}{Style.RESET_ALL}")
            return False

        print()
        print(f"{Fore.GREEN}  ✅ {L['success']}{Style.RESET_ALL}")
        print()
        return True


async def run_spin(language: str = 'vi'):
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

    tasks = [process_with_semaphore(i, acc) for i, acc in enumerate(accounts)]
    await asyncio.gather(*tasks, return_exceptions=True)

    print()
    print_border(
        LANG[language]['completed'].format(successful=successful, total=total),
        Fore.GREEN, language
    )
    print()


if __name__ == "__main__":
    asyncio.run(run_spin('vi'))

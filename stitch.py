#!/usr/bin/env python3
"""
Google Stitch AI 设计自动化 — 通过 CDP 连接已登录 Chrome 进行操作。

前置条件:
    1. 你的 Chrome 浏览器已登录 Google 账号
    2. 你已用该账号访问过 stitch.withgoogle.com（至少一次）

用法:
    python3 stitch.py "<设计prompt>" [--launch-chrome] [--output result.png]

支持平台:
    macOS / Windows / Linux
"""

import sys
import time
import subprocess
import os
import json
import shutil
import platform
from urllib.request import urlopen


# ============================================================
# 平台适配
# ============================================================
SYSTEM = platform.system()  # 'Darwin' / 'Windows' / 'Linux'

if SYSTEM == 'Darwin':
    CHROME_EXE = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    CHROME_PROFILE_SRC = os.path.expanduser('~/Library/Application Support/Google/Chrome')
    CHROME_PROFILE_CLONE = '/tmp/chrome-profile-clone'
    KILL_CMD = ['killall', 'Google Chrome']

elif SYSTEM == 'Windows':
    # Chrome 可能安装在两个位置
    for candidate in [
        os.path.expandvars(r'%PROGRAMFILES%\Google\Chrome\Application\chrome.exe'),
        os.path.expandvars(r'%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe'),
        os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe'),
    ]:
        if os.path.exists(candidate):
            CHROME_EXE = candidate
            break
    else:
        CHROME_EXE = 'chrome.exe'  # fallback: 靠 PATH

    CHROME_PROFILE_SRC = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data')
    CHROME_PROFILE_CLONE = os.path.expandvars(r'%TEMP%\chrome-profile-clone')
    KILL_CMD = ['taskkill', '/F', '/IM', 'chrome.exe', '/T']

else:  # Linux
    CHROME_EXE = 'google-chrome'
    CHROME_PROFILE_SRC = os.path.expanduser('~/.config/google-chrome')
    CHROME_PROFILE_CLONE = '/tmp/chrome-profile-clone'
    KILL_CMD = ['pkill', '-9', 'chrome']


CDP_PORT = 9222
STITCH_URL = 'https://stitch.withgoogle.com/'


# ============================================================
# 核心功能
# ============================================================

def chrome_launch_cdp():
    """关闭现有 Chrome，克隆 profile，以 CDP 模式重新启动"""
    print('[1/5] 关闭现有 Chrome...')
    subprocess.run(KILL_CMD, capture_output=True, shell=(SYSTEM == 'Windows'))
    time.sleep(2)

    # 确保 Chrome 彻底关闭
    if SYSTEM == 'Darwin':
        subprocess.run(['killall', '-9', 'Google Chrome'], capture_output=True)
    time.sleep(1)

    print('[2/5] 克隆 Chrome profile（保留登录态）...')
    if os.path.exists(CHROME_PROFILE_CLONE):
        shutil.rmtree(CHROME_PROFILE_CLONE, ignore_errors=True)

    try:
        shutil.copytree(CHROME_PROFILE_SRC, CHROME_PROFILE_CLONE, symlinks=True)
        print(f'  源: {CHROME_PROFILE_SRC}')
        print(f'  目标: {CHROME_PROFILE_CLONE}')
    except Exception as e:
        print(f'  ⚠ 克隆失败: {e}')
        print(f'  将直接使用原始 profile（需要 --disable-features=DevToolsDebuggingRestrictions）')
        # 回退：直接用原始路径
        os.environ['USE_ORIGINAL_PROFILE'] = '1'

    print('[3/5] 启动 Chrome CDP...')
    chrome_args = [
        CHROME_EXE,
        f'--remote-debugging-port={CDP_PORT}',
    ]

    if os.environ.get('USE_ORIGINAL_PROFILE'):
        chrome_args.append(f'--user-data-dir={CHROME_PROFILE_SRC}')
        chrome_args.append('--disable-features=DevToolsDebuggingRestrictions')
    else:
        chrome_args.append(f'--user-data-dir={CHROME_PROFILE_CLONE}')

    # Windows 不设 stdout/stderr 重定向（没有 DEVNULL 的等价物在所有版本都可靠）
    if SYSTEM == 'Windows':
        subprocess.Popen(chrome_args, creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        subprocess.Popen(chrome_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    time.sleep(3)

    # 验证 CDP 可用
    print('[4/5] 验证 CDP...')
    for i in range(5):
        try:
            resp = urlopen(f'http://localhost:{CDP_PORT}/json/version', timeout=3)
            data = json.loads(resp.read())
            print(f'  ✓ CDP OK: {data.get("Browser", "unknown")}')
            break
        except Exception:
            if i < 4:
                print(f'  等待中... ({i+1}/5)')
                time.sleep(2)
    else:
        print('  ✗ CDP 启动失败')
        print('  提示: 请确保没有其他 Chrome 实例在运行')
        return False

    # 提示用户登录
    print('[5/5] 检查登录状态...')
    print('  ⚠ 如果浏览器弹出 Google 登录页面，请先在浏览器中完成登录。')
    print('  ⚠ 登录后，请访问 stitch.withgoogle.com 确保已授权。')
    return True


def stitch_generate(prompt, output_path='stitch-result.png'):
    """连接 CDP → 操作 Stitch → 输入 prompt → 等待生成 → 截图"""
    from playwright.sync_api import sync_playwright

    print(f'\n{"="*60}')
    print(f'设计任务: {prompt[:80]}{"..." if len(prompt) > 80 else ""}')
    print(f'{"="*60}\n')

    with sync_playwright() as p:
        print('→ 连接到 Chrome CDP...')
        try:
            browser = p.chromium.connect_over_cdp(f'http://localhost:{CDP_PORT}')
        except Exception as e:
            print(f'✗ 连接失败: {e}')
            print('  请先运行: python3 stitch.py --launch-chrome')
            return None

        context = browser.contexts[0]

        # 查找或打开 Stitch 页面
        stitch = None
        for page in context.pages:
            if 'stitch.withgoogle.com' in page.url:
                stitch = page
                print('→ 复用已有 Stitch 页面')
                break

        if not stitch:
            print('→ 打开 Stitch...')
            stitch = context.new_page()
            stitch.goto(STITCH_URL, wait_until='domcontentloaded')
            stitch.wait_for_timeout(4000)

        # Stitch 界面在 iframe 中（来源: app-companion-430619.appspot.com）
        print(f'→ 页面 frame 数量: {len(stitch.frames)}')
        if len(stitch.frames) < 2:
            print('→ 等待 iframe 加载...')
            stitch.wait_for_timeout(5000)

        if len(stitch.frames) < 2:
            print('✗ 未能检测到 Stitch iframe')
            print('  可能原因: 未登录 Google 账号 或 未访问过 stitch.withgoogle.com')
            print('  请在浏览器中: 1) 登录 Google  2) 打开 stitch.withgoogle.com')
            stitch.screenshot(path=output_path, full_page=True)
            return None

        frame = stitch.frames[1]

        # 选择平台「網頁」
        try:
            web_btn = frame.locator('button:has-text("網頁")')
            if web_btn.count() > 0:
                web_btn.first.click()
                stitch.wait_for_timeout(1500)
                print('→ 已选择「網頁」平台')
        except Exception:
            pass  # 可能已经选好了

        # 输入 prompt
        print('→ 输入设计 prompt...')
        textbox = frame.locator('[contenteditable="true"]').first
        textbox.click()
        textbox.fill('')
        textbox.type(prompt, delay=5)
        stitch.wait_for_timeout(1000)

        # 点击生成
        print('→ 点击生成...')
        gen_btn = None
        for selector in [
            'button[placeholder="生成設計"]',
            'button:has-text("生成")',
            'button:has-text("Generate")',
        ]:
            loc = frame.locator(selector)
            if loc.count() > 0:
                gen_btn = loc.first
                break

        if not gen_btn:
            print('✗ 未找到生成按钮，可能 Stitch UI 已变更')
            stitch.screenshot(path=output_path, full_page=True)
            return None

        gen_btn.click()

        # 等待生成完成（最长 150s）
        print('→ 等待生成完成...')
        done = False
        for i in range(30):
            time.sleep(5)
            try:
                body_text = frame.evaluate('() => document.body.innerText')
                if '正在生成' not in body_text and 'Generating' not in body_text:
                    elapsed = (i + 1) * 5
                    print(f'  ✓ 生成完成！(等待 {elapsed}s)')
                    done = True
                    break
            except Exception:
                pass
            print(f'  ... {(i+1)*5}s')

        if not done:
            print('  ⚠ 等待超时，可能是生成时间较长或出错')
            print('  继续截图当前页面...')

        # 截图
        stitch.screenshot(path=output_path, full_page=True)
        print(f'\n✓ 截图已保存: {output_path}')
        return output_path


# ============================================================
# CLI
# ============================================================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Google Stitch AI 设计自动化 — 通过 CDP 连接已登录 Chrome 生成 UI 设计',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 首次使用：启动 CDP 模式的 Chrome（会关闭现有 Chrome）
  python3 stitch.py --launch-chrome

  # 生成设计
  python3 stitch.py "设计一个电商运营数据看板，深色主题，蓝色+橙色配色"

  # 指定输出路径
  python3 stitch.py "modern SaaS dashboard" --output ~/Desktop/design.png

  # 完整流程（启动 + 设计）
  python3 stitch.py "电商数据看板" --launch-chrome --output dashboard.png

前置条件:
  1. 你的 Chrome 浏览器已登录 Google 账号
  2. 你已用该账号访问过 stitch.withgoogle.com
  3. 已安装 playwright: pip install playwright && playwright install chromium
        """,
    )
    parser.add_argument('prompt', nargs='?',
                        help='设计 prompt（中英文均可）')
    parser.add_argument('--launch-chrome', action='store_true',
                        help='关闭现有 Chrome 并以 CDP 模式重启（首次使用必须）')
    parser.add_argument('--output', '-o', default='stitch-result.png',
                        help='输出截图路径 (默认: stitch-result.png)')
    parser.add_argument('--cdp-port', type=int, default=9222,
                        help='CDP 端口 (默认: 9222)')
    args = parser.parse_args()

    CDP_PORT = args.cdp_port

    # 检查依赖
    try:
        import playwright
    except ImportError:
        print('✗ 缺少 playwright，请运行:')
        print('  pip install playwright')
        print('  playwright install chromium')
        sys.exit(1)

    if args.launch_chrome:
        print('🚀 启动 Chrome CDP 模式...')
        print('⚠ 这将关闭你当前的所有 Chrome 窗口！')
        if not chrome_launch_cdp():
            sys.exit(1)
        print()
        if not args.prompt:
            print('Chrome CDP 已就绪，现在可以执行设计任务:')
            print(f'  python3 {__file__} "你的设计prompt"')
            sys.exit(0)

    if not args.prompt:
        parser.print_help()
        sys.exit(0)

    result = stitch_generate(args.prompt, args.output)
    if result:
        print(f'\n完成！可以用以下命令查看:')
        print(f'  open {result}  # macOS')
        print(f'  start {result}  # Windows')

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
import re
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


def stitch_export(stitch, frame, output_dir):
    """从 Stitch 页面导出设计 HTML/CSS — 多策略尝试"""
    print('\n→ 导出设计文件...')

    # 策略1: 查找「Download / 下载」按钮
    export_selectors = [
        'button:has-text("Download")',
        'button:has-text("下载")',
        'button:has-text("Export")',
        'button:has-text("导出")',
        '[aria-label="Download"]',
        '[aria-label="下载"]',
        '[aria-label="Export"]',
        '[title="Download"]',
    ]
    for sel in export_selectors:
        try:
            btn = frame.locator(sel)
            if btn.count() > 0:
                btn.first.click()
                stitch.wait_for_timeout(3000)
                print(f'  点击了: {sel}')
                break
        except Exception:
            continue

    # 策略2: 查找「...」更多菜单中的导出选项
    more_selectors = [
        'button[aria-label="More"]',
        'button:has-text("...")',
        '[aria-label="更多操作"]',
    ]
    for sel in more_selectors:
        try:
            btn = frame.locator(sel)
            if btn.count() > 0:
                btn.first.click()
                stitch.wait_for_timeout(1000)
                # 再找下载选项
                for exp_sel in export_selectors:
                    exp_btn = frame.locator(exp_sel)
                    if exp_btn.count() > 0:
                        exp_btn.first.click()
                        stitch.wait_for_timeout(3000)
                        print(f'  通过菜单点击了: {exp_sel}')
                        break
                break
        except Exception:
            continue

    # 策略3: 从 iframe 中直接提取 HTML（最后的保底方案）
    try:
        html_content = frame.evaluate('''() => {
            // 尝试找预览区的 HTML
            const preview = document.querySelector('.preview, .output, [class*="preview"], [class*="output"], iframe');
            if (preview && preview.contentDocument) {
                return preview.contentDocument.documentElement.outerHTML;
            }
            // 尝试从 body 中提取所有可见的渲染结果
            const rendered = document.querySelector('[class*="rendered"], [class*="result"], [class*="generated"]');
            if (rendered) return rendered.outerHTML;
            return null;
        }''')
        if html_content:
            os.makedirs(output_dir, exist_ok=True)
            html_path = os.path.join(output_dir, 'index.html')
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(f'<!DOCTYPE html>\n{html_content}')
            print(f'  ✓ 提取 HTML: {html_path}')
    except Exception as e:
        print(f'  ⚠ HTML 提取失败: {e}')

    # 策略4: 监听下载事件，捕获浏览器下载的文件
    try:
        download_dir = os.path.abspath(output_dir)
        os.makedirs(download_dir, exist_ok=True)
        with stitch.expect_download(timeout=10000) as download_info:
            pass  # 如果上面触发了下载，这里会捕获到
        if download_info.value:
            download_info.value.save_as(os.path.join(download_dir, download_info.value.suggested_filename))
            print(f'  ✓ 下载文件: {download_info.value.suggested_filename}')
    except Exception:
        pass  # 没有触发下载

    return output_dir


def stitch_generate(prompt, output_path='stitch-result.png', export_dir=None):
    """CDP 连接 → 首页选 Web 平台 → 选最强模型 → 输入 prompt → 按 Enter 创建项目 → 等待自动生成 → 截图"""
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

        # 始终从首页开始（确保平台选择可用）
        print('→ 打开 Stitch 首页...')
        stitch = context.new_page()
        stitch.goto(STITCH_URL, wait_until='domcontentloaded')
        stitch.wait_for_timeout(6000)

        # Stitch 界面在 iframe 中（来源: app-companion-430619.appspot.com）
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

        # 阶段1: 选择「網頁」(Web) 平台 — 平台选择器是 role="radio" 按钮，仅在首页可见
        print('→ 选择「網頁」(Web) 平台...')
        platform_selected = False
        for attempt in range(5):
            web_btn = frame.locator('button[role="radio"]:has-text("網頁")')
            if web_btn.count() > 0:
                checked = web_btn.first.get_attribute('aria-checked')
                if checked == 'true':
                    print('  ✓ 已是 Web 模式')
                    platform_selected = True
                    break
                # 点击切换到 Web
                web_btn.first.click()
                stitch.wait_for_timeout(1500)
                new_checked = web_btn.first.get_attribute('aria-checked')
                if new_checked == 'true':
                    print('  ✓ 已切换到 Web 模式')
                    platform_selected = True
                    break
                else:
                    print(f'  ⚠ 点击后 aria-checked={new_checked}，重试...')
            else:
                # 可能在项目页（无平台选择器），需要回到首页
                current_url = stitch.url
                if '/projects/' in current_url:
                    print('  → 当前在项目页，导航回首页...')
                    stitch.goto(STITCH_URL, wait_until='domcontentloaded')
                    stitch.wait_for_timeout(6000)
                    frame = stitch.frames[1] if len(stitch.frames) >= 2 else frame
            stitch.wait_for_timeout(1000)

        if not platform_selected:
            print('  ⚠ 未能切换平台，将在当前模式下继续。请手动确认 Stitch 中已选择「網頁」！')

        # 阶段2: 选择最强模型 — 使用一步到位的 JS 调用（菜单在离开 JS 上下文时会自动关闭）
        print('→ 选择最强模型...')
        model_result = frame.evaluate('''async () => {
            // 找到模型按钮
            const btns = document.querySelectorAll('button[aria-haspopup="menu"]');
            let modelBtn = null;
            for (const b of btns) {
                const t = b.textContent?.trim() || '';
                if (t.includes('Flash') || t.includes('Pro') || t.includes('Gemini')) {
                    modelBtn = b;
                    break;
                }
            }
            if (!modelBtn) return {status: 'NO BTN'};

            const currentModel = modelBtn.textContent?.trim();

            // 如果已经是 Thinking 模型，无需切换
            if (currentModel.includes('Thinking')) {
                return {status: 'ALREADY BEST', currentModel};
            }

            // 点击打开菜单
            modelBtn.click();

            // 等待 menuitem 渲染（菜单动画有延迟）
            let items = [];
            for (let i = 0; i < 15; i++) {
                await new Promise(r => setTimeout(r, 300));
                items = document.querySelectorAll('[role="menuitem"]');
                if (items.length > 0) break;
            }

            if (items.length === 0) {
                modelBtn.click();  // 关闭菜单
                return {status: 'NO ITEMS', currentModel};
            }

            // 打分选最强：Thinking > Pro > 高版本号
            let best = null;
            let bestScore = -1;
            const options = [];
            for (const item of items) {
                const text = item.textContent?.trim() || '';
                let score = 0;
                if (text.includes('Thinking')) score += 100;
                if (text.includes('Pro')) score += 50;
                const verMatch = text.match(/(\\d+\\.?\\d*)\\s*(Pro|Flash|Ultra|Max)?/);
                if (verMatch) {
                    score += parseFloat(verMatch[1]) || 0;
                }
                options.push({text: text.substring(0, 80), score});
                if (score > bestScore) {
                    bestScore = score;
                    best = item;
                }
            }

            // 只要最强模型和当前不同就切换（对比完整文本前20个字符）
            const bestText = best?.textContent?.trim()?.substring(0, 20) || '';
            const curShort = currentModel?.trim()?.substring(0, 20) || '';
            const isDifferent = !bestText.includes(curShort) && bestScore > 0;
            if (best && isDifferent) {
                best.click();
                await new Promise(r => setTimeout(r, 1000));
                const newModel = modelBtn.textContent?.trim();
                return {status: 'OK', currentModel, newModel, options};
            }

            // 关闭菜单
            modelBtn.click();
            return {status: 'ALREADY BEST', currentModel, options};
        }''')

        if model_result.get('status') == 'OK':
            print(f'  当前: {model_result.get("currentModel")}')
            print(f'  → 已切换至: {model_result.get("newModel")}')
        elif model_result.get('status') == 'ALREADY BEST':
            print(f'  当前已是最强模型: {model_result.get("currentModel")}')
        else:
            print(f'  ⚠ 模型切换未完成: {model_result}')
            print('  请在 Stitch 左上角模型选择器中手动切换到最强模型')

        # 阶段3: 输入 prompt（用键盘输入触发编辑器验证）
        print('→ 输入设计 prompt...')
        editor = frame.locator('[contenteditable="true"]').first
        try:
            editor.click(force=True)  # force=True 绕过可能的弹窗遮挡
            stitch.wait_for_timeout(500)
            # 清空已有内容
            editor.press('Control+a')
            editor.press('Backspace')
            stitch.wait_for_timeout(300)
            # 逐字输入（触发 TipTap 编辑器的 input 事件）
            editor.type(prompt, delay=3)
            stitch.wait_for_timeout(1000)
            typed = editor.text_content() or ''
            print(f'  已输入 {len(typed)} 字符')
        except Exception as e:
            print(f'  ⚠ 键盘输入失败: {e}')
            # 回退: JS 注入（注意：JS 注入可能无法触发编辑器的表单验证）
            safe_prompt = prompt.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '</p><p>')
            frame.evaluate(f"""
                const ed = document.querySelector('[contenteditable="true"]');
                if (ed) {{
                    ed.focus();
                    ed.innerHTML = '<p>{safe_prompt}</p>';
                    ed.dispatchEvent(new InputEvent('input', {{ bubbles: true }}));
                }}
            """)
            stitch.wait_for_timeout(1000)

        # 阶段4: 按 Enter 创建新项目（Stitch 会自动开始生成）
        print('→ 按 Enter 创建项目（Stitch 将自动开始生成）...')
        editor.press('Enter')
        stitch.wait_for_timeout(8000)

        # 检查是否导航到了项目页
        if '/projects/' not in stitch.url:
            print('  ⚠ 未导航到项目页，重试 Enter...')
            editor.press('Enter')
            stitch.wait_for_timeout(8000)

        if '/projects/' in stitch.url:
            print(f'  ✓ 项目已创建: {stitch.url}')
        else:
            print(f'  ⚠ 仍在首页，将尝试手动点击生成按钮')

        # 阶段5: 等待自动生成完成
        print('→ 等待生成完成（最长 5 分钟）...')
        frame = stitch.frames[1] if len(stitch.frames) >= 2 else stitch

        generation_status_texts = [
            '正在生成', 'Generating',
            '正在为您设计', 'Designing',
            '正在开始构建', 'Starting to build',
            'Mapping out', 'Predicting',
            'Design system established',
            'Crafting the detailed', 'Crafting the',
            'Creating',
        ]

        done = False
        for i in range(60):  # 最多等 5 分钟
            time.sleep(5)
            try:
                body_text = frame.evaluate('() => document.body?.innerText || ""')
                still_generating = any(t in body_text for t in generation_status_texts)
                n_frames = len(stitch.frames)

                if still_generating:
                    pass  # 仍在生成，继续等待
                elif n_frames >= 3:
                    # 有预览 frame 且没有生成状态文本 → 生成完成
                    elapsed = (i + 1) * 5
                    print(f'  ✓ 生成完成！(等待 {elapsed}s, frames={n_frames})')
                    done = True
                    break
                # 注意: 不要用「提示：」来判断完成 — 它可能在生成中就会出现
            except Exception:
                pass

            if (i + 1) % 6 == 0:  # 每 30s 输出一次
                nf = len(stitch.frames)
                print(f'  ... {(i+1)*5}s (frames={nf})')

        if not done:
            print('  ⚠ 等待超时，可能是生成时间较长或出错')
            print('  继续截图当前页面...')

        # 阶段6: 截图
        stitch.screenshot(path=output_path, full_page=True)
        print(f'\n✓ 截图已保存: {output_path}')

        # 阶段7: 导出设计文件
        if export_dir:
            stitch_export(stitch, stitch.frames[1] if len(stitch.frames) >= 2 else stitch, export_dir)

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
    parser.add_argument('--export', '-e', nargs='?', const='.stitch/designs',
                        help='导出设计 HTML/CSS 到指定目录 (默认: .stitch/designs)')
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

    result = stitch_generate(args.prompt, args.output, export_dir=args.export)
    if result:
        print(f'\n完成！可以用以下命令查看:')
        print(f'  open {result}  # macOS')
        print(f'  start {result}  # Windows')
        if args.export:
            print(f'  设计文件已导出到: {args.export}')

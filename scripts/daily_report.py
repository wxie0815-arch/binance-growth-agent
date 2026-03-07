#!/usr/bin/env python3
"""
芒果每日汇报脚本 - 北京22:00自动发给无邪
创建时间：2026-03-07 22:03 CST
"""
import requests, json, os, subprocess
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
TG_TOKEN = '8772318809:AAGfZ7ceOZdV-bNUH6_xPmwfdtJb1VVcO1w'
TG_CHAT = '1474765089'
WORKSPACE = '/home/ubuntu/.openclaw/workspace'
TASKS_FILE = f'{WORKSPACE}/data/tasks.json'

def now_cst():
    return datetime.now(CST).strftime('%Y-%m-%d %H:%M CST')

def today_str():
    return datetime.now(CST).strftime('%Y-%m-%d')

def send_telegram(msg):
    r = requests.post(
        f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
        json={'chat_id': TG_CHAT, 'text': msg},
        timeout=10
    )
    return r.json().get('ok', False)

def get_system_status():
    # 磁盘
    disk = subprocess.run(['df', '-h', '/'], capture_output=True, text=True).stdout
    disk_pct = [l for l in disk.split('\n') if '/' in l][-1].split()[4] if disk else '?'

    # 守护进程
    guard = subprocess.run(['pgrep', '-f', 'api_failover_guard'], capture_output=True, text=True)
    guard_ok = '✅ 运行中' if guard.stdout.strip() else '❌ 未运行'

    # ghost_api
    ghost = subprocess.run(['pgrep', '-f', 'ghost_api'], capture_output=True, text=True)
    ghost_ok = '✅ 运行中' if ghost.stdout.strip() else '❌ 未运行'

    # 当前模型
    try:
        cfg = json.load(open('/home/ubuntu/.openclaw/openclaw.json'))
        model = cfg.get('agents', {}).get('defaults', {}).get('model', '未知')
        model = model.split('/')[-1]
    except:
        model = '未知'

    # 邪修API
    try:
        r = requests.get('http://13.229.72.206:8899/status', timeout=5)
        xiexiu_ok = '✅ 在线' if r.status_code == 200 else '❌ 异常'
    except:
        xiexiu_ok = '❌ 不可达'

    return disk_pct, guard_ok, ghost_ok, model, xiexiu_ok

def get_today_tasks():
    try:
        data = json.load(open(TASKS_FILE))
        tasks = data.get('tasks', [])
        today = today_str()
        today_tasks = [t for t in tasks if today in t.get('received_at', '')]
        done = [t for t in today_tasks if t.get('status') == 'done']
        pending = [t for t in today_tasks if t.get('status') == 'pending']
        return len(today_tasks), len(done), len(pending)
    except:
        return 0, 0, 0

def get_failover_summary():
    log_path = f'{WORKSPACE}/memory/failover.log'
    try:
        lines = open(log_path).readlines()
        today = today_str()
        today_lines = [l.strip() for l in lines if today in l]
        switches = [l for l in today_lines if '切换' in l or '切回' in l or '故障' in l]
        return len(switches), switches[-1] if switches else '无切换事件'
    except:
        return 0, '日志不可读'

def get_today_posts():
    """读取今日日志里的发帖记录"""
    log_path = f'{WORKSPACE}/memory/{today_str()}.md'
    try:
        content = open(log_path).read()
        import re
        urls = re.findall(r'https://www\.binance\.com/square/post/\d+', content)
        return list(set(urls))
    except:
        return []

def main():
    today = today_str()
    now = now_cst()

    disk_pct, guard_ok, ghost_ok, model, xiexiu_ok = get_system_status()
    total_tasks, done_tasks, pending_tasks = get_today_tasks()
    switch_count, last_switch = get_failover_summary()
    posts = get_today_posts()

    # 读取今日记忆文件摘要
    today_log = f'{WORKSPACE}/memory/{today}.md'
    today_summary = ''
    if os.path.exists(today_log):
        lines = open(today_log).readlines()
        # 提取工作记录段
        in_section = False
        summary_lines = []
        for line in lines:
            if '工作记录' in line or '任务清单' in line:
                in_section = True
            elif in_section and line.startswith('## ') and '工作记录' not in line and '任务' not in line:
                in_section = False
            elif in_section and line.strip() and not line.startswith('#'):
                summary_lines.append(line.strip())
        today_summary = '\n'.join(summary_lines[:8])

    msg = f"""🥭 芒果每日汇报
📅 {today} 22:00 CST
{'━'*28}

📊 系统状态
  模型：{model}
  磁盘：{disk_pct}
  守护进程：{guard_ok}
  通信API：{ghost_ok}
  邪修API：{xiexiu_ok}

📋 今日任务
  收到：{total_tasks} 个 | 完成：{done_tasks} | 待处理：{pending_tasks}

🔄 模型切换
  切换次数：{switch_count}
  {'最近：' + last_switch[:60] if switch_count > 0 else '无切换事件，主模型稳定'}

📝 广场发帖：{len(posts)} 篇
{''.join(['  • ' + u.split('/')[-1] + chr(10) for u in posts]) if posts else '  今日无发帖记录'}
{'━'*28}
🖤 芒果"""

    ok = send_telegram(msg)
    print(f'[{now}] 每日汇报发送{"成功" if ok else "失败"}')
    print(msg)

if __name__ == '__main__':
    main()

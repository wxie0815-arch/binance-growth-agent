#!/usr/bin/env python3
"""
芒果通信API v3 - 双向通信
端口：8899
创建时间：2026-03-07 20:54 CST
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, os, requests
from datetime import datetime, timezone, timedelta

WORKSPACE = '/home/ubuntu/.openclaw/workspace'
TASKS_FILE = f'{WORKSPACE}/data/tasks.json'
REPORTS_FILE = f'{WORKSPACE}/data/reports.json'
XIU_API = 'http://13.229.72.206:8899'  # 邪修公网API（修复内网IP）
TG_TOKEN = '8772318809:AAGfZ7ceOZdV-bNUH6_xPmwfdtJb1VVcO1w'
TG_CHAT = '1474765089'
CST = timezone(timedelta(hours=8))

def now_cst():
    return datetime.now(CST).strftime('%Y-%m-%d %H:%M CST')

def load_json(path, default):
    try:
        with open(path) as f: return json.load(f)
    except: return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f: json.dump(data, f, ensure_ascii=False, indent=2)

def send_telegram(msg):
    try:
        requests.post(f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
            json={'chat_id': TG_CHAT, 'text': msg}, timeout=10)
    except: pass

def report_to_xiu(title, content):
    """主动汇报给邪修（公网IP）"""
    try:
        requests.post(f'{XIU_API}/task',
            json={'from': '芒果', 'title': title, 'content': content,
                  'time': now_cst()}, timeout=8)
    except: pass

class MangoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/status':
            data = {'status': 'online', 'name': '芒果', 'time': now_cst()}
        elif self.path == '/report':
            data = load_json(REPORTS_FILE, {'reports': []})
        elif self.path == '/tasks':
            data = load_json(TASKS_FILE, {'tasks': []})
        elif self.path == '/inbox':
            # 兼容邪修的 /inbox 端点
            tasks = load_json(TASKS_FILE, {'tasks': []})
            data = {'tasks': [t for t in tasks.get('tasks', []) if t.get('status') == 'pending']}
        elif self.path == '/pending':
            tasks = load_json(TASKS_FILE, {'tasks': []})
            data = {'tasks': [t for t in tasks.get('tasks', []) if t.get('status') == 'pending']}
        else:
            data = {'error': 'not found'}
        self._respond(data)

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length)) if length else {}

        if self.path == '/task':
            # 接收邪修任务
            store = load_json(TASKS_FILE, {'tasks': []})
            task = {
                **body,
                'id': len(store['tasks']) + 1,
                'received_at': now_cst(),
                'status': 'pending'
            }
            store['tasks'].append(task)
            save_json(TASKS_FILE, store)
            # 通知无邪（内容更完整）
            title = body.get('title', body.get('task', '新任务'))
            content_preview = body.get('content', body.get('task', ''))[:150]
            send_telegram(
                f'📨 收到邪修任务 #{task["id"]}\n'
                f'🕐 {now_cst()}\n'
                f'📋 {title}\n'
                f'{"─"*20}\n'
                f'{content_preview}{"..." if len(content_preview)==150 else ""}'
            )
            self._respond({'ok': True, 'task_id': task['id']})

        elif self.path == '/message':
            # 接收邪修消息（不存入任务队列，直接通知）
            content = body.get('content', body.get('message', ''))
            sender = body.get('from', '邪修')
            send_telegram(
                f'💬 {sender} 来消息了\n'
                f'🕐 {now_cst()}\n'
                f'{"─"*20}\n'
                f'{content[:300]}'
            )
            self._respond({'ok': True, 'id': int(datetime.now().timestamp())})

        elif self.path == '/report':
            # 保存汇报 + 同步给邪修
            store = load_json(REPORTS_FILE, {'reports': []})
            report = {**body, 'created_at': now_cst()}
            store['reports'].append(report)
            save_json(REPORTS_FILE, store)
            report_to_xiu(body.get('title', ''), body.get('content', ''))
            self._respond({'ok': True})

        elif self.path == '/done':
            # 任务完成标记 + 通知
            task_id = body.get('task_id')
            result = body.get('result', '')
            store = load_json(TASKS_FILE, {'tasks': []})
            for t in store['tasks']:
                if t['id'] == task_id:
                    t['status'] = 'done'
                    t['result'] = result
                    t['done_at'] = now_cst()
            save_json(TASKS_FILE, store)
            # 通知邪修ACK
            try:
                requests.post(f'{XIU_API}/task',
                    json={'from': '芒果', 'title': f'任务#{task_id}完成',
                          'content': result}, timeout=8)
            except: pass
            send_telegram(f'✅ 芒果完成任务 #{task_id}\n🕐 {now_cst()}\n{result[:150]}')
            self._respond({'ok': True})

        else:
            self._respond({'error': 'not found'}, 404)

    def _respond(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def log_message(self, *args): pass

if __name__ == '__main__':
    os.makedirs(f'{WORKSPACE}/data', exist_ok=True)
    print(f'芒果通信API v3 启动 :8899 | {now_cst()}')
    HTTPServer(('0.0.0.0', 8899), MangoHandler).serve_forever()

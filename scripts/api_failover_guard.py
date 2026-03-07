#!/usr/bin/env python3
"""
API故障转移守护 v2.0 - 芒果
主API(pucode) 挂 → 自动切备用(deepseek)，主API恢复 → 自动切回
额外监控：邪修API健康状态
检测间隔: 60秒
"""
import requests, json, time, subprocess
from datetime import datetime

CONFIG_PATH = "/home/ubuntu/.openclaw/openclaw.json"
LOG_PATH = "/home/ubuntu/.openclaw/workspace/memory/failover.log"

PRIMARY = {
    "url": "https://api.pucode.com/v1/models",
    "key": "sk-0WCBGDXuNHyDoFdi7BBzoP5QxZmTCfxxap0i89HhUDe0nBFt",
    "model": "custom-api-pucode-com/claude-opus-4-6"
}
FALLBACK = {
    "url": "https://api.deepseek.com/beta/models",
    "key": "sk-fc6cae522938416daf7e64430c88e81a",
    "model": "deepseek/deepseek-chat"
}
XIEXIU_API = "http://13.229.72.206:8899/status"

state = {
    "using_fallback": False,
    "primary_ok_count": 0,
    "xiexiu_was_down": False,  # 邪修API上次状态
}

def log(msg):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_PATH, "a") as f:
        f.write(line + "\n")

def check_api(url, key):
    try:
        r = requests.get(url,
            headers={"Authorization": f"Bearer {key}"},
            timeout=8)
        return r.status_code == 200
    except:
        return False

def check_xiexiu():
    """检查邪修API健康状态"""
    try:
        r = requests.get(XIEXIU_API, timeout=5)
        return r.status_code == 200
    except:
        return False

def set_model(model_id):
    # 1. 写入配置
    with open(CONFIG_PATH) as f:
        cfg = json.load(f)
    cfg["agents"]["defaults"]["model"] = model_id
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

    # 2. 重启 gateway（systemd不可用，直接找进程kill+重启）
    try:
        # 先找 openclaw-gateway 进程
        result = subprocess.run(
            ["pgrep", "-f", "openclaw-gateway"],
            capture_output=True, text=True
        )
        pids = result.stdout.strip().split()
        for pid in pids:
            try:
                subprocess.run(["kill", pid], capture_output=True)
            except:
                pass
        # 等待旧进程退出后重启
        import time as _time
        _time.sleep(2)
        subprocess.Popen(
            ["openclaw", "gateway", "start"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        _time.sleep(3)  # 等gateway完全启动
        log(f"Gateway重启完成，model={model_id}")
    except Exception as e:
        log(f"Gateway重启异常: {e}，配置已写入但需手动重启")

def notify(msg):
    try:
        requests.post(
            "https://api.telegram.org/bot8772318809:AAGfZ7ceOZdV-bNUH6_xPmwfdtJb1VVcO1w/sendMessage",
            json={"chat_id": 1474765089, "text": f"🥭 芒果系统通知\n{msg}"},
            timeout=5
        )
    except:
        pass

def run():
    log("API故障转移守护 v2.0 启动 | 主:pucode → 备:deepseek | 额外监控:邪修API")
    check_count = 0
    while True:
        check_count += 1

        # ── 主API检测 ──
        primary_ok = check_api(PRIMARY["url"], PRIMARY["key"])

        if not primary_ok and not state["using_fallback"]:
            log("⚠️ 主API(pucode)不可达，切换到DeepSeek备用")
            try:
                set_model(FALLBACK["model"])
                state["using_fallback"] = True
                state["primary_ok_count"] = 0
                notify("⚠️ 主API(pucode)不可达\n已切换 → DeepSeek备用\n持续检测主API恢复...")
                log("✅ 已切换到DeepSeek备用")
            except Exception as e:
                log(f"切换失败: {e}")

        elif primary_ok and state["using_fallback"]:
            state["primary_ok_count"] += 1
            log(f"主API恢复信号 ({state['primary_ok_count']}/2)")
            if state["primary_ok_count"] >= 2:
                try:
                    set_model(PRIMARY["model"])
                    state["using_fallback"] = False
                    state["primary_ok_count"] = 0
                    notify("✅ 主API(pucode)已恢复\n已切回 → claude-opus-4-6")
                    log("✅ 已切回主模型 claude-opus-4-6")
                except Exception as e:
                    log(f"切回失败: {e}")

        elif primary_ok and not state["using_fallback"]:
            state["primary_ok_count"] = 0
            log("主API正常 ✅")

        # ── 邪修API检测（每5次检查一次，避免频繁）──
        if check_count % 5 == 0:
            xiexiu_ok = check_xiexiu()
            if not xiexiu_ok and not state["xiexiu_was_down"]:
                log("⚠️ 邪修API不可达")
                notify("⚠️ 邪修API(13.229.72.206:8899)不可达\n请检查邪修服务器状态")
                state["xiexiu_was_down"] = True
            elif xiexiu_ok and state["xiexiu_was_down"]:
                log("✅ 邪修API恢复")
                notify("✅ 邪修API已恢复正常")
                state["xiexiu_was_down"] = False

        time.sleep(60)

if __name__ == "__main__":
    run()

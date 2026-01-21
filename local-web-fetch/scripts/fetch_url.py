#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地网页内容拉取工具

此脚本用于拉取指定 URL 的网页内容，并将其转换为 Markdown 格式。
不依赖任何 MCP 工具，使用 Python 标准库和 requests 库。
"""

import sys
import io
import json
import re
import argparse
from urllib.parse import urlparse, urljoin

# 设置标准输出为 UTF-8 编码（Windows 兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from html2text import HTML2Text
    HTML2TEXT_AVAILABLE = True
except ImportError:
    HTML2TEXT_AVAILABLE = False


def clean_html_with_html2text(html_content: str, base_url: str = "") -> str:
    """使用 html2text 将 HTML 转换为 Markdown"""
    if not HTML2TEXT_AVAILABLE:
        return None

    h = HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.body_width = 0  # 不换行
    h.unicode_snob = True
    h.skip_internal_links = False

    return h.handle(html_content)


def clean_html_simple(html_content: str) -> str:
    """简单的 HTML 清理（备用方案）"""
    # 移除 script 和 style 标签
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.IGNORECASE | re.DOTALL)

    # 移除所有 HTML 标签
    html_content = re.sub(r'<[^>]+>', ' ', html_content)

    # 清理多余空白
    html_content = re.sub(r'\s+', ' ', html_content)
    html_content = html_content.strip()

    return html_content


def extract_metadata(html_content: str, url: str) -> dict:
    """从 HTML 中提取元数据"""
    metadata = {'url': url}

    # 提取标题
    title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
    if title_match:
        metadata['title'] = title_match.group(1).strip()

    # 提取描述
    desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
    if desc_match:
        metadata['description'] = desc_match.group(1).strip()

    # 提取 og:title
    og_title = re.search(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
    if og_title:
        metadata['og_title'] = og_title.group(1).strip()

    # 提取 og:description
    og_desc = re.search(r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
    if og_desc:
        metadata['og_description'] = og_desc.group(1).strip()

    return metadata


def extract_main_content(html_content: str) -> str:
    """尝试提取主要内容区域"""
    # 尝试提取常见的文章容器
    patterns = [
        r'<article[^>]*>(.*?)</article>',
        r'<div[^>]*class=["\'][^"\']*content[^"\']*["\'][^>]*>(.*?)</div>',
        r'<div[^>]*id=["\']content["\'][^>]*>(.*?)</div>',
        r'<main[^>]*>(.*?)</main>',
    ]

    for pattern in patterns:
        match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(0)

    # 如果没找到，返回整个内容
    return html_content


def fetch_url(url: str, timeout: int = 30, max_length: int = 50000) -> dict:
    """
    拉取指定 URL 的内容并转换为 Markdown

    Args:
        url: 要拉取的网页 URL
        timeout: 请求超时时间（秒）
        max_length: 最大内容长度

    Returns:
        包含网页内容和元数据的字典
    """
    if not REQUESTS_AVAILABLE:
        return {
            'success': False,
            'error': 'requests 库未安装，请运行: pip install requests'
        }

    try:
        # 设置请求头，模拟浏览器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or 'utf-8'

        html_content = response.text

        # 提取元数据
        metadata = extract_metadata(html_content, url)

        # 尝试提取主要内容
        main_html = extract_main_content(html_content)

        # 转换为 Markdown
        if HTML2TEXT_AVAILABLE:
            markdown_content = clean_html_with_html2text(main_html, url)
        else:
            markdown_content = clean_html_simple(main_html)

        # 限制内容长度
        if len(markdown_content) > max_length:
            markdown_content = markdown_content[:max_length] + '\n\n... (内容过长，已截断)'

        return {
            'success': True,
            'url': response.url,
            'status_code': response.status_code,
            'metadata': metadata,
            'markdown': markdown_content,
            'content_length': len(markdown_content)
        }

    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': f'请求超时（超过 {timeout} 秒）'
        }
    except requests.exceptions.ConnectionError as e:
        return {
            'success': False,
            'error': f'连接失败: {str(e)}'
        }
    except requests.exceptions.HTTPError as e:
        return {
            'success': False,
            'error': f'HTTP 错误: {e.response.status_code}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'未知错误: {str(e)}'
        }


def main():
    parser = argparse.ArgumentParser(description='本地网页内容拉取工具 - 转换为 Markdown')
    parser.add_argument('url', help='要拉取的网页 URL')
    parser.add_argument('-t', '--timeout', type=int, default=30, help='请求超时时间（秒），默认 30')
    parser.add_argument('-l', '--max-length', type=int, default=50000, help='最大内容长度，默认 50000')
    parser.add_argument('-j', '--json', action='store_true', help='以 JSON 格式输出')

    args = parser.parse_args()

    result = fetch_url(args.url, args.timeout, args.max_length)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result['success']:
            # 输出 Markdown 格式
            title = result['metadata'].get('title') or result['metadata'].get('og_title') or '无标题'
            output = []
            output.append(f"# {title}\n")
            output.append(f"> 来源: {result['url']}\n")

            if result['metadata'].get('description'):
                output.append(f"> {result['metadata']['description']}\n")

            output.append("---\n")
            output.append(result['markdown'])

            output_text = ''.join(output)
            # 确保输出使用 UTF-8 编码
            try:
                print(output_text)
            except UnicodeEncodeError:
                print(output_text.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))
        else:
            print(f"错误: {result['error']}", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()

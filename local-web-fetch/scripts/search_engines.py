#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地搜索引擎工具

支持通过百度和 Bing 搜索引擎进行搜索，并返回结果的 Markdown 格式。
不依赖任何 MCP 工具。
"""

import sys
import io

# 设置标准输出为 UTF-8 编码（Windows 兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import json
import re
import argparse
import urllib.parse
from typing import List, Dict, Optional, Set, Tuple
from collections import defaultdict
from difflib import SequenceMatcher


# 无关内容关键词黑名单（用于过滤广告和无关内容）
IRRELEVANT_KEYWORDS: Set[str] = {
    # 广告相关
    '广告', '推广', '赞助', 'ad', 'advertisement', 'sponsored',
    # 下载/安装类（除非关键词明确包含）
    '下载', '安装', 'download', 'install', ' crack', '破解', '注册码',
    # 色情/赌博/暴力
    '赌博', '博彩', '色情', '成人', 'sex', 'porn', 'casino', 'betting',
    # 购物/价格（除非搜索关键词包含）
    '淘宝', '天猫', '京东', '拼多多', '价格', '多少钱', 'buy now', 'shop',
    # 招聘/兼职（除非搜索关键词包含）
    '招聘', '兼职', '求职', 'resume', 'job opening', 'hiring',
}

# 低质量域名黑名单
LOW_QUALITY_DOMAINS: Set[str] = {
    'ads.', 'ad.', 'tracking.', 'promo.',
    'spam.', 'fake.', 'scam.',
}


def extract_query_keywords(query: str) -> Set[str]:
    """
    从搜索查询中提取关键词

    Args:
        query: 搜索查询字符串

    Returns:
        关键词集合
    """
    # 移除特殊字符，保留中英文、数字
    cleaned = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', query, flags=re.UNICODE)

    # 分词（中文按字符/词语，英文按单词）
    words = set()

    # 提取英文单词
    english_words = re.findall(r'[a-zA-Z]{2,}', cleaned)
    words.update(w.lower() for w in english_words)

    # 提取中文词组（简单按连续中文字符）
    chinese_phrases = re.findall(r'[\u4e00-\u9fff]{2,}', cleaned)
    words.update(chinese_phrases)

    return words


def calculate_relevance_score(result: Dict, query_keywords: Set[str]) -> float:
    """
    计算搜索结果与查询的相关性得分

    Args:
        result: 搜索结果字典
        query_keywords: 查询关键词集合

    Returns:
        相关性得分 (0.0 - 1.0)
    """
    score = 0.0

    title = result.get('title', '').lower()
    snippet = result.get('snippet', '').lower()
    url = result.get('url', '').lower()

    # 合并所有文本内容
    all_text = f"{title} {snippet} {url}"

    # 1. 关键词匹配得分（权重 0.6）
    matched_keywords = 0
    for keyword in query_keywords:
        if keyword.lower() in all_text:
            matched_keywords += 1
            # 标题匹配权重更高
            if keyword.lower() in title:
                score += 0.15
            # 摘要匹配
            if keyword.lower() in snippet:
                score += 0.08
            # URL 匹配
            if keyword.lower() in url:
                score += 0.05

    # 2. 内容质量评估（权重 0.2）
    # 检查摘要长度（过短可能是广告）
    if len(snippet) > 30:
        score += 0.1
    elif len(snippet) < 10:
        score -= 0.2

    # 标题长度合理性
    if 10 <= len(title) <= 100:
        score += 0.1

    # 3. 域名质量评估（权重 0.2）
    # 检查是否包含低质量域名特征
    for bad_pattern in LOW_QUALITY_DOMAINS:
        if bad_pattern in url:
            score -= 0.3
            break

    # 知名网站加分
    quality_domains = {
        '.edu', '.gov', '.org',
        'wikipedia.', 'zhihu.', 'csdn.', 'github.',
        'stackoverflow.', 'reddit.', 'medium.',
        'jianshu.', 'bilibili.', 'douban.',
        'dev.to', 'hashnode.', 'freeCodeCamp.',
        'mdn.', 'developer.mozilla.',
    }
    for domain in quality_domains:
        if domain in url:
            score += 0.15
            break

    # 限制得分范围
    return max(0.0, min(1.0, score))


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    计算两个文本的相似度（用于检测重复内容）

    Args:
        text1, text2: 要比较的文本

    Returns:
        相似度得分 (0.0 - 1.0)
    """
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


def extract_domain(url: str) -> str:
    """
    从 URL 中提取主域名

    Args:
        url: URL 字符串

    Returns:
        主域名（如 baidu.com）
    """
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc

        # 移除 www. 前缀
        if domain.startswith('www.'):
            domain = domain[4:]

        return domain
    except:
        return ""


def check_irrelevant_content(result: Dict, query_keywords: Set[str]) -> Tuple[bool, str]:
    """
    增强版内容检查 - 实现 rerank 算法的质量评估

    Args:
        result: 搜索结果字典
        query_keywords: 查询关键词集合

    Returns:
        (是否应过滤, 过滤原因)
    """
    title = result.get('title', '').lower()
    snippet = result.get('snippet', '').lower()
    url = result.get('url', '').lower()
    combined_text = f"{title} {snippet}"

    # 1. 黑名单关键词检查（严格过滤）
    for keyword in IRRELEVANT_KEYWORDS:
        if any(keyword.lower() in qk.lower() for qk in query_keywords):
            continue
        if keyword.lower() in combined_text:
            return True, f"包含黑名单关键词: {keyword}"

    # 2. URL 质量检查
    from urllib.parse import urlparse
    parsed = urlparse(url)
    domain = parsed.netloc

    # IP 地址直接访问
    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain):
        return True, "IP 地址直接访问（不安全）"

    # 过多广告追踪参数
    if url.count('utm_') > 3:
        return True, "广告追踪参数过多"

    # 可疑域名模式
    suspicious_patterns = [
        r'\d{5,}',  # 域名包含长数字
        r'[a-z]{20,}',  # 域名包含超长字母序列
        r'[-_]{2,}',  # 多个连字符或下划线
    ]
    for pattern in suspicious_patterns:
        if re.search(pattern, domain):
            return True, f"可疑域名模式: {pattern}"

    # 3. 内容质量检查
    # 标题过短或过长
    title_len = len(result.get('title', ''))
    if title_len < 5:
        return True, "标题过短（可能是垃圾内容）"
    if title_len > 150:
        return True, "标题过长（可能是堆砌关键词）"

    # 摘要过短且标题不相关
    snippet_len = len(snippet)
    if snippet_len < 15:
        return True, "摘要过短（信息不足）"

    # 4. 标题与摘要相似度检查（防止标题党）
    if snippet and title:
        similarity = calculate_text_similarity(title, snippet)
        if similarity > 0.9:
            return True, "标题与摘要高度重复（可能是低质量内容）"

    # 5. 检查是否为纯广告页面
    ad_indicators = [
        '点击了解', '立即购买', '限时优惠', '免费试用',
        '点击查看', '了解更多', '立即咨询', '马上',
        'click here', 'buy now', 'limited time', 'free trial',
    ]
    for indicator in ad_indicators:
        if indicator in combined_text:
            # 如果查询关键词不包含该词，则判定为广告
            if not any(indicator in qk.lower() for qk in query_keywords):
                return True, f"疑似广告: {indicator}"

    return False, ""


def rerank_results(results: List[Dict], query: str, min_score: float = 0.15,
                   max_per_domain: int = 5) -> List[Dict]:
    """
    增强版 rerank 算法 - 多维度重新排序和过滤

    Args:
        results: 搜索结果列表
        query: 原始查询
        min_score: 最低相关性得分
        max_per_domain: 每个域名最多保留结果数

    Returns:
        重新排序和过滤后的结果列表
    """
    if not results:
        return []

    query_keywords = extract_query_keywords(query)

    # 第一阶段：质量过滤和基础评分
    scored_results = []
    for result in results:
        # 质量检查
        should_filter, reason = check_irrelevant_content(result, query_keywords)
        if should_filter:
            continue

        # 计算相关性得分
        relevance_score = calculate_relevance_score(result, query_keywords)

        # 计算多样性得分（避免同质化内容）
        diversity_score = calculate_diversity_score(result, results)

        # 综合得分：相关性 70% + 多样性 30%
        final_score = relevance_score * 0.7 + diversity_score * 0.3

        result['_relevance_score'] = round(relevance_score, 3)
        result['_diversity_score'] = round(diversity_score, 3)
        result['_final_score'] = round(final_score, 3)

        if final_score >= min_score:
            scored_results.append(result)

    # 第二阶段：按综合得分排序
    scored_results.sort(key=lambda x: x.get('_final_score', 0), reverse=True)

    # 第三阶段：域名多样化（每个域名最多保留 max_per_domain 个结果）
    diversified_results = []
    domain_counts = defaultdict(int)

    for result in scored_results:
        domain = extract_domain(result.get('url', ''))
        if domain_counts[domain] < max_per_domain:
            diversified_results.append(result)
            domain_counts[domain] += 1

    # 第四阶段：去除近似重复内容
    deduplicated_results = remove_near_duplicates(diversified_results)

    return deduplicated_results


def calculate_diversity_score(result: Dict, all_results: List[Dict]) -> float:
    """
    计算结果的多样性得分（奖励独特内容）

    Args:
        result: 当前结果
        all_results: 所有结果列表

    Returns:
        多样性得分 (0.0 - 1.0)
    """
    title = result.get('title', '').lower()
    snippet = result.get('snippet', '').lower()
    combined = f"{title} {snippet}"

    # 与其他结果比较
    similarities = []
    for other in all_results:
        if other is result:
            continue
        other_title = other.get('title', '').lower()
        other_snippet = other.get('snippet', '').lower()
        other_combined = f"{other_title} {other_snippet}"

        sim = calculate_text_similarity(combined, other_combined)
        similarities.append(sim)

    if not similarities:
        return 1.0

    # 平均相似度越低，多样性得分越高
    avg_similarity = sum(similarities) / len(similarities)
    diversity_score = 1.0 - avg_similarity

    return max(0.0, min(1.0, diversity_score))


def remove_near_duplicates(results: List[Dict], similarity_threshold: float = 0.85) -> List[Dict]:
    """
    移除近似重复的结果

    Args:
        results: 结果列表
        similarity_threshold: 相似度阈值，超过此值视为重复

    Returns:
        去重后的结果列表
    """
    if not results:
        return []

    unique_results = [results[0]]

    for result in results[1:]:
        is_duplicate = False
        result_text = f"{result.get('title', '')} {result.get('snippet', '')}"

        for existing in unique_results:
            existing_text = f"{existing.get('title', '')} {existing.get('snippet', '')}"
            similarity = calculate_text_similarity(result_text, existing_text)

            if similarity >= similarity_threshold:
                is_duplicate = True
                # 保留得分更高的结果
                if result.get('_final_score', 0) > existing.get('_final_score', 0):
                    unique_results.remove(existing)
                    unique_results.append(result)
                break

        if not is_duplicate:
            unique_results.append(result)

    return unique_results


def filter_by_relevance(results: List[Dict], query: str, min_score: float = 0.15) -> List[Dict]:
    """
    兼容性接口 - 调用新的 rerank_results

    Args:
        results: 搜索结果列表
        query: 原始查询
        min_score: 最低相关性得分阈值

    Returns:
        过滤后的结果列表
    """
    return rerank_results(results, query, min_score)

try:
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
    BS4_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    BS4_AVAILABLE = False


def search_baidu(query: str, num_results: int = 10) -> List[Dict]:
    """
    使用百度搜索引擎

    Args:
        query: 搜索关键词
        num_results: 返回结果数量

    Returns:
        搜索结果列表
    """
    if not REQUESTS_AVAILABLE:
        return []

    results = []
    try:
        # 构建百度搜索 URL
        search_url = f"https://www.baidu.com/s?wd={urllib.parse.quote(query)}&rn={num_results}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.baidu.com/',
        }

        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'

        if BS4_AVAILABLE:
            soup = BeautifulSoup(response.text, 'html.parser')

            # 百度搜索结果通常在 .result 容器中
            for item in soup.select('.result')[:num_results]:
                title_elem = item.select_one('h3 a')
                snippet_elem = item.select_one('.c-abstract')
                url_elem = item.select_one('h3 a')

                if title_elem and url_elem:
                    title = title_elem.get_text(strip=True)
                    url = url_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                    # 清理 URL（百度会跳转）
                    if url.startswith('/link?url='):
                        # 尝试从跳转链接中提取真实 URL
                        parsed = urllib.parse.urlparse(url)
                        params = urllib.parse.parse_qs(parsed.query)
                        real_url = params.get('url', [''])[0]
                        if real_url:
                            url = real_url

                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet,
                        'source': '百度'
                    })
        else:
            # 无 BeautifulSoup 时的备用方案：使用正则表达式
            # 提取标题和链接
            pattern = r'<h3[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?</h3>'
            for match in re.finditer(pattern, response.text, re.IGNORECASE | re.DOTALL):
                url = match.group(1)
                title = re.sub(r'<[^>]+>', '', match.group(2))
                title = title.strip()

                if url and title:
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': '',
                        'source': '百度'
                    })

                if len(results) >= num_results:
                    break

    except Exception as e:
        print(f"百度搜索出错: {str(e)}", file=sys.stderr)

    return results


def search_bing(query: str, num_results: int = 10) -> List[Dict]:
    """
    使用 Bing 搜索引擎

    Args:
        query: 搜索关键词
        num_results: 返回结果数量

    Returns:
        搜索结果列表
    """
    if not REQUESTS_AVAILABLE:
        return []

    results = []
    try:
        # 构建 Bing 搜索 URL（使用国际版，更稳定）
        search_url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}&count={num_results}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }

        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'

        if BS4_AVAILABLE:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Bing 搜索结果通常在 .b_algo 容器中
            for item in soup.select('.b_algo')[:num_results]:
                title_elem = item.select_one('h2 a')
                snippet_elem = item.select_one('.b_caption p')

                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet,
                        'source': 'Bing'
                    })
        else:
            # 无 BeautifulSoup 时的备用方案
            pattern = r'<h2[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?</h2>'
            for match in re.finditer(pattern, response.text, re.IGNORECASE | re.DOTALL):
                url = match.group(1)
                title = re.sub(r'<[^>]+>', '', match.group(2))
                title = title.strip()

                if url and title:
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': '',
                        'source': 'Bing'
                    })

                if len(results) >= num_results:
                    break

    except Exception as e:
        print(f"Bing 搜索出错: {str(e)}", file=sys.stderr)

    return results


def search_all(query: str, engines: List[str] = None, num_results: int = 10) -> List[Dict]:
    """
    使用指定的搜索引擎进行搜索

    Args:
        query: 搜索关键词
        engines: 搜索引擎列表，默认 ['baidu', 'bing']
        num_results: 每个搜索引擎返回的结果数量

    Returns:
        合并后的搜索结果列表
    """
    if engines is None:
        engines = ['baidu', 'bing']

    all_results = []

    for engine in engines:
        if engine.lower() == 'baidu':
            all_results.extend(search_baidu(query, num_results))
        elif engine.lower() == 'bing':
            all_results.extend(search_bing(query, num_results))

    return all_results


# deduplicate_results 函数已被 rerank_results 替代
# 保留为兼容性接口
def deduplicate_results(results: List[Dict]) -> List[Dict]:
    """
    兼容性接口 - 调用 rerank_results 进行去重

    Args:
        results: 搜索结果列表

    Returns:
        去重后的结果列表
    """
    if not results:
        return []
    # 使用空查询触发基础去重（不进行相关性过滤）
    return rerank_results(results, "", min_score=0.0, max_per_domain=999)


def format_results_markdown(results: List[Dict], query: str) -> str:
    """
    将搜索结果格式化为 Markdown

    Args:
        results: 搜索结果列表
        query: 搜索关键词

    Returns:
        Markdown 格式的字符串
    """
    if not results:
        return f"# 搜索结果：{query}\n\n未找到相关结果。\n"

    lines = [f"# 搜索结果：{query}\n"]
    lines.append(f"找到 {len(results)} 个相关结果\n")

    for i, result in enumerate(results, 1):
        lines.append(f"## {i}. {result['title']}\n")
        lines.append(f"**来源**: {result['source']}")
        lines.append(f"**链接**: {result['url']}\n")

        if result.get('snippet'):
            lines.append(f"{result['snippet']}\n")

        lines.append("---\n")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='本地搜索引擎工具 - 支持 Rerank 算法的智能搜索结果过滤')
    parser.add_argument('query', help='搜索关键词')
    parser.add_argument('-e', '--engines', nargs='+', default=['baidu', 'bing'],
                        choices=['baidu', 'bing'],
                        help='搜索引擎（默认: baidu bing）')
    parser.add_argument('-n', '--num-results', type=int, default=10,
                        help='每个搜索引擎返回结果数量（默认: 10）')
    parser.add_argument('--no-filter', action='store_true',
                        help='禁用 Rerank 过滤（默认启用）')
    parser.add_argument('--min-score', type=float, default=0.15,
                        help='最低相关性得分阈值（默认: 0.15），范围 0.0-1.0')
    parser.add_argument('--max-per-domain', type=int, default=3,
                        help='每个域名最多保留结果数（默认: 3）')
    parser.add_argument('--show-scores', action='store_true',
                        help='显示详细评分信息（调试用）')
    parser.add_argument('-j', '--json', action='store_true',
                        help='以 JSON 格式输出')

    args = parser.parse_args()

    if not REQUESTS_AVAILABLE:
        print("错误: 需要安装 requests 库", file=sys.stderr)
        print("请运行: pip install requests", file=sys.stderr)
        sys.exit(1)

    results = search_all(args.query, args.engines, args.num_results)
    original_count = len(results)

    # 应用 Rerank 算法
    if not args.no_filter:
        results = rerank_results(
            results,
            args.query,
            min_score=args.min_score,
            max_per_domain=args.max_per_domain
        )

        filtered_count = original_count - len(results)
        print(f"# [Rerank] 原始结果: {original_count}, 过滤后: {len(results)}, 过滤掉: {filtered_count}", file=sys.stderr)

        # 统计域名分布
        domain_stats = {}
        for r in results:
            domain = extract_domain(r.get('url', ''))
            domain_stats[domain] = domain_stats.get(domain, 0) + 1
        print(f"# [Rerank] 域名分布: {dict(sorted(domain_stats.items(), key=lambda x: x[1], reverse=True)[:5])}", file=sys.stderr)
        print("", file=sys.stderr)

    if args.json:
        # 移除内部评分字段（除非明确要求显示）
        output_results = results
        if not args.show_scores:
            output_results = []
            for r in results:
                r_copy = {k: v for k, v in r.items() if not k.startswith('_')}
                output_results.append(r_copy)

        output = {
            'query': args.query,
            'engines': args.engines,
            'total_results': len(results),
            'results': output_results
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        # 显示得分信息（如果请求）
        if args.show_scores:
            print(f"# 评分详情 (阈值: {args.min_score})\n", file=sys.stderr)
            for i, r in enumerate(results, 1):
                print(f"{i}. [{r.get('_final_score', 0):.3f}] {r.get('title', '')[:50]}...", file=sys.stderr)
            print("", file=sys.stderr)

        output = format_results_markdown(results, args.query)
        # 确保输出使用 UTF-8 编码
        try:
            print(output)
        except UnicodeEncodeError:
            # Windows 环境下可能需要使用替代字符
            print(output.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))


if __name__ == '__main__':
    main()

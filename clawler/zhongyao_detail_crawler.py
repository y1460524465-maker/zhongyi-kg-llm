import requests
from bs4 import BeautifulSoup
import csv
import os
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

MAX_WORKERS = 3
MAX_RETRIES = 3

def read_zhongyao_csv(file_path):
    """读取CSV文件，获取中药名称和链接"""
    zhongyao_list = []
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            zhongyao_list.append({"名称": row["名称"], "链接": row["链接"]})
    return zhongyao_list

def get_crawled_filenames(output_dir):
    """获取已爬取的中药文件名列表"""
    if not os.path.exists(output_dir):
        return set()
    return {f.replace('.txt', '') for f in os.listdir(output_dir) if f.endswith('.txt')}

def crawl_zhongyao_detail(url):
    """爬取单个中药的详情页"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.get_text(strip=True) if soup.title else "未知中药"

        content = ""

        main_content = soup.find('div', class_='mw-parser-output')

        if main_content:
            paragraphs = main_content.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and len(text) > 10:
                    content += f"{text}\n\n"

            headings = main_content.find_all(['h2', 'h3'])
            for heading in headings:
                heading_text = heading.get_text(strip=True)
                content += f"\n【{heading_text}】\n"

                next_sibling = heading.find_next_sibling()
                while next_sibling and next_sibling.name != 'h2' and next_sibling.name != 'h3':
                    if next_sibling.name == 'p':
                        text = next_sibling.get_text(strip=True)
                        if text and len(text) > 5:
                            content += f"{text}\n\n"
                    elif next_sibling.name == 'table':
                        rows = next_sibling.find_all('tr')
                        for row in rows:
                            cells = row.find_all(['td', 'th'])
                            row_text = " | ".join(cell.get_text(strip=True) for cell in cells)
                            if row_text and len(row_text) > 5:
                                content += f"{row_text}\n"
                        content += "\n"
                    next_sibling = next_sibling.find_next_sibling()

        if not content or len(content) < 100:
            content = soup.get_text()
            lines = content.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                if line and len(line) > 10 and not any(keyword in line for keyword in [
                    '中医理论', '中医保健', '中医食疗', '中药大全', '中医方剂',
                    '疾病大全', '中医书籍', 'Search', 'Login', '关于我们',
                    '版权声明', '服务条款', 'Copyright', '中医百科',
                    '本站致力于', '仅供参考', '涉及版权问题', '非盈利性'
                ]):
                    cleaned_lines.append(line)
            content = '\n\n'.join(cleaned_lines)

        content = re.sub(r'\n{3,}', '\n\n', content).strip()

        return {
            "title": title,
            "content": content
        }

    except Exception as e:
        return None

def sanitize_filename(filename):
    """清理文件名中的非法字符"""
    illegal_chars = r'[\\/:*?"<>|]'
    return re.sub(illegal_chars, '_', filename)

def save_zhongyao_detail(zhongyao_name, content, output_dir="中药"):
    """保存中药详情到txt文件"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    safe_name = sanitize_filename(zhongyao_name)
    file_path = os.path.join(output_dir, f"{safe_name}.txt")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return file_path

def crawl_single_zhongyao(zhongyao, output_dir="中药"):
    """爬取单个中药的完整流程"""
    name = zhongyao["名称"]
    url = zhongyao["链接"]
    
    detail = crawl_zhongyao_detail(url)
    
    if detail:
        full_content = f"中药名称: {name}\n"
        full_content += f"来源链接: {url}\n"
        full_content += "="*60 + "\n\n"
        full_content += detail["content"]
        
        save_zhongyao_detail(name, full_content, output_dir)
        return (name, True, None)
    else:
        return (name, False, "爬取失败")

def crawl_with_retry(zhongyao, output_dir="中药", max_retries=3):
    """带重试机制的爬取"""
    name = zhongyao["名称"]
    url = zhongyao["链接"]
    
    for attempt in range(max_retries):
        result = crawl_single_zhongyao(zhongyao, output_dir)
        if result[1]:
            return result
        if attempt < max_retries - 1:
            time.sleep(1)
    
    return (name, False, f"重试{max_retries}次后失败")

def main(limit=-1, max_workers=3, max_retries=3):
    csv_file = "zhongyao_list.csv"
    output_dir = "中药"

    print("正在读取中药列表...")
    zhongyao_list = read_zhongyao_csv(csv_file)
    print(f"CSV中共有 {len(zhongyao_list)} 个中药")

    crawled_names = get_crawled_filenames(output_dir)
    print(f"已爬取 {len(crawled_names)} 个中药")

    zhongyao_list = [z for z in zhongyao_list if z["名称"] not in crawled_names]
    print(f"剩余待爬取 {len(zhongyao_list)} 个中药")

    if not zhongyao_list:
        print("\n没有新的中药需要爬取！")
        return

    if limit > 0:
        zhongyao_list = zhongyao_list[:limit]
        print(f"本次限制爬取 {limit} 个中药")

    print(f"\n并行度: {max_workers} 个线程")
    print(f"最大重试次数: {max_retries} 次")
    print("\n开始并行爬取...")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    success_count = 0
    fail_count = 0
    failed_zhongyao = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_zhongyao = {executor.submit(crawl_with_retry, zhongyao, output_dir, max_retries): zhongyao for zhongyao in zhongyao_list}
        
        with tqdm(total=len(zhongyao_list), desc="爬取进度", unit="个") as pbar:
            for future in as_completed(future_to_zhongyao):
                name, success, error = future.result()
                
                if success:
                    success_count += 1
                else:
                    fail_count += 1
                    failed_zhongyao.append(name)
                    print(f"\n[FAIL] {name} - {error}")
                
                pbar.update(1)
                pbar.set_postfix({"成功": success_count, "失败": fail_count})

    print("\n" + "="*60)
    print(f"第一轮爬取完成！成功: {success_count} 个, 失败: {fail_count} 个")

    if failed_zhongyao:
        print("\n" + "="*60)
        print(f"开始重试失败的 {len(failed_zhongyao)} 个中药...")
        
        retry_success = 0
        retry_fail = 0
        still_failed = []
        
        retry_list = [z for z in zhongyao_list if z["名称"] in failed_zhongyao]
        
        with tqdm(total=len(retry_list), desc="重试进度", unit="个") as pbar:
            for zhongyao in retry_list:
                name, success, error = crawl_with_retry(zhongyao, output_dir, max_retries)
                
                if success:
                    retry_success += 1
                    print(f"\n[RETRY OK] {name}")
                else:
                    retry_fail += 1
                    still_failed.append(name)
                    print(f"\n[RETRY FAIL] {name}")
                
                pbar.update(1)
                pbar.set_postfix({"重试成功": retry_success, "仍失败": retry_fail})
        
        print("\n" + "="*60)
        print(f"重试完成！重试成功: {retry_success} 个, 仍失败: {retry_fail} 个")
        
        if still_failed:
            print(f"\n最终仍有 {len(still_failed)} 个中药爬取失败:")
            for name in still_failed[:10]:
                print(f"  - {name}")
            if len(still_failed) > 10:
                print(f"  ... 还有 {len(still_failed) - 10} 个")

    print("\n" + "="*60)
    print(f"爬取完成！新增成功: {success_count} 个, 失败: {fail_count} 个")
    print(f"详情文件已保存到: {output_dir}/")

if __name__ == '__main__':
    main(limit=-1, max_workers=3, max_retries=3)
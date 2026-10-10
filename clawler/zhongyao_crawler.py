import requests
from bs4 import BeautifulSoup
import csv
import time

def crawl_zhongyao_list():
    """爬取中药列表"""
    url = "https://zhongyibaike.com/wiki/%E4%B8%AD%E8%8D%AF%E5%A4%A7%E5%85%A8"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    for attempt in range(3):
        try:
            print(f"正在尝试爬取中药列表... (尝试 {attempt + 1}/3)")
            response = requests.get(url, headers=headers, timeout=30)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"请求失败，状态码: {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            zhongyao_list = []
            
            main_content = soup.find('div', class_='mw-parser-output')
            if main_content:
                all_links = main_content.find_all('a', href=True)
            else:
                all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                name = link.get_text(strip=True)
                href = link['href']
                if name and 'wiki' in href and len(name) > 1 and len(name) < 50:
                    if not any(kw in name for kw in ['中医', '中药', '疾病', '保健', '食疗', '书籍', '大全', '方剂', '理论', '关于', '版权', '服务', '搜索', '登录']):
                        full_url = "https://zhongyibaike.com" + href if href.startswith('/') else href
                        zhongyao_list.append({"名称": name, "链接": full_url})
            
            zhongyao_list = [dict(t) for t in {tuple(d.items()) for d in zhongyao_list}]
            
            output_file = "zhongyao_list.csv"
            with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["名称", "链接"])
                writer.writeheader()
                writer.writerows(zhongyao_list)
            
            print(f"爬取完成！共获取 {len(zhongyao_list)} 个中药")
            print(f"数据已保存到 {output_file}")
            
            return zhongyao_list
            
        except Exception as e:
            print(f"爬取过程中出现错误: {e}")
            if attempt < 2:
                print("等待5秒后重试...")
                time.sleep(5)
    
    print("爬取列表失败，返回空列表")
    return []

if __name__ == '__main__':
    crawl_zhongyao_list()
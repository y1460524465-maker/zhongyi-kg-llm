import requests
from bs4 import BeautifulSoup
import csv
import time

def crawl_fangji():
    url = "https://zhongyibaike.com/wiki/%E4%B8%AD%E5%8C%BB%E6%96%B9%E5%89%82"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        fangji_list = []
        
        # 查找方剂列表
        # 通常中医百科的方剂会在表格或列表中
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 1:
                    link_tag = cells[0].find('a')
                    if link_tag and 'href' in link_tag.attrs:
                        name = link_tag.get_text(strip=True)
                        href = link_tag['href']
                        if name and href:
                            full_url = "https://zhongyibaike.com" + href if href.startswith('/') else href
                            fangji_list.append({"名称": name, "链接": full_url})
        
        # 如果表格中没有找到，尝试查找列表形式
        if not fangji_list:
            lists = soup.find_all('ul')
            for ul in lists:
                links = ul.find_all('a')
                for link in links:
                    name = link.get_text(strip=True)
                    href = link.get('href', '')
                    if name and href and 'wiki' in href:
                        full_url = "https://zhongyibaike.com" + href if href.startswith('/') else href
                        fangji_list.append({"名称": name, "链接": full_url})
        
        # 如果还是没找到，尝试查找所有包含方剂的链接
        if not fangji_list:
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                name = link.get_text(strip=True)
                href = link['href']
                if name and 'wiki' in href and len(name) > 1:
                    full_url = "https://zhongyibaike.com" + href if href.startswith('/') else href
                    fangji_list.append({"名称": name, "链接": full_url})
        
        # 去重
        fangji_list = [dict(t) for t in {tuple(d.items()) for d in fangji_list}]
        
        # 保存到CSV
        output_file = "fangji_list.csv"
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["名称", "链接"])
            writer.writeheader()
            writer.writerows(fangji_list)
        
        print(f"爬取完成！共获取 {len(fangji_list)} 个方剂")
        print(f"数据已保存到 {output_file}")
        
        return fangji_list
        
    except Exception as e:
        print(f"爬取过程中出现错误: {e}")
        return []

if __name__ == '__main__':
    crawl_fangji()

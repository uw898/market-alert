#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
市场提醒脚本
功能：获取市场数据，判断是否满足条件，并通过 Server 酱推送微信通知。
"""

import os
import sys
import requests
from datetime import datetime


def get_market_data():
    """
    模拟获取市场数据的函数。
    你可以在这里替换为你自己的 API 调用逻辑。
    例如：requests.get('https://your-api.com/market-data')
    
    Returns:
        dict: 包含市场数据的字典，例如 {'price': 100, 'volume': 5000}
    """
    # 示例：返回一个模拟的市场价格
    # 在实际应用中，请替换为真实的 API 调用
    return {
        "price": 95,  # 假设当前价格是95
        "timestamp": datetime.now().isoformat()
    }


def should_send_alert(market_data):
    """
    判断是否需要发送警报。
    例如：当价格低于100时触发。

    Args:
        market_data (dict): 从 get_market_data() 获取的数据。

    Returns:
        bool: 如果需要发送警报则返回 True，否则返回 False。
    """
    price = market_data.get("price", 0)
    return price < 100  # 示例条件：价格低于100就报警


def send_wechat_notification(title, content):
    """
    使用 Server 酱服务发送微信通知。

    Args:
        title (str): 通知的标题。
        content (str): 通知的正文内容。
    """
    # 从环境变量中获取 Server 酱的 SCKEY
    sckey = os.environ.get('SERVERCHAN_SCKEY')
    if not sckey:
        print("错误: 未设置环境变量 'SERVERCHAN_SCKEY'。")
        print("请在 GitHub 仓库的 Settings -> Secrets and variables -> Actions 中添加。")
        sys.exit(1)

    # Server 酱的推送 URL
    url = f"https://sctapi.ftqq.com/{sckey}.send"
    data = {
        "title": title,
        "desp": content
    }

    try:
        response = requests.post(url, data=data)
        response.raise_for_status()  # 如果状态码不是2xx，会抛出异常
        
        result = response.json()
        if result.get('code') == 0:
            print(f"✅ 微信通知已成功发送！标题: {title}")
        else:
            print(f"❌ 发送失败: {result.get('message', '未知错误')}")
            sys.exit(1)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求出错: {e}")
        sys.exit(1)


def main():
    """主函数"""
    print("🚀 开始执行市场提醒脚本...")
    
    # 1. 获取市场数据
    market_data = get_market_data()
    print(f"📊 获取到市场数据: {market_data}")

    # 2. 判断是否需要报警
    if should_send_alert(market_data):
        print("⚠️  检测到触发条件！准备发送通知...")
        title = "【市场警报】价格已低于阈值！"
        content = f"当前价格: {market_data['price']}\n时间: {market_data['timestamp']}"
        
        # 3. 发送微信通知
        send_wechat_notification(title, content)
    else:
        print("👍 一切正常，无需发送通知。")

    print("🏁 脚本执行完毕。")


if __name__ == "__main__":
    main()

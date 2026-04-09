import os
import sys
import requests
from datetime import datetime

def get_market_data():
    """获取市场数据 (此处为模拟数据)"""
    return {
        "price": 95,
        "timestamp": datetime.now().isoformat()
    }

def should_send_alert(market_data):
    """判断是否需要发送警报"""
    price = market_data.get("price", 0)
    return price < 100

def send_wechat_notification(title, content):
    """通过Server酱发送微信通知"""
    sckey = os.environ.get('SERVERCHAN_SCKEY')
    if not sckey:
        print("❌ 错误: 未设置 SERVERCHAN_SCKEY 环境变量!")
        sys.exit(1)

    url = f"https://sctapi.ftqq.com/{sckey}.send"
    data = {"title": title, "desp": content}

    try:
        response = requests.post(url, data=data)
        result = response.json()
        if result.get('code') == 0:
            print(f"✅ 通知已发送: {title}")
        else:
            print(f"❌ 发送失败: {result.get('message')}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        sys.exit(1)

def main():
    print("🚀 开始执行市场监控...")
    data = get_market_data()
    print(f"📊 当前数据: {data}")

    if should_send_alert(data):
        title = "【市场警报】价格低于阈值!"
        content = f"当前价格: {data['price']}\n触发时间: {data['timestamp']}"
        send_wechat_notification(title, content)
    else:
        print("👍 市场状态正常，无需通知。")

if __name__ == "__main__":
    main()

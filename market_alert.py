import requests
import os

def send_wechat_alert(message):
    sckey = os.getenv("SERVERCHAN_SCKEY")
    if not sckey:
        print("Error: SERVERCHAN_SCKEY not set!")
        return
    
    url = f"https://sctapi.ftqq.com/{sckey}.send"
    data = {"title": "Market Alert", "desp": message}
    response = requests.post(url, data=data)
    print(f"WeChat Alert Status: {response.status_code}")

if __name__ == "__main__":
    # 这里可以添加你的市场监控逻辑
    # 示例：发送测试消息
    send_wechat_alert("✅ Market Alert Test Successful!")

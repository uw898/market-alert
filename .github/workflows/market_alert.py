#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📈 全球行情自动推送脚本
✅ 支持：A股（上证/深证/创业板）+ 港股（恒生）+ 美股（纳斯达克）
⏰ 运行频率：每小时整点（GitHub Actions cron）
📱 推送方式：ServerChan 微信推送
"""

import os
import sys
import requests
import akshare as ak
from datetime import datetime
import logging

# ============ 配置区域 ============
# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('run.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ServerChan 配置
SERVERCHAN_URL = "https://sctapi.ftqq.com/{key}.send"

# ============ 数据获取函数 ============

def get_a_stocks():
    """📈 获取A股三大指数"""
    try:
        logger.info("🔍 正在获取A股数据...")
        df = ak.stock_zh_index_spot()
        
        indices = {
            'sh000001': '上证指数',
            'sz399001': '深证成指',
            'sz399006': '创业板指'
        }
        
        result = []
        for code, name in indices.items():
            item = df[df['代码'] == code]
            if not item.empty:
                price = item['最新价'].values[0]
                change = item['涨跌幅'].values[0]
                volume = item['成交量'].values[0] if '成交量' in item.columns else 'N/A'
                
                # 涨跌符号
                change_float = float(str(change).replace('%', ''))
                sign = "📈" if change_float >= 0 else "📉"
                change_str = f"+{change}" if change_float >= 0 else f"{change}"
                
                result.append({
                    'name': name,
                    'price': price,
                    'change': change_str,
                    'volume': volume,
                    'sign': sign
                })
                logger.info(f"✓ {name}: {price} ({change_str}%)")
            else:
                logger.warning(f"✗ 未找到 {name}({code}) 数据")
        
        return result
    except Exception as e:
        logger.error(f"A股数据获取失败: {str(e)}")
        return None

def get_hk_stocks():
    """🇭🇰 获取港股恒生指数"""
    try:
        logger.info("🔍 正在获取港股数据...")
        df = ak.index_hk_spot()
        
        # 匹配恒生指数（多种可能名称）
        hsi = None
        patterns = ['恒生指数', '恒生', 'HSI']
        for pattern in patterns:
            matched = df[df['名称'].astype(str).str.contains(pattern, na=False)]
            if not matched.empty:
                hsi = matched.iloc[0]
                break
        
        if hsi is not None:
            name = hsi['名称']
            price = hsi['最新价']
            change = hsi['涨跌幅']
            
            # 涨跌符号
            change_str = str(change).strip()
            sign = "📉" if change_str.startswith('-') else "📈"
            change_display = f"+{change_str}" if not change_str.startswith('-') else change_str
            
            logger.info(f"✓ 恒生指数: {price} ({change_display}%)")
            return {
                'name': '恒生指数',
                'price': price,
                'change': change_display,
                'sign': sign
            }
        else:
            logger.warning("✗ 未匹配到恒生指数")
            return None
    except Exception as e:
        logger.error(f"港股数据获取失败: {str(e)}")
        return None

def get_us_stocks():
    """🇺🇸 获取美股纳斯达克指数"""
    try:
        logger.info("🔍 正在获取美股数据...")
        df = ak.index_us_stock_sina(symbol="纳斯达克指数")
        
        if not df.empty:
            item = df.iloc[0]
            name = "纳斯达克"
            price = item['最新价']
            change = item['涨跌幅']
            
            # 涨跌符号
            change_float = float(str(change).replace('%', ''))
            sign = "📈" if change_float >= 0 else "📉"
            change_display = f"+{change}" if change_float >= 0 else f"{change}"
            
            logger.info(f"✓ 纳斯达克: {price} ({change_display}%)")
            return {
                'name': name,
                'price': price,
                'change': change_display,
                'sign': sign
            }
        else:
            logger.warning("✗ 纳斯达克数据为空")
            return None
    except Exception as e:
        logger.error(f"美股数据获取失败: {str(e)}")
        return None

# ============ 消息格式化 ============

def format_message(a_data, hk_data, us_data):
    """📝 格式化推送消息"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    msg = f"""【🌍 全球行情播报】
⏰ 更新时间: {now} (北京时间)

"""
    
    # ========== A股部分 ==========
    msg += "━━━━━━ 🇨🇳 A股市场 ━━━━━━\n"
    if a_data:
        for item in a_data:
            msg += f"{item['sign']} {item['name']}\n"
            msg += f"   💰 点位: {item['price']}\n"
            msg += f"   📊 涨跌: {item['change']}%\n"
            if item.get('volume') != 'N/A':
                msg += f"   💱 成交: {item['volume']}\n"
            msg += "\n"
    else:
        msg += "⚠️ A股数据获取失败或非交易时段\n\n"
    
    # ========== 港股部分 ==========
    msg += "━━━━━━ 🇭🇰 港股市场 ━━━━━━\n"
    if hk_data:
        msg += f"{hk_data['sign']} {hk_data['name']}\n"
        msg += f"   💰 点位: {hk_data['price']}\n"
        msg += f"   📊 涨跌: {hk_data['change']}%\n\n"
    else:
        msg += "⚠️ 港股数据获取失败或非交易时段\n"
        msg += "   （交易时间: 9:30-12:00, 13:00-16:00）\n\n"
    
    # ========== 美股部分 ==========
    msg += "━━━━━━ 🇺🇸 美股市场 ━━━━━━\n"
    if us_data:
        msg += f"{us_data['sign']} {us_data['name']}\n"
        msg += f"   💰 点位: {us_data['price']}\n"
        msg += f"   📊 涨跌: {us_data['change']}%\n"
    else:
        msg += "⚠️ 美股数据获取失败或非交易时段\n"
        msg += "   （交易时间: 21:30-次日4:00 北京时间）\n"
    
    # ========== 免责声明 ==========
    msg += "\n━━━━━━ 📌 说明 ━━━━━━\n"
    msg += "• 本推送仅供参考，不构成投资建议\n"
    msg += "• 每小时整点自动更新（GitHub Actions）\n"
    msg += "• 数据来源: AKShare\n"
    
    return msg

# ============ 推送函数 ============

def push_to_wechat(title, content):
    """📱 推送到微信（ServerChan）"""
    key = os.getenv("SERVERCHAN_KEY")
    
    if not key:
        logger.error("❌ 未配置 SERVERCHAN_KEY 环境变量！")
        print("========================================")
        print("  ⚠️  配置错误：未找到 SERVERCHAN_KEY")
        print("  📌 请按以下步骤配置：")
        print("     1. 微信搜索「方糖服务号」")
        print("     2. 关注后点击「进入」获取 SendKey")
        print("     3. GitHub 仓库 Settings → Secrets")
        print("     4. 新建 Secret: Name=SERVERCHAN_KEY, Value=你的SendKey")
        print("========================================")
        return False
    
    try:
        logger.info("📤 正在推送消息到微信...")
        response = requests.post(
            SERVERCHAN_URL.format(key=key),
            data={
                "title": title,
                "desp": content
            },
            timeout=10
        )
        
        result = response.json()
        if result.get("errno") == 0:
            logger.info("✅ 推送成功！")
            return True
        else:
            logger.error(f"❌ 推送失败: {result}")
            return False
    except Exception as e:
        logger.error(f"❌ 推送异常: {str(e)}")
        return False

# ============ 主函数 ============

def main():
    """🚀 主执行流程"""
    logger.info("=" * 50)
    logger.info("📈 全球行情推送脚本开始执行")
    logger.info("=" * 50)
    
    # 1. 获取数据
    a_data = get_a_stocks()
    hk_data = get_hk_stocks()
    us_data = get_us_stocks()
    
    # 2. 格式化消息
    message = format_message(a_data, hk_data, us_data)
    
    # 3. 推送到微信
    success = push_to_wechat("【🌍 全球行情】每小时播报", message)
    
    # 4. 输出到控制台（方便调试）
    print("\n" + "=" * 50)
    print("📊 本次推送内容预览:")
    print("=" * 50)
    print(message)
    print("=" * 50)
    
    # 5. 返回状态码
    sys.exit(0 if success else 1)

# ============ 程序入口 ============

if __name__ == "__main__":
    main()
import yfinance as yf
import requests
import os
import pandas as pd

# استدعاء المتغيرات السرية
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

def get_market_data(symbol='EURUSD=X'):
    # جلب بيانات الأيام الثلاثة الأخيرة لضمان الحصول على إغلاق اليوم السابق بشكل صحيح
    data = yf.download(symbol, period='3d', interval='1d')
    
    if len(data) >= 2:
        # معالجة التحديث الجديد لمكتبة yfinance لتجنب خطأ Series
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
            
        yesterday_data = data.iloc[-2]
        
        # تحويل البيانات إجبارياً إلى أرقام عادية (Float)
        pdh = float(yesterday_data['High'])
        pdl = float(yesterday_data['Low'])
        close = float(yesterday_data['Close'])
        
        return pdh, pdl, close
    return None, None, None

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    requests.post(url, data=payload)

def main():
    symbol = 'EURUSD=X'
    pdh, pdl, close = get_market_data(symbol)
    
    if pdh is not None:
        # تحديد الانحياز البسيط بناءً على الإغلاق مقابل المنتصف
        mid_point = (pdh + pdl) / 2
        bias = "صاعد (Bullish)" if close > mid_point else "هابط (Bearish)"
        
        message = (
            f"📊 <b>تقرير السيولة اليومي</b> 📊\n"
            f"الزوج: EUR/USD\n\n"
            f"🎯 <b>أهداف السيولة (Draw on Liquidity):</b>\n"
            f"📈 قمة اليوم السابق (BSL): {pdh:.5f}\n"
            f"📉 قاع اليوم السابق (SSL): {pdl:.5f}\n\n"
            f"🧭 <b>الانحياز المقترح:</b> {bias}\n"
            f"<i>* الانحياز مبني على إغلاق الأمس مقارنة بنطاق التداول</i>"
        )
        send_telegram_message(message)
    else:
        send_telegram_message("❌ حدث خطأ في جلب بيانات السوق.")

if __name__ == '__main__':
    main()

"""AgentMall 24h 商城工具箱（給 agent 用的「手」）.

這裡每個函式都是一個 agent tool。重點：
  - 函式的 docstring 會「原封不動」變成給模型看的工具說明，
    所以用清楚的中文寫，模型才知道何時該叫它、要帶什麼參數。
  - 全部打同一個 mock 世界 shop.leapcore.tw（無 LLM、純 CRUD）。
  - 你的每個動作都會即時跳上投影幕訂單牆 /wall 🎉

環境變數：
  SHOP_URL    商城 base URL（預設 https://shop.leapcore.tw）
  STUDENT_ID  你的身分代號（signup 拿到，上牆顯示用）
"""
import os

import httpx

SHOP = os.environ.get("SHOP_URL", "https://shop.leapcore.tw").rstrip("/")
STUDENT = os.environ.get("STUDENT_ID", "guest")

# 結帳賽規則：lab 的 checkout 帶這個 header，手戳 API 不算數
AGENT_HEADERS = {"X-Via": "agent"}

_client = httpx.Client(base_url=SHOP, timeout=20.0)


def _get(path: str, **params):
    r = _client.get(path, params={k: v for k, v in params.items() if v is not None})
    r.raise_for_status()
    return r.json()


def _post(path: str, json=None, headers=None):
    r = _client.post(path, json=json, headers=headers)
    r.raise_for_status()
    return r.json()


def search_products(q: str = "", max_price: int = 0) -> dict:
    """搜尋商城商品。想知道「店裡有沒有 X」「預算內有什麼」就用這個。

    Args:
      q: 關鍵字，例如「耳機」「咖啡」「瑜珈墊」。留空代表列出全部。
      max_price: 預算上限（新台幣）。0 代表不限價。

    Returns:
      dict：count 與 products 清單（含 id/name/price/rating/sold）。
      要加入購物車時，請用 products 裡的 id 給 add_to_cart。
    """
    return _get("/products", q=q or None, max_price=max_price or None)


def get_weather(city: str = "Taipei") -> dict:
    """查某城市今天的天氣（決定要不要叫外送、出門訂位時很有用）。

    Args:
      city: 城市名稱，預設 Taipei。

    Returns:
      dict：weather（文字+emoji）、temp_c、rain_chance（降雨機率 %）。
    """
    return _get("/weather", city=city)


def add_to_cart(product_id: str, qty: int = 1) -> dict:
    """把商品放進「你自己的」購物車。

    Args:
      product_id: 商品 id（先用 search_products 查到），例如 p01。
      qty: 數量，預設 1。

    Returns:
      dict：加入後的購物車內容與總額 total。
    """
    return _post(f"/cart/{STUDENT}/add", json={"product_id": product_id, "qty": qty})


def view_cart() -> dict:
    """看你目前購物車裡有什麼、總額多少（結帳前先確認）。

    Returns:
      dict：items 清單與 total 總額（新台幣）。
    """
    return _get(f"/cart/{STUDENT}")


def checkout() -> dict:
    """結帳：把購物車變成正式訂單（會清空購物車、跳上投影幕訂單牆）。

    ⚠️ 這是「真的會送出去」的動作，金額不可逆。
    建議：呼叫前先 view_cart 確認金額，並讓使用者按 y 同意。

    Returns:
      dict：order_id、total、status 與一句成立訊息。
    """
    return _post(f"/checkout/{STUDENT}", headers=AGENT_HEADERS)


def order_food(restaurant_id: str, items: list[str]) -> dict:
    """跟某家餐廳叫外送。

    Args:
      restaurant_id: 餐廳 id（餐廳清單見 mock 世界，例如 r01=拉麵）。
      items: 要點的品項文字清單，例如 ["豚骨拉麵", "煎餃"]。

    Returns:
      dict：餐廳名、預計送達分鐘數 eta_minutes、狀態。
    """
    return _post(f"/food/{STUDENT}/order",
                 json={"restaurant_id": restaurant_id, "items": items})


def book_table(restaurant_id: str, time: str, people: int) -> dict:
    """到某家餐廳訂位。

    Args:
      restaurant_id: 餐廳 id，例如 r03。
      time: 時間文字，例如「19:30」或「2026-06-20 19:30」。
      people: 人數（1–12）。

    Returns:
      dict：訂位確認資訊（餐廳、時間、人數、狀態）。
    """
    return _post(f"/booking/{STUDENT}",
                 json={"restaurant_id": restaurant_id, "time": time, "people": people})


# 給 step 5/6 直接拿總額用（不經過模型）
def cart_total() -> int:
    """回傳目前購物車總額（新台幣整數）。給 hook / guardrail 內部用。"""
    try:
        return int(view_cart().get("total", 0))
    except Exception:
        return 0

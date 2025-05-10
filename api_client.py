import aiohttp
import json
import asyncio
import datetime
from config import get_api_token, validate_api_token, API_CONFIG

class ApiClient:
    def __init__(self, on_message_callback=None, on_error_callback=None, on_done_callback=None):
        """初始化API客戶端
        
        Args:
            on_message_callback: 收到消息時的回調函數
            on_error_callback: 發生錯誤時的回調函數
            on_done_callback: 完成時的回調函數
        """
        self.on_message = on_message_callback
        self.on_error = on_error_callback
        self.on_done = on_done_callback
        self.session = None
        self.is_cancelled = False
    
    async def create_session(self):
        """創建aiohttp會話"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close_session(self):
        """關閉aiohttp會話"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def cancel(self):
        """取消當前請求"""
        self.is_cancelled = True
    
    async def send_message(self, messages, model, temperature=0.5):
        """發送消息到API
        
        Args:
            messages: 消息歷史列表
            model: 模型ID
            temperature: 溫度參數
            
        Returns:
            元組 (成功標誌, 回應內容, 錯誤消息)
        """
        self.is_cancelled = False
        full_response = ""
        
        # 獲取並驗證API令牌
        api_token = get_api_token()
        if not validate_api_token(api_token):
            if self.on_error:
                self.on_error("API令牌無效，請檢查配置。")
            return False, "", "API令牌錯誤"
        
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        body = {
            "model": model,
            "messages": messages,
            "stream": True,
            "max_tokens": 10000,
            "temperature": temperature
        }
        
        try:
            session = await self.create_session()
            
            async with session.post(
                API_CONFIG["api_url"],
                headers=headers,
                json=body,
                timeout=60
            ) as response:
                if response.status != 200:
                    # 處理非200響應
                    error_text = await response.text()
                    try:
                        error_json = json.loads(error_text)
                        error_message = error_json.get("error", {}).get("message", f"請求失敗: 狀態碼 {response.status}")
                    except:
                        error_message = f"請求失敗: 狀態碼 {response.status}"
                    
                    if self.on_error:
                        self.on_error(error_message)
                    return False, "", f"API錯誤: {response.status}"
                
                # 處理流式響應
                try:
                    async for line in response.content:
                        # 檢查是否取消
                        if self.is_cancelled:
                            break
                        
                        line = line.decode("utf-8").strip()
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            
                            try:
                                data_json = json.loads(data)
                                content = data_json.get("choices", [{}])[0].get("delta", {}).get("content")
                                if content:
                                    full_response += content
                                    if self.on_message:
                                        self.on_message(content)
                            except Exception as e:
                                if not self.is_cancelled and self.on_error:
                                    self.on_error(f"解析響應時出錯: {e}")
                except asyncio.CancelledError:
                    self.is_cancelled = True
                except asyncio.TimeoutError:
                    if not self.is_cancelled and self.on_error:
                        self.on_error("請求超時，請稍後再試。")
                    return False, full_response, "請求超時"
                except Exception as e:
                    if not self.is_cancelled and self.on_error:
                        self.on_error(f"讀取回應時發生錯誤: {e}")
                    return False, full_response, f"讀取錯誤: {str(e)[:50]}"
        
        except asyncio.CancelledError:
            self.is_cancelled = True
        except aiohttp.ClientConnectorError:
            if not self.is_cancelled and self.on_error:
                self.on_error("無法連接到API伺服器，請檢查網絡連接。")
            return False, full_response, "網絡連接錯誤"
        except Exception as e:
            if not self.is_cancelled and self.on_error:
                self.on_error(f"連接錯誤: {e}")
            return False, full_response, f"錯誤: {str(e)[:50]}"
        
        # 調用完成回調
        if self.on_done and not self.is_cancelled:
            self.on_done()
            
        return True, full_response, "就緒" if not self.is_cancelled else "回應已取消" 
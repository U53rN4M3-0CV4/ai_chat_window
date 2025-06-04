import datetime
import threading
import asyncio
import concurrent.futures
from api_client import ApiClient
from ui_utils import get_time_str, set_text_readonly_but_selectable
import tkinter as tk

class ChatManager:
    def __init__(self, update_status_callback=None):
        """初始化聊天管理器
        
        Args:
            update_status_callback: 更新狀態欄的回調函數
        """
        self.chat_history = []
        self.is_sending = False
        self.task_cancelled = False
        self.current_task = None
        self.update_status = update_status_callback
        
        # 創建API客戶端
        self.api_client = None
    
    def get_history(self):
        """獲取聊天歷史"""
        return self.chat_history
    
    def clear_history(self):
        """清除聊天歷史"""
        self.chat_history = []
    
    def _on_message_received(self, content, chat_display):
        """收到消息時的處理函數"""
        chat_display.config(state=tk.NORMAL)
        chat_display.insert(tk.END, content, "assistant")
        chat_display.see(tk.END)
        set_text_readonly_but_selectable(chat_display)
    
    def _on_error_received(self, error_message, chat_display):
        """收到錯誤時的處理函數"""
        chat_display.config(state=tk.NORMAL)
        chat_display.insert(tk.END, f"\n{error_message}\n", "error")
        chat_display.see(tk.END)
        set_text_readonly_but_selectable(chat_display)
        
        if self.update_status:
            self.update_status(f"錯誤: {error_message[:50]}")
    
    def _on_request_done(self):
        """請求完成時的處理函數"""
        if self.update_status and not self.task_cancelled:
            self.update_status("就緒")
    
    async def _send_message_async(self, user_input, chat_display, model_id, temperature, 
                                user_input_entry, send_btn, clear_btn, stop_btn):
        """異步發送消息
        
        Args:
            user_input: 用戶輸入的消息
            chat_display: 聊天顯示區域
            model_id: 模型ID
            temperature: 溫度值
            user_input_entry, send_btn, clear_btn, stop_btn: UI元素
        """
        # 設置發送狀態
        self.is_sending = True
        self.task_cancelled = False
        
        # 存儲UI元素引用，以便停止時使用
        self.current_ui_elements = {
            'user_input_entry': user_input_entry,
            'send_btn': send_btn,
            'clear_btn': clear_btn,
            'stop_btn': stop_btn
        }
        
        # 禁用UI元素
        user_input_entry.config(state=tk.DISABLED)
        send_btn.config(state=tk.DISABLED)
        clear_btn.config(state=tk.DISABLED)
        stop_btn.config(state=tk.NORMAL)
        
        try:
            # 獲取當前時間
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 添加用戶消息到聊天歷史
            self.chat_history.append({"role": "user", "content": user_input, "timestamp": current_time})
            
            # 在UI中顯示用戶消息
            time_str = get_time_str()
            chat_display.config(state=tk.NORMAL)
            chat_display.insert(tk.END, f"[{time_str}] ", "time")
            chat_display.insert(tk.END, f"您:\n", "user_header")
            chat_display.insert(tk.END, f"{user_input}\n\n", "user")
            chat_display.see(tk.END)
            set_text_readonly_but_selectable(chat_display)
            
            # 創建API客戶端並設置回調
            self.api_client = ApiClient(
                on_message_callback=lambda content: self._on_message_received(content, chat_display),
                on_error_callback=lambda error: self._on_error_received(error, chat_display),
                on_done_callback=self._on_request_done
            )
            
            # 顯示AI回應的開始
            time_str = get_time_str()
            response_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            chat_display.config(state=tk.NORMAL)
            chat_display.insert(tk.END, f"[{time_str}] ", "time")
            chat_display.insert(tk.END, f"{model_id.split('/')[-1]}:\n", "assistant_header")
            chat_display.see(tk.END)
            set_text_readonly_but_selectable(chat_display)
            
            # 更新狀態欄
            if self.update_status:
                model_name = model_id.split('/')[-1]
                self.update_status(f"正在使用 {model_name} 處理請求，溫度: {temperature:.2f}")
            
            # 發送消息
            success, full_response, status = await self.api_client.send_message(
                self.chat_history, model_id, temperature
            )
            
            # 添加換行
            if not self.task_cancelled:
                chat_display.config(state=tk.NORMAL)
                chat_display.insert(tk.END, "\n\n")
                chat_display.see(tk.END)
                set_text_readonly_but_selectable(chat_display)
            
            # 更新聊天歷史
            if full_response:
                # 如果被取消，標記為截斷
                suffix = " [回應被截斷]" if self.task_cancelled else ""
                self.chat_history.append({
                    "role": "assistant", 
                    "content": full_response + suffix, 
                    "timestamp": response_time,
                    "model": model_id
                })
            
            # 如果取消了，顯示取消提示
            if self.task_cancelled:
                chat_display.config(state=tk.NORMAL)
                chat_display.insert(tk.END, "[回應已取消]\n\n", "system")
                chat_display.see(tk.END)
                set_text_readonly_but_selectable(chat_display)
            
            # 更新狀態欄
            if self.update_status:
                self.update_status(status)
                
        finally:
            # 關閉API客戶端會話
            if self.api_client:
                await self.api_client.close_session()
            
            # 恢復UI元素狀態
            user_input_entry.config(state=tk.NORMAL)
            send_btn.config(state=tk.NORMAL)
            clear_btn.config(state=tk.NORMAL)
            stop_btn.config(state=tk.DISABLED)
            
            # 讓輸入框重新獲得焦點
            user_input_entry.focus_set()
            
            # 重置狀態
            self.is_sending = False
            self.current_task = None
            self.current_ui_elements = None
    
    def send_message(self, user_input, chat_display, model_id, temperature,
                     user_input_entry, send_btn, clear_btn, stop_btn, model_name=""):
        """發送消息（主線程調用）
        
        Args:
            user_input: 用戶輸入的消息
            chat_display: 聊天顯示區域
            model_id: 模型ID
            temperature: 溫度值
            user_input_entry, send_btn, clear_btn, stop_btn: UI元素
            model_name: 模型名稱，用於顯示
        """
        # 檢查是否已經在發送中
        if self.is_sending:
            return
            
        # 創建一個函數來運行異步任務
        def run_async_task():
            # 獲取事件循環
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 創建任務
            task = loop.create_task(self._send_message_async(
                user_input, chat_display, model_id, temperature,
                user_input_entry, send_btn, clear_btn, stop_btn
            ))
            self.current_task = task
            
            try:
                # 運行任務直到完成
                loop.run_until_complete(task)
            except concurrent.futures.CancelledError:
                pass
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"任務異常: {e}")
                if self.update_status:
                    self.update_status(f"發生錯誤: {e}")
            finally:
                # 清理
                loop.close()
        
        # 在新線程中運行
        threading.Thread(target=run_async_task).start()
    
    def stop_response(self):
        """停止當前響應"""
        self.task_cancelled = True
        
        # 如果有API客戶端，取消它
        if self.api_client:
            self.api_client.cancel()
        
        # 如果有當前任務，嘗試取消它
        if self.current_task:
            try:
                self.current_task.cancel()
            except:
                pass
        
        # 立即恢復UI元素狀態（使用存儲的UI元素引用）
        if hasattr(self, 'current_ui_elements') and self.current_ui_elements:
            ui_elements = self.current_ui_elements
            
            if ui_elements.get('user_input_entry'):
                ui_elements['user_input_entry'].config(state=tk.NORMAL)
            if ui_elements.get('send_btn'):
                ui_elements['send_btn'].config(state=tk.NORMAL)
            if ui_elements.get('clear_btn'):
                ui_elements['clear_btn'].config(state=tk.NORMAL)
            if ui_elements.get('stop_btn'):
                ui_elements['stop_btn'].config(state=tk.DISABLED)
            
            # 讓輸入框重新獲得焦點
            if ui_elements.get('user_input_entry'):
                ui_elements['user_input_entry'].focus_set()
        
        # 更新狀態欄
        if self.update_status:
            self.update_status("回應已取消")
        
        # 重置發送狀態
        self.is_sending = False
        
        # 清理UI元素引用
        self.current_ui_elements = None 
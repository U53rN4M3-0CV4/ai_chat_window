import tkinter as tk
import datetime
from config import DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZES

def get_time_str():
    """獲取當前時間格式化字符串"""
    now = datetime.datetime.now()
    return now.strftime("%H:%M:%S")

def set_text_readonly_but_selectable(text_widget):
    """設置文字框為唯讀但可選取的模式"""
    # 啟用文字框以允許配置標籤和選取功能
    text_widget.config(state=tk.NORMAL)
    
    # 解除所有可能影響選取的綁定
    for binding in ["<Button-1>", "<B1-Motion>", "<ButtonRelease-1>", "<Double-Button-1>", "<Triple-Button-1>"]:
        try:
            text_widget.unbind(binding)
        except:
            pass
    
    # 重新綁定快捷鍵功能，使複製功能正常工作
    text_widget.bind("<Control-c>", lambda e: None)  # 允許複製
    text_widget.bind("<Control-a>", lambda e: text_widget.tag_add("sel", "1.0", "end-1c"))  # 全選功能
    
    # 綁定事件以禁止修改操作但允許選取
    text_widget.bind("<Key>", lambda e: "break" if e.keysym not in ("c", "C", "Up", "Down", "Left", "Right", "Home", "End", "Prior", "Next") else None)
    
    # 設置一個自訂屬性以追蹤當前狀態
    text_widget.readonly_selectable = True
    
    # 確保文字框可以獲得焦點，這樣鍵盤操作才能生效
    text_widget.config(takefocus=1)

def create_custom_dialog(parent, title, message, width=300, height=120, 
                         buttons=None, default_button=None):
    """創建自訂對話框
    
    Args:
        parent: 父視窗
        title: 對話框標題
        message: 顯示消息
        width: 寬度
        height: 高度
        buttons: 按鈕列表，格式為[(text, command), ...]
        default_button: 設置焦點的按鈕索引
        
    Returns:
        對話框實例
    """
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.geometry(f"{width}x{height}")
    dialog.resizable(False, False)
    
    # 模態對話框設置
    dialog.transient(parent)
    dialog.grab_set()
    
    # 更新等待視窗完成繪製
    dialog.update_idletasks()
    
    # 計算位置使對話框在父視窗中央
    x = parent.winfo_x() + (parent.winfo_width() // 2) - (dialog.winfo_width() // 2)
    y = parent.winfo_y() + (parent.winfo_height() // 2) - (dialog.winfo_height() // 2)
    
    dialog.geometry(f"+{x}+{y}")
    
    # 添加消息標籤
    message_label = tk.Label(
        dialog,
        text=message,
        font=(DEFAULT_FONT_FAMILY, 10),
        pady=10,
        wraplength=width-20  # 文字自動換行
    )
    message_label.pack(pady=10)
    
    # 添加按鈕
    if buttons:
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        button_list = []
        for i, (text, command) in enumerate(buttons):
            # 創建封裝命令的函數，捕獲當前dialog和原始命令
            def create_command(cmd, dlg):
                if cmd.__code__.co_argcount > 0:
                    return lambda: cmd(dlg)
                else:
                    return lambda: cmd()
            
            btn = tk.Button(
                button_frame,
                text=text,
                command=create_command(command, dialog),
                width=8,
                font=(DEFAULT_FONT_FAMILY, 9)
            )
            btn.pack(side=tk.LEFT, padx=5)
            button_list.append(btn)
        
        # 設置默認按鈕焦點
        if default_button is not None and 0 <= default_button < len(button_list):
            button_list[default_button].focus_set()
    
    return dialog

def create_context_menu(text_widget, root):
    """為文字框創建右鍵選單
    
    Args:
        text_widget: 文字框
        root: 根視窗，用於剪貼板操作
    """
    context_menu = tk.Menu(text_widget, tearoff=0)
    
    # 定義複製選取文字的函數
    def copy_selected_text():
        try:
            selected_text = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            root.clipboard_clear()
            root.clipboard_append(selected_text)
        except tk.TclError:
            pass  # 無選取文字
    
    # 定義全選文字的函數
    def select_all_text():
        text_widget.tag_add(tk.SEL, "1.0", tk.END)
        return 'break'
    
    context_menu.add_command(label="複製", command=copy_selected_text)
    context_menu.add_command(label="全選", command=select_all_text)
    
    # 綁定右鍵彈出選單
    def show_context_menu(event):
        context_menu.post(event.x_root, event.y_root)
        return 'break'
    
    text_widget.bind("<Button-3>", show_context_menu)
    
    return context_menu

def validate_decimal(action, value_if_allowed):
    """驗證小數輸入
    
    Args:
        action: 動作類型
        value_if_allowed: 修改後的值
        
    Returns:
        是否允許修改
    """
    # 排除空值
    if value_if_allowed == "":
        return True
    # 檢查是否為有效的數字格式（包括小數）
    try:
        # 檢查是否超過一位小數 
        if '.' in value_if_allowed:
            parts = value_if_allowed.split('.')
            if len(parts) > 2 or len(parts[1]) > 1:
                return False
        float(value_if_allowed)
        return True
    except ValueError:
        return False 
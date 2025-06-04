import tkinter as tk
from tkinter import scrolledtext, ttk, filedialog
import datetime
import tkinter.messagebox as messagebox

from config import (APP_VERSION, DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZES, 
                  FONT_SCALE_MIN, FONT_SCALE_MAX, LAST_VALID_CUSTOM_SCALE,
                  MODELS, UI_COLORS, setup_warnings)
from chat_manager import ChatManager
from ui_utils import (get_time_str, set_text_readonly_but_selectable, 
                    create_custom_dialog, create_context_menu,
                    validate_decimal)

# 初始化全局變量
selected_model = None
temperature_value = None
font_scale_value = None
status_bar = None
chat_manager = None

def update_status(message):
    """更新狀態欄消息"""
    global status_bar
    if status_bar:
        status_bar.config(text=message)

def clear_history_handler(chat_display):
    """處理清除歷史的操作"""
    global chat_manager
    
    # 定義確認清除的回調
    def confirm_clear(dialog=None):
        global chat_manager
        chat_manager.clear_history()
        
        # 清除聊天顯示
        chat_display.config(state=tk.NORMAL)
        chat_display.delete(1.0, tk.END)
        chat_display.insert(tk.END, "聊天歷史已清除\n\n", "system")
        set_text_readonly_but_selectable(chat_display)
        
        # 關閉對話框
        if dialog:
            dialog.destroy()
        
        # 更新狀態欄
        update_status("聊天歷史已清除")
    
    # 定義關閉對話框的函數
    def close_dialog(dialog=None):
        if dialog:
            dialog.destroy()
    
    # 創建確認對話框
    buttons = [
        ("確認", confirm_clear),
        ("取消", close_dialog)
    ]
    
    dialog = create_custom_dialog(
        chat_display.master,
        "確認",
        "確定要清除聊天歷史嗎？\n這個操作無法撤銷。",
        buttons=buttons,
        default_button=1  # 默認選擇取消
    )

def update_font_size():
    """更新界面所有元素的字體大小"""
    global LAST_VALID_CUSTOM_SCALE, font_scale_value
    global chat_display, user_input_entry, send_btn, stop_btn, clear_btn, export_btn
    global model_label, temp_label, temp_value_label, temp_desc
    global font_size_label, font_size_radios, custom_size_entry, custom_size_label
    global title_label, version_label, status_bar
    
    # 獲取當前選擇的比例
    scale = font_scale_value.get()
    
    # 如果是自訂值，則從輸入框獲取
    if scale == -1:
        try:
            scale = float(custom_size_var.get())
            # 四捨五入到小數點後一位
            scale = round(scale * 10) / 10
            if scale < FONT_SCALE_MIN:
                scale = FONT_SCALE_MIN
                custom_size_var.set(f"{FONT_SCALE_MIN:.1f}")
            elif scale > FONT_SCALE_MAX:
                scale = FONT_SCALE_MAX
                custom_size_var.set(f"{FONT_SCALE_MAX:.1f}")
            else:
                custom_size_var.set(f"{scale:.1f}")
                
            # 更新最後一次有效值
            LAST_VALID_CUSTOM_SCALE = custom_size_var.get()
        except ValueError:
            # 如果輸入無效，使用最後一次有效的縮放值
            custom_size_var.set(LAST_VALID_CUSTOM_SCALE)
            scale = float(LAST_VALID_CUSTOM_SCALE)
    
    # 計算各元素的字體大小
    main_size = round(DEFAULT_FONT_SIZES["main"] * scale)
    title_size = round(DEFAULT_FONT_SIZES["title"] * scale)
    subtitle_size = round(DEFAULT_FONT_SIZES["subtitle"] * scale)
    input_size = round(DEFAULT_FONT_SIZES["input"] * scale)
    time_size = round(DEFAULT_FONT_SIZES["time"] * scale)
    status_size = round(DEFAULT_FONT_SIZES["status"] * scale)
    button_size = round(DEFAULT_FONT_SIZES["button"] * scale)
    description_size = round(DEFAULT_FONT_SIZES["description"] * scale)
    
    # 更新所有界面元素的字體大小
    if 'chat_display' in globals() and chat_display:
        chat_display.config(font=(DEFAULT_FONT_FAMILY, main_size))
        chat_display.tag_configure("time", font=(DEFAULT_FONT_FAMILY, time_size))
        chat_display.tag_configure("user_header", font=(DEFAULT_FONT_FAMILY, main_size, "bold"))
        chat_display.tag_configure("assistant_header", font=(DEFAULT_FONT_FAMILY, main_size, "bold"))
        chat_display.tag_configure("system", font=(DEFAULT_FONT_FAMILY, status_size, "italic"))
    
    # 更新輸入框和按鈕
    if 'user_input_entry' in globals() and user_input_entry:
        user_input_entry.config(font=(DEFAULT_FONT_FAMILY, input_size))
    
    # 更新其他UI元素的字體大小 (如果它們存在)
    for elem_name in ['send_btn', 'stop_btn', 'clear_btn', 'export_btn',
                     'model_label', 'temp_label', 'temp_value_label', 'temp_desc',
                     'font_size_label', 'title_label', 'version_label', 'status_bar']:
        if elem_name in globals() and globals()[elem_name]:
            if 'btn' in elem_name:
                globals()[elem_name].config(font=(DEFAULT_FONT_FAMILY, button_size, "bold"))
            elif elem_name == 'title_label':
                globals()[elem_name].config(font=(DEFAULT_FONT_FAMILY, title_size, "bold"))
            elif elem_name == 'version_label':
                globals()[elem_name].config(font=(DEFAULT_FONT_FAMILY, subtitle_size))
            elif elem_name == 'status_bar':
                globals()[elem_name].config(font=(DEFAULT_FONT_FAMILY, status_size))
            elif elem_name == 'temp_desc':
                globals()[elem_name].config(font=(DEFAULT_FONT_FAMILY, description_size))
            else:
                globals()[elem_name].config(font=(DEFAULT_FONT_FAMILY, main_size))
    
    # 更新字體大小單選按鈕字體
    if 'font_size_radios' in globals() and font_size_radios:
        for radio_btn in font_size_radios:
            radio_btn.config(font=(DEFAULT_FONT_FAMILY, main_size))
    
    # 更新自訂大小輸入框
    if 'custom_size_entry' in globals() and custom_size_entry:
        custom_size_entry.config(font=(DEFAULT_FONT_FAMILY, main_size))
    if 'custom_size_label' in globals() and custom_size_label:
        custom_size_label.config(font=(DEFAULT_FONT_FAMILY, main_size))
    
    # 更新Radiobutton風格
    style = ttk.Style()
    style.configure("TRadiobutton", font=(DEFAULT_FONT_FAMILY, main_size))

def export_history(chat_display):
    """導出聊天歷史到文本文件"""
    global chat_manager
    
    # 定義關閉對話框的函數
    def close_dialog(dialog):
        dialog.destroy()
    
    # 獲取聊天歷史
    chat_history = chat_manager.get_history()
    
    if not chat_history:
        # 創建提示對話框
        create_custom_dialog(
            chat_display.master,
            "提示",
            "當前沒有聊天歷史可供導出",
            width=300,
            height=100,
            buttons=[("確定", close_dialog)],
            default_button=0
        )
        return
    
    # 建立默認檔名（含日期時間）
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    default_filename = f"聊天記錄_{current_time}.txt"
    
    # 打開文件保存對話框
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
        initialfile=default_filename
    )
    
    if not file_path:  # 用戶取消了保存
        return
    
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            # 寫入標題
            file.write(f"===== AI 聊天助手對話記錄 =====\n")
            file.write(f"導出時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 寫入對話內容
            for msg in chat_history:
                if msg["role"] == "user":
                    role = "您"
                else:
                    # 使用模型名稱，若無則默認為「AI」
                    role = msg.get("model", "AI").split('/')[-1]
                
                # 使用消息中的時間戳
                timestamp = msg.get("timestamp", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                file.write(f"[{timestamp}] {role}: {msg['content']}\n\n")
        
        # 更新狀態
        update_status(f"聊天記錄已保存到: {file_path}")
        
        # 創建成功對話框
        create_custom_dialog(
            chat_display.master,
            "成功",
            f"聊天記錄已保存到:\n{file_path}",
            width=350,
            height=120,
            buttons=[("確定", close_dialog)],
            default_button=0
        )
        
    except Exception as e:
        # 顯示錯誤
        update_status(f"保存失敗: {e}")
        
        # 創建錯誤對話框
        create_custom_dialog(
            chat_display.master,
            "錯誤",
            f"保存失敗: {e}",
            width=350,
            height=120,
            buttons=[("確定", close_dialog)],
            default_button=0
        )

def send_message_handler(user_input_entry, chat_display, send_btn, clear_btn, stop_btn):
    """處理發送消息的操作"""
    global chat_manager, selected_model, temperature_value
    
    # 獲取用戶輸入
    user_input = user_input_entry.get("1.0", "end-1c")
    placeholder_text = "歡迎使用AI聊天助手！請輸入您的問題。(按Enter發送，Shift+Enter換行)"
    
    # 檢查輸入是否為空或是placeholder
    if not user_input.strip() or user_input == placeholder_text:
        return
    
    # 清除輸入框
    user_input_entry.delete("1.0", tk.END)
    
    # 處理特殊命令
    if user_input.lower() == 'clear':
        clear_history_handler(chat_display)
    else:
        # 獲取當前選擇的模型ID和名稱
        model_name = selected_model.get()
        model_id = MODELS.get(model_name, MODELS["DeepSeek V3-0324"])
        
        # 獲取溫度值
        temp = temperature_value.get()
        
        # 發送消息
        chat_manager.send_message(
            user_input, chat_display, model_id, temp,
            user_input_entry, send_btn, clear_btn, stop_btn,
            model_name
        )

def create_gui():
    global selected_model, status_bar, temperature_value, font_scale_value
    global chat_display, user_input_entry, send_btn, stop_btn, clear_btn, export_btn
    global model_label, temp_label, temp_value_label, temp_desc
    global font_size_label, font_size_radios, custom_size_entry, custom_size_label
    global title_label, version_label, chat_manager, custom_size_var
    
    # 建立根視窗
    root = tk.Tk()
    root.title(f"AI 聊天助手 v{APP_VERSION}")
    root.geometry("770x810")
    root.minsize(540, 740)
    
    # 配置視窗自適應大小
    root.grid_rowconfigure(0, weight=0)  # 標題區域不需要擴展
    root.grid_rowconfigure(1, weight=1)  # 聊天顯示區域需要擴展
    root.grid_rowconfigure(2, weight=0)  # 控制區域不需要擴展
    root.grid_columnconfigure(0, weight=1)  # 所有列都可以水平擴展
    
    # 初始化變量
    selected_model = tk.StringVar(root)
    selected_model.set("DeepSeek V3-0324")  # 默認選擇模型
    temperature_value = tk.DoubleVar(root)
    temperature_value.set(0.5)  # 默認溫度值
    font_scale_value = tk.DoubleVar(root)  # 字體縮放比例變量
    font_scale_value.set(0.8)  # 默認比例為0.8（小型）
    
    # 創建聊天管理器
    chat_manager = ChatManager(update_status_callback=update_status)
    
    # 設置主題色彩
    bg_color = UI_COLORS["bg_color"]
    text_bg = UI_COLORS["text_bg"]
    
    root.configure(bg=bg_color)
    
    # RadioButton 風格設置
    style = ttk.Style()
    style.configure("TRadiobutton", background=bg_color, font=(DEFAULT_FONT_FAMILY, 10))
    
    # 創建上方標題區域
    header_frame = tk.Frame(root, bg=UI_COLORS["header_bg"], pady=10)
    header_frame.grid(row=0, column=0, sticky="ew")
    
    # 創建子框架用於水平排列標題和版本號
    title_frame = tk.Frame(header_frame, bg=UI_COLORS["header_bg"])
    title_frame.pack()
    
    title_label = tk.Label(
        title_frame,
        text="AI 聊天助手",
        font=(DEFAULT_FONT_FAMILY, 16, "bold"),
        fg=UI_COLORS["header_fg"],
        bg=UI_COLORS["header_bg"]
    )
    title_label.pack(side=tk.LEFT)
    
    version_label = tk.Label(
        title_frame,
        text=f"v{APP_VERSION}",
        font=(DEFAULT_FONT_FAMILY, 8),
        fg=UI_COLORS["header_subtitle_fg"],
        bg=UI_COLORS["header_bg"],
        padx=5,
        pady=8
    )
    version_label.pack(side=tk.LEFT)
    
    # 創建聊天顯示區域
    chat_frame = tk.Frame(root, bg=bg_color)
    chat_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
    
    chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, bg=text_bg, font=(DEFAULT_FONT_FAMILY, 10))
    chat_display.pack(fill=tk.BOTH, expand=True)
    
    # 創建右鍵菜單
    create_context_menu(chat_display, root)
    
    # 啟用文字選取功能
    chat_display.config(cursor="ibeam")
    chat_display.bind("<B1-Motion>", lambda e: "break" if False else None)
    chat_display.bind("<ButtonRelease-1>", lambda e: "break" if False else None)
    set_text_readonly_but_selectable(chat_display)
    
    # 設置標籤
    chat_display.tag_configure("time", foreground="#808080", font=(DEFAULT_FONT_FAMILY, 8))
    chat_display.tag_configure("user_header", foreground="#007BFF", font=(DEFAULT_FONT_FAMILY, 10, "bold"))
    chat_display.tag_configure("user", foreground="#000000")
    chat_display.tag_configure("assistant_header", foreground="#28a745", font=(DEFAULT_FONT_FAMILY, 10, "bold"))
    chat_display.tag_configure("assistant", foreground="#000000")
    chat_display.tag_configure("system", foreground="#6c757d", font=(DEFAULT_FONT_FAMILY, 9, "italic"))
    chat_display.tag_configure("error", foreground="#dc3545")
    
    # 創建模型選擇區域
    model_frame = tk.Frame(root, bg=bg_color, padx=15, pady=0)
    model_frame.grid(row=2, column=0, sticky="ew", padx=15)
    
    # 模型選擇區域的頂部部分
    model_top_frame = tk.Frame(model_frame, bg=bg_color)
    model_top_frame.pack(fill=tk.X, pady=(0, 0))
    
    model_label = tk.Label(model_top_frame, text="選擇模型:", bg=bg_color, font=(DEFAULT_FONT_FAMILY, 10, "bold"))
    model_label.pack(side=tk.LEFT, padx=(0, 0))
    
    # 添加溫度控制區域（在模型選擇右側）
    temp_frame = tk.Frame(model_top_frame, bg=bg_color)
    temp_frame.pack(side=tk.RIGHT)
    
    temp_label = tk.Label(
        temp_frame,
        text="溫度:",
        bg=bg_color,
        font=(DEFAULT_FONT_FAMILY, 10),
        padx=10
    )
    temp_label.pack(side=tk.LEFT, padx=(0, 5))
    
    # 創建一個StringVar來顯示溫度值
    temp_text = tk.StringVar()
    temp_text.set(f"{temperature_value.get():.1f}")
    
    temp_value_label = tk.Label(
        temp_frame,
        textvariable=temp_text,
        width=3,
        bg=bg_color,
        font=(DEFAULT_FONT_FAMILY, 10, "bold")
    )
    temp_value_label.pack(side=tk.LEFT)
    
    # 更新溫度顯示的函數
    def update_temp_display(val):
        temp = float(val)
        temp_text.set(f"{temp:.1f}")
    
    # 溫度滑塊
    temp_slider = ttk.Scale(
        temp_frame,
        from_=0.0,
        to=1.0,
        orient=tk.HORIZONTAL,
        length=100,
        variable=temperature_value,
        command=update_temp_display
    )
    temp_slider.pack(side=tk.LEFT)
    
    # 創建兩行模型選擇區
    row1_frame = tk.Frame(model_frame, bg=bg_color)
    row1_frame.pack(fill=tk.X, pady=(0, 5))
    
    row2_frame = tk.Frame(model_frame, bg=bg_color)
    row2_frame.pack(fill=tk.X, pady=(0, 5))
    
    # 將模型分為兩行顯示
    model_names = list(MODELS.keys())
    first_row = model_names[:3]
    second_row = model_names[3:]
    
    # 創建第一行的單選按鈕
    for model_name in first_row:
        rb = ttk.Radiobutton(
            row1_frame,
            text=model_name,
            variable=selected_model,
            value=model_name,
            style="TRadiobutton"
        )
        rb.pack(side=tk.LEFT, padx=(10, 0))
    
    # 創建第二行的單選按鈕
    for model_name in second_row:
        rb = ttk.Radiobutton(
            row2_frame,
            text=model_name,
            variable=selected_model,
            value=model_name,
            style="TRadiobutton"
        )
        rb.pack(side=tk.LEFT, padx=(10, 0))
    
    # 添加溫度說明
    temp_desc_frame = tk.Frame(model_frame, bg=bg_color)
    temp_desc_frame.pack(fill=tk.X)
    
    temp_desc = tk.Label(
        temp_desc_frame,
        text="溫度說明: 較低 = 更精確/一致的回應，較高 = 更有創意/多樣的回應",
        fg="#555555",
        bg=bg_color,
        font=(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZES["description"]),
        anchor=tk.W
    )
    temp_desc.pack(side=tk.LEFT, pady=(0, 2))
    
    # 添加字體大小控制區域
    font_size_frame = tk.Frame(model_frame, bg=bg_color)
    font_size_frame.pack(fill=tk.X, pady=(5, 0))
    
    font_size_label = tk.Label(
        font_size_frame,
        text="字體大小:",
        bg=bg_color,
        font=(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZES["main"]),
        padx=5
    )
    font_size_label.pack(side=tk.LEFT)
    
    # 創建字體大小選擇單選按鈕
    font_size_radios = []
    font_sizes = [
        ("小型", 0.8),
        ("中型", 1.0),
        ("大型", 1.5),
        ("特大", 3.0),
        ("自訂", -1)  # 特殊值表示自訂
    ]
    
    # 創建單選按鈕框架
    font_size_radio_frame = tk.Frame(font_size_frame, bg=bg_color)
    font_size_radio_frame.pack(side=tk.LEFT, padx=(0, 10))
    
    # 創建單選按鈕
    for i, (text, value) in enumerate(font_sizes):
        rb = tk.Radiobutton(
            font_size_radio_frame,
            text=text,
            variable=font_scale_value,
            value=value,
            bg=bg_color,
            font=(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZES["main"])
        )
        rb.pack(side=tk.LEFT, padx=(0, 5))
        font_size_radios.append(rb)
    
    # 創建自訂字體大小輸入框
    custom_size_frame = tk.Frame(font_size_frame, bg=bg_color)
    custom_size_frame.pack(side=tk.LEFT, padx=(0, 0))
    
    custom_size_var = tk.StringVar(value="1.0")
    
    # 註冊驗證器
    vcmd = (custom_size_frame.register(validate_decimal), '%d', '%P')
    
    custom_size_entry = tk.Entry(
        custom_size_frame, 
        textvariable=custom_size_var, 
        width=4, 
        font=(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZES["main"]),
        validate="key", 
        validatecommand=vcmd
    )
    custom_size_entry.pack(side=tk.LEFT)
    
    # 標籤顯示"x"
    custom_size_label = tk.Label(custom_size_frame, text="倍", bg=bg_color, font=(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZES["main"]))
    custom_size_label.pack(side=tk.LEFT, padx=(2, 0))
    
    # 選擇默認字體大小為"小型"
    font_scale_value.set(0.8)
    # 初始設置輸入框為禁用狀態
    custom_size_entry.config(state="disabled")
    
    # 應用自訂大小的函數
    def apply_custom_size(*args):
        global LAST_VALID_CUSTOM_SCALE
        # 只有當自訂選項被選中時才會套用變更
        if font_scale_value.get() == -1:
            try:
                # 嘗試轉換為浮點數，確認是有效值
                scale_value = float(custom_size_var.get())
                # 四捨五入到小數點後一位
                scale_value = round(scale_value * 10) / 10
                # 確認在允許範圍內
                if FONT_SCALE_MIN <= scale_value <= FONT_SCALE_MAX:
                    # 更新最後一次有效值，格式化為小數點後一位
                    LAST_VALID_CUSTOM_SCALE = f"{scale_value:.1f}"
                    # 更新顯示格式
                    custom_size_var.set(LAST_VALID_CUSTOM_SCALE)
                else:
                    # 超出範圍，截取到範圍內，並格式化
                    if scale_value < FONT_SCALE_MIN:
                        scale_value = FONT_SCALE_MIN
                    elif scale_value > FONT_SCALE_MAX:
                        scale_value = FONT_SCALE_MAX
                    custom_size_var.set(f"{scale_value:.1f}")
                    LAST_VALID_CUSTOM_SCALE = custom_size_var.get()
                update_font_size()
            except ValueError:
                # 如果輸入無效，恢復到上一次有效值
                custom_size_var.set(LAST_VALID_CUSTOM_SCALE)
                update_font_size()
    
    # 綁定回車鍵和失焦事件到自訂大小輸入框
    custom_size_entry.bind("<Return>", apply_custom_size)
    custom_size_entry.bind("<FocusOut>", apply_custom_size)
    
    # 當選擇改變時的回調函數
    def on_radio_change(*args):
        # 如果不是自訂，則禁用輸入框
        if font_scale_value.get() != -1:
            custom_size_entry.config(state="disabled")
        else:
            custom_size_entry.config(state="normal")
            custom_size_entry.focus_set()
        update_font_size()
    
    # 監聽字體大小選擇的變化
    font_scale_value.trace_add("write", on_radio_change)
    
    # 創建輸入和按鈕區域
    input_frame = tk.Frame(root, bg=bg_color)
    input_frame.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 10))
    
    # 輸入區域
    input_area = tk.Frame(input_frame, bg=bg_color)
    input_area.pack(fill=tk.X)
    
    # 創建輸入框並設置placeholder
    user_input_entry = tk.Text(input_area, 
                             font=(DEFAULT_FONT_FAMILY, 12),
                             width=30,
                             height=3,
                             wrap=tk.WORD,
                             padx=5, 
                             pady=5,
                             relief=tk.SUNKEN,
                             borderwidth=1)
    user_input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 5))
    
    # 為輸入框設置placeholder效果
    placeholder_text = "歡迎使用AI聊天助手！請輸入您的問題。(按Enter發送，Shift+Enter換行)"
    user_input_entry.insert("1.0", placeholder_text)
    user_input_entry.config(fg='grey')
    
    def on_entry_click(event):
        """當用戶點擊輸入框時，如果顯示的是placeholder，則清空內容"""
        if user_input_entry.get("1.0", "end-1c") == placeholder_text:
            user_input_entry.delete("1.0", tk.END)
            user_input_entry.config(fg='black')
    
    def on_focus_out(event):
        """當輸入框失去焦點時，如果為空，則顯示placeholder"""
        if user_input_entry.get("1.0", "end-1c") == '':
            user_input_entry.delete("1.0", tk.END)
            user_input_entry.insert("1.0", placeholder_text)
            user_input_entry.config(fg='grey')
    
    # 綁定事件
    user_input_entry.bind('<FocusIn>', on_entry_click)
    user_input_entry.bind('<FocusOut>', on_focus_out)
    
    # 設定按鍵綁定
    def handle_keypress(event):
        # 如果是純Enter鍵（不是Shift+Enter），觸發發送
        if event.keysym == "Return" and not event.state & 0x1:
            send_message_handler(user_input_entry, chat_display, send_btn, clear_btn, stop_btn)
            return "break"  # 防止默認行為（插入換行）
        # 如果是Shift+Enter，允許插入換行
        elif event.keysym == "Return" and event.state & 0x1:
            return None  # 允許默認行為（插入換行）
    
    user_input_entry.bind("<KeyPress>", handle_keypress)
    
    # 創建一個框架用於按鈕的2x2網格排列
    button_area = tk.Frame(input_area, bg=bg_color)
    button_area.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
    
    # 配置按鈕區域的網格
    button_area.columnconfigure(0, weight=1)
    button_area.columnconfigure(1, weight=1)
    button_area.rowconfigure(0, weight=1)
    button_area.rowconfigure(1, weight=1)
    
    # 美化按鈕設計
    button_style = {"font": (DEFAULT_FONT_FAMILY, 10, "bold"), "borderwidth": 1, "relief": tk.RAISED, "padx": 10, "pady": 2}
    
    send_btn = tk.Button(
        button_area,
        text="發送",
        bg=UI_COLORS["send_btn_color"],
        fg="white",
        **button_style
    )
    send_btn.grid(row=0, column=0, padx=2, pady=2, sticky="ew")
    
    clear_btn = tk.Button(
        button_area,
        text="清除歷史",
        bg=UI_COLORS["clear_btn_color"],
        fg="white",
        **button_style
    )
    clear_btn.grid(row=0, column=1, padx=2, pady=2, sticky="ew")
    
    stop_btn = tk.Button(
        button_area,
        text="停止",
        bg=UI_COLORS["stop_btn_color"],
        fg="white",
        state=tk.DISABLED,  # 初始狀態為禁用
        command=lambda: chat_manager.stop_response(),
        **button_style
    )
    stop_btn.grid(row=1, column=0, padx=2, pady=2, sticky="ew")
    
    export_btn = tk.Button(
        button_area,
        text="導出記錄",
        bg=UI_COLORS["export_btn_color"],
        fg="white",
        command=lambda: export_history(chat_display),
        **button_style
    )
    export_btn.grid(row=1, column=1, padx=2, pady=2, sticky="ew")
    
    # 添加狀態欄
    status_bar = tk.Label(
        root,
        text="就緒",
        fg=UI_COLORS["status_fg"],
        bg=UI_COLORS["status_bg"],
        anchor=tk.W,
        padx=10,
        relief=tk.SUNKEN,
        font=(DEFAULT_FONT_FAMILY, 9)
    )
    status_bar.grid(row=4, column=0, sticky="ew")
    
    # 設置按鈕命令
    send_btn.config(command=lambda: send_message_handler(user_input_entry, chat_display, send_btn, clear_btn, stop_btn))
    clear_btn.config(command=lambda: clear_history_handler(chat_display))
    
    # 點擊空白區域失焦功能
    def defocus_input(event):
        # 點擊空白區域時使輸入框失去焦點
        # 檢查點擊的是否為輸入框本身或聊天顯示區域
        if is_chat_display_or_child(event.widget):
            return
        
        # 如果不是輸入框或自訂字體大小輸入框，則將焦點移至根窗口
        if event.widget != user_input_entry and event.widget != custom_size_entry:
            root.focus_set()
    
    # 檢查小部件是否為chat_display或其子元素
    def is_chat_display_or_child(widget):
        if widget == chat_display:
            return True
        
        try:
            # 檢查是否為子元素
            parent = widget.master
            while parent:
                if parent == chat_display:
                    return True
                parent = parent.master
            return False
        except:
            return False
    
    # 為各個框架添加點擊事件來失焦（不包括聊天顯示區域）
    for frame in [header_frame, model_frame, model_top_frame, row1_frame, 
                 row2_frame, temp_desc_frame, font_size_frame, input_frame,
                 temp_frame, font_size_radio_frame]:
        frame.bind("<Button-1>", defocus_input)
    
    # 為根窗口添加點擊事件
    root.bind("<Button-1>", defocus_input)
    
    # 顯示歡迎信息
    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, f"歡迎使用 AI 聊天助手 (v{APP_VERSION})！\n", "system")
    chat_display.insert(tk.END, "請在下方輸入框中輸入您的問題。\n", "system")
    chat_display.insert(tk.END, "提示：您可以拖曳視窗邊緣來調整對話框大小。\n\n", "system")
    set_text_readonly_but_selectable(chat_display)
    
    # 聚焦輸入框
    user_input_entry.focus_set()
    
    # 確保字體大小設置正確應用
    font_scale_value.set(0.8)
    custom_size_entry.config(state="disabled")
    update_font_size()
    
    return root

def main():
    # 設置忽略警告
    setup_warnings()
    
    # 創建GUI
    root = create_gui()
    
    # 啟動主循環
    root.mainloop()

if __name__ == "__main__":
    main() 
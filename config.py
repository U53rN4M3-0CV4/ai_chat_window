import os
import sys
import warnings
import base64

# 應用程式版本
APP_VERSION = "1.2"

# 默認字體大小設置
DEFAULT_FONT_SIZES = {
    "main": 15,              # 主要文字大小
    "title": 24,             # 標題文字大小
    "subtitle": 12,          # 副標題文字大小
    "input": 18,             # 輸入框文字大小
    "time": 12,              # 時間標籤文字大小
    "status": 13.5,          # 狀態欄文字大小
    "button": 15,            # 按鈕文字大小
    "description": 12        # 描述文字大小
}

# 默認字體設置
DEFAULT_FONT_FAMILY = "Microsoft JhengHei"

# 字體縮放倍率範圍限制
FONT_SCALE_MIN = 0.1
FONT_SCALE_MAX = 3.0

# 最後一次有效的自訂縮放值
LAST_VALID_CUSTOM_SCALE = "1.0"

# 自訂的文字框狀態標誌
READONLY_BUT_SELECTABLE = "readonly_selectable"

# 支持的模型列表
MODELS = {
    "DeepSeek V3-0324": "deepseek-ai/DeepSeek-V3-0324",
    "DeepSeek R1": "deepseek-ai/DeepSeek-R1",
    "DeepSeek R1-0528": "deepseek-ai/DeepSeek-R1-0528",
    "DeepSeek Prover V2": "deepseek-ai/DeepSeek-Prover-V2-671B",
    "DeepSeek R1T Chimera": "tngtech/DeepSeek-R1T-Chimera",
    "Qwen3 235B": "Qwen/Qwen3-235B-A22B",
    "Llama-4 Maverick": "chutesai/Llama-4-Maverick-17B-128E-Instruct-FP8"
}

# API配置
API_CONFIG = {
    "api_url": "https://llm.chutes.ai/v1/chat/completions",
    # API令牌將從環境變數或設定檔讀取
    "api_token_env_var": "LLM_API_TOKEN",
}

# UI相關顏色配置
UI_COLORS = {
    "bg_color": "#f5f5f5",
    "text_bg": "#ffffff",
    "send_btn_color": "#4CAF50",
    "stop_btn_color": "#FF9800",
    "clear_btn_color": "#f44336",
    "export_btn_color": "#3498db",
    "header_bg": "#2c3e50",
    "header_fg": "white",
    "header_subtitle_fg": "#ecf0f1",
    "status_bg": "#e0e0e0",
    "status_fg": "#555555"
}

# 忽略警告設置
def setup_warnings():
    os.environ['TK_SILENCE_DEPRECATION'] = '1'  # 抑制macOS的tkinter棄用警告
    if sys.platform == 'win32':  # 僅在Windows上設置
        os.environ['PYTHONWARNINGS'] = 'ignore::Warning'
        warnings.filterwarnings("ignore", category=ResourceWarning)
        warnings.filterwarnings("ignore", message=".*[iI][cC][cC][pP].*")

# 獲取API令牌
def get_api_token():
    # 優先從環境變數獲取API令牌
    token = os.environ.get(API_CONFIG["api_token_env_var"])
    
    # 如果環境變數中沒有令牌，嘗試從config.local.py讀取
    if not token:
        try:
            from config_local import LOCAL_API_TOKEN
            token = LOCAL_API_TOKEN
        except ImportError:
            token = ""
    
    return token

# 驗證API令牌
def validate_api_token(token):
    return token and len(token) > 20 and token.startswith("cpk_") 
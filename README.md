# AI 聊天視窗應用

## 設置說明

### API 令牌配置
為了使用此應用程式，您需要配置 API 令牌。有兩種方法可以配置：

1. **使用環境變數（推薦）**
   - 設置環境變數 `LLM_API_TOKEN` 為您的 API 令牌值

   ```bash
   # Windows 命令提示符
   set LLM_API_TOKEN=your_api_token_here
   
   # Windows PowerShell
   $env:LLM_API_TOKEN = "your_api_token_here"
   
   # Linux/macOS
   export LLM_API_TOKEN=your_api_token_here
   ```

2. **使用本地配置文件**
   - 複製 `config_local.py.example` 為 `config_local.py`
   - 在 `config_local.py` 中設置您的 API 令牌
   ```python
   LOCAL_API_TOKEN = "your_api_token_here"
   ```

**注意：** 請勿將您的 API 令牌提交到版本控制系統中。
`config_local.py` 已經被添加到 `.gitignore` 中，確保它不會被不小心提交。 
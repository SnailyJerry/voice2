# MiniMax 文本转语音 (TTS) 工具

这是一个使用 MiniMax API 将文本转换为语音的 Python 工具，提供了一个简单的 Streamlit Web 界面和原始的命令行脚本。

## 功能

-   **多角色语音生成**：在 `voice.txt` 中配置多个声音角色。
-   **Web 界面**：通过 Streamlit 提供了一个用户友好的界面，可以输入文本并为所有已配置的角色生成语音。
-   **在线播放**：在 Web 界面上直接播放生成的音频文件。
-   **命令行支持**：保留了原始的命令行脚本，用于快速生成单个角色的语音。

## 设置指南

### 1. 安装依赖

在运行此工具之前，您需要安装必要的 Python 库。在您的终端中运行以下命令：

```bash
pip install streamlit requests
```

### 2. 检查角色配置

角色配置现在直接定义在 `app.py` 文件的 `ROLES_CONFIG` 变量中。如果您想添加、删除或修改角色，请直接编辑此文件。

## 运行指南

### 推荐：使用 Streamlit Web 应用

这是与此工具交互的首选方式。

1.  **启动应用**：在您的终端中，导航到项目目录，然后运行以下命令：

    ```bash
    streamlit run app.py
    ```

    如果上述命令不起作用（例如，提示 `command not found`），请尝试使用以下命令：

    ```bash
    python3 -m streamlit run app.py
    ```

2.  **输入凭证**：应用启动后，在浏览器页面的左侧边栏中，输入您的 MiniMax `Group ID` 和 `API Key`。

3.  **生成语音**：在主页面的文本框中输入文本，然后点击“生成语音”按钮即可。

## 部署指南

您可以将此应用部署到任何支持 Python 的托管平台。Streamlit Community Cloud 是一个很好的免费选择。

1.  **将您的项目推送到 GitHub**：确保您的 GitHub 仓库包含以下文件：
    -   `app.py`
    -   `requirements.txt`
2.  **在 Streamlit Community Cloud 上注册**：使用您的 GitHub 帐户登录。
3.  **部署应用**：点击 "New app"，选择您的 GitHub 仓库和 `app.py` 文件，然后点击 "Deploy!"。

## 文件说明

-   `app.py`：Streamlit Web 应用的源代码，包含所有逻辑和角色配置。
-   `requirements.txt`：项目所需的 Python 依赖项列表，用于部署。
-   `text_to_speech.py`：原始的命令行版本 TTS 脚本（已弃用）。
-   `voice.txt`：旧的配置文件（已弃用）。
-   `minimax_tts_api.md`：MiniMax TTS API 的官方文档备份。
-   `outputs/`：存放生成的 `.mp3` 音频文件的目录。

# -*- coding: utf-8 -*-

import json
import time
import requests
import streamlit as st
import os
import zipfile
import io

# 将角色配置直接定义在代码中
ROLES_CONFIG = [
    {
        "name": "小蜗牛宝宝",
        "voiceID": "moss_audio_bcba52f7-6b7d-11f0-91e6-02fdcf4c792f",
        "voice speed": "0.85",
        "model": "speech-02-hd"
    },
    {
        "name": "小猪宝宝",
        "voiceID": "moss_audio_69366bd0-729f-11f0-8f2e-c6962c94cb82",
        "voice speed": "0.99",
        "model": "speech-02-hd"
    },
    {
        "name": "小鳄鱼宝宝",
        "voiceID": "moss_audio_4b0cd404-6b7e-11f0-bf93-9a83873876d1",
        "voice speed": "0.96",
        "model": "speech-02-hd"
    }
]

def generate_speech(text_to_speak, role_config, group_id, api_key, emotion, base_filename=None):
    """
    调用 MiniMax API 将文本转换为语音并返回文件路径。
    """
    if not text_to_speak:
        st.warning("要转换的文本不能为空。")
        return None

    url = f"https://api.minimax.io/v1/t2a_v2?GroupId={group_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": role_config.get("model", "speech-02-hd"),
        "text": text_to_speak,
        "stream": False,
        "voice_setting": {
            "voice_id": role_config.get("voiceID"),
            "speed": float(role_config.get("voice speed", 1.0)),
            "vol": 1.0,
            "pitch": 0,
            "emotion": emotion
        },
        "audio_setting": {
            "sample_rate": 44100,
            "bitrate": 256000,
            "format": "mp3",
            "channel": 1
        },
        "output_format": "hex"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()

        response_json = response.json()

        if response_json.get("base_resp", {}).get("status_code") == 0:
            audio_hex = response_json.get("data", {}).get("audio")
            if audio_hex:
                audio_bytes = bytes.fromhex(audio_hex)
                
                # 确保输出目录存在
                if not os.path.exists("outputs"):
                    os.makedirs("outputs")

                if base_filename:
                    file_name = f"outputs/{base_filename}_{role_config['name']}.mp3"
                else:
                    timestamp = int(time.time())
                    file_name = f"outputs/{role_config['name']}_output_{timestamp}.mp3"
                
                with open(file_name, "wb") as f:
                    f.write(audio_bytes)
                
                return file_name
            else:
                st.error(f"角色 '{role_config['name']}' 的 API 响应中未找到音频数据。")
                return None
        else:
            st.error(f"角色 '{role_config['name']}' 的 API 请求失败: {response_json.get('base_resp', {}).get('status_msg')}")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"请求 API 时发生错误: {e}")
        return None
    except Exception as e:
        st.error(f"处理响应时发生未知错误: {e}")
        return None

# --- Streamlit App ---
st.set_page_config(page_title="MiniMax TTS 生成器", layout="wide")

st.title("MiniMax 文本转语音生成器")

# 在侧边栏中获取 API 凭证
with st.sidebar:
    st.header("API 凭证")
    st.info("请在此处输入您的 MiniMax API 凭证。")
    
    group_id_input = st.text_input("Group ID", value=st.session_state.get("group_id", ""))
    api_key_input = st.text_input("API Key", type="password", value=st.session_state.get("api_key", ""))

    if group_id_input and api_key_input:
        st.session_state["group_id"] = group_id_input
        st.session_state["api_key"] = api_key_input
        st.success("凭证已保存。")

st.info("请在下方的文本框中输入您想要转换为语音的文本，然后点击“生成语音”按钮。")

# Emotion selection
emotion_options = ["happy", "sad", "angry", "fearful", "disgusted", "surprised", "neutral"]
selected_emotion = st.selectbox("选择一个情绪", emotion_options, index=0)

base_filename_input = st.text_input("输入基础文件名（可选）")
text_to_convert = st.text_area("输入文本", height=150)

if st.button("生成语音"):
    # 检查凭证是否已输入
    if "group_id" not in st.session_state or "api_key" not in st.session_state:
        st.error("请在左侧边栏中输入您的 Group ID 和 API Key。")
    elif not text_to_convert.strip():
        st.warning("请输入要转换为语音的文本。")
    else:
        st.success("正在为所有角色生成语音...")
        
        all_successful = True
        generated_files = []

        base_filename = base_filename_input.strip() if base_filename_input else None

        for role in ROLES_CONFIG:
            with st.spinner(f"正在为角色 '{role['name']}' 生成语音..."):
                file_path = generate_speech(
                    text_to_convert,
                    role,
                    st.session_state["group_id"],
                    st.session_state["api_key"],
                    emotion=selected_emotion,
                    base_filename=base_filename
                )
            
            if file_path:
                generated_files.append((role['name'], file_path))
            else:
                all_successful = False

        if all_successful:
            st.success("所有语音文件已成功生成！")
        else:
            st.warning("部分语音文件生成失败。")

        if generated_files:
            st.subheader("播放生成的音频：")
            for role_name, file_path in generated_files:
                st.markdown(f"**角色：{role_name}**")
                st.audio(file_path, format='audio/mp3')

            # Create a zip file in memory
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                for _, file_path in generated_files:
                    zip_file.write(file_path, os.path.basename(file_path))
            
            st.download_button(
                label="一键全部下载",
                data=zip_buffer.getvalue(),
                file_name="generated_audios.zip",
                mime="application/zip"
            )

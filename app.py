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
    # 原有的自定义角色
    {
        "name": "小蜗牛宝宝",
        "voiceID": "moss_audio_f0666a48-7334-11f0-87d3-b63243124dc4",
        "voice speed": "0.85",
        "model": "speech-2.5-hd-preview",
        "category": "自定义角色",
        "default_speed": 0.96,
        "default_pitch": 0,
        "default_emotion": "happy"
    },
    {
        "name": "小猪宝宝",
        "voiceID": "moss_audio_6ce18488-740c-11f0-b242-1e4178e90ad2",
        "voice speed": "0.99",
        "model": "speech-2.5-hd-preview",
        "category": "自定义角色",
        "default_speed": 1.0,
        "default_pitch": 1,
        "default_emotion": "happy"
    },
    {
        "name": "小鳄鱼宝宝",
        "voiceID": "moss_audio_8d5b1cb7-a8c5-11f0-aa74-6a175ee91adb",
        "voice speed": "0.99",
        "model": "speech-2.5-hd-preview",
        "category": "自定义角色",
        "default_speed": 0.97,
        "default_pitch": -2,
        "default_emotion": "happy"
    },
    # 新增的系统音色
    {
        "name": "智慧女性",
        "voiceID": "Wise_Woman",
        "voice speed": "1.0",
        "model": "speech-2.5-hd-preview",
        "category": "系统音色"
    },
    {
        "name": "友好的人",
        "voiceID": "Friendly_Person",
        "voice speed": "1.0",
        "model": "speech-2.5-hd-preview",
        "category": "系统音色"
    },
    {
        "name": "励志女孩",
        "voiceID": "Inspirational_girl",
        "voice speed": "1.0",
        "model": "speech-2.5-hd-preview",
        "category": "系统音色"
    },
    {
        "name": "深沉男声",
        "voiceID": "Deep_Voice_Man",
        "voice speed": "1.0",
        "model": "speech-2.5-hd-preview",
        "category": "系统音色"
    },
    {
        "name": "冷静女性",
        "voiceID": "Calm_Woman",
        "voice speed": "1.0",
        "model": "speech-2.5-hd-preview",
        "category": "系统音色"
    },
    {
        "name": "随意男性",
        "voiceID": "Casual_Guy",
        "voice speed": "1.0",
        "model": "speech-2.5-hd-preview",
        "category": "系统音色"
    },
    {
        "name": "活泼女孩",
        "voiceID": "Lively_Girl",
        "voice speed": "1.0",
        "model": "speech-2.5-hd-preview",
        "category": "系统音色"
    },
    {
        "name": "耐心男性",
        "voiceID": "Patient_Man",
        "voice speed": "1.0",
        "model": "speech-2.5-hd-preview",
        "category": "系统音色"
    },
    {
        "name": "年轻骑士",
        "voiceID": "Young_Knight",
        "voice speed": "1.0",
        "model": "speech-2.5-hd-preview",
        "category": "系统音色"
    },
    {
        "name": "坚定男性",
        "voiceID": "Determined_Man",
        "voice speed": "1.0",
        "model": "speech-2.5-hd-preview",
        "category": "系统音色"
    },
    {
        "name": "可爱女孩",
        "voiceID": "Lovely_Girl",
        "voice speed": "1.0",
        "model": "speech-2.5-hd-preview",
        "category": "系统音色"
    },
    {
        "name": "正派男孩",
        "voiceID": "Decent_Boy",
        "voice speed": "1.0",
        "model": "speech-2.5-hd-preview",
        "category": "系统音色"
    },
    {
        "name": "威严气质",
        "voiceID": "Imposing_Manner",
        "voice speed": "1.0",
        "model": "speech-2.5-hd-preview",
        "category": "系统音色"
    },
    {
        "name": "优雅男性",
        "voiceID": "Elegant_Man",
        "voice speed": "1.0",
        "model": "speech-2.5-hd-preview",
        "category": "系统音色"
    },
    {
        "name": "女修道院院长",
        "voiceID": "Abbess",
        "voice speed": "1.0",
        "model": "speech-2.5-hd-preview",
        "category": "系统音色"
    },
    {
        "name": "甜美女孩2",
        "voiceID": "Sweet_Girl_2",
        "voice speed": "1.0",
        "model": "speech-2.5-hd-preview",
        "category": "系统音色"
    },
    {
        "name": "活力女孩",
        "voiceID": "Exuberant_Girl",
        "voice speed": "1.0",
        "model": "speech-2.5-hd-preview",
        "category": "系统音色"
    }
]

def get_smart_defaults(selected_roles):
    """
    根据选中的角色计算智能默认值
    如果只选中了一个角色且有默认值，使用该角色的默认值
    否则使用系统默认值
    """
    if len(selected_roles) == 1:
        role = selected_roles[0]
        return {
            "speed": role.get("default_speed", 1.0),
            "pitch": role.get("default_pitch", 0),
            "emotion": role.get("default_emotion", "happy")
        }
    else:
        # 多个角色时，使用系统默认值
        return {
            "speed": 1.0,
            "pitch": 0,
            "emotion": "happy"
        }

def generate_speech(text_to_speak, role_config, group_id, api_key, emotion, speed, pitch, base_filename=None):
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
            "speed": speed,
            "vol": 1.0,
            "pitch": pitch,
            "emotion": emotion
        },
        "audio_setting": {
            "sample_rate": 44100,
            "format": "wav",
            "channel": 2
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
                    file_name = f"outputs/{base_filename}_{role_config['name']}.wav"
                else:
                    timestamp = int(time.time())
                    file_name = f"outputs/{role_config['name']}_output_{timestamp}.wav"
                
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

# 角色选择部分
st.subheader("🎭 角色选择")
col1, col2 = st.columns(2)

with col1:
    generation_mode = st.radio(
        "生成模式",
        ["选择生成", "全部生成"],
        index=0,
        help="选择生成：只为选中的角色生成语音\n全部生成：为所有角色生成语音"
    )

with col2:
    if generation_mode == "选择生成":
        # 按分类显示角色选择
        custom_roles = [role for role in ROLES_CONFIG if role.get("category") == "自定义角色"]
        system_roles = [role for role in ROLES_CONFIG if role.get("category") == "系统音色"]

        st.write("**自定义角色：**")
        selected_custom = []
        for role in custom_roles:
            if st.checkbox(f"{role['name']}", key=f"custom_{role['name']}", value=True):
                selected_custom.append(role)

        st.write("**系统音色：**")
        selected_system = []
        for role in system_roles:
            if st.checkbox(f"{role['name']}", key=f"system_{role['name']}"):
                selected_system.append(role)

        selected_roles = selected_custom + selected_system

        if selected_roles:
            st.success(f"已选择 {len(selected_roles)} 个角色")
        else:
            st.warning("请至少选择一个角色")
    else:
        # 全部生成模式
        selected_roles = ROLES_CONFIG
        st.info(f"将为所有 {len(ROLES_CONFIG)} 个角色生成语音")

# 计算智能默认值
if generation_mode == "选择生成" and selected_roles:
    smart_defaults = get_smart_defaults(selected_roles)
else:
    smart_defaults = {"speed": 1.0, "pitch": 0, "emotion": "happy"}

# Emotion selection
st.subheader("🎵 语音参数")
emotion_options = ["happy", "sad", "angry", "fearful", "disgusted", "surprised", "neutral"]
default_emotion_index = emotion_options.index(smart_defaults["emotion"]) if smart_defaults["emotion"] in emotion_options else 0
selected_emotion = st.selectbox("选择一个情绪", emotion_options, index=default_emotion_index)

# Speed and Pitch selection
selected_speed = st.slider("选择语速", min_value=0.5, max_value=2.0, value=smart_defaults["speed"], step=0.01)
selected_pitch = st.slider("选择音调", min_value=-12, max_value=12, value=smart_defaults["pitch"], step=1)

base_filename_input = st.text_input("输入基础文件名（可选）")
text_to_convert = st.text_area("输入文本", height=150)

if st.button("生成语音"):
    # 检查凭证是否已输入
    if "group_id" not in st.session_state or "api_key" not in st.session_state:
        st.error("请在左侧边栏中输入您的 Group ID 和 API Key。")
    elif not text_to_convert.strip():
        st.warning("请输入要转换为语音的文本。")
    elif generation_mode == "选择生成" and not selected_roles:
        st.warning("请至少选择一个角色进行生成。")
    else:
        # 根据生成模式确定要使用的角色
        roles_to_generate = selected_roles if generation_mode == "选择生成" else ROLES_CONFIG

        st.success(f"正在为 {len(roles_to_generate)} 个角色生成语音...")

        all_successful = True
        generated_files = []

        base_filename = base_filename_input.strip() if base_filename_input else None

        for role in roles_to_generate:
            with st.spinner(f"正在为角色 '{role['name']}' 生成语音..."):
                file_path = generate_speech(
                    text_to_convert,
                    role,
                    st.session_state["group_id"],
                    st.session_state["api_key"],
                    emotion=selected_emotion,
                    speed=selected_speed,
                    pitch=selected_pitch,
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
                st.audio(file_path, format='audio/wav')

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

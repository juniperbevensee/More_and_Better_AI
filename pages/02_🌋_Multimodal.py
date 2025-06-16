import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO
import json
import ollama
from utilities.icon import page_icon

st.set_page_config(
    page_title="Image Analysis",
    page_icon="🌋",
    layout="wide",
    initial_sidebar_state="expanded",
)

def img_to_base64(image):
    """Convert an image to base64 format."""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def get_allowed_model_names(models_info) -> tuple:
    """
    Returns a tuple containing the names of the allowed models.
    Updated to work with current Ollama API response structure.
    """
    allowed_models = ["bakllava:latest", "llava:latest"]
    
    # Safely extract model names from the response
    installed_models = []
    if hasattr(models_info, 'models'):
        installed_models = [model.model for model in models_info.models if hasattr(model, 'model')]
    
    return tuple(model for model in allowed_models if model in installed_models)

def main():
    page_icon("🌋")
    st.subheader("Image Analysis", divider="red", anchor=False)

    try:
        models_info = ollama.list()
        available_models = get_allowed_model_names(models_info)
        missing_models = set(["bakllava:latest", "llava:latest"]) - set(available_models)
    except Exception as e:
        st.error(f"Failed to get model list: {str(e)}", icon="😳")
        available_models = []
        missing_models = set(["bakllava:latest", "llava:latest"])

    col_1, col_2 = st.columns(2)
    with col_1.popover("⚙️ Model Management", help="Manage models here"):
        if not available_models:
            st.error("No allowed models are available.", icon="😳")
            model_to_download = st.selectbox(
                "Select a model to download (~5GB)", ["bakllava:latest", "llava:latest"]
            )
            if st.button(f"Download {model_to_download}"):
                try:
                    with st.spinner(f"Downloading {model_to_download}..."):
                        ollama.pull(model_to_download)
                    st.toast(f"Downloaded model: {model_to_download}", icon="✅")
                    st.rerun()
                except Exception as e:
                    st.error(
                        f"Failed to download model: {model_to_download}. Error: {str(e)}",
                        icon="😳",
                    )
        else:
            if missing_models:
                model_to_download = st.selectbox(
                    ":green[**📥 DOWNLOAD MODEL**]", list(missing_models)
                )
                if st.button(f":green[Download **_{model_to_download}_**]"):
                    try:
                        with st.spinner(f"Downloading {model_to_download}..."):
                            ollama.pull(model_to_download)
                        st.toast(f"Downloaded model: {model_to_download}", icon="✅")
                        st.rerun()
                    except Exception as e:
                        st.error(
                            f"Failed to download model: {model_to_download}. Error: {str(e)}",
                            icon="😳",
                        )

            selected_model = st.selectbox(":red[**⛔️ DELETE MODEL**]", available_models)
            if st.button(f"Delete **_{selected_model}_**", type="primary"):
                try:
                    ollama.delete(selected_model)
                    st.toast(f"Deleted model: {selected_model}", icon="✅")
                    st.rerun()
                except Exception as e:
                    st.error(
                        f"Failed to delete model: {selected_model}. Error: {str(e)}",
                        icon="😳",
                    )

    if not available_models:
        return

    selected_model = col_2.selectbox(
        "Pick a model available locally on your system ↓", 
        available_models, 
        key="model_select"
    )

    # Initialize chat session
    if "chats" not in st.session_state:
        st.session_state.chats = []
    if "uploaded_file_state" not in st.session_state:
        st.session_state.uploaded_file_state = None

    uploaded_file = st.file_uploader(
        "Upload an image for analysis", 
        type=["png", "jpg", "jpeg"],
        key="image_upload"
    )

    col1, col2 = st.columns(2)

    with col2:
        container1 = st.container(height=500, border=True)
        with container1:
            if uploaded_file is not None:
                st.session_state.uploaded_file_state = uploaded_file.getvalue()
                image = Image.open(BytesIO(st.session_state.uploaded_file_state))
                st.image(image, caption="Uploaded image")

    with col1:
        container2 = st.container(height=500, border=True)

        if uploaded_file is not None:
            # Display chat history
            for message in st.session_state.chats:
                avatar = "🌋" if message["role"] == "assistant" else "🫠"
                with container2.chat_message(message["role"], avatar=avatar):
                    st.markdown(message["content"])

            # Handle new user input
            if user_input := st.chat_input("Question about the image...", key="chat_input"):
                st.session_state.chats.append({"role": "user", "content": user_input})
                container2.chat_message("user", avatar="🫠").markdown(user_input)

                image_base64 = img_to_base64(image)
                API_URL = "http://localhost:11434/api/generate"
                
                with container2.chat_message("assistant", avatar="🌋"):
                    with st.spinner(":blue[processing...]"):
                        try:
                            response = requests.post(
                                API_URL,
                                json={
                                    "model": selected_model,
                                    "prompt": user_input,
                                    "images": [image_base64],
                                    "stream": False
                                },
                                headers={"Content-Type": "application/json"}
                            )
                            
                            if response.status_code == 200:
                                response_data = response.json()
                                llava_response = response_data.get("response", "")
                                st.markdown(llava_response)
                                st.session_state.chats.append(
                                    {"role": "assistant", "content": llava_response}
                                )
                            else:
                                st.error(f"API Error: {response.status_code}", icon="😳")
                        except Exception as e:
                            st.error(f"Error processing request: {str(e)}", icon="😳")

if __name__ == "__main__":
    main()

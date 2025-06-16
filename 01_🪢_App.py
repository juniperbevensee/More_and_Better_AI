#Ensure that your (updated) python environment has access to all packages. 

import ollama
import streamlit as st
from openai import OpenAI
from utilities.icon import page_icon

st.set_page_config(
    page_title="More and Better AI",
    page_icon="🪢",
    layout="wide",
    initial_sidebar_state="expanded"
)

def extract_model_names(models_info: dict) -> tuple:
    """
    Extracts the model names from the models information.
    
    :param models_info: A dictionary containing the models' information.
    Return:
        A tuple containing the model names.
    """
    # Updated to use the correct response structure
    return tuple(model["model"] for model in models_info.get("models", []))

def main():
    """
    The main function that runs the application.
    """
    st.image("logo.png")
    st.subheader("More and Better AI", divider="red", anchor=False)
    st.markdown('*A platform to create and use free, local, and open-source AI models.*')

    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",  # required, but unused
    )

    try:
        models_info = ollama.list()
        available_models = extract_model_names(models_info)
    except Exception as e:
        st.error(f"Failed to connect to Ollama: {e}", icon="⚠️")
        st.stop()

    if available_models:
        selected_model = st.selectbox(
            "Pick a model available locally on your system ↓", 
            available_models, 
            help="Go to Settings to download or create models."
        )
    else:
        st.warning("You have not pulled any model from Ollama yet!", icon="⚠️")
        if st.button("Go to settings to download a model"):
            st.switch_page("pages/03_⚙️_Settings.py")
        return

    message_container = st.container(height=500, border=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        avatar = "🤖" if message["role"] == "assistant" else "😎"
        with message_container.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    if prompt := st.chat_input("How can we help each other?"):
        try:
            st.session_state.messages.append({"role": "user", "content": prompt})
            message_container.chat_message("user", avatar="😎").markdown(prompt)

            with message_container.chat_message("assistant", avatar="🤖"):
                with st.spinner("model working..."):
                    stream = client.chat.completions.create(
                        model=selected_model,
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ],
                        stream=True,
                    )
                # stream response
                response = st.write_stream(stream)
            st.session_state.messages.append(
                {"role": "assistant", "content": response})

        except Exception as e:
            st.error(f"Error during chat: {e}", icon="⛔️")

if __name__ == "__main__":
    main()
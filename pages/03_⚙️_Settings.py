import streamlit as st
import ollama
from time import sleep
from utilities.icon import page_icon

st.set_page_config(
    page_title="Model management",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Model selection dictionary (display name: actual model name)
MODEL_CHOICES = {
    "deepseek-r1 (4.7GB)": "deepseek-r1",
    "deepseek-r1 (400GB)": "deepseek-r1:671B",
    "gemma3 (815MB)": "gemma3:1b",
    "gemma3 (17GB)": "gemma3:27b",
    "llama4 (67GB)": "llama4:scout",
    "llama4 (245GB)": "llama4:maverick",
    "uncensored llama 2 (3.8GB)": "llama2-uncensored",
    "codellama (3.8GB)": "codellama",
    "llava (for multimodal) (4.5GB)": "llava"
}

def main():
    page_icon("⚙️")
    st.subheader("Model Management", divider="red", anchor=False)

    st.subheader("Download Models", anchor=False)


    # Create selectbox with formatted display names
    selected_display = st.selectbox(
        "Select model to download (takes ages) ↓",
        options=list(MODEL_CHOICES.keys()),
        index=None,
        placeholder="Choose a model..."
    )
    
    if st.button(f"📥 :green[**Download**]"):
        if selected_display:
            model_name = MODEL_CHOICES[selected_display]
            try:
                with st.spinner(f"Downloading {model_name}..."):
                    ollama.pull(model_name)
                st.success(f"Downloaded model: {selected_display}", icon="🎉")
                st.balloons()
                sleep(1)
                st.rerun()
            except Exception as e:
                st.error(
                    f"""Failed to download model: {
                    selected_display}. Error: {str(e)}""",
                    icon="😳",
                )
        else:
            st.warning("Please select a model to download.", icon="⚠️")


    st.markdown("Additional models and info available [here](https://github.com/ollama/ollama?tab=readme-ov-file#model-library). ")


    model_name_text = st.text_input(
        "If you prefer an an unlisted model ↓", placeholder="mistral"
    )
    if st.button(f"📥 :green[**Download**] :red[{model_name_text}]"):
        if model_name_text:
            try:
                ollama.pull(model_name_text)
                st.success(f"Downloaded model: {model_name_text}", icon="🎉")
                st.balloons()
                sleep(1)
                st.rerun()
            except Exception as e:
                st.error(
                    f"""Failed to download model: {
                    model_name_text}. Error: {str(e)}""",
                    icon="😳",
                )
        else:
            st.warning("Please enter a model name.", icon="⚠️")

    st.divider()

    st.subheader("Create model via system prompt (modelfile)", anchor=False)
    
    
    def extract_model_names(models_info: dict) -> tuple:
        """
        Extracts the model names from the models information.
        
        :param models_info: A dictionary containing the models' information.
        Return:
            A tuple containing the model names.
        """
        # Updated to use the correct response structure
        return tuple(model["model"] for model in models_info.get("models", []))

    st.markdown("*Note: Overwrites previous modelfiles.*")

    try:
        models_info = ollama.list()
        available_models = extract_model_names(models_info)
    except Exception as e:
        st.error(f"Failed to connect to Ollama: {e}", icon="⚠️")
        st.stop()

    if available_models:
        base_model = st.selectbox(
            "Pick a model available locally on your system ↓", 
            available_models
        )
    else:
        st.warning("You have not pulled any model from Ollama yet!", icon="⚠️")
        return

    system_prompt = st.text_area(
        "System prompt (SYSTEM clause)",
        height=100,
        placeholder="You are Mario from Super Mario Bros.",
        help="The custom instructions for your model"
    )
    
    temperature_selection = st.slider(
        "Temperature (0=coherent 1=creative):",
        min_value=0.0,
        max_value=1.0,
        value=0.8,
        step=0.1
        )


    model_name = st.text_input(
        "Name for your new model (one word only):",
        placeholder="mario"
    )
    
    
    
    if st.button(f"🆕 Create Model {model_name}"):
        if model_name and base_model and system_prompt:
            try:
                # Using the correct API syntax
                ollama.create(
                    model=model_name,
                    from_=base_model,
                    parameters={"temperature":temperature_selection},
                    system=system_prompt
                )
                st.success(f"Created model: {model_name}", icon="✅")
                st.balloons()
                sleep(1)
                st.rerun()
            except Exception as e:
                st.error(
                    f"""Failed to create model: {
                         model_name}. Error: {str(e)}""",
                    icon="😳",
                )
        else:
            st.warning("Please enter all required fields: model name, base model, and system prompt", icon="⚠️")

    st.divider()

    st.subheader("Delete Models", anchor=False)
    try:
        client = ollama.Client()
        models_list = client.list()
        
        # Extract model names safely
        available_models = []
        if models_list and hasattr(models_list, 'models'):
            available_models = [model.model for model in models_list.models if hasattr(model, 'model')]

        if available_models:
            selected_models = st.multiselect("Select models to delete", available_models)
            if st.button("🗑️ :red[**Delete Selected Model(s)**]"):
                for model in selected_models:
                    try:
                        client.delete(model)
                        st.success(f"Deleted model: {model}", icon="🎉")
                        st.balloons()
                        sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(
                            f"""Failed to delete model: {
                            model}. Error: {str(e)}""",
                            icon="😳",
                        )
        else:
            st.info("No models available for deletion.", icon="🦗")
    except Exception as e:
        st.error(f"Failed to list models: {str(e)}", icon="😳")

if __name__ == "__main__":
    main()

# model_loader.py
from langchain_community.chat_models import ChatLlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler


def load_local_model(gguf_path: str):
    """
    Loads a GGUF model in Chat Mode using ChatLlamaCpp.
    Matches the parameters from your Modelfile.
    """
    print(f"Loading GGUF from: {gguf_path} ... (Chat Mode)")

    # We use ChatLlamaCpp because it automatically applies the
    # <|start_header_id|> templates you showed in your Modelfile.
    llm = ChatLlamaCpp(
        model_path=gguf_path,

        # --- HARDWARE SETTINGS ---
        n_gpu_layers=-1,  # -1 = Offload ALL layers to GPU (Best for P100/T4)
        n_ctx=4096,  # Matches 'PARAMETER num_ctx 4096'

        # --- GENERATION SETTINGS ---
        temperature=0.1,  # Matches 'PARAMETER temperature 0.1'
        max_tokens=512,  # Safety limit to prevent long ramblings
        verbose=False,  # Set to True only if you need to debug crashing

        # --- SAFETY STOPS ---
        # These stop the model if it tries to generate the User's turn
        stop=[
            "<|eot_id|>",
            "<|start_header_id|>",
            "<|end_header_id|>",
            "User:",
            "Human:"
        ]
    )
    return llm
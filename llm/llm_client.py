from llama_cpp import Llama  

MODEL_PATH = r"D:\Assignment 2 TiCS\llm\models\bin\Llama-3.2-1B-Instruct-Q4_0.gguf" # Change to your own model directory

# Loads model
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,
    verbose=False
)

def run_llm(prompt: str) -> str:
    """Run inference using local LLaMA."""
    response = llm(
        prompt,
        max_tokens=512,
        temperature=0.2,
        top_p=0.95,
    )
    return response["choices"][0]["text"].strip()

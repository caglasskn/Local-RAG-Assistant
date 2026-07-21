import onnxruntime as ort
from transformers import AutoTokenizer
from pathlib import Path
import numpy as np

MODEL_DIR = Path("models") / "bge-m3"
ONNX_PATH = MODEL_DIR / "model.onnx"

# Tokenizer ve ONNX modeli uygulama başlarken bir kez yüklenir.
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
session = ort.InferenceSession(str(ONNX_PATH))

def generate_embedding(document):
    """
    Verilen metin için BGE-M3 embedding vektörü oluşturur ve normalize edilmiş embedding'i döndürür.
    """

    tokens = tokenizer(document, padding=True, truncation=True, return_tensors="np")

    # ONNX modeli çalıştırılarak token embeddingleri elde edilir. 
    output = session.run(None, dict(tokens))

    last_hidden_state = output[0]

    # Token embeddinglerinin ortalaması alınarak tek bir embedding üretilir.
    embedding = np.mean(last_hidden_state, axis=1)

    embedding = embedding[0]

    # Cosine similarity için embedding normalize edilir.
    embedding = embedding / np.linalg.norm(embedding)

    return embedding.tolist()
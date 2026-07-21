from openai import OpenAI
from src.retrieval import retrieve
from src.config import TEMPERATURE, BASE_URL, MODEL_NAME

# Local LLM servisine bağlanmak için OpenAI istemcisi oluşturulur.
client = OpenAI(
    base_url=BASE_URL,
    api_key="not-needed"
)

# LLM'e gönderilecek prompt'u oluşturur.
def build_prompt(context, history, question):
    """
    LLM'e gönderilecek prompt'u oluşturur.
    Prompt; konuşma geçmişi, bulunan dökümanlar ve
    kullanıcının güncel sorusunu içerir.
    """

    # LLM'in cevap üretirken kullanacağı prompt hazırlanır.
    prompt = f"""
You are an AI assistant that answers questions using the provided context.

Instructions:
- Use ONLY the information in the context.
- Use the conversation history only to understand what the user is referring to.
- Do not invent information.
- If the answer is not in the context, say:
"I don't have enough information in the provided documents."

Conversation History:
{history}

Context:
{context}

Current Question:
{question}

Answer:
"""
    return prompt

# Retrieval sonucunu kullanarak LLM'den cevap üretir.
def generate_answer(question, history, retrieval_query):
    """
    Retrieval sonucunu kullanarak LLM'den cevap üretir
    ve kullanılan kaynaklarla birlikte döndürür.
    """

    # Kullanıcı sorusuna en uygun dökümanlar retrieval ile bulunur.
    result = retrieve(retrieval_query)

    # Uygun döküman bulunamazsa kullanıcı bilgilendirilir.
    if result is None:
        return {
            "answer": "Dökümanlarda yeterli bilgi bulunamadı.",
            "sources": []
        }
    
    # Retrieval sonucundan context ve kaynak bilgileri alınır.
    context = result["context"]
    sources = result["sources"]

    prompt = build_prompt(context, history, question)

    # Prompt Local LLM'e gönderilir ve cevap üretilir.
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI assistant. Answer ONLY using the provided context."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=TEMPERATURE
    )

    # Model cevabı ve kullanılan kaynaklar döndürülür.
    return {
    "answer": response.choices[0].message.content,
    "sources": sources
    }
from src.database import get_all_documents
from src.embeddings import generate_embedding
from src.config import TOP_K, SIMILARITY_THRESHOLD

import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def calculate_similarity(query_embedding, db_embedding):
    """
    Soru embedding'i ile veritabanındaki embedding arasındaki cosine similarity skorunu hesaplar.
    """
    score = cosine_similarity(
        [query_embedding],
        [db_embedding]
    )[0][0]

    return score


def search(question, k=TOP_K):
    """
    Kullanıcı sorusuna en benzer dökümanları bulur ve benzerlik skoruna göre sıralayarak döndürür.
    """
    query_embedding = generate_embedding(question)

    documents = get_all_documents()

    filtered = []

    # Veritabanındaki tüm dökümanlar üzerinde benzerlik hesaplanır.
    for row in documents:
        db_embedding = json.loads(row[3])
        db_embedding = np.array(db_embedding)

        score = calculate_similarity(query_embedding, db_embedding)

        # Benzerlik skoru threshold değerinin üzerindeyse sonuçlara eklenir.
        if score >= SIMILARITY_THRESHOLD:
            filtered.append((score, row))

    # Sonuçlar benzerlik skoruna göre büyükten küçüğe sıralanır.
    filtered.sort(reverse=True, key=lambda x: x[0])

    # Debug amacıyla en benzer sonuçlar terminale yazdırılır.
    print("\nTop Results\n")

    for score, row in filtered[:k]:
        print(f"{row[0]} | {score:.3f}")

    return filtered[:k]
    

def retrieve(question, k=TOP_K):
    """
    En benzer dökümanları alır, LLM'e gönderilecek context'i ve kaynak bilgilerini hazırlar.
    """
    results = search(question, k)

    if len(results) == 0:
        return None

    contexts = []
    sources = []

    for score, row in results:
        soru = row[1]
        cevap = row[2]

        # LLM'in kullanacağı context hazırlanır.
        contexts.append(
            f"Soru: {soru}\n"
            f"Cevap: {cevap}"
        )

        # Arayüzde gösterilecek kaynak bilgileri hazırlanır.
        sources.append(
            {
                "id": row[0],
                "question": soru,
                "answer": cevap,
                "score": round(float(score), 3)
            }
        )

    return { 
        "context": "\n\n".join(contexts),
        "sources": sources
    }
import json
from src.database import insert_question
from src.embeddings import generate_embedding

def load_json():
    """
    Soru bankasını JSON dosyasından okuyarak belleğe yükler.
    """

    with open("data/azure_questions.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    return data

def ingest_data():
    """
    JSON dosyasındaki soru-cevap verileri için embedding oluşturur ve tüm kayıtları SQLite veritabanına kaydeder.
    """

    data = load_json()

    soru_bankasi = data["azure_kapsamli_soru_bankasi"]

    for kategori, sorular in soru_bankasi.items():
        for soru_objesi in sorular:
            id = soru_objesi["id"]
            soru = soru_objesi["soru"]
            cevap = soru_objesi["cevap"]
            
            #Embedding oluşturulacak metin hazırlanır.
            document = (f"Soru: {soru}\nCevap: {cevap}")

            embedding_list = generate_embedding(document)
            embedding = json.dumps(embedding_list)

            insert_question(id, kategori, soru, cevap, embedding)
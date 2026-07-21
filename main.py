"""
main.py

Bu dosya terminal üzerinden hızlı test yapmak amacıyla hazırlanmıştır.
Asıl kullanıcı arayüzü Streamlit (app.py) üzerinden çalıştırılmaktadır.
"""

from src.database import create_table
from src.ingest import ingest_data
from src.generator import generate_answer

# Veritabanı ve gerekli tablo oluşturulur.
create_table()

# İlk çalıştırmada veriler veritabanına yüklenir.
# Veri yüklendikten sonra tekrar çalıştırılmaması için yoruma alınabilir.
# ingest_data()

if __name__ == "__main__":
    """
    Terminal üzerinden hızlı soru-cevap testi yapılmasını sağlar.
    """

    question = input("Soru: ")

    # İlk soru olduğu için konuşma geçmişi yalnızca mevcut sorudan oluşur.
    history = question
    retrieval_query = question

    answer = generate_answer(question, history, retrieval_query)

    print("\nCevap:\n")
    print(answer["answer"])

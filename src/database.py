import sqlite3
from src.config import DATABASE_NAME

def get_connection():
    """
    SQLite veritabanı bağlantısını oluşturur ve bağlantı nesnesini döndürür.
    """

    conn = sqlite3.connect(DATABASE_NAME)

    return conn

def create_table():
    """
    Soruların, cevapların ve embedding bilgilerinin saklanacağı 'sorular' tablosunu oluşturur.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sorular (
        id INTEGER PRIMARY KEY,
        kategori TEXT,
        soru TEXT,
        cevap TEXT,
        embedding TEXT           
    )
    """)

    conn.commit()
    conn.close()

def insert_question(id, kategori, soru, cevap, embedding):
    """
    Yeni bir soru kaydını ve embedding bilgisini veritabanına ekler.
    Aynı ID'ye sahip kayıt varsa tekrar eklenmez.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO sorular (kategori, id, soru, cevap, embedding)
        VALUES(?, ?, ?, ?, ?)
        """, (
            kategori,
            id,
            soru,
            cevap,
            embedding
        ))

    conn.commit()
    conn.close()

def get_all_documents():
    """
    Veritabanındaki tüm dökümanları embedding bilgileriyle birlikte getirir.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, soru, cevap, embedding
        FROM sorular
    """)

    result = cursor.fetchall()

    conn.close()

    return result

def get_document_by_id(id):
    """
    Verilen ID'ye ait dökümanı veritabanından getirir.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, kategori, soru, cevap, embedding
        FROM sorular
        WHERE id = ?
    """, (id,))

    result = cursor.fetchone()

    conn.close()

    return result
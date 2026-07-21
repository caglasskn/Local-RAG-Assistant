"""
app.py

Streamlit tabanlı kullanıcı arayüzü.

Kullanıcının sorularını alır, RAG sistemine gönderir,
üretilen cevabı ve kullanılan kaynakları görüntüler.
"""

import streamlit as st
from src.database import get_connection
from src.generator import generate_answer

# Streamlit sayfa ayarları
st.set_page_config(
    page_title="Local RAG Assistant",
    page_icon="🤖"
)

st.title("🤖 Local RAG Assistant")

# Sidebar: Sistem bilgileri ve veritabanı istatistikleri
with st.sidebar:
    st.header("⚙️ Sistem Bilgileri")
    st.caption("Yerel Çevrimdışı RAG Mimarisi")
    st.divider()

    # Modeller ve Çalışma Zamanı
    st.subheader("🤖 Yapay Zeka Modelleri")
    st.success("LLM: **Phi-4-Mini** (Yerel / Offline)", icon="⚡")
    st.info("Embedding: **BGE-M3** (ONNX Engine)", icon="🔤")

    st.divider()

    # Veritabanı ve İstatistikler
    st.subheader("💾 Bilgi Tabanı")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Tablo adınız 'sorular' olduğu için güncellendi
        cursor.execute("SELECT COUNT(*) FROM sorular")
        toplam_soru = cursor.fetchone()[0]
        conn.close()

        st.metric(
            label="Kayıtlı Soru-Cevap Sayısı", 
            value=f"{toplam_soru} Adet",
            help="SQLite veritabanında indexlenmiş toplam bilgi sayısı"
        )
    except Exception:
        st.error("Veritabanına bağlanılamadı.", icon="🚨")

    st.divider()
    st.caption("🔒 *Bu uygulama tamamen çevrimdışı çalışır. İnternet bağlantısı gerekmez.*")


# Sohbet geçmişi ilk çalıştırmada oluşturulur.
if "messages" not in st.session_state:
    st.session_state.messages = []


# Önceki sohbet mesajları ekranda gösterilir.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if (message["role"] == "assistant" and "sources" in message and message["sources"]):
            with st.expander("📚 Kullanılan Kaynaklar"):
                for index, source in enumerate(message["sources"], start=1):
                    st.caption(f"📚 Kaynak: {index}")
                    st.caption(
                        f"**ID:** {source['id']} | "
                        f"**Skor:** {source['score']:.3f} | "
                        f"**Soru:** {source['question']} | "
                        f"**Cevap:** {source['answer']}"
                    )


# Kullanıcıdan yeni soru alınır.
question = st.chat_input("Sorunuzu girin")

if question:
    # Kullanıcı mesajı sohbet geçmişine eklenir.
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Önceki kullanıcı soruları konuşma geçmişi olarak hazırlanır.
    history = []

    for message in st.session_state.messages:
        if message["role"] == "user":
            history.append(message["content"])

    # Son iki kullanıcı sorusu birleştirilerek retrieval sorgusu oluşturulur.
    retrieval_query = "\n".join(history[-2:])

    # Asistan cevabı oluşturulur ve kullanıcıya gösterilir.
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("*İlgili belgeler getiriliyor...*")
        
        # Retrieval ve Local LLM kullanılarak cevap üretilir.
        answer = generate_answer(question, history, retrieval_query)
        

        message_placeholder.markdown(answer["answer"])
        
        # Modelin bilgi bulamadığı durum kontrol edilir.
        is_unknown_answer = (
            "enough information" in answer["answer"].lower() or 
            "bulunmamaktadır" in answer["answer"].lower()
        )
        
        # Cevap üretildiyse kullanılan kaynaklar gösterilir.
        if answer["sources"] and not is_unknown_answer:
            with st.expander("📚 Kullanılan Kaynaklar", expanded=True):
                for index, source in enumerate(answer["sources"], start=1):
                    st.caption(f"📚 Kaynak: {index}")
                    st.caption(
                        f"**ID:** {source['id']} | "
                        f"**Skor:** {source['score']:.3f} | "
                        f"**Soru:** {source['question']} | "
                        f"**Cevap:** {source['answer']}"
                    )

    # Asistan cevabı sohbet geçmişine kaydedilir.
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer["answer"],
        "sources": answer["sources"] if not is_unknown_answer else []
    })
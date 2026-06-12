# nodes.py
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI # Import model Gemini
from schemas import MainState, RouteClassifier, TroubleshootingEvaluator

# 1. Pastikan load_dotenv() dipanggil di paling atas sebelum menginisialisasi LLM
load_dotenv()

# 2. Masukkan api_key secara eksplisit ke dalam parameter


# Inisialisasi Gemini Core (Gunakan gemini-1.5-pro untuk reasoning atau gemini-1.5-flash untuk speed)
# Temperature 0 memastikan jawaban teknis mekanik tetap presisi dan konsisten
#llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    model_kwargs={"response_mime_type": "application/json"}
    )
# ==========================================
# 1. NODE: ROUTER UTAMA
# ==========================================
def main_router_node(state: MainState):
    structured_llm = llm.with_structured_output(RouteClassifier)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "- Kamu adalah Router Inteligen untuk Chatbot Mekanik Motor.\n"
                   "- Tugasmu menganalisis input user dan mengarahkannya ke rute yang tepat.\n"
                   "- Rute 'knowledge': Penjelasan part, teori skema (pembakaran, CVT, body, aero).\n"
                   "- Rute 'comparison': Kelebihan/kekurangan motor pabrikan tertentu.\n"
                   "- Rute 'modification': Peningkatan performa, upgrade harian, bore-up.\n"
                   "- Rute 'troubleshooting': Kerusakan motor, mogok, bunyi aneh, solusi perbaikan."),
        ("human", "{user_input}")
    ])
    
    chain = prompt | structured_llm
    result = chain.invoke({"user_input": state["user_input"]})
    
    return {"current_route": result.route}

# ==========================================
# 2. NODE: EVALUATOR TROUBLESHOOTING
# ==========================================
def ts_evaluator_node(state: MainState):
    structured_llm = llm.with_structured_output(TroubleshootingEvaluator)
    
    symptoms = state.get("symptoms") or []
    asked_questions = state.get("asked_questions") or []
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "- Kamu adalah Evaluator Diagnostik Kerusakan Motor Senior.\n"
                   "- Tugasmu menilai apakah info gejala dari user sudah cukup untuk vonis kerusakan.\n"
                   "- Jangan terburu-buru memvonis jika gejala masih terlalu umum (misal: 'motor mati').\n"
                   "- Ajukan pertanyaan taktis terkait komponen fisik (Contoh: warna busi, kondisi kelistrikan, area bunyi).\n"
                   "- Riwayat pertanyaan yang sudah diajukan: {asked_questions}"),
        ("human", "Input User Terbaru: {user_input}\nGejala Teridentifikasi: {symptoms}")
    ])
    
    chain = prompt | structured_llm
    result = chain.invoke({
        "user_input": state["user_input"],
        "symptoms": symptoms,
        "asked_questions": asked_questions
    })
    
    updated_symptoms = symptoms + result.detected_symptoms
    new_questions = list(asked_questions)
    if result.next_question:
        new_questions.append(result.next_question)
        
    return {
        "symptoms": updated_symptoms,
        "asked_questions": new_questions,
        "is_complete": result.is_enough_info,
        "response_data": {
            "status": "interviewing",
            "message": result.next_question if not result.is_enough_info else "Analisis selesai."
        }
    }

# ==========================================
# 3. NODES: WORKER / GENERATOR OUTPUT
# ==========================================
def solve_node(state: MainState):
    """Node andalan untuk memberikan solusi perbaikan final menggunakan Gemini"""
    prompt = f"Berikan solusi perbaikan terstruktur untuk gejala motor berikut: {state['symptoms']}"
    res = llm.invoke(prompt)
    
    return {
        "response_data": {
            "status": "solved",
            "category": "troubleshooting",
            "analysis": f"Berdasarkan keluhan {state['symptoms']}, terjadi indikasi malfungsi komponen.",
            "steps": res.content
        }
    }

def knowledge_node(state: MainState):
    """Menjelaskan detail part dan 4 skema utama motor menggunakan Gemini"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "- Kamu adalah Pakar Mekanik Motor Senior.\n"
                   "- Tugasmu menjelaskan skema kendaraan (pembakaran, penggerakan/CVT, aerodinamik, body) atau fungsi part spesifik secara mendalam, teknis, namun mudah dipahami.\n"
                   "- Berikan penjelasan terstruktur dengan bulleted dashes."),
        ("human", "Jelaskan mengenai hal ini secara detail: {user_input}")
    ])
    
    chain = prompt | llm
    res = chain.invoke({"user_input": state["user_input"]})
    
    return {
        "response_data": {
            "status": "success",
            "category": "knowledge",
            "data": res.content  # Sekarang berisi teks penjelasan detail dari Gemini
        }
    }

def comparison_node(state: MainState):
    """Menjelaskan kelebihan dan kekurangan motor pabrikan"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "- Kamu adalah Reviewer Motor Independen yang objektif.\n"
                   "- Jelaskan kelebihan dan kekurangan produk motor pabrikan yang ditanyakan user.\n"
                   "- Fokus pada realita bengkel (common issue, durabilitas part, kenyamanan).\n"
                   "- Gunakan bulleted dashes."),
        ("human", "Berikan analisis kelebihan dan kekurangan untuk: {user_input}")
    ])
    
    chain = prompt | llm
    res = chain.invoke({"user_input": state["user_input"]})
    
    return {
        "response_data": {
            "status": "success",
            "category": "comparison",
            "data": res.content
        }
    }

def modification_node(state: MainState):
    """Memberikan rekomendasi upgrade dan improvement kendaraan"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "- Kamu adalah Penasihat Modifikasi Performa Motor.\n"
                   "- Berikan rekomendasi improvement/modifikasi (harian/bolt-on atau ekstrem) yang aman dan logis.\n"
                   "- Jelaskan efek samping dari modifikasi tersebut terhadap komponen lain.\n"
                   "- Gunakan bulleted dashes."),
        ("human", "Berikan ide modifikasi/improvement untuk: {user_input}")
    ])
    
    chain = prompt | llm
    res = chain.invoke({"user_input": state["user_input"]})
    
    return {
        "response_data": {
            "status": "success",
            "category": "modification",
            "data": res.content
        }
    }
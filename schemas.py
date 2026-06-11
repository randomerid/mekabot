# schemas.py
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

# ==========================================
# 1. GRAPH STATES
# ==========================================

class MainState(TypedDict):
    user_input: str
    current_route: str
    chat_history: List[dict]
    
    # State untuk Sub-Graph Troubleshooting
    symptoms: List[str]
    asked_questions: List[str]
    is_complete: bool
    
    # Output Akhir
    response_data: dict

# ==========================================
# 2. PYDANTIC MODELS FOR STRUCTURED LLM
# ==========================================

class RouteClassifier(BaseModel):
    """Memaksa LLM memilih satu rute utama"""
    route: Literal["knowledge", "comparison", "modification", "troubleshooting"] = Field(
        description="Klasifikasikan input user ke dalam salah satu rute mekanik yang sesuai."
    )
    reason: str = Field(description="Alasan singkat pemilihan rute.")

class TroubleshootingEvaluator(BaseModel):
    """Memaksa LLM menilai kecukupan data diagnosis"""
    is_enough_info: bool = Field(
        description="Set True jika gejala dan profil motor sudah cukup untuk menentukan akar masalah."
    )
    next_question: Optional[str] = Field(
        description="Jika is_enough_info False, berikan satu pertanyaan spesifik lanjutan untuk cek fisik komponen."
    )
    detected_symptoms: List[str] = Field(
        description="Daftar gejala atau info motor baru yang berhasil divalidasi dari jawaban user."
    )
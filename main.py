# main.py
import uvicorn
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # Tambahkan import ini
from pydantic import BaseModel
from graph import compiled_graph

app = FastAPI(title="MekaBot Core AI Engine")

# --- KONFIGURASI CORS AGAR UI BISA MENGAKSES API ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Mengizinkan semua origin untuk development
    allow_credentials=True,
    allow_methods=["*"],  # Mengizinkan semua method (GET, POST, dll)
    allow_headers=["*"],  # Mengizinkan semua headers
)

# Model request masuk dari user/frontend
class ChatRequest(BaseModel):
    user_input: str
    # Mengirimkan kembali state sebelumnya dari frontend untuk menjaga memory percabangan
    symptoms: list = []
    asked_questions: list = []

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Siapkan payload awal untuk diinput ke LangGraph State
        initial_state = {
            "user_input": request.user_input,
            "symptoms": request.symptoms,
            "asked_questions": request.asked_questions,
            "is_complete": False
        }
        
        # Jalankan LangGraph invoke
        output_state = compiled_graph.invoke(initial_state)
        
        # Kembalikan data respon beserta state terbaru agar frontend bisa menyimpannya
        return {
            "current_route": output_state.get("current_route"),
            "symptoms": output_state.get("symptoms", []),
            "asked_questions": output_state.get("asked_questions", []),
            "is_complete": output_state.get("is_complete", False),
            "response": output_state.get("response_data")
        }
        
    except Exception as e:
       # --- 2. BERSIHKAN MASKING ERROR DAN PRINT DETAILNYA KE TERMINAL ---
        print("\n" + "="*50)
        print("🚨 CRASH TERDETEKSI PADA ENGINE GRAPH BACKEND:")
        print("="*50)
        traceback.print_exc()  # Ini akan mencetak file dan baris spesifik yang rusak
        print("="*50 + "\n")
        
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
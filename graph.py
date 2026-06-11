# graph.py
from langgraph.graph import StateGraph, END
from schemas import MainState
from nodes import (
    main_router_node,
    ts_evaluator_node,
    solve_node,
    knowledge_node,
    comparison_node,
    modification_node
)

# 1. Inisialisasi StateGraph menggunakan skema MainState
workflow = StateGraph(MainState)

# 2. Daftarkan Semua Node ke dalam Graph
workflow.add_node("router", main_router_node)
workflow.add_node("knowledge_node", knowledge_node)
workflow.add_node("comparison_node", comparison_node)
workflow.add_node("modification_node", modification_node)
workflow.add_node("ts_evaluator_node", ts_evaluator_node)
workflow.add_node("solve_node", solve_node)

# 3. Tentukan Entry Point
workflow.set_entry_point("router")

# 4. Definisikan Conditional Edges (Percabangan)
# Fungsi pengecekan rute utama
def route_main(state: MainState):
# Jika user sedang dalam sesi tanya-jawab troubleshooting, kunci jalurnya
    if state.get("symptoms") and not state.get("is_complete"):
        return "troubleshooting"
    
    # Jika chat baru atau tidak sedang troubleshooting, gunakan hasil router LLM
    return state["current_route"]
    
workflow.add_conditional_edges(
    "router",
    route_main,
    {
        "knowledge": "knowledge_node",
        "comparison": "comparison_node",
        "modification": "modification_node",
        "troubleshooting": "ts_evaluator_node"
    }
)

# Fungsi pengecekan loop troubleshooting (interview vs solve)
def route_troubleshoot(state: MainState):
    if state.get("is_complete") is True:
        return "solve"
    return "interview"

workflow.add_conditional_edges(
    "ts_evaluator_node",
    route_troubleshoot,
    {
        "solve": "solve_node",
        "interview": END  # Hentikan sementara untuk menunggu jawaban user berikutnya di API
    }
)

# Hubungkan sisa node worker ke titik akhir (END)
workflow.add_edge("knowledge_node", END)
workflow.add_edge("comparison_node", END)
workflow.add_edge("modification_node", END)
workflow.add_edge("solve_node", END)

# Compile Graph agar siap dieksekusi
compiled_graph = workflow.compile()
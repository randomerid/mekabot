---
title: "MEKABOT"
date: 2026-06-13
---

# Mekabot
Program chatbot yang diperuntukan untuk mekanik dalam menangani permasalahan di kendaraan khususnya sepeda motor.
Teknologi yang digunakan untuk pendekatannya yaitu menggunakan RAG dan Agentic Workflow

## Fitur 
Mekabot memiliki beberapa fitur :
* **Menjelaskan Part dan Skema kendaraan** (Knowledge Base RAG)
* **Kelebihan dan kekurangan Produk pabrikan** (Comparison Engine)
* **Improvement & Modifikasi** (Rekomendation Agent)
* **Diagnosis & Perbaikan Kerusakan** Fitur andalan (Stateful Traubleshooting)

## Skema
Workflow
                    [ User Input ]
                            │
                            ▼
                    [ Conditional Router ]
                            │
      ┌─────────────────────┼─────────────────────┬─────────────────────┐
      ▼                     ▼                     ▼                     ▼
[Route: Knowledge]  [Route: Comparison]   [Route: Modif/Improv]  [Route: Troubleshoot]
  - Skema Motor       - Kelebihan Motor     - Upgrade Bolt-on      - State 1: Interview
  - Penjelasan Part   - Kekurangan Motor    - Bore-up / Remap      - State 2: Solusi Step-by-Step
      │                     │                     │                     │
      └─────────────────────┴─────────────────────┼─────────────────────┘
                                                  ▼
                                            [ Generate JSON ]

## Implementasi

* file .env berisi : **GOOGLE_API_KEY=**
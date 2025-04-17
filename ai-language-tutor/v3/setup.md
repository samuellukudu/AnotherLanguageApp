┌─────────┐       HTTPS       ┌─────────────┐       → OpenAI API / fine‑tuned GPT  
│ Browser │ ───────────────── │  FastAPI    │ ───────────────────────────────→ LLM  
│ (React) │                   │  Backend    │  
└─────────┘                   └─────────────┘  
    ↓                              │  
 WebSockets                        ↓  
(for simulation)             PostgreSQL  
                              (JSONB storage)  

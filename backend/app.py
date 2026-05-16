from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
import pandas as pd
import io
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/analyze")
async def analyze(file: UploadFile = File(...), question: str = Form(...)):
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    csv_preview = df.head(20).to_string()
    stats = df.describe().to_string()

    prompt = f"""You are a data analyst agent. Here is a CSV dataset:

PREVIEW (first 20 rows):
{csv_preview}

STATISTICS:
{stats}

COLUMNS: {list(df.columns)}
TOTAL ROWS: {len(df)}

User question: {question}

Answer clearly and helpfully. If relevant, suggest what chart would best visualize this."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024
    )
    return {
        "answer": response.choices[0].message.content,
        "rows": len(df),
        "columns": list(df.columns)
    }
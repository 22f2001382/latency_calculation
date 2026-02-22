from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST"],
    allow_headers=["*"],
)

# ✅ Load once (important for Vercel)
df = pd.read_json('q-vercel-latency.json')

class SampleRequest(BaseModel):
    regions: list[str]
    threshold_ms: int


@app.post('/')
def calculate_metrics(payload: SampleRequest):
    regions = payload.regions
    threshold = payload.threshold_ms
    result = {}

    for region in regions:
        filtered_df = df[df['region'] == region]

        if filtered_df.empty:
            continue

        average_latency = float(filtered_df['latency_ms'].mean())
        percentile_95 = float(np.percentile(filtered_df['latency_ms'], 95))
        average_uptime = float(filtered_df['uptime_pct'].mean())
        record_count = int((filtered_df['latency_ms'] > threshold).sum())

        result[region] = {
            "avg_latency": average_latency,
            "p95_latency": percentile_95,
            "avg_uptime": average_uptime,
            "breaches": record_count
        }

    return result


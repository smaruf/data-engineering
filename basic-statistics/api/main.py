"""
FastAPI application for statistics as a service.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.python.descriptive import CentralTendency, Dispersion, Shape
from src.python.probability import Distributions

app = FastAPI(
    title="Basic Statistics API",
    description="Statistical computations as a service",
    version="1.0.0"
)

class DataInput(BaseModel):
    """Input model for statistical computations."""
    data: List[float]
    
class DescriptiveStatsResponse(BaseModel):
    """Response model for descriptive statistics."""
    mean: float
    median: float
    std_dev: float
    variance: float
    min: float
    max: float
    range: float
    iqr: float
    skewness: float
    kurtosis: float

class DistributionRequest(BaseModel):
    """Request for distribution computations."""
    distribution: str
    x: float
    params: dict

@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "message": "Basic Statistics API",
        "version": "1.0.0",
        "endpoints": {
            "descriptive": "/stats/descriptive",
            "distributions": "/stats/distribution",
            "health": "/health"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.post("/stats/descriptive", response_model=DescriptiveStatsResponse)
def compute_descriptive_stats(data_input: DataInput):
    """
    Compute comprehensive descriptive statistics.
    
    - **data**: List of numerical values
    
    Returns all major descriptive statistics.
    """
    try:
        data = data_input.data
        
        if len(data) == 0:
            raise HTTPException(status_code=400, detail="Data cannot be empty")
        
        return DescriptiveStatsResponse(
            mean=CentralTendency.mean(data),
            median=CentralTendency.median(data),
            std_dev=Dispersion.std_dev(data),
            variance=Dispersion.variance(data),
            min=float(min(data)),
            max=float(max(data)),
            range=Dispersion.range(data),
            iqr=Dispersion.iqr(data),
            skewness=Shape.skewness(data),
            kurtosis=Shape.kurtosis(data)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stats/mean")
def compute_mean(data_input: DataInput):
    """Compute mean of data."""
    try:
        return {"mean": CentralTendency.mean(data_input.data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stats/median")
def compute_median(data_input: DataInput):
    """Compute median of data."""
    try:
        return {"median": CentralTendency.median(data_input.data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stats/variance")
def compute_variance(data_input: DataInput):
    """Compute variance of data."""
    try:
        return {"variance": Dispersion.variance(data_input.data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/distribution/normal/pdf")
def normal_pdf(request: DistributionRequest):
    """
    Calculate Normal distribution PDF.
    
    Params should include: mu, sigma
    """
    try:
        mu = request.params.get("mu", 0)
        sigma = request.params.get("sigma", 1)
        result = Distributions.Normal.pdf(request.x, mu, sigma)
        return {"pdf": float(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/distribution/normal/cdf")
def normal_cdf(request: DistributionRequest):
    """
    Calculate Normal distribution CDF.
    
    Params should include: mu, sigma
    """
    try:
        mu = request.params.get("mu", 0)
        sigma = request.params.get("sigma", 1)
        result = Distributions.Normal.cdf(request.x, mu, sigma)
        return {"cdf": float(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

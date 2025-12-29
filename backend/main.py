"""
TapQuote FastAPI Backend
Main application entry point with API endpoints
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io

from config import OPENAI_API_KEY, LABOR_RATE, MATERIAL_MARKUP
from agent import generate_quote, generate_mock_quote
from pdf_generator import generate_pdf
from materials import get_all_materials, search_materials


# Initialize FastAPI app
app = FastAPI(
    title="TapQuote API",
    description="AI-powered quote generation for electricians",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class QuoteRequest(BaseModel):
    job_description: str
    customer_name: str = "Customer"


class QuoteResponse(BaseModel):
    success: bool
    quote: dict | None = None
    error: str | None = None


class PDFRequest(BaseModel):
    quote: dict


# Health check endpoint
@app.get("/")
async def root():
    return {
        "service": "TapQuote API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


# Configuration endpoint
@app.get("/config")
async def get_config():
    """Return current pricing configuration."""
    return {
        "labor_rate": LABOR_RATE,
        "material_markup": MATERIAL_MARKUP,
        "api_configured": bool(OPENAI_API_KEY)
    }


# Materials endpoint
@app.get("/materials")
async def list_materials():
    """List all available materials."""
    return {
        "materials": get_all_materials(),
        "count": len(get_all_materials())
    }


@app.get("/materials/search")
async def search_materials_endpoint(q: str):
    """Search materials by keyword."""
    results = search_materials(q)
    return {
        "query": q,
        "results": results,
        "count": len(results)
    }


# Quote generation endpoint
@app.post("/generate-quote", response_model=QuoteResponse)
async def generate_quote_endpoint(request: QuoteRequest):
    """
    Generate a quote from a job description.
    Uses OpenAI API if configured, otherwise falls back to mock.
    """
    try:
        if not request.job_description.strip():
            raise HTTPException(status_code=400, detail="Job description is required")
        
        # Use real LLM if API key is configured, otherwise mock
        if OPENAI_API_KEY:
            quote = await generate_quote(
                job_description=request.job_description,
                customer_name=request.customer_name
            )
        else:
            # Use mock for testing
            quote = generate_mock_quote(
                job_description=request.job_description,
                customer_name=request.customer_name
            )
        
        if "error" in quote:
            return QuoteResponse(
                success=False,
                error=quote.get("error")
            )
        
        return QuoteResponse(
            success=True,
            quote=quote
        )
        
    except Exception as e:
        return QuoteResponse(
            success=False,
            error=str(e)
        )


# PDF generation endpoint
@app.post("/download-pdf")
async def download_pdf(request: PDFRequest):
    """
    Generate and download a PDF from quote data.
    """
    try:
        if not request.quote:
            raise HTTPException(status_code=400, detail="Quote data is required")
        
        # Generate PDF
        pdf_bytes = generate_pdf(request.quote)
        
        # Return as downloadable file
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=quote_{request.quote.get('customer_name', 'customer').replace(' ', '_')}.pdf"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

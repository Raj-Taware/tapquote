"""
TapQuote LangChain Agent
Handles AI-powered quote generation with material retrieval and calculation
"""
import json
from typing import Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from config import OPENAI_API_KEY, OPENAI_MODEL, LABOR_RATE, MATERIAL_MARKUP
from materials import search_materials, get_all_materials


# Pydantic models for structured output
class QuoteItem(BaseModel):
    description: str = Field(description="Description of the work item")
    qty: int = Field(description="Quantity of items", default=1)
    unit_material_cost: float = Field(description="Cost per unit after markup")
    estimated_hours: float = Field(description="Estimated labor hours")
    labor_cost: float = Field(description="Labor cost (hours * rate)")
    line_total: float = Field(description="Total for this line item")
    is_estimate: bool = Field(description="True if price is estimated (not from database)", default=False)


class Quote(BaseModel):
    customer_name: str = Field(description="Customer name", default="Customer")
    job_summary: str = Field(description="Brief summary of the job")
    items: list[QuoteItem] = Field(description="List of quote line items")
    subtotal: float = Field(description="Subtotal before tax")
    tax: float = Field(description="Tax amount (GST)")
    grand_total: float = Field(description="Grand total including tax")


def retrieve_materials(job_description: str) -> str:
    """
    Search materials database and return formatted string for LLM context.
    This is the 'Retriever' component of the RAG pattern.
    """
    # Extract key terms and search
    materials_found = []
    
    # Get all materials for reference
    all_materials = get_all_materials()
    
    # Search based on job description
    search_results = search_materials(job_description)
    
    if search_results:
        materials_found = search_results[:10]  # Top 10 matches
    
    # Format for LLM
    if not materials_found:
        return "No exact matches found in database. Use realistic market estimates and flag as estimates."
    
    formatted = "Available Materials (with base costs before markup):\n"
    for mat in materials_found:
        formatted += f"- {mat['name']} (SKU: {mat['sku']}): ${mat['base_cost']:.2f}\n"
    
    return formatted


def calculate_pricing(base_cost: float, quantity: int, labor_hours: float) -> dict:
    """
    Apply markup and labor rate to calculate final pricing.
    This is the 'Calculator' component.
    """
    # Apply markup to materials
    material_with_markup = base_cost * (1 + MATERIAL_MARKUP / 100)
    material_total = material_with_markup * quantity
    
    # Calculate labor
    labor_cost = labor_hours * LABOR_RATE
    
    # Line total
    line_total = material_total + labor_cost
    
    return {
        "unit_cost_with_markup": round(material_with_markup, 2),
        "material_total": round(material_total, 2),
        "labor_cost": round(labor_cost, 2),
        "line_total": round(line_total, 2)
    }


async def generate_quote(job_description: str, customer_name: str = "Customer") -> dict:
    """
    Main quote generation function using LangChain.
    """
    # Step 1: Retrieve relevant materials
    materials_context = retrieve_materials(job_description)
    
    # Step 2: Create LLM chain
    llm = ChatOpenAI(
        model=OPENAI_MODEL,
        api_key=OPENAI_API_KEY,
        temperature=0.2
    )
    
    # System prompt as per PRD
    system_prompt = """You are the TapQuote Estimator, an expert electrical quantity surveyor.

Configuration:
- Labor Rate: ${labor_rate}/hour
- Material Markup: {markup}%

{materials_context}

Your task is to analyze the job description and create a detailed quote.

Instructions:
1. Break the job into distinct line items (each task/installation is a separate item)
2. For each item, identify the materials needed from the database
3. If a material is not in the database, use a realistic market estimate and set is_estimate to true
4. Estimate reasonable labor hours for each task (typical: GPO install 0.5hr, downlight 0.75hr, circuit run 2-3hr)
5. Calculate costs using:
   - unit_material_cost = base_cost * (1 + markup/100)
   - labor_cost = estimated_hours * labor_rate
   - line_total = (unit_material_cost * qty) + labor_cost
6. Calculate totals:
   - subtotal = sum of all line_totals
   - tax = subtotal * 0.10 (10% GST)
   - grand_total = subtotal + tax

Return a valid JSON object matching the schema exactly."""

    user_prompt = """Job Description: {job_description}

Customer Name: {customer_name}

Generate a complete quote as JSON with this exact structure:
{{
    "customer_name": "string",
    "job_summary": "string",
    "items": [
        {{
            "description": "string",
            "qty": number,
            "unit_material_cost": number,
            "estimated_hours": number,
            "labor_cost": number,
            "line_total": number,
            "is_estimate": boolean
        }}
    ],
    "subtotal": number,
    "tax": number,
    "grand_total": number
}}"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", user_prompt)
    ])
    
    # Format the prompt
    formatted_prompt = prompt.format_messages(
        labor_rate=LABOR_RATE,
        markup=MATERIAL_MARKUP,
        materials_context=materials_context,
        job_description=job_description,
        customer_name=customer_name
    )
    
    # Step 3: Get LLM response
    response = await llm.ainvoke(formatted_prompt)
    
    # Step 4: Parse JSON from response
    try:
        # Clean the response - extract JSON
        content = response.content
        
        # Find JSON in response
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        
        if start_idx != -1 and end_idx > start_idx:
            json_str = content[start_idx:end_idx]
            quote_data = json.loads(json_str)
            return quote_data
        else:
            raise ValueError("No JSON found in response")
            
    except json.JSONDecodeError as e:
        # Return error structure
        return {
            "error": f"Failed to parse quote: {str(e)}",
            "raw_response": response.content
        }


def generate_mock_quote(job_description: str, customer_name: str = "Customer") -> dict:
    """
    Generate a mock quote for testing without OpenAI API.
    """
    # Simple parsing for demo
    items = []
    
    # Check for common items in description
    desc_lower = job_description.lower()
    
    if "downlight" in desc_lower or "led" in desc_lower:
        qty = 4  # Default
        for word in job_description.split():
            if word.isdigit():
                qty = int(word)
                break
        
        pricing = calculate_pricing(25.00, qty, 0.75 * qty)
        items.append({
            "description": f"LED Downlight 10W installation (supply & fit)",
            "qty": qty,
            "unit_material_cost": 30.00,  # After 20% markup
            "estimated_hours": 0.75 * qty,
            "labor_cost": pricing["labor_cost"],
            "line_total": pricing["line_total"],
            "is_estimate": False
        })
    
    if "gpo" in desc_lower or "outlet" in desc_lower or "power point" in desc_lower:
        pricing = calculate_pricing(12.50, 1, 0.5)
        items.append({
            "description": "Clipsal Double GPO 10A installation",
            "qty": 1,
            "unit_material_cost": 15.00,  # After 20% markup
            "estimated_hours": 0.5,
            "labor_cost": pricing["labor_cost"],
            "line_total": pricing["line_total"],
            "is_estimate": False
        })
    
    if "circuit" in desc_lower or "20a" in desc_lower or "pool" in desc_lower:
        # Pool pump circuit
        pricing_breaker = calculate_pricing(18.00, 1, 0.25)
        pricing_cable = calculate_pricing(5.50, 15, 1.5)  # 15m of 4mm cable
        pricing_isolator = calculate_pricing(45.00, 1, 0.5)
        
        total_labor = 2.5  # hours
        total_material = (18.00 * 1.2) + (5.50 * 15 * 1.2) + (45.00 * 1.2)
        labor_cost = total_labor * LABOR_RATE
        
        items.append({
            "description": "20A Circuit for pool pump (inc. breaker, 4mm cable 15m, isolator)",
            "qty": 1,
            "unit_material_cost": round(total_material, 2),
            "estimated_hours": total_labor,
            "labor_cost": labor_cost,
            "line_total": round(total_material + labor_cost, 2),
            "is_estimate": False
        })
    
    # If no items detected, add a generic one
    if not items:
        items.append({
            "description": "Electrical work as described",
            "qty": 1,
            "unit_material_cost": 50.00,
            "estimated_hours": 1.0,
            "labor_cost": LABOR_RATE,
            "line_total": 50.00 + LABOR_RATE,
            "is_estimate": True
        })
    
    # Calculate totals
    subtotal = sum(item["line_total"] for item in items)
    tax = round(subtotal * 0.10, 2)
    grand_total = round(subtotal + tax, 2)
    
    return {
        "customer_name": customer_name,
        "job_summary": job_description[:100] + "..." if len(job_description) > 100 else job_description,
        "items": items,
        "subtotal": round(subtotal, 2),
        "tax": tax,
        "grand_total": grand_total
    }

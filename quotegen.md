Product Requirements Document (PRD)

Project Name:TapQuote MVP (Electrician Edition) Version: 1.0 Date:
October 26, 2023 Status:

Draft

1\. ExecutiveSummary

TapQuote is an AI-powered estimation platform tailored for tradespeople,
launching with an

initial focus on electricians.The goal of the MVP is to demonstrate a
seamless "Text-to-Quote"

workflow where natural language job descriptions are converted into
accurate, branded PDF

quotes using a user's specific labor rates and material costs.

2\. ProblemStatement

Tradespeople spend hours manually calculating line items, looking up
supplier prices, and

formatting quotes inWord or Excel.This leads to lost billable hours and
inconsistent pricing.

3.CoreObjectives

> 1\. Automation: Reduce quote creation time from ~30 minutes to \<1
> minute.
>
> 2\. Accuracy: Ensure quotes reference actual supplier pricing and
> user-defined margins.
>
> 3\. Usability: Provide a simple interface requiring no technical
> knowledge to operate.

4.User Flow & Features

4.1 Onboarding & Configuration

> User Login: Standard email/password or SSO.
>
> Business Profile:
>
> Input: Business Name, Logo Upload, Address,Tax ID.
>
> Pricing Configuration (The "Brain"):
>
> Input: Hourly Labor Rate (e.g., \$85/hr).
>
> Input: Material Markup Percentage (e.g., 20%).

4.2 Data Ingestion (Context)

> Supplier Data: User connects or uploads a dataset of materials
> (CSV/Airtable).
>
> *MVP* *Scope:* Pre-loaded "Common Electrical Items" list hosted in
> Airtable.
>
> Integration: System indexes these items for retrieval by the AI.

4.3 Quote Generation (The Core Loop)

> 1\. Input: User enters a natural language description.
>
> *Example:* "Install 4 LED downlights in the kitchen, supply and fit
> new Clipsal double
>
> GPO in the bedroom, and run a new 20A circuit for the pool pump."
>
> 2\. AI Processing (LangChain):
>
> Intent Extraction: Parses the text into specific tasks.
>
> RAG (Retrieval): Searches the database for "LED Downlight," "Double
> GPO," "20A
>
> Breaker," and "2.5mm Cable."
>
> Calculation:
>
> Retrieves base cost.
>
> Applies 20% Markup.
>
> Estimates Labor Hours per task.
>
> Calculates LineTotal.
>
> 3\. Review: User sees a draft quote on screen and can edit quantities
> or prices manually.

4.4 Output

> PDF Generation: One-click generation of a branded PDF containing:
>
> Header (Logo/Business Info).
>
> Customer Details.
>
> Line Items table (Description, Qty, Unit Price,Total).
>
> Totals (Subtotal,Tax, GrandTotal).

5.TechnicalArchitecture

5.1Technology Stack

> Frontend: CustomWeb App (React/Next.js or Streamlit for rapid
> prototyping).
>
> Database: Airtable (Acting as the CMS for User Profiles and Material
> Pricing).
>
> Orchestration: LangChain (Python/JS).
>
> LLM: OpenAI API (GPT-4 or GPT-3.5-Turbo).
>
> PDF Engine: ReportLab (Python) or pdfmake (JS).

5.2 AI Logic (LangChain Agent)

The system will utilize a Retrieval-Augmented Generation (RAG) pattern.

> 1\. Vector Store/Search: A semantic search layer over the Airtable
> data to match "outlet" to
>
> "Clipsal Double GPO 10A".
>
> 2\. Logic Chain:
>
> Input -\> Keyword Search -\> Retrieve Prices -\> Inject into Prompt
> -\> LLM
>
> Processing -\> Structured JSON Output .

6\. Functional Requirements

> ID Feature
>
> FR- Profile Config 01
>
> FR- Material Lookup 02
>
> FR- Hallucination 03 Control
>
> FR- PDF Export 04
>
> FR- Editability
>
> 05

Description

User must be able to save global labor rates and markup % persistently.

System must fuzzy-match user text to specific database SKUs.

If a price is not found, the AI must explicitly label the item as
"Estimate Only."

Generated PDF must look professional and include the user's logo.

User must be able to edit theJSON/Draft before finalizing

the PDF.

Priority

P0

P0

P1

P0

P1

7.Appendix:TheAISystem Prompt

Role:You are theTapQuote Estimator, an expert electrical quantity
surveyor.

Input Context:

> Labor Rate: {labor_rate}
>
> Markup: {markup_percentage}
>
> Material Database Matches: {retrieved_material_data}

Task: Analyze the followingJob Description: "{user_job_description}"

Instructions:

> 1\. IdentifyTasks: Break the job down into distinct line items.
>
> 2\. Match Materials: Use the *Material* *Database* *Matches* provided.
> Do not invent prices. If a
>
> price is missing, use a realistic market estimate and flag it.
>
> 3\. Calculate:
>
> Item Price = Base Cost \* (1 + (Markup / 100))
>
> Labor Cost = Estimated Hours \* Labor Rate
>
> Total = (Item Price \* Qty) + Labor Cost
>
> 4\. Format: Return pureJSON matching the schema below.

JSON Schema:

> {
>
> "customer_name": "Unknown", "job_summary": "String", "items": \[
>
> {
>
> "description": "String", "qty": 1, "unit_material_cost": 0.00,
> "estimated_hours": 0.00, "final_line_price": 0.00
>
> } \],
>
> "grand_total": 0.00 }

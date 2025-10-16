# Campus Social Media Insights - Multi-Agent Validation System

Three-agent CrewAI system that validates data completeness, generates insights, and fact-checks results for 20 university campuses. Built with Claude Sonnet 4.5 for Spanish insights with automated quality assurance.

---

## What This Does

Takes 3 preprocessed JSON files → Validates all 20 campuses have complete data → Generates insights for each campus → Fact-checks every claim against source data → Outputs validation, insights, and quality reports.

**Input:** 3 structured JSON files (metrics, publications, scores)  
**Output:** 3 JSON reports (validation, insights, quality) with automated error detection

---

## Architecture

### Three-Agent Pipeline

1. **Agent 1: Data Validator**
   - Checks all 20 campuses have data in all 3 files
   - Validates field presence and completeness
   - Outputs: `validation_report.json`

2. **Agent 2: Insight Generator**
   - Generates one insight per campus (20 total)
   - Calculates percentage changes from actual data
   - Uses only category labels (no numeric scores)
   - Outputs: `insights_report.json`

3. **Agent 3: Quality Checker**
   - Fact-checks all 20 insights against source data
   - Flags percentage errors, wrong categories, invented data
   - Calculates accuracy rate
   - Outputs: `quality_report.json`

**Process:** Sequential with context passing (Agent 2 gets Agent 1's output, Agent 3 gets Agent 2's output)

---

## Tech Stack

- **Python 3.10+** (Jupyter Notebook)
- **CrewAI** - Multi-agent orchestration
- **Claude Sonnet 4.5** - All 3 agents
- **Pydantic** - Structured outputs
- **JSON processing** - Data validation

---

## Project Structure

```
.
├── preprocess_metrics.py          # Custom preprocessing for metrics
├── preprocess_publications.py      # Custom preprocessing for publications  
├── preprocess_sdm.py              # Custom preprocessing for SDM scores
├── schemas.py                     # Pydantic schemas (unique to this system)
├── mainpy.ipynb                   # Main Jupyter notebook
├── .env                           # API keys
└── README.md
```

**Note:** The preprocessing scripts and schemas for this version are different from other implementations - don't mix them.

---

## Setup

### 1. Install Dependencies

```bash
pip install crewai python-dotenv anthropic
```

### 2. Configure API Key

Create `.env` file:

```
ANTHROPIC_API_KEY=your_key_here
```

### 3. Prepare Input Files

Place these in the project root:
- `Mes_Actual_2_SDMxRegion.json`
- `Mes_del_A_o_anterior_3_SDMxRegion.json`
- `Todas_las_publicaciones_con_sus_metricas_1_SDMxRegion.json`
- `Regiones Unificadas - Valores.csv`

---

## Usage

### Option 1: Run Everything (Recommended)

Open `mainpy.ipynb` in Jupyter and run all cells in order.

### Option 2: Step by Step

**Step 1: Preprocess Data**

```python
!python preprocess_metrics.py
!python preprocess_sdm.py
!python preprocess_publications.py
```

**Outputs:**
- `metrics_estructurado.json`
- `sdm_estructurado.json`
- `Publicaciones_estructuradas_Top8.json` (JSONL format)

**Step 2: Run Multi-Agent System**

Execute the main crew cell. Takes ~10-15 minutes.

**Outputs:**
- `validation_report.json` - Data completeness for 20 campuses
- `insights_report.json` - 20 campus insights in Spanish
- `quality_report.json` - Fact-check results with error flagging

---

## How It Works

### Agent 1: Data Validator

**Goal:** Verify all 20 campuses have complete data

**Process:**
1. Loads all 3 JSON files
2. Extracts campus_id from each
3. Checks each campus exists in all 3 files
4. Validates required fields are present
5. Reports complete vs incomplete campuses

**Output Structure:**
```json
{
  "total_campuses": 20,
  "complete_campuses": 18,
  "incomplete_campuses": 2,
  "validations": [
    {
      "campus_id": "MTY",
      "has_publications": true,
      "has_metrics": true,
      "has_scores": true,
      "is_complete": true
    }
  ]
}
```

---

### Agent 2: Insight Generator

**Goal:** Generate 20 insights using ONLY actual data

**Process:**
1. Takes validated data from Agent 1
2. For each campus:
   - Calculates real percentages from current vs previous year
   - Extracts publication themes from top posts
   - Uses ONLY category words (excepcional/sobresaliente/satisfactorio/regular/deficiente)
   - Never shows numeric scores
3. Outputs 20 structured insights

**Insight Format:**
```
Campus [NOMBRE COMPLETO]

En agosto 2025, el campus [nombre] presentó un desempeño [categoría]. 
La visibilidad fue [categoría] y la resonancia [categoría]. 
El alcance [aumentó/disminuyó] un [X.X]% y las interacciones [aumentaron/disminuyeron] un [X.X]% respecto al mismo mes del año anterior.

Entre las publicaciones destacadas se encuentran: [temas reales].

Los comentarios [aumentaron/disminuyeron] un [X.X]% con respecto al año anterior.
```

**Critical Rules:**
- NEVER show numbers like "(83 puntos)" or "(175 puntos)"
- ONLY use category labels
- Calculate percentages from actual JSON data
- Mention real publication content

---

### Agent 3: Quality Checker

**Goal:** Catch every inaccuracy in all 20 insights

**Process:**
1. Takes insights from Agent 2
2. For each insight:
   - Extracts every numeric claim
   - Recalculates percentages from source data
   - Verifies categories match actual data
   - Checks publication themes exist in top_8_posts
   - Flags errors with severity levels
3. Calculates overall accuracy rate

**Error Types Flagged:**
- `percentage_error` - Percentage off by >3%
- `score_error` - Numeric scores shown (shouldn't appear)
- `publication_mismatch` - Invented publication themes
- `categoria_mismatch` - Wrong category label

**Severity Levels:**
- `critical` - Invented data or major errors
- `high` - Percentage off by >5%
- `medium` - Category mismatch
- `low` - Minor inconsistencies

**Output Structure:**
```json
{
  "total_campuses_checked": 20,
  "accurate_campuses": 18,
  "campuses_with_errors": 2,
  "total_issues_found": 5,
  "overall_accuracy_rate": 90.0,
  "campus_checks": [
    {
      "campus_id": "MTY",
      "is_accurate": false,
      "verified_claims": 8,
      "total_claims": 10,
      "issues_found": [
        {
          "issue_type": "percentage_error",
          "incorrect_statement": "alcance aumentó 76.9%",
          "correct_information": "alcance aumentó 82.23%",
          "severity": "high"
        }
      ]
    }
  ]
}
```

---

## Configuration

### Campus List

20 campuses validated (MTY, GDL, PUE, CDJ, TOL, CCM, CEM, QRO, CHI, SIN, AGS, COB, LEO, LAG, SON, HGO, SLP, CVA, CSF, SAL)

Defined in preprocessing scripts - don't modify unless you know what you're doing.

### Analysis Period

Currently set to **Agosto 2025**

Change in notebook:
```python
result = crew.kickoff(inputs={
    'month': 'agosto',  # Change here
    'year': 2025
})
```

### Error Tolerance

Quality checker flags percentage errors >3% deviation.

Modify in agent backstory if you want different tolerance.

---

## Token Usage & Cost

**Per full run (3 agents × 20 campuses):**
- Agent 1 (Validator): ~10K tokens
- Agent 2 (Insights): ~100K tokens (20 insights)
- Agent 3 (Quality): ~50K tokens (fact-checking)
- **Total: ~160K tokens**
- **Cost: ~$0.80** (Claude Sonnet 4.5)

**Runtime:** 10-15 minutes for complete validation + insight + quality check

---

## Output Files

### validation_report.json
Data completeness status for all 20 campuses. Shows which campuses have missing data.

### insights_report.json
20 campus insights in Spanish with calculated metrics and publication analysis.

### quality_report.json
Fact-check results showing accuracy rate, error locations, and severity levels.

**All reports include metadata (timestamp, totals, summaries).**

---

## Troubleshooting

### "Fewer than 20 insights generated"

Agent 2 stopped early. Check:
1. All 20 campuses have data in input files
2. `max_iter=3` is sufficient (increase if needed)
3. Task description says "ALL 20" explicitly

### "Empty issues_found array but errors mentioned"

Agent 3 found errors but didn't populate the array. This is a known issue with Pydantic validation. Re-run or check task output manually.

### "Wrong campus_ids in validation"

Agent 1 modified IDs (CVA→CCV, GDL→CGD). Fix:
- Add explicit ID mapping in task description
- Use EXACT IDs from source files

### "Publications file not loading"

`Publicaciones_estructuradas_Top8.json` is JSONL format (one object per line), not standard JSON. Make sure you're reading it line-by-line.

---

## Design Decisions

**Why 3 agents instead of 1?**  
Separation of concerns. Validation catches missing data, insights focus on analysis, quality ensures accuracy. Cleaner outputs, better debugging.

**Why fact-check insights with Agent 3?**  
LLMs hallucinate. Agent 2 might invent percentages or publication themes. Agent 3 catches this automatically.

**Why sequential process?**  
Agent 2 needs validation results. Agent 3 needs insights. Can't parallelize - each agent depends on the previous.

**Why Claude Sonnet 4.5 for all agents?**  
Need consistent quality across validation, generation, and fact-checking. Haiku would be cheaper but less reliable for complex tasks.

**Why Jupyter notebook?**  
Easier to run cells independently, inspect intermediate outputs, and debug issues per agent.

---

## Known Issues

1. **Agent 2 sometimes stops at 10-15 insights** - Increase `max_iter` or add explicit counting logic
2. **Agent 3 may miss errors in issues_found** - Pydantic validation issue, manual review recommended
3. **Publications file format (JSONL)** - Different from other JSON files, easy to forget

---

## Future Improvements

- Add retry logic for incomplete insight generation
- Implement automated fixes for flagged errors
- Add comparative analysis across campuses
- Export to PDF/Markdown format

---

## Notes

- All insights in Spanish
- Designed for university social media teams
- Automated quality assurance reduces manual review time
- Three-stage validation ensures data accuracy

---

**Questions?** Check the agent backstories in the notebook - they contain detailed instructions for each step.
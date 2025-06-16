import tempfile
import streamlit as st

from agno.agent import Agent
from agno.media import Image
from agno.models.openai import OpenAIChat
from agno.tools.serpapi import SerpApiTools

from pydantic import BaseModel, Field
from typing import List, Literal
from textwrap import dedent

class WaterVisualAnalysisOutput(BaseModel):
    detected_features: List[str] = Field(..., description="List of visible signs of contamination")
    contamination_level: Literal["Low", "Moderate", "High"] = Field(..., description="Severity based on visual indicators")
    likely_risks: List[str] = Field(..., description="Possible health/environmental risks inferred from visual inspection")

class ContaminationCause(BaseModel):
    type: str = Field(..., description="Contamination category, e.g., Biological, Chemical, Vector-borne")
    source: str = Field(..., description="Probable visible indicator or origin, e.g., murkiness, algae, sediment")
    risk_level: str = Field(..., description="Estimated risk: Low, Moderate, or High")

class WaterContaminationDiagnosis(BaseModel):
    summary: str = Field(..., description="Concise overview of the contamination situation")
    severity: str = Field(..., description="Overall severity: Low, Moderate, or High")
    contamination_causes: List[ContaminationCause] = Field(..., description="Identified types of contamination and associated risks")
    action_note: str = Field(..., description="A neutral, non-instructional remark that summarizes urgency or concern level")

def water_visual_output_to_string(output: WaterVisualAnalysisOutput) -> str:
    features = ", ".join(output.detected_features)
    risks = ", ".join(output.likely_risks)

    return f"""🔍 **Visual Water Inspection Summary**

**Detected Contaminants**: {features}  
**Contamination Level**: `{output.contamination_level}`  
**Likely Risks**: {risks}
"""

def water_diagnosis_to_string(diagnosis: WaterContaminationDiagnosis) -> str:
    lines = []

    lines.append("🧪 **Water Contamination Diagnosis**")
    lines.append("")
    lines.append(f"**Summary**: {diagnosis.summary}")
    lines.append(f"**Severity**: `{diagnosis.severity}`")
    lines.append("")

    lines.append("🔬 **Identified Contamination Causes:**")
    for cause in diagnosis.contamination_causes:
        lines.append(f"- **Type**: {cause.type}")
        lines.append(f"  • Source: {cause.source}")
        lines.append(f"  • Risk Level: `{cause.risk_level}`")
        lines.append("")

    lines.append(f"⚠️ **Note**: {diagnosis.action_note}")
    return "\n".join(lines)

def render_sidebar():
    st.sidebar.title("🔐 API Configuration")
    st.sidebar.markdown("---")

    # OpenAI API Key input
    openai_api_key = st.sidebar.text_input(
        "OpenAI API Key",
        type="password",
        help="Don't have an API key? Get one [here](https://platform.openai.com/account/api-keys)."
    )
    if openai_api_key:
        st.session_state.openai_api_key = openai_api_key
        st.sidebar.success("✅ OpenAI API key updated!")

    # SerpAPI Key input
    serp_api_key = st.sidebar.text_input(
        "Serp API Key",
        type="password",
        help="Don't have an API key? Get one [here](https://serpapi.com/manage-api-key)."
    )
    if serp_api_key:
        st.session_state.serp_api_key = serp_api_key
        st.sidebar.success("✅ Serp API key updated!")

    st.sidebar.markdown("---")

def render_water_quality_inputs():
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    # Column 1: Image Upload
    with col1:
        st.subheader("📷 Upload Water Photo")
        uploaded_image = st.file_uploader(
            "Upload a clear image of water in a container or surface body",
            type=["jpg", "jpeg", "png"]
        )

    # Column 2: Water Source Information
    with col2:
        st.subheader("🚰 Water Source Details")

        water_source_type = st.selectbox(
            "Where is this water from?",
            ["Tap", "Hand Pump", "Well", "River/Pond", "Stored Tank", "Bottle", "Other"], index=None
        )

        water_usage = st.selectbox(
            "What is this water used for?",
            ["Drinking", "Cooking", "Bathing", "Cleaning", "Irrigation", "Livestock", "Other"], index=None
        )

        surrounding_area = st.selectbox(
            "What surrounds the water source?",
            ["Urban", "Rural", "Industrial", "Agricultural", "Natural", "Unknown"], index=None
        )

    # Column 3: User Observation & Preferences
    with col3:
        st.subheader("🔍 Additional Details")

        noticed_issues = st.multiselect(
            "Have you noticed any of these?",
            [
                "Unusual smell", "Color change", "Floating particles",
                "Mosquito larvae", "Oil sheen", "No visible issue"
            ]
        )

        purification_possible = st.selectbox(
            "Are you open to purifying this water?",
            ["Yes", "No", "Unsure"]
        )

        urgency_level = st.selectbox(
            "How urgent is this evaluation?",
            ["Routine check", "Suspected contamination", "Emergency use"]
        )

    return {
        "uploaded_image": uploaded_image,
        "water_source_type": water_source_type,
        "water_usage": water_usage,
        "surrounding_area": surrounding_area,
        "noticed_issues": noticed_issues,
        "purification_possible": purification_possible,
        "urgency_level": urgency_level
    }

def generate_water_quality_report(user_water_inputs):
    uploaded_image = user_water_inputs["uploaded_image"]
    water_source_type = user_water_inputs["water_source_type"]
    water_usage = user_water_inputs["water_usage"]
    surrounding_area = user_water_inputs["surrounding_area"]
    noticed_issues = user_water_inputs["noticed_issues"]
    purification_possible = user_water_inputs["purification_possible"]
    urgency_level = user_water_inputs["urgency_level"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(uploaded_image.getvalue())
        image_path = tmp.name

    # Step 1: Visual Analysis Agent
    visual_analyzer_agent = Agent(
        name="Water Visual Analyzer",
        model=OpenAIChat(id="gpt-4o", api_key=st.session_state.openai_api_key),
        description=dedent("""
            Analyzes a water image to detect signs of contamination and assess severity.
        """),
        role="You are a water safety inspector. Given an image of water in a container or body, detect visual signs of contamination and assess risk level.",
        instructions=[
            "Inspect the uploaded water image for visible indicators such as:",
            "- Murky or discolored water",
            "- Foam or oil sheen",
            "- Floating particles or sediment",
            "- Algae, moss, or biofilm",
            "- Signs of mosquito breeding (like larvae)",
            "",
            "Output the results in the following format:",
            "- `detected_features`: List of visual contamination indicators",
            "- `contamination_level`: Choose one of Low, Moderate, High",
            "- `likely_risks`: Possible contamination risks (e.g., bacterial, chemical, mosquito-borne)"
        ],
        response_model=WaterVisualAnalysisOutput,
        use_json_mode=True
    )

    # Run agent
    visual_insights = visual_analyzer_agent.run(
        "Inspect this water image for contamination signs.", 
        images=[Image(filepath=image_path)]
    ).content
    visual_insights_str = water_visual_output_to_string(visual_insights)

    # Step 2: Water Risk Mapper Agent
    water_risk_mapper_agent = Agent(
            name="Water Risk Mapper",
            model=OpenAIChat(id="gpt-4o", api_key=st.session_state.openai_api_key),
            description="Analyzes water image findings and context to classify contamination causes and severity without suggesting actions.",
            role="You are a water risk analyst. Based on visual indicators and context, summarize contamination types and risk levels without giving recommendations.",
            instructions=[
                "Take the visual insights and user-provided water details to classify contamination.",
                "For each cause, specify:",
                "- Type: Biological, Chemical, or Vector-borne",
                "- Source: e.g., murkiness, algae, larvae, sediment",
                "- Risk Level: Low, Moderate, or High",
                "Return a short overall summary, severity label, and causes list.",
                "End with an optional note on concern or urgency (without giving advice)."
            ],
            response_model=WaterContaminationDiagnosis,
            use_json_mode=True
        )
    
    contamination_input_prompt = f"""💧 **Water Risk Mapping Input**

    {visual_insights_str}

    **Water Source**: {water_source_type}
    **Usage**: {water_usage}
    **Surrounding Area**: {surrounding_area}
    **User-Noticed Issues**: {', '.join(noticed_issues) or 'None'}
    **Urgency Level**: {urgency_level}
    """

    water_diagnosis = water_risk_mapper_agent.run(
        contamination_input_prompt
    ).content
    water_diagnosis_str = water_diagnosis_to_string(water_diagnosis)

    # Step 3: Web Researcher Agent
    web_researcher_agent = Agent(
        name="Water Safety Research Assistant",
        role="Finds broad water purification and safety information based on contamination diagnosis.",
        model=OpenAIChat(id="gpt-4o", api_key=st.session_state.openai_api_key),
        description="Given a water contamination diagnosis and water source type, search across categories like DIY purification methods, water safety guides, NGO advisories, and filter recommendations.",
        instructions=[
            "Analyze the contamination diagnosis summary, severity, and causes.",
            "Use the user's selected water source type (e.g., glass, pond, tank) to inform relevance.",
            "Initiate targeted searches across categories like:",
            "- DIY purification methods",
            "- Water safety and hygiene guides",
            "- NGO/government advisories and community support programs",
            "- Filter technology comparisons or recommendations",
            "Use SerpAPI to find and return 12-16 useful links total from across those categories.",
            "Present results in clean markdown format with clear, short titles and clickable URLs.",
            "Avoid location-specific recommendations. Prioritize broadly applicable practices."
        ],
        tools=[SerpApiTools(api_key=st.session_state.serp_api_key)],
        tool_call_limit=4,
        markdown=True, 
    )

    research_inputs = f"""
    📋 Water Contamination Summary:
    {water_diagnosis_str}

    Water Source Type: {water_source_type or 'Not specified'}

    Based on this input, perform SerpAPI-based web searches across the following categories:
    - DIY water purification
    - Water safety and hygiene guidelines
    - NGO or public advisories
    - Water filter reviews or recommendations

    Return 12-16 helpful and broadly useful links in markdown format.
    """

    research_links = web_researcher_agent.run(research_inputs).content

    # Step 4: Report Generator Agent
    water_report_generator_agent = Agent(
        name="Water Quality Report Generator",
        model=OpenAIChat(id="o3-mini", api_key=st.session_state.openai_api_key),
        role="Generates a structured, markdown-formatted water safety report using visual inspection, contamination diagnosis, and practical research links.",
        description=dedent("""
            You are a water safety assistant and report generator. You are provided with:
            1. A visual contamination summary of a water sample.
            2. A structured diagnosis including contamination type, severity, and health risks.
            3. A set of curated web links grouped into:
            - DIY water purification
            - Water safety and hygiene guidelines
            - NGO or public advisories
            - Water filter reviews or recommendations

            Your job is to go through the links to generate a clean, markdown-formatted report to help users take safe, informed action.
        """),
        instructions=[
                "Start with: ## 🚱 Water Quality Report",
                "",
                "### 🔍 Visual Contamination Summary",
                "- Highlight visible signs such as murky color, floating particles, algae, oil sheen, or mosquitoes.",
                "- Indicate overall contamination level: Low, Moderate, or High.",
                "- List potential contamination types (e.g., bacterial, chemical, vector-borne).",
                "",
                "### 🧪 Diagnosis & Risk Mapping",
                "- Summarize what the visual signs imply about likely risks or sources of contamination.",
                "- Include brief notes on urgency or health standards (if mentioned in input).",
                "",
                "### 💧 Suggested Purification Methods",
                "- Recommend best-fit purification techniques for the given scenario (boiling, chlorination, filters, etc.).",
                "- Embed DIY and water filter links directly inside the suggestions (e.g., [boil water safely at home](https://...)).",
                "",
                "### 🚫 Do’s and Don’ts",
                "- Bullet out practical water usage tips and safety warnings (e.g., ‘Do not use untreated water for cooking’).",
                "- Embed relevant links into safety tips when possible (e.g., [basic hygiene practices](https://...), [when to avoid water use](https://...)).",
                "- Keep the language friendly, clear, and actionable.",
                "",
                "### 🔗 Curated Resources",
                "- Organize links under these subheadings:",
                "  #### 🛠️ DIY Water Purification",
                "  #### 📘 Water Safety & Hygiene Guidelines",
                "  #### 🏥 NGO or Public Advisories",
                "  #### 🧪 Water Filter Reviews & Recommendations",
                "- Use clear markdown list formatting with descriptive link titles.",
                "",
                "**Important**: Embed 1–2 relevant links directly into the ‘Suggested Purification Methods’ and ‘Do’s and Don’ts’ sections above.",
                "Only return the final markdown report. No other output or commentary."
            ],
        markdown=True,
        add_datetime_to_instructions=True
    )

    # Prompt for report generation
    report_prompt = f"""
    {visual_insights_str}

    {water_diagnosis_str}

    🔬 **Curated Web Resources**

    {research_links}

    Generate a markdown-formatted, personalized Water Safety report using the content and structure above.
    """

    # Run the agent
    water_report = water_report_generator_agent.run(report_prompt).content
    return water_report

def main() -> None:
    # Page config
    st.set_page_config(page_title="Water Quality Auditor Bot", page_icon="🚱", layout="wide")

    # Custom styling
    st.markdown(
        """
        <style>
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        div[data-testid="stTextInput"] {
            max-width: 1200px;
            margin-left: auto;
            margin-right: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Header and intro
    st.markdown("<h1 style='font-size: 2.5rem;'>🚱 Water Quality Auditor Bot</h1>", unsafe_allow_html=True)
    st.markdown(
        "Welcome to Water Quality Auditor Bot — a practical Streamlit assistant that analyzes water images for clarity, color, and visible pollutants, delivering personalized guidance to help ensure access to cleaner, safer water for drinking and everyday use.",
        unsafe_allow_html=True
    )

    render_sidebar()
    user_water_inputs = render_water_quality_inputs()

    st.markdown("---")

    # Call the report generation method when the user clicks the button
    if st.button("🚰 Generate Water Safety Report"):
        if not hasattr(st.session_state, "openai_api_key"):
            st.error("Please provide your OpenAI API key in the sidebar.")
        elif not hasattr(st.session_state, "serp_api_key"):
            st.error("Please provide your SerpAPI key in the sidebar.")
        elif "uploaded_image" not in user_water_inputs or not user_water_inputs["uploaded_image"]:
            st.error("Please upload an image of the water sample before generating the report.")
        else:
            with st.spinner("Analyzing your water sample and generating your personalized Water Safety report..."):
                report = generate_water_quality_report(user_water_inputs)

                st.session_state.water_report = report
                st.session_state.water_image = user_water_inputs["uploaded_image"]

    # Display and download
    if "water_report" in st.session_state:
        st.markdown("## 🧊 Uploaded Water Sample Image")
        st.image(st.session_state.water_image, use_container_width=False)

        st.markdown(st.session_state.water_report, unsafe_allow_html=True)

        st.download_button(
            label="📥 Download Water Safety Report",
            data=st.session_state.water_report,
            file_name="water_safety_report.md",
            mime="text/markdown"
        )

if __name__ == "__main__":
    main()

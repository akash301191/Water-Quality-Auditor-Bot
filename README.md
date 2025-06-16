# Water Quality Auditor Bot

**Water Quality Auditor Bot** is a smart Streamlit application that inspects water samples through image analysis and curated web research. Powered by [Agno](https://github.com/agno-agi/agno), OpenAI's GPT-4o, and SerpAPI, this bot generates a structured, markdown-formatted Water Safety Report with personalized purification advice, contamination insights, and actionable resources.

## Folder Structure

```
Water-Quality-Auditor-Bot/
├── water-quality-auditor-bot.py
├── README.md
└── requirements.txt
```

* **water-quality-auditor-bot.py**: The main Streamlit application.
* **requirements.txt**: Required Python packages.
* **README.md**: This documentation file.

## Features

* **Water Sample Image Upload + Context Input**
  Upload a water image and provide contextual details—like source type, usage, surroundings, and observed issues.

* **AI-Powered Visual Contamination Analysis**
  A visual inspection agent detects visible signs of contamination (e.g., murkiness, particles, algae, larvae) and estimates risk level.

* **Contamination Diagnosis & Mapping**
  A dedicated agent reviews the visual findings and your inputs to classify risks by type (biological, chemical, vector-borne) and severity.

* **Curated Web Search Assistant**
  A web agent uses SerpAPI to gather useful links across:

  * DIY purification methods
  * Water safety and hygiene guidelines
  * NGO and public advisories
  * Water filter reviews and recommendations

* **Structured Water Safety Report**
  A final agent weaves everything into a clean, markdown-formatted report with:

  * Visual summaries
  * Risk mapping
  * Recommended purification techniques
  * Do’s and Don’ts with links
  * Curated resources by category

* **Download Option**
  Download the complete Water Safety Report as a `.md` file for future use or sharing.

* **Minimal UI**
  Built with Streamlit for a focused and responsive experience.

## Prerequisites

* Python 3.11 or higher
* An OpenAI API key ([Get one here](https://platform.openai.com/account/api-keys))
* A SerpAPI key ([Get one here](https://serpapi.com/manage-api-key))

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/akash301191/Water-Quality-Auditor-Bot.git
   cd Water-Quality-Auditor-Bot
   ```

2. **(Optional) Create and activate a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate        # On macOS/Linux
   # or
   venv\Scripts\activate           # On Windows
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the app**:

   ```bash
   streamlit run water-quality-auditor-bot.py
   ```

2. **In your browser**:

   * Enter your OpenAI and SerpAPI keys in the sidebar.
   * Upload a clear water image.
   * Fill in details like water source, usage, surrounding environment, and observed issues.
   * Click **🚰 Generate Water Safety Report**.
   * View and download your AI-generated report with recommendations and resources.

3. **Download Option**
   Use the **📥 Download Water Safety Report** button to save your results as a `.md` file.

## Code Overview

* **`render_water_quality_inputs()`**
  Captures user-provided inputs—image, usage type, surroundings, issues, and preferences.

* **`render_sidebar()`**
  Collects and stores OpenAI and SerpAPI credentials in Streamlit session state.

* **`generate_water_quality_report()`**

  * Runs a `Water Visual Analyzer` agent to identify visible contamination.
  * Passes results to `Water Risk Mapper` for structured diagnosis.
  * Triggers a `Water Safety Research Assistant` agent to fetch categorized resources.
  * Uses `Water Quality Report Generator` to build the final markdown-formatted report.

* **`main()`**
  Sets up the Streamlit app layout, processes interactions, and coordinates report generation and display.

## Contributions

Contributions are welcome! Fork the repository, submit pull requests, or suggest enhancements. Please ensure your changes align with the goal of promoting accessible water safety guidance.

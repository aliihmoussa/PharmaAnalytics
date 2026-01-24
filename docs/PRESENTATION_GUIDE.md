# PowerPoint Presentation Guide

## Quick Start

### Option 1: Generate PowerPoint Automatically (Recommended)

1. **Install the required library:**
   ```bash
   pip install python-pptx
   ```

2. **Run the script:**
   ```bash
   cd /home/alimoussa/Documents/M2-\ 2026/Projects2026/PharmaAnalytics
   python scripts/generate_presentation.py
   ```

3. **Find your presentation:**
   The PowerPoint file will be saved as `PharmaAnalytics_Presentation.pptx` in the project root directory.

### Option 2: Manual Creation from Outline

1. **Open the outline:**
   - File: `docs/POWERPOINT_PRESENTATION_OUTLINE.md`
   - Contains all 21 slides with content

2. **Create PowerPoint:**
   - Open Microsoft PowerPoint or Google Slides
   - Copy content from each slide section
   - Follow the design recommendations at the bottom of the outline

## Presentation Structure

The presentation contains **21 slides** organized as follows:

1. **Title Slide** - Project name and subtitle
2. **Project Overview** - What is PharmaAnalytics?
3. **Architecture Overview** - System architecture
4. **Technology Stack - Backend** - Backend technologies
5. **Technology Stack - Data & ML** - Data processing and ML tools
6. **Core Modules Overview** - Four main modules
7-10. **Module Details** - One slide per module (Ingestion, Analytics, Diagnostics, Forecasting)
11-12. **Data Model** - Database schema and input fields
13. **Key Features** - Platform capabilities
14. **Deployment Architecture** - Docker services
15. **Project Structure** - Codebase organization
16. **Use Cases** - Target users
17. **API Endpoints** - REST API overview
18. **Current Status** - Project status
19. **Benefits** - Platform advantages
20. **Thank You** - Closing slide

## Customization Tips

### Colors
- Primary Blue: #2E86AB
- Secondary Green: #06A77D
- Accent Orange: #F18F01

### Fonts
- Headings: Arial Bold or Calibri Bold (32-44pt)
- Body: Arial or Calibri (18-24pt)
- Code: Consolas or Courier New (14-16pt)

### Visual Elements
- Add icons for each module
- Include architecture diagram (Slide 3)
- Add screenshots of API responses if available
- Use charts/graphs for analytics examples

## Notes

- The Python script creates a basic PowerPoint with all content
- You can customize colors, fonts, and add images after generation
- The markdown outline provides detailed content and design recommendations
- All slides follow a consistent structure for professional presentation


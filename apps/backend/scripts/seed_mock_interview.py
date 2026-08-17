"""
What: Seed script for creating a mock interview with candidates.
Why: Populates the local database with a realistic "Senior Graphic Designer" interview and 5 pending candidates.
Boundaries: Standalone script, not imported by the main application.
"""

import asyncio
import sys
import os

# Ensure src/ is in the path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from sqlalchemy import select
from app.core.db import async_session_factory
from app.models.user import User
from app.models.interview import Interview
from app.models.goal import Goal
from app.models.candidate import Candidate

# The provided JSON payload
MOCK_DATA = {
  "job_name": "Senior Graphic Designer",
  "job_description": "We are seeking a Senior Graphic Designer to own the visual identity of our brand across digital and print channels. You will design marketing assets including social media graphics, email templates, print brochures, and packaging, applying strong typography, layout composition, and color theory to keep everything on-brand. You'll work primarily in Adobe Illustrator and Photoshop for print-ready and raster assets, and in Figma for digital mockups and design systems shared with the product team. You will lead client and stakeholder review sessions, presenting design concepts, defending creative choices, and incorporating rounds of revision feedback into polished final deliverables. You'll also mentor junior designers, reviewing their work and giving constructive feedback, and help maintain our brand style guide as it evolves. Required: 5+ years of professional graphic design experience, a strong portfolio showing both print and digital work, expert-level Adobe Creative Suite skills, and experience presenting and defending design work directly to clients or executives.",
  "difficulty": "senior",
  "num_goals": 4,
  "total_duration_minutes": 45,
  "goals": [
    {
      "goal_id": "g_01",
      "topic": "Design Systems and Brand Consistency",
      "goal": "Evaluate the candidate's ability to maintain and evolve a design system across diverse media, specifically how they ensure visual consistency between print-ready assets and digital product mockups.",
      "interview_time_in_minute": 12,
      "need_grounding": True
    },
    {
      "goal_id": "g_02",
      "topic": "Technical Proficiency and Workflow",
      "goal": "Assess the candidate's technical workflow in Adobe Illustrator/Photoshop versus Figma, focusing on their process for preparing print-ready files versus responsive digital assets.",
      "interview_time_in_minute": 10,
      "need_grounding": True
    },
    {
      "goal_id": "g_03",
      "topic": "Stakeholder Presentation and Defense",
      "goal": "Evaluate the candidate's ability to present design concepts to non-design stakeholders, specifically how they articulate the rationale behind creative choices and handle conflicting feedback.",
      "interview_time_in_minute": 12,
      "need_grounding": False
    },
    {
      "goal_id": "g_04",
      "topic": "Mentorship and Design Review",
      "goal": "Assess the candidate's approach to reviewing junior designers' work, specifically how they provide actionable, constructive feedback that improves the quality of the output while fostering the junior's professional growth.",
      "interview_time_in_minute": 11,
      "need_grounding": False
    }
  ],
  "grounding_theories": [
    {
      "goal_id": "g_01",
      "theory": "### Core Concept: Bridging Print and Digital Consistency\nMaintaining brand consistency across print and digital media requires a dual-framework approach: **Brand Guidelines** (the foundational identity) and **Design Systems** (the scalable implementation). While brand guidelines define the \"what\" (logos, core colors, typography, tone), design systems provide the \"how\" for digital products (reusable components, design tokens, and code-based documentation).\n\n### Key Mechanisms for Consistency\nTo ensure visual alignment between print-ready assets and digital mockups, designers must manage specific technical and structural differences:\n\n*   **Color Space Management:** Digital media uses the RGB (additive) color model, while print uses CMYK (subtractive). A common failure point is the direct translation of digital colors to print, which can result in dull or inaccurate hues. Professionals use Pantone (PMS) colors as a bridge or reference point to ensure that brand colors remain consistent across both media types.\n*   **Typography and Spacing:** Font rendering and readability differ significantly between responsive digital interfaces and fixed-size print layouts. Designers must adjust font weights, kerning, and line spacing for print to ensure that the visual balance achieved on screen is not lost on paper.\n*   **Design Tokens:** These act as a centralized, single source of truth for design attributes (colors, spacing, sizing, typography). By using tokens, teams can ensure that updates to a core brand element propagate consistently across both digital product components and print templates.\n*   **Visual Hierarchy and Templates:** Maintaining a consistent visual hierarchy—such as header sizes, button placement, and grid systems—is essential. Reusable templates for both print (e.g., brochures, business cards) and digital (e.g., web components, social graphics) help enforce these rules, reducing the risk of \"off-brand\" variations.\n\n### Practical Implementation\n*   **Centralized Resources:** Organizations should maintain a centralized repository of assets. This prevents the use of outdated logos or incorrect color profiles.\n*   **Regular Audits:** Periodic brand check-ins are necessary to audit materials, templates, and assets. This ensures that print collateral and digital interfaces remain aligned as the brand evolves.\n*   **Documentation:** A change log or versioning system for the design system ensures that all stakeholders (designers, developers, and external vendors) are working from the most current specifications.\n\n### Common Pitfalls\n*   **Treating Print and Digital as Silos:** Failing to integrate brand identity into the design system from the start leads to \"retrofitting\" costs and divergent visual languages.\n*   **Ignoring Medium-Specific Constraints:** Assuming that a digital design will translate perfectly to print without adjustments for bleed, trim, and paper-specific color rendering.\n*   **Inconsistent Asset Usage:** Allowing different versions of a logo or conflicting color palettes to exist across different channels, which confuses the audience and erodes brand credibility.",
      "references": [
        {
          "url": "https://www.pioneerpresscolorado.com/news/from-digital-to-print-how-we-ensure-perfect-brand-consistency",
          "title": "From Digital to Print: How We Ensure Perfect Brand Consistency",
          "excerpt": "One of the most common disconnects between digital and print design comes down to color. Screens create color using the RGB (Red, Green, Blue) model... Print, on the other hand, uses the CMYK (Cyan, Magenta, Yellow, Key/Black) model... We always work with our clients to ensure their digital files are converted to the CMYK color space accurately, often using Pantone (PMS) colors as a bridge to guarantee the final printed color perfectly matches their brand guidelines.",
          "matched_query": "best practices for brand consistency between print and digital design systems",
          "credibility_tier": "A",
          "corroborated": True
        },
        {
          "url": "https://www.pioneerpresscolorado.com/news/from-digital-to-print-how-we-ensure-perfect-brand-consistency",
          "title": "From Digital to Print: How We Ensure Perfect Brand Consistency",
          "excerpt": "The way fonts render and the amount of space needed around text can differ significantly between a responsive website and a fixed-size printed page. What looks perfectly balanced on a screen might appear cramped or poorly spaced on a business card or brochure. We pay close attention to typography, ensuring that font weights, letter spacing (kerning), and line spacing are optimized for readability and aesthetic appeal in the final printed format.",
          "matched_query": "best practices for brand consistency between print and digital design systems",
          "credibility_tier": "A",
          "corroborated": True
        },
        {
          "url": "https://whatifdesign.co/feeds/blog/brand-guidelines-vs-design-system",
          "title": "Brand Guidelines vs Design Systems: A Comprehensive Comparison",
          "excerpt": "Brand guidelines govern visual identity (logos, colors, typography, and tone) across your website, pitch materials, print collateral, and every channel where your brand appears. Design systems provide reusable UI components, design tokens, and documentation for digital product development. Both work together: brand guidelines define your identity, design systems scale digital products.",
          "matched_query": "best practices for brand consistency between print and digital design systems",
          "credibility_tier": "A",
          "corroborated": True
        },
        {
          "url": "https://visualsoldiers.com/ultimate-guide-cross-platform-design-consistency",
          "title": "Ultimate Guide to Cross-Platform Design Consistency - Visual Soldiers",
          "excerpt": "Design tokens serve as a centralized reference for essential design elements such as colors, typography, spacing, and sizing. By standardizing these components, they help maintain a consistent visual style across various platforms and devices.",
          "matched_query": "maintaining design system consistency across print and digital media",
          "credibility_tier": "A",
          "corroborated": True
        },
        {
          "url": "https://www.uprinting.com/blog/how-to-keep-branding-consistent",
          "title": "How to Keep Branding Consistent for Designers",
          "excerpt": "Repetition is key to branding consistency — and that includes visual hierarchy in your design. For example, use the same header sizes, whether you’re creating content for print or digital platforms. Make sure call-to-action buttons and images are placed in familiar places, and use the right margins, bleed, trim, and spacing on all templates.",
          "matched_query": "maintaining design system consistency across print and digital media",
          "credibility_tier": "A",
          "corroborated": True
        }
      ]
    },
    {
      "goal_id": "g_02",
      "theory": "### Print-Ready Workflow (Adobe Illustrator/Photoshop)\nThe primary objective in preparing files for print is ensuring color accuracy, resolution integrity, and physical production requirements (bleed, trim, and safety).\n\n*   **Document Setup:** Files must be created in CMYK color mode with a resolution of at least 300 PPI (pixels per inch) for raster elements. Artboards should include a defined bleed area (typically 0.125 inches) to prevent white edges after trimming.\n*   **Typography:** To avoid font substitution issues, text should be converted to outlines (vector paths). For small black text, designers should use 100% K (black) rather than a 4-color CMYK build to ensure crisp registration.\n*   **Asset Management:** Images must be embedded or linked at high resolution (300 DPI at final print size). Designers should clean up unused swatches and layers to simplify the file for pre-press departments.\n*   **Final Output:** Files are typically exported as high-quality PDFs. Pre-press checks should include verifying color separations (ensuring no unintended spot colors or over-saturated ink builds) and confirming that all critical content is within the \"safe zone\" (at least 0.125 inches from the trim line).\n\n### Responsive Digital Workflow (Figma)\nThe primary objective in digital design is creating scalable, consistent, and developer-friendly assets that adapt to various viewports.\n\n*   **Layout & Structure:** Designers utilize Frames (the equivalent of artboards) to represent different device breakpoints. A grid system is essential for maintaining alignment and consistency across these breakpoints.\n*   **Scalability & Responsiveness:** Figma’s \"Auto Layout\" and \"Constraints\" are the core mechanisms for responsive design. These features allow elements to automatically resize, reposition, or wrap based on the parent frame's dimensions.\n*   **Design Systems:** Efficiency is maintained through the use of Styles (colors, typography, effects) and Components (reusable UI elements). These ensure global consistency; updating a master component propagates changes across all instances.\n*   **Developer Handoff:** Modern workflows leverage \"Dev Mode\" and plugins to bridge the gap between design and code. This allows developers to inspect properties, export assets in various formats (SVG, PNG, etc.), and sometimes generate responsive code snippets directly from the design file.\n*   **Organization:** A clean file structure—using clear naming conventions, organized layers, and centralized asset libraries—is critical for team collaboration and version control.",
      "references": [
        {
          "url": "https://www.linkedin.com/posts/sw19-design-and-print_photoshopforprint-printreadyfiles-graphicdesigntips-activity-7420435539717423104-uWCd",
          "title": "Photoshop Print-Ready File Preparation Best Practices",
          "excerpt": "If you want your design to print exactly how you intended, here’s what makes a file production-ready: 1. Use 100K for Small Black Text... 3. Add Proper Bleed... 4. Send Embedded Fonts... 5. Send High-Resolution Images (300 DPI at size)... 6. Check Separations.",
          "matched_query": "Adobe Illustrator Photoshop print-ready file preparation best practices",
          "credibility_tier": "A",
          "corroborated": True
        },
        {
          "url": "https://primoprint.com/blog/diy-into-create-print-ready-files-in-adobe-illustrator",
          "title": "DIY: How to Create Print-Ready Files in Adobe Illustrator",
          "excerpt": "Before we save, you will want to outline the text... Go to File > Save As and select the ‘High-Quality Print’ option. This will preserve everything but if the file size is too big, you can always uncheck ‘Preserve Illustrator Editing Capabilities.’",
          "matched_query": "Adobe Illustrator Photoshop print-ready file preparation best practices",
          "credibility_tier": "A",
          "corroborated": True
        },
        {
          "url": "https://www.figma.com/resource-library/responsive-website-design",
          "title": "Responsive Website Design: Key Components - Figma",
          "excerpt": "Design with a Grid System... Use Styles and Components... Pay Attention to Responsive Design... Create frames in your canvas... Use auto layout and constraints. This allows you to define how your design elements should resize and position themselves across screens.",
          "matched_query": "Figma responsive digital asset design workflow best practices",
          "credibility_tier": "A",
          "corroborated": True
        },
        {
          "url": "https://www.figma.com/resource-library/responsive-website-design",
          "title": "Responsive Website Design: Key Components - Figma",
          "excerpt": "Figma’s Dev Mode streamlines the design-to-development handoff. Codegen plugins can enhance your workflow and help you create responsive websites by automatically generating code based on designs.",
          "matched_query": "Figma responsive digital asset design workflow best practices",
          "credibility_tier": "A",
          "corroborated": True
        }
      ]
    }
  ],
}

MOCK_CANDIDATES = [
    {"first_name": "Alice", "last_name": "Smith", "email": "alice@example.com"},
    {"first_name": "Bob", "last_name": "Johnson", "email": "bob@example.com"},
    {"first_name": "Charlie", "last_name": "Brown", "email": "charlie@example.com"},
    {"first_name": "Diana", "last_name": "Prince", "email": "diana@example.com"},
    {"first_name": "Ethan", "last_name": "Hunt", "email": "ethan@example.com"}
]

async def seed_interview():
    async with async_session_factory() as session:
        # Get admin user
        result = await session.execute(select(User).where(User.email == "admin@example.com"))
        admin = result.scalar_one_or_none()
        
        if not admin:
            print("Error: admin@example.com not found. Did you run seed_mock_user.py?")
            return
            
        print("Creating mock interview...")
        interview = Interview(
            creator_id=admin.id,
            job_name=MOCK_DATA["job_name"],
            job_description=MOCK_DATA["job_description"],
            difficulty=MOCK_DATA["difficulty"],
            num_goals=MOCK_DATA["num_goals"],
            total_duration_minutes=MOCK_DATA["total_duration_minutes"],
            status="scheduled"
        )
        session.add(interview)
        await session.flush() # flush to get interview.id
        
        print(f"Created interview: {interview.id}")
        
        # Build mapping of grounding theories
        theories_map = {g["goal_id"]: g for g in MOCK_DATA.get("grounding_theories", [])}
        
        # Create Goals
        for goal_data in MOCK_DATA["goals"]:
            theory_data = theories_map.get(goal_data["goal_id"], {})
            
            goal = Goal(
                goal_ref=goal_data["goal_id"],
                interview_id=interview.id,
                topic=goal_data["topic"],
                goal=goal_data["goal"],
                grounding_theory=theory_data.get("theory"),
                references=theory_data.get("references", []),
                # Default empty values for missing fields in JSON
                passing_criteria=[],
                pushback_triggers=[],
                wrong_answer_signals=[]
            )
            session.add(goal)
            
        # Create Candidates
        print(f"Creating {len(MOCK_CANDIDATES)} candidates...")
        for c in MOCK_CANDIDATES:
            candidate = Candidate(
                interview_id=interview.id,
                first_name=c["first_name"],
                last_name=c["last_name"],
                email=c["email"],
                status="not_started" # Has not started yet
            )
            session.add(candidate)
            
        await session.commit()
        print("Successfully seeded interview, goals, and candidates!")

if __name__ == "__main__":
    asyncio.run(seed_interview())

"""
What: Executes the full Question-Maker Agent graph across a batch of user-configured job description test cases.
Why: Allows developers and recruiters to evaluate graph performance, schema compliance, and quality across diverse job roles.
Boundaries: Standalone evaluation and simulation script for development/testing; not executed in production API flows.
"""

import os
import sys
import json
import time
import importlib
from typing import List, Dict, Any

# Setup workspace paths for monorepo imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env")))

# Dynamically import question-maker-agent graph to avoid hyphens in module name
graph_module = importlib.import_module("question-maker-agent.graph")
compiled_question_maker_graph = graph_module.graph


# --- Batch Test Cases Array ---
BATCH_TEST_CASES: List[Dict[str, Any]] = [
    # --- 1-5: Diverse Roles (Standard & Hard Cases) ---
    {
        "test_case_name": "Case 1: Mid-level Fullstack React/Node Developer (Software)",
        "inputs": {
            "job_name": "Mid-level Fullstack React/Node Developer",
            "job_description": "We are looking for a Mid-Level Fullstack Engineer to join our product team and help build and maintain our core web application. On the frontend, you will build reusable UI components in React (using hooks and functional components), manage application state with Redux or the Context API, and work closely with our design team to turn Figma mockups into pixel-accurate interfaces. On the backend, you will design and build RESTful APIs using Node.js and Express, write and optimize SQL queries in PostgreSQL, and implement authentication and authorization flows. You should be comfortable writing unit and integration tests (Jest, React Testing Library), using Git for version control, and packaging services with Docker for consistent local and production environments. You will take part in sprint planning, occasional pair programming, and peer code reviews. Required: 2-4 years of professional experience with React and Node.js, a solid understanding of REST API design and relational databases, and basic Docker usage. Nice to have: experience with TypeScript, CI/CD pipelines (GitHub Actions), and AWS or GCP.",
            "difficulty": "mid",
            "num_goals": 4,
            "total_duration_minutes": 60,
            "domain_hint": "software"
        },
    },
    {
        "test_case_name": "Case 2: Professional Video Editor (Creative)",
        "inputs": {
            "job_name": "Professional Video Editor",
            "job_description": "We are hiring a Professional Video Editor to join our in-house creative team, producing polished promotional videos, brand documentaries, and social media content. Day to day, you will import and organize raw camera footage, assemble rough cuts, and trim and sequence clips for pacing and story flow, delivering final exports in multiple formats (16:9 for YouTube, 9:16 for Instagram Reels/TikTok, etc.). You will perform color correction and color grading to keep footage visually consistent, sync dialogue and music tracks, clean up audio levels, and add basic motion graphics or lower-third titles. You'll take notes from the Creative Director, incorporate multiple rounds of feedback, and manage tight turnaround deadlines, sometimes juggling two to three projects at once. Required tools: Adobe Premiere Pro (must-have), Adobe Media Encoder, and basic familiarity with After Effects for motion graphics. Required skills: a strong sense of pacing and rhythm, attention to detail in audio sync, and organized media management (proxies, folder structures, version naming). 2+ years of professional editing experience and a demo reel are required.",
            "difficulty": "mid",
            "num_goals": 4,
            "total_duration_minutes": 45,
            "domain_hint": "creative"
        },
    },
    {
        "test_case_name": "Case 3: Senior Quantitative Trader (Finance)",
        "inputs": {
            "job_name": "Senior Quantitative Trader",
            "job_description": "We are looking for a Senior Quantitative Trader to join our proprietary trading desk, responsible for designing, deploying, and actively managing market-making and statistical arbitrage strategies across liquid futures, options, and derivatives markets. You will monitor live positions throughout the trading day, adjust quoting parameters in response to changing market microstructure and order book depth, and manage risk limits and drawdown thresholds in real time. You'll analyze execution quality (slippage, fill rates, latency) and work with quant researchers and engineers to refine signal generation and execution logic. Strong programming skills in Python or C++ for backtesting and strategy prototyping are expected, along with hands-on experience with a trading platform (e.g., Bloomberg Terminal, or a proprietary OMS/EMS system) and statistical tools such as NumPy or pandas. Required: 5+ years of professional trading experience, a deep understanding of order book dynamics and market microstructure, and a track record of profitable strategy development. You must be comfortable working under pressure during high-volatility sessions and making fast, disciplined decisions.",
            "difficulty": "senior",
            "num_goals": 5,
            "total_duration_minutes": 60,
            "domain_hint": "finance"
        },
    },
    {
        "test_case_name": "Case 4: Customer Service Lead (Support)",
        "inputs": {
            "job_name": "Customer Service Lead",
            "job_description": "We're hiring a Customer Service Lead to manage our tier-1 support team and act as the first point of escalation for difficult client issues. You will monitor incoming ticket queues in Zendesk, assign and triage tickets by priority, and track team performance metrics like CSAT (customer satisfaction score), first-response time, and resolution time. When a customer escalates a complaint, you'll step in to de-escalate the situation, using active listening and clear communication to resolve the issue or route it to the right department. You'll write and maintain response templates and internal knowledge-base articles so the team can answer common questions quickly and consistently. As a team lead, you'll run weekly one-on-one coaching sessions, review support agents' ticket quality, and help onboard and train new hires. Required: 2+ years in a customer support role with at least one year in a lead or supervisory capacity, hands-on experience with a helpdesk tool like Zendesk or Freshdesk, and strong conflict-resolution skills. You should be comfortable staying calm and professional when a customer is upset.",
            "difficulty": "mid",
            "num_goals": 4,
            "total_duration_minutes": 45,
            "domain_hint": "support"
        },
    },
    {
        "test_case_name": "Case 5: Technical Recruiter (HR)",
        "inputs": {
            "job_name": "Technical Recruiter",
            "job_description": "We are looking for a Technical Recruiter to own the full-cycle hiring process for our engineering and design teams, from job posting to signed offer letter. You will write and post job descriptions, proactively source candidates on LinkedIn Recruiter and GitHub, and screen incoming applications for technical fit. You'll conduct 20-30 minute phone or video screening calls to assess candidates' experience, communication skills, and interest, and clearly explain our company culture, benefits, and growth opportunities to keep candidates engaged through the process. You will coordinate technical interview panels with hiring managers and engineers, gather structured feedback, and guide candidates through offer negotiations, including salary, equity, and start-date discussions. You'll also track every candidate's status in our applicant tracking system (e.g., Greenhouse or Lever) and report weekly pipeline metrics, like time-to-fill and offer-acceptance rate, to leadership. Required: 2+ years of technical recruiting experience, familiarity with engineering roles and terminology (e.g., knowing the difference between a backend and a DevOps engineer), and strong negotiation and relationship-building skills.",
            "difficulty": "mid",
            "num_goals": 4,
            "total_duration_minutes": 45,
            "domain_hint": "hr"
        },
    },
    # --- 6-10: Vague / Underspecified Inputs (Inference Testing) ---
    {
        "test_case_name": "Case 6: Content Writer (Creative)",
        "inputs": {
            "job_name": "Content Writer",
            "job_description": "We are hiring a Content Writer to plan, write, and publish blog articles that grow our organic search traffic and establish our company as a trusted voice in our industry. You will research topics using keyword-research tools (like Ahrefs or SEMrush) to find subjects our target audience is searching for, write clear and engaging long-form articles (typically 1,000-2,000 words), and structure posts with SEO best practices in mind, such as headers, meta descriptions, and internal links. You'll work with our marketing manager to plan a monthly content calendar, incorporate feedback from editors, and occasionally repurpose blog content into shorter social media posts or email newsletter snippets. You will publish and format posts directly in our CMS (WordPress). Required: 1-2 years of professional writing experience (blog, journalism, or marketing content), a strong grasp of grammar and a plain, engaging writing style, and basic familiarity with SEO principles. A portfolio of published writing samples is required.",
            "difficulty": "infer",
            "num_goals": 3,
            "total_duration_minutes": 30,
            "domain_hint": "creative"
        },
    },
    {
        "test_case_name": "Case 7: Retail Sales Associate (Sales)",
        "inputs": {
            "job_name": "Retail Sales Associate",
            "job_description": "We are hiring a Retail Sales Associate to work on the floor of our clothing store, helping customers find what they're looking for and providing a friendly shopping experience. Your day-to-day tasks include greeting customers as they walk in, answering questions about sizing, materials, and current promotions, and helping customers find items either on the sales floor or in the stockroom. You will operate the point-of-sale (POS) register to process purchases, returns, and exchanges, and help keep the store tidy by folding and restocking clothing racks and shelves throughout your shift. You'll also help set up seasonal window displays and promotional signage as directed by the store manager. No prior retail experience is required, but you should be comfortable standing for most of your shift, working weekends, and staying friendly and patient even when the store is busy. Basic math skills, for handling cash and calculating discounts, and a positive attitude are required.",
            "difficulty": "junior",
            "num_goals": 3,
            "total_duration_minutes": 30,
            "domain_hint": "sales"
        },
    },
    {
        "test_case_name": "Case 8: Executive Assistant (Support)",
        "inputs": {
            "job_name": "Executive Assistant",
            "job_description": "We are looking for an Executive Assistant to support two members of our leadership team with day-to-day scheduling and logistics. You will manage complex, ever-changing calendars across multiple time zones, scheduling and rescheduling meetings and proactively flagging conflicts before they happen. You'll book flights, hotels, and ground transportation for business trips, and prepare detailed travel itineraries. You will screen and prioritize incoming emails and phone calls, drafting responses or forwarding urgent items on the executives' behalf, and act as a gatekeeper to protect their focus time. You'll also help prepare materials for board meetings, such as slides and printed agendas, and handle occasional personal errands or appointment scheduling. Required: 3+ years of experience supporting senior executives, strong proficiency with Google Calendar or Outlook, excellent written communication, and the ability to handle confidential information with discretion. You should be highly organized and comfortable managing shifting priorities under time pressure.",
            "difficulty": "mid",
            "num_goals": 3,
            "total_duration_minutes": 30,
            "domain_hint": "support"
        },
    },
    {
        "test_case_name": "Case 9: Office Manager (Support)",
        "inputs": {
            "job_name": "Office Manager",
            "job_description": "We are hiring an Office Manager to keep our office running smoothly day to day. You will manage relationships with vendors and building management, order and restock office supplies and kitchen snacks, and ensure common areas (kitchen, conference rooms, lobby) stay clean and well-stocked. You'll greet and check in visitors and guests, coordinate badge access for new employees, and help set up conference rooms for meetings or client visits. You will help plan and execute internal events, like team lunches, birthdays, and holiday parties, and act as the point of contact for facilities issues, such as a broken AC unit or a jammed printer, coordinating repairs with building maintenance or outside vendors. You'll also help onboard new hires by preparing their desk setup and welcome materials on their first day. Required: 1-3 years of office administration or coordination experience, strong organizational skills, and the ability to juggle multiple small tasks throughout the day without dropping any of them.",
            "difficulty": "infer",
            "num_goals": 3,
            "total_duration_minutes": 30,
            "domain_hint": "support"
        },
    },
    {
        "test_case_name": "Case 10: Financial Analyst (Finance)",
        "inputs": {
            "job_name": "Financial Analyst",
            "job_description": "We are hiring a Financial Analyst to support our finance team with budgeting, reporting, and forecasting. You will build and maintain financial models in Excel or Google Sheets, using formulas like VLOOKUP/XLOOKUP, pivot tables, and basic macros to analyze company spending against budget. You'll track monthly and quarterly departmental budgets, flag variances to department heads, and prepare financial forecast reports for leadership review. You will pull data from our accounting system (e.g., QuickBooks or NetSuite) and reconcile it against internal spreadsheets to make sure numbers match. You'll also prepare slide decks summarizing financial performance for monthly leadership meetings, and support the annual budgeting process by gathering department-level inputs. Required: a degree in Finance, Accounting, or a related field (or equivalent experience), 1-3 years of experience in financial analysis or accounting, advanced Excel skills, and strong attention to detail with numbers.",
            "difficulty": "mid",
            "num_goals": 4,
            "total_duration_minutes": 45,
            "domain_hint": "finance"
        },
    },
    # --- 11-15: Technical / Specialized Roles ---
    {
        "test_case_name": "Case 11: Embedded Firmware Engineer (Hardware)",
        "inputs": {
            "job_name": "Embedded Firmware Engineer",
            "job_description": "Join our robotics team as an Embedded Firmware Engineer, developing the low-level software that controls our motor control boards. You will write real-time control loop code in C for STM32 microcontrollers, implementing tasks like PID control tuning for motor speed and position accuracy. You'll debug firmware issues directly on hardware, using a JTAG debugger to step through code and an oscilloscope or logic analyzer to inspect electrical signals and timing. You will build and maintain firmware tasks under FreeRTOS, manage inter-task communication, and implement CAN bus messaging so our boards can communicate with other robot subsystems. You'll write unit tests where possible, document register-level configuration decisions, and work closely with hardware engineers to bring up new circuit board revisions. Required: 2-4 years of embedded C experience, hands-on experience with ARM Cortex-M microcontrollers (STM32 preferred), and familiarity with RTOS concepts, CAN bus, and basic control theory (PID loops). Comfort reading schematics and using lab equipment such as an oscilloscope and multimeter is expected.",
            "difficulty": "mid",
            "num_goals": 4,
            "total_duration_minutes": 45,
            "domain_hint": "hardware"
        },
    },
    {
        "test_case_name": "Case 12: Senior Graphic Designer (Creative)",
        "inputs": {
            "job_name": "Senior Graphic Designer",
            "job_description": "We are seeking a Senior Graphic Designer to own the visual identity of our brand across digital and print channels. You will design marketing assets including social media graphics, email templates, print brochures, and packaging, applying strong typography, layout composition, and color theory to keep everything on-brand. You'll work primarily in Adobe Illustrator and Photoshop for print-ready and raster assets, and in Figma for digital mockups and design systems shared with the product team. You will lead client and stakeholder review sessions, presenting design concepts, defending creative choices, and incorporating rounds of revision feedback into polished final deliverables. You'll also mentor junior designers, reviewing their work and giving constructive feedback, and help maintain our brand style guide as it evolves. Required: 5+ years of professional graphic design experience, a strong portfolio showing both print and digital work, expert-level Adobe Creative Suite skills, and experience presenting and defending design work directly to clients or executives.",
            "difficulty": "senior",
            "num_goals": 4,
            "total_duration_minutes": 45,
            "domain_hint": "creative"
        },
    },
    {
        "test_case_name": "Case 13: Product Manager (Management)",
        "inputs": {
            "job_name": "Product Manager",
            "job_description": "We are hiring a Product Manager to bridge the gap between our product strategy and the engineering team building it. You will conduct and synthesize user research, such as interviews, surveys, and usage-data analysis, to identify customer pain points, then translate those insights into clear, written product requirements and user stories for engineering. You'll run regular roadmap grooming sessions with engineering leads to prioritize the backlog based on customer impact, business value, and technical effort. You will manage incoming feature requests from sales, support, and customers, deciding what gets built next and communicating those decisions, and the reasoning behind them, to stakeholders. You'll coordinate closely with designers on UX flows and with engineers during sprint planning and standups, and track feature launches to see whether they achieved the intended impact using product analytics tools such as Amplitude or Mixpanel. Required: 3+ years of product management experience, strong written and verbal communication skills, and comfort using data to make prioritization decisions. Experience with agile/scrum workflows and Jira is expected.",
            "difficulty": "mid",
            "num_goals": 4,
            "total_duration_minutes": 45,
            "domain_hint": "management"
        },
    },
    {
        "test_case_name": "Case 14: B2B Enterprise Account Executive (Sales)",
        "inputs": {
            "job_name": "B2B Enterprise Account Executive",
            "job_description": "We are hiring a B2B Enterprise Account Executive to manage and close deals with large enterprise clients. You will run full sales cycles from qualified lead to signed contract, delivering polished product demos tailored to executive stakeholders (VPs, C-suite) and clearly articulating our product's ROI for their business. You'll navigate complex procurement processes at large organizations, working with legal, security, and finance teams on the client side to move deals through approval. You will negotiate pricing, contract terms, and multi-year agreements, typically closing deals in the five-to-six-figure annual contract value range. You'll manage your pipeline in Salesforce, forecast deal timelines accurately for sales leadership, and work with our sales engineering team to answer technical questions during the evaluation stage. Required: 4+ years of enterprise B2B sales experience with a track record of hitting or exceeding quota, strong negotiation skills, and experience selling to VP or C-level stakeholders at large companies. Familiarity with Salesforce or a similar CRM is required.",
            "difficulty": "senior",
            "num_goals": 4,
            "total_duration_minutes": 45,
            "domain_hint": "sales"
        },
    },
    {
        "test_case_name": "Case 15: QA Automation Engineer (QA)",
        "inputs": {
            "job_name": "QA Automation Engineer",
            "job_description": "We are hiring a QA Automation Engineer to build and maintain automated test suites that catch bugs before they reach production. You will write end-to-end and integration tests using Playwright or Cypress (or Selenium WebDriver for legacy suites) in JavaScript or Python, covering critical user flows like signup, checkout, and account settings. You'll configure and maintain automated test execution pipelines in Jenkins, so tests run automatically on every code merge, and investigate and triage test failures to determine whether they're real bugs or flaky tests. You will document test cases and maintain a shared test plan with the QA and engineering teams, and collaborate with developers to reproduce and clearly describe bugs you find, filing detailed tickets in Jira. Required: 2-4 years of QA automation experience, hands-on experience with at least one modern testing framework (Playwright, Cypress, or Selenium), proficiency in JavaScript or Python, and familiarity with CI/CD concepts. Strong attention to detail and a mindset for breaking things on purpose are a must.",
            "difficulty": "mid",
            "num_goals": 4,
            "total_duration_minutes": 45,
            "domain_hint": "qa"
        },
    },
    # --- 16-20: Hard Edge Cases & Constraint Stress ---
    {
        "test_case_name": "Case 16: Junior Copy Editor (Contradictory Requirements)",
        "inputs": {
            "job_name": "Junior Copy Editor",
            "job_description": "We are hiring a Junior Copy Editor for an entry-level position on our editorial team. Day-to-day tasks include proofreading blog posts, marketing emails, and internal documents for spelling, grammar, and punctuation errors, using a style guide (like AP or Chicago Manual of Style) to keep our writing consistent, and flagging awkward phrasing or typos before content goes live. Despite being labeled an entry-level role, the listed requirements ask for 10+ years of experience in complex international treaty arbitration, intellectual property litigation editing, and corporate mergers and acquisitions law, a background typically held by senior legal professionals, not entry-level copy editors, and mismatched with the actual day-to-day duties described above. Reasonable requirements for this role would instead include strong grammar skills and comfort using collaborative editing tools like Google Docs' suggestion mode and Grammarly.",
            "difficulty": "junior",
            "num_goals": 3,
            "total_duration_minutes": 45,
            "domain_hint": "creative"
        },
    },
    {
        "test_case_name": "Case 17: Customer Support Lead (Discriminatory Content)",
        "inputs": {
            "job_name": "Customer Support Lead",
            "job_description": "We are hiring a Customer Support Lead to run our late-night (10pm-6am) call center shift, overseeing a team of 6-8 support agents. Responsibilities include building the nightly staffing schedule, mediating conflicts between team members, stepping in on escalated customer calls, and personally leading customer checkout calls during peak volume. The listed candidate profile explicitly states a preference for 'a masculine male candidate under 30 with a commanding vocal presence,' criteria based on gender, age, and gender expression rather than job-relevant skills, which would be discriminatory and illegal under employment law in most jurisdictions and is unrelated to the actual duties of the role. Legitimate requirements for this position would instead include prior call-center leadership experience, comfort working overnight shifts, and strong conflict-mediation and scheduling skills.",
            "difficulty": "junior",
            "num_goals": 3,
            "total_duration_minutes": 30,
            "domain_hint": "support"
        },
    },
    {
        "test_case_name": "Case 18: Futures Trader (Scalping Specialist - Narrow Scope)",
        "inputs": {
            "job_name": "Futures Trader (Scalping Specialist)",
            "job_description": "We are hiring a Futures Trader specializing in manual scalping strategies for high-volume S&P 500 index futures contracts. This is a narrowly scoped role: essentially all of your day is spent watching order book depth at the microsecond level, tracking execution slippage on every trade, and manually positioning orders within the queue to get better fills. You will sit at a multi-monitor trading desk running Level II market data feeds, executing dozens to hundreds of manual scalp trades per session, typically holding positions for seconds to a few minutes, and closing out all positions before market close with no overnight risk. You'll log slippage and fill-quality metrics after every trading session to refine your queue-positioning approach over time. Required: 5+ years of hands-on futures scalping experience, deep familiarity with order book and Level II data, extremely fast decision-making under pressure, and strict personal risk discipline with defined daily loss limits. This role does not involve strategy coding, portfolio management, or client-facing work; it is purely manual, high-frequency discretionary execution.",
            "difficulty": "senior",
            "num_goals": 12,
            "total_duration_minutes": 90,
            "domain_hint": "finance"
        },
    },
    {
        "test_case_name": "Case 19: Creative Content Manager (Overly Broad Scope)",
        "inputs": {
            "job_name": "Creative Content Manager",
            "job_description": "We are hiring a Creative Content Manager to single-handedly run content across every channel we have. Responsibilities include editing promotional videos, designing social graphics, writing blog articles, building and sending email newsletters, auditing and improving our SEO keyword rankings, planning and running paid search campaigns on Google Ads, organizing and hosting community webinars, scripting and producing podcast episodes, and drafting daily social media copy across Instagram, LinkedIn, and X. This is an unusually broad mandate for a single person; at most companies, these tasks are split across a video editor, graphic designer, copywriter, email marketer, SEO specialist, paid media manager, and podcast producer. Tools you'd need working knowledge of include Adobe Premiere Pro, Canva or Photoshop, an email platform such as Mailchimp or Klaviyo, Google Ads, an SEO tool like Ahrefs or SEMrush, webinar software such as Zoom Webinar, and basic podcast recording and editing software. Required: 3+ years of hands-on marketing or content experience across at least several of these disciplines, and comfort constantly switching between very different types of creative and analytical work.",
            "difficulty": "mid",
            "num_goals": 15,
            "total_duration_minutes": 30,
            "domain_hint": "creative"
        },
    },
    {
        "test_case_name": "Case 20: Junior Financial Analyst (Unrealistic Requirements)",
        "inputs": {
            "job_name": "Junior Financial Analyst",
            "job_description": "We are hiring a Junior Financial Analyst for an entry-level position supporting our finance team with day-to-day spreadsheet work and billing tasks. Typical responsibilities include entering and reconciling invoices, updating simple budget-tracking spreadsheets in Excel, and helping prepare basic monthly expense reports for the finance manager. Despite being labeled entry-level, the listed requirement calls for candidates to have personally managed a private trading portfolio of at least $50 million with a documented, audited annual return of 25%+ for the past ten consecutive years, a track record realistically held by only a small number of elite professional fund managers in the world, not junior-level candidates, and unrelated to the invoice and spreadsheet work described above. Reasonable entry-level requirements would instead include basic Excel proficiency (formulas, pivot tables) and a degree or coursework in finance, accounting, or a related field.",
            "difficulty": "junior",
            "num_goals": 4,
            "total_duration_minutes": 60,
            "domain_hint": "finance"
        },
    }
]

def executeQuestionMakerBatchSuite(testCaseInputSuite: List[Dict[str, Any]]) -> None:
    """
    Sequentially invokes the full question-maker graph for every test case in the suite,
    logging step-by-step node execution progress and rendering the final output JSON.

    Args:
        testCaseInputSuite: List of test case objects containing metadata and input payloads.
    """
    totalCaseCount = len(testCaseInputSuite)
    print("=" * 80)
    print(f"STARTING BATCH EXECUTION FOR {totalCaseCount} TEST CASES")
    print("=" * 80)

    for caseIndex, testCase in enumerate(testCaseInputSuite, start=1):
        caseName = testCase.get("test_case_name", f"Case {caseIndex}")
        inputPayload = testCase.get("inputs", {})

        print(f"\n[{caseIndex}/{totalCaseCount}] Executing: {caseName}")
        print(f"Job Name: {inputPayload.get('job_name')}")
        print(f"Difficulty: {inputPayload.get('difficulty')} | Goals: {inputPayload.get('num_goals')} | Duration: {inputPayload.get('total_duration_minutes')}m")
        print("-" * 60)

        startTimeSeconds = time.time()
        assembledSuiteOutput = None

        try:
            for graphEvent in compiled_question_maker_graph.stream(inputPayload, stream_mode="updates"):
                for nodeName, stateUpdate in graphEvent.items():
                    print(f"  ✓ Finished Node: {nodeName}")

                    if nodeName == "plan_node":
                        extractedGoals = stateUpdate.get("goals", [])
                        print(f"    - Planner produced {len(extractedGoals)} goal(s).")
                        for goalElement in extractedGoals:
                            print(f"      * [{goalElement.goal_id}] {goalElement.topic} (Grounding: {goalElement.need_grounding})")

                    elif nodeName == "retriever_generator_subgraph":
                        retrievedTheories = stateUpdate.get("grounding_theories", [])
                        if retrievedTheories:
                            print(f"    - Retrieved theory for {len(retrievedTheories)} goal(s).")

                    elif nodeName == "generateQuestionItemFromGoal":
                        generatedQuestions = stateUpdate.get("generated_questions", [])
                        if generatedQuestions:
                            print(f"    - Generated {len(generatedQuestions)} question item(s).")

                    elif nodeName == "validateQuestionSuite":
                        validationFeedback = stateUpdate.get("critic_feedback", {})
                        isValidStatus = validationFeedback.get("is_valid")
                        print(f"    - Validator decision: is_valid={isValidStatus}")
                        if validationFeedback.get("failed_goal_ids"):
                            print(f"      * Failed goal IDs: {validationFeedback.get('failed_goal_ids')}")

                    elif nodeName == "assemble_node":
                        assembledSuiteOutput = stateUpdate.get("final_suite")

            executionDuration = time.time() - startTimeSeconds
            print(f"\nCompleted in {executionDuration:.2f} seconds.")

            if assembledSuiteOutput:
                print("--- FINAL GENERATED QUESTION SUITE ---")
                print(assembledSuiteOutput.model_dump_json(indent=2))
            else:
                print("⚠️ Warning: No final question suite produced for this case.")

        except Exception as executionError:
            print(f"❌ Execution failed for '{caseName}': {executionError}")

        print("=" * 80)

    print("\nBATCH TEST SUITE EXECUTION COMPLETE.")


if __name__ == "__main__":
    executeQuestionMakerBatchSuite(BATCH_TEST_CASES)

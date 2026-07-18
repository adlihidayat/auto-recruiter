test_cases = [
    {
        "name": "Loop 1 - Initial Search (Database)",
        "inputs": {
            "topic": "PostgreSQL Performance",
            "goal": "Evaluate candidate's ability to optimize PostgreSQL databases using EXPLAIN ANALYZE.",
            "search_count": 0,
            "messages": [],
        },
    },
    {
        "name": "Loop 1 - Jargon-Heavy Emerging Domain (DeFi)",
        "inputs": {
            "topic": "Decentralized Finance",
            "goal": "Evaluate candidate's understanding of impermanent loss risk in automated market maker (AMM) liquidity pools.",
            "search_count": 0,
            "messages": [],
        },
    },
    {
        "name": "Loop 1 - Physical Craft Skill, Hard to Phrase (Culinary)",
        "inputs": {
            "topic": "Professional Kitchen Knife Skills",
            "goal": "Evaluate candidate's knife skills and mise en place technique for a professional kitchen trial.",
            "search_count": 0,
            "messages": [],
        },
    },
    {
        "name": "Loop 1 - Unsettled/Emerging Guidelines",
        "inputs": {
            "topic": "AI-Generated Content and Authorship Guidelines",
            "goal": "Evaluate candidate's understanding of current content creation guidance on authorship of AI-assisted creative works.",
            "search_count": 0,
            "messages": [],
        },
    },
    {
        "name": "Loop 1 - Regional Craft Jargon (Competitive BBQ)",
        "inputs": {
            "topic": "Competitive BBQ Judging",
            "goal": "Evaluate candidate's ability to judge brisket doneness using the bark, bend test, and stall-management technique.",
            "search_count": 0,
            "messages": [],
        },
    },
    {
        "name": "Loop 1 - Options Trading Strategy (Finance)",
        "inputs": {
            "topic": "Options Trading",
            "goal": "Evaluate candidate's understanding of gamma scalping and how gamma exposure changes with time to expiration.",
            "search_count": 0,
            "messages": [],
        },
    },
    {
        "name": "Loop 1 - Pre-Modern Music Theory (Niche Classical)",
        "inputs": {
            "topic": "Renaissance Counterpoint",
            "goal": "Evaluate candidate's ability to apply species counterpoint rules (first through fifth species) when writing a cantus firmus exercise.",
            "search_count": 0,
            "messages": [],
        },
    },
    {
        "name": "Loop 1 - Contested Empirical Economics",
        "inputs": {
            "topic": "Labor Economics",
            "goal": "Evaluate candidate's ability to explain the empirical debate over minimum wage increases and employment effects (monopsony vs. competitive labor market models).",
            "search_count": 0,
            "messages": [],
        },
    },
    {
        "name": "Loop 1 - Under-Documented Craft (Medieval Manuscript Illumination)",
        "inputs": {
            "topic": "Medieval Manuscript Illumination",
            "goal": "Evaluate candidate's knowledge of period-accurate pigment preparation techniques (e.g. ultramarine from lapis lazuli, verdigris) used in illuminated manuscripts.",
            "search_count": 0,
            "messages": [],
        },
    },
    {
        "name": "Loop 2 - Gap Identification (Medical)",
        "inputs": {
            "topic": "Clinical Diagnosis — Type 2 Diabetes",
            "goal": "Evaluate candidate's knowledge of first-line pharmacological treatment thresholds.",
            "search_count": 1,
            "messages": [
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "call_1a",
                            "name": "tavily_search_results_json",
                            "args": {"query": "metformin first-line therapy Type 2 diabetes ADA guidelines"},
                        },
                        {
                            "id": "call_1b",
                            "name": "tavily_search_results_json",
                            "args": {"query": "Type 2 diabetes HbA1c treatment target thresholds"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1a",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'ada.org/standards-of-care', 'content': "
                        "'Metformin remains first-line pharmacological therapy for most patients with "
                        "newly diagnosed Type 2 diabetes, alongside lifestyle intervention. It is "
                        "generally contraindicated or requires dose adjustment in patients with "
                        "significant renal impairment, though exact eGFR cutoffs are not detailed here.'}]"
                    ),
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1b",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'ada.org/standards-of-care', 'content': "
                        "'The general HbA1c target for most nonpregnant adults is below 7%, though this "
                        "excerpt does not specify how the target shifts for elderly or comorbid "
                        "patients.'}]"
                    ),
                },
            ],
        },
    },
    {
        "name": "Loop 2 - Redundant Query Trap (Privacy Law)",
        "inputs": {
            "topic": "Data Privacy Frameworks",
            "goal": "Evaluate candidate's understanding of generic data retention and right-to-erasure workflows in enterprise systems.",
            "search_count": 1,
            "messages": [
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "call_1a",
                            "name": "tavily_search_results_json",
                            "args": {"query": "GDPR right to erasure Article 17 exceptions"},
                        },
                        {
                            "id": "call_1b",
                            "name": "tavily_search_results_json",
                            "args": {"query": "GDPR data retention period requirements enterprise"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1a",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'gdpr.eu', 'content': "
                        "'Article 17(3) lists exceptions to erasure, including freedom of expression, "
                        "compliance with a legal obligation, and public interest in public health.'}]"
                    ),
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1b",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'gdpr.eu', 'content': "
                        "'There is no single fixed retention period defined by GDPR; Article 5(1)(e) "
                        "requires data be kept no longer than necessary for its documented purpose "
                        "(storage limitation principle).'}, "
                        "{'url': 'edpb.europa.eu', 'content': "
                        "'Organizations are expected to maintain a retention schedule mapping data "
                        "categories to specific retention periods and legal bases, rather than a single "
                        "blanket policy. Some sector-specific laws (e.g. AML financial record rules) "
                        "impose fixed minimums that override the general storage-limitation principle "
                        "for that data category.'}]"
                    ),
                },
            ],
        },
    },
    {
        "name": "Loop 2 - Jurisdiction-Dependent Policy (Real Estate)",
        "inputs": {
            "topic": "Property Possession Guidelines",
            "goal": "Evaluate candidate's understanding of property possession time periods and the 'hostile' element.",
            "search_count": 1,
            "messages": [
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "call_1a",
                            "name": "tavily_search_results_json",
                            "args": {"query": "property possession time period requirements US states"},
                        },
                        {
                            "id": "call_1b",
                            "name": "tavily_search_results_json",
                            "args": {"query": "property possession hostile element formal definition"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1a",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'law.cornell.edu/wex', 'content': "
                        "'Adverse possession statutory periods vary significantly by state, ranging from "
                        "as short as 5 years to as long as 20 years depending on jurisdiction and whether "
                        "color of title or payment of taxes is present.'}]"
                    ),
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1b",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'law.cornell.edu/wex', 'content': "
                        "'Jurisdictions split on whether hostile possession requires a good-faith belief "
                        "of ownership (majority rule) or permits knowing trespass to still qualify "
                        "(minority rule); this is one of the most litigated elements of the doctrine.'}]"
                    ),
                },
            ],
        },
    },
    {
        "name": "Loop 2 - Historical/Non-STEM Depth (Byzantine History)",
        "inputs": {
            "topic": "Byzantine Iconoclasm",
            "goal": "Evaluate candidate's understanding of the theological arguments for and against icon veneration during the Byzantine Iconoclasm (726–842 CE).",
            "search_count": 1,
            "messages": [
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "call_1a",
                            "name": "tavily_search_results_json",
                            "args": {"query": "Byzantine Iconoclasm Leo III causes 726 CE"},
                        },
                        {
                            "id": "call_1b",
                            "name": "tavily_search_results_json",
                            "args": {"query": "iconoclast theological argument against icon veneration"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1a",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'britannica.com', 'content': "
                        "'Emperor Leo III banned the veneration of religious images beginning around 726 "
                        "CE, a policy later reversed and reinstated across two distinct iconoclast "
                        "periods before ending in 842 CE.'}]"
                    ),
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1b",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'oxfordbibliographies.com', 'content': "
                        "'Iconoclasts argued that depicting Christ in an image either separated his divine "
                        "and human natures or confined the uncircumscribable divine nature to matter, "
                        "making icon veneration a form of idolatry.'}]"
                    ),
                },
            ],
        },
    },
    {
        "name": "Loop 2 - Mathematical Niche Sports Rule (Cricket)",
        "inputs": {
            "topic": "Cricket Rules",
            "goal": "Evaluate candidate's understanding of how the Duckworth-Lewis-Stern (DLS) method recalculates a target score in rain-interrupted limited-overs matches.",
            "search_count": 1,
            "messages": [
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "call_1a",
                            "name": "tavily_search_results_json",
                            "args": {"query": "Duckworth-Lewis-Stern method resource table explained"},
                        },
                        {
                            "id": "call_1b",
                            "name": "tavily_search_results_json",
                            "args": {"query": "DLS par score calculation rain interruption cricket"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1a",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'icc-cricket.com', 'content': "
                        "'The DLS method uses a resource table representing the percentage of run-scoring "
                        "resources (overs and wickets remaining) a team has available at any point in an "
                        "innings.'}]"
                    ),
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1b",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'espncricinfo.com', 'content': "
                        "'When a match is shortened, the revised target is calculated by comparing the "
                        "resource percentages available to each team; the par score at any interruption "
                        "point tells the chasing team whether they are ahead of or behind the required "
                        "rate.'}]"
                    ),
                },
            ],
        },
    },
    {
        "name": "Loop 2 - Non-English Source Terminology (TCM)",
        "inputs": {
            "topic": "Traditional Chinese Medicine",
            "goal": "Evaluate candidate's understanding of Zang-fu theory and the functional relationship between the Liver (Gan) and Spleen (Pi) organ systems.",
            "search_count": 1,
            "messages": [
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "call_1a",
                            "name": "tavily_search_results_json",
                            "args": {"query": "Zang-fu theory organ systems TCM overview"},
                        },
                        {
                            "id": "call_1b",
                            "name": "tavily_search_results_json",
                            "args": {"query": "Liver Gan Spleen Pi functional relationship TCM"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1a",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'ncbi.nlm.nih.gov/pmc', 'content': "
                        "'Zang-fu theory organizes the body into five Zang (solid, yin) organs and six "
                        "Fu (hollow, yang) organs, each associated with specific physiological and "
                        "emotional functions distinct from their Western anatomical namesakes.'}]"
                    ),
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1b",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'ncbi.nlm.nih.gov/pmc', 'content': "
                        "'The Liver (Gan) is responsible for the smooth flow of Qi; when Liver Qi "
                        "stagnates it commonly \"invades\" the Spleen (Pi), impairing the Spleen's "
                        "transformation and transportation function.'}]"
                    ),
                },
            ],
        },
    },
    {
        "name": "Loop 2 - Contested Consensus Domain (Nutrition Science)",
        "inputs": {
            "topic": "Nutrition Science",
            "goal": "Evaluate candidate's understanding of the evidence base for intermittent fasting's effect on metabolic health markers.",
            "search_count": 1,
            "messages": [
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "call_1a",
                            "name": "tavily_search_results_json",
                            "args": {"query": "intermittent fasting metabolic health randomized controlled trials"},
                        },
                        {
                            "id": "call_1b",
                            "name": "tavily_search_results_json",
                            "args": {"query": "time-restricted eating insulin sensitivity weight loss"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1a",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'nejm.org', 'content': "
                        "'A 2020 randomized trial found no significant difference in weight loss between "
                        "time-restricted eating and consistent-meal-timing groups when total caloric "
                        "intake was matched.'}]"
                    ),
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1b",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'ncbi.nlm.nih.gov/pmc', 'content': "
                        "'Other trials report modest improvements in insulin sensitivity independent of "
                        "weight change, suggesting a possible circadian-alignment mechanism distinct from "
                        "caloric restriction, though findings are inconsistent across study populations.'}]"
                    ),
                },
            ],
        },
    },
    {
        "name": "Loop 2 - Soil Science / Agriculture",
        "inputs": {
            "topic": "Soil Microbiome",
            "goal": "Evaluate candidate's understanding of how arbuscular mycorrhizal fungi facilitate phosphorus uptake in crop plants.",
            "search_count": 1,
            "messages": [
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "call_1a",
                            "name": "tavily_search_results_json",
                            "args": {"query": "arbuscular mycorrhizal fungi phosphorus uptake mechanism"},
                        },
                        {
                            "id": "call_1b",
                            "name": "tavily_search_results_json",
                            "args": {"query": "mycorrhizal fungi crop plant symbiosis nutrient exchange"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1a",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'sciencedirect.com', 'content': "
                        "'Arbuscular mycorrhizal fungi extend hyphal networks well beyond the root's "
                        "phosphorus depletion zone, accessing immobile soil phosphate pools the plant "
                        "root alone cannot reach.'}]"
                    ),
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1b",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'sciencedirect.com', 'content': "
                        "'In exchange for phosphorus and other nutrients, the host plant supplies the "
                        "fungus with photosynthetically-fixed carbon, typically as sugars, making the "
                        "relationship a mutualistic nutrient-for-carbon exchange.'}]"
                    ),
                },
            ],
        },
    },
    {
        "name": "Loop 3 - Hard Rule Under Thin Data (Contract Management)",
        "inputs": {
            "topic": "Contract Management — Force Majeure",
            "goal": "Evaluate candidate's understanding of force majeure clause creation and operational invocation standards.",
            "search_count": 2,
            "messages": [
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "call_1a",
                            "name": "tavily_search_results_json",
                            "args": {"query": "force majeure clause elements unforeseeability impossibility"},
                        },
                        {
                            "id": "call_1b",
                            "name": "tavily_search_results_json",
                            "args": {"query": "force majeure invocation notice requirements contract drafting"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1a",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'cornell.edu/lawreview', 'content': "
                        "'Courts generally require the invoking party to show the event was not "
                        "reasonably foreseeable and that performance is truly impossible, not merely "
                        "more expensive.'}]"
                    ),
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1b",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'practicallaw.com', 'content': "
                        "'Most clauses require written notice within a specified period, often 5-10 "
                        "business days, of becoming aware of the triggering event, or risk waiving the "
                        "defense.'}]"
                    ),
                },
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "call_2a",
                            "name": "tavily_search_results_json",
                            "args": {"query": "force majeure catch-all language ejusdem generis interpretation"},
                        },
                        {
                            "id": "call_2b",
                            "name": "tavily_search_results_json",
                            "args": {"query": "force majeure pandemic clause enforceability COVID case precedent"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_2a",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'practicallaw.com', 'content': "
                        "'Catch-all language such as \"or any other event beyond the reasonable control "
                        "of the party\" is typically construed narrowly under ejusdem generis, limited to "
                        "events similar in kind to the specifically listed examples.'}]"
                    ),
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_2b",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'cornell.edu/lawreview', 'content': "
                        "'In COVID-19-era disputes, courts largely rejected force majeure defenses where "
                        "the clause did not explicitly reference pandemics or government shutdowns.'}]"
                    ),
                },
            ],
        },
    },
    {
        "name": "Loop 3 - Hard Rule Under Genuinely Thin/Contradictory Data (Nutrition)",
        "inputs": {
            "topic": "Nutrition Science",
            "goal": "Evaluate candidate's understanding of the evidence base for intermittent fasting's effect on metabolic health markers.",
            "search_count": 2,
            "messages": [
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "call_1a",
                            "name": "tavily_search_results_json",
                            "args": {"query": "intermittent fasting metabolic health randomized controlled trials"},
                        },
                        {
                            "id": "call_1b",
                            "name": "tavily_search_results_json",
                            "args": {"query": "time-restricted eating insulin sensitivity weight loss"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1a",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'nejm.org', 'content': "
                        "'A 2020 randomized trial found no significant difference in weight loss between "
                        "time-restricted eating and consistent-meal-timing groups when total caloric "
                        "intake was matched.'}]"
                    ),
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1b",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'ncbi.nlm.nih.gov/pmc', 'content': "
                        "'Other trials report modest improvements in insulin sensitivity independent of "
                        "weight change, though findings are inconsistent across study populations.'}]"
                    ),
                },
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "call_2a",
                            "name": "tavily_search_results_json",
                            "args": {"query": "intermittent fasting circadian rhythm meal timing mechanism"},
                        },
                        {
                            "id": "call_2b",
                            "name": "tavily_search_results_json",
                            "args": {"query": "intermittent fasting study population inconsistency explanation"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_2a",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'ncbi.nlm.nih.gov/pmc', 'content': "
                        "'One proposed mechanism is alignment of eating windows with circadian patterns "
                        "of insulin sensitivity, which is naturally higher earlier in the day, though "
                        "this remains a hypothesis rather than a settled explanation.'}]"
                    ),
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_2b",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'jamanetwork.com', 'content': "
                        "'A meta-analysis noted substantial heterogeneity across trials in fasting "
                        "window length, adherence measurement, and baseline metabolic status, making "
                        "direct comparison across studies difficult and limiting firm conclusions.'}]"
                    ),
                },
            ],
        },
    },
    {
        "name": "Loop 3 - Hard Rule, Regulatory Domain (Aviation)",
        "inputs": {
            "topic": "FAA Part 135 Charter Operations",
            "goal": "Evaluate candidate's understanding of duty-time and rest-requirement rules for single-pilot Part 135 charter operations.",
            "search_count": 2,
            "messages": [
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "call_1a",
                            "name": "tavily_search_results_json",
                            "args": {"query": "FAA Part 135 duty time limits single pilot"},
                        },
                        {
                            "id": "call_1b",
                            "name": "tavily_search_results_json",
                            "args": {"query": "Part 135 rest requirements minimum hours between flights"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1a",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'ecfr.gov', 'content': "
                        "'Under 14 CFR 135.267, a single pilot in unscheduled operations may not exceed "
                        "specified flight-time limits within a 24-hour period, with different limits for "
                        "scheduled vs. unscheduled operations.'}]"
                    ),
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1b",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'faa.gov', 'content': "
                        "'Required rest periods scale with the length of the preceding duty period and "
                        "must be free of all duty obligations to count toward the minimum.'}]"
                    ),
                },
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "call_2a",
                            "name": "tavily_search_results_json",
                            "args": {"query": "Part 135 reserve status duty time calculation rules"},
                        },
                        {
                            "id": "call_2b",
                            "name": "tavily_search_results_json",
                            "args": {"query": "Part 135 duty time cumulative weekly monthly limits"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_2a",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'faa.gov', 'content': "
                        "'Time spent on reserve status counts toward duty time only once a pilot is "
                        "contacted for an assignment, not for the entire reserve availability window.'}]"
                    ),
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_2b",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'ecfr.gov', 'content': "
                        "'Cumulative flight-time limits also apply on 7-day and 30-day (or calendar "
                        "month) bases in addition to the 24-hour limit, layering multiple constraints a "
                        "pilot must track simultaneously.'}]"
                    ),
                },
            ],
        },
    },
    {
        "name": "Loop 3 - Hard Rule, Cutting-Edge Cryptography (zk-SNARKs)",
        "inputs": {
            "topic": "Zero-Knowledge Proofs",
            "goal": "Evaluate candidate's understanding of zk-SNARK circuit design tradeoffs, specifically the trusted setup requirement versus transparent alternatives.",
            "search_count": 2,
            "messages": [
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "call_1a",
                            "name": "tavily_search_results_json",
                            "args": {"query": "zk-SNARK trusted setup ceremony purpose risk"},
                        },
                        {
                            "id": "call_1b",
                            "name": "tavily_search_results_json",
                            "args": {"query": "zk-SNARK circuit arithmetic constraint system basics"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1a",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'vitalik.ca', 'content': "
                        "'zk-SNARKs typically require a trusted setup ceremony that generates public "
                        "parameters; if the toxic waste (secret randomness) from that ceremony is not "
                        "destroyed, a malicious party could forge false proofs.'}]"
                    ),
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1b",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'zkproof.org', 'content': "
                        "'The prover encodes a computation as an arithmetic circuit, then compiles it "
                        "into a rank-1 constraint system (R1CS) that the proving system operates over.'}]"
                    ),
                },
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "call_2a",
                            "name": "tavily_search_results_json",
                            "args": {"query": "zk-STARK transparent setup comparison zk-SNARK tradeoff"},
                        },
                        {
                            "id": "call_2b",
                            "name": "tavily_search_results_json",
                            "args": {"query": "multi-party computation ceremony trusted setup mitigation"},
                        },
                    ],
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_2a",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'zkproof.org', 'content': "
                        "'zk-STARKs avoid a trusted setup entirely (transparent) and are proving faster "
                        "in some scenarios, though they require significantly larger proof sizes than "
                        "SNARKs.'}]"
                    ),
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_2b",
                    "name": "tavily_search_results_json",
                    "content": (
                        "[{'url': 'zkproof.org', 'content': "
                        "'To mitigate the trusted setup risk, modern SNARKs often use multi-party "
                        "computation (MPC) ceremonies where the setup is secure as long as at least one "
                        "participant is honest.'}]"
                    ),
                },
            ],
        },
    }
]

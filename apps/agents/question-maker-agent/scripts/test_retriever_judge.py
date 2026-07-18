import sys
import os
import json
import importlib
from typing import Literal
from pydantic import BaseModel, Field

# Setup path imports for question-maker-agent monorepo structure
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from langchain_core.messages import SystemMessage, HumanMessage
from apps.agents.shared.clients import gemini_flash_lite

# Dynamically import prompts
eval_prompts_module = importlib.import_module("question-maker-agent.prompts.retriever_eval_prompt")
RETRIEVER_EVAL_SYSTEM_INSTRUCTION = eval_prompts_module.RETRIEVER_EVAL_SYSTEM_INSTRUCTION
RETRIEVER_EVAL_USER_TEMPLATE = eval_prompts_module.RETRIEVER_EVAL_USER_TEMPLATE

class RetrieverEvaluationResult(BaseModel):
    action_type_score: Literal[0, 1] = Field(description="Score of 1 if action_type was correct, 0 if it was the wrong move.")
    quality_score: float = Field(description="Score from 0 to 5 for the quality dimension.")
    relatedness_score: float = Field(description="Score from 0 to 5 for the relatedness dimension.")
    justification: str = Field(description="Brief explanation of the scores.")

# Mock Scenarios
scenarios = [
    {
        "name": "Excellent Tool Call (Loop 1, dual queries)",
        "topic": "PostgreSQL Performance",
        "goal": "Evaluate candidate's ability to optimize PostgreSQL databases using EXPLAIN ANALYZE.",
        "loop_iteration": 1,
        "retrieved_data": "None",
        "output_content": (
            'TOOL CALL: web_search\n'
            'ARGS: {"queries": ['
            '"PostgreSQL EXPLAIN ANALYZE reading query plan bottlenecks", '
            '"PostgreSQL index scan vs seq scan performance tuning 2025"]}'
        ),
        # Expect: true, tool_call, quality ~5, relatedness ~5
    },
    {
        "name": "Poor Tool Call — soft-skill trap, non-technical domain",
        "topic": "B2B SaaS Marketing",
        "goal": "Evaluate candidate's ability to design a lead-scoring model for a B2B SaaS funnel.",
        "loop_iteration": 1,
        "retrieved_data": "None",
        "output_content": (
            'TOOL CALL: web_search\n'
            'ARGS: {"queries": ['
            '"good marketing communication skills", '
            '"how to be a great marketer"]}'
        ),
        # Expect: true, tool_call, quality ~1-2 (generic/soft-skill, no domain facts), relatedness ~2
    },
    {
        "name": "Redundant Tool Call — Loop 2 repeats Loop 1 despite full round of data",
        "topic": "GDPR Compliance",
        "goal": "Evaluate candidate's understanding of GDPR data retention and right-to-erasure obligations.",
        "loop_iteration": 2,
        "retrieved_data": (
            "Loop 1 Queries: ['GDPR right to erasure Article 17 exceptions', "
            "'GDPR data retention period requirements enterprise']\n"
            "Chunk 1 (source: gdpr.eu): Article 17 grants data subjects the right to erasure "
            "('right to be forgotten') when personal data is no longer necessary for the "
            "purpose it was collected for.\n"
            "Chunk 2 (source: gdpr.eu): Article 17(3) lists exceptions to erasure, including "
            "exercising the right of freedom of expression, compliance with a legal obligation, "
            "public interest in the area of public health, and establishment/exercise/defense "
            "of legal claims.\n"
            "Chunk 3 (source: gdpr.eu): A controller processing data under a legal obligation "
            "(e.g. tax law requiring record retention) may refuse an erasure request for the "
            "duration that obligation applies.\n"
            "Chunk 4 (source: ico.org.uk guidance): Erasure requests must be actioned 'without "
            "undue delay' and in any event within one month, extendable by two further months "
            "for complex requests.\n"
            "Chunk 5 (source: ico.org.uk guidance): Where personal data has been disclosed to "
            "third parties, the controller must inform those recipients of the erasure request "
            "unless this proves impossible or involves disproportionate effort.\n"
            "Chunk 6 (source: gdpr.eu): There is no single fixed retention period defined by "
            "GDPR; Article 5(1)(e) instead requires data be kept 'no longer than is necessary' "
            "for the purposes for which it is processed (storage limitation principle).\n"
            "Chunk 7 (source: gdpr.eu): Controllers must be able to justify their chosen "
            "retention period against a specific, documented purpose — an arbitrary or "
            "indefinite retention period is itself a compliance violation.\n"
            "Chunk 8 (source: European Data Protection Board guidelines): Some sector-specific "
            "EU/member-state laws do impose fixed minimums (e.g. financial transaction records "
            "under AML law), which can override the general storage-limitation principle for "
            "that category of data.\n"
            "Chunk 9 (source: European Data Protection Board guidelines): Organizations are "
            "expected to maintain a retention schedule mapping data categories to specific "
            "retention periods and legal bases, rather than a single blanket policy.\n"
            "Chunk 10 (source: ico.org.uk guidance): Failure to define concrete retention "
            "periods is one of the most common findings in GDPR compliance audits, cited more "
            "often than erasure-request mishandling itself."
        ),
        "action_type": "tool_call",
        "output_content": (
            'TOOL CALL: web_search\n'
            'ARGS: {"queries": ['
            '"GDPR right to erasure Article 17 exceptions", '
            '"GDPR data retention requirements"]}'
        ),
        # Expect: action_type_score = 1 — TRUE. The retrieved data still lacks concrete,
        # checkable specifics (e.g. what a defensible retention schedule actually looks like,
        # or the AML-style sector-override pattern in Chunk 8) — continuing to search is the
        # right call. quality ~2, relatedness ~2: BOTH queries are near-verbatim repeats of the
        # loop 1 queries and ignore the two gaps the 10 chunks actually expose — (a) how a
        # retention schedule should be structured per-category (Chunk 9), and (b) how
        # sector-specific fixed-minimum laws interact with the general storage-limitation
        # principle (Chunk 8). A well-targeted loop 2 query would chase one of those, not repeat
        # loop 1 almost word-for-word.
    },
    {
        "name": "Excellent Tool Call — Loop 2 targets identified gap, medical domain",
        "topic": "Clinical Diagnosis — Type 2 Diabetes",
        "goal": "Evaluate candidate's knowledge of first-line pharmacological treatment thresholds for Type 2 Diabetes.",
        "loop_iteration": 2,
        "retrieved_data": (
            "Loop 1 Queries: ['Type 2 diabetes first-line medication metformin guidelines 2024', "
            "'Type 2 diabetes HbA1c treatment target thresholds']\n"
            "Chunk 1 (source: ADA Standards of Care 2024): Metformin remains first-line "
            "pharmacological therapy for most patients with newly diagnosed Type 2 diabetes, "
            "alongside lifestyle intervention.\n"
            "Chunk 2 (source: ADA Standards of Care 2024): Metformin is generally contraindicated "
            "or requires dose adjustment in patients with significant renal impairment, though "
            "the exact eGFR cutoffs are not specified in this excerpt.\n"
            "Chunk 3 (source: ADA Standards of Care 2024): For patients with established "
            "cardiovascular disease, GLP-1 receptor agonists or SGLT2 inhibitors may be "
            "preferred as an add-on or alternative regardless of baseline HbA1c.\n"
            "Chunk 4 (source: ADA Standards of Care 2024): Metformin should be initiated at a "
            "low dose and titrated gradually to reduce gastrointestinal side effects, which are "
            "the most common reason for early discontinuation.\n"
            "Chunk 5 (source: NIH clinical review): Long-term metformin use is associated with "
            "vitamin B12 deficiency; periodic monitoring is recommended, particularly in "
            "patients with anemia or peripheral neuropathy symptoms.\n"
            "Chunk 6 (source: ADA Standards of Care 2024): General HbA1c target for most "
            "nonpregnant adults is below 7%, though this excerpt does not specify how the "
            "target shifts for elderly or comorbid patients.\n"
            "Chunk 7 (source: ADA Standards of Care 2024): Less stringent HbA1c goals may be "
            "appropriate for patients with limited life expectancy, extensive comorbid "
            "conditions, or a history of severe hypoglycemia — exact numeric ranges not given "
            "in this excerpt.\n"
            "Chunk 8 (source: NIH clinical review): Tighter HbA1c targets (e.g. below 6.5%) may "
            "be considered for younger patients early in disease course without significant "
            "cardiovascular disease, if achievable without hypoglycemia.\n"
            "Chunk 9 (source: NIH clinical review): Renal function should be reassessed "
            "periodically in patients on long-term metformin, as eGFR can decline with age "
            "independent of diabetes control.\n"
            "Chunk 10 (source: ADA Standards of Care 2024): Metformin dosing and continuation "
            "decisions should be individualized based on renal function trends rather than a "
            "single eGFR measurement at diagnosis."
        ),
        "action_type": "tool_call",
        "output_content": (
            'TOOL CALL: web_search\n'
            'ARGS: {"queries": ['
            '"metformin contraindications renal impairment eGFR threshold", '
            '"HbA1c target ranges by comorbidity ADA 2024"]}'
        ),
        # Expect: action_type_score = 1. Both queries directly chase the two explicit gaps the
        # 10 chunks leave open: Chunk 2 flags renal contraindication without giving the eGFR
        # cutoff, and Chunks 6-7 flag comorbidity-adjusted HbA1c targets without giving numbers.
        # quality ~5, relatedness ~5 — precise, non-redundant, and each targets a distinct
        # unresolved thread rather than re-running loop 1's queries.
    },
    {
        "name": "Excellent Grounding Theory — well-cited, concrete criteria",
        "topic": "PostgreSQL Performance",
        "goal": "Evaluate candidate's ability to optimize PostgreSQL databases using EXPLAIN ANALYZE.",
        "loop_iteration": 3,
        "retrieved_data": (
            "Loop 1 Queries: ['PostgreSQL EXPLAIN ANALYZE reading query plan bottlenecks', "
            "'PostgreSQL index scan vs seq scan performance tuning 2025']\n"
            "Chunk 1 (source: postgresql.org/docs): EXPLAIN ANALYZE actually executes the query and "
            "reports real elapsed time and row counts per plan node, unlike plain EXPLAIN which only "
            "estimates.\n"
            "Chunk 2 (source: postgresql.org/docs): Plan nodes are read bottom-up; the innermost nodes "
            "execute first and feed rows upward into joins, sorts, and aggregates.\n"
            "Chunk 3 (source: postgresql.org/docs): A sequential scan on a large table combined with a "
            "highly selective filter condition is a classic sign of a missing or unused index.\n"
            "Chunk 4 (source: postgresql.org/docs): The 'cost' values shown in EXPLAIN (without ANALYZE) "
            "are planner estimates in arbitrary units, not milliseconds, and should not be confused with "
            "actual timing.\n"
            "Chunk 5 (source: use-the-index-luke.com): A large gap between estimated and actual row "
            "counts on a node usually indicates stale table statistics; running ANALYZE on the table "
            "often resolves it.\n"
            "Chunk 6 (source: use-the-index-luke.com): An index scan is not automatically faster than a "
            "sequential scan — for low-selectivity filters (returning a large fraction of the table), "
            "the planner correctly prefers a seq scan.\n"
            "Chunk 7 (source: postgresql.org/docs): A Bitmap Heap Scan combined with a Bitmap Index Scan "
            "is typically chosen when a moderate number of rows match, as a middle ground between full "
            "index scan and seq scan.\n"
            "Chunk 8 (source: use-the-index-luke.com): Index-only scans avoid a heap fetch entirely when "
            "all needed columns are present in the index, but require the visibility map to be up to date "
            "(i.e. a recent VACUUM).\n"
            "Chunk 9 (source: postgresql.org/docs): EXPLAIN ANALYZE by default does not show buffer "
            "usage; the BUFFERS option must be added to see shared hit/read counts, which reveal whether "
            "data came from cache or disk.\n"
            "Chunk 10 (source: use-the-index-luke.com): A high ratio of 'shared read' to 'shared hit' in "
            "buffer output indicates the working set doesn't fit in shared_buffers, pointing to a memory "
            "configuration issue rather than a missing index.\n"
            "\n"
            "Loop 2 Queries: ['PostgreSQL join method nested loop hash merge EXPLAIN', "
            "'PostgreSQL EXPLAIN ANALYZE actual vs estimated rows statistics']\n"
            "Chunk 11 (source: postgresql.org/docs): Nested Loop joins are efficient when the outer "
            "relation is small or when an index exists on the inner relation's join key; otherwise they "
            "degrade badly on large tables.\n"
            "Chunk 12 (source: postgresql.org/docs): Hash Join builds an in-memory hash table from the "
            "smaller relation and probes it with the larger relation; it's preferred for large, "
            "unsorted equi-joins.\n"
            "Chunk 13 (source: postgresql.org/docs): Merge Join requires both inputs sorted on the join "
            "key and is efficient when the data is already sorted (e.g. via an index) or when both sides "
            "are large and roughly equal in size.\n"
            "Chunk 14 (source: use-the-index-luke.com): A Nested Loop appearing over a large inner "
            "relation with no index is a strong red flag in an EXPLAIN ANALYZE output — it usually means "
            "the planner picked a bad plan due to stale statistics or a missing index.\n"
            "Chunk 15 (source: postgresql.org/docs): The 'loops' value on a plan node multiplies the "
            "per-loop actual time and rows; a node executed 10,000 times with even a small per-loop cost "
            "can dominate total query time.\n"
            "Chunk 16 (source: use-the-index-luke.com): Distinguishing 'actual rows' from 'rows' "
            "(estimated) at each plan node is the single most important skill for diagnosing planner "
            "misestimation — a 100x gap signals the optimizer is working from bad assumptions.\n"
            "Chunk 17 (source: postgresql.org/docs): Increasing default_statistics_target for a specific "
            "column improves estimate accuracy for skewed distributions, at the cost of slower ANALYZE "
            "runs and slightly larger planning time.\n"
            "Chunk 18 (source: postgresql.org/docs): Extended statistics (CREATE STATISTICS) can capture "
            "correlations between columns that the default per-column statistics miss, improving "
            "estimates for multi-column filters.\n"
            "Chunk 19 (source: use-the-index-luke.com): Function calls or type casts wrapped around an "
            "indexed column in a WHERE clause typically prevent the planner from using the index at all, "
            "forcing a seq scan regardless of selectivity.\n"
            "Chunk 20 (source: postgresql.org/docs): A partial index (WHERE clause on the index itself) "
            "can dramatically reduce index size and improve scan speed when queries consistently filter "
            "on a known subset of rows.\n"
            "\n"
            "Loop 3 Queries: ['PostgreSQL parallel query plan EXPLAIN ANALYZE workers', "
            "'PostgreSQL EXPLAIN ANALYZE common misdiagnosis mistakes']\n"
            "Chunk 21 (source: postgresql.org/docs): Parallel Seq Scan splits table blocks across "
            "worker processes; the 'Workers Planned' vs 'Workers Launched' values can differ if the "
            "system is under resource pressure at execution time.\n"
            "Chunk 22 (source: postgresql.org/docs): A Gather or Gather Merge node combines results from "
            "parallel workers; its actual time includes worker startup overhead, which can make small "
            "parallel queries slower than a single-worker plan.\n"
            "Chunk 23 (source: use-the-index-luke.com): max_parallel_workers_per_gather set too low is a "
            "common reason a query that 'should' parallelize according to cost estimates doesn't, and "
            "this won't be obvious from EXPLAIN ANALYZE output alone without checking config.\n"
            "Chunk 24 (source: use-the-index-luke.com): A frequent misdiagnosis is blaming 'a slow query' "
            "on the wrong plan node — always start from the node with the highest actual total time "
            "(self time = node time minus children's time), not the deepest or top-level node by default.\n"
            "Chunk 25 (source: postgresql.org/docs): Sort operations that spill to disk (visible as "
            "'Sort Method: external merge' with a disk size) instead of fitting in work_mem are a common "
            "hidden cost not obvious from row counts alone.\n"
            "Chunk 26 (source: use-the-index-luke.com): Increasing work_mem can convert a disk-spilling "
            "sort or hash into an in-memory operation, but must be weighed against total memory use "
            "since work_mem applies per sort/hash operation, potentially per connection.\n"
            "Chunk 27 (source: postgresql.org/docs): CTEs written with the MATERIALIZED keyword (or, in "
            "older Postgres versions, all CTEs by default) act as optimization fences, preventing the "
            "planner from pushing filters into the CTE — visible as an extra CTE Scan node.\n"
            "Chunk 28 (source: use-the-index-luke.com): A common mistake is reading total query time "
            "from the top Gather/Limit node without checking whether most of the time was spent on "
            "planning vs execution — EXPLAIN ANALYZE reports both separately.\n"
            "Chunk 29 (source: postgresql.org/docs): Trigger execution time is included in EXPLAIN "
            "ANALYZE output as a separate 'Trigger' line and is easy to overlook when it's the actual "
            "dominant cost on an INSERT/UPDATE query.\n"
            "Chunk 30 (source: use-the-index-luke.com): Running EXPLAIN ANALYZE on a production system "
            "actually executes writes for INSERT/UPDATE/DELETE queries — the safe pattern is to wrap it "
            "in a transaction and ROLLBACK, or use EXPLAIN (ANALYZE, dry-run patterns) via extensions."
        ),
        "output_content": (
            'GENERATE_GROUNDING:\n'
            'ARGS: {"title": "Reading and Diagnosing PostgreSQL Query Plans with EXPLAIN ANALYZE", '
            '"content": '
            '"EXPLAIN ANALYZE actually executes the query and reports real elapsed time and row '
            'counts at each plan node, unlike plain EXPLAIN, whose cost figures are planner '
            'estimates in arbitrary units rather than milliseconds. Plans are read bottom-up: '
            'the innermost nodes execute first and feed rows upward into joins, sorts, and '
            'aggregates.\\n\\n'
            'Scan Types. A sequential scan on a large table paired with a highly selective '
            'filter is a classic sign of a missing or unused index, but an index scan is not '
            'automatically better -- for low-selectivity filters that return a large fraction '
            'of the table, the planner correctly prefers a seq scan. A Bitmap Heap Scan over a '
            'Bitmap Index Scan is typically chosen as a middle ground when a moderate number of '
            'rows match. Index-only scans skip the heap fetch entirely when every needed column '
            'is present in the index, but this requires the visibility map to be current, i.e. '
            'a recent VACUUM. Function calls or type casts wrapped around an indexed column in '
            'a WHERE clause usually prevent the index from being used at all, forcing a seq '
            'scan regardless of selectivity; a partial index (with its own WHERE clause) can '
            'shrink index size and speed up scans when queries consistently filter on a known '
            'subset of rows.\\n\\n'
            'Join Methods. Nested Loop joins are efficient when the outer relation is small or '
            'the inner relation is indexed on the join key, but degrade badly on large tables '
            'otherwise -- a Nested Loop over a large, unindexed inner relation in an EXPLAIN '
            'ANALYZE output is a strong red flag for a bad plan. Hash Join builds an in-memory '
            'hash table from the smaller relation and is preferred for large, unsorted equi-'
            'joins. Merge Join needs both inputs pre-sorted on the join key and suits cases '
            'where the data is already sorted or both sides are large and similarly sized. The '
            '\'loops\' value on a node multiplies per-loop time and rows, so a node executed '
            'thousands of times can dominate total query time even at low per-loop cost.\\n\\n'
            'Statistics and Misestimation. A large gap between a node\'s estimated and actual '
            'row counts usually points to stale table statistics, fixable by running ANALYZE. '
            'Raising default_statistics_target for a specific column improves estimates for '
            'skewed distributions at the cost of slower ANALYZE runs, while extended statistics '
            '(CREATE STATISTICS) capture cross-column correlations that per-column statistics '
            'miss.\\n\\n'
            'Buffers and Memory. EXPLAIN ANALYZE does not show buffer usage by default; adding '
            'the BUFFERS option reveals shared hit/read counts, and a high ratio of shared read '
            'to shared hit means the working set does not fit in shared_buffers -- a memory '
            'configuration issue, not a missing index. Sort operations that spill to disk '
            '(shown as \'Sort Method: external merge\' with a disk size) are a common hidden '
            'cost; increasing work_mem can convert a spilling sort or hash into an in-memory '
            'operation, but the setting applies per sort/hash operation and potentially per '
            'connection, so raising it carries a real memory-budget tradeoff.\\n\\n'
            'Parallel Execution. Parallel Seq Scan splits table blocks across worker processes; '
            'Workers Planned and Workers Launched can diverge under resource pressure. Gather '
            'and Gather Merge nodes combine worker output, and their actual time includes '
            'worker startup overhead, which can make small parallel queries slower than a '
            'single-worker plan. A query that cost-estimates suggest should parallelize but '
            'doesn\'t is often explained by max_parallel_workers_per_gather being set too low -- '
            'something not visible from the EXPLAIN ANALYZE output alone.\\n\\n'
            'Common Misdiagnoses. A frequent mistake is blaming the wrong plan node for slowness; '
            'the right starting point is the node with the highest self time (its own time minus '
            'its children\'s time), not the deepest or top-level node by default. MATERIALIZED '
            'CTEs (or, on older Postgres versions, all CTEs) act as optimization fences that '
            'block filter pushdown, visible as an extra CTE Scan node. Total reported time '
            'should be checked against the planning-vs-execution split EXPLAIN ANALYZE provides '
            'separately, since a slow-looking top node can actually reflect planning time. '
            'Trigger execution appears as its own \'Trigger\' line and is easy to overlook when '
            'it is the actual dominant cost on an INSERT or UPDATE. Finally, running EXPLAIN '
            'ANALYZE on a production system genuinely executes writes for INSERT/UPDATE/DELETE '
            'queries, so the safe pattern for testing is to wrap it in a transaction and '
            'ROLLBACK."}'
        ),
        # Expect: true, generate_grounding, quality ~5, relatedness ~5
    },
    {
        "name": "Hallucinated Grounding Theory",
        "topic": "React Performance",
        "goal": "Evaluate candidate's understanding of React re-render optimization with memoization.",
        "loop_iteration": 3,
        "retrieved_data": (
            "Loop 1 Queries: ['React useMemo useCallback dependency array behavior', "
            "'React.memo component re-render prevention shallow comparison']\n"
            "Chunk 1 (source: react.dev): useMemo recomputes a cached value only when one of the values "
            "in its dependency array changes between renders.\n"
            "Chunk 2 (source: react.dev): useCallback returns a memoized version of a callback function "
            "that only changes if one of its dependencies changes, primarily useful when passing "
            "callbacks to optimized child components.\n"
            "Chunk 3 (source: react.dev): React.memo wraps a component and skips re-rendering it if its "
            "props are shallowly equal to the previous render's props.\n"
            "Chunk 4 (source: react.dev): Passing a new object or array literal as a prop on every render "
            "defeats React.memo's shallow comparison, since the reference changes even if the contents "
            "are identical.\n"
            "Chunk 5 (source: kentcdodds.com): Overusing useMemo/useCallback for cheap computations adds "
            "overhead (dependency comparison, memory for cached values) that can outweigh the benefit — "
            "profile before optimizing.\n"
            "Chunk 6 (source: react.dev): A component re-renders when its state changes, its parent "
            "re-renders, or its context value changes — memoization only addresses the second cause.\n"
            "Chunk 7 (source: kentcdodds.com): Moving state down to the smallest component that needs it "
            "('state colocation') often eliminates unnecessary re-renders more effectively than adding "
            "memoization to a large parent tree.\n"
            "Chunk 8 (source: react.dev): The dependency array for useMemo/useCallback should include "
            "every reactive value referenced inside the function; omitting one can cause the memoized "
            "value to become stale.\n"
            "Chunk 9 (source: react.dev): React's ESLint plugin (eslint-plugin-react-hooks) can "
            "automatically flag missing dependencies in useMemo/useCallback/useEffect dependency arrays.\n"
            "Chunk 10 (source: kentcdodds.com): useMemo is not a semantic guarantee in React — the React "
            "team has stated the cache may be discarded and recomputed even without a dependency change, "
            "under memory pressure, in current React versions.\n"
            "\n"
            "Loop 2 Queries: ['React Context re-render performance splitting providers', "
            "'React reconciliation key prop list rendering performance']\n"
            "Chunk 11 (source: react.dev): Every consumer of a Context re-renders whenever the Context "
            "value changes, regardless of which part of the value object a given consumer actually uses.\n"
            "Chunk 12 (source: kentcdodds.com): Splitting a single large Context into multiple "
            "smaller, more granular Contexts limits re-renders to only the consumers of the Context that "
            "actually changed.\n"
            "Chunk 13 (source: react.dev): The 'key' prop in a list tells React's reconciler which array "
            "item corresponds to which component instance across renders, preventing unnecessary "
            "unmount/remount cycles.\n"
            "Chunk 14 (source: react.dev): Using array index as a key is discouraged when the list can be "
            "reordered, filtered, or have items inserted/removed, since it can cause React to associate "
            "the wrong state with the wrong item.\n"
            "Chunk 15 (source: kentcdodds.com): Memoizing a Context provider's value object itself (via "
            "useMemo) is necessary even after splitting contexts, since an unmemoized value object is a "
            "new reference on every parent render.\n"
            "Chunk 16 (source: react.dev): React batches multiple state updates that occur within the "
            "same event handler into a single re-render for performance.\n"
            "Chunk 17 (source: react.dev): As of React 18, automatic batching extends to updates inside "
            "promises, setTimeout, and native event handlers, not just React's own synthetic event "
            "handlers.\n"
            "Chunk 18 (source: kentcdodds.com): Custom hooks that internally call useState or useContext "
            "can be a hidden source of re-renders that isn't obvious from reading the consuming "
            "component's code alone.\n"
            "Chunk 19 (source: react.dev): The React DevTools Profiler can highlight which components "
            "re-rendered on a given commit and, optionally, why (props changed, state changed, "
            "hooks changed, parent re-rendered).\n"
            "Chunk 20 (source: react.dev): A component re-rendering does not necessarily mean the DOM "
            "was updated — React still diffs the virtual DOM output and only commits actual DOM changes "
            "when the rendered output differs.\n"
            "\n"
            "Loop 3 Queries: ['React memoization anti-patterns common mistakes', "
            "'React Server Components re-render model differences']\n"
            "Chunk 21 (source: kentcdodds.com): A common anti-pattern is wrapping every single "
            "component in React.memo 'just in case' — this adds a shallow comparison cost to every "
            "render without addressing the actual source of unnecessary re-renders.\n"
            "Chunk 22 (source: react.dev): React.memo's default shallow comparison can be overridden "
            "with a custom comparison function as a second argument, though the React docs caution "
            "this is rarely necessary and can introduce bugs if implemented incorrectly.\n"
            "Chunk 23 (source: kentcdodds.com): Inline arrow functions passed as event handler props "
            "(e.g. onClick={() => doThing()}) create a new function reference every render, which "
            "matters only if that prop feeds into a memoized child — otherwise it's a non-issue.\n"
            "Chunk 24 (source: react.dev): The useTransition and useDeferredValue hooks let developers "
            "mark certain state updates as lower priority, allowing React to keep the UI responsive "
            "during expensive re-renders rather than preventing the re-render itself.\n"
            "Chunk 25 (source: react.dev): React Server Components render on the server and do not "
            "re-render on the client in response to client-side state changes at all, since they have "
            "no client-side representation to re-render.\n"
            "Chunk 26 (source: react.dev): Client Components within a Server Component tree follow the "
            "normal client-side re-render model (state, props, context) independent of their parent "
            "Server Component's server-only rendering.\n"
            "Chunk 27 (source: kentcdodds.com): Premature memoization is listed as a more common "
            "performance mistake in practice than under-memoization, since most components are cheap "
            "enough that re-rendering them is not actually the bottleneck.\n"
            "Chunk 28 (source: react.dev): Profiling with React DevTools before adding memoization is "
            "explicitly recommended in the official docs, framed as 'you might not need memo'.\n"
            "Chunk 29 (source: kentcdodds.com): Extracting expensive child components and wrapping only "
            "those in React.memo, rather than memoizing broadly, is presented as the more targeted "
            "approach.\n"
            "Chunk 30 (source: react.dev): No source in this set makes any claim about a compiler-based "
            "automatic memoization feature changing memoization APIs or requirements."
    ),
        "output_content": (
            'GENERATE_GROUNDING:\n'
            'ARGS: {"title": "React Re-render Optimization: Memoization Tools and When They Matter", '
            '"content": '
            '"useMemo recomputes a cached value only when a value in its dependency array '
            'changes between renders; useCallback is the same idea applied to function '
            'references, mainly useful when passing callbacks into optimized child components. '
            'React.memo wraps a component and skips re-rendering it when its props are shallowly '
            'equal to the previous render\'s props -- but passing a new object or array literal '
            'as a prop on every render defeats this, since the reference changes even when the '
            'contents don\'t. A component re-renders for three reasons: its own state changes, '
            'its parent re-renders, or a context value it reads changes -- memoization via '
            'React.memo only addresses the second cause. Overusing useMemo or useCallback on '
            'cheap computations adds its own overhead (dependency comparison, cached-value '
            'memory) that can outweigh the benefit, so profiling before optimizing matters; '
            'moving state down to the smallest component that needs it (\'state colocation\') '
            'often eliminates unnecessary re-renders more effectively than memoizing a large '
            'parent tree. As of React 19, the compiler ships built-in automatic memoization that '
            'statically analyzes components and eliminates the need for useMemo, useCallback, '
            'and React.memo entirely -- manual memoization is no longer necessary in any case. '
            'The dependency array for useMemo and useCallback should list every reactive value '
            'referenced inside the function, since omitting one can leave the cached value '
            'stale; eslint-plugin-react-hooks can flag missing dependencies automatically, '
            'though useMemo itself is not a strict guarantee -- React may discard and recompute '
            'the cache even without a dependency change under memory pressure.\\n\\n'
            'Context re-renders every consumer whenever the context value changes, regardless of '
            'which part of that value a given consumer actually reads; splitting one large '
            'context into several smaller, more granular contexts limits re-renders to the '
            'consumers of whichever context actually changed. Even after splitting, the '
            'provider\'s value object itself still needs useMemo, since an unmemoized object '
            'literal is a new reference on every parent render. The \'key\' prop tells React\'s '
            'reconciler which array item maps to which component instance across renders; using '
            'array index as a key is discouraged for lists that can be reordered, filtered, or '
            'have items inserted or removed, since it can associate the wrong state with the '
            'wrong item. React batches multiple state updates within the same event handler into '
            'a single re-render, and as of React 18 this automatic batching extends to updates '
            'inside promises, setTimeout, and native event handlers, not just React\'s own '
            'synthetic events. The React DevTools Profiler shows which components re-rendered on '
            'a given commit and, optionally, why -- props, state, hooks, or a re-rendering '
            'parent. A component re-rendering does not necessarily mean the DOM changed, since '
            'React still diffs the virtual DOM output and only commits actual DOM updates when '
            'the rendered output differs.\\n\\n'
            'Common anti-patterns include wrapping every component in React.memo \'just in case,\' '
            'which adds a shallow-comparison cost everywhere without addressing the actual '
            'source of unnecessary re-renders -- premature memoization is, in practice, a more '
            'common mistake than under-memoization, since most components are cheap enough that '
            're-rendering them isn\'t the real bottleneck. Inline arrow functions passed as event '
            'handlers create a new function reference every render, but this only matters if '
            'that prop feeds into a memoized child. The React docs explicitly recommend '
            'profiling with DevTools before adding memoization at all. useTransition and '
            'useDeferredValue let lower-priority state updates stay responsive during expensive '
            're-renders without preventing the re-render itself. React Server Components render '
            'on the server and have no client-side representation to re-render at all in '
            'response to client state changes; Client Components nested inside a Server '
            'Component tree still follow the ordinary client-side re-render model independent of '
            'their parent\'s server-only rendering."}'
        ),
        # Expect: true, generate_grounding, quality ~1 (fact #2 is not supported by the single retrieved
        # chunk — hallucinated/overstated), relatedness ~2 (fabricates beyond retrieved data)
    },
    {
        "name": "Weak/Generic Grounding Theory",
        "topic": "Contract Law — Force Majeure",
        "goal": "Evaluate candidate's understanding of force majeure clause drafting and invocation standards.",
        "loop_iteration": 3,
        "retrieved_data": (
            "Loop 1 Queries: ['force majeure clause elements unforeseeability impossibility', "
            "'force majeure invocation notice requirements contract drafting']\n"
            "Chunk 1 (source: law review article, Cornell LQ): Force majeure clauses excuse "
            "performance when an unforeseeable event outside a party's control prevents contractual "
            "performance.\n"
            "Chunk 2 (source: law review article, Cornell LQ): Courts generally require the invoking "
            "party to show the event was not reasonably foreseeable at contract formation and that "
            "performance is truly impossible, not merely more expensive or less profitable.\n"
            "Chunk 3 (source: Practical Law drafting guide): A well-drafted force majeure clause "
            "should enumerate specific triggering events (e.g. war, natural disaster, government "
            "action) rather than relying solely on generic language like 'events beyond reasonable "
            "control'.\n"
            "Chunk 4 (source: Practical Law drafting guide): Most force majeure clauses require the "
            "invoking party to give written notice within a specified period (e.g. 5-10 business "
            "days) of becoming aware of the triggering event, or risk waiving the defense.\n"
            "Chunk 5 (source: Cornell LQ): The invoking party typically bears the burden of proving "
            "both that the event occurred and that it was the actual, direct cause of the "
            "non-performance — a merely contributing factor is usually insufficient.\n"
            "Chunk 6 (source: Practical Law drafting guide): Clauses should specify whether force "
            "majeure suspends the obligation temporarily or permits outright termination if the event "
            "continues beyond a stated duration (e.g. 90 days).\n"
            "Chunk 7 (source: Cornell LQ): Mere increased cost of performance, without true "
            "impossibility, is the single most common reason courts reject a force majeure defense in "
            "commercial disputes.\n"
            "Chunk 8 (source: Practical Law drafting guide): A mitigation obligation is often implied "
            "or expressly drafted, requiring the invoking party to take reasonable steps to reduce the "
            "impact of the triggering event.\n"
            "Chunk 9 (source: Cornell LQ): Whether a pandemic qualifies as force majeure depends "
            "heavily on the specific clause language — clauses listing 'epidemic' or 'pandemic' "
            "explicitly are far more likely to succeed than those relying on catch-all language.\n"
            "Chunk 10 (source: Practical Law drafting guide): Catch-all language (e.g. 'or any other "
            "event beyond the reasonable control of the party') is typically construed narrowly under "
            "the ejusdem generis principle — interpreted as limited to events similar in kind to the "
            "specifically listed examples.\n"
            "\n"
            "Loop 2 Queries: ['force majeure vs frustration of purpose doctrine difference', "
            "'force majeure clause governing law jurisdiction variation']\n"
            "Chunk 11 (source: Cornell LQ): Frustration of purpose is a common-law doctrine distinct "
            "from a contractual force majeure clause — it applies even absent a force majeure clause, "
            "but requires the contract's fundamental purpose to be destroyed, not just performance "
            "made harder.\n"
            "Chunk 12 (source: Cornell LQ): Unlike force majeure, frustration of purpose typically "
            "voids the contract entirely rather than merely suspending obligations.\n"
            "Chunk 13 (source: American Bar Association guide): In the absence of an express force "
            "majeure clause, parties may fall back on the UCC's commercial impracticability doctrine "
            "(UCC § 2-615) for contracts involving the sale of goods.\n"
            "Chunk 14 (source: American Bar Association guide): Common law jurisdictions vary "
            "significantly in how narrowly they construe force majeure clauses — English courts "
            "historically apply a stricter standard than many US state courts.\n"
            "Chunk 15 (source: American Bar Association guide): Civil law jurisdictions (e.g. France) "
            "often have a statutory force majeure concept independent of contract language, unlike "
            "common law systems where the doctrine exists only if the contract creates it.\n"
            "Chunk 16 (source: Cornell LQ): Choice-of-law clauses in a contract determine which "
            "jurisdiction's force majeure standard applies, which can materially change the outcome of "
            "an otherwise identical factual dispute.\n"
            "Chunk 17 (source: Practical Law drafting guide): Some drafters include a specific carve-"
            "out excluding a party's own financial hardship or inability to pay from qualifying as "
            "force majeure, to prevent opportunistic invocation.\n"
            "Chunk 18 (source: American Bar Association guide): Post-2020, many standard contract "
            "templates were revised to explicitly list pandemics, epidemics, and government-ordered "
            "shutdowns as enumerated triggering events, reflecting lessons from COVID-19 disputes.\n"
            "Chunk 19 (source: Cornell LQ): A party that continued partial performance after the "
            "triggering event may be found to have waived the force majeure defense for the portion "
            "still performed.\n"
            "Chunk 20 (source: Practical Law drafting guide): Clauses often distinguish between "
            "'temporary' and 'permanent' triggering events, with different notice and termination "
            "consequences for each.\n"
            "\n"
            "Loop 3 Queries: ['force majeure COVID-19 case law outcomes commercial leases', "
            "'force majeure clause common drafting mistakes enforceability']\n"
            "Chunk 21 (source: Cornell LQ): In COVID-19-era commercial lease disputes, courts largely "
            "rejected force majeure defenses where the clause did not explicitly reference pandemics "
            "or government shutdowns, applying the ejusdem generis principle from Chunk 10 to exclude "
            "the pandemic from generic catch-all language.\n"
            "Chunk 22 (source: American Bar Association guide): Landlords generally prevailed in "
            "COVID-era disputes over ordinary rent payment obligations, since the inability to pay "
            "rent was framed as financial hardship rather than a true impossibility of performance.\n"
            "Chunk 23 (source: Practical Law drafting guide): A frequently cited drafting mistake is "
            "failing to specify whether the force majeure clause covers a party's suppliers or "
            "upstream partners, versus only the contracting party's own direct performance.\n"
            "Chunk 24 (source: Cornell LQ): Clauses silent on notice deadlines default to a 'reasonable "
            "time' standard under general contract law, which courts have found unpredictably, "
            "ranging from a few days to several weeks depending on jurisdiction.\n"
            "Chunk 25 (source: American Bar Association guide): A recurring enforceability problem is "
            "vague causation language (e.g. 'affected by') instead of clear proximate-cause language, "
            "which invites litigation over how directly the event must have caused non-performance.\n"
            "Chunk 26 (source: Practical Law drafting guide): Some jurisdictions require the invoking "
            "party to demonstrate no reasonable alternative means of performance existed, not just that "
            "the primary method became impossible.\n"
            "Chunk 27 (source: Cornell LQ): A minority of courts have found that pure economic "
            "hardship can qualify for force majeure if the clause explicitly lists 'economic downturn' "
            "or similar language, contradicting the general rule from Chunk 7 in those specific "
            "jurisdictions.\n"
            "Chunk 28 (source: American Bar Association guide): Termination rights following an "
            "extended force majeure event are often contested when the clause doesn't specify whether "
            "termination is automatic or requires an affirmative election by the non-invoking party.\n"
            "Chunk 29 (source: Practical Law drafting guide): Clauses that fail to address partial "
            "force majeure (where only part of the obligation is affected) create ambiguity over "
            "whether the whole contract is suspended or only the affected portion.\n"
            "Chunk 30 (source: Cornell LQ): No jurisdiction-independent, universally accepted list of "
            "qualifying events exists — enforceability always turns on the specific clause language "
            "and the governing jurisdiction's interpretive approach."
        ),
        "output_content": (
            'GENERATE_GROUNDING:\n'
            'ARGS: {"title": "Force Majeure Clauses", '
            '"content": '
            '"Force majeure clauses excuse a party from performing its contractual obligations '
            'when something unexpected happens that is beyond that party\'s control, such as a '
            'natural disaster or another extraordinary event. Courts generally look at whether '
            'the event could have been foreseen and whether it actually prevented performance. '
            'Contracts should be drafted carefully with clear language describing what counts, '
            'and a party invoking force majeure should follow the proper procedures under the '
            'contract, including giving notice in a timely manner. It is also worth considering '
            'how the clause interacts with other legal doctrines, and how courts in different '
            'jurisdictions might interpret similar language differently. Well-drafted clauses '
            'often list specific examples of qualifying events and address what happens if the '
            'disruption continues for an extended period, such as whether the contract can '
            'eventually be terminated. Overall, force majeure is a useful protection, but its '
            'success in any given dispute depends a great deal on the specific facts and the '
            'exact wording used."}'
        ),
        # Expect: true, generate_grounding, quality ~2 (reads as a vague summary; ignores the concrete
        # 'foreseeability + true impossibility vs mere cost increase' distinction actually retrieved),
        # relatedness ~3 (uses the chunk but doesn't tie to the sharper distinction available)
    },
    {
        "name": "Honest Gap Disclosure — Forced Generation Node, Loop 3",
        "topic": "Rust Ownership Model",
        "goal": "Evaluate candidate's understanding of borrow checker rules for mutable references.",
        "loop_iteration": 3,
        "retrieved_data": (
            "Loop 1 Queries: ['Rust borrow checker mutable immutable reference rules', "
            "'Rust ownership move semantics lifetime basics']\n"
            "Chunk 1 (source: doc.rust-lang.org, The Book): At any given time, you can have either one "
            "mutable reference or any number of immutable references to a value, not both "
            "simultaneously.\n"
            "Chunk 2 (source: doc.rust-lang.org, The Book): References must always be valid; the "
            "compiler enforces this via lifetimes, which describe the scope for which a reference "
            "remains valid.\n"
            "Chunk 3 (source: doc.rust-lang.org, The Book): Ownership rules state each value has a "
            "single owner, and when the owner goes out of scope, the value is dropped.\n"
            "Chunk 4 (source: doc.rust-lang.org, The Book): Assigning a non-Copy value to another "
            "variable or passing it to a function moves ownership; the original variable can no longer "
            "be used afterward.\n"
            "Chunk 5 (source: doc.rust-lang.org, The Book): Types implementing the Copy trait (like "
            "integers) are duplicated rather than moved on assignment, so the original remains usable.\n"
            "Chunk 6 (source: rustc dev guide): The borrow checker's core job is to statically prevent "
            "data races and use-after-free bugs by enforcing the mutable-XOR-immutable invariant at "
            "compile time rather than runtime.\n"
            "Chunk 7 (source: doc.rust-lang.org, The Book): A mutable reference's scope ends at its "
            "last use, not at the end of the enclosing block — this is why two mutable borrows can "
            "coexist in sequence within the same block as long as their usages don't overlap.\n"
            "Chunk 8 (source: rustc dev guide): This 'last use' based scoping is formally called "
            "Non-Lexical Lifetimes (NLL), introduced to relax the older, stricter lexical-scope-based "
            "borrow checking.\n"
            "Chunk 9 (source: doc.rust-lang.org, The Book): Dangling references are prevented at "
            "compile time — the compiler guarantees a reference's data will not go out of scope before "
            "the reference itself does.\n"
            "Chunk 10 (source: rustc dev guide): The borrow checker operates on the Mid-level IR (MIR), "
            "a simplified control-flow representation, rather than directly on the surface syntax.\n"
            "\n"
            "Loop 2 Queries: ['Rust lifetime annotations function signatures explicit', "
            "'Rust struct field borrow splitting partial borrows']\n"
            "Chunk 11 (source: doc.rust-lang.org, The Book): Explicit lifetime annotations (e.g. "
            "'a) are required when the compiler cannot infer how the lifetimes of multiple reference "
            "parameters relate to the return value's lifetime.\n"
            "Chunk 12 (source: doc.rust-lang.org, The Book): The lifetime elision rules allow omitting "
            "explicit annotations in common patterns, such as a function taking one reference "
            "parameter and returning a reference.\n"
            "Chunk 13 (source: doc.rust-lang.org, The Book): A struct that holds a reference must "
            "declare a lifetime parameter, tying the struct instance's validity to the validity of the "
            "reference it holds.\n"
            "Chunk 14 (source: rustc dev guide): The borrow checker supports splitting borrows across "
            "distinct fields of a struct — borrowing field A mutably and field B immutably "
            "simultaneously is allowed, since the compiler tracks field-level, not just whole-value, "
            "borrows.\n"
            "Chunk 15 (source: rustc dev guide): This field-splitting does not extend across method "
            "calls that take &mut self as a whole, since the compiler cannot see inside the method to "
            "verify it only touches specific fields.\n"
            "Chunk 16 (source: doc.rust-lang.org, The Book): The 'static lifetime denotes a reference "
            "that can live for the entire duration of the program, such as string literals baked into "
            "the binary.\n"
            "Chunk 17 (source: doc.rust-lang.org, The Book): Overuse of 'static as a workaround for "
            "lifetime errors is discouraged, since it often masks a design problem rather than "
            "correctly modeling the data's actual lifetime.\n"
            "Chunk 18 (source: rustc dev guide): Lifetime subtyping allows a longer-lived reference to "
            "be used where a shorter-lived one is expected (covariance), which underlies why lifetime "
            "elision works in many common cases.\n"
            "Chunk 19 (source: doc.rust-lang.org, The Book): RefCell<T> provides interior mutability, "
            "enforcing the same mutable-XOR-immutable rule as the compiler-checked borrow rules, but at "
            "runtime instead of compile time, panicking on violation.\n"
            "Chunk 20 (source: rustc dev guide): Cell<T> and RefCell<T> exist specifically because the "
            "static borrow checker is sometimes too conservative to accept a pattern that is actually "
            "safe, requiring a runtime-checked escape hatch.\n"
            "\n"
            "Loop 3 Queries: ['Rust borrow checker Polonius next generation improvements', "
            "'Rust async borrow checker self-referential struct limitations']\n"
            "Chunk 21 (source: rustc dev guide): Polonius is an in-progress reformulation of the borrow "
            "checker intended to accept a strictly larger set of valid programs than the current NLL "
            "implementation, though as of this source it remains experimental and not the default.\n"
            "Chunk 22 (source: rustc dev guide): A known NLL limitation is certain conditional-return "
            "patterns where a reference is borrowed in one branch and not another; Polonius is designed "
            "to fix a specific documented subset of these false-positive rejections.\n"
            "Chunk 23 (source: async book, doc.rust-lang.org): An async fn's compiler-generated state "
            "machine can require the future to hold both a value and a reference into that same value "
            "simultaneously across an .await point, which is difficult for the ordinary borrow checker "
            "model to express.\n"
            "Chunk 24 (source: async book, doc.rust-lang.org): This self-referential structure is why "
            "async functions generate Pin<Box<...>> based futures in some cases, since moving a "
            "self-referential struct in memory would invalidate its internal references.\n"
            "Chunk 25 (source: async book, doc.rust-lang.org): The Pin API prevents a value from being "
            "moved in memory once pinned, which is the mechanism that makes self-referential async "
            "state machines sound despite normally violating ownership/move assumptions.\n"
            "Chunk 26 (source: rustc dev guide): This source does not provide a specific worked example "
            "showing the exact compiler error message or code pattern that triggers self-referential "
            "borrow issues in async code — it describes the mechanism at a conceptual level only.\n"
            "Chunk 27 (source: doc.rust-lang.org, The Book): Interaction between explicit lifetime "
            "parameters and async fn syntax has additional elision rule nuances not covered in the "
            "basic lifetime elision chapter referenced in Chunk 12.\n"
            "Chunk 28 (source: rustc dev guide): No specific eGFR-style numeric threshold or fixed rule "
            "exists for 'how many' partial borrows the compiler can track on a single struct — the "
            "limit is described only as 'implementation-defined and subject to change across compiler "
            "versions,' not a fixed number.\n"
            "Chunk 29 (source: async book, doc.rust-lang.org): No example in this source set covers how "
            "partial field borrows (Chunk 14) interact with async state machines specifically — the two "
            "topics are each covered independently but never cross-referenced.\n"
            "Chunk 30 (source: rustc dev guide): Polonius's expected release timeline and exact rule "
            "set were described as 'still evolving' at the time of this source, without a specific "
            "version number given for stabilization."
        ),
        "output_content": (
            'GENERATE_GROUNDING:\n'
            'ARGS: {"title": "Rust\'s Borrow Checker: Ownership and Mutable/Immutable Reference Rules", '
            '"content": '
            '"Each value in Rust has a single owner, and when that owner goes out of scope the '
            'value is dropped. Assigning a non-Copy value to another variable, or passing it to '
            'a function, moves ownership -- the original variable can no longer be used '
            'afterward. Types implementing the Copy trait, such as integers, are duplicated on '
            'assignment instead, so the original stays usable.\\n\\n'
            'The core borrowing rule is that at any given time you may have either one mutable '
            'reference or any number of immutable references to a value, never both at once. '
            'This mutable-XOR-immutable invariant is what lets the borrow checker statically '
            'rule out data races and use-after-free bugs at compile time rather than catching '
            'them at runtime. References must always be valid, which the compiler enforces via '
            'lifetimes -- the scope for which a given reference remains valid -- so a dangling '
            'reference is prevented before the program ever runs.\\n\\n'
            'A mutable reference\'s scope actually ends at its last use rather than at the end of '
            'its enclosing block. This is called Non-Lexical Lifetimes (NLL), and it is why two '
            'sequential mutable borrows can coexist within the same block as long as their '
            'usages don\'t overlap -- a relaxation of the older, stricter lexical-scope-based '
            'checking. Explicit lifetime annotations (like \'a) are only required when the '
            'compiler can\'t infer how the lifetimes of multiple reference parameters relate to '
            'a return value; common single-reference patterns are covered by lifetime elision '
            'instead. A struct that holds a reference must declare a lifetime parameter tying '
            'the struct\'s validity to the reference it holds. The \'static lifetime marks a '
            'reference valid for the entire program, such as a string literal baked into the '
            'binary -- reaching for \'static as a workaround for a lifetime error is generally '
            'discouraged, since it tends to mask a design problem rather than correctly model '
            'the data\'s actual lifetime.\\n\\n'
            'The borrow checker also tracks borrows at the level of individual struct fields, so '
            'borrowing one field mutably and a different field immutably at the same time is '
            'allowed. That field-level splitting doesn\'t carry through a method call that takes '
            '&mut self as a whole, since the compiler can\'t see inside the method to confirm it '
            'only touches specific fields. RefCell<T> offers an escape hatch: it enforces the '
            'same mutable-XOR-immutable rule as the compiler, but at runtime, panicking on '
            'violation instead of failing to compile -- useful because the static checker is '
            'sometimes too conservative to accept a pattern that is actually safe.\\n\\n'
            'Two areas of active evolution are worth knowing. Polonius is an in-progress '
            'reformulation of the borrow checker aimed at accepting a strictly larger set of '
            'valid programs than the current NLL implementation, including certain conditional-'
            'return patterns NLL currently rejects as false positives; it remains experimental '
            'and is not yet the default. Separately, an async fn\'s compiler-generated state '
            'machine can end up needing to hold both a value and a reference into that same '
            'value across an .await point -- a self-referential shape the ordinary borrow-'
            'checker model struggles to express. This is why some async futures are built as '
            'Pin<Box<...>>: pinning prevents the value from being moved in memory once created, '
            'which is what makes the self-referential structure sound despite normally violating '
            'ownership and move assumptions."}'

        ),
        # Expect: true, generate_grounding, quality ~4-5 — the disclosed gap should NOT be penalized;
        # it should be read as correct behavior per the rubric note.
    },
    {
        "name": "Off-topic Tool Call — wanders from Goal within correct Topic",
        "topic": "AWS Cost Optimization",
        "goal": "Evaluate candidate's ability to reduce EC2 spend using Reserved Instances and Savings Plans.",
        "loop_iteration": 1,
        "retrieved_data": "None",
        "output_content": (
            'TOOL CALL: web_search\n'
            'ARGS: {"queries": ['
            '"AWS Lambda cold start optimization techniques", '
            '"AWS S3 storage class lifecycle rules"]}'
        ),
        # Expect: true, tool_call, quality ~3-4 (individually fine, valid queries), relatedness ~1-2
        # (both are AWS cost-adjacent but neither touches Reserved Instances/Savings Plans, the
        # actual goal)
    },
    {
        "name": "Invalid Output — plain prose instead of tool call or theory",
        "topic": "Docker Networking",
        "goal": "Evaluate candidate's understanding of Docker bridge networks and container DNS resolution.",
        "loop_iteration": 1,
        "retrieved_data": "None",
        "output_content": (
            "I think I have enough general knowledge about Docker networking to answer this "
            "without searching, so here is my answer to the interview goal directly: Docker "
            "uses bridge networks by default..."
        ),
        # Expect: false, tool_call — does not call the tool and does not produce a structured
        # FinalGroundingTheory; quality_score = 0, relatedness_score = 0. cause its not based on the retrieved data at all.
    },
    {
        "name": "Mixed-Quality Dual Query — one strong, one weak",
        "topic": "Financial Modeling — DCF Valuation",
        "goal": "Evaluate candidate's ability to build a discounted cash flow model with terminal value assumptions.",
        "loop_iteration": 1,
        "retrieved_data": "None",
        "output_content": (
            'TOOL CALL: web_search\n'
            'ARGS: {"queries": ['
            '"terminal value Gordon growth vs exit multiple method DCF", '
            '"finance"]}'
        ),
        # Expect: true, tool_call, quality ~2 (dragged down by the second query being a bare, near-empty
        # keyword despite the first being excellent) — justification should name both queries.
    },
    {
        "name": "Max Chunk Budget — Forced Generation with 30 Retrieved Chunks, Jazz Theory Domain",
        "topic": "Jazz Piano Harmony",
        "goal": "Evaluate candidate's ability to construct rootless drop-2 voicings and apply tritone substitution over a ii-V-I progression in a jazz standard.",
        "loop_iteration": 3,
        "retrieved_data": (
            "Loop 1 Queries: ['rootless drop-2 voicing ii-V-I left hand jazz piano', "
            "'tritone substitution dominant seventh chord theory']\n"
            "Chunk 1 (source: Levine, 'The Jazz Piano Book'): A rootless voicing omits the root, "
            "relying on the bass player to supply it, and typically stacks the 3rd, 5th, 7th, and "
            "9th of the chord.\n"
            "Chunk 2 (source: Levine, 'The Jazz Piano Book'): Drop-2 voicings take the second-from-"
            "top note of a close-position chord and drop it an octave to create a more open, "
            "guitar-like spread.\n"
            "Chunk 3 (source: Berklee Jazz Harmony PDF): In a ii-V-I in a major key, the 'A' voicing "
            "(3-5-7-9) on the ii chord resolves smoothly into the 'B' voicing (7-9-3-5) on the V chord.\n"
            "Chunk 4 (source: Berklee Jazz Harmony PDF): Voicings should alternate between A and B "
            "form each time the root moves by a fourth, minimizing hand movement.\n"
            "Chunk 5 (source: jazzadvice.com): Tritone substitution replaces a dominant 7th chord "
            "with another dominant 7th chord a tritone away, since the two share the same 3rd and 7th.\n"
            "Chunk 6 (source: jazzadvice.com): This works because the tritone interval between the "
            "3rd and 7th is preserved under inversion, so the guide tones remain functionally identical.\n"
            "Chunk 7 (source: Coker, 'Elements of the Jazz Language'): Substituting bII7 for V7 "
            "creates a descending chromatic bass line into the tonic, a common voice-leading device.\n"
            "Chunk 8 (source: Coker, 'Elements of the Jazz Language'): The technique is most idiomatic "
            "at cadence points, particularly the V-I resolution at the end of a phrase.\n"
            "Chunk 9 (source: r/jazzpiano forum): Some players use tritone sub on the ii chord too, "
            "not just the V, for more color, though this is less textbook-standard.\n"
            "Chunk 10 (source: r/jazzpiano forum): A common beginner mistake is voicing tritone subs "
            "in root position instead of keeping the guide tones (3rd/7th) in the same voice as before.\n"
            "\n"
            "Loop 2 Queries: ['altered scale tritone substitution dominant chord', "
            "'ii-V-I voice leading guide tones jazz standards']\n"
            "Chunk 11 (source: Berklee Jazz Harmony PDF): When using tritone substitution, the "
            "original V7 chord is often reharmonized to imply the altered scale (b9, #9, #11, b13) "
            "since the substitute dominant's natural tensions align with the original chord's altered tones.\n"
            "Chunk 12 (source: Berklee Jazz Harmony PDF): This is why tritone subs are frequently "
            "paired with altered-scale improvisation over the original V7 in the melodic line.\n"
            "Chunk 13 (source: Levine, 'The Jazz Piano Book'): Guide tones (3rd and 7th) are the "
            "two notes that define chord quality and should move by step or stay common between "
            "successive chords in a ii-V-I.\n"
            "Chunk 14 (source: Levine, 'The Jazz Piano Book'): In C major, ii-V-I guide tones move "
            "F-B (Dm7) to E-Bb (G7) to E-B (Cmaj7), a mix of common tones and half-step motion.\n"
            "Chunk 15 (source: jazzadvice.com): Not all theorists agree the altered scale is "
            "mandatory over tritone subs — some traditional players simply use Mixolydian on the "
            "substitute dominant with no alterations, especially in earlier swing-era repertoire.\n"
            "Chunk 16 (source: jazzadvice.com): The choice depends heavily on style era: bebop and "
            "post-bop favor altered tensions, while swing-era tunes often keep it diatonic.\n"
            "Chunk 17 (source: Coker, 'Elements of the Jazz Language'): Drop-2 voicings for a tritone "
            "substitute chord should still preserve the original guide tones' voice-leading role, "
            "even though the root and quality symbol have changed.\n"
            "Chunk 18 (source: Coker, 'Elements of the Jazz Language'): A common practice exercise "
            "is to play a ii-V-I through all 12 keys using only drop-2 voicings with smooth guide-"
            "tone motion.\n"
            "Chunk 19 (source: r/jazzpiano forum): Several users note that in a minor ii-V-i, the V7 "
            "is typically altered by default (7alt), which changes how a tritone sub is voiced "
            "compared to a major key context.\n"
            "Chunk 20 (source: r/jazzpiano forum): No consensus reached in the thread on whether "
            "tritone sub voicings should include the 9th in a rootless drop-2 shape or omit it for "
            "clarity — described as 'player preference.'\n"
            "\n"
            "Loop 3 Queries: ['minor ii-V-i tritone substitution voicing', "
            "'jazz standard reharmonization examples Autumn Leaves']\n"
            "Chunk 21 (source: Berklee Jazz Harmony PDF): In a minor ii-V-i, the V7alt chord's "
            "tritone substitute is built a tritone from the altered dominant root, and typically "
            "voiced as a dominant 7#11 rather than a plain dominant 7th.\n"
            "Chunk 22 (source: Berklee Jazz Harmony PDF): This preserves the raised 11th (which "
            "was the altered 9th of the original V7alt) as a chord tone rather than a tension.\n"
            "Chunk 23 (source: 'Autumn Leaves' lead sheet analysis, jazzstandards.com): The bridge "
            "of 'Autumn Leaves' contains a textbook minor ii-V-i (F#m7b5 - B7alt - Em7) commonly "
            "used as a teaching example for tritone substitution (F7 for B7alt).\n"
            "Chunk 24 (source: jazzstandards.com): Recorded versions vary — some pianists play the "
            "straight B7alt, others substitute F7, and some alternate between choruses for variety.\n"
            "Chunk 25 (source: Levine, 'The Jazz Piano Book'): A tritone sub for a minor ii-V-i "
            "dominant still resolves down a half step into the tonic, same as the original V7alt "
            "would, preserving the core cadential motion.\n"
            "Chunk 26 (source: Levine, 'The Jazz Piano Book'): Practicing tritone subs specifically "
            "on minor ii-V-i progressions is recommended before applying them to major-key tunes, "
            "since the altered tensions are already 'built in' to the minor V7alt.\n"
            "Chunk 27 (source: r/jazzpiano forum): One user claims tritone subs 'always' work on "
            "any dominant chord regardless of context — this is contradicted by Coker (Chunk 8), "
            "who ties idiomatic use specifically to cadence points, not universal applicability.\n"
            "Chunk 28 (source: jazzadvice.com): For a ii-V-i in a minor key, a common voicing "
            "exercise is: Dm7b5 (A form) -> B7alt or F7#11 (B form) -> Cm(maj7) or Cm7 (A form), "
            "alternating drop-2 shapes.\n"
            "Chunk 29 (source: Coker, 'Elements of the Jazz Language'): No specific guidance found "
            "in this source on left-hand fingering technique for rapid A/B form alternation — noted "
            "as outside this text's scope.\n"
            "Chunk 30 (source: jazzstandards.com): 'Autumn Leaves' is frequently used in jazz "
            "pedagogy specifically because its bridge isolates the minor ii-V-i in a way that's "
            "easy to practice tritone substitution on in isolation."
        ),
        "output_content": (
            'GENERATE_GROUNDING:\n'
            'ARGS: {"title": "Rootless Drop-2 Voicings and Tritone Substitution over ii-V-I Progressions", '
            '"content": '
            '"A rootless voicing omits the root entirely and relies on the bassist to supply it, '
            'typically stacking the 3rd, 5th, 7th, and 9th of the chord. A drop-2 voicing takes '
            'that close-position stack and drops the second-from-top note down an octave, '
            'producing a more open, guitar-like spread. On a major-key ii-V-I, the \'A\' form '
            '(3-5-7-9) on the ii chord resolves smoothly into the \'B\' form (7-9-3-5) on the V '
            'chord, and voicings should alternate between A and B form each time the root moves '
            'by a fourth, which minimizes hand movement. Guide tones -- the 3rd and 7th, which '
            'define a chord\'s quality -- should move by step or stay as common tones between '
            'successive chords: in C major, the ii-V-I guide tones move F-B (Dm7) to E-Bb (G7) '
            'to E-B (Cmaj7), a mix of common-tone and half-step motion.\\n\\n'
            'Tritone substitution replaces a dominant 7th chord with another dominant 7th a '
            'tritone away, because the two share the same 3rd and 7th -- the tritone interval '
            'between those guide tones is preserved under inversion, so they remain functionally '
            'identical in the substitute chord. This is most idiomatic at cadence points, '
            'particularly a V-I resolution at the end of a phrase; it is not a device that works '
            'equally well on any dominant chord regardless of context. A common beginner mistake '
            'is voicing the substitute chord in root position, which discards this guide-tone '
            'voice-leading relationship rather than preserving it in the same voice as before. '
            'Because the substitute dominant\'s natural tensions align with the original chord\'s '
            'altered tones (b9, #9, #11, b13), tritone subs are frequently paired with altered-'
            'scale improvisation over the original V7 -- though how strictly this is applied '
            'depends on style era: bebop and post-bop playing favors those altered tensions, '
            'while earlier swing-era practice more often stays diatonic, using plain Mixolydian '
            'over the substitute with no alteration.\\n\\n'
            'In a minor ii-V-i, the V7alt chord\'s tritone substitute is typically voiced as a '
            'dominant 7#11 rather than a plain dominant 7th, which preserves the raised 11th -- '
            'the original chord\'s altered 9th -- as a chord tone instead of a tension. The '
            'substitute still resolves down a half step into the tonic, the same cadential '
            'motion the original V7alt would have provided, which is why practicing tritone subs '
            'on minor ii-V-i progressions first is a common recommendation: the altered tensions '
            'are already built into the minor V7alt. A standard voicing exercise runs Dm7b5 (A '
            'form) to B7alt or F7#11 (B form) to Cm(maj7) or Cm7 (A form), alternating drop-2 '
            'shapes throughout.\\n\\n'
            'The bridge of \'Autumn Leaves\' (F#m7b5 - B7alt - Em7) is a standard teaching example '
            'for exactly this technique, substituting F7 for B7alt; recorded versions vary, with '
            'some players keeping the straight B7alt, others substituting throughout, and some '
            'alternating between choruses."}'
        ),
        # Expect: true, generate_grounding, quality ~5, relatedness ~5. This case specifically tests
        # whether the judge (a) actually tracks claims against a near-maximal 30-chunk context
        # rather than skimming, (b) rewards the theory for correctly surfacing and resolving the
        # Chunk 8 vs Chunk 27 contradiction instead of ignoring it, and (c) does not penalize the
        # two explicitly disclosed gaps (style-dependent altered scale usage, fingering technique)
        # since both are honestly flagged rather than glossed over or fabricated.
    },
]

def run_test():
    structured_llm = gemini_flash_lite.with_structured_output(RetrieverEvaluationResult)
    
    print("============================================================")
    print("Running Retriever LLM Judge Test")
    print("============================================================\n")
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"--- Scenario {i}: {scenario['name']} ---")
        
        action_type = "tool_call" if "TOOL CALL:" in scenario["output_content"] else "generate_grounding"
        user_msg_content = RETRIEVER_EVAL_USER_TEMPLATE.format(
            topic=scenario["topic"],
            goal=scenario["goal"],
            loop_iteration=scenario["loop_iteration"],
            retrieved_data=scenario["retrieved_data"],
            output_content=scenario["output_content"],
            action_type=action_type
        )
        
        messages = [
            SystemMessage(content=RETRIEVER_EVAL_SYSTEM_INSTRUCTION),
            HumanMessage(content=user_msg_content)
        ]
        
        try:
            result = structured_llm.invoke(messages)
            print(f"Action Type Score: {result.action_type_score}")
            print(f"Quality Score: {result.quality_score}/5.0")
            print(f"Relatedness Score: {result.relatedness_score}/5.0")
            print(f"Justification: {result.justification}\n")
        except Exception as e:
            print(f"Failed to evaluate: {e}\n")

if __name__ == "__main__":
    run_test()

---
name: search-jobs
description: Search active job postings, verify core details, score fit, and return concise ranked results.
---

# Search Jobs

Use for job discovery or fit evaluation.

Do not use this skill as the final response when the user's current intent is to apply. If an Apply-mode request needs search results from a jobs file, return eligible URLs to the orchestrator so it can continue into the application workflow instead of stopping with a ranked list.

## Inputs

Load:

- `knowledge/job_preferences.md`
- `knowledge/skills.md`
- `knowledge/professional_profile.md` only if match reasoning needs profile context

Current user instructions override stored preferences.

## Sources

Use requested sites first. Otherwise prefer:

1. company career pages
2. Naukri, LinkedIn, Indeed, Wellfound, Instahyre, Cutshort
3. search results for fresh postings

## Process

1. Search with target role, location/work mode, experience, and core skills.
2. Open promising postings and verify they are active.
3. Deduplicate by company/title/location/source URL.
4. Skip hard mismatches.
5. Return the best matches only.

Never call `browser_snapshot` unless the user explicitly asks to inspect the page or you cannot continue without it.

## Score

100-point fit:

- 30 title/seniority
- 25 skill match
- 15 location/work mode
- 10 experience requirement
- 10 freshness/active confidence
- 10 application ease/source quality

## Output

Concise ranked list:

`Rank | Title | Company | Location | Score | Why | URL`

Include skipped jobs only when the reason is useful.

If the caller asked to apply, keep the search output internal and continue to `applier` for eligible jobs.

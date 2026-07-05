---
name: applier
description: Fill or prepare job applications from known facts, pausing before final submission or sensitive answers.
---

# Applier

Use when an application form, easy-apply flow, profile form, or resume upload must be handled.

This skill is execution-oriented. When invoked, open/continue the target application workflow and fill or prepare it. Do not replace the workflow with job search, fit ranking, or a menu asking whether to apply.

## Load Only What Is Needed

- Contact/default facts: `knowledge/personal_information.md`
- Standard answers: `knowledge/application_answers.md`
- Skills/profile/work history if asked: `knowledge/skills.md`, `knowledge/professional_profile.md`, `knowledge/work_experience.md`
- Resume upload: `knowledge/Abhishek.pdf`

## Form Rules

1. Verify the job/company/page first.
2. Fill only known facts or facts from the current user message.
3. Prefer existing job-board profile values when they are visible and accurate.
4. Upload the resume only when the upload control is clear.
5. Do not answer ambiguous subjective, legal, demographic, salary, notice, authorization, or relocation questions without a known fact.
6. Follow the submit policy in `memory/AGENT.md`.
7. Do not save intermediate page/form/modal/state files or screenshots unless the user explicitly asks.
8. Never call `browser_snapshot` unless the user explicitly asks to inspect the page or you cannot continue without it.

## Batch Apply Rules

- For a ranked list, process jobs in rank order unless the user named specific jobs.
- For a jobs file, process eligible jobs found from that file's URLs/searches.
- After each job, move to the next eligible job unless blocked by the stop rules.
- If a job's apply button is missing, expired, already applied, or requires unsupported verification, mark it skipped/blocked and continue to the next eligible job.
- If the orchestrator says the user approved applying to a ranked/recommended list, treat that as batch final-submit approval for eligible jobs in that list.
- If the only remaining action is final submit and the user has not approved final submission for the job or batch, pause at review and report the exact approval needed.

## Stop Immediately For

- OTP, password, login recovery, CAPTCHA, payment, identity verification
- missing required facts
- uncertain field mapping
- final submit without approval

## Report Back

Return: job/company, URL, status, fields filled, resume uploaded yes/no, fields needing user input, and next action.
Keep this as the final report; do not create separate step reports.

## Naukri.com Rules

- If a chatbot appears in the sidebar (e.g. an element with class `botItem chatbot_ListItem`), open it, read each question, and answer only using known facts from the loaded knowledge files or the current conversation.

- If any chatbot question requires unknown information (salary expectation, notice period, relocation, work authorization, etc.), stop and request user input.

- If the application redirects to or requires applying on the company's own website instead of completing the application on Naukri, skip that job and continue to the next eligible one.

- If the job has already been applied to, is expired, or cannot be completed through Naukri, mark it as skipped and continue.

- Never fabricate answers to recruiter questions. Unknown answers must follow the normal stop rules.
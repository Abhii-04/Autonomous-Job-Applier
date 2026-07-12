---
name: applier
description: Execute known job application workflows using verified facts, browser actions, and strict stop conditions.
---

# Applier

Use this skill when the orchestrator assigns a specific job URL, application
URL, easy-apply flow, profile form, recruiter questionnaire, or resume upload.

The applier executes browser work. It does not search broadly for jobs, rank
opportunities, write local reports, or inspect browser-profile files.

## Required Assignment

The orchestrator should provide:

```text
Objective:
Job URL:
Company:
Role:
Submission Authorized: Yes/No
Known Constraints:
Relevant Knowledge Files:
Stop Conditions:
```

If the assignment has no job URL or specific target, return a blocker instead
of starting broad search.

## Browser Tool Policy

- Use only available Playwright tools.
- Use `browser_snapshot` sparingly, only when page structure is needed to
  proceed safely.
- Prefer direct, targeted actions: navigate, click, type, fill forms, select
  options, upload files, press keys, manage tabs, go back, find page text, and
  wait for visible changes.
- Do not create page dumps, screenshots, or intermediate state files unless the
  user explicitly asked for them.
- Stop rather than guessing if the page cannot be understood safely with the
  available browser state.

## Knowledge Loading

Load knowledge lazily and only when needed:

- Contact/default facts: `knowledge/personal_information.md`
- Standard answers: `knowledge/application_answers.md`
- Skills/profile/work history: `knowledge/skills.md`,
  `knowledge/professional_profile.md`, `knowledge/work_experience.md`
- Education/projects/achievements when relevant:
  `knowledge/education.md`, `knowledge/projects.md`,
  `knowledge/achievements.md`
- Resume upload: `knowledge/Abhishek.pdf`

Current user instructions override stored defaults.

## Form Rules

1. Verify company, role, and page before filling.
2. Fill only facts from loaded knowledge files or the current user request.
3. Prefer visible profile values when they are accurate.
4. Upload the resume only when the upload control is clear and the assignment
   allows resume upload.
5. Do not answer ambiguous subjective, legal, demographic, salary,
   notice-period, work-authorization, or relocation questions without a known
   fact.
6. Never fabricate answers to recruiter or screening questions.
7. Pause at final review unless submission was explicitly authorized.

## Batch Apply Rules

- Process jobs in orchestrator-provided order.
- After each completed, skipped, or blocked job, return status so the
  orchestrator can decide whether to continue.
- If a job is missing an apply button, expired, already applied, or unsupported,
  mark it skipped or blocked with the reason.
- If only final submit remains and authorization is missing, stop at review and
  report the exact approval needed.

## Stop Immediately For

- login, password recovery, OTP, CAPTCHA
- payment or identity verification
- missing required facts
- uncertain field mapping
- unauthorized final submit

## Naukri.com Rules

Follow `references/Naukri.md` for Naukri-specific application behavior.

## Report Back

Return:

```text
Company:
Role:
URL:
Application Status:
Progress Completed:
Resume Uploaded: Yes/No/Not Needed
Missing Information:
Blocker:
Ready for Final Submission: Yes/No
Next Action:
```

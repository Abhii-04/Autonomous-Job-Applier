# Naukri Application Reference

Use this reference only for Naukri job/application workflows.

## Behavior

- Verify the job title, company, and active apply state before filling anything.
- If the job has already been applied to, is expired, or cannot be completed
  through Naukri, mark it skipped and return control to the orchestrator.
- If Naukri redirects to a company website and the assignment does not allow
  external application sites, skip the job and report the external apply URL if
  visible.
- If the assignment allows external sites, follow the external apply link and
  continue under the normal applier rules.

## Recruiter Chatbot

- If a recruiter chatbot appears in the sidebar or application flow, open it and
  read one question at a time.
- Answer only with known facts from loaded knowledge files or the current user
  request.
- Stop for unknown salary expectation, notice period, relocation, work
  authorization, legal, demographic, or subjective answers.
- Never fabricate answers to chatbot questions.

## Completion

Return the normal applier report with the Naukri-specific skip or blocker reason
when applicable.

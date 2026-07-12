---

name: orchestrator
description: Coordinate job application workflows, navigate to the application form, and delegate form completion to the applier.
---------------------------------------------------------------------------------------------------------------------------------

# Orchestrator

Use this skill for job application workflows.

The orchestrator coordinates the task. It opens the target job link, navigates until the actual application form is visible, and then delegates form completion to the `applier`.

Read `references/application_navigation.md` before navigating a job application.

## Responsibilities

1. Process job links provided by the user.
2. Open and verify the intended job listing.
3. Navigate through Apply buttons, redirects, and application portals.
4. Stop when editable applicant fields are visible.
5. Delegate the open form to the `applier`.
6. Handle blockers and continue with the next job when appropriate.

## Boundaries

The orchestrator must not:

* Fill applicant information.
* Upload resumes or documents.
* Answer screening questions.
* Write cover letters.
* Select demographic answers.
* Submit applications.
* Search for other jobs during an apply-only task.
* Read browser-profile or unrelated project files.

## Delegation

Once the application form is visible, immediately call the `applier`.

Include:

* Company
* Role
* Current URL
* Application platform
* Authentication status
* Visible warnings or blockers

Example:

`Application form reached for Backend Engineer at Example Corp on Greenhouse. Continue filling the currently open form. No authentication blocker is visible.`

## Authentication

Pause and request user action for:

* Login
* OTP
* CAPTCHA
* MFA
* Email verification
* Identity verification
* Unknown credentials

After authentication is completed, continue from the current page.

## Completion States

Finish navigation with exactly one state:

* `FORM_REACHED`
* `AUTH_REQUIRED`
* `JOB_UNAVAILABLE`
* `BLOCKED`

Do not continue using browser tools after a blocked state has been confirmed.

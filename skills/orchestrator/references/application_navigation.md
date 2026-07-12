# Application Navigation Rules

## Objective

Navigate from the job listing to the actual application form.

A page with only job details and an Apply button is not the application form.

The form is reached when editable applicant fields appear, such as:

* Name
* Email
* Phone
* Resume upload
* Education
* Work experience
* Location
* Cover letter
* Screening questions

## Workflow

1. Open the provided job URL.
2. Verify the company and role when possible.
3. Locate the primary application action.
4. Click Apply, Apply Now, Easy Apply, Continue, or an equivalent button.
5. Follow legitimate redirects and newly opened tabs.
6. Verify that the redirected page still belongs to the intended application.
7. Stop when applicant fields are visible.
8. Delegate immediately to the applier.

## Progress Check

After every browser action, verify meaningful progress.

Progress means at least one of these changed:

* URL
* Page heading
* Application modal
* Visible form step
* Applicant fields
* Authentication state
* Open browser tab

A successful browser tool response does not prove that navigation succeeded.

## Retry Limit

For one navigation objective:

1. Attempt the action once.
2. Check for progress.
3. If unchanged, inspect for overlays, cookie banners, disabled controls, validation errors, new tabs, or stale references.
4. Retry once using a different valid interaction.
5. If still unchanged, stop with `BLOCKED`.

Never perform more than three browser actions without meaningful progress.

## Loop Prevention

Do not repeat:

`snapshot -> click -> snapshot -> click`

If two snapshots show the same relevant page state:

* Do not click the same intended control again.
* Diagnose the blocker.
* Use at most one alternative interaction.
* Stop if the page still does not progress.

Do not take repeated snapshots of an unchanged page.

## Redirects

Legitimate destinations may include:

* Greenhouse
* Lever
* Ashby
* Workable
* LinkedIn
* Wellfound
* Company career portals
* Other applicant tracking systems

Follow the redirect only when it reasonably matches the intended company or role.

## Blocked Output

When blocked, report:

* Status
* Company
* Role
* Current URL
* Intended action
* Actions attempted
* Observed obstacle
* Required user action

Do not continue clicking after producing a blocked result.

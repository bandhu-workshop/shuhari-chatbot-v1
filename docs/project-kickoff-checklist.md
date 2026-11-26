# Project kickoff requirements checklist

> **Last updated:** 2026-11-26 18:52 IST

Use these prompts when starting a software project or a substantial feature. Not every
question applies. Mark each answer as **decided**, **open**, or **not applicable** so that
unknowns stay visible instead of becoming silent assumptions.

## 1. Purpose and success

- What problem are we solving, and why now?
- Who has this problem?
- What do they do today instead?
- What outcome should the project improve?
- How will we measure success? What target would count as good enough?
- What is explicitly out of scope?
- What would make the project a failure, even if the software runs?
- Are there products or workflows we should learn from?

## 2. Users and access

- Who will use the system: customers, staff, admins, or other systems?
- What does each kind of user need to do?
- Do users need accounts? How will identity be verified?
- Are there different permissions or roles?
- Does the system need to support multiple organizations or isolate user data?
- What devices, browsers, languages, or accessibility needs matter?

## 3. Functional requirements: what it does

For each important user task, ask:

- What starts the task?
- What information does the user provide?
- What does the system do in response?
- What should the user see when it succeeds?
- What happens if input is missing, invalid, duplicated, or unexpected?
- Can the user cancel, edit, retry, or undo?
- What should happen on timeouts or service errors?
- What needs to be saved, and what should be deleted?
- Are notifications, reports, exports, or admin controls needed?

Write requirements as observable behavior. For example: “When a user sends a message, the
chat displays the reply as it arrives and shows a clear error if generation fails.”

## 4. User flows and interface

- What are the main tasks, from opening the app to completion?
- What screens or states does each task involve?
- What should first-time users see?
- What should loading, empty, success, and error states look like?
- What information must be visible at a glance?
- Are keyboard use, screen readers, contrast, and reduced motion requirements?
- Which parts need mobile layouts?

## 5. Data and integrations

- What data does the system collect, create, read, update, or delete?
- Which fields are required? How long is data retained?
- Who owns the data, and can users export or delete it?
- What data is sensitive or confidential?
- What external services or APIs are involved?
- What happens when an integration is unavailable or changes?
- Are data import, migration, backup, and restore needed?

## 6. Technical requirements: how it must work

- Which platforms and environments are required: web, mobile, desktop, cloud, or local?
- Is there an existing stack or architecture to follow?
- Which languages, frameworks, databases, and services are approved?
- What systems must it integrate with?
- Are there limits on hosting, budget, licenses, or vendors?
- What needs to be configurable, and where will configuration live?
- How will development, testing, staging, and production differ?
- What deployment and rollback process is expected?

## 7. Quality requirements

Make these measurable where possible:

- How many users or requests should it support?
- What response time is acceptable?
- What uptime or recovery target is needed?
- What happens if a service or database goes down?
- What level of accuracy or reliability is required?
- What logs, metrics, traces, and alerts will help diagnose issues?
- What browsers, devices, or environments must be supported?
- What test coverage or automated checks are required?

## 8. Security, privacy, and compliance

- What threats or misuse should we consider?
- How will login, permissions, and secrets be handled?
- Can one user ever access another user's data?
- What sensitive data must be encrypted or excluded from logs?
- Are there legal, regulatory, or organizational requirements?
- How will security issues and data incidents be handled?

## 9. AI-specific questions, when relevant

- What tasks may the model perform, and what must it never do?
- What sources may it use, and how should it cite them?
- What should it do when it does not know?
- Can it use tools or change external state? Which actions need user approval?
- How will you evaluate answer quality, safety, and consistency?
- How will you handle prompt injection and untrusted tool output?
- What are the limits for latency and model/API cost?

For a chatbot, clarify early whether it only answers questions or also uses tools, remembers
users, or changes data. Those choices affect the API, data model, security, and evaluations.

## 10. Delivery and ownership

- What is the smallest useful first release?
- What are the milestones and dependencies?
- Who makes product and technical decisions?
- Who reviews and accepts the work?
- What documentation and training are needed?
- Who will operate and maintain it after launch?
- What must be true before release?

## Before development starts

At minimum, agree on:

1. The target users and problem.
2. The first release's scope and non-goals.
3. The main user flows and expected behavior.
4. The data and integration needs.
5. The important security and quality requirements.
6. Acceptance criteria: observable conditions for calling the work done.

Keep unresolved details visible rather than silently guessing. Details such as exact UI polish
or later-scale capacity can be deferred if they do not affect the first milestone.

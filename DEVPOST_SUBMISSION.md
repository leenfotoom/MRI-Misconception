# Devpost submission — copy-ready

## Project name

Misconception MRI

## Tagline

Diagnose the belief. Repair the model. Verify the learning.

## Inspiration

A student can choose the correct answer while still using the wrong mental model. Most educational tools mark the answer correct and move on, allowing the same misconception to reappear in a new context. We wanted educational AI to go beyond explanation: identify the reasoning pattern, intervene on that exact pattern, and verify whether conceptual change actually happened.

## What it does

Misconception MRI is a closed-loop STEM learning system:

1. **Assess:** the learner answers and explains why.
2. **Diagnose:** GPT-OSS 120B extracts constrained reasoning signals while a Bayesian model ranks competing misconceptions.
3. **Challenge:** active learning selects the counterexample with the highest expected information gain.
4. **Verify evidence:** a deterministic STEM engine—not the LLM—computes the observable result.
5. **Intervene:** MRI explains the detected misunderstanding, presents the correct mental model, and delivers a three-step micro-lesson.
6. **Transfer practice:** the learner answers a new question targeting the same misconception and explains the reasoning.
7. **Re-evaluate:** MRI marks the misconception Resolved only when the answer and reasoning both match the expected model; otherwise it remains Persistent.
8. **Plan:** persistent patterns are prioritized in a study plan based on the learner's academic major, with learning sequence, activities, reassessment points, and progress tracking.

The bilingual prototype covers Science, Technology, Engineering, and Mathematics with 16 diagnostic environments, 32 misconception models, 16 adaptive deterministic experiments, and targeted transfer practice for every environment.

## Why this is different

Misconception MRI does not equate a correct answer with understanding. In our demo, a learner selects the correct answer to an AI-evaluation question but justifies it with the same accuracy-only misconception. The system detects the repeated reasoning pattern, labels it Persistent, and makes AI evaluation the first priority in a Computer Science study plan.

That is the difference between answer checking and learning verification.

## How we built it

The frontend uses Next.js 16, React 19, and TypeScript. FastAPI exposes the diagnostic, intervention, verification, and study-plan APIs. PostgreSQL, SQLAlchemy, and Alembic persist verified accounts, sessions, scans, interventions, verification status, academic major, and learner progress.

GPT-OSS 120B is used only to interpret natural-language reasoning using a scenario-specific claim allowlist. Those signals become soft evidence for a Bayesian learner model. Expected information gain ranks diagnostic experiments.

Truth is separated from language generation. Four deterministic engine families compute circuit behavior, program traces and AI metrics, structural/design results, and mathematical counterexamples. Post-intervention verification checks three independent conditions: the transfer answer is correct, correct-model reasoning is expressed, and the original misconception pattern is absent. If the external AI provider is unavailable, a transparent bilingual heuristic parser keeps the prototype functional.

Major-aware plans are generated only from persistent, observed misconceptions. Severity combines post-verification confidence and repeated persistence; major-specific domain order determines tie-breaking and learning sequence. Plans do not output generic study hours—they answer what the learner should study next and how mastery will be reassessed.

## Challenges we ran into

The hardest problem was preventing the language model from acting as both interpreter and judge. If one generative model diagnosed the learner, generated a lesson, and declared the truth, the result would be difficult to trust. We separated language interpretation, Bayesian inference, active experiment selection, deterministic evidence, and reasoning-based verification.

A second challenge was recognizing that a correct answer can still contain faulty reasoning. We built verification around explicit correct-model and misconception signals, so a correct choice with persistent reasoning does not falsely count as resolved.

A third challenge was expanding from a physics prototype to reusable STEM architecture. We generalized scenarios, misconception catalogs, evidence engines, transfer practice, and study-plan priorities across four domains while keeping the learner history account-scoped.

## Accomplishments that we are proud of

- A complete Detect → Intervene → Practice → Verify → Plan learning loop.
- Reasoning-based Resolved/Persistent classification rather than answer-only grading.
- Major-aware plans built only from persistent misconceptions.
- A meaningful AI role beyond chat or generic content generation.
- Bayesian active learning and deterministic truth engines independent of the LLM.
- English and Arabic reasoning support.
- 16 environments and 32 misconception models across all four STEM domains.
- Secure accounts, cross-session intervention history, and progress analytics.
- 17 passing backend tests, a full end-to-end API loop test, and a successful typed production frontend build.

## What we learned

Personalization is not merely generating a different explanation. Strong personalization selects the contradiction, lesson, transfer question, and next learning priority that correspond to the learner's actual reasoning pattern.

We also learned that educational AI should verify a change in reasoning before claiming learning success. A correct answer may be a guess; a correct explanation is stronger evidence that the mental model changed.

## What's next

- Calibrate reasoning thresholds and likelihood tables with classroom response data.
- Add multiple transfer-question variants per misconception for spaced reassessment.
- Add a teacher dashboard and cohort-level persistent-misconception maps.
- Let educators author validated interventions and practice variants.
- Measure delayed retention, not only immediate resolution.
- Add accessibility and voice-based explanations.

## Built with

Next.js · React · TypeScript · FastAPI · Python · PostgreSQL · SQLAlchemy · Alembic · Cloudflare Workers AI · GPT-OSS 120B · Bayesian inference · Information gain · Deterministic STEM engines

## Links to add before submission

- **Demo video:** [paste link]
- **Source code:** [paste GitHub link]
- **Live demo:** [paste deployment link, if available]

## Final submission checklist

- Video is under two minutes; the rules state content after 2:00 will not be viewed.
- Repository contains no `.env`, API keys, passwords, `.venv`, `node_modules`, `.next`, or database exports.
- README explains the closed loop and reasoning-based verification.
- Demo account is verified and Technology → AI Audit loads before recording.
- Video shows the correct-answer-but-Persistent moment and the Computer Science study plan.
- Video briefly shows all four STEM domains.
- GitHub, video, and live-demo links work in an incognito window.
- Submission is saved early enough to recover from upload problems.

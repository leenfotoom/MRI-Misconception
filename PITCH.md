# Misconception MRI — competition pitch

## One-line pitch

Misconception MRI is a closed-loop learning system that diagnoses the mental model behind a mistake, repairs it with a targeted intervention, verifies the student's new reasoning, and turns persistent misconceptions into a major-aware study plan.

## Core story

Students can reach the correct final answer while still using the wrong rule. Ordinary tutoring systems mark that answer correct and move on. Misconception MRI asks a harder question: **did the student's reasoning actually change?**

The product runs one complete learning loop:

**Assess → Diagnose → Challenge → Explain → Targeted Learning → Transfer Practice → Reasoning Verification → Resolved / Persistent → Major-Aware Study Plan**

GPT-OSS 120B extracts constrained reasoning signals. A Bayesian model ranks competing misconceptions. Active learning selects a counterexample with high expected information gain. Deterministic STEM engines establish truth. After evidence, MRI explains the precise misunderstanding, teaches the replacement model, and asks a transfer question. The second answer is marked Resolved only when both the choice and reasoning match the new model. Persistent reasoning becomes a prioritized plan based on the learner's academic major.

The bilingual prototype covers Science, Technology, Engineering, and Mathematics with 16 environments, 32 misconception models, 16 deterministic experiments, targeted transfer practice for every environment, persistent accounts, and progress tracking.

## Why it can win

- **Educational impact:** closes the loop from detection to remediation and verifies conceptual change instead of answer memorization.
- **Creative AI:** the LLM is a constrained reasoning sensor inside Bayesian diagnosis, active experiment selection, and post-intervention verification.
- **Technical execution:** full-stack accounts, PostgreSQL persistence, bilingual UX, deterministic truth engines, 17 automated tests, and a reasoning-aware study-plan pipeline.
- **Pitch & demo:** the judge can watch a correct answer remain Persistent because the reasoning is still wrong—then see that exact pattern become priority one in a Computer Science plan.

## Exact two-minute video script

### 0:00–0:10 — Hook

**Screen:** Landing page and closed learning loop.

**Voice:** “A student can give the correct answer and still keep the misconception. Most learning systems never notice. Misconception MRI evaluates the mental model behind the answer.”

### 0:10–0:25 — What is different

**Screen:** Ordinary AI versus Misconception MRI.

**Voice:** “We do not stop at detecting a mistake. MRI diagnoses the hidden belief, challenges it, teaches the missing model, and verifies whether the learner's reasoning actually changed.”

### 0:25–0:48 — Live diagnosis

**Screen:** Technology → AI Audit. Select the wrong high-accuracy choice and paste the prepared diagnosis reasoning.

**Voice:** “This classifier is 99 percent accurate but misses every sick patient. The learner says accuracy alone proves it is good. GPT-OSS extracts constrained reasoning signals, and a Bayesian model identifies the accuracy-only misconception.”

### 0:48–1:05 — Counterexample with deterministic truth

**Screen:** Run Minority-Class Audit and reveal zero minority recall.

**Voice:** “Active learning chooses the most discriminating audit. A deterministic metrics engine reveals high accuracy but zero minority recall. The language model interprets reasoning; it never decides what is true.”

### 1:05–1:31 — Intervention and reasoning verification

**Screen:** Open Targeted Intervention, show the correct model and micro-lesson, then answer the transfer question with B while pasting the intentionally persistent reasoning below.

**Voice:** “MRI now explains the exact misunderstanding, gives a three-step micro-lesson, and asks a transfer question. I choose the correct answer—but I justify it with the same bad rule. MRI does not reward the guess. It detects the repeated reasoning pattern and marks the misconception Persistent.”

### 1:31–1:46 — Major-aware action

**Screen:** Choose Computer Science and generate the plan. Highlight Artificial Intelligence as priority one.

**Voice:** “Because the pattern persisted, MRI combines it with the student's Computer Science major. It prioritizes AI evaluation, gives a learning sequence and practice activities, and defines the exact reasoning-based reassessment point.”

### 1:46–1:55 — STEM breadth

**Screen:** Quickly switch S → T → E → M.

**Voice:** “The same closed loop works across physics, technology, engineering, and mathematics—in English and Arabic.”

### 1:55–2:00 — Close

**Screen:** Logo or verification architecture.

**Voice:** “Misconception MRI: diagnose the belief, repair the model, verify the learning.”

## Demo inputs

### Initial diagnosis reasoning

Select **Yes, 99% is excellent** and paste:

```text
It is an excellent model because 99 percent accuracy is almost perfect. Class balance does not matter if total accuracy is high.
```

During the Minority-Class Audit, select **accuracy sufficient** and run the evidence engine.

### Transfer-practice reasoning for the Persistent demo

Choose **B — No, inspect minority recall**, but paste this intentionally flawed reasoning:

```text
I picked B, but high accuracy proves the model is good.
```

The final choice is correct, but the same mental model remains, so MRI should show **PERSISTENT**.

### Optional Resolved reasoning

For a second take or screenshots, choose B and paste:

```text
Overall accuracy hides minority-class failure, so I must inspect minority recall and the confusion matrix before approving the model.
```

MRI should show **RESOLVED**.

## Recording checklist

- Pre-create and verify the demo account.
- Open Technology → AI Audit before recording.
- Set the academic major to Computer Science during the demo, not beforehand, so the personalization is visible.
- Practice the two paste actions and keep the final export under 1:58.
- Hide `.env`, terminal secrets, notifications, and unrelated tabs.
- Record at 1080p and verify audio before uploading.
- Show one loop deeply; show the remaining STEM domains quickly.

# NetSage AI Presentation: 5–10 Minute Demo Script

## 1. Introduction (1 min)
**Visual:** Show the repository structure or a high-level architecture diagram.
**Speaker Notes:**
> "Hello everyone! Today we are presenting **NetSage AI**, a tool designed to automatically troubleshoot and grade Cisco Packet Tracer network topologies. Grading network labs at scale is incredibly time-consuming for instructors, and students often wait days for feedback. 
> 
> NetSage solves this by combining the reasoning power of Large Language Models (like Anthropic's Claude / Groq's LLaMA 3) with deterministic, rule-based checks. Let me walk you through how it works."

## 2. The AI Diagnosis Engine (2 mins)
**Visual:** Open `prompts/diagnose_prompt.md` and briefly show `runner/run_diagnosis.py`.
**Speaker Notes:**
> "At the core of the system is our AI Diagnosis Engine. We extract the running config and CLI output from the student's Packet Tracer file.
> 
> Instead of just asking the AI to guess the problem, we use a highly structured **system prompt** that guides the LLM through a specific reasoning framework. We inject the exact network symptoms and the router configurations into this prompt.
> 
> The AI then acts as an expert Network Engineer, identifying the OSI layer, the core concept (like VLANs or OSPF), providing the root cause, and generating the exact Cisco IOS commands to fix it. We constrain the output to strict JSON so it integrates perfectly with our pipeline."

## 3. The Rule Checker Validation (1.5 mins)
**Visual:** Open `checker/rule_checker.py` and point out a few regex rules.
**Speaker Notes:**
> "We quickly realized that LLMs can hallucinate IP addresses or miss subtle syntax errors. To solve this, we introduced the **Deterministic Rule Checker**.
> 
> After the AI suggests a root cause, our pipeline runs deterministic regex and logic checks against the configuration. For example, if the AI says 'The OSPF process is missing,' the rule checker physically scans the config for `router ospf \d+`. 
> 
> This dual-engine approach guarantees that the AI's diagnosis is grounded in reality before it's ever presented to a human."

## 4. Responsible AI & Human-in-the-Loop Review (1.5 mins)
**Visual:** Show `review/responsible_ai_log.md` and `review/review_template.csv`.
**Speaker Notes:**
> "Because this is an educational tool, we strictly adhere to Responsible AI principles. We never auto-grade without human oversight.
> 
> Our pipeline automatically generates a `review_template.csv` for every batch of cases. An instructor can quickly scan the AI's findings. If the AI hallucinates—for example, blaming a missing static route when an interface is actually shut down—the instructor marks it as 'Edited' or 'Rejected' and provides a correction.
> 
> This feedback loop generates a **Responsible AI Log**, allowing us to track the AI's accuracy over time and refine our prompts."

## 5. The Telemetry Dashboard (2 mins)
**Visual:** Run the React Dashboard (`npm run dev` in the `dashboard` folder) and showcase the UI.
**Speaker Notes:**
> "Finally, we built a modern React dashboard using Vite, Tailwind, Recharts, and Framer Motion to visualize all of this telemetry data.
> 
> *[Show the top stats]* Here you can see the total cases processed, our AI base agreement rate, and how many cases required human intervention. 
> 
> *[Show the charts]* We have visual breakdowns showing which networking concepts (like NAT, OSPF, or VLANs) students are struggling with the most, and how often the AI gets it right versus when it needs correction.
> 
> *[Expand a table row]* Instructors can search for a specific case, expand it, and view the exact evidence the AI used, side-by-side with the human correction. They can also view the full Responsible AI Review Log directly from the modal at the top.
> 
> By combining AI reasoning, deterministic validation, and human-in-the-loop oversight, NetSage AI drastically reduces grading time while maintaining 100% accuracy and trust."

## 6. Q&A (1-2 mins)
**Speaker Notes:**
> "Thank you for your time. I’m happy to answer any questions about the pipeline, the prompt engineering, or the UI!"

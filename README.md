# Automated Dynamic SLA Arbiter

## Overview
The **Automated Dynamic SLA Arbiter** is an intelligent contract primitive built for GenLayer that automates the verification and escrow settlement of service level agreements (SLAs) and freelance milestones. Instead of relying on centralized trusted third parties or simple binary state variables, this contract leverages GenLayer's multi-validator LLM execution to intelligently audit external project deliverables (such as code repositories, deployed web apps, or document links) against natural-language contract terms.

## Why This Primitive Matters
* **Real-World Utility:** Solves the persistent trust problem in decentralized collaboration and freelancing where conditions are qualitative rather than purely quantitative.
* **Reusable Architecture:** Can be imported or extended by other builders to create decentralized job boards, freelance platforms, and grant management systems.
* **Beyond a One-Off Demo:** Combines persistent state management (`LegacyMap`), strict role-based access control (`msg.sender`), and decentralized consensus evaluation (`exec_prompt`).

## How GenLayer Consensus is Utilized
1. **Dynamic Prompt Execution:** When the provider submits a deliverable URL, GenLayer dispatches the evaluation task across independent validator nodes.
2. **Semantic Equivalence:** Each validator independently evaluates the deliverable against the natural-language SLA terms using advanced LLM reasoning.
3. **Consensus Settlement:** The network reaches consensus on whether the work meets the criteria, deterministically updating the contract state (`Completed` or `Disputed`) and releasing escrow funds safely.

## Testing & Verification
To test this contract locally in the GenLayer simulator:
1. Deploy `SLAArbiter`.
2. Call `create_agreement` with a unique ID, provider address, terms string, and escrow amount.
3. Call `submit_and_evaluate_deliverable` as the provider address with a valid project URL to observe real-time AI consensus arbitration and state transition.

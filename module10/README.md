# Module 10 — GenAIOps exercise archive

This archive preserves the local exercise source and reviewed results, alongside the existing infrastructure portfolio at the repository root. It is a snapshot, not a claim that all cloud artifacts were exported.

| Exercise | Present | Missing or not independently verified |
|---|---|---|
| 1 Infrastructure | Root infrastructure portfolio; module10/infra and azure.yaml | Cloud deployment evidence beyond existing README |
| 2 Prompt and agent versions | src/agents/trail_guide_agent/agent.yaml; prompts v1–v3; interaction and batch scripts | Foundry-only agent/version exports and personal run records |
| 3 Prompt optimization | v4_optimized_concise_instructions.txt; monitoring prompt examples | Exported prompt comparison results |
| 4 Automated evaluation | 89-row baseline and 89-row nano datasets; evaluator and generation scripts; evaluation_results.txt; earlier evaluation_analysis.md | Per-item cloud evaluation output; nano-specific evaluation results |
| 5 Monitoring and tracing | run_monitoring.py, check_traces.py, five test prompts | Exported traces and monitoring comparisons |
| 6 Fine-tuning | SFT/DPO/RFT interactive HTML labs and attached completed simulation transcripts under evidence/exercise06 | Separate executable notebooks and actual fine-tuning datasets/jobs are not present; this exercise uses simulations |

## Evidence and limitations

The latest evaluation summary has 89 scored items, zero errors, averages 4.96 / 4.96 / 4.84 and pass rates 100% / 100% / 95.5% at threshold 4. The earlier analysis records a separate result at threshold 3 and remains unchanged.

The nano comparison evaluator currently references the baseline dataset and writes the shared evaluation_results.txt. Its filename alone does not establish a completed nano evaluation. Review its configuration before running it.

The workflow is archived under module10/.github, so it is not an active GitHub Actions workflow. Its duplicate trigger and indentation were corrected in this archive, and score descriptions aligned to threshold 4. Configure paths and credentials deliberately before activating it.

Exercise 6 transcripts are user-supplied outputs from the interactive simulations; they do not establish real Azure training or deployment. Azure UUIDs and project endpoints in those transcripts are redacted.

## Preservation and exclusions

Original working directories and their commit histories were left intact. Source main HEAD: 0a7eaa9 (Complete automated evaluation analysis); it was one commit ahead of its cached origin/main. The source remote belongs to vicmike199-design, while this archive targets VicScottNYC/10-genaiops-foundry-infrastructure.

SOURCE-MANIFEST.json records source file hashes. The archived workflow is the one intentionally edited source file. No .env, credentials, local Azure state, virtual environments, caches, backup files, compiled infrastructure JSON, raw traces, or unreviewed binary troubleshooting document are included. The external Exercise 4 troubleshooting DOCX remains local pending content review.

Run scripts from the module10 directory with your own local configuration. No cloud scripts were executed during this audit.

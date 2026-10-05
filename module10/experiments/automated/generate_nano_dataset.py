import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv(dotenv_path=".env")

repo_root = Path(__file__).resolve().parents[2]

source_file = repo_root / "data" / "trail_guide_evaluation_dataset.jsonl"
output_file = (
    repo_root
    / "experiments"
    / "automated"
    / "trail_guide_gpt5nano_dataset.jsonl"
)

agent_name = "trail-guide-nano"

client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

openai_client = client.get_openai_client()

# Load the original 89-record dataset.
with source_file.open() as f:
    rows = [json.loads(line) for line in f if line.strip()]

print(f"Loaded {len(rows)} baseline records.")
print(f"Comparison agent: {agent_name}")
print(f"Output file: {output_file}")

# Determine how many records have already been completed.
completed = 0

if output_file.exists():
    with output_file.open() as f:
        completed = sum(1 for line in f if line.strip())

print(f"Already completed: {completed}/{len(rows)}")

if completed >= len(rows):
    print("All comparison responses have already been generated.")
    raise SystemExit(0)

# Generate a fresh gpt-5-nano response for every remaining query.
with output_file.open("a") as out:
    for index, row in enumerate(rows, start=1):

        if index <= completed:
            continue

        query = row["query"]
        ground_truth = row["ground_truth"]

        print(f"\n[{index}/{len(rows)}] {query[:70]}")

        try:
            conversation = openai_client.conversations.create()

            openai_client.conversations.items.create(
                conversation_id=conversation.id,
                items=[
                    {
                        "type": "message",
                        "role": "user",
                        "content": query,
                    }
                ],
            )

            response = openai_client.responses.create(
                conversation=conversation.id,
                extra_body={
                    "agent_reference": {
                        "name": agent_name,
                        "type": "agent_reference",
                    }
                },
                input="",
            )

            try:
                response_text = response.output[0].content[0].text
            except Exception:
                response_text = str(response)

            comparison_record = {
                "query": query,
                "response": response_text,
                "ground_truth": ground_truth,
            }

            out.write(json.dumps(comparison_record) + "\n")
            out.flush()

            print("✓ Response saved")

            # Small pause to reduce pressure on the low-capacity
            # temporary deployment.
            time.sleep(2)

        except Exception as exc:
            print(f"\nERROR on record {index}: {exc}")
            print(
                "Completed records are preserved. "
                "Rerun the script to continue."
            )
            raise

print(f"\nCompleted: {len(rows)}/{len(rows)}")
print(f"Saved: {output_file}")

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from .mapper import EndpointMapper


def main() -> None:
    parser = argparse.ArgumentParser(description="Biomedical endpoint mapper")
    parser.add_argument("--input", default="data/demo_endpoints.csv")
    parser.add_argument("--ontology", default="config/endpoints.json")
    parser.add_argument("--output", default="output/mapped_endpoints.csv")
    parser.add_argument("--threshold", type=float, default=0.72)
    args = parser.parse_args()

    mapper = EndpointMapper.from_json(args.ontology, args.threshold)
    with Path(args.input).open(encoding="utf-8-sig", newline="") as f:
        source_rows = list(csv.DictReader(f))
    output_rows = [
        {**row, **mapper.map(row["source_endpoint"], row.get("domain") or None).to_dict()}
        for row in source_rows
    ]
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)

    counts = Counter(row["match_method"] for row in output_rows)
    summary = {"rows": len(output_rows), "methods": dict(counts), "output": str(output)}
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

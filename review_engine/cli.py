from __future__ import annotations

import argparse
import json
from pathlib import Path

from .app import ReviewEngineApp
from .configuration import load_configuration
from .request_boundary import build_request  # re-exported for compatibility/tests


def run_from_files(*, config_path: str, request_path: str, memory_db: str, sessions_db: str) -> dict:
    configuration = load_configuration(config_path)
    app = ReviewEngineApp(configuration, memory_db=memory_db, sessions_db=sessions_db)
    payload = json.loads(Path(request_path).read_text(encoding="utf-8"))
    return app.review(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="Governed multi-LLM Review Engine MVP")
    parser.add_argument("--config", required=True, help="reviewer/provider JSON configuration")
    parser.add_argument("--request", required=True, help="request JSON")
    parser.add_argument("--memory-db", default="review-engine-memory.db")
    parser.add_argument("--sessions-db", default="review-engine-sessions.db")
    args = parser.parse_args()
    result = run_from_files(config_path=args.config, request_path=args.request, memory_db=args.memory_db, sessions_db=args.sessions_db)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__": raise SystemExit(main())

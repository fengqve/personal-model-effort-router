"""Optional deterministic helper for the route-model-effort Skill."""
import sys
sys.dont_write_bytecode = True
from model_effort_router.cli import main

if __name__ == "__main__":
    raise SystemExit(main())

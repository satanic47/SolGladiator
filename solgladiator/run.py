"""SolGladiator Launcher Script (Fallback from inner package folder)."""

import sys
from pathlib import Path

# Add project root (parent directory) to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 60)
    print("⚡ Starting SolGladiator Server on http://localhost:8000")
    print("=" * 60 + "\n")
    uvicorn.run("app.server:app", host="0.0.0.0", port=8000, reload=True)

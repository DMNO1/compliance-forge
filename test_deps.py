import sys
try:
    import fastapi
    import httpx
    import dotenv
    print("deps OK")
except ImportError as e:
    print(f"MISSING: {e}")
    sys.exit(1)

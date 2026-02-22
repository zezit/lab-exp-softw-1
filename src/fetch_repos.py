import os
import pathlib

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------

def main() -> None:
    raise NotImplementedError


if __name__ == "__main__":
    main()
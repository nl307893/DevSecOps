import subprocess
import sys
import venv
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
VENV_DIR = ROOT_DIR / ".venv"
REQUIREMENTS_FILE = ROOT_DIR / "requirements.txt"


def get_venv_python() -> Path:
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def main() -> None:
    venv_python = get_venv_python()

    if not venv_python.exists():
        print("Tworzenie środowiska .venv...")
        venv.EnvBuilder(with_pip=True).create(VENV_DIR)

    print("Instalowanie zależności...")
    subprocess.check_call(
        [
            str(venv_python),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "-r",
            str(REQUIREMENTS_FILE),
        ],
        cwd=ROOT_DIR,
    )

    print("Uruchamianie aplikacji pod adresem http://127.0.0.1:5000")
    subprocess.check_call(
        [str(venv_python), "-m", "flask", "--app", "app", "run"],
        cwd=ROOT_DIR,
    )


if __name__ == "__main__":
    main()

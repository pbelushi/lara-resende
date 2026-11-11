"""Roda o pipeline inteiro: calibração → experimento (48 cenários) → sensibilidade → gráficos."""
import contextlib
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from argmodel import calibrate, experiment, report, sensitivity  # noqa: E402

for name, mod in [("calibração", calibrate), ("experimento", experiment),
                  ("sensibilidade", sensitivity), ("gráficos", report)]:
    print(f"-> {name}...", flush=True)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        mod.main()
    (Path(__file__).parent / "outputs" / f"log_{mod.__name__.split('.')[-1]}.txt").write_text(buf.getvalue())
print("pronto — resultados em outputs/")

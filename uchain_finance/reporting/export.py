from pathlib import Path


def ensure_output_dir() -> Path:
    output_dir = Path("data/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def export_dataframe(df, filename: str) -> str:
    output_dir = ensure_output_dir()
    path = output_dir / filename
    df.to_csv(path, index=False)
    return str(path)

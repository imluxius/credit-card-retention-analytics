"""Download the pinned public Kaggle dataset without storing credentials."""
from pathlib import Path
import argparse
import hashlib
import io
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.pipeline import SOURCE_SHA256

URL = 'https://www.kaggle.com/api/v1/datasets/download/sakshigoyal7/credit-card-customers'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'data/raw/BankChurners.csv')
    args = parser.parse_args()
    request = urllib.request.Request(URL, headers={'User-Agent': 'CardScope-Portfolio/1.0'})
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = response.read(10_000_001)
    if len(payload) > 10_000_000:
        raise ValueError('Unexpectedly large download')
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        candidates = [x for x in archive.infolist() if Path(x.filename).name == 'BankChurners.csv']
        if len(candidates) != 1 or candidates[0].file_size > 10_000_000:
            raise ValueError('Unexpected archive contents')
        csv_bytes = archive.read(candidates[0])
    if hashlib.sha256(csv_bytes).hexdigest() != SOURCE_SHA256:
        raise ValueError('Kaggle content changed. Review provenance before replacing the pinned snapshot.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix('.download')
    temporary.write_bytes(csv_bytes)
    temporary.replace(args.output)
    print(f'Verified and saved {args.output.name}: {len(csv_bytes):,} bytes')


if __name__ == '__main__':
    main()

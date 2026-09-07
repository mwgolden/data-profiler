import argparse
import json
import pandas as pd
from pathlib import Path


def percentage(value: str) -> float:
    pct = float(value)

    if not 0.0 < pct <= 1.0:
        raise argparse.ArgumentTypeError(f"sample-pct must be in range (0.0, 1.0]. {value} provided")

    return pct

def json_profiler(args: argparse.Namespace): 
    from data_profiler.json_profiler.profile_json import profile_json
    from data_profiler.json_profiler.models import ProfileOptions, SamplingConfig
    from data_profiler.sampling.strategy import RandomSample

    random_sampling = RandomSample(
        sample_pct=args.sample_pct,
        sample_cnt=args.sample_cnt,
        max_sample_size=args.max_sample_size,
        with_replacement=args.with_replacement,
        seed=args.seed
    )

    sampling_config = SamplingConfig(
        sampling_strategy=random_sampling
    )

    options = ProfileOptions(
        sampling_options=sampling_config
    )

    data_path = Path(args.path)
    output_path = Path(args.output_path)

    with open(data_path, 'r') as f:
        raw_data = json.load(f)

    profile = profile_json(raw_data,options)

    output_path.mkdir(parents=True, exist_ok=True)
    with open(output_path / "profile.json", 'w') as f:
        json.dump(profile.to_dict(), f, indent=4)


    exploded = profile.explode()

    df = pd.DataFrame(exploded)
    df.to_csv(output_path / "exploded_json.csv", index=False)


def main():
    parser = argparse.ArgumentParser(prog="profile")

    subparsers = parser.add_subparsers(dest="format", required=True)

    json_parser = subparsers.add_parser("json")
    json_parser.add_argument(
        "--path",
        type=Path
    )

    json_parser.add_argument(
        "--output-path",
        type=Path
    )

    json_parser.add_argument(
        "--sampling-strategy",
        choices=["random"],
        default="random"
    )

    json_parser.add_argument(
        "--sample-pct",
        type=percentage,
        default=1.0
    )

    json_parser.add_argument(
        "--sample-cnt",
        type=int,
        default=None
    )

    json_parser.add_argument(
        "--max-sample-size",
        type=int,
        default=0
    )

    json_parser.add_argument(
        "--with-replacement",
        action="store_true"
    )

    json_parser.add_argument("--seed")

    json_parser.set_defaults(func=json_profiler)

    args = parser.parse_args()

    json_profiler(args)
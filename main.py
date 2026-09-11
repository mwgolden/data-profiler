from pathlib import Path
import json
import pandas as pd
from report.json_report import generate_report

#raw_path = Path(Path.cwd() / "data" / "raw" /"food-enforcement-0001-of-0001.json")
#raw_path = Path(Path.cwd() / "data" / "raw" /"address.json")
raw_path = Path(Path.cwd() / "data" / "raw" / "0_1qgyjdg.json")


with open(raw_path, 'r') as f:
    raw_data = json.load(f)

from data_profiler.json_profiler.profile_json import profile_json
from data_profiler.json_profiler.models import ProfileOptions, SamplingConfig
from data_profiler.sampling.strategy import RandomSample

sample_config = SamplingConfig(sampling_strategy=RandomSample(sample_pct=1))

options = ProfileOptions(sampling_options=sample_config)


profile = profile_json(raw_data,options)

with open("./output/profile.json", 'w') as f:
    json.dump(profile.to_dict(), f, indent=4)


exploded = profile.explode()

df = pd.DataFrame(exploded)
df.to_csv("./output/exploded_json.csv", index=False)

generate_report(df)
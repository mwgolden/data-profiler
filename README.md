# data-profiler
# Data Profiler

A Python utility for profiling structured and semi-structured data and generating detailed metadata about its structure, types, values, and relationships.

The profiler builds an intermediate representation of the JSON structure as an abstract syntax tree (AST), capturing information about nodes, paths, types, values, and relationships. The AST can be serialized to JSON or exploded into a tabular CSV representation for analysis.

## Current Support

The project currently supports:

* **JSON** input
* Exploded/flattened CSV output

## CLI

The project provides a `profile` command.

### Usage

```text
profile json [options]
```

The JSON profiler accepts an input file, sampling configuration, and an output directory.

### Options

| Option                | Type     |  Default | Description                                                                          |
| --------------------- | -------- | -------: | ------------------------------------------------------------------------------------ |
| `--path`              | `Path`   |        — | Path to the JSON input file                                                          |
| `--output-path`       | `Path`   |        — | Directory where profiling results are written                                        |
| `--sampling-strategy` | `random` | `random` | Sampling strategy to use                                                             |
| `--sample-pct`        | `float`  |    `1.0` | Percentage of array elements to sample, expressed as a value between `0.0` and `1.0` |
| `--sample-cnt`        | `int`    |   `None` | Maximum number of elements to sample                                                 |
| `--max-sample-size`   | `int`    |   `None` | Maximum number of elements that can be sampled                                       |
| `--with-replacement`  | flag     |  `False` | Sample array elements with replacement                                               |
| `--seed`              | string   |   `None` | Random seed used by the sampling strategy                                            |

### Sampling Percentage

`--sample-pct` accepts a value greater than `0.0` and less than or equal to `1.0`.

For example:

```bash
--sample-pct 1.0
```

samples 100% of the data, while:

```bash
--sample-pct 0.1
```

samples 10%.

## Examples

### Profile a JSON file

```bash
profile json \
    --path ./raw/data.json \
    --output-path ./output
```

This produces:

```text
output/
├── profile.json
└── exploded_json.csv
```

### Sample 10% of array elements

```bash
profile json \
    --path ./raw/data.json \
    --output-path ./output \
    --sample-pct 0.1
```

### Sample a fixed number of elements

```bash
profile json \
    --path ./raw/data.json \
    --output-path ./output \
    --sample-cnt 1000
```

### Limit the maximum sample size

```bash
profile json \
    --path ./raw/data.json \
    --output-path ./output \
    --max-sample-size 5000
```

### Sample with replacement

```bash
profile json \
    --path ./raw/data.json \
    --output-path ./output \
    --with-replacement
```

### Specify a random seed

```bash
profile json \
    --path ./raw/data.json \
    --output-path ./output \
    --sample-pct 0.1 \
    --seed 42
```

Using a fixed seed allows a sampling run to be reproduced.

## Output

### `profile.json`

Contains the serialized intermediate AST representation produced by the JSON profiler. The representation captures the hierarchical structure of the source JSON along with profiling metadata for each node.

### `exploded_json.csv`

Contains a flattened representation of the intermediate AST, making the hierarchical profiling information easier to inspect and analyze with tabular tools such as pandas or SQL.

## Project Structure

The project uses a `src` layout:

```text
src/
├── profile_cli/
│   └── main.py
└── data_profiler/
    ├── json_profiler/
    └── sampling/
```

The CLI is an entry point to the profiling functionality; profiling and sampling logic are implemented independently of the command-line interface.

## Installation

The project uses [uv](https://docs.astral.sh/uv/) for project and dependency management.

Install/synchronize the project environment with:

```bash
uv sync
```

The CLI can then be run with:

```bash
uv run profile json --path ./raw/data.json --output-path ./output
```

When the environment is activated, the command can also be invoked directly:

```bash
profile json --path ./raw/data.json --output-path ./output
```

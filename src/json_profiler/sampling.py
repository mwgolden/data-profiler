import random
import math
from typing import Protocol, Sequence
from dataclasses import dataclass
from typing import Any

class SamplingStrategy(Protocol):
    def sample(self, size: int) -> Sequence[int]:
        ...

@dataclass
class RandomSample:
    sample_pct: float = 1.0
    sample_cnt: int|None = None
    max_sample_size: int|None = None
    with_replacement: bool = False
    seed: int|float|str|bytes|bytearray|None = None

    def sample(self,size: int):
        """
            Provide a random sample from a list of indexes. 

            Args:
                size: size fo the list to be sampled
            
            Returns:
                A list of sampled indexes from the original list
            
            Raises:
                ValueError: If sample_pct is outside range (0.0: 1.0]
        """
        if self.sample_pct <= 0.0 or self.sample_pct > 1.0:
            raise ValueError(f"sample_pct must be in range (0.0, 1.0]. {self.sample_pct} provided")

        rng = random.Random(self.seed)

        sample_size = min(
            size,
            self.max_sample_size or size
        )

        sample_cnt = self.sample_cnt
        if sample_cnt is None:
            sample_cnt = max(
                1,
                math.floor(float(sample_size) * self.sample_pct)
            )

        if self.with_replacement:
            return rng.choices(range(sample_size), k=sample_cnt)

        return rng.sample(range(sample_size), sample_cnt)


import random
import math
from typing import Protocol, Sequence

class SamplingStrategy(Protocol):
    def sample_indices(self, size: int, pct_sample: float) -> Sequence[int]:
        ...



class RandomSample:
    def sample_indices(self, size: int, pct_sample: float) -> Sequence[int]:
        if pct_sample <= 0.0 or pct_sample > 1.0:
            raise ValueError(f"pct_sample must be in range (0.0, 1.0]. {pct_sample} provided")
        
        sample_count = max(
            1, 
            math.floor((float(size) * pct_sample))
        )

        sample_indexes = random.sample(range(size), sample_count)

        return sample_indexes
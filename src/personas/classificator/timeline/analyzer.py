import collections
from typing import List

from personas.common.post import Post


class TimelineAnalyzer:

    @staticmethod
    def get_preferred_language(timeline: List[Post]) -> str:
        if timeline:
            detected_languages = collections.Counter()
            for post in timeline:
                detected_languages[post.language] += 1

            return detected_languages.most_common(1)[0][0]
        else:
            return None

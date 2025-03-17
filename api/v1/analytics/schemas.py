from pydantic import BaseModel


class AnalyticsSchema(BaseModel):
    total_notes: int = 0
    total_words: int = 0
    avg_words: int = 0
    common_words: dict[str, int] = {}
    top_longest_notes: dict[str, int] = {}
    top_shortest_notes: dict[str, int] = {}

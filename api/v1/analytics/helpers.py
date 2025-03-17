import re
from collections import Counter

import pandas as pd
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.analytics.controllers import get_all_notes_for_analytics
from api.v1.analytics.schemas import AnalyticsSchema
from core.database.db_helper import db_helper


def clean_text(text: str) -> str:
    return re.sub(r"[^a-zA-Zа-яА-ЯёЁ0-9\s]", "", text.lower())


def count_total_and_avg_words(df: pd.DataFrame) -> tuple[int, int]:
    total_words = df["word_count"].sum()
    avg_words = int(df["word_count"].mean())
    return total_words, avg_words


def count_most_common_words(df: pd.DataFrame, top: int) -> dict:
    words = " ".join(df["content"]).lower().split()
    word_counts = Counter(words)
    common_words = dict(word_counts.most_common(top))
    return common_words


def count_top_shortest_and_longest(df: pd.DataFrame, top: int) -> tuple:
    top_longest_notes = dict(
        df.nlargest(top, "word_count")[["title", "word_count"]].values
    )
    top_shortest_notes = dict(
        df.nsmallest(top, "word_count")[["title", "word_count"]].values
    )
    return top_longest_notes, top_shortest_notes


async def get_analytics(session: AsyncSession = Depends(db_helper.session_getter)):
    notes = await get_all_notes_for_analytics(session)
    schema = AnalyticsSchema()
    if not notes:
        return schema

    titles, texts = zip(*notes)

    cleaned_titles = [clean_text(title) for title in titles]
    cleaned_texts = [clean_text(text) for text in texts]

    df = pd.DataFrame({"title": cleaned_titles, "text": cleaned_texts})
    df["content"] = df["title"] + " " + df["text"]
    df["word_count"] = df["content"].apply(lambda x: len(x.split()))

    total_words, avg_words = count_total_and_avg_words(df)

    common_words = count_most_common_words(df, 10)
    top_longest_notes, top_shortest_notes = count_top_shortest_and_longest(df, 3)

    return AnalyticsSchema(
        total_notes=len(df),
        total_words=total_words,
        avg_words=avg_words,
        common_words=common_words,
        top_longest_notes=top_longest_notes,
        top_shortest_notes=top_shortest_notes,
    )

import asyncio
from datetime import datetime

from sqlalchemy import Result, select

from core.database import Note, NoteHistory, User
from core.database.db_helper import db_helper

data_users = [
    {
        "username": "string",
        "password": "$2b$12$frguuxHVXuuI5MpmwaQAgeoFMeQAJ5pz4026sNq5vgmzf1k7lcfNC",
    }
]

data_notes = [
    {
        "user_id": 1,
        "title": "The Solar System",
        "text": (
            "The Solar System consists of the Sun and the objects "
            "that are gravitationally bound to it. This includes "
            "eight planets, their moons, dwarf planets, asteroids, "
            "comets, and other small bodies. The planets are divided "
            "into two groups: the inner rocky planets and the outer gas giants."
        ),
        "summarization": (
            "The Solar System is made up of the Sun, planets, moons, and other objects."
        ),
        "created_at": datetime(2025, 2, 17, 18, 0, 0),
        "updated_at": datetime(2025, 2, 22, 18, 0, 0),
    },
    {
        "user_id": 1,
        "title": "Coffee and Health",
        "text": (
            "Coffee is one of the most popular beverages worldwide, "
            "consumed for its stimulating effects due to caffeine. "
            "Moderate coffee consumption has been linked to several health "
            "benefits, including improved mental alertness, reduced risk "
            "of certain diseases like Parkinson''s and Type 2 diabetes, "
            "and potential longevity benefits. However, excessive intake "
            "can cause anxiety, disrupt sleep, and lead to other health issues."
        ),
        "summarization": (
            "Coffee can be beneficial in moderation but harmful in excess."
        ),
        "created_at": datetime(2025, 2, 17, 18, 0, 0),
        "updated_at": datetime(2025, 2, 22, 18, 0, 0),
    },
    {
        "user_id": 1,
        "title": "The Theory of Evolution",
        "text": (
            "The theory of evolution, proposed by Charles Darwin, "
            "suggests that all species of organisms have descended "
            "from common ancestors and evolved over time through "
            "natural selection. The process involves genetic variation, "
            "survival of the fittest, and the passing of advantageous "
            "traits to offspring. This theory has become a cornerstone "
            "of modern biology, explaining the diversity of life on Earth."
        ),
        "summarization": (
            "Evolution explains how species change and adapt over "
            "time through natural selection."
        ),
        "created_at": datetime(2025, 2, 17, 18, 0, 0),
        "updated_at": datetime(2025, 2, 22, 18, 0, 0),
    },
]

data_note_history = [
    {
        "note_id": 1,
        "title": "The Solar System",
        "text": (
            "The Solar System consists of the Sun and objects gravitationally "
            "bound to it, including eight planets, moons, dwarf planets, "
            "asteroids, comets, and small bodies. The planets are "
            "categorized into rocky inner planets and gas giant outer planets."
        ),
        "created_at": datetime(2025, 2, 22, 18, 0, 0),
    },
    {
        "note_id": 2,
        "title": "Coffee and Health",
        "text": (
            "Coffee is widely consumed for its caffeine effects. "
            "Moderate intake has benefits such as improved alertness "
            "and a reduced risk of diseases like Parkinson's, while "
            "excessive consumption can cause anxiety and disrupt sleep."
        ),
        "created_at": datetime(2025, 2, 22, 18, 0, 0),
    },
    {
        "note_id": 3,
        "title": "The Theory of Evolution",
        "text": (
            "Darwin''s theory of evolution suggests all species descended "
            "from common ancestors, evolving through natural selection. "
            "Genetic variation and survival of the fittest drive "
            "the process, explaining Earth''s biodiversity."
        ),
        "created_at": datetime(2025, 2, 22, 18, 0, 0),
    },
]


async def insert_data():
    async with db_helper.factory() as session:
        stmt = select(Note)
        result: Result = await session.execute(stmt)
        notes = result.scalars().all()
        stmt = select(User)
        result: Result = await session.execute(stmt)
        users = result.scalars().all()
        if not notes and not users:
            session.add_all([User(**user) for user in data_users])
            await session.commit()
            session.add_all([Note(**note) for note in data_notes])
            await session.commit()
            session.add_all([NoteHistory(**history) for history in data_note_history])
            await session.commit()


asyncio.run(insert_data())

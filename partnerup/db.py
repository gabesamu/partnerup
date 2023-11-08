import sqlite3
from enum import Enum
from contextlib import closing
from typing import Optional


class Timeblock(Enum):
    Monday = 1
    Tuesday = 2
    Wednesday = 3
    Thursday = 4
    Friday = 5
    Saturday = 6
    Sunday = 7


    def __str__(self):
        return self.name

    @staticmethod
    def display_schedule(timeblocks: list["Timeblock"] ) -> str:
        return ", ".join(str(timeblock) for timeblock in sorted(timeblocks))



class ScheduleTable:
    def __init__(self, dbPath: str) -> None:
        self.db = dbPath;
        self.conn = sqlite3.connect(self.db)
        self._setup()

    def _setup(self) -> None:
        with closing(self.conn.cursor()) as c:
            c.execute('''CREATE TABLE IF NOT EXISTS schedule
                (guild_id INTEGER,
                timeblock INTEGER,
                user_id INTEGER,
                PRIMARY KEY (guild_id, timeblock, user_id))''')
            self.conn.commit()

    def insert_timeblock(self, timeblock: Timeblock, guild_id: int, user_id: int) -> None:
        with closing(self.conn.cursor()) as c:
            c.execute("INSERT INTO schedule VALUES (?, ?, ?)", (guild_id, timeblock.value, user_id))
            self.conn.commit()


    def delete_timeblock(self, timeblock: Timeblock, guild_id: int, user_id: int) -> None:
        with closing(self.conn.cursor()) as c:
            c.execute("DELETE FROM schedule WHERE guild_id = ? AND timeblock = ? AND user_id = ?",
                      (guild_id, timeblock.value, user_id))
            self.conn.commit()

    def delete_user(self, guild_id: int, user_id: int) -> None:
        with closing(self.conn.cursor()) as c:
            c.execute("DELETE FROM schedule WHERE guild_id = ? AND user_id = ?",
                      (guild_id, user_id))
            self.conn.commit()


    def select_userid(self, guild_id: int, timeblock: Timeblock) -> list[int]:
        with closing(self.conn.cursor()) as c:
            c.execute("SELECT user_id FROM schedule WHERE guild_id = ? AND timeblock = ?",
                      (guild_id, timeblock.value))
            return c.fetchall()


    def select_timeblocks(self, guild_id: int, user_id: int) -> list[Timeblock]:
        with closing(self.conn.cursor()) as c:
            c.execute("SELECT timeblock FROM schedule WHERE guild_id = ? AND user_id = ?",
                      (guild_id, user_id))
            return [Timeblock(row[0]) for row in c.fetchall()]


class GroupsTable:
    def __init__(self, dbPath: str) -> None:
        self.db = dbPath;
        self.conn = sqlite3.connect(self.db)
        self._setup()

    @staticmethod
    def _serialize_userids(user_ids: list[int]) -> str:
        return",".join(map(str, sorted(user_ids)))

    @staticmethod
    def _deserialize_userids(user_ids_str: str) -> list[int]:
        return list(map(int, user_ids_str.split(",")))

    def _setup(self) -> None:
        with closing(self.conn.cursor()) as c:
            c.execute('''CREATE TABLE IF NOT EXISTS pairs
                (guild_id INTEGER,
                user_ids TEXT,
                channel_id INTEGER,
                thread_id INTEGER,
                PRIMARY KEY (guild_id, user_id, partner_id))''')
            self.conn.commit()


    def insert_group(self, guild_id: int, user_ids: list[int], channel_id: int, thread_id: int) -> None:
        with closing(self.conn.cursor()) as c:
            c.execute("INSERT INTO pairs VALUES (?, ?, ?, ?)",
                      (guild_id, GroupsTable._serialize_userids(user_ids), channel_id, thread_id))
            self.conn.commit()

    def delete_group(self, guild_id: int, user_ids: list[int]) -> None:
        with closing(self.conn.cursor()) as c:
            c.execute("DELETE FROM pairs WHERE guild_id = ? AND user_ids = ?",
                      (guild_id, GroupsTable._serialize_userids(user_ids)))
            self.conn.commit()

    def select_thread_id(self, guild_id: int, user_ids: list[int]) -> Optional[int]:
        with closing(self.conn.cursor()) as c:
            c.execute("SELECT thread_id FROM pairs WHERE guild_id = ? AND user_ids = ?",
                      (guild_id, GroupsTable._serialize_userids(user_ids)))
            result = c.fetchone()
            return result[0] if result else None

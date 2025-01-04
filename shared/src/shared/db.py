import logging
from typing import ClassVar, List, Optional, Type

from asyncpg.exceptions import UniqueViolationError
from databases import Database
from pydantic import BaseModel, TypeAdapter

from datetime import datetime
from uuid import UUID

logger = logging.getLogger("databases")


class DatabaseConfig(BaseModel):
    driver: str
    url: str
    port: int
    db_name: str
    username: str
    password: str


class Entity(BaseModel):
    _table_name: ClassVar[Optional[str]] = None
    _pk: ClassVar[Optional[str]] = None

    pass


class AbstractRepository:
    def __init__(self, db: Database, entity: Type):
        self._db = db
        self._entity = entity
        self._table_name = entity._table_name

    def _get_query_parameters(self, dump):
        keys = list(dump.keys())
        columns = ",".join(keys)
        placeholders = ",".join(map(lambda x: f":{x}", keys))
        return columns, placeholders

    async def add(self, entities, ignore_conflict=False):
        if not isinstance(entities, list):
            entities = [entities]

        if entities == []:
            return

        dumps = list(map(lambda x: x.model_dump(), entities))

        columns, placeholders = self._get_query_parameters(dumps[0])

        query = f"INSERT INTO {self._table_name}({columns}) VALUES ({placeholders})"
        logger.debug(f"Executing query: {query}")

        if ignore_conflict:
            query += " ON CONFLICT DO NOTHING"

        await self._db.execute_many(query=query, values=dumps)

    async def update(self, entity, fields: List[str]):
        dump = entity.model_dump()
        query_set = [f"{field} = :{field}" for field in fields]

        pk = entity._pk
        if not isinstance(pk, tuple):
            pk = (pk,)

        where_clause = " AND ".join(f"{key} = :{key}" for key in pk)
        query = (
            f"UPDATE {self._table_name} SET {','.join(query_set)} WHERE {where_clause}"
        )
        logger.debug(f"Executing query: {query}")
        await self._db.execute(
            query=query,
            values={k: dump[k] for k in fields} | {key: dump[key] for key in pk},
        )

    async def get(self, field=None, value=None) -> List:
        query = f"SELECT * FROM {self._table_name}"
        logger.debug(f"Executing query: {query}")
        if field is not None:
            query += f" WHERE {field} = :{field}"
            rows = await self._db.fetch_all(query=query, values={field: value})
        else:
            rows = await self._db.fetch_all(query=query)

        return list(
            map(
                lambda row: TypeAdapter(self._entity).validate_python(
                    dict(row._mapping)
                ),
                rows,
            )
        )


class PgRepository(AbstractRepository):
    async def add_or_update(self, entity: Entity, fields: List[str]):
        try:
            await self.add(entity)
        except UniqueViolationError:
            await self.update(entity, fields)


class IntervalRepository(PgRepository):
    async def get_intersections(
        self, l_bound: datetime, r_bound: datetime, channel_id: int
    ):
        query = f"SELECT * FROM {self._table_name} WHERE r_bound >= :l_bound and l_bound <= :r_bound and channel_id = :channel_id"

        rows = await self._db.fetch_all(
            query=query,
            values={"l_bound": l_bound, "r_bound": r_bound, "channel_id": channel_id},
        )

        return list(map(lambda row: dict(row._mapping), rows))


class SourceRepository(PgRepository):
    async def get_cached(
        self, channel_id: int, left_bound: datetime, right_bound: datetime
    ):
        query = f"SELECT * FROM {self._table_name} WHERE channel_id = :channel_id AND ts <= :right_bound AND ts >= :left_bound"
        rows = await self._db.fetch_all(
            query=query,
            values={
                "channel_id": channel_id,
                "right_bound": right_bound,
                "left_bound": left_bound,
            },
        )
        return list(map(lambda row: dict(row._mapping), rows))


class EmbeddingRepository(PgRepository):
    async def get_by_ids(self, ids: list[UUID]):
        query = f"SELECT * FROM {self._table_name} WHERE source_id = ANY(:ids)"
        rows = await self._db.fetch_all(query=query, values={"ids": ids})
        return list(map(lambda row: dict(row._mapping), rows))


def create_db_string(creds: DatabaseConfig):
    return f"{creds.driver}://{creds.username}:{creds.password}@{creds.url}:{creds.port}/{creds.db_name}"

from typing import List, Type

from asyncpg.exceptions import UniqueViolationError
from databases import Database
from pydantic import TypeAdapter

from shared.entities import Entity
from shared.resources import DatabaseCredentials


def create_db_string(creds: DatabaseCredentials):
    return f"{creds.driver}://{creds.username}:{creds.password}@{creds.url}:{creds.port}/{creds.db_name}"


class AbstractRepository:
    def __init__(self, db: Database, table_name: str):
        self._db = db
        self._table_name = table_name

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

        if ignore_conflict:
            query += " ON CONFLICT DO NOTHING"

        await self._db.execute_many(query=query, values=dumps)

    async def update(self, entity: Entity, fields: List[str]):
        dump = entity.model_dump()

        pk = entity._pk
        query_set = [f"{field} = :{field}" for field in fields]
        query = f"UPDATE {self._table_name} SET {','.join(query_set)} WHERE {pk} = :{pk}"

        await self._db.execute(
            query=query, values={k: dump[k] for k in fields} | {pk: dump[pk]}
        )

    async def get(
        self, cls: Type[Entity], field=None, value=None
    ) -> List[Entity]:
        query = f"SELECT * FROM {self._table_name}"
        if field is not None:
            query += f" WHERE {field} = :{field}"
            rows = await self._db.fetch_all(query=query, values={field: value})
        else:
            rows = await self._db.fetch_all(query=query)

        mapped = map(
            lambda row: TypeAdapter(cls).validate_python(dict(row._mapping)),
            rows,
        )

        return list(mapped)


class PgRepository(AbstractRepository):
    async def add_or_update(self, entity: Entity, fields: List[str]):
        try:
            await self.add(entity)
        except UniqueViolationError:
            await self.update(entity, fields)

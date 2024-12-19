import datetime

from .db import async_engine, async_session
from sqlalchemy import select, insert, update
import json
from .models import *


class Database:
    @staticmethod
    async def db_start():
        await Database.create_tables()
        await Database.db_succes()

    @staticmethod
    async def create_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def db_succes():
        async with async_session() as session:
            print("Подключение к БД прошло успешно!")

    @staticmethod
    async def get_all_users():
        async with async_session() as session:
            query = select(Users)
            result = await session.execute(query)
            list_users = result.scalars().all()
            return list_users
            # [ОбьектЮзер1.id]

    @staticmethod
    async def get_shedule_for_cls(cls: str):
        async with async_session() as session:
            query = select(SchoolShedule.lessons).where(SchoolShedule.cls_rus == cls)
            result = await session.execute(query)
            lessons = result.scalar()
            if lessons:
                return lessons
            return None

    @staticmethod
    async def add_user(user_id: int, username: str, fullname: str):
        async with async_session() as session:
            query = select(Users.username).where(Users.user_id == user_id)
            res = await session.execute(query)
            old_username = res.scalar()

            if old_username is None:
                insert_new_user = insert(Users).values(
                    user_id=user_id,
                    username=username,
                    fullname=fullname
                )
                await session.execute(insert_new_user)

            else:
                if old_username != username:
                    update_user = (update(Users)
                                   .where(Users.user_id == user_id)
                                   .values(username=username,
                                           fullname=fullname))
                    await session.execute(update_user)
            await session.commit()

    @staticmethod
    async def set_favcls(user_id: int, favcls: str):
        async with async_session() as session:
            query = select(Users.favcls).where(Users.user_id == user_id)
            res = await session.execute(query)
            favcls_list = res.scalar()

            if favcls_list and favcls_list[0]:
                new_favcls_list = favcls_list
                if favcls not in new_favcls_list:
                    new_favcls_list.append(favcls)

            else:
                new_favcls_list = [favcls]

            favcls_list_json = new_favcls_list

            query = update(Users).where(Users.user_id == user_id).values(
                favcls=favcls_list_json
            )

            await session.execute(query)
            await session.commit()

    @staticmethod
    async def get_favcls_list(user_id: int):
        async with async_session() as session:
            query = select(Users.favcls).where(Users.user_id == user_id)
            res = await session.execute(query)
            res = res.scalar()

            if res:
                favcls_list = res
                return favcls_list
            else:
                return []

    @staticmethod
    async def del_favcls(user_id: int, cls: str):
        async with async_session() as session:
            favcls_list = await Database.get_favcls_list(user_id)

            if cls in favcls_list:
                favcls_list.remove(cls)

                query = update(Users).where(Users.user_id == user_id).values(
                    favcls=favcls_list
                )
                await session.execute(query)
                await session.commit()
                return True
            else:
                return False

    @staticmethod
    async def get_cls_list():
        async with async_session() as session:
            query = select(SchoolShedule.cls_rus)
            res = await session.execute(query)
            res = res.scalars() # [9а, 9б]
            return res

    @staticmethod
    async def save_result(user_id: int, result: str):
        async with async_session() as session:
            query = insert(Results).values(
                user_id=user_id,
                result=result,
                timestamp=datetime.datetime.now()
            )
            await session.execute(query)
            await session.commit()

    @staticmethod
    async def check_result(user_id: int):
        async with async_session() as session:
            query = select(Results.result, Results.timestamp).where(Results.user_id == user_id)
            res = await session.execute(query)
            res = res.all()
            return res

    @staticmethod
    async def set_task(user_id: int, task_name: str, desc_task: str):
        async with async_session() as session:
            query = insert(Tasks).values(
                user_id=user_id,
                task_name=task_name,
                description=desc_task
            )

            await session.execute(query)
            await session.commit()








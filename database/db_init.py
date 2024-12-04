import random
import string

from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError

from database.database import Database
from database.models import Fraction, FractionsTaskTypes, TaskType


async def db_init(database: Database):
    await database.execute_raw_sql(
        '''
        DROP TABLE IF EXISTS "fractions"; ''')
    await database.execute_raw_sql(
        '''
    CREATE TABLE IF NOT EXISTS "fractions" (
        "id"	INTEGER NOT NULL,
        "city_name"	VARCHAR,
        "branch_name"	TEXT,
        "fraction_name"	VARCHAR,
        PRIMARY KEY("id")
    );''')
    await database.execute_raw_sql(
        '''
    INSERT INTO "fractions" ("id","city_name","branch_name","fraction_name") VALUES (1,'Владимир',NULL,''),
      (2,'Екатеринбург','Все остальные клубы',''),
      (3,'Екатеринбург','Краснолесье, 127',''),
      (4,'Златоуст',NULL,''),
      (5,'Ижевск',NULL,''),
      (6,'Казань',NULL,''),
      (7,'Кемерово',NULL,''),
      (8,'Курск',NULL,''),
      (9,'Липецк',NULL,''),
      (10,'Москва','Нижегородская, 2к1',''),
      (11,'Москва','Мытищи, Лётная, 21',''),
      (12,'Москва','Дмитровское шоссе, 98',''),
      (13,'Москва','Ореховый проезд, 41 стр.2',''),
      (14,'Москва','Кантемировская, 14',NULL),
      (15,'Москва','Южнобутовская, 97',NULL),
      (16,'Москва','Братиславская, 14',NULL),
      (17,'Москва','Бирюлёвская, 43',NULL),
      (18,'Москва','Зюзино. Симферопольский бульвар,17к2',NULL),
      (19,'Москва','Алтуфьево ,80 ',NULL),
      (20,'Москва','Беляево \ Профсоюзная,104 ',NULL),
      (21,'Москва','Лётчика Бабушкина,30',NULL),
      (22,'Москва','Химки. Пр.Мельникова,2б',NULL),
      (23,'Москва','Ул.Гарибальди,21',NULL),
      (24,'Москва',' ул. Санникова, 17, стр. 2',NULL),
      (25,'Магнитогорск',NULL,NULL),
      (26,'Набережные Челны',NULL,NULL),
      (27,'Нижний Новгород','Коминтерна,123',NULL),
      (28,'Нижний Новгород','пл.М.Горького,4',NULL),
      (29,'Нижний Новгород','Ул.Новая,36',NULL),
      (30,'Нижний Новгород','пр.Ленина,28',NULL),
      (31,'Нижний Новгород','Краснодонцев,10',NULL),
      (32,'Нижний Новгород','Мещерский бульвар,7',NULL),
      (33,'Нижний Новгород','Казанское шоссе,5',NULL),
      (34,'Нижний Новгород','пр.Молодёжный,2Б',NULL),
      (35,'Нижний Новгород','пр.Гагарина,212А',NULL),
      (36,'Нижний Новгород','Белинского,106А',NULL),
      (37,'Нижний Новгород','Ванеева,163',NULL),
      (38,'Нижний Новгород','Московский вокзал',NULL),
      (39,'Новосибирск',NULL,NULL),
      (40,'Омск',NULL,NULL),
      (41,'Орёл',NULL,NULL),
      (42,'Оренбург',NULL,NULL),
      (43,'Пермь',NULL,NULL),
      (44,'Самара','Все остальные клубы',NULL),
      (45,'Самара','Московское шоссе,284А',NULL),
      (46,'Санкт-Петербург','Просвещения,49 ',NULL),
      (47,'Санкт-Петербург','Наличная,44к1',NULL),
      (48,'Санкт-Петербург','пр.Испытателей 26к2',NULL),
      (49,'Санкт-Петербург','Московский проспект,208',NULL),
      (50,'Санкт-Петербург','Пр.Косыгина,24',NULL),
      (51,'Санкт-Петербург','Невский проспект,91',NULL),
      (52,'Санкт-Петербург','ул. Коллонтай, д. 12',NULL),
      (53,'Саранск',NULL,NULL),
      (54,'Стерлитамак',NULL,NULL),
      (55,'Тамбов',NULL,NULL),
      (56,'Тверь',NULL,NULL),
      (57,'Тула',NULL,NULL),
      (58,'Тольятти',NULL,NULL),
      (59,'Ульяновск',NULL,NULL),
      (60,'Челябинск','Все остальные клубы',NULL),
      (61,'Челябинск','Ворошилова,57А',NULL),
      (62,'Уфа',NULL,NULL);'''
    )

    db = await database.get_async_session().__anext__()

    # Очистка таблицы FractionsTaskTypes
    async with db.begin():
        delete_stmt = delete(FractionsTaskTypes)
        await db.execute(delete_stmt)
        await db.commit()

    fractions = None
    async with db.begin():
        stmt = select(Fraction)
        result = await db.execute(stmt)
        fractions = result.scalars().all()

    # задаем рандомные типы заданий фракциям на каждый день ивента
    for fraction in fractions:
        for day in range(1, 7 + 1):
            add_fraction_task_type = FractionsTaskTypes(fraction_id=fraction.id,
                                                        task_type=random.choice(list(TaskType)).value,
                                                        day=day,
                                                        )
            db.add(add_fraction_task_type)
    await db.commit()
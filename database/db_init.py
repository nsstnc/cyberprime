import random
import string

from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError

from database.database import Database
from database.models import Fraction, TaskType, Task, Variant


async def db_init(database: Database):
    await database.execute_raw_sql(
        '''
        DROP TABLE IF EXISTS "fractions"; ''')
    await database.execute_raw_sql(
        '''
    CREATE TABLE IF NOT EXISTS "fractions" (
        "id"	INTEGER NOT NULL,
        "city_name"	VARCHAR,
        "fraction_name"	VARCHAR,
        PRIMARY KEY("id")
    );''')

    await database.execute_raw_sql(
        '''
    INSERT INTO "fractions" ("id","city_name","fraction_name") VALUES 
    (1,'Владимир', 'Эльфы'),
      (2,'Екатеринбург','Эльфы'),
      (3,'Златоуст','Хоббиты'),
      (4,'Ижевск','Эльфы'),
      (5,'Казань','Эльфы'),
      (6,'Копейск','Саурон и орки'),
      (7,'Кемерово','Гномы'),
      (8,'Курск','Саурон и орки'),
      (9,'Липецк','Хоббиты'),
      (10,'Москва','Гномы'),
      (11,'Магнитогорск','Саурон и орки'),
      (12,'Набережные Челны','Эльфы'),
      (13,'Нижний Новгород','Эльфы'),
      (14,'Новосибирск','Гномы'),
      (15,'Нижний Тагил','Гномы'),
      (16,'Омск','Саурон и орки'),
      (17,'Орёл','Саурон и орки'),
      (18,'Оренбург','Эльфы'),
      (19,'Пермь','Саурон и орки'),
      (20,'Самара','Гномы'),
      (21,'Санкт-Петербург','Гномы'),
      (22,'Саранск','Саурон и орки'),
      (23,'Стерлитамак','Гномы'),
      (24,'Тамбов','Хоббиты'),
      (25,'Тверь','Хоббиты'),
      (26,'Тула','Гномы'),
      (27,'Тольятти','Эльфы'),
      (28,'Ульяновск','Эльфы'),
      (29,'Челябинск','Эльфы'),
      (30,'Уфа','Гномы');'''
    )

    # ДОБАВЛЯЕМ ЗАДАНИЯ
    await database.execute_raw_sql(
        '''
        DROP TABLE IF EXISTS "tasks"; ''')
    await database.execute_raw_sql(
        '''
    CREATE TABLE IF NOT EXISTS "tasks" (
        "id"	INTEGER NOT NULL,
        "type"	TEXT,
        "day"	INTEGER,
        PRIMARY KEY("id")
    );''')

    tasks = [
        Task(id=1, type=TaskType.PHOTOHUNTING.value, day=1),
        Task(id=2, type=TaskType.PUZZLE.value, day=2),
        Task(id=3, type=TaskType.PUZZLE.value, day=3),
        Task(id=4, type=TaskType.PUZZLE.value, day=4),
        Task(id=5, type=TaskType.PUZZLE.value, day=5),
    ]

    async with database.get_async_session() as db:
        # задаем задания в таблицу
        for task in tasks:
            db.add(task)
        await db.commit()

    # ДОБАВЛЯЕМ ВАРИАНТЫ ЗАДАНИЙ
    await database.execute_raw_sql(
        '''
        DROP TABLE IF EXISTS "variants"; ''')
    await database.execute_raw_sql(
        '''
    CREATE TABLE IF NOT EXISTS "variants" (
        "id"	INTEGER NOT NULL,
        "task_id"	INTEGER,
        "fraction_name" TEXT,
        "image_url"	TEXT,
        "description" TEXT,
        "answer" TEXT,
        "hint" TEXT,
        PRIMARY KEY("id")
    );''')

    variants = [
        Variant(task_id=1,
                fraction_name=None,
                image_url="images/312872f7bf82b118f094ee8d6780101b.jpg",
                description="Моя прелесть, у тебя есть ровно"
                            "сутки , чтобы выполнить задание, найди моё кольцо, и пришли фото."
                            "За креативность +10 очков. Поспеши!",
                answer=None,
                hint=None),

        Variant(task_id=2,
                fraction_name=None,
                image_url="images/cbe4e84c4df8aab1de55222c1306463f.jpg",
                description="Расшифровать загадочные послания от мудрецов Средиземья, чтобы помочь своей"
                            "фракции продвинуться к победе. Это испытание проверит вашу смекалку и знания"
                            "мира 'Властелина колец'!\n\n"
                            "Зашифрованное сообщение:\nIr kdv wluh ri Wkh Rqh ulqj.",
                answer="",
                hint="Поищи метод, где каждое слово немного смещено, как шаги на лестнице. Вспомни древние шифры воинов!"),

        Variant(task_id=2,
                fraction_name=None,
                image_url="images/cbe4e84c4df8aab1de55222c1306463f.jpg",
                description="Расшифровать загадочные послания от мудрецов Средиземья, чтобы помочь своей"
                            "фракции продвинуться к победе. Это испытание проверит вашу смекалку и знания"
                            "мира 'Властелина колец'!\n\n"
                            "Зашифрованное сообщение:\nGsv Ufiif lu Zgvihvihvhz.",
                answer="",
                hint="Прочти это наоборот, как если бы ты смотрел в зеркало. Этот метод часто использовали древние маги."),
        Variant(task_id=2,
                fraction_name=None,
                image_url="images/cbe4e84c4df8aab1de55222c1306463f.jpg",
                description="Расшифровать загадочные послания от мудрецов Средиземья, чтобы помочь своей"
                            "фракции продвинуться к победе. Это испытание проверит вашу смекалку и знания"
                            "мира 'Властелина колец'!\n\n"
                            "Зашифрованное сообщение:\nОМД ИГ ТРИ КИЬЛОНО ЕМШЕНА.",
                answer="",
                hint="Переставь буквы местами, чтобы собрать смысл. Это как собрать меч из осколков."),
        Variant(task_id=2,
                fraction_name=None,
                image_url="images/cbe4e84c4df8aab1de55222c1306463f.jpg",
                description="Расшифровать загадочные послания от мудрецов Средиземья, чтобы помочь своей"
                            "фракции продвинуться к победе. Это испытание проверит вашу смекалку и знания"
                            "мира 'Властелина колец'!\n\n"
                            "Зашифрованное сообщение:\n. .-.. . ..-. / --. .- .-.. .- -.. .-..",
                answer="",
                hint="Эта система использует точки и тире. Найди переводчик, чтобы раскрыть послание. Это как язык света и тени."),
        Variant(task_id=2,
                fraction_name=None,
                image_url="images/cbe4e84c4df8aab1de55222c1306463f.jpg",
                description="Расшифровать загадочные послания от мудрецов Средиземья, чтобы помочь своей"
                            "фракции продвинуться к победе. Это испытание проверит вашу смекалку и знания"
                            "мира 'Властелина колец'!\n\n"
                            "Зашифрованное сообщение:\nɘʞılɿoͻ ɔılɘʞılɿoͻ oɔ ʞılɘʞılɿʞɘ",
                answer="",
                hint="Смотри в отражение, чтобы увидеть истину. Как на поверхности воды."),
        Variant(task_id=2,
                fraction_name=None,
                image_url="images/cbe4e84c4df8aab1de55222c1306463f.jpg",
                description="Расшифровать загадочные послания от мудрецов Средиземья, чтобы помочь своей"
                            "фракции продвинуться к победе. Это испытание проверит вашу смекалку и знания"
                            "мира 'Властелина колец'!\n\n"
                            "Зашифрованное сообщение:\nLvk o yrn grsnj oz ylql hzhqn.",
                answer="",
                hint="Ключ к разгадке скрыт в самом чёрном имени Средиземья. Используй его, чтобы расшифровать."),
        Variant(task_id=2,
                fraction_name=None,
                image_url="images/cbe4e84c4df8aab1de55222c1306463f.jpg",
                description="Расшифровать загадочные послания от мудрецов Средиземья, чтобы помочь своей"
                            "фракции продвинуться к победе. Это испытание проверит вашу смекалку и знания"
                            "мира 'Властелина колец'!\n\n"
                            "Пример шифра:\nᛃᚢᚦᛅᛦᚾᛂ ᛁᛃᚢᛂᚱ ᚦᛂᚢᛆᚴᛁ",
                answer="",
                hint="Эти символы знают только хранители гор. Ищи ключ в рунной письменности гномов."),
        Variant(task_id=2,
                fraction_name=None,
                image_url="images/cbe4e84c4df8aab1de55222c1306463f.jpg",
                description="Расшифровать загадочные послания от мудрецов Средиземья, чтобы помочь своей"
                            "фракции продвинуться к победе. Это испытание проверит вашу смекалку и знания"
                            "мира 'Властелина колец'!\n\n"
                            "Зашифрованное сообщение:\n01101011 01100001 01101101 00100000 01110101 01101110 01100010 01100001 01110010",
                answer="",
                hint="Этот язык используют машины, но ответ связан с древним камнем у дороги. Переведи его в буквы."),
        Variant(task_id=2,
                fraction_name=None,
                image_url="images/cbe4e84c4df8aab1de55222c1306463f.jpg",
                description="Расшифровать загадочные послания от мудрецов Средиземья, чтобы помочь своей"
                            "фракции продвинуться к победе. Это испытание проверит вашу смекалку и знания"
                            "мира 'Властелина колец'!\n\n"
                            "Зашифрованное сообщение:\nАНМОРДЕРС ИРОПДО.",
                answer="",
                hint="Это слово состоит из тех же букв, что и место, где всё закончится. Переставь их, чтобы найти дорогу."),
        Variant(task_id=2,
                fraction_name=None,
                image_url="images/cbe4e84c4df8aab1de55222c1306463f.jpg",
                description="Расшифровать загадочные послания от мудрецов Средиземья, чтобы помочь своей "
                            "фракции продвинуться к победе. Это испытание проверит вашу смекалку и знания"
                            "мира 'Властелина колец'!\n\n"
                            "Зашифрованное сообщение:\nЧтобы найти Кольцо, отправься на север через два леса, затем поверни на восток, к Горе Судьбы.",
                answer=None,
                hint="Внимательно изучи карту. Ты найдёшь истину, если отследишь путь по направлениям."),

        Variant(task_id=3,
                fraction_name=None,
                image_url=None,
                description="Ваши земли в опасности! Чтобы сохранить свою крепость, вам нужно найти два "
                            "заклинания, скрытые в разных местах клуба. Каждое заклинание — это часть "
                            "великой магии. Найдите их и восстановите. Не забывайте, что другим фракциям "
                            "предстоит выполнить это задание тоже! Вы должны быть быстрее, чтобы защитить свою крепость.",
                answer="обвини, часы вечности",
                hint="Это заклинание связано с вечным состоянием и бессмертием."),
        Variant(task_id=4,
                fraction_name="Эльфы",
                image_url="images/DALL·E-2024-12-06-09.08.jpg",
                description="Составьте астрологическую карту Средиземья, ориентируясь на подсказки о звездах\n"
                            "Вечная звезда леса взойдёт на севере, там, где деревья тянутся к небу, а свет её не угаснет даже в самые тёмные ночи.",
                answer="Звезда 'Сияние Лотлориэна'",
                hint=None),
        Variant(task_id=4,
                fraction_name="Хоббиты",
                image_url="images/DALL·E-2024-12-06-09.08.jpg",
                description="Составьте астрологическую карту Средиземья, ориентируясь на подсказки о звездах\n"
                        "Ищи звезду, что мелькает среди полей. Её свет напоминает свечу в уютном доме, где всегда ждёт пир.",
                answer="Звезда 'Сердце Горы'",
                hint=None),
        Variant(task_id=4,
                fraction_name="Гномы",
                image_url="images/DALL·E-2024-12-06-09.08.jpg",
                description="Составьте астрологическую карту Средиземья, ориентируясь на подсказки о звездах\n"
                "Под землёй сияет звезда, которая видна только тому, кто смотрит с вершины горы. Она хранит тайны древних шахт",
                answer="Звезда 'Очаг'",
                hint=None),
        Variant(task_id=4,
                fraction_name="Саурон и орки",
                image_url="images/DALL·E-2024-12-06-09.08.jpg",
                description="Составьте астрологическую карту Средиземья, ориентируясь на подсказки о звездах\n"
                "Красная звезда, вспыхивающая над пепельной равниной, ведёт только к одному месту — к Оке Пламени.",
                answer="Звезда 'Око'",
                hint=None),

        Variant(task_id=5,
                fraction_name="Гномы",
                image_url=None,
                description="Легенды Средиземья скрывают секреты, которые доступны только тем, "
                            "кто понимает язык времени. Перед вами — врата времени. Чтобы их "
                            "открыть, нужно расшифровать код, связанный с великими событиями вашего мира.\n"
                            "Временной код: 13:07:19\n"
                            "Что означают эти числа? Найдите их связь с вашим наследием и ответьте, чтобы открыть врата!",
                answer="13 гномов, 7 колец, эпоха Толкина",
                hint=None),
        Variant(task_id=5,
                fraction_name="Гномы",
                image_url=None,
                description="Легенды Средиземья скрывают секреты, которые доступны только тем, "
                            "кто понимает язык времени. Перед вами — врата времени. Чтобы их "
                            "открыть, нужно расшифровать код, связанный с великими событиями вашего мира.\n"
                            "Временной код: 16:02:03\n"
                            "Что означают эти числа? Найдите их связь с вашим наследием и ответьте, чтобы открыть врата!",
                answer="Эребор, короли, войны",
                hint=None),
        Variant(task_id=5,
                fraction_name="Эльфы",
                image_url=None,
                description="Легенды Средиземья скрывают секреты, которые доступны только тем, "
                            "кто понимает язык времени. Перед вами — врата времени. Чтобы их "
                            "открыть, нужно расшифровать код, связанный с великими событиями вашего мира.\n"
                            "Временной код: 19:03:14\n"
                            "Что означают эти числа? Найдите их связь с вашим наследием и ответьте, чтобы открыть врата!",
                answer="19 колец, 3 эльфийских кольца, Лотлориэн",
                hint=None),
        Variant(task_id=5,
                fraction_name="Эльфы",
                image_url=None,
                description="Легенды Средиземья скрывают секреты, которые доступны только тем, "
                            "кто понимает язык времени. Перед вами — врата времени. Чтобы их "
                            "открыть, нужно расшифровать код, связанный с великими событиями вашего мира.\n"
                            "Временной код: 21:06:01\n"
                            "Что означают эти числа? Найдите их связь с вашим наследием и ответьте, чтобы открыть врата!",
                answer="Звёзды, леса, свет",
                hint=None),
        Variant(task_id=5,
                fraction_name="Саурон и орки",
                image_url=None,
                description="Легенды Средиземья скрывают секреты, которые доступны только тем, "
                            "кто понимает язык времени. Перед вами — врата времени. Чтобы их "
                            "открыть, нужно расшифровать код, связанный с великими событиями вашего мира.\n"
                            "Временной код: 09:01:24\n"
                            "Что означают эти числа? Найдите их связь с вашим наследием и ответьте, чтобы открыть врата!",
                answer="Назгулы, Кольцо, вечность",
                hint=None),
        Variant(task_id=5,
                fraction_name="Саурон и орки",
                image_url=None,
                description="Легенды Средиземья скрывают секреты, которые доступны только тем, "
                            "кто понимает язык времени. Перед вами — врата времени. Чтобы их "
                            "открыть, нужно расшифровать код, связанный с великими событиями вашего мира.\n"
                            "Временной код: 11:05:66\n"
                            "Что означают эти числа? Найдите их связь с вашим наследием и ответьте, чтобы открыть врата!",
                answer="Барад-Дур, армии, падение",
                hint=None),
        Variant(task_id=5,
                fraction_name="Хоббиты",
                image_url=None,
                description="Легенды Средиземья скрывают секреты, которые доступны только тем, "
                            "кто понимает язык времени. Перед вами — врата времени. Чтобы их "
                            "открыть, нужно расшифровать код, связанный с великими событиями вашего мира.\n"
                            "Временной код: 14:10:33\n"
                            "Что означают эти числа? Найдите их связь с вашим наследием и ответьте, чтобы открыть врата!",
                answer="Пироги, палантиры, Фродо",
                hint=None),
        Variant(task_id=5,
                fraction_name="Хоббиты",
                image_url=None,
                description="Легенды Средиземья скрывают секреты, которые доступны только тем, "
                            "кто понимает язык времени. Перед вами — врата времени. Чтобы их "
                            "открыть, нужно расшифровать код, связанный с великими событиями вашего мира.\n"
                            "Временной код: 18:00:22\n"
                            "Что означают эти числа? Найдите их связь с вашим наследием и ответьте, чтобы открыть врата!",
                answer="Урожай, скромность, герои",
                hint=None),
    ]
    async with database.get_async_session() as db:
        # задаем задания в таблицу
        for variant in variants:
            db.add(variant)
        await db.commit()

    # # Очистка таблицы FractionsTaskTypes
    # async with database.get_async_session() as db:
    #     delete_stmt = delete(FractionsTaskTypes)
    #     await db.execute(delete_stmt)
    #     await db.commit()
    #
    # fractions = None
    # async with database.get_async_session() as db:
    #     stmt = select(Fraction)
    #     result = await db.execute(stmt)
    #     fractions = result.scalars().all()
    #
    #     # задаем рандомные типы заданий фракциям на каждый день ивента
    #     for fraction in fractions:
    #         for day in range(1, 5 + 1):
    #             add_fraction_task_type = FractionsTaskTypes(fraction_id=fraction.id,
    #                                                         task_type=random.choice(list(TaskType)).value,
    #                                                         day=day,
    #                                                         )
    #             db.add(add_fraction_task_type)
    #     await db.commit()

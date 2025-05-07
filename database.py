import aiosqlite

DATABASE_NAME = 'database.db'

async def init_db():
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                worker INTEGER,
                is_worker BOOLEAN NOT NULL DEFAULT 0
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS mamonts (
                unique_id TEXT PRIMARY KEY,
                user_id INTEGER,
                online BOOLEAN NOT NULL DEFAULT 0,
                steal_key TEXT NOT NULL
            )
        ''')
        await db.commit()
    print("initialize db")

async def add_user(user_id, is_worker=False, worker="Неизвестный"):
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute('INSERT INTO users (user_id, is_worker, worker) VALUES (?, ?, ?)', (user_id, is_worker, worker))
        await db.commit()

async def is_user_exists(user_id):
    async with aiosqlite.connect(DATABASE_NAME) as db:
        async with db.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,)) as cursor:
            return await cursor.fetchone() is not None

async def set_worker(user_id, is_worker):
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute('UPDATE users SET is_worker = ? WHERE user_id = ?', (is_worker, user_id))
        await db.commit()

async def add_mamont(unique_id, user_id, steal_key):
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute('INSERT INTO mamonts (unique_id, user_id, steal_key) VALUES (?, ?, ?)', (unique_id, user_id, steal_key))
        await db.commit()

async def is_mamont_exists(unique_id):
    async with aiosqlite.connect(DATABASE_NAME) as db:
        async with db.execute('SELECT 1 FROM mamonts WHERE unique_id = ?', (unique_id,)) as cursor:
            return await cursor.fetchone() is not None

async def del_mamont(unique_id):
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute('DELETE FROM mamonts WHERE unique_id = ?', (unique_id,))
        await db.commit()

async def update_key_mamont(unique_id, steal_key):
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute('UPDATE mamonts SET steal_key = ? WHERE unique_id = ?', (steal_key, unique_id))
        await db.commit()

async def update_mamont(unique_id, online):
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute('UPDATE mamonts SET online = ? WHERE unique_id = ?', (online, unique_id))
        await db.commit()

async def is_steal_key_valid(unique_id, steal_key):
    async with aiosqlite.connect(DATABASE_NAME) as db:
        async with db.execute('SELECT 1 FROM mamonts WHERE unique_id = ? AND steal_key = ?', (unique_id, steal_key)) as cursor:
            return await cursor.fetchone() is not None

async def get_worker_by_mamont_id(user_id):
    async with aiosqlite.connect(DATABASE_NAME) as db:
        async with db.execute('SELECT worker FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None
import sqlite3
import datetime
import traceback


class Sqlite:

    connection = None
    cursor = None
    chat_id = 0

    def __init__(self):
        self.connection = sqlite3.connect("database.db")
        self.cursor = self.connection.cursor()
        self.global_tables_initialise()


    def execute_query(self, query):
        print(query)
        self.cursor.execute(query)


# Locale abbreviations: https://www.science.co.il/language/Locale-codes.php

    def global_tables_initialise(self):
        sql_create_songs_table = f"CREATE TABLE IF NOT EXISTS songs (" \
                                 f"artist TEXT, " \
                                 f"title TEXT," \
                                 f"lirycs TEXT," \
                                 f"original_tone TEXT, " \
                                 f"user_tone INTEGER, " \
                                 f"date_created TEXT," \
                                 f"date_modified TEXT," \
                                 f"tags TEXT," \
                                 f"file TEXT);"
        sql_create_tags_table = f"CREATE TABLE IF NOT EXISTS tags (" \
                                 f"tag TEXT NOT NULL UNIQUE);"


        self.cursor.execute(sql_create_songs_table)
        self.cursor.execute(sql_create_tags_table)
        print(" Global Sqlite Database tables created succesfully")

    def insert_song(self, artist, title):
        try:
            sql = f'INSERT OR IGNORE INTO songs(artist, title, user_tone, date_created, tags) ' \
                  f'VALUES("{artist}", "{title}", 0, ' \
                  f'"{datetime.datetime.today().strftime("%y-%m-%d %H.%M.%S")}", "") '
            print(sql)
            self.cursor.execute(sql)
            lastId = self.cursor.lastrowid
            self.connection.commit()
            return lastId
        except Exception as e:
            traceback.print_exc()

    def insert_tag(self, tag):
        try:
            sql = f'INSERT OR IGNORE INTO tags(tag) ' \
                  f'VALUES("{tag}") '
            print(sql)
            self.cursor.execute(sql)
            lastId = self.cursor.lastrowid
            self.connection.commit()
            return lastId
        except Exception as e:
            traceback.print_exc()

    def get_songs(self):
        self.cursor.execute(f"SELECT rowid, * FROM songs ORDER BY artist DESC;")
        rows = self.cursor.fetchall()
        return rows

    def get_tags(self):
        self.cursor.execute(f"SELECT * FROM tags ORDER BY tag DESC;")
        rows = self.cursor.fetchall()
        tags = []
        for tag in rows:
            tags.append(tag[0])
        return tags

    def get_song_by_id(self, id):
        self.cursor.execute(f"SELECT * FROM songs WHERE rowid = {id};")
        rows = self.cursor.fetchall()
        return rows[0]

    def select_song_by_tag(self, tag):
        query = f"SELECT * FROM songs WHERE tags LIKE '%{tag}%';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        print(query)
        print(f"rows: {rows}")
        if len(rows) > 0:
            return rows[0]
        else:
            return rows

    def get_artists(self):
        self.cursor.execute(f"SELECT DISTINCT artist FROM songs ORDER BY artist DESC;")
        rows = self.cursor.fetchall()
        artists = []
        for artist in rows:
            artists.append(artist[0])
        print("", artists)
        return artists

    def update_song(self, rowid, artist, title, lyrics, original_tone, tags=""):
        lyrics = lyrics.replace('"',"'")
        sql = f'UPDATE songs SET artist="{artist}", title="{title}", lirycs="{lyrics}",' \
              f'original_tone="{original_tone}",' \
              f'date_modified="{datetime.datetime.today().strftime("%y-%m-%d %H.%M.%S")}",' \
              f'tags="{tags}" ' \
              f'WHERE rowid = {rowid};'
        print(sql)
        cur = self.connection.cursor()
        cur.execute(sql)
        self.connection.commit()

    def update_song_user_tone(self, rowid, user_tone):
        sql = f'UPDATE songs SET user_tone="{user_tone}", ' \
              f'date_modified="{datetime.datetime.today().strftime("%y-%m-%d %H.%M.%S")}" ' \
              f'WHERE rowid = {rowid};'
        print(sql)
        cur = self.connection.cursor()
        cur.execute(sql)
        self.connection.commit()

    def update_song_file(self, rowid, file):
        sql = f'UPDATE songs SET file="{file}", ' \
          f'date_modified="{datetime.datetime.today().strftime("%y-%m-%d %H.%M.%S")}" ' \
              f'WHERE rowid = {rowid};'
        print(sql)
        cur = self.connection.cursor()
        cur.execute(sql)
        self.connection.commit()

    def update_user_tone(self, rowid, tone):
        sql = f'UPDATE songs SET user_tone="{tone}" WHERE rowid = {rowid};'
        print(sql)
        cur = self.connection.cursor()
        cur.execute(sql)
        self.connection.commit()

    def delete_song(self, rowid):
        sql = f"DELETE FROM songs WHERE rowid = {rowid}"
        print(sql)
        cur = self.connection.cursor()
        cur.execute(sql)
        self.connection.commit()

    def delete_tag(self, tag):
        sql = f"DELETE FROM tags WHERE tag = '{tag}'"
        print(sql)
        cur = self.connection.cursor()
        cur.execute(sql)
        self.connection.commit()


    def alter_table_add_column(self):
        sql = '''ALTER TABLE users_-1001139202549 ADD COLUMN warns;'''

    def get_chats_ids(self):
        self.cursor.execute(f"SELECT chat_id FROM chats")
        rows = self.cursor.fetchall()
        ids = []
        for row in rows:
            ids.append(row[0])
        return ids


    def get_chats_by_tag(self, tag):
        self.cursor.execute(f"SELECT * FROM chats WHERE tags LIKE '%{tag}%' ORDER BY priority ASC;")
        rows = self.cursor.fetchall()
        return rows

    def get_chat_by_id(self, chat_id):
        self.cursor.execute(f"SELECT title, link FROM chats WHERE chat_id = {chat_id} ;")
        rows = self.cursor.fetchall()
        return rows

    def scoreboard(self):
        sql = ''' SELECT user_id, score FROM users_{ci} ORDER BY score DESC LIMIT 20; '''.format(ci=self.chat_id)
        rows = self.cursor.execute(sql)
        self.connection.commit()
        return rows

    def search_reaction(self, message_id, user_id):
        self.cursor.execute("SELECT rowid,message_id,user_id,reaction,date FROM reactions_"+str(self.chat_id)+" WHERE message_id="+str(message_id)+" AND user_id="+str(user_id))
        rows = self.cursor.fetchall()
        return rows

    def get_user(self, user_id):
        self.cursor.execute("SELECT rowid,user_id,score,warns FROM users_"+str(self.chat_id)+" WHERE user_id="+str(user_id))
        rows = self.cursor.fetchall()
        return rows

    def get_users(self, chat_id):
        chat_id = str(chat_id).replace("-", "N")
        self.cursor.execute(f"SELECT rowid,user_id,score,warns FROM users_{chat_id}")
        rows = self.cursor.fetchall()
        return rows

    def get_warns(self, user_id):
        query = "SELECT warns FROM users_"+str(self.chat_id)+" WHERE user_id="+str(user_id)
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def print_reactions(self):
        self.cursor.execute(
            "SELECT * FROM reactions_"+str(self.chat_id)+"")
        rows = self.cursor.fetchall()
        print("Table Reactions: " )
        print(*rows)

    def print_scores(self):
        self.cursor.execute(
            "SELECT * FROM users_"+str(self.chat_id)+"")
        rows = self.cursor.fetchall()
        # print("Table users: " )
        # print(*rows)

    def update_reactions(self, data):
        """
        update priority, begin_date, and end date of a task
        :param conn:
        :param task:
        :return: project id
        """
        sql = ''' UPDATE reactions_{ci} SET reaction = ? WHERE rowid = ?'''.format(ci=self.chat_id)
        cur = self.connection.cursor()
        cur.execute(sql, data)
        self.connection.commit()

    def update_chat(self, chat):
        """
        update priority, begin_date, and end date of a task
        :param conn:
        :param task:
        :return: project id
        """
        admins_ids = ""
        members_count = chat.get_members_count()
        if "group" in chat.type:
            chat_admins = chat.get_administrators()
            for chat_admin in chat_admins:
                admin_id = chat_admin.user.id
                admins_ids = f"{admins_ids} {admin_id}"
        sql = f'UPDATE chats SET title="{chat.title}", link="{chat.link}", description="{chat.description}", ' \
              f'admins="{admins_ids}", members={members_count} ' \
              f'WHERE chat_id = {chat.id}'
        cur = self.connection.cursor()
        cur.execute(sql)
        self.connection.commit()

    def update_global_user(self, user, chat_id):
        sql = f'UPDATE users SET name="{user.full_name}", username="{user.username}", ' \
              f'WHERE chat_id = {chat_id}'
        cur = self.connection.cursor()
        cur.execute(sql)
        self.connection.commit()

    def increase_score(self, user_id, score):
        """
        update priority, begin_date, and end date of a task
        :param conn:
        :param task:
        :return: project id
        """
        sql = ''' UPDATE users_{ci} SET score = score + {score} WHERE user_id = {user_id}'''.format(ci=self.chat_id, user_id=user_id, score=score)
        print(sql)
        cur = self.connection.cursor()
        cur.execute(sql)
        self.connection.commit()

    def warn(self, chat_id, user_id):
        """
                update priority, begin_date, and end date of a task
                :param conn:
                :param task:
                :return: project id
                """
        chat_id = str(chat_id).replace("-", "N")
        sql = ''' UPDATE users_{ci}
                  SET warns = warns + 1
                  WHERE user_id = {user_id}'''.format(ci=chat_id, user_id=user_id)
        print(sql)
        cur = self.connection.cursor()
        cur.execute(sql)
        self.connection.commit()

    def reset_warns(self, data):
        sql = ''' UPDATE users_{ci} SET warns = 0 WHERE user_id = ?'''.format(ci=self.chat_id)
        cur = self.connection.cursor()
        cur.execute(sql, data)
        self.connection.commit()

    def drop_scores_table(self):
        sql = ' DROP TABLE  users_'+str(self.chat_id)
        lastId = self.cursor.execute(sql)
        self.connection.commit()
        return lastId

    # def lookup_for_tags(self, chat):
    #     try:
    #         timestamp = datetime.datetime.now().strftime('%y/%b/%d %H:%M:%S')
    #         print(f"--- {timestamp} LOOKUP FOR TAGS IN CHAT INFO ---")
    #         chat_title = chat.title
    #         chat_description = chat.description
    #         if(chat_description is None ): chat_description = ""
    #         chat_username = chat.username
    #         chat_info = f"{chat_title} {chat_description} {chat_username}".lower()
    #         print("Chat Info: " + chat_info)
    #         predefined_tags = configurations.get_chat_tags()
    #         tags = []
    #         for item in predefined_tags.items():
    #             # print(f"Validating in chat description and title tag: {item[0]}")
    #             match = re.search(item[1],chat_info)
    #             if item[1] != "" and match is not None:
    #                 tags.append(item[0])
    #                 print(f"Tag {item[0]} founded in chat info")
    #                 continue
    #         print("Tags founded in chat info: ", tags)
    #         return tags
    #     except Exception as e:
    #         traceback.print_exc()

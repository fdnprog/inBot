import sqlite3

class DB:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def getAllGroups(self):
        result = self.cursor.execute("SELECT * FROM `groups`")
        return result.fetchall()

    def groupExists(self, group_id):
        result = self.cursor.execute("SELECT `id` FROM `groups` WHERE `group_id` = ?", (group_id,))
        return bool(len(result.fetchall()))

    def addGroup(self, group_id):
        if not self.groupExists(group_id):
            self.cursor.execute("INSERT INTO `groups` (`group_id`) VALUES (?)", (group_id,))
            return True
        else:
            return False

    def userInGroupExists(self, user_id, group_id):
        result = self.cursor.execute("SELECT `user_id` FROM `users` WHERE `group_id` = ?", (group_id,))
        for i in result.fetchall():
            if (i[0] == user_id):
                return True

        return False

    def addUser(self, user_id, username, first_name, group_id, tag_is_able=True):
        if not self.userInGroupExists(user_id, group_id):
            self.cursor.execute("INSERT INTO `users` (`user_id`, `username`, `first_name`, `group_id`, `tag_is_able`) VALUES (?, ?, ?, ?, ?)", (user_id, username, first_name, group_id, tag_is_able))
            return True
        else:
            return False

    def deleteUser(self, user_id, group_id):
        if self.userInGroupExists(user_id, group_id):
            self.cursor.execute("DELETE FROM `users` WHERE `user_id` = ? AND `group_id` = ?", (user_id, group_id))
            return True
        else:
            return False

    def tagUser(self, user_id, group_id, tag_is_able=True):
        self.cursor.execute("UPDATE `users` SET `tag_is_able` = ? WHERE `user_id` = ? AND `group_id` = ?", (tag_is_able, user_id, group_id))
        return True

    def changeUserTag(self, user_id, username):
        self.cursor.execute("UPDATE `users` SET `username` = ? WHERE `user_id` = ?", (username, user_id))
        return True

    def getUserTagsByGroupId(self, group_id, all = True):
        if all:
            result = self.cursor.execute("SELECT `username` FROM `users` WHERE `group_id` = ?", (group_id,))
        else:
            result = self.cursor.execute("SELECT `username` FROM `users` WHERE `group_id` = ? AND `tag_is_able` = ?", (group_id, True,))
        return result.fetchall()

    def getAllUsers(self, group_id):
        if self.groupExists(group_id):
            result = self.cursor.execute("SELECT * FROM `users` WHERE `group_id` = ?", (group_id,))
            return result.fetchall()
        else:
            return False

    def close(self):
        self.conn.close()
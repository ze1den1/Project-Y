import sqlite3


class Hero_charecteristics:
    def __init__(self):
        self.con = sqlite3.connect("database.sqlite")
        self.cur = self.con.cursor()
        self.speed = 100
        self.hp = 100
        self.cur.execute("SELECT power FROM hero WHERE power")
        self.power = self.cur.fetchall()
        self.cur.execute("SELECT armor FROM hero WHERE armor")
        self.armor = self.cur.fetchall()
        print(self.armor, self.power)

    def return_speed(self):
        return self.speed

    def return_hp(self):
        return self.hp

    def return_power(self):
        return self.power

    def return_armor(self):
        return self.armor


class Enemies_charecteristics:
    def __init__(self):
        self.con = sqlite3.connect("database.sqlite")
        self.cur = self.con.cursor()
        self.speed = 100
        self.hp = 100
        self.cur.execute("SELECT power FROM enemies WHERE power")
        self.power = self.cur.fetchall()
        self.cur.execute("SELECT armor FROM enemies WHERE armor")
        self.armor = self.cur.fetchall()
        print(self.armor, self.power)

    def return_speed(self):
        return self.speed

    def return_hp(self):
        return self.hp

    def return_power(self):
        return self.power

    def return_armor(self):
        return self.armor

from lib import CURSOR, CONN
from lib.employee import Employee

class Department:
    all = {}

    def __init__(self, name, location, id=None):
        self.id = id
        self.name = name
        self.location = location

    def __repr__(self):
        return f"<Department {self.id}: {self.name}, {self.location}>"

    # ==== Property Setters ====

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if isinstance(value, str) and len(value.strip()) > 0:
            self._name = value.strip()
        else:
            raise ValueError("Name must be a non-empty string")

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        if isinstance(value, str) and len(value.strip()) > 0:
            self._location = value.strip()
        else:
            raise ValueError("Location must be a non-empty string")

    # ==== Table methods ====

    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY,
                name TEXT,
                location TEXT
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS departments")
        CONN.commit()

    def save(self):
        sql = """
            INSERT INTO departments (name, location)
            VALUES (?, ?)
        """
        CURSOR.execute(sql, (self.name, self.location))
        CONN.commit()
        self.id = CURSOR.lastrowid
        Department.all[self.id] = self

    def update(self):
        sql = """
            UPDATE departments
            SET name = ?, location = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.location, self.id))
        CONN.commit()

    def delete(self):
        sql = "DELETE FROM departments WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        if self.id in Department.all:
            del Department.all[self.id]
        self.id = None

    @classmethod
    def create(cls, name, location):
        dept = cls(name, location)
        dept.save()
        return dept

    @classmethod
    def instance_from_db(cls, row):
        dept_id = row[0]
        if dept_id in cls.all:
            dept = cls.all[dept_id]
            dept.name = row[1]
            dept.location = row[2]
        else:
            dept = cls(row[1], row[2], dept_id)
            cls.all[dept_id] = dept
        return dept

    @classmethod
    def find_by_id(cls, id):
        CURSOR.execute("SELECT * FROM departments WHERE id = ?", (id,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_name(cls, name):
        CURSOR.execute("SELECT * FROM departments WHERE name = ?", (name,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def get_all(cls):
        CURSOR.execute("SELECT * FROM departments")
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    def employees(self):
        CURSOR.execute("SELECT * FROM employees WHERE department_id = ?", (self.id,))
        rows = CURSOR.fetchall()
        return [Employee.instance_from_db(row) for row in rows]

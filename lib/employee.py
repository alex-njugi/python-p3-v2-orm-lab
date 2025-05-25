from lib import CONN, CURSOR

class Employee:
    all = {}

    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self.name = name
        self.job_title = job_title
        self.department_id = department_id

    def __repr__(self):
        return f"<Employee {self.id}: {self.name}>"

    @classmethod
    def create_table(cls):
        CURSOR.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT,
                job_title TEXT,
                department_id INTEGER,
                FOREIGN KEY (department_id) REFERENCES departments(id)
            )
        """)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS employees")
        CONN.commit()

    @classmethod
    def create(cls, name, job_title, department_id):
        employee = cls(name, job_title, department_id)
        employee.save()
        return employee

    def save(self):
        if self.id:
            self.update()
        else:
            CURSOR.execute(
                "INSERT INTO employees (name, job_title, department_id) VALUES (?, ?, ?)",
                (self.name, self.job_title, self.department_id)
            )
            CONN.commit()
            self.id = CURSOR.lastrowid
            Employee.all[self.id] = self

    @classmethod
    def instance_from_db(cls, row):
        id, name, job_title, department_id = row
        if id in cls.all:
            return cls.all[id]
        employee = cls(name, job_title, department_id, id)
        cls.all[id] = employee
        return employee

    def delete(self):
        CURSOR.execute("DELETE FROM employees WHERE id = ?", (self.id,))
        CONN.commit()
        if self.id in Employee.all:
            del Employee.all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        CURSOR.execute("SELECT * FROM employees")
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    def reviews(self):
        from lib.review import Review
        CURSOR.execute("SELECT * FROM reviews WHERE employee_id = ?", (self.id,))
        rows = CURSOR.fetchall()
        return [Review.instance_from_db(row) for row in rows]

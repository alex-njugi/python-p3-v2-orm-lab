from lib import CURSOR, CONN
from lib.department import Department

class Employee:
    all = {}

    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self.name = name
        self.job_title = job_title
        self.department_id = department_id

    def __repr__(self):
        return f"<Employee {self.id}: {self.name}, {self.job_title}, Department ID: {self.department_id}>"

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
    def job_title(self):
        return self._job_title

    @job_title.setter
    def job_title(self, value):
        if isinstance(value, str) and len(value.strip()) > 0:
            self._job_title = value.strip()
        else:
            raise ValueError("Job title must be a non-empty string")

    @property
    def department_id(self):
        return self._department_id

    @department_id.setter
    def department_id(self, value):
        if isinstance(value, int) and Department.find_by_id(value):
            self._department_id = value
        else:
            raise ValueError("department_id must reference a valid department")

    # ==== Database Table Methods ====

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

    def save(self):
        CURSOR.execute(
            "INSERT INTO employees (name, job_title, department_id) VALUES (?, ?, ?)",
            (self.name, self.job_title, self.department_id)
        )
        CONN.commit()
        self.id = CURSOR.lastrowid
        Employee.all[self.id] = self

    def update(self):
        CURSOR.execute(
            "UPDATE employees SET name = ?, job_title = ?, department_id = ? WHERE id = ?",
            (self.name, self.job_title, self.department_id, self.id)
        )
        CONN.commit()

    def delete(self):
        CURSOR.execute("DELETE FROM employees WHERE id = ?", (self.id,))
        CONN.commit()
        if self.id in Employee.all:
            del Employee.all[self.id]
        self.id = None

    @classmethod
    def create(cls, name, job_title, department_id):
        employee = cls(name, job_title, department_id)
        employee.save()
        return employee

    @classmethod
    def instance_from_db(cls, row):
        emp_id = row[0]
        if emp_id in cls.all:
            emp = cls.all[emp_id]
            emp.name = row[1]
            emp.job_title = row[2]
            emp.department_id = row[3]
        else:
            emp = cls(row[1], row[2], row[3], emp_id)
            cls.all[emp_id] = emp
        return emp

    @classmethod
    def get_all(cls):
        CURSOR.execute("SELECT * FROM employees")
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id):
        CURSOR.execute("SELECT * FROM employees WHERE id = ?", (id,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_name(cls, name):
        CURSOR.execute("SELECT * FROM employees WHERE name = ?", (name,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row) if row else None

    def reviews(self):
        from lib.review import Review
        CURSOR.execute("SELECT * FROM reviews WHERE employee_id = ?", (self.id,))
        rows = CURSOR.fetchall()
        return [Review.instance_from_db(row) for row in rows]

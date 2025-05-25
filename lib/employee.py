from lib import CURSOR, CONN
from lib.department import Department



class Review:
    all = {}

    def __init__(self, year, summary, employee, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee = employee

    def __repr__(self):
        return f"<Review {self.id}: {self.year}, {self.summary}, Employee ID: {self.employee.id}>"

    @classmethod
    def create_table(cls):
        CURSOR.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INTEGER,
                summary TEXT,
                employee_id INTEGER,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS reviews")
        CONN.commit()

    def save(self):
        if self.id:
            self.update()
        else:
            CURSOR.execute(
                "INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?)",
                (self.year, self.summary, self.employee.id)
            )
            CONN.commit()
            self.id = CURSOR.lastrowid
            Review.all[self.id] = self

    @classmethod
    def create(cls, year, summary, employee):
        review = cls(year, summary, employee)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        id, year, summary, employee_id = row
        if id in cls.all:
            return cls.all[id]
        from lib.employee import Employee
        employee = Employee.find_by_id(employee_id)
        review = cls(year, summary, employee, id)
        cls.all[id] = review
        return review

    @classmethod
    def find_by_id(cls, id):
        CURSOR.execute("SELECT * FROM reviews WHERE id = ?", (id,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        CURSOR.execute("""
            UPDATE reviews SET year = ?, summary = ?, employee_id = ? WHERE id = ?
        """, (self.year, self.summary, self.employee.id, self.id))
        CONN.commit()

    def delete(self):
        CURSOR.execute("DELETE FROM reviews WHERE id = ?", (self.id,))
        CONN.commit()
        if self.id in Review.all:
            del Review.all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        CURSOR.execute("SELECT * FROM reviews")
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    # === Property Validations ===

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if isinstance(value, int) and value >= 2000:
            self._year = value
        else:
            raise ValueError("Year must be an integer >= 2000")

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if isinstance(value, str) and value.strip():
            self._summary = value.strip()
        else:
            raise ValueError("Summary must be a non-empty string")

    @property
    def employee(self):
        return self._employee

    @employee.setter
    def employee(self, value):
        from lib.employee import Employee
        if isinstance(value, Employee) and value.id:
            self._employee = value
        else:
            raise ValueError("Employee must be a valid persisted Employee instance")

    @property
    def employee_id(self):
        return self.employee.id

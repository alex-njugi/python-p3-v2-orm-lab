from lib import CURSOR, CONN

class Employee:
    all = {}

    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self.name = name
        self.job_title = job_title
        self.department_id = department_id

    def __repr__(self):
        return f"<Employee {self.id}: {self.name}, {self.job_title}>"

    @classmethod
    def find_by_id(cls, id):
        CURSOR.execute("SELECT * FROM employees WHERE id = ?", (id,))
        row = CURSOR.fetchone()
        if row:
            id, name, job_title, department_id = row
            return cls(name, job_title, department_id, id)
        return None

    def reviews(self):
        from lib.review import Review
        CURSOR.execute("SELECT * FROM reviews WHERE employee_id = ?", (self.id,))
        rows = CURSOR.fetchall()
        return [Review.instance_from_db(row) for row in rows]
    
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


"""

    Dash Subclasses 
    -- 

    These are NOT stand-alone governance objects, but are stored in the data field in a serialized json form. 

"""

# this lives in the report record
#  -- there is no unique governance object
class Report:
    report = {}
    def __init__(self):
        self.report["governance_object_id"] = 0
        self.report["name"] = ""
        self.report["url"] = ""
        self.report["description"] = ""

    def load(self, record_id):
        sql = """
            select
                governance_object_id,
                name,
                url,
                description
            from report where 
                id = %s """ % record_id

        mysql.db.query(sql)
        res = mysql.db.store_result()
        row = res.fetch_row()
        if row:
            print row[0]
            (self.user["governance_object_id"], self.user["name"], self.user["url"], self.user["description"]) = row[0]
            print "loaded report successfully"

            return True

        return False

    def set_report(self, newreport):
        self.report = newreport

    def create_new(self, name, url, description):
        self.report["name"] = name
        self.report["url"] = url
        self.report["description"] = description

    def save(self):
        sql = """
            INSERT INTO report 
                (governance_object_id, name, url, description)
            VALUES
                (%(governance_object_id)s,%(name)s,%(url)s,%(description)s)
            ON DUPLICATE KEY UPDATE
                governance_object_id=%(governance_object_id)s,
                name=%(name)s,
                url=%(url)s,
                description=%(description)s
        """

        mysql.db.query(sql % self.report)



class Payday:
    payday = {}
    def __init__(self):
        pass

    def create_new(self, last_id):
        self.payday["governance_object_id"] = last_id
        self.payday["date"] = ""
        self.payday["income"] = ""
        self.payday["expenses"] = ""
        self.payday["signature_one"] = ""
        self.payday["signature_two"] = ""

    def load(self, record_id):
        sql = """
            select
                governance_object_id,
                date,
                income,
                expenses,
                signature_one,
                signature_two
            from user where 
                id = %s """ % record_id

        mysql.db.query(sql)
        res = mysql.db.store_result()
        row = res.fetch_row()
        if row:
            print row[0]
            (self.user["governance_object_id"], self.user["date"], self.user["income"], 
                self.user["expenses"], self.user["signature_one"], self.user["signature_two"]) = row[0]
            print "loaded payday successfully"

            return True

        return False

    def get_id(self):
        pass

    def save(self):
        sql = """
            INSERT INTO user 
                (governance_object_id, date, income, expenses, signature_one, signature_two)
            VALUES
                (%(governance_object_id)s,%(date)s,%(income)s,%(expenses)s,%(signature_one)s,%(signature_two)s)
            ON DUPLICATE KEY UPDATE
                governance_object_id=%(governance_object_id)s,
                date=%(date)s,
                income=%(income)s,
                expenses=%(expenses)s,
                signature_one=%(signature_one)s,
                signature_two=%(signature_two)s
        """

        mysql.db.query(sql % self.user)

    def is_valid(self):
        # todo - 12.1 - check mananger signature(s) against payday
        return True

    def set_field(self, name, value):
        self.payday[name] = value
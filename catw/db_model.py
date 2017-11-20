from . import db, lm
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm.exc import NoResultFound


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(10), index=True, unique=True)
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def register(username, password):
        user = User()
        user.username = username
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

    @staticmethod
    def update_password(user, password):
        user.password_hash = generate_password_hash(password)
        db.session.commit(user)
        return

    def __repr__(self):
        return "<User: {user}>".format(user=self.username)


class Project(db.Model):
    __tablename__ = "projects"
    project_id = db.Column(db.Integer, primary_key=True)
    wbs = db.Column(db.String(256))
    name = db.Column(db.String(256))
    start = db.Column(db.Date)
    end = db.Column(db.Date)
    entered = db.Column(db.DateTime, default=db.func.now())
    status = db.Column(db.String(256))
    billable = db.Column(db.String(256))
    info = db.Column(db.Text)
    cats = db.relationship('Timesheet', back_populates='project')

    def __repr__(self):
        return "<Project: {name}>".format(name=self.name)

    @staticmethod
    def add(**params):
        """
        This method will add a project to the project table.

        :param params:

        :return: True if project has been added, False otherwise
        """
        project_inst = Project(**params)
        db.session.add(project_inst)
        db.session.commit()
        return True

    @staticmethod
    def edit(**params):
        project_obj = db.session.query(Project).filter_by(project_id=params['project_id']).first()
        project_obj.name = params['name']
        project_obj.wbs = params['wbs']
        project_obj.status = params['status']
        project_obj.info = params['info']
        project_obj.billable = params['billable']
        db.session.commit()
        return


class Timesheet(db.Model):
    __tablename__ = "timesheet"
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id'), primary_key=True)
    datestring = db.Column(db.Date(), primary_key=True)
    timestring = db.Column(db.Integer)
    project = db.relationship('Project', back_populates='cats')

    def __repr__(self):
        return "<Time Entry: Project ID {p} - Date {d} - Worked {w}>".format(p=self.project_id,
                                                                             d=self.datestring,
                                                                             w=self.timestring)

    @staticmethod
    def add(**params):
        """
        This method will add a timesheet record to the timesheet table if it doesn't exist, or update a record if it
        exists already.

        :param params:

        :return: True if timesheet record has been merged, False otherwise
        """
        timesheet_inst = Timesheet(**params)
        db.session.add(timesheet_inst)
        db.session.commit()
        return True

    @staticmethod
    def edit(**params):
        """
        This method will edit a timesheet record to the timesheet table if it doesn't exist, or update a record if it
        exists already.

        :param params:

        :return: True if timesheet record has been merged, False otherwise
        """
        timesheet_inst = Timesheet.query.filter_by(datestring=params['datestring'],
                                                   project_id=params['project_id']).one()
        timesheet_inst.timestring = params['timestring']
        db.session.commit()
        return True

    @staticmethod
    def delete(**params):
        """
        This method will delete a timesheet record from the timesheet table.

        :param params:

        :return: True if timesheet record has been deleted, False otherwise
        """
        # timesheet_inst = Timesheet(**params)
        timesheet_inst = Timesheet.query.filter_by(**params).one()
        db.session.delete(timesheet_inst)
        db.session.commit()
        return True


class Parameter(db.Model):
    __tablename__ = 'parameters'
    parameter = db.Column(db.String(255), nullable=False, primary_key=True)
    value = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return "<{key}: {value}>".format(key=self.parameter, value=self.value)


@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def billable_all_total_time():
    """
    This method will get the total time for the all billable projects.
    :return: Total time  over all billable projects(int).
    """
    total_time_query = db.func.sum(Timesheet.timestring).label('total_time')
    total_query = db.session.query(Project, total_time_query).filter_by(billable='customer').join(Project.cats)
    total_time_value = total_query.one().total_time
    return int(total_time_value)


def billable_per_year():
    """
    This method will get the total time for the all billable projects grouped per year.
    :return: SQLAclchemy Query object, allowing to access total time over all billable projects per year ordered by
    year descending. Query object can be iterated, where each row in iteration has attributes year and billable_time.
    """
    year_time = db.func.strftime('%Y', Timesheet.datestring).label('year')
    total_time_query = db.func.sum(Timesheet.timestring).label('billable_time')
    total_query = db.session.query(Project, total_time_query, year_time).filter_by(billable='customer')\
        .join(Project.cats)
    total_per_year = total_query.group_by(year_time).order_by(year_time.desc())
    return total_per_year


def get_oldest_booking():
    """
    This function will return the date of the oldest booking.
    :return:
    """
    query = db.session.query(db.func.min(Timesheet.datestring).label('oldest')).one()
    return query.oldest


def get_param_value(parameter='hoursPerDay', to_int=True):
    """
    This method returns the value for the required parameter.

    :param parameter: Parameter key for which value is required. Default: 'hoursPerDay'.

    :param to_int: Convert the value to Integer? Default: True.

    :return: Value for the parameter, or False if no value is found for the parameter.
    """
    try:
        value = Parameter.query.filter_by(parameter=parameter).one().value
        if to_int:
            value = int(value)
    except NoResultFound:
        value = False
    return value


def holidays_all_total_time():
    """
    This method will get the total time for the holidays.
    :return: Total time  of holidays.
    """
    total_time_query = db.func.sum(Timesheet.timestring).label('total_time')
    total_query = db.session.query(Project, total_time_query).filter_by(name='Not Available').join(Project.cats)
    total_time_value = total_query.one().total_time
    return int(total_time_value)


def overview_all():
    """
    This method will get an overview of all projects and the total amount of hours worked on the project.

    :return: List of rows with tuples. Tuple content is Project object and attribute total_time.
    """
    total_time = db.func.sum(Timesheet.timestring).label('total_time')
    project_list = db.session.query(Project, total_time).join(Project.cats).group_by(Project.name)
    ordered_list = project_list.order_by(total_time.desc())
    return ordered_list.all()


def overview_all_total_time():
    """
    This method will get the total time for the overview of all projects and the total amount of hours worked on the
    project.

    :return: Total time (int).
    """
    total_time_query = db.func.sum(Timesheet.timestring).label('total_time')
    total_time_value = db.session.query(total_time_query).one().total_time
    return int(total_time_value)


def overview_year(year):
    """
    This method will get an overview of all projects and the total amount of hours worked on the project, consolidated
    per year.

    :param year: The year for which the overview is required (needs to be a string!)

    :return: List of rows with tuples. Tuple content is Project object and attribute total_time.
    """
    total_time = db.func.sum(Timesheet.timestring).label('total_time')
    year_time = db.func.strftime('%Y', Timesheet.datestring).label('year')
    project_list = db.session.query(Project, total_time).join(Project.cats)
    project_group = project_list.filter(year_time == year).group_by(Project.name)
    ordered_list = project_group.order_by(total_time.desc())
    # print("Query: {q}".format(q=str(ordered_list)))
    return ordered_list.all()


def overview_year_total_time(year):
    """
    This method will get the total time over a specific year.

    :param year: String - The year for which the total time is required

    :return: Total time (int).
    """
    total_time_query = db.func.sum(Timesheet.timestring).label('total_time')
    year_time = db.func.strftime('%Y', Timesheet.datestring)
    total_time_value = db.session.query(total_time_query).filter(year_time == year).one().total_time
    return int(total_time_value)


def project(project_id):
    """
    This method returns the Project object for this ID.

    :param project_id:

    :return: Project Object
    """
    project_query = Project.query.filter_by(project_id=project_id)
    return project_query.one()


def projects_all():
    """
    This method will return all projects, sorted on status (open, closed) and billable (customer, not).

    :return: List containing all Project objects, sorted by status, billable and name.
    """
    projects = Project.query.order_by(Project.status.desc(), Project.billable, Project.name)
    return projects.all()


def project_day(project_id):
    """
    This method will return the time worked on the project per day.

    :param project_id: Project ID for which total time is required

    :return: List of tuples containing Project object, ds representing day as datestring and ts as timestring.
    """
    total_time_query = db.func.sum(Timesheet.timestring).label('total_time')
    year_time = db.func.strftime('%Y', Timesheet.datestring).label('year')
    month_time = db.func.strftime('%M', Timesheet.datestring).label('month')
    query = db.session.query(Project, Timesheet.datestring.label('ds'), Timesheet.timestring.label('ts'))\
        .filter_by(project_id=project_id).join(Project.cats)
    sorted_query = query.order_by(Timesheet.datestring.asc())
    return sorted_query.all()


def project_month(project_id):
    """
    This method will return the time worked on the project per month.

    :param project_id: Project ID for which total time is required

    :return: List of tuples containing Project object, year as string, month number as string and total_time as string
    ordered by year, month descending.
    """
    total_time_query = db.func.sum(Timesheet.timestring).label('total_time')
    year_time = db.func.strftime('%Y', Timesheet.datestring).label('year')
    month_time = db.func.strftime('%m', Timesheet.datestring).label('month')
    query = db.session.query(Project, year_time, month_time, total_time_query)\
        .filter_by(project_id=project_id).join(Project.cats).group_by(year_time, month_time)
    sorted_query = query.order_by(Timesheet.datestring.desc())
    return sorted_query.all()


def project_total(project_id):
    """
    This method will return the total time worked on the project.

    :param project_id: Project ID for which total time is required

    :return: Total time worked on the project (integer).
    """
    total_time_query = db.func.sum(Timesheet.timestring).label('total_time')
    query = db.session.query(Project, total_time_query).filter_by(project_id=project_id).join(Project.cats)
    res = query.one()
    return int(res.total_time)


def openprojectlist():
    """
    This method will return the open projects that are relevant for this time period.

    :return: project objects for the open projects.
    """
    project_query = db.session.query(Project).filter_by(status='open').order_by(Project.name)
    return project_query.all()


def projectlist(pid_array):
    """
    This method will return the projects for which the project id is in array.

    :param pid_array: Array of project IDs

    :return: project records for the projects.
    """
    project_query = db.session.query(Project).filter(Project.project_id.in_(pid_array)).order_by(Project.name)
    return project_query.all()


def project_time(from_date, to_date):
    """
    This method will return a dictionary documenting the booked time for a project on a specific date. Dictionary key
    is Datestring and Project_id, Value is the time booked.

    :param from_date: First day of the interval as datetime

    :param to_date: Last day (inclusive) of the interval (datetime).

    :return: Dictionary, key Date and Project (YYYY.MM.DD.Project_id), value is booked time
    """
    timesheet_query = db.session.query(Timesheet).filter(Timesheet.datestring >= from_date)\
        .filter(Timesheet.datestring <= to_date)
    res = timesheet_query.all()
    project_time_dict = {}
    for rec in res:
        datestr = rec.datestring.strftime('%Y.%m.%d')
        date_project = "{dt}.{pid}".format(dt=datestr, pid=rec.project_id)
        project_time_dict[date_project] = rec.timestring
    return project_time_dict


def total_time_per_year():
    """
    This method will get the total time per year.

    :return: List of dictionaries with year as key and total time as value.
    """
    total_time_query = db.func.sum(Timesheet.timestring)
    year_time = db.func.strftime('%Y', Timesheet.datestring)
    time_year = db.session.query(total_time_query.label('total_time'), year_time.label('year')).group_by(year_time)
    time_year_dict = {}
    for rec in time_year:
        time_year_dict[rec.year] = rec.total_time
    return time_year_dict


def total_time_eh_year():
    """
    This method will get the total time per year, excluding holidays

    :return: List of dictionaries with year as key and total time (excluding holidays) as value.
    """
    total_time = db.func.sum(Timesheet.timestring).label('total_time')
    year_time = db.func.strftime('%Y', Timesheet.datestring).label('year')
    total_query = db.session.query(Project, total_time, year_time)\
        .filter(Project.name != 'Not Available').join(Project.cats)
    time_year = total_query.group_by(year_time)
    time_year_dict = {}
    for rec in time_year:
        time_year_dict[rec.year] = rec.total_time
    return time_year_dict


def update_time(dbid=None, ts=None):
    """
    This method will update the timesheet entry. If a valid integer number, then the entry for this
    date and project ID will be update if it exists, created otherwise.
    If not a valid number, then the entry for this date and project ID will be removed.
    Logging is not done for now...
    Note that for data insert, the date needs to be a (Python) datetime object, while for querying the
    date needs to be a string.

    :param dbid: Datestring (%Y-%m-%d) and Project ID concatenated with .

    :param ts: Timestring (string)

    :return: (nothing)
    """
    datestring, project_id = dbid.split(".")
    dt_obj = datetime.strptime(datestring, '%Y-%m-%d')
    params = dict(datestring=datestring,
                  project_id=project_id)
    try:
        ts = int(ts)
    except ValueError:
        # Not a valid number so ignore it...
        return
    # I have a valid timestring, get current record
    try:
        # Timesheet.query.filter_by(datestring=datestring, project_id=project_id).one()
        Timesheet.query.filter_by(**params).one()
    except NoResultFound:
        # This is a new record, add it if value integer and > 0
        if ts > 0:
            # Change datestring to datetime object
            params['datestring'] = dt_obj
            params['timestring'] = ts
            Timesheet.add(**params)
    else:
        if ts > 0:
            # Existing record, modify it
            params['timestring'] = ts
            Timesheet.edit(**params)
        else:
            # Existing record, delete it.
            Timesheet.delete(**params)
    return


def years_available():
    """
    This method will return the years available for selecting reports for a specific year.
    :return: List of years available.
    """

    year_time = db.func.strftime('%Y', Timesheet.datestring)
    year_list = db.session.query(db.distinct(year_time).label('year')).order_by(year_time.desc())
    years = [rec.year for rec in year_list]
    return years

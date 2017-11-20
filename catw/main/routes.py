# import logging
import calendar
import catw.db_model as dbm
from lib import my_env
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, login_user, logout_user, current_user
from .forms import *
from . import main
from catw.db_model import User


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.verify_password(form.password.data):
            flash('Login not successful', "error")
            return redirect(url_for('main.login', **request.args))
        login_user(user, remember=form.remember_me.data)
        return redirect(request.args.get('next') or url_for('main.index'))
    return render_template('login.html', form=form, hdr='Login')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@main.route('/pwdupdate', methods=['GET', 'POST'])
@login_required
def pwd_update():
    form = PwdUpdate()
    if form.validate_on_submit():
        user = dbm.load_user(current_user.get_id())
        if user is None or not user.verify_password(form.current_pwd.data):
            flash('Password update not successful', 'error')
            return redirect(url_for('main.pwd_update'))
        # User and password is OK, so update the password
        user.set_password(form.new_pwd.data)
        flash('Password changed!', 'info')
        return redirect(url_for('main.index'))
    return render_template('login.html', form=form, hdr='Change Password')


@main.route('/')
def index():
    # return render_template('index.html')
    return redirect(url_for('main.report_all'))


@main.route('/entertime', methods=['GET', 'POST'])
@login_required
def enter_time():
    form = SelectDate()
    if request.method == 'POST':
        weeklist = my_env.date2week(form.date.data)
        # The project list is the list of all projects.
        # This allows to modify time entries from the past.
        # For now, project list will only have Open Projects
        projectlist = dbm.openprojectlist()
        # Time per Project is the booked time per project in the specified week.
        # This is a dictionary with key YYYY.MM.DD.Project_id and value the number of hours booked for the project.
        project_time = dbm.project_time(weeklist[0], weeklist[6])
        return render_template('enter_sheet.html', weeklist=weeklist,
                               projectlist=projectlist, project_time=project_time)
    return render_template('project_add.html', form=form, title='Kies periode')


@main.route('/updatetime', methods=['GET', 'POST'])
@login_required
def update_time():
    """
    This function accepts the information to update. According to Flask documentation, use args.get to obtain the
    parameters.
    Additional information on http://flask.pocoo.org/docs/0.12/patterns/jquery/.
    :return: 'OK' - You need to return something. Flask doesn't like an empty return.
    """
    dbid = request.args.get('dbid')
    ts = request.args.get('ts')
    dbm.update_time(dbid=dbid, ts=ts)
    return 'OK'


@main.route('/project/add', methods=['GET', 'POST'])
@login_required
def project_add(project_id=None):
    form = ProjectAdd()
    if request.method == 'POST':
        if form.validate_on_submit():
            project = dict(wbs=form.wbs.data,
                           name=form.name.data,
                           status=form.status.data,
                           billable=form.billable.data,
                           info=form.information.data
                           )
            if project_id:
                title = 'Maintain Project'
                project['project_id'] = project_id
                dbm.Project.edit(**project)
                flash('Project aangepast: {p}'.format(p=project), 'info')
            else:
                title = 'Add Project'
                dbm.Project.add(**project)
                flash('{p} toegevoegd:'.format(p=project), "info")
            return redirect(url_for('main.report_project_select'))
    else:
        if project_id:
            title = 'Maintain Project'
            project = dbm.Project.query.filter_by(project_id=project_id).first()
            form.wbs.data = project.wbs
            form.name.data = project.name
            form.status.data = project.status
            form.billable.data = project.billable
            form.information.data = project.info
        else:
            title = 'Add Project'
    return render_template('project_add.html', form=form, title=title)


@main.route('/project/edit/<project_id>', methods=['GET', 'POST'])
@login_required
def project_edit(project_id):
    return project_add(project_id)


@main.route('/report/project/<project_id>/month')
def report_project_month(project_id):
    params = dict(
        month_name=calendar.month_name,
        project=dbm.project(project_id),
        project_total=dbm.project_total(project_id),
        project_month=dbm.project_month(project_id),
        hpd=dbm.get_param_value()
    )
    return render_template('report_project_month.html', **params)


@main.route('/report/project/<project_id>/day')
def report_project_day(project_id):
    params = dict(
        project=dbm.project(project_id),
        project_total=dbm.project_total(project_id),
        project_day=dbm.project_day(project_id),
        hpd=dbm.get_param_value()
    )
    return render_template('report_project_day.html', **params)


@main.route('/report/project/select')
def report_project_select():
    params = dict(
        project_list=dbm.projects_all()
    )
    return render_template('report_project_select.html', **params)


@main.route('/report/billable')
def report_billable():
    params = dict(
        oldest_booking=dbm.get_oldest_booking(),
        report_header='Overview Billable',
        total_time=dbm.overview_all_total_time(),
        total_billable=dbm.billable_all_total_time(),
        total_holidays=dbm.holidays_all_total_time(),
        hpd=dbm.get_param_value(),
        billable_per_year=dbm.billable_per_year(),
        time_per_year=dbm.total_time_per_year(),
        time_per_year_eh=dbm.total_time_eh_year()
    )
    return render_template('report_billable.html', **params)


@main.route('/report/all')
def report_all():
    params = dict(
        report_header='Overview All Projects',
        project_report=dbm.overview_all(),
        total_time=dbm.overview_all_total_time(),
        hpd=dbm.get_param_value(),
    )
    return render_template('report_projects.html', **params)


@main.route('/report/week', methods=['GET', 'POST'])
def report_week():
    form = SelectDate()
    if request.method == 'POST':
        weeklist = my_env.date2week(form.date.data)
        # The project list is the list of relevant projects for the week.
        # Time per Project is the booked time per project in the specified week.
        # This is a dictionary with key YYYY.MM.DD.Project_id and value the number of hours booked for the project.
        project_time = dbm.project_time(weeklist[0], weeklist[6])
        pids = my_env.get_pids_from_period(project_time.keys())
        projectlist = dbm.projectlist(pids)
        return render_template('report_week.html', weeklist=weeklist,
                               projectlist=projectlist, project_time=project_time)
    return render_template('project_add.html', form=form, title='Kies Periode')


@main.route('/report/years')
@main.route('/report/years/<year>')
def report_year(year=None):
    if year:
        params = dict(
            report_header='Overview All Projects {yr}'.format(yr=year),
            project_report=dbm.overview_year(year=year),
            total_time=dbm.overview_year_total_time(year=year),
            hpd=dbm.get_param_value()
        )
        return render_template('report_projects.html', **params)
    else:
        # Show list of years
        years = dbm.years_available()
        return render_template('report_year_select.html', years=years)


@main.errorhandler(404)
def not_found(e):
    return render_template("404.html", err=e)

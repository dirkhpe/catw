"""
This module consolidates all local configuration for the script, including modulename collection for logfile name
setup and initializing the config file.
Also other utilities find their home here.
"""

import datetime
import logging
import logging.handlers
import os
import platform


def get_modulename(scriptname):
    """
    Modulename is required for logfile and for properties file.
    :param scriptname: Name of the script for which modulename is required. Use __file__.
    :return: Module Filename from the calling script.
    """
    # Extract calling application name
    (filepath, filename) = os.path.split(scriptname)
    (module, fileext) = os.path.splitext(filename)
    return module


def init_loghandler(scriptname, logdir, loglevel):
    """
    This function initializes the loghandler. Logfilename consists of calling module name + computername.
    Logfile directory is read from the project .ini file.
    Format of the logmessage is specified in basicConfig function.
    This is for Log Handler configuration. If basic log file configuration is required, then use init_logfile.
    Review logger, there seems to be a conflict with the flask logger.
    :param scriptname: Name of the calling module.
    :param logdir: Directory of the logfile.
    :param loglevel: The loglevel for logging.
    :return: logging handler
    """
    modulename = get_modulename(scriptname)
    loglevel = loglevel.upper()
    # Extract Computername
    computername = platform.node()
    # Define logfileName
    logfile = logdir + "/" + modulename + "_" + computername + ".log"
    # Configure the root logger
    logger = logging.getLogger()
    level = logging.getLevelName(loglevel)
    logger.setLevel(level)
    # Create Console Handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    # Create Rotating File Handler
    # Get logfiles of 1M
    maxbytes = 1024 * 1024
    rfh = logging.handlers.RotatingFileHandler(logfile, maxBytes=maxbytes, backupCount=5)
    # Create Formatter for file
    formatter_file = logging.Formatter(fmt='%(asctime)s|%(module)s|%(funcName)s|%(lineno)d|%(levelname)s|%(message)s',
                                       datefmt='%d/%m/%Y|%H:%M:%S')
    formatter_console = logging.Formatter(fmt='%(asctime)s - %(module)s - %(funcName)s - %(lineno)d - %(levelname)s -'
                                              ' %(message)s',
                                          datefmt='%H:%M:%S')
    # Add Formatter to Console Handler
    ch.setFormatter(formatter_console)
    # Add Formatter to Rotating File Handler
    rfh.setFormatter(formatter_file)
    # Add Handler to the logger
    logger.addHandler(ch)
    logger.addHandler(rfh)
    return logger


def datestr2date(datestr):
    """
    This method will convert datestring to date type. Datestring must be of the form YYYY-MM-DD
    :param datestr: Datestring to be converted
    :return: Date in datetime object type, or False if not successful
    """
    date_obj = datetime.datetime.strptime(datestr, '%Y-%m-%d').date()
    return date_obj


def get_pids_from_period(kl):
    """
    This method will get the project IDs from a list of datestring.pid keys.

    :param kl: key list with datestring.pid values.

    :return:
    """
    logging.info("Kl: {kl}".format(kl=kl))
    pids = []
    for v in kl:
        pid = v.split(".")[3]
        if pid not in pids:
            pids.append(pid)
    logging.info("Result: {r}".format(r=pids))
    return pids


def iso_to_gregorian(iso_year, iso_week, iso_day):
    """
    Given an iso tuple, what is the date?
    http://stackoverflow.com/questions/304256/whats-the-best-way-to-find-the-inverse-of-datetime-isocalendar
    :param iso_year:
    :param iso_week:
    :param iso_day:
    :return:
    """
    jan4 = datetime.date(iso_year, 1, 4)
    start = jan4 - datetime.timedelta(days=jan4.isoweekday()-1)
    return start + datetime.timedelta(weeks=iso_week-1, days=iso_day-1)


def date2week(dt):
    """
    This method will convert a given date to the corresponding week. A list will be returned with this week's
    datetime day objects, from Monday to Sunday

    :param dt: datetime.date object with the date in a week.

    :return: List of the week's datetime day objects from Monday to Sunday.
    """
    (iso_year, iso_week, iso_day) = dt.isocalendar()
    res = [iso_to_gregorian(iso_year, iso_week, cnt) for cnt in range(1, 8)]
    return res


class LoopInfo:
    """
    This class handles a FOR loop information handling.
    """

    def __init__(self, attribname, triggercnt):
        """
        Initialization of FOR loop information handling. Start message is printed for attribname. Information progress
        message will be printed for every triggercnt iterations.
        :param attribname:
        :param triggercnt:
        :return:
        """
        self.rec_cnt = 0
        self.loop_cnt = 0
        self.attribname = attribname
        self.triggercnt = triggercnt
        curr_time = datetime.datetime.now().strftime("%H:%M:%S")
        print("{0} - Start working on {1}".format(curr_time, str(self.attribname)))
        return

    def info_loop(self):
        """
        Check number of iterations. Print message if number of iterations greater or equal than triggercnt.
        :return:
        """
        self.rec_cnt += 1
        self.loop_cnt += 1
        if self.loop_cnt >= self.triggercnt:
            curr_time = datetime.datetime.now().strftime("%H:%M:%S")
            print("{0} - {1} {2} handled".format(curr_time, str(self.rec_cnt), str(self.attribname)))
            self.loop_cnt = 0
        return

    def end_loop(self):
        curr_time = datetime.datetime.now().strftime("%H:%M:%S")
        print("{0} - {1} {2} handled - End.\n".format(curr_time, str(self.rec_cnt), str(self.attribname)))
        return

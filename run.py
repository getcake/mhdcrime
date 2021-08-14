#!/usr/bin/env python3.9
# -*- encoding: utf-8 -*-


from app import views
from app.database import server

from app.get_reports import download_reports

import app.main as main 


from threading import Thread
from termcolor import cprint
import functools


from flask import Flask


from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from datetime import datetime
from time import sleep
from timeit import timeit



if __name__ == '__main__':

     #NOTE Uncomment to run with scheduler and update database 

     # def execution_listener(event):

     #      try:
     #           if event.exception:
     #                print('The job crashed')
     
     #           else:
     #                print('The job executed successfully')

     #                job = scheduler.get_job(event.job_id)

     #                if job.name == 'first_job':
     #                     print('Running the second job')
     #                     jobs = scheduler.get_jobs()
     #                     second_job = next((j for j in jobs if j.name == 'second_job'), None)
     #                     if second_job:

     #                          print("WAITING...")
     #                          sleep(3)
     #                          second_job.modify(next_run_time=datetime.now())
     #                          cprint('MODIFED SECOND JOB', 'red')


     #                     else:
     #                          scheduler.add_job(timeit(main.make_report), name='second_job', id='second') #NOTE make_report() kind of works 
     #                          # scheduler.shutdown(wait=True)
     #                          cprint('ELSE', 'red')
     #                          # scheduler.remove_job('second')
     #                          # scheduler.shutdown()
     #                          cprint('REMOVED JOB')

          
     #      except AttributeError:pass

     # scheduler = BackgroundScheduler()
     # scheduler.add_listener(execution_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
     # scheduler.add_job(download_reports, 'interval', hours=24, next_run_time=datetime.now(), name="first_job") 

     # scheduler.add_job(main.make_report, 'interval', hours=24, name="second_job")
     # scheduler.start()

     server.run(host="0.0.0.0", debug=True)

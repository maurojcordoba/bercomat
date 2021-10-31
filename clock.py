from apscheduler.schedulers.blocking import BlockingScheduler

import bercomat

sched = BlockingScheduler()


@sched.scheduled_job('interval', seconds=20)
def timed_job():
    print('Test 20')
    #sched.shutdown(wait=False)

def bercomat_job():
    print('Inicia bercomat')
    bercomat.process()
    print('Finaliza bercomat')

sched.add_job(bercomat_job, trigger='cron', hour=15, minute=55)

print(sched.print_jobs())

sched.start()
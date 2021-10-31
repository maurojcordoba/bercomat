from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

@sched.scheduled_job('interval', seconds = 5)
def timed_job():
    print('Test 5.')

@sched.scheduled_job('interval', seconds=20)
def timed2_job():
    print('Test 20 shutdown.')
    #sched.shutdown(wait=False)

def timed3_job():
    print('Test')

sched.add_job(timed3_job, trigger='cron', hour=15, minute=40)

print(sched.print_jobs())

sched.start()
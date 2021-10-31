from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

@sched.scheduled_job('interval', seconds = 5)
def timed_job():
    print('Test 5.')

@sched.scheduled_job('interval', seconds=20)
def timed2_job():
    print('Test 20 shutdown.')
    sched.shutdown(wait=False)

sched.start()
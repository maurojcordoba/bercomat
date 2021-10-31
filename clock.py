from apscheduler.schedulers.blocking import BlockingScheduler

import bercomat, ofertas

sched = BlockingScheduler()


@sched.scheduled_job('interval', seconds=20)
def timed_job():
    print('Test 20')
    #sched.shutdown(wait=False)

def bercomat_job():
    print('Inicia bercomat')
    bercomat.procesar()
    print('Finaliza bercomat')

def ofertas_job():
    print('Inicia ofertas')
    ofertas.procesar()
    print('Finaliza ofertas')

sched.add_job(bercomat_job, trigger='cron', hour=15, minute=57)
sched.add_job(ofertas_job, trigger='cron', hour=16, minute=55)

print(sched.print_jobs())

sched.start()
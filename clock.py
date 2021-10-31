from apscheduler.schedulers.blocking import BlockingScheduler

import bercomat, ofertas

sched = BlockingScheduler()

def bercomat_job():
    print('Inicia bercomat')
    bercomat.procesar()
    print('Finaliza bercomat')

def ofertas_job():
    print('Inicia ofertas')
    ofertas.procesar()
    print('Finaliza ofertas')

sched.add_job(bercomat_job, trigger='cron', hour=12)
sched.add_job(ofertas_job, trigger='cron', hour=12, minute=45)

print(sched.print_jobs())

sched.start()
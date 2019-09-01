import os

from apscheduler.schedulers.blocking import BlockingScheduler

def start_crawling():
    cmd = "scrapy crawl selfie_photo"
    print("Executing command '%s'" % cmd)
    os.system(cmd)
    cmd = "scrapy crawl asia_bt"
    print("Executing command '%s'" % cmd)
    os.system(cmd)


def create_apscheduler_jobs():
    sched = BlockingScheduler()

    # 每整分钟执行
    sched.add_job(start_crawling, "cron", hour="*", minute="20")
    sched.start()


if __name__ == "__main__":
    create_apscheduler_jobs()
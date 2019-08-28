import os

from apscheduler.schedulers.blocking import BlockingScheduler

def start_crawling():
    os.system("scrapy crawl selfie_photo")
    os.system("scrapy crawl asia_bt")


def create_apscheduler_jobs():
    sched = BlockingScheduler()

    # 每整分钟执行
    sched.add_job(start_crawling, "cron", hour="*")
    sched.start()


if __name__ == "__main__":
    create_apscheduler_jobs()
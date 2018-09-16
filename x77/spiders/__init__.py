# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
def need_refresh(text):
    if text.endswith("F5"):
        print("NEED REFRESH!!!")
        return True
    return False

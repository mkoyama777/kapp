from icrawler.builtin import BingImageCrawler

text="アジア人男性画像"
num = 1000
crawler = BingImageCrawler(storage = {'root_dir' : './image'})
crawler.crawl(keyword = text, max_num = num)
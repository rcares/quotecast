import io
import json
import random
import logging
from scrapy.crawler import CrawlerProcess
from rich.console import Console
from rich.logging import RichHandler
# spiders
from quoted.scrapy.spiders import toscrape, brainyquote, goodreads

# Logging
logger = logging.getLogger(__name__)

# Buffer
bytestream = io.BytesIO()


def init_logging(log_level=logging.CRITICAL):
    FORMAT = "%(message)s"
    logging.basicConfig(
        level=log_level,
        format=FORMAT, datefmt="[%X] ",
        handlers=[RichHandler(level=log_level)]
    )

    return logging.getLogger(__name__)


def get_spider():
    spiders = [
        toscrape.QuotesSpider,
        brainyquote.QuotesSpider,
        goodreads.QuotesSpider
    ]
    spider_selector = random.randint(1, len(spiders)-1)

    return spiders[spider_selector]


def do_crawl(spider):
    """
    Crawl web sites to get quotes using scrapy spiders.
    module: quoted.quoted.spiders
    """
    process = CrawlerProcess(settings={
        "LOG_ENABLED": False,
        "TELNETCONSOLE_ENABLED": False,
        "FEED_STORAGES": {
            'buffered': 'quoted.scrapy.extensions.storage.BufferedFeedStorage',
        },
        "FEED_STORAGE_BUFFERED": {
            "bytestream": {
                "module": "quoted.quoted",
                "buffer": "bytestream"
            },
        },
        "FEEDS": {
            "buffered:bytestream": {"format": "json"},
        },
    })

    process.crawl(spider)

    # the script will block here until the crawling is finished
    process.start()


def get_quote_from_json_stream(stream):
    stream_value = stream.getvalue()
    logger.debug(stream_value)
    quotes = json.loads(stream_value)
    logger.debug(quotes)
    quote_selector = random.randint(1, len(quotes)-1)

    return quotes[quote_selector]


def main():
    print_styles = {
        "text": "italic",
        "author": "bold"
    }

    logger = init_logging(logging.CRITICAL)
    console = Console()

    spider = get_spider()
    do_crawl(spider)

    try:
        quote = get_quote_from_json_stream(bytestream)

        console.print("")
        console.print("“%s”" % quote["text"], style=print_styles["text"])
        console.print("―― %s" % quote["author"], style=print_styles["author"])
        console.print("")
        console.print("tags: %s" % ', '.join(quote["tags"]))
        console.print("link: %s" % quote["url"])
        console.print("")
        console.print("© %s" % spider.name)
        console.print("")
        console.print("Powered by quoted")

    except json.JSONDecodeError:
        logger.error("JSONDecodeError: Failed parsing json response!")
    except TypeError:
        logger.error("TypeError: Failed parsing json response!")


if __name__ == "__main__":
    main()

# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

from pathlib import Path
import scrapy

class ConferenceSpider(scrapy.Spider):
    
    name = "conferences"
    
    start_urls = [
        "https://en.wikipedia.org/wiki/List_of_computer_science_conferences"
    ]
    
    def parse(self, response):
            # print("Response:")
            # print("==========")
            # print(response)
            
            # page = response.url.split("/")[-2]
            # filename = f"conferences-{page}.html"
            # Path(filename).write_bytes(response.body)
            # self.logger.info(f"Saved file {filename}")
            # print()
            
            # self.logger.info("Parsing conference list")
            
            # for row in response.css("table.wikitable tr"):
            #     cols = row.css("td, th")
            #     if not cols:
            #         continue
                
            #     name = cols[0].css("a::text").get()
            #     if not name:
            #         name = cols[0].css("::text").get()
                
            #     if not name:
            #         continue
                
            #     link = cols[0].css("a::attr(href)").get()

                
            #     yield{
            #             "name": name.strip(),
            #             "website": response.urljoin(link) if link else None,
            #             "source_url": response.url
            #     
            
            for table in response.css("table.wikitable"):
                for row in table.css("tr"):
                    cells = row.css("td, th")
                    if not cells:
                        continue
                    
                    name = cells[0].xpath("string()").get()
                    if not name:
                        continue
                    
                    name = name.strip()
                    
                    # if len(name) < 4 or "Conference" not in name and name.isupper():
                    #     continue
                    
                    link = cells[0].css("a::attr(href)").get()
                    
                    yield{
                        "name" : name,
                        "website": response.urljoin(link) if link else None,
                        "source_url": response.url
                    }
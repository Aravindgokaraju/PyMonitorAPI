# from django_rq import job
# import os
# import django
# from django.conf import settings

# @job('scraping', timeout=7200)  # 2 hour timeout
# def scrape_website_task(flow_data, skus_data):
#     """
#     Background task that runs on the paid worker
#     This is where your actual scraping happens
#     """
#     # CRITICAL: Setup Django environment in the worker
#     if not settings.configured:
#         os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PyMonitor.settings')
#         django.setup()
    
#     # Now import after Django is setup - use the correct path
#     from execution.scraping.scrape_website import ScrapingService
#     import time
    
#     print(f"Starting scraping task for {len(skus_data)} SKUs")
#     start_time = time.time()
    
#     try:
#         scraper = ScrapingService()
#         results = scraper.scrape_websites({
#             'flows': [flow_data],
#             'skus': skus_data
#         })
        
#         duration = time.time() - start_time
#         print(f"Scraping completed in {duration:.2f} seconds")
#         return results
        
#     except Exception as e:
#         print(f"Scraping failed: {str(e)}")
#         raise

# # from django_rq import job
# # import os
# # import django
# # from django.conf import settings

# # @job('chromedriver', timeout=10800)  # 3 hours timeout
# # def scrape_website_task(flow_data, skus_data):
# #     """
# #     Background task that runs on the ChromeDriver worker
# #     """
# #     # Setup Django environment (critical for worker)
# #     if not settings.configured:
# #         os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PyMonitor.settings')
# #         django.setup()
    
# #     from execution.scrape_website import ScrapingService  # Adjust to your actual import
# #     import time
    
# #     print(f"Starting ChromeDriver scraping task for {len(skus_data)} SKUs")
# #     start_time = time.time()
    
# #     try:
# #         scraper = ScrapingService()
# #         results = scraper.scrape_websites({
# #             'flows': [flow_data],
# #             'skus': skus_data
# #         })
        
# #         duration = time.time() - start_time
# #         print(f"ChromeDriver scraping completed in {duration:.2f} seconds")
# #         return results
        
# #     except Exception as e:
# #         print(f"ChromeDriver scraping failed: {str(e)}")
# #         raise
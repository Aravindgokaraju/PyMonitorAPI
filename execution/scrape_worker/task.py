


# # execution/tasks.py
# import traceback
# from django_rq import job
# import os
# import django
# from django.conf import settings
# import time

# @job('worker', timeout=720)  # 2 hour timeout
# def scrape_worker(data):
#     """s
#     Background task that runs on the paid worker
#     This is where your actual scraping happens
#     """
#     # CRITICAL: Setup Django environment in the worker
#     print("SCRAPE WORKER WORKERING")
#     if not settings.configured:
#         os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PyMonitor.settings.worker')
#         django.setup()
    
#     # Import after Django setup
#     from .standalone_scraper import StandaloneScrapingService
    
#     # print(f"Starting scraping task for {len(skus_data)} SKUs")
#     start_time = time.time()
    
#     try:
#         # Create standalone scraper (no database dependencies)
#         scraper = StandaloneScrapingService(stealth_level='stable')
        
#         # Process the request
#         results = scraper.scrape_websites(data)
        
#         duration = time.time() - start_time
#         print(f"Scraping completed in {duration:.2f} seconds")
#         print("RESULTS:",results)
#         # Return pure data - let the main app handle database operations
#         return {
#             'success': True,
#             'data': results,
#             'metadata': {
#                 'processing_time': duration,
#                 'items_processed': len(results),
#                 'website': "wbebite"
#             }
#         }
        
#     except Exception as e:
#         duration = time.time() - start_time
#         print(f"Scraping failed after {duration:.2f} seconds: {str(e)}")
#         traceback.print_exc()
        
#         return {
#             'success': False,
#             'data': None,
#             'error': str(e),
#             'metadata': {
#                 'processing_time': duration,
#                 'items_processed': 0,
#                 'website': "test site"
#             }
#         }
from django.http import JsonResponse
from django_rq import enqueue, get_queue
from rest_framework.decorators import api_view
import logging

from execution.scrape_worker.tasks import scrape_worker


logger = logging.getLogger(__name__)

# @api_view(['POST'])
# def execute_scraping(request):
#     try:
#         scraper = ScrapingService()
#         logger.info("Starting scraping process...")
#         results = scraper.scrape_websites(request.data)
#         logger.info(f"Scraping completed with {len(results)} results")
        
#         return Response({
#             'status': 'success',
#             'data': results
#         }, status=status.HTTP_200_OK)
        
#     except Exception as e:
#         logger.error(f"Scraping failed: {str(e)}", exc_info=True)
#         return Response({
#             'status': 'error',
#             'message': str(e)
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(['POST'])
# def start_worker(request):
#     """This runs on the FREE web worker, queues job for PAID worker"""
#     if request.method == 'POST':
#         data = request.POST
#         flow_list = data.get('website_config_id', [])
#         sku_list = data.get('sku_list', [])
#         print("STARTING WORKER")
#         try:
#             job = enqueue(
#                 scrape_worker, 
#                 flow_list, 
#                 sku_list,
#                 queue='worker',
#                 timeout=600
#             )
            
#             print(f"Job queued successfully: {job.id}")
            
#             return JsonResponse({
#                 'job_id': job.id,
#                 'status': 'queued',
#                 'message': 'Scraping job queued for processing'
#             })
            
#         except Exception as e:
#             print(f"Failed to queue job: {str(e)}")
#             return JsonResponse({
#                 'error': f'Failed to queue job: {str(e)}'
#             }, status=500)

from django_rq import get_queue

@api_view(['POST'])
def start_worker(request):
    data = request.data
    print("DATA:",data)
    flow_list = data.get('flows', [])
    sku_list = data.get('skus', [])
    
    # Explicitly get the worker queue
    queue = get_queue('worker')
    
    job = queue.enqueue(
        scrape_worker, 
        data,
    )
    
    print(f"Job queued successfully: {job.id}")
    return JsonResponse({'job_id': job.id, 'status': 'queued'})

@api_view(['GET'])
def queue_status(request):
    """Check queue status"""
    queue = get_queue('worker')
    jobs = queue.get_jobs()
    
    return JsonResponse({
        'queue_length': len(jobs),
        'job_ids': [job.id for job in jobs]
    })

# In your views.py
from django.http import JsonResponse
from django_rq import get_queue
from rq.job import Job
from rq.exceptions import NoSuchJobError

@api_view(['GET'])
def get_job_result(request, job_id):
    """
    Check the status of a job and return results if completed
    """
    queue = get_queue('worker')
    
    try:
        # Fetch the job from Redis
        job = Job.fetch(job_id, connection=queue.connection)
        
        if job.is_finished:
            # Job completed successfully, return the result
            return JsonResponse({
                'status': 'completed',
                'result': job.result,  # This is what your scrape_worker returned
                'job_id': job_id
            })
            
        elif job.is_failed:
            # Job failed
            return JsonResponse({
                'status': 'failed',
                'error': str(job.exc_info),  # Exception information
                'job_id': job_id
            }, status=500)
            
        else:
            # Job is still queued or in progress
            status = 'queued' if job.is_queued else 'started'
            return JsonResponse({
                'status': status,
                'job_id': job_id
            })
            
    except NoSuchJobError:
        return JsonResponse({
            'error': f'Job with ID {job_id} not found'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error fetching job: {str(e)}'
        }, status=500)
from django.http import JsonResponse
from django_rq import enqueue, get_queue
from rest_framework.decorators import api_view
import logging

# from execution.scrape_worker.task import scrape_worker


from rq.job import Job
from rq.exceptions import NoSuchJobError

logger = logging.getLogger(__name__)

@api_view(['POST'])
def start_worker(request):
    data = request.data
    flow_list = data.get('flows', [])
    sku_list = data.get('skus', [])
    
    # Explicitly get the worker queue
    queue = get_queue('worker')
    print("scrape string passing @@@@@@@@@@@@@@@@@@")
    job = queue.enqueue(
        'scraping.scraping_worker.tasks.scrape_worker', 
        data,
    )
    
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
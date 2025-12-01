# from execution.scrape_worker.scraping_models import Criteria
# class CommandStack:
#     def __init__(self):
#         self.stack:Criteria = []

#     def is_empty(self):
#         return len(self.stack) == 0

#     def push(self, item):
#         self.stack.append(item)

#     def pop(self):
#         if self.is_empty():
#             raise IndexError("Pop from an empty stack")
#         return self.stack.pop()

#     def peek(self):
#         if self.is_empty():
#             raise IndexError("Peek from an empty stack")
#         return self.stack[-1]

#     def size(self):
#         return len(self.stack)
    
#     def clear(self):
#         self.stack:Criteria = []

#     def __str__(self):
#         return str(self.stack)
#     def get_stack_info(self):
#         return [{
#             'xpath': c.xpath,
#             'action_progress': f"{c.actionCount}/{len(c.actions)}",
#             'child_count': c.childCount
#         } for c in self.stack]
from rest_framework.pagination import PageNumberPagination



def paginate_data(paginator, serializer):
    paginated_response = paginator.get_paginated_response(serializer.data)
    paginated_data = paginated_response.data

    return {
        'payload': paginated_data['results'],
        'pagination': {
            'next': paginated_data['next'],
            'previous': paginated_data['previous'],
            'page_size': paginator.page_size,
            'count': paginated_data['count']
        }
    }
class CategoryPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
    invalid_page_message = "The requested page does not exist."

class ContentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
    invalid_page_message = "The requested page does not exist."

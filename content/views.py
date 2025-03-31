from rest_framework.decorators import api_view
from core.utils import *
from .serializers import *
from django.core.cache import cache
from .paginator import *
from .utils import *



@api_view(['GET', 'POST', 'DELETE'])
def categories(request):
    try:
        user = request.user
        data = request.data
        if request.method == 'GET':
            categories = Category.objects.all().select_related('user')

            paginator = CategoryPagination()
            paginated_categories = paginator.paginate_queryset(categories, request)
            serializer = CategorySerializer(paginated_categories, many=True)
            paginated_data = paginate_data(paginator, serializer)
            return success(data=paginated_data)
        elif request.method == 'POST':
            if not request.user.is_staff:
                return error(message="Only Admins can create a category")
            
            name = data.get('name')
            description = data.get('description')

            required_fields = ['name']
            check_required_fields(data, required_fields)

            if Category.objects.filter(name=name).exists():
                return error(message="Category name aleady exists please choose a different category name")
            
            category = Category.objects.create(
                user=user,
                name=name,
                description=description
            )
            
            serializer = CategorySerializer(category)
            return success(message=f"{name} - Category created successfuly", data=serializer.data)
        elif request.method == 'DELETE':
            if not request.user.is_staff:
                return error(message="Only Admins can delete categories")
            
            category_ids = data.get('category_ids')
            required_fields = ["category_ids"]

            check_required_fields(data, required_fields)
            
            if not isinstance(category_ids, list):
                return error(message="Category IDs should be a list")

            category_ids = [int(id) for id in category_ids]

            categories = Category.objects.filter(id__in=category_ids)

            valid_category_ids = categories.values_list('id', flat=True)
            invalid_category_ids = [id for id in category_ids if id not in valid_category_ids]
            
            if invalid_category_ids:
                return error(message=f"One or more category IDs are invalid: {invalid_category_ids}")
            
            deleted_count = categories.count()

            deleted_categories, _ = categories.delete()
            if deleted_count == 1:
                message = f'Category deleted successfully'
            else:
                message = f'{deleted_count} categories deleted successfully'
            return success(message=message)
    except ValidationError as e:
        return error(message=f"{e.messages[0]}")
    except Exception as e:
        return error(message=str(e))

@api_view(['GET', 'PATCH', 'DELETE'])
def category(request, id):
    try:
        user = request.user
        data = request.data
        category = get_object_or_404_json(Category, id=id)
        if request.method == 'GET':
            serializer = CategorySerializer(category)
            return success(serializer.data)
        elif request.method == 'PATCH':
            if not request.user.is_staff:
                return error(message="Only Admins can update a category")
            
            name = data.get('name')
            description = data.get('description')

            required_fields = ['name']
            check_required_fields(data, required_fields)
            
            category.name=name
            category.description=description

            category.save()
            
            serializer = CategorySerializer(category)
            return success(message=f"{name} - Category updated successfuly", data=serializer.data)
        elif request.method == 'DELETE':
            if not request.user.is_staff:
                return error(message="Only Admins can delete a category")
            
            category.delete()
            return success(message=f"{category.name} - Category Deleted Successfully")
    except ValidationError as e:
        return error(message=f"{e.messages[0]}")
    except Exception as e:
        return error(message=str(e))

@api_view(['GET', 'POST', 'DELETE'])
def contents(request):
    try:
        user = request.user
        data = request.data
        query_params = request.query_params
        if request.method == 'GET':
            user_contents = parse_bool(query_params.get('user_contents'), 'user_contents')

            if user_contents:
                contents = Content.objects.filter(user=user)
            else:
                contents = Content.objects.all()

            paginator = ContentPagination()
            paginated_contents = paginator.paginate_queryset(contents, request)
            serializer = ContentSerializer(paginated_contents, many=True)
            paginated_data = paginate_data(paginator, serializer)
            return success(data=paginated_data)
        elif request.method == 'POST':
            title = data.get('title')
            description = data.get('description')
            category_id = data.get('category_id')
            tags = data.get('tags', [])

            required_fields = ['title', 'category_id']
            check_required_fields(data, required_fields)
            
            category = get_object_or_404_json(Category, id=category_id)
            
            if not isinstance(tags, list):
                return error(message="Tags must be provided as a list.")
            
            content = Content.objects.create(
                user=user,
                title=title,
                description=description,
                category=category
            )
            
            if tags:
                content.tags.set(tags)
            
            serializer = ContentSerializer(content)
            return success(message=f"{title} - Content created successfuly", data=serializer.data)
        elif request.method == 'DELETE':
            content_ids = data.get('content_ids')
            required_fields = ["content_ids"]

            check_required_fields(data, required_fields)
            
            if not isinstance(content_ids, list):
                return error(message="Content IDs should be a list")

            content_ids = [int(id) for id in content_ids]

            contents = Content.objects.filter(id__in=content_ids, user=user)

            valid_content_ids = contents.values_list('id', flat=True)
            invalid_content_ids = [id for id in content_ids if id not in valid_content_ids]
            
            if invalid_content_ids:
                return error(message=f"One or more content IDs are invalid: {invalid_content_ids}")
            
            deleted_count = contents.count()

            deleted_contents, _ = contents.delete()
            if deleted_count == 1:
                message = f'Content deleted successfully'
            else:
                message = f'{deleted_count} contents deleted successfully'
            return success(message=message)
    except ValidationError as e:
        return error(message=f"{e.messages[0]}")
    except Exception as e:
        return error(message=str(e))

@api_view(['GET', 'PATCH', 'DELETE'])
def content(request, id):
    try:
        user = request.user
        data = request.data
        
        if request.method == 'GET':
            content = get_object_or_404_json(Content, id=id)
            serializer = ContentSerializer(content)
            return success(serializer.data)
        elif request.method == 'PATCH':
            title = data.get('title')
            description = data.get('description')
            category_id = data.get('category_id')
            tags = data.get('tags', [])

            required_fields = ['title', 'category_id']
            check_required_fields(data, required_fields)
            
            content = get_object_or_404_json(Content, id=id, user=user)

            category = get_object_or_404_json(Category, id=category_id)
            
            if not isinstance(tags, list):
                return error(message="Tags must be provided as a list.")
            
            content.title=title
            content.description=description
            content.category=category

            content.save()
            
            if tags:
                content.tags.set(tags)
            
            serializer = ContentSerializer(content)
            return success(serializer.data)
        elif request.method == 'DELETE':
            content = get_object_or_404_json(Content, id=id, user=user)

            content.delete()
            return success(message="Content Deleted Successfully")
    except ValidationError as e:
        return error(message=f"{e.messages[0]}")
    except Exception as e:
        return error(message=str(e))

@api_view(['GET'])
def content_recommendations(request):
    user = request.user

    cache_key = f"user_{user.id}_content_recommendations"
    
    if cached_data := cache.get(cache_key):
        return success(data=cached_data, message="Cached recommendations retrieved")
    
    data = calculate_content_recommendations(user)
    
    return success(data=data, message="Recommendations computed and cached")
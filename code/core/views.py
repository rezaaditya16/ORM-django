from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from core.models import Course, CourseContent, CourseMember, User
from django.db.models import Max, Min, Avg, Count
from django.core import serializers

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the core index.")

def testing(request):
    guru = User.objects.create_user(
        username="guru_satu",
        email="guru_1@gmail.com",
        password="rahasia",
        first_name="guru",
        last_name="satu"
    )

    Course.objects.create(
        name="Pemrograman python",
        description="Belajar pemrograman python",
        price=50000,
        teacher=guru
    )
    return HttpResponse("kosongan")

def allCourse(request):
    courses = Course.objects.all().select_related('teacher')
    data_resp = []
    for course in courses:
        record = {
            'id': course.id,
            'name': course.name,
            'price': course.price,
            'teacher':{
                'id': course.teacher.id,
                'username': course.teacher.username,
                'fulname': f"{course.teacher.first_name} {course.teacher.last_name}"
            }
        }
        data_resp.append(record)
    return JsonResponse(data_resp, safe=False)

def userprofile(request, user_id):
    user = User.objects.get(pk=user_id)
    courses = Course.objects.filter(teacher=user)
    data_resp = {
       'username': user.username,
       'email': user.email,
       'fullname': f"{user.first_name} {user.last_name}"
    }
    data_resp ['courses'] = []
    for course in courses:
        record = {
            'id': course.id,
            'name': course.name,
            'description': course.description,
            'price': course.price
        }
        data_resp['courses'].append(record)
    return JsonResponse(data_resp, safe=False)

def courseStat(request):
  courses = Course.objects.all()
  stats = courses.aggregate(max_price=Max('price'),
                              min_price=Min('price'),
                              avg_price=Avg('price'))
  cheapest = Course.objects.filter(price=stats['min_price'])
  expensive = Course.objects.filter(price=stats['max_price'])
  popular = Course.objects.annotate(member_count=Count('coursemember'))\
                          .order_by('-member_count')[:5]
  unpopular = Course.objects.annotate(member_count=Count('coursemember'))\
                          .order_by('member_count')[:5]

  result = {'course_count': len(courses), 'courses': stats,
            'cheapest': serializers.serialize('python', cheapest), 
            'expensive': serializers.serialize('python', expensive),
            'popular': serializers.serialize('python', popular), 
            'unpopular': serializers.serialize('python', unpopular)}
  return JsonResponse(result, safe=False)

def courseDetail(request, course_id):
    course = Course.objects.annotate(member_count=Count('coursemember'), 
                                     content_count=Count('coursecontent'),
                                     comment_count=Count('coursecontent__comment'))\
                           .get(pk=course_id)
    contents = CourseContent.objects.filter(course_id=course.id)\
                                    .annotate(count_comment=Count('comment'))\
                                    .order_by('-count_comment')[:3]
    result = {
        "name": course.name,
        'description': course.description,
        'price': course.price,
        'member_count': course.member_count,
        'content_count': course.content_count,
        'teacher': {
            'username': course.teacher.username,
            'email': course.teacher.email,
            'fullname': f"{course.teacher.first_name} {course.teacher.last_name}"
        },
        'comment_stat': {
            'comment_count': course.comment_count,
            'most_comment': [
                {'name': content.name, 'comment_count': content.count_comment} 
                for content in contents
            ]
        }
    }

    return JsonResponse(result)
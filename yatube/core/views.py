from django.shortcuts import render


def page_not_found(request, exception):
    context = {'path': request.path
               }
    return render(request, 'core/404.html', context, status=404)


def permission_denied(request, exception):
    return render(request, 'core/403.html', status=403)


def csrf_failure(request, reason=''):
    return render(request, 'core/403csrf.html')


def server_error(request):
    return render(request, 'core/500.html', status=500)

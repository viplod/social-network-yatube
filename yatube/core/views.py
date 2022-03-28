from django.shortcuts import render


def page_not_found(reguest, exception):
    template = 'core/404.html'
    context = {
        'path': reguest.path,
    }
    return render(reguest, template, context, status=404)


def csrf_failure(request, reason=''):
    template = 'core/403csrf.html'
    return render(request, template)


def server_error(request):
    template = 'core/500.html'
    return render(request, template, status=500)


def permission_denied(request, exception):
    template = 'core/403.html'
    return render(request, template, status=403)

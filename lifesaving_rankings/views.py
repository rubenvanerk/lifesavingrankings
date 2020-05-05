from django.shortcuts import render, redirect


def error_404_view(request, exception):
    data = {"message": "Error 404: Page not found"}
    return render(request, 'lifesaving_rankings/error.html', data)


def error_500_view(request):
    data = {"message": "Error 500: Server error"}
    return render(request, 'lifesaving_rankings/error.html', data)


def ultimate_lifesaver(request):
    return render(request, 'lifesaving_rankings/ultimate-lifesaver.html')


def changelog(request):
    return render(request, 'lifesaving_rankings/changelog.html')


def about(request):
    return render(request, 'lifesaving_rankings/about.html')


def rankings_redirect(request, path):
    return redirect(path)

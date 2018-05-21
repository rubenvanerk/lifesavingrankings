from django.shortcuts import render


def error_404_view(request, exception):
    data = {"message": "Error 404: Page not found"}
    return render(request, 'lifesaving_rankings/error.html', data)


def error_500_view(request, exception):
    data = {"message": "Error 404: Page not found"}
    return render(request, 'lifesaving_rankings/error.html', data)

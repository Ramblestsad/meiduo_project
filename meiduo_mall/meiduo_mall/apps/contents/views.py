from django.shortcuts import render
from django.views import View

# Create your views here.


class IndexView(View):
    """index advertisements"""

    def get(self, request):
        """index.html"""

        return render(request, 'index.html')

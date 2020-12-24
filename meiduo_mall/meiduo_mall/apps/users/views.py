from django.shortcuts import render
from django.views import View

# Create your views here.


class RegisterView(View):

    '''
    description: users regiter
    param {*}
    return {*}
    '''

    def get(self, request):

        """display register.html"""

        return render(request, 'register.html')

    def post(self, request):

        """register"""

        pass

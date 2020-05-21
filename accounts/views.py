from django.shortcuts import render, HttpResponse, redirect
from django.views.generic import (TemplateView, FormView)
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
import json
from django.shortcuts import get_object_or_404
from .forms import RegisterForm, LoginForm, PhoneVerificationForm
from .authy_api import send_verfication_code, verify_sent_code
from .models import User


class IndexView(TemplateView):

    template_name = 'accounts/index.html'


class RegisterView(SuccessMessageMixin, FormView):
    template_name = 'accounts/register.html'
    form_class = RegisterForm
    success_message = "One-Time password sent to your registered mobile number.\
                        The verification code is valid for 10 minutes."

    def form_valid(self, form):
        # user = form.save()
        user=self.request.POST
        # print(user)
        # username = self.request.POST['username']
        # password = self.request.POST['password1']
        # user = authenticate(username=username, password=password)
        # print(user.message)
        try:
            response = send_verfication_code(user)
        except Exception as e:
            messages.add_message(self.request, messages.ERROR,
                                'verification code not sent. \n'
                                'Please re-register.')
            return redirect('/register')
        data = json.loads(response.text)

        print(response.status_code, response.reason)
        print(response.text)
        print(data['success'])
        if data['success'] == False:
            messages.add_message(self.request, messages.ERROR,
                            data['message'])
            return redirect('/register')

        else:
            kwargs = {'user': user}
            print("this is kwargs under register view")
            print(kwargs)
            self.request.method = 'GET'
            return PhoneVerificationView(self.request,**kwargs)







def view1(request):
    print("under view1 login get request")
    return render(request,'accounts/login.html')

def resend_url(request,phone_number,country_code):

    user={"phone_number":phone_number,"country_code":country_code}
    try:
        response = send_verfication_code(user)
        pass
    except Exception as e:

        print("Exception while sending verification code")
        messages.add_message(request, messages.ERROR,
                'verification code not sent. \n'
                )
        return redirect('/login')
    data = json.loads(response.text)

    if data['success'] == False:




        messages.add_message(request, messages.ERROR,
        data['message'])
        return redirect('/login')

    print(response.status_code, response.reason)
    print(response.text)
    if data['success'] == True:

        request.method = "GET"
        print(request.method)
        kwargs = {'user':user}
        dict={'user':user}
        return PhoneVerificationView(request,**kwargs)


def LoginView(request):
    print("under view1 login get request")
    template_name='accounts/login.html'
    print("Inside login 1")
    if request.method == "POST":
        print("Inside login post method")
        # username = request.POST['username']
        user=request.POST
        userob = User.objects.filter(phone_number=user['phone_number'])
        if userob:
            try:
                response = send_verfication_code(user)
                pass
            except Exception as e:
                print("Exception while sending verification code")
                messages.add_message(request, messages.ERROR,
                        'verification code not sent. \n'
                        'Please retry logging in.')
                return redirect('/login')
            data = json.loads(response.text)

            if data['success'] == False:
                    print("If verifiacation code is not sent by twilio")
                    messages.add_message(request, messages.ERROR,
                    data['message'])
                    return redirect('/login')

            print(response.status_code, response.reason)
            print(response.text)
            if data['success'] == True:
                print("if verification code is sent by twilio")
                request.method = "GET"
                print(request.method)
                kwargs = {'user':user}
                dict={'user':user}
                return PhoneVerificationView(request,**kwargs)
            else:
                messages.add_message(request, messages.ERROR,
                data['message'])
                return redirect('/login')
        else:
            messages.add_message(request, messages.ERROR,
                    'User does not exist. \n'
                    'Please register.')
            return redirect('/register')

    else:
        return HttpResponse("Not Allowed")




# class LoginView(View):
#     template_name = 'accounts/login.html'
#
#     form_class =LoginForm
#     print("under login view")
#     # success_message = "One-Time password sent to your registered mobile number.\
#     #                     The verification code is valid for 10 minutes."
#
#     def post(self,request):
#         print("under post method")
#         form = self.form_class(request.POST)
#         if form.is_valid():
#             user=self.request.POST
#             print(user)
#
#             try:
#                 response = send_verfication_code(user)
#             except Exception as e:
#                 messages.add_message(self.request, messages.ERROR,
#                                 'verification code not sent. \n'
#                                 'Please re-login.')
#                 return redirect('/login')
#             data = json.loads(response.text)
#
#             print(response.status_code, response.reason)
#             print(response.text)
#             print(data['success'])
#             if data['success'] == False:
#                 messages.add_message(self.request, messages.ERROR,
#                                 data['message'])
#                 return redirect('/login')
#
#             else:
#                 kwargs = {'user': user}
#                 print("this is kwargs under register view")
#                 print(kwargs)
#                 self.request.method = 'GET'
#                 return PhoneVerificationView(self.request,**kwargs)
#



    #
    #
    # def get(self,request):
    #     print("under get method")
    #     form = self.form_class()
    #     return render(request, self.template_name, {'form': form})








flag=False
user_for_phone_confirmation={}
def PhoneVerificationView(request, **kwargs):
    template_name = 'accounts/phone_confirm.html'
    global flag,user_for_phone_confirmation
    if flag==False and user_for_phone_confirmation=={} and kwargs!={}:
        print(kwargs['user'])
        user_for_phone_confirmation=kwargs['user']
        flag=True




    if request.method == "POST":
        flag=False
        phone_number = request.POST['phone_number']
        form = PhoneVerificationForm(request.POST)
        if form.is_valid():
            user=user_for_phone_confirmation
            verification_code = request.POST['one_time_password']
            response = verify_sent_code(verification_code, user)
            print(response.text)
            data = json.loads(response.text)

            if data['success'] == True:
                # flag=False
                try:
                    already=User.objects.get(phone_number=phone_number)
                except:
                    already=None
                if already:
                    login(request, already)
                    # if user.phone_number_verified is False:
                    #     user.phone_number_verified = True
                        # user.save()
                    return redirect('/index')


                else:
                    userob=User.objects.create(full_name=user['full_name'],
                                            phone_number=user['phone_number'],
                                            country_code=user['country_code'])
                    print(userob)
                    login(request, userob)
                    return redirect('/index')
            else:
                messages.add_message(request, messages.ERROR,
                                data['message'])
                user_for_phone_confirmation=user
                return render(request, template_name, {'user':user})
        else:
            context = {
                'user': user,
                'form': form,
            }
            return render(request, template_name, context)

    elif request.method == "GET":
        try:
            user = kwargs['user']
            return render(request, template_name, {'user': user})
        except Exception as e:
            print("This is Exception")
            print(e)
            return HttpResponse("Not Allowed")



# class LoginView(FormView):
#
#     template_name = 'login.html'
#     form_class = LoginForm
#     success_url = '/dashboard'
#     print('before dispatch')
#     def dispatch(self, request, *args, **kwargs):
#         if self.request.user.is_authenticated:
#             messages.add_message(self.request, messages.INFO,
#                                 "User already logged in")
#             return redirect('/dashboard')
#         else:
#             return super().dispatch(request, *args, **kwargs)
#
#
#     print('after dispatch')
#     def form_valid(self, form):
#         user = form.save()
#         # user=User.object.get(phone_number)
#         # print(user.two_factor_auth)
#         # if user.two_factor_auth is False:
#         #     login(self.request, user)
#         #     return redirect('/dashboard')
#         # else:
#
#
#         try:
#             response = send_verfication_code(user)
#             pass
#         except Exception as e:
#             messages.add_message(self.request, messages.ERROR,
#                                 'verification code not sent. \n'
#                                 'Please retry logging in.')
#             return redirect('/login')
#         data = json.loads(response.text)
#
#         if data['success'] == False:
#             messages.add_message(self.request, messages.ERROR,
#                             data['message'])
#             return redirect('/login')
#
#         print(response.status_code, response.reason)
#         print(response.text)
#         if data['success'] == True:
#             self.request.method = "GET"
#             print(self.request.method)
#             kwargs = {'user':user}
#             return PhoneVerificationView(self.request, **kwargs)
#         else:
#             messages.add_message(self.request, messages.ERROR,
#                     data['message'])
#             return redirect('/login')

#
# def view1(request):
#     return render(request,'accounts/login.html')
#
# def LoginView(request):
#     template_name='accounts/login.html'
#
#     if request.method == "POST":
#         # username = request.POST['username']
#         phone_number = request.POST['phone_number']
#         user = User.objects.get(phone_number=phone_number)
#         if user:
#             try:
#                 response = send_verfication_code(user)
#                 pass
#             except Exception as e:
#                 messages.add_message(request, messages.ERROR,
#                         'verification code not sent. \n'
#                         'Please retry logging in.')
#                 return redirect('/login')
#             data = json.loads(response.text)
#
#             if data['success'] == False:
#                     messages.add_message(request, messages.ERROR,
#                     data['message'])
#                     return redirect('/login')
#
#             print(response.status_code, response.reason)
#             print(response.text)
#             if data['success'] == True:
#                 request.method = "GET"
#                 print(request.method)
#                 kwargs = {'user':user}
#                 dict={'user':user}
#                 return PhoneVerificationView(request,**kwargs)
#             else:
#                 messages.add_message(request, messages.ERROR,
#                 data['message'])
#                 return redirect('/login')
#         else:
#             return redirect('/login')
#
#
#     else:
#         return HttpResponse("Not Allowed")





@method_decorator(login_required(login_url="/login/"), name='dispatch')
class DashboardView(SuccessMessageMixin, View):
    template_name = 'accounts/dashboard.html'

    def get(self, request):
        context = {
            'user':self.request.user,
            }
        # if not request.user.phone_number_verified:
        #     messages.add_message(self.request, messages.INFO,
        #                         "User Not verified.")
        # return render(self.request, self.template_name, context)

    # def post(self, request):
    #     if 'two_factor_auth' in request.POST:
    #         if request.user.two_factor_auth:
    #             request.user.two_factor_auth = False
    #         else:
    #             request.user.two_factor_auth = True
    #         request.user.save()

        return render(self.request, self.template_name, {})

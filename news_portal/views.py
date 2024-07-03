# Импортируем класс, который говорит нам о том,
# что в этом представлении мы будем выводить список объектов из БД
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.views import View
from django.core.mail import send_mail, EmailMultiAlternatives # объект письма с HTML
from django.template.loader import render_to_string # функция для рендера HTML в строку
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, TemplateView
from django.shortcuts import render
from .models import Post, Comment, Category, Appointment
from .filters import PostFilter
from .forms import PostForm
from django.shortcuts import reverse, render, redirect
from datetime import datetime
from pprint import pprint


class PostsList(ListView): #класс для показа общего списка всепх публикаций
    # Указываем модель, объекты которой мы будем выводить
    model = Post
    # Поле, которое будет использоваться для сортировки объектов
    # ordering = 'create_time'
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'flatpages/news.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'post'
    paginate_by = 10

    def context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        return context

class PostDetail(DetailView): # детальная информация конкретного поста
    model = Post
    template_name = 'flatpages/post.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs): # модернизация контекста для отображения комментариев
                                                # на отдельной странице поста
        context=super().get_context_data(**kwargs)
        context['comm'] = Comment.objects.filter(post_id=self.kwargs['pk'])
        form=PostForm(initial={'title': self.object.title,
                               'content': self.object.content,
                               'create_time': self.object.create_time,
                               'author': self.object.author,
                               'postType': self.object.postType})
        form.fields['author'].disabled = True
        form.fields['title'].disabled = True
        form.fields['content'].disabled = True
        form.fields['create_time'].disabled = True
        form.fields['postType'].disabled = True
        context['form'] = form
        context['id']=self.object.pk # переменная контекста, передающая id поста
        return context

class PostFilterView(ListView): # класс для отображения фильтра поста на отдельной HTML странице 'search.html'
    model = Post
    template_name = 'flatpages/search.html'
    context_object_name = 'post'
    paginate_by =3

    def get_queryset(self):
        queryset=super().get_queryset()
        self.filter = PostFilter(self.request.GET,queryset)
        return self.filter.qs

    def get_context_data(self,  **kwargs): #добавление в контекст фильтра
        context=super().get_context_data(**kwargs)
        context['filter']=self.filter
        return context

def create_post(request): # функция для создания и добавления новой публикации
    form=PostForm()
    form.fields['create_time'].disabled = True
    if request.method=='POST':
        form=PostForm(request.POST)
        if form.is_valid():
            Post.objects.create(**form.cleaned_data)
            return render(request, 'flatpages/messages.html', {'state':'Новая публикация добавлена успешно!'})
    return render(request, 'flatpages/edit.html', {'form':form, 'button':'Опубликовать'})

def edit_post(request, pk): # функция для редактирования названия и содержания поста
    post = Post.objects.get(pk=pk)
    form=PostForm(initial={'create_time':post.create_time,
                           'author':post.author,
                           'postType':post.postType,
                           'title': post.title,
                           'content': post.content
                           })
    form.fields['postType'].disabled = True
    form.fields['author'].disabled = True
    form.fields['create_time'].disabled = True
    if request.method=='POST':
        form=PostForm(request.POST, post)
        form.fields['postType'].required = False
        form.fields['author'].required = False
        form.fields['create_time'].required = False
        try:
            if form.is_valid():
                Post.objects.filter(pk=pk).update(**{'author':post.author,
                                                     'postType':post.postType,
                                                     'create_time':post.create_time,
                                                     'title':form.cleaned_data['title'],
                                                     'content':form.cleaned_data['content']})
                return render(request, 'flatpages/messages.html', {'state': 'Изменения успешно сохранены.'})
        except TypeError:
            return render(request, 'flatpages/messages.html', {'state':'Возникла ошибка! Возможно причина в превышении лимита названия поста, попавшего в БД не через форму'})
    return render(request, 'flatpages/edit.html', {'form':form, 'button':'Сохранить изменения'})

def delete_post(request, pk):
    post = Post.objects.get(pk=pk)
    if request.method=='POST':
        post.delete()
        return render(request, 'flatpages/messages.html', {'state': 'Пост успешно удален'})
    return render(request, 'flatpages/del_post.html',{'post':post})

class AppointementView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'flatpages/mail.html', {})

    def post(self, request, *args, **kwargs):
        appointment = Appointment(client=request.POST['client_name'],
                                   # date=datetime.strptime(request.POST['date'],''),
                                   message=request.POST['message'])
        appointment.save()

        # отправка письма
        # send_mail(subject=f'{appointment.client} ',
        #           message=appointment.message, # сообщение с кратким описанием проблемы
        #           from_email='sportactive.SK@yandex.ru', # почта, с которой осуществляется отправка,
        #           recipient_list=['sportactive.SK@yandex.ru','rfa-kstu@yandex.ru'] # список полуяателей
        # )

        # преоьразование HTML в текст
        html_content =render_to_string('flatpages/send_html_mail.html', {'appointment':appointment})
        msg=EmailMultiAlternatives(subject=f'{appointment.client} ',
                                   body=appointment.message,
                                   from_email='sportactive.SK@yandex.ru',
                                   to=[f'{request.POST['email']}'])
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
        return render(request, 'flatpages/messages.html', {})




# Неиспользуемые классы ниже
class CommListView(ListView):  # класс для отобрпажения
    model = Comment
    template_name = 'flatpages/comm.html'
    context_object_name = 'cmts'
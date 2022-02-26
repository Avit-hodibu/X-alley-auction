from itertools import count
from multiprocessing import cpu_count
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.views import View
User = get_user_model()
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db.models import Count
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import DetailView, ListView,TemplateView

from .models import User, Category, Listing, Comment, Watch, Bid
from django.db import models
from .forms import CreateUserForm, ListingForm, CommentFormInline, ContactFormData, BidForm
import os

class Contact(TemplateView):
    template_name = "auctions/contact.html"

def index(request):
    top_engage= Listing.objects.filter(active=True).annotate(c_count=Count("comment")).filter(c_count__gt=3)
    top_review= Listing.objects.filter(active=True).annotate(b_count=Count("bid")).filter(b_count__gt=3)      
    return render(request, "auctions/index.html", {
        "top_engage": top_engage,
        "top_review":top_review,
        "listings": Listing.objects.filter(active=True).exclude(id=22),
        "specials": Listing.objects.filter(special=True).exclude(id=22),
        "categories": Listing.objects.filter(active=True).values('category__title', 'category__id').annotate(models.Count('id')),
        })


def about(request):
    return render(request,"auctions/about.html",{
        "listings": Listing.objects.filter(active=True),

        "categories": Listing.objects.filter(active=True).values('category__title', 'category__id').annotate(models.Count('id')),
        })      
def contactFormView(request):
    if request.method == "POST":
        form = ContactFormData(request.POST or None)
        if form.is_valid():
            form.save()
            form = ContactFormData()
    else:
        form = ContactFormData()
    return render(request, "auctions/contact.html", {
        "form": form,
        "listings": Listing.objects.filter(active=True),
        "categories": Listing.objects.filter(active=True).values('category__title', 'category__id').annotate(models.Count('id')),
        })

def active(request):
    
    top_engage= Listing.objects.filter(active=True).annotate(c_count=Count("comment")).filter(c_count__gt=3)
    top_review= Listing.objects.filter(active=True).annotate(b_count=Count("bid")).filter(b_count__gt=3)
    # for list in top_engage:
    #     print(list.title, list.c_count, list.active)
    # total=Comment.objects.filter(listing=listing)
    # print(total.count())
    return render(request,"auctions/shop-grid.html", {
        "top_engage": top_engage,
        "top_review":top_review,
        "listings": Listing.objects.filter(active=True).exclude(id=22),
        "specials": Listing.objects.filter(special=True).exclude(id=22),

        "categories": Listing.objects.filter(active=True).values('category__title', 'category__id').annotate(models.Count('id')),
    })

def search(request):
    search = request.GET['search']
    listings = Listing.objects.filter(title__icontains=search)
    params = {"listings": listings,
                "categories": Listing.objects.filter(active=True).values('category__title', 'category__id').annotate(models.Count('id'))
                }
    return render(request,"auctions/search.html",params)
 
# @login_required(login_url='/login')
def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Listing.objects.filter(active=True).values('category__title', 'category__id').annotate(models.Count('id')),
        })


class ListingList(ListView):
    model = Listing
    fields = '__all__'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the category
        category_id = 0
        if 'category_id' in self.kwargs :
            category_id = self.kwargs['category_id']
        active_filter = True
        if category_id == 9999 :
            active_filter = False
            category_id = 0
        if category_id > 0 :
            context['categories'] = Listing.objects.filter(active=active_filter).filter(category=Category.objects.get(id=category_id)).values('category__title', 'category__id').annotate(models.Count('id'))
        else :
            context['categories'] = Listing.objects.filter(active=active_filter).values('category__title', 'category__id').annotate(models.Count('id'))
        context['active'] = active_filter
        return context

    def get_queryset(self):
        if 'category_id' in self.kwargs :
            category_id = self.kwargs['category_id']
            active_filter = True
            if category_id == 9999 :
                active_filter = False
                category_id = 0
            if category_id > 0 :
                category = Category.objects.get(id=category_id)
                return Listing.objects.filter(category=category).filter(active=active_filter) #.annotate(filename)
        return Listing.objects.all().filter(active=active_filter) #.annotate(filename)


class ListingDetail(DetailView):
    model = Listing

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # If current user is authenticated and is consignor?
        user = self.request.user
        consignor = self.object.created_by
        if user.is_authenticated :
            if user.id == consignor.id :
                context['consignor'] = True
            watchs = Watch.objects.filter(listing=self.object, user=user)
            watch = None
            if watchs :
                watch = watchs[0]
            context['watch'] = watch
            form = BidForm()
            context['form'] = form
        context['bids'] = Bid.objects.filter(listing=self.object)
        last_bid = Bid.objects.filter(listing=self.object).last()
        context['last_bid'] = last_bid
        bid_count = Bid.objects.filter(listing=self.object).aggregate(models.Count('listing'))['listing__count']
        context['bid_count'] = bid_count
        min_bid = self.object.start_price
        if bid_count > 0 :
            min_bid = int(last_bid.price + 1)
        context['min_bid'] = min_bid
        context['comment_form'] = CommentFormInline()
        context['comments'] = Comment.objects.filter(listing=self.object).order_by('created').reverse()
        context['next'] = Listing.objects.filter(id__gt=self.object.id).order_by('id').first()
        context['previous'] = Listing.objects.filter(id__lt=self.object.id).order_by('id').last()
        context['first'] = Listing.objects.order_by('id').first()
        context['last'] = Listing.objects.order_by('id').last()
        if self.object.active == False :
            winner = User.objects.get(id=self.object.winner)
            context['winner'] = winner
        return context

@login_required(login_url='auctions:login')
def BidCreate(request, listing_id) :
    if request.method == 'POST' :
        f = BidForm(request.POST)
        if f.is_valid():
            if request.user.is_authenticated :
                new_bid = Bid()
                current_user = request.user
                new_bid.price = f.cleaned_data['price']
                new_bid.listing = Listing.objects.get(id=listing_id)
                new_bid.author = current_user
                new_bid.save()
                new_bid.listing.current_price = new_bid.price
                new_bid.listing.save()
    return HttpResponseRedirect(reverse("auctions:listing-detail", args=(listing_id, )))

@method_decorator(login_required, name='dispatch')
class ListingCreate(CreateView):
    model = Listing
    form_class = ListingForm

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class ListingUpdate(UpdateView):
    model = Listing
    form_class = ListingForm

@method_decorator(login_required, name='dispatch')
class Myauction(View):
    # model = Listing
    
    def get(self,request,*args, **kwargs):
        # Call the base implementation first to get a context
        # context = super().get_context_data(**kwargs)
        # If current user is authenticated and is consignor?
        user = request.user
        context={}
        if user.is_authenticated :

                list = Listing.objects.filter(created_by=user)
                print('fvdv',list)
                context['object_list'] = list
                
        return render(request,'auctions/myauction.html',context)
    # def get_queryset(self):

    #     user = self.request.user
    #     consignor = self.request.created_by
    #     if user.is_authenticated :
    #         if user.id == consignor.id :
    #             list = Listing.objects.get(user.id == consignor.id)
    #             return Listing.objects.filter(user.id == consignor.id) #.annotate(filename)
    #     return Listing.objects.all().filter(user.id == consignor.id)

@method_decorator(login_required, name='dispatch')
class ListingDelete(DeleteView):
    model = Listing
    success_url = reverse_lazy('auctions:listing-list', args= (0,))

@login_required(login_url='auctions:login')
def ListingClose(request, listing_id):
    if request.user.is_authenticated :
        listing = Listing.objects.get(id=listing_id)
        last_bid = Bid.objects.filter(listing=listing).last()
        if listing.created_by == request.user :
            listing.active = False
            winner = last_bid.author
            listing.winner = winner.id
            listing.save()
    return HttpResponseRedirect(reverse("auctions:listing-detail", args=(listing_id, )))

@login_required(login_url='auctions:login')
def CommentCreate(request, listing_id):
    if request.method == 'POST' :
        f = CommentFormInline(request.POST)
        if f.is_valid():
            if request.user.is_authenticated :
                new_comment = Comment()
                current_user = request.user
                new_comment.text = f.cleaned_data['text']
                new_comment.listing = Listing.objects.get(id=listing_id)
                new_comment.author = current_user
                new_comment.save()
                return HttpResponseRedirect(reverse("auctions:listing-detail", args=(listing_id, )))
    form = CommentFormInline()
    return render(request, 'auctions/comment_form.html', {'form':form})


@login_required(login_url='auctions:login')
def WatchCreate(request, listing_id):
    if request.user.is_authenticated :
        listing = Listing.objects.get(id=listing_id)
        if listing :
            old_watch = Watch.objects.filter(listing=listing, user=request.user)
            if not old_watch :
                new_watch = Watch()
                new_watch.listing = listing
                new_watch.user = request.user
                new_watch.save()
    return HttpResponseRedirect(reverse("auctions:listing-detail", args=(listing_id, )))

@method_decorator(login_required, name='dispatch')
class WatchList(ListView):
    model = Watch
    fields = '__all__'

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)
        return Watch.objects.filter(user=user) #annotate(Bid.objects.filter(listing=Watch.listing).last())

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)
        watches = Watch.objects.filter(user=user)
        watches_list = []
        for watch in watches :
            last_bid = Bid.objects.filter(listing=watch.listing).last()
            if not watch.listing.active :
                winner = User.objects.get(id=watch.listing.winner)
            else :
                winner = None
            if last_bid :
                item = {'title': watch.listing.title,
                        'price' : last_bid.price,
                        'by' : last_bid.author.username,
                        'listing_id': watch.listing.id,
                        'image': os.path.basename(watch.listing.image.url),
                        'created_by': watch.listing.created_by,
                        'active': watch.listing.active,
                        'winner': winner}
            else :
                item = {'title': watch.listing.title,
                        'price' : 'no bid',
                        'listing_id': watch.listing.id,
                        'image': os.path.basename(watch.listing.image.url),
                        'created_by': watch.listing.created_by}
            watches_list.append(item)
        context['watches'] = watches_list
        return context

@login_required(login_url='auctions:login')
def WatchDelete(request, watch_id):
    user = request.user
    watch = Watch.objects.get(id=watch_id)
    listing_id = watch.listing.id
    if watch and watch.user == user :
        watch.delete()
    return HttpResponseRedirect(reverse("auctions:listing-detail", args=(listing_id, )))


def login_view(request):
	if request.user.is_authenticated:
		return redirect('auctions:index')
	else:
		if request.method == 'POST':
			username = request.POST.get('username')
			password =request.POST.get('password')

			user = authenticate(request, username=username, password=password)

			if user is not None:
				login(request, user)
				return redirect('auctions:index')
			else:
				messages.info(request, 'Username OR password is incorrect')

		context = {}
		return render(request, 'auctions/login.html', context)


    # if request.user.is_authenticated:
    #     return redirect('http://127.0.0.1:8000/') # code to be changed
    # if request.method == "POST":

    #     # Attempt to sign user in
    #     username = request.POST["username"]
    #     password = request.POST["password"]
    #     user = authenticate(request, username=username, password=password)

    #     # Check if authentication successful
    #     if user is not None:
    #         login(request, user)
    #         return HttpResponseRedirect(reverse("auctions:index"))
    #     else:
    #         return render(request, "auctions/login.html", {
    #             "message": "Invalid username and/or password."
    #         })
    # else:
    #     return render(request, "auctions/login.html")

@login_required(login_url='auctions:login')
def logout_view(request):
	logout(request)
	return redirect('auctions:login')
    # return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user)

                return redirect('auctions:login')
            

        context = {'form':form}
        return render(request, 'auctions/register.html', context)


    # if request.method == "POST":
    #     username = request.POST["username"]
    #     email = request.POST["email"]

    #     # Ensure password matches confirmation
    #     password = request.POST["password"]
    #     confirmation = request.POST["confirmation"]
    #     if password != confirmation:
    #         return render(request, "auctions/register.html", {
    #             "message": "Passwords must match."
    #         })

    #     # Attempt to create new user
    #     try:
    #         user = User.objects.create_user(username, email, password)
    #         user.save()
    #     except IntegrityError:
    #         return render(request, "auctions/register.html", {
    #             "message": "Username already taken."
    #         })
    #     login(request, user)
    #     return HttpResponseRedirect(reverse("auctions:index"))
    # else:
    #     return render(request, "auctions/register.html")

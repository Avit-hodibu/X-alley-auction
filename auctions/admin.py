from django.contrib import admin
from .models import User, Category, Listing, Comment, Watch, Bid, ContactForm




admin.site.site_header = "X-ALLEY"
admin.site.site_title = "X-alley "
admin.site.index_title = "Welcome to X-alley admin pannel"
# Register your models here.


class CommentInline(admin.TabularInline): # new
    model = Comment
class BidInline(admin.TabularInline): # new
    model = Bid

admin.site.register(User)
admin.site.register(Category)
admin.site.register(ContactForm)

admin.site.register(Comment)
@admin.register(Watch)
class WatchAdmin(admin.ModelAdmin):
    list_display= ('user','listing')

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display= ('listing','price','author','created',)
    list_filter = ("price", )
    

class ListingAdmin(admin.ModelAdmin):
    list_display =('title','start_price','description','image','category','current_price','created_by','active','winner')
    list_filter = ('category','start_price','active' )
    search_fields = ("title", )
    inlines = [
    CommentInline, BidInline, 
    ]
    

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        try:
            search_term_as_int = int(search_term)
        except ValueError:
            pass
        else:
            queryset |= self.model.objects.filter(starting_bid=search_term_as_int)
        return queryset, use_distinct
admin.site.register(Listing, ListingAdmin)
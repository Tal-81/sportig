from django.contrib import admin
from .models import SupportTicket, TicketReply


class TicketReplyInline(admin.TabularInline):
    model = TicketReply
    extra = 1
    readonly_fields = ['author', 'created_at', 'is_staff_reply']


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'subject', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['subject', 'user__email']
    list_editable = ['status']
    inlines = [TicketReplyInline]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, TicketReply):
                instance.author = request.user
                instance.is_staff_reply = True
                instance.save()
        formset.save_m2m()

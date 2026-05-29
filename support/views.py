"""Support ticket views."""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django import forms

from .models import SupportTicket, TicketReply


class TicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ['subject', 'message']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe your issue'}),
        }


class ReplyForm(forms.ModelForm):
    class Meta:
        model = TicketReply
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Your reply'})
        }


@method_decorator(login_required, name='dispatch')
class TicketListView(View):
    template_name = 'support/ticket_list.html'

    def get(self, request):
        tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')
        return render(request, self.template_name, {
            'tickets': tickets,
            'page_title': 'Support Tickets',
        })


@method_decorator(login_required, name='dispatch')
class CreateTicketView(View):
    template_name = 'support/create_ticket.html'

    def get(self, request):
        form = TicketForm()
        return render(request, self.template_name, {'form': form, 'page_title': 'New Support Ticket'})

    def post(self, request):
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('support:detail', ticket_id=ticket.id)
        return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name='dispatch')
class TicketDetailView(View):
    template_name = 'support/ticket_detail.html'

    def get(self, request, ticket_id):
        ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
        form = ReplyForm()
        return render(request, self.template_name, {
            'ticket': ticket,
            'replies': ticket.replies.select_related('author').all(),
            'form': form,
            'page_title': f'Ticket #{ticket.id}',
        })

    def post(self, request, ticket_id):
        ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.ticket = ticket
            reply.author = request.user
            reply.is_staff_reply = request.user.is_staff
            reply.save()
            return redirect('support:detail', ticket_id=ticket.id)
        return render(request, self.template_name, {
            'ticket': ticket,
            'replies': ticket.replies.all(),
            'form': form,
        })

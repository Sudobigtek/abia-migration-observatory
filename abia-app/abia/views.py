from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    return render(request, "dashboard.html")

@login_required
def migrant_list_view(request):
    return render(request, "migrant_list.html")

@login_required
def case_detail_view(request):
    return render(request, "case_detail.html")

@login_required
def referral_form_view(request):
    return render(request, "referral_form.html")

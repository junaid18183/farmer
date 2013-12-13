import json

from django.shortcuts import render_to_response, redirect
from django.contrib.admin.views.decorators import staff_member_required

from farmer.models import Job

def run_job(inventories, cmd):
    job = Job()
    job.inventories = inventories
    job.cmd = cmd
    job.run()


@staff_member_required
def home(request):
    if request.method == 'POST':
        inventories = request.POST.get('inventories', '')
        cmd = request.POST.get('cmd', '')
        if '' in [inventories.strip(), cmd.strip()]:
            return redirect('/')
        run_job(inventories, cmd)
        return redirect('/')
    else:
        jobs = Job.objects.all().order_by('-id')
        return render_to_response('home.html', locals())

@staff_member_required
def detail(request, id):
    assert(request.method == 'GET')
    job = Job.objects.get(id = id)
    result = job.result and json.loads(job.result) or {}
    failures = {}
    success = {}
    for k, v in result.items():
        if v.get('rc'):
            failures[k] = v
        else:
            success[k] = v
    return render_to_response('detail.html', locals())

@staff_member_required
def retry(request, id):
    assert(request.method == 'GET')
    job = Job.objects.get(id = id)
    if job.result is None:
        inventories = job.inventories
    else:
        result = json.loads(job.result)
        failures = {}
        for k, v in result.items():
            if v.get('rc'):
                failures[k] = v
        failures = failures.keys()
        if failures:
            inventories = ':'.join(failures)
        else:
            inventories = job.inventories
    run_job(inventories, job.cmd)
    return redirect('/')

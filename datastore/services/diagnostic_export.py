from datastore import models


def project_diagnostic_row(project):
    project_runs = [
        pr.project_run for pr in project.project_results.all()
        if pr.project_run is not None
    ]
    row = {
        'project_id': project.project_id,
        'project_pk': project.id,
        'project_result_count': project.project_results.count(),
        'project_run_count': len(project_runs),
        'project_run_count_pending': sum([
            1 for pr in project_runs if pr.status == 'PENDING'
        ]),
        'project_run_count_running': sum([
            1 for pr in project_runs if pr.status == 'RUNNING'
        ]),
        'project_run_count_success': sum([
            1 for pr in project_runs if pr.status == 'SUCCESS'
        ]),
        'project_run_count_failed': sum([
            1 for pr in project_runs if pr.status == 'FAILED'
        ]),
    }
    return row


def diagnostic_export():
    projects = models.Project.objects.all().prefetch_related(
        'project_results',
        'project_results__project_run',
    ).order_by('-id')

    return {
        'headers': [
            'project_id',
            'project_pk',
            'project_result_count',
            'project_run_count',
            'project_run_count_pending',
            'project_run_count_running',
            'project_run_count_success',
            'project_run_count_failed',
        ],
        'rows': [
            project_diagnostic_row(project) for project in projects
        ],
    }

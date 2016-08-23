from datastore.services import overview
import pytest

@pytest.mark.django_db
def test_overview():
    results = overview()
    assert results['project_count'] == 0
    assert results['consumptionmetadata_count'] == 0
    assert results['consumptionrecord_count'] == 0
    assert results['projectresult_count'] == 0

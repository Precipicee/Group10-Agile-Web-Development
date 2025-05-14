from Fittrack import create_app
from Fittrack.models import db, SharedReport

app = create_app()
with app.app_context():
    invalid_reports = SharedReport.query.filter((SharedReport.report_type == None) | (SharedReport.report_type == '')).all()
    for report in invalid_reports:
        db.session.delete(report)
    db.session.commit()
    print("Cleaned invalid SharedReport records")
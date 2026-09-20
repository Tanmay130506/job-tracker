from sqlalchemy import text


def get_status_counts(user_id, db):
    result= db.execute(
        text("""
            SELECT status, COUNT(*) as count
            FROM applications
            WHERE user_id= :user_id
            GROUP BY status
        """),
        {
            "user_id": user_id,         
        }
    )
    rows= result.fetchall()
    return [{"status": row[0], "count": row[1]} for row in rows]


def get_applications_per_week(user_id, db):

    result= db.execute(
        text("""
        SELECT DATE_TRUNC('week', date) as week, COUNT(*) as count
        FROM applications
        WHERE user_id= :user_id
        GROUP BY week
        ORDER BY week
        """),
        {
            "user_id": user_id
        }
    )
    rows= result.fetchall()
    return [{"week": str(row[0]), "count": row[1]} for row in rows]


def get_response_rate(user_id, db):

    result = db.execute(
        text("""
            SELECT
    CASE 
        WHEN COUNT(*) = 0 THEN 0
        ELSE COUNT(CASE WHEN status IN ('interviewing', 'offered') THEN 1 END) * 100.0 / COUNT(*)
    END AS response_rate
FROM applications
WHERE user_id = :user_id
        """),
        {
            "user_id": user_id,
        }
    )

    response_rate = result.scalar()

    return response_rate
    

def company_count(user_id, db):
    result= db.execute(
        text("""
        SELECT company_name, COUNT(*) as count
        FROM applications
        WHERE user_id = :user_id
        GROUP BY company_name
        """),
        {
            "user_id": user_id
        }
    )

    rows= result.fetchall()
    return [{"company_name": row[0], "count": row[1]} for row in rows]


def average_days_to_response(user_id, db):
    result = db.execute(
        text("""
            SELECT AVG(
                EXTRACT(
                    EPOCH FROM (first_response.first_response_date - applications.date)
                ) / 86400
            ) AS average_days
            FROM applications
            JOIN (
                SELECT
                    application_id,
                    MIN(date) AS first_response_date
                FROM history
                WHERE new_status IN ('interviewing', 'offered')
                GROUP BY application_id
            ) AS first_response
            ON applications.application_id = first_response.application_id
            WHERE applications.user_id = :user_id
        """),
        {
            "user_id": user_id
        }
    )

    return result.scalar()
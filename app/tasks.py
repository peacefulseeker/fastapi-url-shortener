from app.db import GetDBTable


def increment_url_visits(short_path: str, table: GetDBTable) -> None:
    table.update_item(
        Key={"ShortPath": short_path},
        UpdateExpression="ADD Visits :inc",
        ExpressionAttributeValues={":inc": 1},
    )

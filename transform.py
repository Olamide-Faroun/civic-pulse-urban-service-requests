import polars as pl
import os
from dotenv import load_dotenv

load_dotenv()

storage_options = {
    'account_name': 'urbancitystoragee',
    'account_key': os.getenv('ACCOUNT_KEY')
}

def transform():
    source_uri = 'az://bronze/urban_service_requests.csv'
    target_uri = 'az://silver/urban_service_requests.parquet'

    df = pl.scan_csv(source_uri, storage_options=storage_options)

    column_mapping = {
        "Unique Key": "request_id",
        "Created Date": "created_date",
        "Closed Date": "closed_date",
        "Agency": "agency",
        "Agency Name": "agency_name",
        "Problem (formerly Complaint Type)": "problem",
        "Problem Detail (formerly Descriptor)": "problem_detail",
        "Additional Details": "additional_details",
        "Location Type": "location_type",
        "Incident Zip": "incident_zip",
        "Incident Address": "incident_address",
        "City": "city",
        "Borough": "borough",
        "Status": "status",
        "Resolution Description": "resolution_description",
        "Resolution Action Updated Date": "resolution_updated_date",
        "Community Board": "community_board",
        "Council District": "council_district",
        "Police Precinct": "police_precinct",
        "Open Data Channel Type": "channel",
        "Latitude": "latitude",
        "Longitude": "longitude"
    }

    # More data transformation
    df_refined = df.select([
        pl.col(old).alias(new) for old, new in column_mapping.items()
    ])

    text_columns = [
        col for col, dtype in df_refined.schema.items()
        if dtype == pl.String
    ]

    df_refined = df_refined.with_columns([
        pl.col(col).str.strip_chars().replace("", None).alias(col) for col in text_columns
    ])

    df_refined = df_refined.with_columns([
        pl.col("created_date").str.strptime(
            pl.Datetime,
            format="%m/%d/%Y %H:%M",
            strict=False
        ),

        pl.col("closed_date").str.strptime(
            pl.Datetime,
            format="%m/%d/%Y %H:%M",
            strict=False
        ),

        pl.col("resolution_updated_date").str.strptime(
            pl.Datetime,
            format="%m/%d/%Y %H:%M",
            strict=False
        )
    ])

    # Change datetime precision for Azure Data Factory compatibility
    df_refined = df_refined.with_columns([
        pl.col("created_date").cast(pl.Datetime(time_unit="ms")),
        pl.col("closed_date").cast(pl.Datetime(time_unit="ms")),
        pl.col("resolution_updated_date").cast(pl.Datetime(time_unit="ms"))
    ])

    df_refined = df_refined.with_columns([
        pl.col("borough").str.to_uppercase(),
        pl.col("city").str.to_uppercase(),
        pl.col("status").str.to_titlecase(),
        pl.col("agency").str.to_uppercase(),
        pl.col("channel").str.to_uppercase()
    ])

    df_refined = df_refined.with_columns(
        pl.col("incident_zip").cast(pl.Int64, strict=False).cast(pl.String)
    )

    df_refined = df_refined.with_columns([
        pl.col("latitude").cast(pl.Float64, strict=False),
        pl.col("longitude").cast(pl.Float64, strict=False)
    ])

    df_refined = df_refined.with_columns(
        (pl.col("closed_date") - pl.col("created_date")).dt.total_minutes().truediv(60).round(2).alias("resolution_hours")
    )

    df_refined = df_refined.with_columns(
        pl.when(pl.col("status") != "Closed").then(pl.lit(True)).otherwise(pl.lit(False)).alias("is_backlog")
    )

    df_refined = df_refined.with_columns([
        pl.col("created_date").dt.date().alias("created_date_only"),
        pl.col("created_date").dt.year().alias("created_year"),
        pl.col("created_date").dt.month().alias("created_month"),
        pl.col("created_date").dt.weekday().alias("created_weekday"),
        pl.col("created_date").dt.hour().alias("created_hour")
    ])

    df_refined = df_refined.unique(
        subset=["request_id"],
        keep="first"
    )

    df_refined = df_refined.with_columns(
    pl.col("police_precinct").str.replace("Precinct ", "").cast(pl.Int64, strict=False).alias("police_precinct")
    )

    df_refined = df_refined.with_columns(
    pl.col("council_district").cast(pl.Int64, strict=False).alias("council_district")
    )

    df_refined.sink_parquet(
        target_uri,
        storage_options=storage_options,
        compression='snappy'
    )

    print(f'data loaded to {target_uri}')

    return None

transform()
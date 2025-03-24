import boto3
from datetime import datetime, timedelta, timezone

# AWS region
AWS_REGION = "us-east-1"  # Change this to your region
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:123456789012:StaleSnapshotAlerts"  # Replace with your SNS ARN

# Initialize AWS clients
ec2 = boto3.client("ec2", region_name=AWS_REGION)
cloudtrail = boto3.client("cloudtrail", region_name=AWS_REGION)
sns = boto3.client("sns", region_name=AWS_REGION)

# Define time thresholds
today = datetime.now(timezone.utc)
three_months_ago = today - timedelta(days=90)
six_months_ago = today - timedelta(days=180)

def send_sns_alert(snapshot_list):
    """Send an email alert for stale snapshots using SNS."""
    if not snapshot_list:
        return

    message = "The following snapshots are older than 3 months and have no associated volume:\n\n"
    for snap in snapshot_list:
        message += f"- Snapshot: {snap['SnapshotId']}, Created: {snap['StartTime']}, Volume Deleted: {snap['VolumeDeletedTime']}\n"

    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject="AWS Stale Snapshot Alert",
        Message=message
    )
    print("📧 SNS Alert Sent!")

def get_volume_deletion_time(volume_id):
    """Check CloudTrail logs for the DeleteVolume event of a given volume."""
    try:
        response = cloudtrail.lookup_events(
            LookupAttributes=[{"AttributeKey": "ResourceName", "AttributeValue": volume_id}],
            StartTime=six_months_ago,
            EndTime=today,
            MaxResults=5
        )

        for event in response.get("Events", []):
            if "DeleteVolume" in event["EventName"]:
                return event["EventTime"]  # Timestamp of deletion

    except Exception as e:
        print(f"⚠️ Error checking CloudTrail logs: {e}")
    
    return None  # No delete event found

def delete_snapshot(snapshot_id):
    """Delete an EBS snapshot."""
    try:
        ec2.delete_snapshot(SnapshotId=snapshot_id)
        print(f"✅ Deleted snapshot: {snapshot_id}")
    except Exception as e:
        print(f"❌ Error deleting snapshot {snapshot_id}: {e}")

def process_snapshots():
    """List snapshots, send alerts, and delete old ones."""
    response = ec2.describe_snapshots(OwnerIds=["self"])
    snapshots = response.get("Snapshots", [])

    alert_snapshots = []  # Store snapshots for SNS alerts

    for snapshot in snapshots:
        snapshot_id = snapshot["SnapshotId"]
        start_time = snapshot["StartTime"]
        volume_id = snapshot.get("VolumeId", None)

        # If no associated volume
        if not volume_id:
            if start_time < six_months_ago:
                print(f"⏳ Deleting snapshot {snapshot_id}, Created: {start_time}")
                delete_snapshot(snapshot_id)
            elif start_time < three_months_ago:
                alert_snapshots.append({
                    "SnapshotId": snapshot_id,
                    "StartTime": start_time,
                    "VolumeDeletedTime": "Unknown"
                })
        else:
            # Check if the volume was deleted
            volume_deleted_time = get_volume_deletion_time(volume_id)
            if volume_deleted_time and volume_deleted_time < three_months_ago:
                alert_snapshots.append({
                    "SnapshotId": snapshot_id,
                    "StartTime": start_time,
                    "VolumeDeletedTime": volume_deleted_time
                })

    # Send SNS alert for snapshots older than 3 months
    if alert_snapshots:
        send_sns_alert(alert_snapshots)
    else:
        print("No stale snapshots found.")

# Run the function
if __name__ == "__main__":
    process_snapshots()


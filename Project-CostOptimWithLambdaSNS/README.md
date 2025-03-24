# AWS Cost Optimization - Stale Snapshot Cleanup

## Overview
This project automates the cleanup of stale AWS EBS snapshots to optimize costs. The Lambda function:
- **Deletes snapshots older than 6 months** if they have no associated volume.
- **Sends SNS email alerts for snapshots older than 3 months** if their associated volume was deleted.
- **Runs bi-weekly** using AWS Lambda and CloudWatch Events.

## Prerequisites
### AWS Resources Required:
- **AWS Lambda** for automation.
- **Amazon EC2** for snapshot management.
- **Amazon SNS** for email alerts.
- **AWS CloudTrail** to track volume deletion events.
- **Amazon EventBridge (CloudWatch Events)** to schedule Lambda execution.

## Deployment Steps
### 1️⃣ Set Up IAM Role for Lambda
1. Navigate to **IAM** → **Roles** → **Create Role**.
2. Choose **AWS Service** → **Lambda**.
3. Attach the following policies:
   - `AmazonEC2FullAccess` (for snapshot operations)
   - `AWSCloudTrailReadOnlyAccess` (for tracking volume deletion)
   - `AmazonSNSFullAccess` (for sending alerts)
4. Click **Create Role** and copy the Role ARN.

### 2️⃣ Create SNS Topic for Alerts
1. Go to **Amazon SNS** → **Create Topic** → **Standard**.
2. Name it **StaleSnapshotAlerts** and copy the **Topic ARN**.
3. Under **Subscriptions**, create a new subscription:
   - **Protocol:** Email
   - **Endpoint:** Your email address
4. Confirm the email subscription.

### 3️⃣ Deploy Lambda Function
1. Go to **AWS Lambda** → **Create Function** → **Author from Scratch**.
2. Enter **Function Name:** `stale-snapshot-cleanup`.
3. Runtime: **Python 3.9 or later**.
4. Choose **Use an existing role** and select the IAM role created earlier.
5. Click **Create Function**.

### 4️⃣ Upload the Python Script
1. Navigate to the **Code** tab in Lambda.
2. Delete existing code and paste the [script](script.py).
3. Click **Deploy**.

### 5️⃣ Add Environment Variables
Go to **Configuration** → **Environment Variables** and add:
```
AWS_REGION = us-east-1
SNS_TOPIC_ARN = arn:aws:sns:us-east-1:123456789012:StaleSnapshotAlerts
```
Click **Save**.

### 6️⃣ Increase Timeout
Go to **Configuration** → **General Configuration**:
- Increase **timeout** to **2 minutes**.
- Click **Save**.

### 7️⃣ Test the Function
1. Click **Test** → **Create a test event**.
2. Name it `test-event` and use `{}` as payload.
3. Click **Test** and check CloudWatch logs for execution results.

### 8️⃣ Schedule Lambda with CloudWatch
1. Go to **Amazon EventBridge** (CloudWatch Events).
2. Click **Create Rule**.
3. Name: `stale-snapshot-schedule`.
4. Choose **Schedule Expression** → `rate(14 days)`.
5. Select **Target** → **AWS Lambda Function** → Choose `stale-snapshot-cleanup`.
6. Click **Create**.

## Testing and Monitoring
- Monitor logs in **CloudWatch Logs**.
- Check **SNS Email Alerts** for 3-month-old stale snapshots.
- Verify **deleted snapshots** in **EC2 Snapshot Console**.

## Contributing
Feel free to submit issues or pull requests to improve the automation.

## License
This project is licensed under the MIT License.

---
🚀 **Your Lambda function is now fully automated!** 🚀



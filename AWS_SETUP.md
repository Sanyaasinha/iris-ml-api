# AWS + GitHub setup (one time, ~30 minutes)

Use the AWS Console. Pick one region (e.g. `ap-south-1`) and use it everywhere.

## 1. Create the ECR repository
ECR → Repositories → **Create repository** → private, name `iris-ml-api`.
Note the URI: `<account-id>.dkr.ecr.<region>.amazonaws.com/iris-ml-api`.

## 2. Create an IAM role for the EC2 instance (so it can pull from ECR)
IAM → Roles → Create role → trusted entity **EC2** → attach policy **AmazonEC2ContainerRegistryReadOnly** → name `iris-ec2-ecr-read`.

## 3. Launch the EC2 instance
* AMI: **Amazon Linux 2023**, type **t2.micro / t3.micro** (free-tier eligible)
* Key pair: create one (`.pem`) and keep it safe
* IAM instance profile: `iris-ec2-ecr-read`
* Security group inbound rules: **SSH (22)** from *My IP* (GitHub runners use changing IPs; if SSH deploy times out, temporarily allow 0.0.0.0/0 for port 22 while testing, then lock it down), **HTTP (80)** from anywhere
* SSH in and run the bootstrap script, then log out and in again:
  ```bash
  ssh -i key.pem ec2-user@<EC2_PUBLIC_IP>
  # paste the contents of scripts/ec2-bootstrap.sh, or git clone the repo and run it
  ```

## 4. Create an IAM user for GitHub Actions
IAM → Users → create `github-actions-deployer` → attach policy **AmazonEC2ContainerRegistryPowerUser** → Security credentials → create an **access key** (use case: CLI/third-party). Save both values.

## 5. Add GitHub repository secrets
Repo → Settings → Secrets and variables → Actions → New repository secret:

| Secret | Value |
|---|---|
| `AWS_ACCESS_KEY_ID` | from step 4 |
| `AWS_SECRET_ACCESS_KEY` | from step 4 |
| `AWS_REGION` | e.g. `ap-south-1` |
| `ECR_REPOSITORY` | `iris-ml-api` |
| `EC2_HOST` | EC2 public IPv4 address (use an Elastic IP so it doesn't change) |
| `EC2_USER` | `ec2-user` |
| `EC2_SSH_KEY` | full contents of the `.pem` file |

## 6. Block pushes/merges when tests fail
Push the repo and let the workflow run once so the `test` check exists. Then:
Repo → Settings → **Branches** (or Rules → Rulesets) → add rule for `main`:
* ✅ Require a pull request before merging
* ✅ Require status checks to pass before merging → select **`test`**
* ✅ Do not allow bypassing the above settings (include administrators)

Now a change that breaks a test can't reach `main`, so it is never deployed.

## 7. Verify
```bash
./scripts/demo.sh http://<EC2_PUBLIC_IP>
```
Take screenshots of: the green Actions run, the ECR image list, the EC2 instance, and the curl output — useful for the README/presentation.

## Cost / cleanup
t2.micro is free-tier eligible; ECR has a small free storage allowance. After grading, **stop the EC2 instance, delete the ECR images, and delete the IAM access key.**

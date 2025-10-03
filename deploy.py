import subprocess
import argparse
import datetime
import os

IMAGE_TAG = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
ECR_REPO = "flask-app"

def run(cmd, capture_output=False):
    print(f"> {cmd}")
    if dry_run:
        return "\n"
    result = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=capture_output)
    if capture_output:
        return result.stdout.strip()
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Show commands that are going to be run but without running them.")
    args = parser.parse_args()
    dry_run = args.dry_run

    try:
        run(f"aws ecr describe-repositories --repository-names {ECR_REPO} --region {REGION}", dry_run=dry_run)
        print(f"ECR repository {ECR_REPO} already exists. Continuing...")
    except subprocess.CalledProcessError:
        run(f"aws ecr create-repository --repository-name {ECR_REPO} --region {REGION}", dry_run=dry_run)

    account_id = run("aws sts get-caller-identity --query Account --output text", capture_output=True, dry_run=dry_run)
    registry = f"{account_id}.dkr.ecr.{REGION}.amazonaws.com"

    run(f"aws ecr get-login-password --region {REGION} | docker login --username AWS --password-stdin {registry}", dry_run=dry_run)
    
    image_uri = f"{ECR_REPO}:{IMAGE_TAG}"
    run(f"docker build -t {image_uri} .", dry_run=dry_run)

    run(f"docker push {image_uri}", dry_run=dry_run)

    try:
        run(f"aws eks describe-cluster --name {EKS_CLUSTER_NAME} --region {REGION}", dry_run=dry_run)
        print(f"EKS cluster {EKS_CLUSTER_NAME} exists")
    except subprocess.CalledProcessError:
        run(f"aws eks create-cluster "
        f"--name {EKS_CLUSTER_NAME} "
        f"--region {REGION} "
        f"--role-arn {EKS_ROLE_ARN} "
        f"--resources-vpc-config subnetIds={SUBNET_IDS},securityGroupIds={SECURITY_GROUP_IDS}",
        dry_run=dry_run
        )
        print("Waiting for cluster to become ready...")
        run(f"aws eks wait cluster-active --name {EKS_CLUSTER_NAME} --region {REGION}", dry_run=dry_run)
        print("Cluster is now ready")


if __name__ == "__main__":
    main()
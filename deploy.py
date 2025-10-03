import subprocess
import argparse
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

REGION = os.getenv("REGION")
EKS_CLUSTER_NAME = os.getenv("EKS_CLUSTER_NAME")
EKS_ROLE_ARN = os.getenv("EKS_ROLE_ARN")
SUBNET_IDS = os.getenv("SUBNET_IDS")
SECURITY_GROUP_IDS = os.getenv("SECURITY_GROUP_IDS")
ECR_REPO = os.getenv("ECR_REPO", "flask-app")

IMAGE_TAG = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
image_uri = f"{ECR_REPO}:{IMAGE_TAG}"

aws_env = os.environ.copy()
aws_env["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID")
aws_env["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_env["AWS_DEFAULT_REGION"] = REGION

def run(cmd, capture_output=False):
    print(f"> {cmd}")
    if dry_run:
        return "\n"
    result = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=capture_output, env=aws_env)
    if capture_output:
        return result.stdout.strip()
    return None

def main():
    global dry_run
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Show commands without executing them.")
    args = parser.parse_args()
    dry_run = args.dry_run

    try:
        run(f"aws ecr describe-repositories --repository-names {ECR_REPO}")
        print(f"ECR repository {ECR_REPO} already exists. Continuing...")
    except subprocess.CalledProcessError:
        run(f"aws ecr create-repository --repository-name {ECR_REPO}")
        print(f"Created ECR repository {ECR_REPO}")

    account_id = run("aws sts get-caller-identity --query Account --output text",
                     capture_output=True)
    registry = f"{account_id}.dkr.ecr.{REGION}.amazonaws.com"
    run(f"aws ecr get-login-password | docker login --username AWS --password-stdin {registry}")

    run(f"docker build -t {image_uri} .")
    run(f"docker push {image_uri}")
    print(f"Pushed Docker image successfully: {image_uri}")

    try:
        run(f"aws eks describe-cluster --name {EKS_CLUSTER_NAME}")
        print(f"EKS cluster {EKS_CLUSTER_NAME} exists")
    except subprocess.CalledProcessError:
        run(f"aws eks create-cluster "
            f"--name {EKS_CLUSTER_NAME} "
            f"--role-arn {EKS_ROLE_ARN} "
            f"--resources-vpc-config subnetIds={SUBNET_IDS},securityGroupIds={SECURITY_GROUP_IDS}")
        print("Waiting for cluster to become ready. This could take a while...")
        run(f"aws eks wait cluster-active --name {EKS_CLUSTER_NAME}")
        print("Cluster is now ready")

if __name__ == "__main__":
    main()
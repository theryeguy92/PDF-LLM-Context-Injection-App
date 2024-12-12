
# PDF_LLM_Context_Injection_App

## Overview
This cloud-based application allows users to upload PDFs, store their content and metadata in a MySQL database, and interact with a Large Language Model (LLM) service for context-based question answering. The system uses Kafka for real-time message streaming and integrates multiple services into a cohesive cloud architecture.

## Objective
The goal of this project was to build a scalable and efficient cloud-based solution enabling seamless PDF upload, processing, and querying. By leveraging modern technologies such as Kafka, MySQL, FastAPI, and Docker, this application provides a robust foundation for context-driven Q&A functionality, ensuring extensibility for future enhancements.

---

## Key Components
### Terraform Automation
The project includes a `main.tf` file that uses Terraform to provision the required AWS infrastructure, including:
- Virtual Machines (EC2 instances) for:
  - Frontend and PDF processing (VM1)
  - Kafka and Zookeeper (VM2)
  - LLM Service (VM3)
  - MySQL database and Kafka consumer (VM4)
- Networking components such as a VPC, subnets, and security groups.
- Dockerized deployment of application components.

---

## Prerequisites
1. **AWS Account**: Ensure you have an active AWS account with sufficient permissions to create EC2 instances, networking resources, and related infrastructure.
2. **AWS CLI**: Install the AWS CLI and configure it with your credentials:
   ```bash
   aws configure
   ```
3. **Terraform**: Download and Install Terraform

### Installing Terraform
1. **Download Terraform**:
   - Visit the [Terraform download page](https://www.terraform.io/downloads).
   - Select the version compatible with your operating system and download it.

2. **Install Terraform**:
   - Extract the downloaded archive and move the `terraform` binary to a directory in your system's PATH.
   - Confirm the installation by running:
     ```bash
     terraform -v
     ```

---

### Deploying the Application with Terraform

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/theryeguy92/PDF-LLM-Context-Injection-App
   cd PDF_LLM_Context_Injection_App
   ```
2. **Navigate to the Terraform Directory**:
   ```bash
   cd terraform
   ```
3. **Initialize Terraform**:
    - Run the following command to download the requirements for the Terraform Project
   ```bash
   terraform init
   ```

4. **Review the Terraform Plan**:
    - Generate and review the plan
   ```bash
   terraform plan
   ```

5. **Apply the Terraform Configuration**:
    - Generate and review the plan
   ```bash
   terraform Apply
   ```
---
### Access the Application
- Once everything is configured, go to http://<VM1_Public_IP> to access the application.
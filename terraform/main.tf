provider "aws" {
  region = "us-east-2"
}

# Security Group for All VMs
resource "aws_security_group" "vm_security_group" {
  name        = "vm_security_group"
  description = "Security group for all VMs"

  ingress {
    description = "SSH Access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow Ping (ICMP)
  ingress {
    description = "Allow Ping (ICMP)"
    from_port   = -1
    to_port     = -1
    protocol    = "icmp"
    cidr_blocks = ["172.31.0.0/16"]
  }

  # Allow Internal Communication
  ingress {
    description = "Allow All Internal Communication"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["172.31.0.0/16"]
  }

  # For external access to VM1 web (port 8000)
  ingress {
    description = "HTTP VM1"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # For external access to VM3 LLM (port 5000), if needed
  ingress {
    description = "HTTP VM3 LLM"
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # external access to Kafka/Zookeeper or MySQL, add similar rules.

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# VPC and Subnets
resource "aws_vpc" "my_vpc" {
  cidr_block           = "172.31.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
}

resource "aws_subnet" "my_subnets" {
  count                   = 2
  vpc_id                  = aws_vpc.my_vpc.id
  cidr_block              = cidrsubnet(aws_vpc.my_vpc.cidr_block, 8, count.index)
  map_public_ip_on_launch = true
}

# Common Variables
variable "key_name" {
  default = "<key-name>"
}

variable "private_key_path" {
  default = "<path-to-key"
}

# VM1: Frontend / PDF Uploader
resource "aws_instance" "vm1_frontend" {
  ami           = "ami-0aeb7c931a5a61206"
  instance_type = "t3.medium"
  key_name      = var.key_name
  subnet_id     = aws_subnet.my_subnets[0].id
  vpc_security_group_ids = [aws_security_group.vm_security_group.id]

  tags = {
    Name = "VM1-Frontend"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update -y",
      "sudo apt-get install -y docker.io git",
      "sudo systemctl start docker",
      "sudo systemctl enable docker",
      "sudo usermod -aG docker ubuntu",
      "newgrp docker",
      # Clone the repository containing main.py, Dockerfile, .env, templates
      "git clone https://github.com/theryeguy92/PDF-LLM-Context-Injection-App /home/ubuntu/app",
      "cd /home/ubuntu/app/VM1/Frontend/pdf_uploader && sudo docker build -t pdf_uploader_image .",
      "sudo docker run -d -p 8000:8000 --name pdf_uploader_container pdf_uploader_image"
    ]

    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file(var.private_key_path)
      host        = self.public_ip
    }
  }
}

# VM2: Kafka/Zookeeper
resource "aws_instance" "vm2_kafka_zookeeper" {
  ami           = "ami-0aeb7c931a5a61206"
  instance_type = "t3.medium"
  key_name      = var.key_name
  subnet_id     = aws_subnet.my_subnets[0].id
  vpc_security_group_ids = [aws_security_group.vm_security_group.id]

  tags = {
    Name = "VM2-Kafka-Zookeeper"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update -y",
      "sudo apt-get install -y docker.io",
      "sudo systemctl start docker",
      "sudo systemctl enable docker",
      "sudo docker network create kafka_network",
      # Zookeeper
      "sudo docker run -d --name zookeeper --network kafka_network -e ZOOKEEPER_CLIENT_PORT=2181 confluentinc/cp-zookeeper:latest",
      # Kafka
      "LOCAL_IP=$(curl -s http://<IP>/latest/meta-data/local-ipv4)",
      "sudo docker run -d --name kafka --network kafka_network -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://$LOCAL_IP:9092 -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 confluentinc/cp-kafka:latest"
    ]

    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file(var.private_key_path)
      host        = self.public_ip
    }
  }
}

# VM3: LLM
resource "aws_instance" "vm3_llm" {
  ami           = "ami-0aeb7c931a5a61206"
  instance_type = "t3.medium"
  key_name      = var.key_name
  subnet_id     = aws_subnet.my_subnets[0].id
  vpc_security_group_ids = [aws_security_group.vm_security_group.id]

  tags = {
    Name = "VM3-LLM"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update -y",
      "sudo apt-get install -y docker.io git",
      "sudo systemctl start docker",
      "sudo systemctl enable docker",
      "sudo usermod -aG docker ubuntu",
      "newgrp docker",
      # Clone repo and build LLM container
      "git clone https://github.com/theryeguy92/PDF-LLM-Context-Injection-App /home/ubuntu/app",
      "cd /home/ubuntu/app/VM3/LLM && sudo docker build -t llm_image .",
      "sudo docker run -d -p 5000:5000 --name llm_container llm_image"
    ]

    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file(var.private_key_path)
      host        = self.public_ip
    }
  }
}

# VM4: MySQL
resource "aws_instance" "vm4_mysql" {
  ami           = "ami-0aeb7c931a5a61206"
  instance_type = "t3.medium"
  key_name      = var.key_name
  subnet_id     = aws_subnet.my_subnets[0].id
  vpc_security_group_ids = [aws_security_group.vm_security_group.id]

  tags = {
    Name = "VM4-MySQL"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update -y",
      "sudo apt-get install -y docker.io git",
      "sudo systemctl start docker",
      "sudo systemctl enable docker",
      "sudo usermod -aG docker ubuntu",
      "newgrp docker",
      # Clone repo and build MySQL container with schema
      "git clone https://github.com/theryeguy92/PDF-LLM-Context-Injection-App /home/ubuntu/app",
      "cd /home/ubuntu/app/VM4/MySQL/docker && sudo docker build -t mysql_image .",
      "sudo docker run -d -p 3306:3306 --name mysql_container mysql_image"
    ]

    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file(var.private_key_path)
      host        = self.public_ip
    }
  }
}

# Output the public IPs of each VM
output "vm1_ip" {
  value = aws_instance.vm1_frontend.public_ip
}

output "vm2_ip" {
  value = aws_instance.vm2_kafka_zookeeper.public_ip
}

output "vm3_ip" {
  value = aws_instance.vm3_llm.public_ip
}

output "vm4_ip" {
  value = aws_instance.vm4_mysql.public_ip
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "sa-east-1"
}

resource "aws_ecr_repository" "postapi" {
  name = "postapi"
}

resource "aws_security_group" "sg_api" {
  name        = "launch-wizard-1"
  description = "launch-wizard-1 created 2026-08-17T18:25:03.012Z"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "api" {
  ami           = "ami-05401e1394491333f"
  instance_type = "t3.small"

  subnet_id = "subnet-0c02ffd109f728712"

  vpc_security_group_ids = [aws_security_group.sg_api.id]
}

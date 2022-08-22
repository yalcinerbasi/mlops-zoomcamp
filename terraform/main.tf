provider "aws" {
  region = var.region
}

resource "aws_instance" "webserver" {
  ami = var.ami
  instance_type = var.instance_type
  key_name = "mlops"
  vpc_security_group_ids = [aws_security_group.main.id]
  associate_public_ip_address = true

   provisioner "file" {
        source      = "../Project"
        destination = "/home/ubuntu/Project"
        
       
    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file("~/.ssh/mlops.pem")
      host        = self.public_ip
    }
   }


  tags = {
    Name = "MLOps"
  }
}

resource "aws_security_group" "main" {
  egress = [
    {
      cidr_blocks      = ["0.0.0.0/0", ]
      description      = ""
      from_port        = 0
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "-1"
      security_groups  = []
      self             = false
      to_port          = 0
    }
  ]
  ingress = [
    {
      cidr_blocks      = ["0.0.0.0/0", ]
      description      = ""
      from_port        = 22
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "tcp"
      security_groups  = []
      self             = false
      to_port          = 22
    }
  ]
}


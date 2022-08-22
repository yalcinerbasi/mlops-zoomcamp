variable "region" {
  default = "eu-central-1"
}


variable "ami" {
    type = string
    default = "ami-065deacbcaac64cf2"
}

variable "instance_type" {
    type = string
    default = "t2.xlarge"
}

data "external" "zip_file" {
  program = ["python", "${path.module}/archive.py"]

  query = {
    source_dir  = var.source_dir
    output_path = var.output_path
  }
}

output "zip_path" {
  value = data.external.zip_file.result.output_path
}

output "base64sha256" {
  value = data.external.zip_file.result.output_base64sha256
}

variable "source_dir" {
  type = string
}

variable "output_path" {
  type = string
}

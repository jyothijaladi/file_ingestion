resource "aws_s3_bucket" "bucket_1" {
  bucket = var.bucket_1
}
resource "aws_s3_bucket" "bucket_2" {
  bucket = var.bucket_2
}
resource "aws_s3_bucket" "bucket_3" {
  bucket = var.bucket_3
}

resource "aws_s3_bucket" "bucket_4" {
  bucket = var.bucket_4
}

resource "aws_s3_bucket" "bucket_5" {
  bucket = var.bucket_5
}

resource "aws_s3_object" "object" {
  bucket = "data-ing-code"
  key    = "movie-lens/config/file_ingestion_config.json"
  source = "..\\src\\config\\file_ingestion_config.json"

  etag = filemd5("..\\src\\config\\file_ingestion_config.json")
}
